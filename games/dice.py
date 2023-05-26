import random
from enum import Enum
from games.gameClass import Game, GameStatus
from helpers import SendDataType
from errorDefinitions import ShooterDpassBet, InvalidBet
import time
from rules import dice_rules, dice_commands
from _thread import *


class DiceWinTypes(Enum):
    PASS = 0
    DPASS = 1
    DRAW = 2

    def __repr__(self):
        return f'{self.name.lower()}'

    def __str__(self):
        return self.__repr__()


def calculate_winning(p_dict, rolled):
    if rolled == DiceWinTypes.DRAW:
        return p_dict['dpass']
    elif rolled == DiceWinTypes.PASS:
        return p_dict['pass'] * 2
    elif rolled == DiceWinTypes.DPASS:
        return p_dict['dpass'] * 2


class Dice(Game):
    MAX_PLAYERS = 16
    MIN_PLAYERS = 1

    def __init__(self):
        super().__init__()
        self.bets = dict()
        self.shooter = None
        self.shooterId = -1
        self.isBetTime = 1
        self.isRollTime = 0
        self.state = 0
        self.point = 0
        self.message_sent = 0
        random.seed(time.time())

    def roll(self):
        r1 = random.randint(1, 6)
        r2 = random.randint(1, 6)
        return r1 + r2, (r1, r2)

    def send_message(self, message, type, s):
        self.message_queues[s].put(
            (bytes(message, "utf-8"), type))
        self.output.append(s)

    def reset_timer(self):
        self.time_of_last_move = time.time()

    def handle_response(self, response, s):
        if self.status != GameStatus.STOPPED:
            if response == "commands":
                self.send_message(dice_commands, SendDataType.STRING, s)
            elif response == "gmrules":
                self.send_message(dice_rules, SendDataType.STRING, s)
            elif response == "roll":
                if self.shooter == s and self.state not in (-1, 0):

                    # If shooter types roll to fast (while handling previous roll)
                    if self.status == GameStatus.BUSY:
                        self.reset_timer()
                        self.send_message("Could not roll, try again", SendDataType.STRING, s)
                        return

                    self.handle_roll(*self.roll())

                elif self.shooter != s:
                    self.send_message("You are not a shooter!", SendDataType.STRING, s)
                else:  # not self.isRollTime
                    self.send_message("Wait for players to place their bets before rolling!", SendDataType.STRING, s)
            elif not self.isBetTime:
                self.send_message("Cant place bets now, wait", SendDataType.STRING, s)
            else:  # Potential game command
                try:
                    print(response)
                    response_split = response.split(" ")

                    if self.bets.get(s) is None:
                        self.bets[s] = {"pass": 0, "dpass": 0}

                    if response_split[0] == "dpass" and self.shooter == s:
                        raise ShooterDpassBet

                    amount = int(response_split[1])

                    if self.players[s].balance < amount:
                        raise InvalidBet

                    self.bets[s][response_split[0]] += amount
                    self.players[s].balance -= amount
                    self.update_balance(s, -amount)

                    self.send_message("Bet placed", SendDataType.STRING, s)

                except Exception as e:
                    self.send_message("Error: " + repr(e), SendDataType.STRING, s)

    def change_state(self, state):
        if state == 0:
            self.message_sent = 0
            self.isBetTime = 1
            self.isRollTime = 0
        if state in (1,2):
            self.isRollTime = 1
            self.isBetTime = 0

        self.reset_timer()
        self.state = state

    def handle_round_end(self, winning_bet):
        for client_key in self.players.keys():
            self.send_message(f"{winning_bet} wins!!", SendDataType.STRING, client_key)

        for client_key in self.players.keys():
            if self.bets.get(client_key) is not None:
                client_score = calculate_winning(self.bets[client_key], winning_bet)

                self.players[client_key].balance += client_score
                self.update_balance(client_key, client_score)

                self.send_message(f"You won: {client_score}" if client_score > 0 else "You lose", SendDataType.STRING,
                                  client_key)

                won = 0
                if client_score > 0:
                    won = 1

                winnings = 0
                loss = 0

                if winning_bet == DiceWinTypes.DPASS:
                    loss = self.bets[client_key]['pass']
                    winnings = self.bets[client_key]['dpass']
                elif winning_bet == DiceWinTypes.PASS:
                    loss = self.bets[client_key]['dpass']
                    winnings = self.bets[client_key]['pass']
                elif winning_bet == DiceWinTypes.DRAW:
                    loss = self.bets[client_key]['pass']
                    winnings = 0

                self.add_game_history(client_key, "dice", won, winnings, loss)

        self.new_round()

    def new_round(self):
        self.bets.clear()
        self.next_shooter()
        self.change_state(0)

    def next_shooter(self):
        curr_shooter_id = self.input.index(self.shooter)  # check current shooter id
        if curr_shooter_id is None:  # shooter not in game room
            if self.shooterId < len(self.input):
                self.shooter = self.input[self.shooterId]
            else:
                self.shooterId = 0
                self.shooter = self.input[self.shooterId]
        else:  # shooter in game room
            self.shooterId = (curr_shooter_id + 1) % len(self.input)
            self.shooter = self.input[self.shooterId]

    def handle_roll(self, roll, roll_tuple):
        self.status = GameStatus.BUSY
        if self.state == 1:
            if roll in (7, 11, 2, 3, 12):
                for client_key in self.players.keys():
                    self.send_message(f"Rolled {roll_tuple} for total of {roll}",
                                      SendDataType.STRING, client_key)
                self.handle_round_end(
                    DiceWinTypes.PASS if roll in (7, 11) else (DiceWinTypes.DRAW if roll == 12 else DiceWinTypes.DPASS))
            else:
                for client_key in self.players.keys():
                    self.send_message(f"Rolled {roll_tuple} for total of {roll}, waiting for next roll! ",
                                      SendDataType.STRING, client_key)
                self.change_state(2)
                self.point = roll

        elif self.state == 2:
            if roll != 7:
                if roll == self.point:
                    for client_key in self.players.keys():
                        self.send_message(f"Rolled {roll_tuple} for total of  {roll}",
                                          SendDataType.STRING, client_key)

                    self.handle_round_end(DiceWinTypes.PASS)
                else:
                    for client_key in self.players.keys():
                        self.send_message(f"Rolled {roll_tuple} for total of {roll}, waiting for next roll! ",
                                          SendDataType.STRING, client_key)
                    self.change_state(2)
            else:
                for client_key in self.players.keys():
                    self.send_message(f"Rolled {roll_tuple} for total of {roll}",
                                      SendDataType.STRING, client_key)

                self.handle_round_end(DiceWinTypes.DPASS)
                self.change_state(0)

        self.status = GameStatus.UPDATE

    def handle_skip_roll(self, s):
        for client_key in self.players.keys():
            if self.bets.get(client_key) is not None:
                for key in ("pass", "dpass"):
                    self.players[client_key].balance += self.bets[client_key][key]
            self.send_message("Shooter left, all bets were refounded, wait for new shooter to be chosen",
                              SendDataType.STRING, client_key)

        self.change_state(0)
        self.next_shooter()
        self.game_room.untransfer_player(s)

    def start(self):
        self.shooter = self.input[0]
        self.shooterId = 0

    def handle_timer(self):
        if self.state == 0:
            if not self.message_sent:
                for client_key in self.players.keys():
                    self.send_message("Its betting time", SendDataType.STRING, client_key)
                    if client_key == self.shooter:
                        self.send_message("You are a shooter", SendDataType.STRING, client_key)

                self.message_sent = 1

            if time.time() - self.time_of_last_move >= 15:
                self.isBetTime = 0

                for client_key in self.players.keys():
                    self.send_message("Bets ended, time for shooter to roll!", SendDataType.STRING, client_key)

                self.change_state(1)
                self.status = GameStatus.UPDATE

        elif self.state in (1, 2):
            if time.time() - self.time_of_last_move >= 15:

                for client_key in self.players.keys():
                    self.send_message(f"Shooter disconnected, returning all bets", SendDataType.STRING, client_key)

                self.isRollTime = 0
                self.handle_skip_roll(self.shooter)

    def reset_room(self):
        for client_key in self.players.keys():
            if self.bets.get(client_key) is not None:
                for key in ("pass", "dpass"):
                    self.players[client_key].balance += self.bets[client_key][key]

                self.send_message(f"Not enough players, all players will be kicked from server", SendDataType.STRING, client_key)

        for client_key in self.players.keys():
            self.game_room.untransfer_player(client_key)

        self.change_state(0)
        self.status = GameStatus.STOPPED
