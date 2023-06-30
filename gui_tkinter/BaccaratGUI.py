import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk

translator = {'2': '2',
              '3': '3',
              '4': '4',
              '5': '5',
              '6': '6',
              '7': '7',
              '8': '8',
              '9': '9',
              '10': '10',
              'A': 'ace',
              'J': 'jack',
              'K': 'king',
              'Q': 'queen',
              "♠": "spades",
              "♥": "hearts",
              "♦": "diamonds",
              "♣": "clubs"}


class BaccaratGamePage(tk.Frame):
    def __init__(self, parent, controller, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller
        self.s = self.controller.s
        self.player_cards_list = []
        self.banker_cards_list = []
        # GUI
        self.gui_elements = {}
        self.images = dict()
        self.init_images()
        self.ft = ('Candara', 13)
        self.message_entry = tk.StringVar()
        self.back_button = self.create_back_button()
        self.side_frame = self.create_side_frame()
        self.main_frame = self.create_main_frame()
        self.player_cards = self.gui_elements["player_cards"]
        self.banker_cards = self.gui_elements["banker_cards"]

    def create_back_button(self):
        self.gui_elements['back_button'] = tk.Button(self, text="Back", command=self.back, font=self.ft, fg="#FFFFFF",
                                                     justify='center', width=10)
        self.gui_elements['back_button'].pack(side=tk.TOP, anchor=tk.NW, padx=10, pady=10)
        return self.gui_elements['back_button']

    def create_side_frame(self):
        self.gui_elements['side_frame'] = tk.Frame(self)
        self.gui_elements['side_frame'].pack(side=tk.TOP, padx=10, pady=10)

        self.gui_elements['message_entry'] = tk.Entry(self.gui_elements['side_frame'], font=self.ft, textvariable=self.message_entry)
        self.gui_elements['message_entry'].pack(padx=10, pady=10, ipadx=10, ipady=6)

        self.create_button_frame()
        return self.gui_elements['side_frame']

    def create_button_frame(self):
        self.gui_elements['button_frame'] = tk.Frame(self.gui_elements['side_frame'])
        self.gui_elements['button_frame'].pack(side=tk.LEFT, padx=10, pady=10)

        self.gui_elements['player_button'] = tk.Button(self.gui_elements['button_frame'], text='Bet player',
                                                       command=lambda: self.send_message("player"), font=self.ft,
                                                       fg="#FFFFFF", justify='center', width=10)
        self.gui_elements['player_button'].pack(side=tk.LEFT, padx=10, pady=10)

        self.gui_elements['banker_button'] = tk.Button(self.gui_elements['button_frame'], text='Bet banker',
                                                       command=lambda: self.send_message("banker"), font=self.ft,
                                                       fg="#FFFFFF", justify='center', width=10)
        self.gui_elements['banker_button'].pack(side=tk.LEFT, padx=10, pady=10)

    def create_main_frame(self):
        self.gui_elements['main_frame'] = tk.Frame(self)
        self.gui_elements['main_frame'].pack(side=tk.TOP, padx=10, pady=10)

        self.create_cards_container('Player cards', 'player')
        self.create_cards_container(' ', 'empty')
        self.create_cards_container('Banker cards', 'banker')
        return self.gui_elements['main_frame']

    def create_cards_container(self, text, prefix):
        self.gui_elements[f'{prefix}_cards'] = tk.Frame(self.gui_elements['main_frame'], borderwidth=2)
        self.gui_elements[f'{prefix}_cards'].pack(side=tk.LEFT)

        self.gui_elements[f'{prefix}_label'] = tk.Label(self.gui_elements[f'{prefix}_cards'], text=text,
                                                     font=self.ft, fg="#FFFFFF", justify='center')
        self.gui_elements[f'{prefix}_label'].pack()

    def init_images(self):
        for side in ["clubs", "diamonds", "spades", "hearts"]:
            for figure in ["ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "king", "queen"]:
                self.images[f"{figure}_of_{side}"] = ImageTk.PhotoImage(
                    Image.open(f"assets/cards/{figure}_of_{side}.png").resize((50, 90)))

    def handle_message(self, data):
        message_body = data[1].decode()
        message_split = message_body.split(" ")
        if "Player:" in message_body:
            lines = message_body.split("\n")
            cards = lines[1].split(":")
            player_cards = cards[0].split(" ")
            banker_cards = cards[1].split(" ")
            self.show_cards(player_cards, self.player_cards_list, self.player_cards)
            self.show_cards(banker_cards, self.banker_cards_list, self.banker_cards)
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

    def show_cards(self, cards, displayed_cards_list, cards_box):
        for card in displayed_cards_list:
            card.pack_forget()
        for card in cards:
            path = f"{translator[card[:-1]]}_of_{translator[card[-1]]}"
            img_el = tk.Label(cards_box, image=self.images[path], fg="#FFFFFF", justify='center')
            img_el.pack(side='left', padx=10)
            displayed_cards_list.append(img_el)

    def send_message(self, bet_type):
        message = self.message_entry.get()
        self.s.send(bytes(f"bet {bet_type} {message}", 'utf-8'))
        self.message_entry.set("")

    def back(self):
        self.s.send(bytes("back", 'utf-8'))
        self.controller.show_frame('ChooseGamePage')
        self.clear()

    def clear(self):
        self.message_entry.set("")
