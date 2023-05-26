import tkinter as tk
import socket
from helpers import SendDataType, receive_data
from _thread import *


class PokerGamePage(tk.Frame):
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

        self.raise_button = tk.Button(self, text="Raise", command=self.place_raise)
        self.raise_button.pack()

        self.call_button = tk.Button(self, text="Call", command=self.send_call)
        self.call_button.pack()

        self.fold_button = tk.Button(self, text="Fold", command=self.send_fold)
        self.fold_button.pack()

        self.check_button = tk.Button(self, text="Check", command=self.send_check)
        self.check_button.pack()

        self.discard_button = tk.Button(self, text="Discard", command=self.send_discard)
        self.discard_button.pack()

        self.back_button = tk.Button(self, text="Go back", command=self.back)
        self.back_button.pack()

        self.hand_text = tk.Text(self, width=30, height=10)
        self.hand_text.pack()

        self.cmd_text = tk.Text(self, width=30, height=10)
        self.cmd_text.pack()

    def place_bet(self):
        bet_amount = self.bet_entry.get()
        self.s.send(bytes(f"bet {bet_amount}", "utf-8"))

    def place_raise(self):
        raise_amount = self.bet_entry.get()
        self.s.send(bytes(f"raise {raise_amount}", "utf-8"))

    def send_discard(self):
        cards_to_discard = self.bet_entry.get()
        self.s.send(bytes(f"discard{cards_to_discard}", "utf-8"))

    # def play(self):
    #     self.s.send(bytes("play bingo", "utf-8"))

    def update_hand(self, hand):
        self.hand_text.delete('1.0', tk.END)
        self.hand_text.insert(tk.END, hand)

    def update_cmd(self, cmd):
        self.cmd_text.delete('1.0', tk.END)
        self.cmd_text.insert(tk.END, cmd)

    def send_check(self):
        self.s.send(bytes("check", "utf-8"))

    def send_call(self):
        self.s.send(bytes("call", "utf-8"))

    def send_fold(self):
        self.s.send(bytes("fold", "utf-8"))

    def back(self):
        self.s.send(bytes("back", 'utf-8'))
        self.controller.show_frame('ChooseGamePage')
        self.clear()

    def clear(self):
        self.bet_entry.delete(0, tk.END)
        self.hand_text.delete('1.0', tk.END)
        self.cmd_text.delete('1.0', tk.END)

    def handle_message(self, data):
        if data is not None:
            if data[0] == SendDataType.STRING:
                msg = data[1].decode()
                if msg.startswith("cards:"):
                    self.update_hand(msg[6:])
                else:
                    self.update_cmd(msg)

