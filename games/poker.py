import random
from enum import Enum

from errorDefinitions import NotEnoughRaiseError
from games.gameClass import Game, GameStatus
from helpers import SendDataType
import time
from collections import Counter


class Deck:
    def __init__(self):
        self.cards = []
        self.fill_deck()
        random.seed(time.time())

    def fill_deck(self):
        self.cards = []
        for suit in ["♠", "♥", "♦", "♣"]:
            for value in range(1, 14):
                self.cards.append(Card(suit, value))
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) < 1:
            self.fill_deck()

        return self.cards.pop()


FIGURES = ["J", "Q", "K"]


def value_to_figure(value):
    if value == 1:
        return "A"
    elif value <= 10:
        return str(value)
    else:
        return FIGURES[value - 11]


def suit_to_value(suit):
    values = {"♠": 4, "♥": 3, "♦": 2, "♣": 1}
    return values[suit]


class Card:
    def __init__(self, suit, val):
        self.suit = suit
        self.value = val

    def __str__(self):
        return f"{value_to_figure(self.value)}{self.suit}"

    def __repr__(self):
        return f"{value_to_figure(self.value)}{self.suit}"


class GameState(Enum):
    INITIAL_BET = 0
    BETTING = 1
    DRAWING = 2
    WAIT_FOR_DRAWS = 3
    BETTING_AGAIN = 4
    CHECK = 5
    GAME_OVER = 6


class PokerHand:
    def __init__(self):
        self.cards = []
        self.rank = 100

    def __str__(self):
        return ' '.join([str(card) for card in self.cards])

    def __repr__(self):
        return self.__str__()

    def __gt__(self, other):
        self.evaluate_rank()
        other.evaluate_rank()
        if self.rank > other.rank:
            return True
        if self.rank == other.rank:
            self_highest_card = max(self.cards, key=lambda card: card.value)
            other_highest_card = max(other.cards, key=lambda card: card.value)
            if self_highest_card.value > other_highest_card.value:
                return True
            if self_highest_card.value == other_highest_card.value:
                return suit_to_value(self_highest_card.suit) > suit_to_value(other_highest_card.suit)
        return False

    def evaluate_rank(self):
        if self.is_royal_flush():
            self.rank = 10
        elif self.is_straight_flush():
            self.rank = 9
        elif self.is_four_of_a_kind():
            self.rank = 8
        elif self.is_full_house():
            self.rank = 7
        elif self.is_flush():
            self.rank = 6
        elif self.is_straight():
            self.rank = 5
        elif self.is_three_of_a_kind():
            self.rank = 4
        elif self.is_two_pair():
            self.rank = 3
        elif self.is_one_pair():
            self.rank = 2
        else:
            self.rank = 1

    def is_royal_flush(self):
        suits = set(card.suit for card in self.cards)
        if len(suits) != 1:
            return False

        values = set(card.value for card in self.cards)
        expected_values = {1, 10, 11, 12, 13}
        return values == expected_values

    def is_straight_flush(self):
        if not self.is_flush() or not self.is_straight():
            return False

        return True

    def is_four_of_a_kind(self):
        value_counts = Counter(card.value for card in self.cards)
        return any(count == 4 for count in value_counts.values())

    def is_full_house(self):
        value_counts = Counter(card.value for card in self.cards)
        return 2 in value_counts.values() and 3 in value_counts.values()

    def is_flush(self):
        suits = set(card.suit for card in self.cards)
        return len(suits) == 1

    def is_straight(self):
        values = sorted(card.value for card in self.cards)
        return values == list(range(values[0], values[0] + 5))

    def is_three_of_a_kind(self):
        value_counts = Counter(card.value for card in self.cards)
        return 3 in value_counts.values()

    def is_two_pair(self):
        value_counts = Counter(card.value for card in self.cards)
        return list(value_counts.values()).count(2) == 2

    def is_one_pair(self):
        value_counts = Counter(card.value for card in self.cards)
        return 2 in value_counts.values()


