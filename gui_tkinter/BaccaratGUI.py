import socket
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, scrolledtext, TOP, NW
from helpers import receive_data, SendDataType
import threading
from gameRoom import GAMES
import tkinter.font as font
from PIL import Image, ImageTk

translator = {'2':'2',
              '3':'3',
              '4':'4',
              '5':'5',
              '6':'6',
              '7':'7',
              '8':'8',
              '9':'9',
              '10':'10',
              'A':'ace',
              'J':'jack',
              'K':'king',
              'Q':'queen',
              "♠":"spades",
              "♥":"hearts",
              "♦":"diamonds",
              "♣":"clubs"}



class BaccaratGamePage(tk.Frame):
    def __init__(self, parent, controller, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller
        self.s = self.controller.s

        self.images = dict()
        self.init_images()

        self.player_cards_list = []
        self.banker_cards_list = []

        self.ft = ('Candara', 13)

        self.back_button = tk.Button(self, text="Back", command=self.back, font=self.ft, fg="#FFFFFF", justify='center', width=10)
        self.back_button.pack(side=TOP, anchor=NW, padx=10, pady=10)

        self.side_frame = tk.Frame(self)
        self.side_frame.pack(side=tk.TOP, padx=10, pady=10)

        # Set up the message entry and send button
        self.message_entry = tk.Entry(self.side_frame, font=self.ft)
        self.message_entry.pack(padx=10, pady=10, ipadx=10, ipady=6)

        self.button_frame = tk.Frame(self.side_frame)
        self.button_frame.pack(side=tk.LEFT, padx=10, pady=10)
        self.player_button = tk.Button(self.button_frame, text='Bet player', command=lambda : self.send_message("player"), font=self.ft, fg="#FFFFFF", justify='center', width=10)
        self.player_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.banker_button = tk.Button(self.button_frame, text='Bet banker', command=lambda : self.send_message("banker"), font=self.ft, fg="#FFFFFF", justify='center', width=10)
        self.banker_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side=tk.TOP, padx=10, pady=10)

        self.player_cards = tk.Frame(self.main_frame, borderwidth="1px")
        self.player_cards.pack(side=tk.LEFT)
        self.banker_cards = tk.Frame(self.main_frame)
        self.banker_cards.pack(side=tk.LEFT)

        self.player_label = tk.Label(self.player_cards, text='Player cards', font=self.ft, fg="#FFFFFF", justify='center')
        self.player_label.pack()

        self.banker_label = tk.Label(self.banker_cards, text='Banker cards', font=self.ft, fg="#FFFFFF", justify='center')
        self.banker_label.pack()

        # Set up the message listbox
        self.message_listbox = scrolledtext.ScrolledText(self, height=20)
        #self.message_listbox.pack(side=tk.TOP, padx=10, pady=10)

    def init_images(self):
        for side in ["clubs","diamonds","spades","hearts"]:
            for figure in ["ace","2","3","4","5","6","7","8","9","10","jack","king","queen"]:
                self.images[f"{figure}_of_{side}"] = ImageTk.PhotoImage(Image.open(f"assets/cards/{figure}_of_{side}.png").resize((50, 90)))

    def handle_message(self, data):
        message_body = data[1].decode()
        message_split = message_body.split(" ")
        if "Player:" in message_body:
            lines = message_body.split("\n")
            cards = lines[1].split(":")
            player_cards = cards[0].split(" ")
            banker_cards = cards[1].split(" ")
            self.show_cards(player_cards, banker_cards)
        elif "wins!" in message_body:
            error = ttk.Label(text=f"{message_body}", bootstyle='light', font=('Candara', 13))
            error.place(relx=0.5, rely=0.7, anchor='n')
            error.after(4000, lambda: error.place_forget())
        elif "Outcome" in message_body:
            error = ttk.Label(text=f"{message_body}", bootstyle='light', font=('Candara', 13))
            error.place(relx=0.5, rely=0.8, anchor='n')
            error.after(4000, lambda: error.place_forget())
        elif "Not" in message_body or "Invalid" in message_body:
            error = ttk.Label(text=f"{message_body}", bootstyle='light', font=('Candara', 13))
            error.place(relx=0.5, rely=0.15, anchor='n')
            error.after(4000, lambda: error.place_forget())
        else:
            self.message_listbox.insert(tk.END, f"{message_body}\n")

    def show_cards(self, player_cards, banker_cards):
        for card in self.player_cards_list:
            card.pack_forget()

        for card in self.banker_cards_list:
            card.pack_forget()

        for card in player_cards:
            path=f"{translator[card[:-1]]}_of_{translator[card[-1]]}"
            img_el = tk.Label(self.player_cards, image=self.images[path], fg="#FFFFFF", justify='center')
            img_el.pack(side='left', padx=10)
            self.player_cards_list.append(img_el)

        for card in banker_cards:
            path = f"{translator[card[:-1]]}_of_{translator[card[-1]]}"
            img_el = tk.Label(self.banker_cards, image=self.images[path], fg="#FFFFFF", justify='center')
            img_el.pack(side='left', padx=10)
            self.banker_cards_list.append(img_el)

    def send_message(self, bet_type):
        message = self.message_entry.get()
        self.s.send(bytes(f"bet {bet_type} {message}", 'utf-8'))
        self.message_entry.delete(0, tk.END)


    def back(self):
        self.s.send(bytes("back", 'utf-8'))
        self.controller.show_frame('ChooseGamePage')
        self.clear()

    def clear(self):
        self.message_listbox.delete('1.0', tk.END)
        self.message_entry.delete(0, tk.END)
