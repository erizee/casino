import socket
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, scrolledtext, TOP, NW
from helpers import receive_data, SendDataType
import threading
from gameRoom import GAMES
import tkinter.font as font
from PIL import Image, ImageTk


class DiceGamePage(tk.Frame):

    def __init__(self, parent, controller, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller
        self.s = self.controller.s

        self.isRollTime = 0
        self.isBetTime = 0
        self.isMeShooter = 0

        self.dice_imgs = self.init_dice_imgs()

        self.ft = ('Candara', 13)

        self.back_btn = tk.Button(self, bg="#375A7F", font=self.ft, fg="#FFFFFF", justify='center', text="Back",
                                  command=self.back)
        self.back_btn.place(x=10, y=10, width=70)

        self.roll_frame = tk.Frame(self)
        self.roll_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1, anchor='nw')

        self.fake_label_top_roll = tk.Label(self.roll_frame)
        self.fake_label_top_roll.pack(expand=True)

        self.dice_frame = tk.Frame(self.roll_frame)

        self.dice_1 = tk.Label(self.dice_frame, image=self.dice_imgs[0], fg="#FFFFFF", justify='center')
        self.dice_1.pack(side='left', padx=10)

        self.dice_2 = tk.Label(self.dice_frame, image=self.dice_imgs[0], fg="#FFFFFF", justify='center')
        self.dice_2.pack(side='left', padx=10)

        self.dice_frame.pack(pady=20)

        self.roll_btn = tk.Button(self.roll_frame, bg="#375A7F", font=self.ft, fg="#FFFFFF", justify='center', text="Roll",
                                  command=self.roll, width=10)
        self.roll_btn.pack(pady=10)

        self.fake_label_bottom_roll = tk.Label(self.roll_frame)
        self.fake_label_bottom_roll.pack(expand=True)

        self.bet_frame = tk.Frame(self)
        self.bet_frame.place(relx=0.5, y=7, relwidth=0.5, relheight=1, anchor='nw')

        self.fake_label_top = tk.Label(self.bet_frame)
        self.fake_label_top.pack(expand=True)

        self.bet_label = tk.Label(self.bet_frame, font=self.ft, fg="#FFFFFF", justify='center', text="Enter bet amount")
        self.bet_label.pack(pady=20)

        self.bet_entry = ttk.Entry(self.bet_frame, font=self.ft, text="Entry")
        self.bet_entry.pack(pady=20)

        self.btn_frame = tk.Frame(self.bet_frame)
        self.btn_frame.pack(pady=30)

        self.pass_btn = tk.Button(self.btn_frame, background="#375A7F", font=self.ft, fg="#FFFFFF", justify='center', text=" pass"
                                  , command=self.pass_handler, width=10)
        self.pass_btn.pack(side='left', expand=True, padx=20)

        self.dpass_btn = tk.Button(self.btn_frame, background="#375A7F", font=self.ft, fg="#FFFFFF", justify='center',
                                   text="dpass"
                                   , command=self.dpass_handler, width=10)
        self.dpass_btn.pack(side='left', expand=True, padx=20)

        self.fake_label_bottom = tk.Label(self.bet_frame)
        self.fake_label_bottom.pack(expand=True)

        self.messages_output = tk.Listbox(self, borderwidth='1px', font=self.ft,  fg="#FFFFFF", justify='center',
                                          height=5, bg="#000000")
        self.messages_output.R = 255
        self.messages_output.G = 255
        self.messages_output.B = 255
        self.messages_output.place(relx=0.5, y=10, relwidth=0.7, anchor='n')

        self.back_btn.tkraise()

    def show_message(self, message):
        self.messages_output.insert(tk.END, f"{message}\n")
        self.messages_output.yview(tk.END)

    def init_dice_imgs(self):
        return [ImageTk.PhotoImage(Image.open(f"assets/dice-{i}.png").resize((110, 110))) for i in range(1, 7)]

    def dpass_handler(self):
        if self.bet_entry.get() is not None and self.bet_entry.get().isnumeric() and self.isBetTime:
            self.s.send(bytes(f"dpass {self.bet_entry.get()}", 'utf-8'))
        self.bet_entry.delete(0, tk.END)

    def pass_handler(self):
        if self.bet_entry.get() is not None and self.bet_entry.get().isnumeric() and self.isBetTime:
            self.s.send(bytes(f"pass {self.bet_entry.get()}", 'utf-8'))
        self.bet_entry.delete(0, tk.END)

    def roll(self):
        if self.isRollTime:
            self.isRollTime = 0
            self.roll_btn['bg'] = "#375A7F"
            self.s.send(bytes("roll", 'utf-8'))

    def handle_message(self, data):
        message_body = data[1].decode()
        message_split = message_body.split(" ")

        if len(message_split) == 0:
            return
        elif message_body == "Its betting time":
            self.isBetTime = 1
        elif message_body == "You are a shooter":
            self.isMeShooter = 1
        elif message_split[0] == "Disconnected":
            self.controller.show_frame('ChooseGamePage')
        elif message_body == "Bets ended, time for shooter to roll!":
            # self.show_message("Bets ended, time for shooter to roll!")
            self.isRollTime = 1
            if self.isMeShooter:
                self.roll_btn['bg'] = 'green'
        elif message_split[0] == "Rolled":
            str_tuple_1 = message_split[1]
            str_tuple_2 = message_split[2]
            self.dice_1['image'] = self.dice_imgs[int(str_tuple_1[1]) - 1]
            self.dice_2['image'] = self.dice_imgs[int(str_tuple_2[0]) - 1]

        if "waiting for next roll!" in message_body:
            self.isRollTime = 1
            self.roll_btn['bg'] = 'green'
        if "Rolled" not in message_body:
            self.show_message(message_body)

    def back(self):
        self.s.send(bytes("back", 'utf-8'))
        self.controller.show_frame('ChooseGamePage')
        self.clear()

    def clear(self):
        self.messages_output.delete(0, tk.END)
        self.bet_entry.delete(0, tk.END)
        self.roll_btn['bg'] = "#375A7F"