class Poker(Game):
    MAX_PLAYERS = 6
    MIN_PLAYERS = 2

    def __init__(self):
        super().__init__()
        self.bets = {}
        self.deck = Deck()
        self.state = None
        self.pot = 0
        self.hands = {}
        self.max_time = 30
        self.someone_raised = False
        self.raise_responded = {}
        self.raise_amount = 0
        self.initial_bet = 10
        self.players_list = []
        self.player_turn_idx = 0
        self.folded = []
        self.betting_again = False

    def initial_cards(self):
        for player in self.players.keys():
            self.hands[player] = PokerHand()
        for _ in range(5):
            for player in self.players.keys():
                self.hands[player].cards.append(self.deck.draw())
        for player in self.players.keys():
            self.hands[player].cards.sort(key=lambda card: card.value)
        self.message_queues[self.players_list[self.player_turn_idx]].put(
            (bytes("Now it is your turn!\n", "utf-8"), SendDataType.STRING))
        self.output.append(self.players_list[self.player_turn_idx])

    def start(self):
        self.status = GameStatus.UPDATE
        self.players_list = list(self.players.keys())
        random.shuffle(self.players_list)
        for key in self.players.keys():
            greeting_message = f"Welcome to the Five Card Draw Poker game!\nPlace initial bet {self.initial_bet}:\n"
            self.message_queues[key].put((bytes(greeting_message, "utf-8"), SendDataType.STRING))
            self.output.append(key)
        self.state = GameState.INITIAL_BET

    def bet(self, player_key, bet_amount):
        if player_key not in self.bets.keys():
            self.bets[player_key] = 0
        if self.players[player_key].balance < bet_amount:
            self.message_queues[player_key].put(
                (bytes("You don't have enough money!\n", "utf-8"), SendDataType.STRING))
            self.output.append(player_key)
            return False
        else:
            self.bets[player_key] += bet_amount
            self.players[player_key].balance -= bet_amount
            self.pot += bet_amount
            self.message_queues[player_key].put(
                (bytes(f"{bet_amount} bet placed, game starts!\n", "utf-8"), SendDataType.STRING))
            self.output.append(player_key)
            return True

    def next_player(self):
        if len(self.folded) == len(self.players.keys()) - 1:
            winner = list(set(list(self.players.keys())).difference(self.folded))[0]
            for player_key in self.players.keys():
                if player_key == winner:
                    self.handle_win(player_key)
                else:
                    self.handle_lost(player_key)
            self.prepare_next_round()
        else:
            self.player_turn_idx = (self.player_turn_idx + 1) % (len(self.players_list))
            while self.players_list[self.player_turn_idx] in self.folded:
                self.player_turn_idx = (self.player_turn_idx + 1) % (len(self.players_list))
            self.message_queues[self.players_list[self.player_turn_idx]].put(
                (bytes(f"Now it is your turn!\n", "utf-8"), SendDataType.STRING))
            self.output.append(self.players_list[self.player_turn_idx])
            if self.player_turn_idx == 0 and not self.someone_raised:
                if not self.betting_again:
                    self.state = GameState.DRAWING
                else:
                    self.state = GameState.CHECK

    def his_turn(self, player_key):
        return self.players_list[self.player_turn_idx] == player_key

    def handle_response(self, response, s):
        super(Poker, self).handle_response(response, s)
        if self.status != GameStatus.STOPPED and self.state != GameState.GAME_OVER:
            if self.state == GameState.INITIAL_BET and response[:3] == "bet" and s not in self.bets.keys():
                try:
                    bet_amount = int(response[3:])
                    if bet_amount != self.initial_bet:
                        raise ValueError
                    self.bet(s, bet_amount)
                except ValueError:
                    self.message_queues[s].put((bytes("Invalid bet!\n", "utf-8"), SendDataType.STRING))
                    self.output.append(s)
                self.time_of_last_move = time.time()

            elif self.his_turn(s) and self.state == GameState.BETTING and response[
                                                                          :5] == "check" and not self.someone_raised:
                self.next_player()
                self.message_queues[s].put(
                    (bytes(f"You checked!\n", "utf-8"), SendDataType.STRING))
                self.output.append(s)
            elif self.his_turn(s) and self.state == GameState.BETTING and response[:4] == "fold":
                self.raise_responded[s] = True
                self.folded.append(s)
                self.message_queues[s].put(
                    (bytes(f"You folded!\n", "utf-8"), SendDataType.STRING))
                self.output.append(s)
                self.next_player()
            elif self.his_turn(s) and self.state == GameState.BETTING and response[
                                                                          :4] == "call" and self.someone_raised:
                if self.bet(s, self.raise_amount):
                    self.raise_responded[s] = True
                    self.next_player()
                    self.message_queues[s].put(
                        (bytes(f"Successfully called {self.raise_amount}!\n", "utf-8"), SendDataType.STRING))
                    self.output.append(s)
            elif self.his_turn(s) and self.state == GameState.BETTING and response[:5] == "raise":
                try:
                    raise_amount = int(response[5:])
                    if raise_amount <= self.raise_amount:
                        raise NotEnoughRaiseError
                    else:
                        self.raise_amount = raise_amount
                        for player_key in self.players.keys():
                            if player_key not in self.folded:
                                self.raise_responded[player_key] = False
                        self.raise_responded[s] = True
                        self.someone_raised = True
                        self.next_player()
                        self.message_queues[s].put(
                            (bytes(f"Successfully raised {raise_amount}!\n", "utf-8"), SendDataType.STRING))
                        self.output.append(s)
                except (ValueError, NotEnoughRaiseError) as e:
                    self.message_queues[s].put((bytes("Invalid raise!\n", "utf-8"), SendDataType.STRING))
                    self.output.append(s)
            elif self.state == GameState.WAIT_FOR_DRAWS and response[:7] == "discard" and s not in self.folded:
                try:
                    discard_idx = [int(i) for i in response[7:].split(',')]
                    if len(discard_idx) > 0 and (max(discard_idx) > 4 or min(discard_idx) < 0):
                        raise IndexError
                    new_deck = []
                    for i in range(5):
                        if i not in discard_idx:
                            new_deck.append(self.hands[s].cards[i])
                    for i in range(len(discard_idx)):
                        new_deck.append(self.deck.draw())
                    new_deck.sort(key=lambda card: card.value)
                    self.hands[s].cards = new_deck
                    self.send_hand(s)
                except (ValueError, IndexError) as e:
                    self.message_queues[s].put(
                        (bytes("Invalid card index to discard!\n", "utf-8"), SendDataType.STRING))
                    self.output.append(s)
            else:
                self.message_queues[s].put((bytes("Invalid command\n", "utf-8"), SendDataType.STRING))
                self.output.append(s)
            if self.state == GameState.BETTING and self.someone_raised:
                if False not in self.raise_responded.values():
                    if not self.betting_again:
                        self.state = GameState.DRAWING
                    else:
                        self.state = GameState.CHECK

    def send_hand(self, player_key):
        card_string = ""
        for card in self.hands[player_key].cards:
            card_string += str(card) + '|'
        card_string = "cards: " + card_string[:-1] + '\n'
        self.message_queues[player_key].put((bytes(card_string, "utf-8"), SendDataType.STRING))
        self.output.append(player_key)

    def send_hands(self):
        for player_key in self.players.keys():
            self.send_hand(player_key)

    def handle_timer(self):
        print(self.state)
        if self.status != GameStatus.STOPPED and self.state == GameState.INITIAL_BET:
            if len(self.bets) == len(self.players):
                self.state = GameState.BETTING
                self.initial_cards()
                self.send_hands()
        elif self.status != GameStatus.STOPPED and self.state == GameState.DRAWING:
            for key in self.players.keys():
                message = f"Type comma separated indexes of cards to discard from 0 to 4\n"
                self.message_queues[key].put((bytes(message, "utf-8"), SendDataType.STRING))
                self.output.append(key)
            self.time_of_last_move = time.time()
            self.state = GameState.WAIT_FOR_DRAWS
        elif self.status != GameStatus.STOPPED and self.state == GameState.WAIT_FOR_DRAWS and \
                time.time() - self.time_of_last_move > self.max_time:
            self.state = GameState.BETTING
            for key in self.players.keys():
                if key not in self.folded:
                    message = f"Discarding cards ended, second bet round\n"
                    self.message_queues[key].put((bytes(message, "utf-8"), SendDataType.STRING))
                    self.output.append(key)
            self.player_turn_idx = 0
            self.betting_again = True
            self.raise_amount = 0
            self.someone_raised = False
            self.message_queues[self.players_list[self.player_turn_idx]].put(
                (bytes("Now it is your turn!\n", "utf-8"), SendDataType.STRING))
            self.output.append(self.players_list[self.player_turn_idx])
        elif self.status != GameStatus.STOPPED and self.state == GameState.CHECK:
            winner = None
            for player_key in self.players.keys():
                if player_key not in self.folded:
                    if winner is None:
                        winner = player_key
                    elif winner is not None and self.hands[winner] < self.hands[player_key]:
                        winner = player_key
            for player_key in self.players.keys():
                if player_key == winner:
                    self.handle_win(player_key)
                else:
                    self.handle_lost(player_key)
            self.prepare_next_round()

    def handle_win(self, player_key):
        self.players[player_key].balance += self.pot
        self.message_queues[player_key].put((bytes(f"You won!\n", "utf-8"), SendDataType.STRING))
        self.output.append(player_key)

    def handle_lost(self, player_key):
        self.message_queues[player_key].put((bytes(f"You lost!\n", "utf-8"), SendDataType.STRING))
        self.output.append(player_key)

    def prepare_next_round(self):
        self.bets = {}
        self.deck = Deck()
        self.state = GameState.INITIAL_BET
        self.pot = 0
        self.hands = {}
        self.someone_raised = False
        self.raise_responded = {}
        self.raise_amount = 0
        self.player_turn_idx = 0
        self.folded = []
        self.betting_again = False
        # TODO: to request play again, kick after 30 seconds
        # TODO: quit/back handling (players_list change)
