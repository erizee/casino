import tkinter as tk
from tkinter import messagebox
import socket
from helpers import SendDataType, receive_data
from _thread import *


class BlackjackGamePage(tk.Frame):
    def __init__(self, parent, controller, width, height, **kw):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.running = 1

        self.parent = parent
        self.controller = controller
        self.s = self.controller.s

        self.label = tk.Label(self, text="Welcome to the Blackjack game!")
        self.label.pack()

        self.bet_entry = tk.Entry(self)
        self.bet_entry.pack()

        self.bet_button = tk.Button(self, text="Place Bet", command=self.place_bet)
        self.bet_button.pack()

        # self.play_button = tk.Button(self, text="Play", command=self.play)
        # self.play_button.pack()

        self.back_button = tk.Button(self, text="Go back", command=self.back)
        self.back_button.pack()

        self.ph_label = tk.Label(self, text="Your cards:")
        self.ph_label.pack()

        self.player_hand = tk.Text(self, width=30, height=2)
        self.player_hand.pack()

        self.dh_label = tk.Label(self, text="Dealer cards:")
        self.dh_label.pack()

        self.dealer_hand = tk.Text(self, width=30, height=2)
        self.dealer_hand.pack()

        self.hit_button = tk.Button(self, text="Hit", command=self.hit)
        self.hit_button.pack()

        self.stand_button = tk.Button(self, text="Stand", command=self.stand)
        self.stand_button.pack()

        self.cmd_text = tk.Text(self, width=30, height=6)
        self.cmd_text.pack()

        self.result_text = tk.Text(self, width=30, height=3)
        self.result_text.pack()

    def place_bet(self):
        self.result_text.delete('1.0', tk.END)
        bet = self.bet_entry.get()
        self.s.send(bytes(f"bet {bet}", "utf-8"))

    def update_hand(self, hand, hand_str):
        hand.delete('1.0', tk.END)
        hand.insert(tk.END, hand_str)

    def update_cmd(self, cmd):
        self.cmd_text.delete('1.0', tk.END)
        self.cmd_text.insert(tk.END, cmd)

    def update_result(self, msg):
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, msg)

    def hit(self):
        self.s.send(bytes("hit", "utf-8"))

    def stand(self):
        self.s.send(bytes("stand", "utf-8"))

    def back(self):
        self.s.send(bytes("back", 'utf-8'))
        self.clear()
        self.controller.show_frame('ChooseGamePage')

    def clear(self):
        self.bet_entry.delete(0, tk.END)
        self.dealer_hand.delete('1.0', tk.END)
        self.player_hand.delete('1.0', tk.END)
        self.cmd_text.delete('1.0', tk.END)

    # def play(self):
    #     self.s.send(bytes("play blackjack", "utf-8"))

    def handle_message(self, data):
        if data is not None:
            if data[0] == SendDataType.STRING:
                msg = data[1].decode()
                if msg.startswith("Your"):
                    self.update_hand(self.player_hand, msg[12:])
                elif msg.startswith("Dealer cards"):
                    self.update_hand(self.dealer_hand, msg[13:])
                elif msg.startswith("You "):
                    self.update_result(msg)
                else:
                    self.update_cmd(msg)


