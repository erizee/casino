import random
from games.gameClass import Game, GameStatus
import time
from errorDefinitions import InvalidBet


def get_field_color_from_number(rolled_number):
    if rolled_number % 2 == 1:
        return 'black'
    elif rolled_number != 0:
        return 'red'
    else:
        return 'green'


class Roulette(Game):
    MAX_PLAYERS = 100
    MIN_PLAYERS = 1

    def __init__(self):
        super().__init__()
        self.bets = dict()
        self.is_bet_time = 0
        self.state = 1
        random.seed(time.time())

    def roll(self):
        return random.randint(0, 36)

    def handle_response(self, response, s):
        super(Roulette, self).handle_response(response, s)
        if self.status != GameStatus.STOPPED:
            if response == "commands":
                self.send_str("""Available commands:
    -Betting:
        bet [red|black] <amount>
    -Quit
        back""", s)
            elif not self.is_bet_time:
                self.send_str("Cant place bets now, wait", s)
            else:
                try:
                    info = response.split(" ")
                    if self.bets.get(s) is None:
                        self.bets[s] = {"green": 0, "red": 0, "black": 0}

                    amount = int(info[2])

                    if self.players[s].balance < amount:
                        raise InvalidBet

                    self.players[s].balance -= amount
                    self.update_balance(s, -amount)
                    self.bets[s][info[1]] += amount

                    self.send_str("Bet placed", s)
                except (IndexError, InvalidBet):
                    self.send_str("Invalid bet", s)

    def calculate_winning(self, p_dict, rolled):
        if rolled % 2 == 0:
            return p_dict['red'] * 2
        if rolled == 0:
            return p_dict['green'] * 14

        return p_dict['black'] * 2

    def start(self):
        pass

    def handle_timer(self):
        if self.state == 0:
            if time.time() - self.time_of_last_move >= 10:
                self.is_bet_time = 0

                for client_key in self.players.keys():
                    self.send_str("Rolling...", client_key)
                self.state = 1
                self.status = GameStatus.UPDATE
                self.time_of_last_move = time.time()
        elif self.state == 1:
            if time.time() - self.time_of_last_move >= 0.7:
                rolled = self.roll()
                for client_key in self.players.keys():
                    self.send_str(
                        f"Number rolled: {rolled} - {get_field_color_from_number(rolled)}",
                        client_key)

                for client_key in self.players.keys():
                    if self.bets.get(client_key) is not None:
                        client_score = self.calculate_winning(self.bets[client_key], rolled)
                        self.players[client_key].balance += client_score
                        self.update_balance(client_key, client_score)

                        won = 1
                        message = f"You won: {client_score}"

                        if client_score == 0:
                            message = "You lost"
                            won = 0
                        winning = client_score
                        loss = 0
                        if rolled % 2 == 0:
                            loss = self.bets[client_key]['green'] + self.bets[client_key]['black']
                        elif rolled == 0:
                            loss = self.bets[client_key]['red'] + self.bets[client_key]['black']
                        else:
                            loss = self.bets[client_key]['red'] + self.bets[client_key]['green']
                        try:
                            if loss > winning:
                                won = 0
                            self.add_game_history(client_key, "roulette", won, winning, loss)
                        except Exception as e:
                            print(e)
                        self.send_str(message, client_key)

                self.bets.clear()
                self.state = 2
                self.status = GameStatus.UPDATE
                self.time_of_last_move = time.time()
        elif self.state == 2:
            if time.time() - self.time_of_last_move >= 4:
                for client_key in self.players.keys():
                    self.send_str("Its betting time", client_key)
                self.is_bet_time = 1
                self.state = 0
                self.status = GameStatus.UPDATE
                self.time_of_last_move = time.time()
