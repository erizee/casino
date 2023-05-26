import tkinter as tk
import socket
from helpers import SendDataType, receive_data
from _thread import *

class BingoGamePage(tk.Frame):
    def __init__(self, parent, controller, width, height, **kw):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.running = 1

        self.parent = parent
        self.controller = controller
        self.s = self.controller.s

        # self.back_btn = tk.Button(self, text="Back", command=self.back)

        self.label = tk.Label(self, text="Welcome to the Bingo game!")
        self.label = tk.Label(self, text="Welcome to the Bingo game!")
        self.label.pack()

        self.bet_entry = tk.Entry(self)
        self.bet_entry.pack()

        # self.play_button = tk.Button(self, text="Play", command=self.play)
        # self.play_button.pack()

        self.bet_button = tk.Button(self, text="Place Bet", command=self.place_bet)
        self.bet_button.pack()

        self.mark_button = tk.Button(self, text="Mark Number", command=self.mark_number)
        self.mark_button.pack()

        self.back_button = tk.Button(self, text="Go back", command=self.back)
        self.back_button.pack()

        self.board_text = tk.Text(self, width=30, height=10)
        self.board_text.pack()

        self.number_label = tk.Label(self, text="Current Number:")
        self.number_label.pack()

        self.number_text = tk.Text(self, width=10, height=1)
        self.number_text.pack()

        self.bingo_button = tk.Button(self, text="Bingo!", command=self.send_bingo)
        self.bingo_button.pack()

        self.cmd_text = tk.Text(self, width=30, height=10)
        self.cmd_text.pack()

    def place_bet(self):
        bet_amount = self.bet_entry.get()
        self.s.send(bytes(f"bet {bet_amount}", "utf-8"))

    def mark_number(self):
        position = self.bet_entry.get()
        self.s.send(bytes(position, "utf-8"))

    # def play(self):
    #     self.s.send(bytes("play bingo", "utf-8"))

    def update_board(self, board):
        self.board_text.delete('1.0', tk.END)
        self.board_text.insert(tk.END, board)

    def update_number(self, number):
        self.number_text.delete('1.0', tk.END)
        self.number_text.insert(tk.END, number)

    def update_cmd(self, cmd):
        self.cmd_text.delete('1.0', tk.END)
        self.cmd_text.insert(tk.END, cmd)

    def send_bingo(self):
        self.s.send(bytes("bingo", "utf-8"))

    def back(self):
        self.s.send(bytes("back", 'utf-8'))
        self.controller.show_frame('ChooseGamePage')
        self.clear()

    def clear(self):
        self.bet_entry.delete(0, tk.END)
        self.board_text.delete('1.0', tk.END)
        self.cmd_text.delete('1.0', tk.END)

    def handle_message(self, data):
        if data is not None:
            if data[0] == SendDataType.STRING:
                msg = data[1].decode()
                if msg[:16] == "Current number: ":
                    self.update_number(int(msg[16:]))
                elif msg[:4] == "Your":
                    self.update_board(msg[18:])
                else:
                    self.update_cmd(msg)

