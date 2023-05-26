import random as rn
from enum import Enum
from games.gameClass import Game, GameStatus
from helpers import SendDataType
import time

def check(board):
    for i in range(5):
        if board[i][i] == "*":
            j = 0
            while j < 5 and board[i][j] == "*":
                j += 1
            if j == 5:
                return True
            j = 0
            while j < 5 and board[j][i] == "*":
                j += 1
            if j == 5:
                return True
    return False


def board_to_str(board):
    message = f"Your Bingo Board:\n"
    for row in board:
        message += " ".join(map(str, row)) + "\n"
    return message


class GameState(Enum):
    BETTING = 0
    PLAYING = 1
    GAME_OVER = 2


class Bingo(Game):
    MAX_PLAYERS = 6
    MIN_PLAYERS = 1

    def __init__(self):
        super().__init__()
        self.numbers = []
        self.current_nb_idx = 0
        self.current_nb = 0
        self.boards = {}
        self.bets = {}
        self.state = GameState.BETTING
        self.max_time = 10
        self.last_update = time.time()
        self.initialized = False
        self.pot = 0
        self.winner = None

    def create_boards(self):
        for client_key in self.players.keys():
            # self.boards[client_key] = [rn.sample(range(15 * j + 1, 15 * (j + 1) + 1), 5) for j in range(5)]
            self.boards[client_key] = [[1 for _ in range(5)] for _ in range(5)]
            self.boards[client_key][2][2] = "*"

    def generate_numbers(self):
        # self.numbers = [i for i in range(1, 76)]
        self.numbers = [1 for i in range(1, 76)]
        rn.shuffle(self.numbers)

    def handle_response(self, response, s):
        super(Bingo, self).handle_response(response, s)
        if self.status != GameStatus.STOPPED and self.state != GameState.GAME_OVER:
            if response[:3] == "bet":
                try:
                    bet_amount = int(response[3:])
                    if self.players[s].balance < bet_amount:
                        self.message_queues[s].put(
                            (bytes("You don't have enough money!\n", "utf-8"), SendDataType.STRING))
                        self.output.append(s)
                    else:
                        self.bets[s] = bet_amount
                        self.players[s].balance -= bet_amount
                        self.update_balance(s, -bet_amount)
                        self.pot += bet_amount
                        self.message_queues[s].put(
                            (bytes(f"{bet_amount} bet placed, wait for other players\n", "utf-8"), SendDataType.STRING))
                        self.output.append(s)
                except ValueError:
                    self.message_queues[s].put((bytes("Invalid bet!\n", "utf-8"), SendDataType.STRING))
                    self.output.append(s)
            elif response == "bingo" and self.winner is None:
                if check(self.boards[s]):
                    self.handle_win(s)
                    self.winner = s
                else:
                    self.message_queues[s].put((bytes("You don't have bingo!\n", "utf-8"), SendDataType.STRING))
                    self.output.append(s)
            else:
                try:
                    position = tuple(int(x) for x in response.split(", "))
                except ValueError:
                    self.message_queues[s].put((bytes("Invalid command\n", "utf-8"), SendDataType.STRING))
                    self.output.append(s)
                else:
                    try:
                        if len(position) == 2 and self.boards[s][position[0]][position[1]] == self.current_nb:
                            self.boards[s][position[0]][position[1]] = "*"
                            self.message_queues[s].put((bytes(board_to_str(self.boards[s]), "utf-8"),
                                                        SendDataType.STRING))
                            self.output.append(s)
                    except IndexError:
                        self.message_queues[s].put((bytes("Invalid move\n", "utf-8"), SendDataType.STRING))
                        self.output.append(s)

    def handle_timer(self):
        if self.state == GameState.GAME_OVER:
            self.reset()
        elif not self.initialized and len(self.players) == len(self.bets):
            self.create_boards()
            self.generate_numbers()
            self.current_nb = self.numbers[self.current_nb_idx]
            self.current_nb_idx += 1
            for client_key in self.players.keys():
                message = board_to_str(self.boards[client_key])
                message += f"Current number: {self.current_nb}\n"
                self.message_queues[client_key].put((bytes(message, "utf-8"), SendDataType.STRING))
                self.output.append(client_key)
            self.last_update = time.time()
            self.initialized = True
        elif self.initialized and self.status != GameStatus.STOPPED and time.time() - self.last_update >= self.max_time:
            if self.current_nb_idx > 69:
                for client_key in self.players.keys():
                    self.message_queues[client_key].put((bytes("Game over!", "utf-8"), SendDataType.STRING))
                    self.output.append(client_key)
                self.reset()
            else:
                self.current_nb = self.numbers[self.current_nb_idx]
                self.current_nb_idx += 1
                for client_key in self.players.keys():
                    self.current_nb = self.numbers[self.current_nb_idx]
                    self.current_nb_idx += 1
                    message = f"Current number: {self.current_nb}\n"
                    self.message_queues[client_key].put((bytes(message, "utf-8"), SendDataType.STRING))
                    self.output.append(client_key)
                self.last_update = time.time()

    def handle_win(self, s):
        self.players[s].balance += self.pot
        self.message_queues[s].put((bytes(f"You won {self.pot}!", "utf-8"), SendDataType.STRING))
        self.output.append(s)
        self.update_balance(s, self.pot)
        self.add_game_history(s, "bingo", 1, self.pot, 0)
        self.end_game()

    def end_game(self):
        for client_key in self.players.keys():
            self.message_queues[client_key].put((bytes("Game over!", "utf-8"), SendDataType.STRING))
            self.output.append(client_key)
            if client_key != self.winner:
                self.add_game_history(client_key, "bingo", 0, 0, self.bets[client_key])
        self.state = GameState.GAME_OVER

    def reset(self):
        self.numbers = []
        self.current_nb_idx = 0
        self.current_nb = 0
        self.boards = {}
        self.bets = {}
        self.state = 0
        self.max_time = 10
        self.last_update = time.time()
        self.initialized = False
        self.pot = 0
        self.winner = None
        self.status = GameStatus.STOPPED

    def start(self):
        self.status = GameStatus.UPDATE

        greeting_message = f"Welcome to the Bingo game!\nPlace your bet:\n"
        for client_key in self.players.keys():
            self.message_queues[client_key].put((bytes(greeting_message, "utf-8"), SendDataType.STRING))
            self.output.append(client_key)
