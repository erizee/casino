import random
from enum import Enum
from errorDefinitions import InvalidResponseException, InvalidBet
from games.gameClass import Game, GameStatus
from games.cardClass import Deck, CardBaccarat


class Outcome(Enum):
    tie = 0
    player = 1
    banker = 2
    nobody = -1

    def next(self):
        return Outcome((self.value + 1) % 3)


class Baccarat(Game):
    MAX_PLAYERS = 1
    MIN_PLAYERS = 1

    def __init__(self):
        super().__init__()
        self.bets = {"tie": 0, "player": 0, "banker": 0}
        self.cards = Deck(CardBaccarat, 6)
        self.table = [[], []]
        self.player = None

    def handle_response(self, response, s):
        super(Baccarat, self).handle_response(response, s)
        if self.status != GameStatus.STOPPED:
            split_response = response.split(" ")
            if not split_response:
                raise InvalidResponseException

            bet_nr = self.bets_parser(response)

            sums = [0, 0]
            if bet_nr == 1:
                outcome = self.first_round(sums)

                if outcome.value >= 0:
                    self.display_table()
                    self.handle_win(outcome)
                else:
                    outcome = self.second_round(sums)
                    self.display_table()
                    self.handle_win(outcome)
                self.clear()

    def start(self):
        for key in self.players.keys():
            self.player = key
        self.send_str("Welcome to baccarat!!\n To see all available commands type 'commands'", self.player)

    def handle_win(self, outcome: Outcome):
        if self.bets[outcome.name] == 0:
            self.send_str(f"Outcome:-{self.bets[outcome.next().name] + self.bets[outcome.next().next().name]}",
                          self.player)
            self.add_game_history(self.player, "baccarat", 0, 0,
                                  self.bets[outcome.next().name] + self.bets[outcome.next().next().name])
        else:
            self.players[self.player].balance += self.bets[outcome.name] * 2
            self.update_balance(self.player, self.bets[outcome.name] * 2)
            self.send_str(f"Outcome:+{self.bets[outcome.name]}", self.player)
            self.add_game_history(self.player, "baccarat", 1, self.bets[outcome.name], 0)

    def first_round(self, sums):
        self.table[0].append(self.cards.draw())
        self.table[1].append(self.cards.draw())
        self.table[0].append(self.cards.draw())
        self.table[1].append(self.cards.draw())

        player_sum = (self.table[0][0].value + self.table[0][1].value) % 10
        banker_sum = (self.table[1][0].value + self.table[1][1].value) % 10

        sums[0] = player_sum
        sums[1] = banker_sum

        if player_sum == banker_sum and player_sum not in (8, 9):
            self.send_str("Its a Tie!", self.player)
            return Outcome.tie
        elif player_sum in (8, 9):
            self.send_str("Player wins!", self.player)
            return Outcome.player
        elif banker_sum in (8, 9):
            self.send_str("Banker wins!", self.player)
            return Outcome.banker
        else:
            return Outcome.nobody

    def second_round(self, sums):
        is_player_pat = 0
        player_third_card = 0
        banker_third_card = 0

        player_total = sums[0]
        banker_total = sums[1]

        if player_total <= 5:
            is_player_pat = 1
            new_card = self.cards.draw()
            self.table[0].append(new_card)
            player_third_card = new_card.value

        if is_player_pat:
            if banker_total <= 2 or (banker_total == 3 and player_third_card != 8) or (
                    banker_total == 4 and 2 <= player_third_card <= 7) or \
                    (banker_total == 5 and 4 <= player_third_card <= 7) or (
                    banker_total == 6 and 6 <= player_third_card <= 7):
                new_card = self.cards.draw()
                self.table[0].append(new_card)
                banker_third_card = new_card.value

        player_total = (player_total + player_third_card) % 10
        banker_total = (banker_total + banker_third_card) % 10
        if player_total == banker_total:
            self.send_str("Its a Tie!", self.player)
            return Outcome.tie
        else:
            if abs(9 - player_total) < abs(9 - banker_total):
                self.send_str("Player wins!", self.player)
                return Outcome.player
            else:
                self.send_str("Banker wins!", self.player)
                return Outcome.banker

    def display_table(self):
        player_cards = " ".join([str(card) for card in self.table[0]])
        banker_cards = " ".join([str(card) for card in self.table[1]])
        self.send_str(f"""Player:     Banker:\n{player_cards}:{banker_cards}\n""", self.player)

    def bets_parser(self, bet):
        try:
            bet_splited = bet.split(" ")
            if bet_splited[0] == "commands":
                self.send_str("""Available commands:
    -Betting:
        bet [tie|banker|player] <amount>
    -Quit
        back""", self.player)
                return 0
            elif bet_splited[0] == "bet":
                if self.bets.get(bet_splited[1]) is not None:
                    amount = int(bet_splited[2])

                    if amount < 0:
                        self.send_str("Invalid bet", self.player)
                        return -1
                    if self.players[self.player].balance < amount:
                        self.send_str("Not enough money", self.player)
                        return -1
                    self.bets[bet_splited[1]] = amount
                    self.players[self.player].balance -= amount
                    self.update_balance(self.player, -amount)
                    return 1
            else:
                raise InvalidBet()
        except (IndexError, InvalidBet):
            self.send_str("Invalid bet", self.player)
        return -1

    def clear(self):
        self.table = [[], []]
        for key in self.bets:
            self.bets[key] = 0
