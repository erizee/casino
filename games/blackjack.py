from enum import Enum
from games.gameClass import Game, GameStatus
import time
from games.cardClass import Deck, CardBlackjack


class GameState(Enum):
    BETTING = 0
    PLAYER_TURN = 1
    DEALER_TURN = 2
    GAME_OVER = 3


def calculate_hand_value(hand):
    value = 0
    aces = 0
    for card in hand:
        if card.value == 1:
            value += 11
            aces += 1
        else:
            value += card.value
    while value > 21 and aces > 0:
        value -= 10
        aces -= 1
    return value


class Blackjack(Game):
    def __init__(self):
        super().__init__()
        self.bets = {}
        self.deck = Deck(CardBlackjack, 6)
        self.player_key = None
        self.state = GameState.BETTING
        self.pot = 0
        self.player_hand = []
        self.dealer_hand = []
        self.max_time = 30
        self.bet_request = False

    def initial_cards(self):
        self.player_hand.append(self.deck.draw())
        self.dealer_hand.append(self.deck.draw())
        self.player_hand.append(self.deck.draw())
        self.dealer_hand.append(self.deck.draw())

    def handle_response(self, response, s):
        super(Blackjack, self).handle_response(response, s)
        if self.status != GameStatus.STOPPED and self.state != GameState.GAME_OVER:
            if self.state == GameState.BETTING and response[:3] == "bet":
                try:
                    bet_amount = int(response[3:])
                    if self.players[s].balance < bet_amount:
                        self.send_str("You don't have enough money!\n", s)
                    else:
                        self.bets[s] = bet_amount
                        self.players[s].balance -= bet_amount
                        self.pot += bet_amount
                        self.update_balance(s, -bet_amount)
                        self.send_str(f"{bet_amount} bet placed, game starts!\n", s)
                        self.state = GameState.PLAYER_TURN
                        self.initial_cards()
                        self.send_str(f"Your cards: {self.player_hand}\n", s)
                        self.send_str(f"Dealer cards: {['X'] + self.dealer_hand[1:]}\n", s)
                except ValueError:
                    self.send_str("Invalid bet!\n", s)
                self.time_of_last_move = time.time()
            elif self.state == GameState.PLAYER_TURN and response == "hit":
                self.player_hand.append(self.deck.draw())
                self.send_str(f"Your cards: {self.player_hand}\n", s)
                if calculate_hand_value(self.player_hand) > 21:
                    self.handle_lost()
                elif calculate_hand_value(self.player_hand) == 21:
                    self.handle_win()
                self.time_of_last_move = time.time()
            elif self.state == GameState.PLAYER_TURN and response == "stand":
                self.state = GameState.DEALER_TURN
            else:
                self.send_str("Invalid command\n", s)

    def start(self):
        self.status = GameStatus.UPDATE
        self.bet_request = True
        for key in self.players.keys():
            self.player_key = key
        greeting_message = f"Welcome to the Blackjack game!\nPlace your bet:\n"
        self.send_str(greeting_message, self.player_key)

    def handle_timer(self):
        if self.status != GameStatus.STOPPED and self.bet_request is False and self.state == GameState.BETTING:
            self.send_str(f"Place your bet:\n", self.player_key)
            self.bet_request = True

        elif self.status != GameStatus.STOPPED and self.state == GameState.DEALER_TURN:
            if calculate_hand_value(self.dealer_hand) < 17:
                self.dealer_turn()
            elif calculate_hand_value(self.dealer_hand) > 21 or \
                    calculate_hand_value(self.player_hand) > calculate_hand_value(self.dealer_hand):
                self.send_str(f"Dealer cards: {self.dealer_hand}\n", self.player_key)
                self.handle_win()
            else:
                self.send_str(f"Dealer cards: {self.dealer_hand}\n", self.player_key)
                self.handle_lost()

        elif self.status != GameStatus.STOPPED and self.state == GameState.PLAYER_TURN and \
                time.time() - self.time_of_last_move > self.max_time:
            self.state = GameState.DEALER_TURN

    def handle_win(self):
        self.players[self.player_key].balance += self.pot
        self.send_str(f"You won!\n", self.player_key)
        self.update_balance(self.player_key, self.pot)
        self.add_game_history(self.player_key, "blackjack", 1, self.pot, 0)
        self.prepare_next_round()

    def handle_lost(self):
        self.send_str(f"You lost!\n", self.player_key)
        self.add_game_history(self.player_key, "blackjack", 0, 0, self.bets[self.player_key])
        self.prepare_next_round()

    def prepare_next_round(self):
        self.pot = 0
        self.bets = {}
        self.player_hand = []
        self.dealer_hand = []
        self.state = GameState.BETTING
        self.bet_request = False
        self.time_of_last_move = time.time()

    def dealer_turn(self):
        if calculate_hand_value(self.dealer_hand) < 21:
            self.dealer_hand.append(self.deck.draw())
            self.send_str(f"Dealer draws {self.dealer_hand[-1]}\n", self.player_key)
            self.send_str(f"Dealer cards: {self.dealer_hand}\n", self.player_key)
