import tkinter as tk
import ttkbootstrap as ttk
from helpers import SendDataType


class BingoGamePage(tk.Frame):
    def __init__(self, parent, controller, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller
        self.s = self.controller.s

        # GUI variables
        self.bingo_numbers = []
        self.messages_output = None
        self.current_number_label = None
        self.bet_entry = None
        self.bingo_button = None

        # Split screen into two halves
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Left half
        left_frame = tk.Frame(self)
        left_frame.grid(row=0, column=0, sticky="nsew")

        self.create_betting_option(left_frame)
        self.create_messages_output(left_frame)
        self.create_current_number_label(left_frame)
        self.create_back_button(left_frame)

        # Right half
        right_frame = tk.Frame(self)
        right_frame.grid(row=0, column=1, sticky="nsew")

        self.create_bingo_grid(right_frame)

    def create_bingo_grid(self, parent):
        self.bingo_numbers = []

        for i in range(5):
            number_row = []
            frame = tk.Frame(parent)
            frame.pack(side="top", pady=5)
            for j in range(5):
                number = tk.StringVar()
                button = tk.Button(
                    frame,
                    textvariable=number,
                    font=("Candara", 14),
                    background="#375A7F",
                    foreground="#FFFFFF",
                    borderwidth=1,
                    relief="solid",
                    width=6,
                    height=3,
                    anchor="center",
                    command=lambda row=i, col=j: self.button_click(row, col)
                )
                number_row.append(number)
                button.pack(side="left", padx=5)
            self.bingo_numbers.append(number_row)

        bingo_frame = tk.Frame(parent)
        bingo_frame.pack(side="top", pady=10)
        self.bingo_button = tk.Button(
            bingo_frame,
            text="Bingo!",
            font=("Candara", 14),
            background="#375A7F",
            foreground="#FFFFFF",
            borderwidth=1,
            relief="solid",
            width=10,
            height=3,
            command=self.bingo_button_click
        )
        self.bingo_button.pack()

    def bingo_button_click(self):
        self.s.send(bytes("bingo", "utf-8"))

    def update_bingo_numbers(self, numbers):
        for i in range(5):
            for j in range(5):
                self.bingo_numbers[i][j].set(numbers[i][j])

    def create_current_number_label(self, parent):
        self.current_number_label = tk.Label(
            parent,
            font=("Candara", 14),
            bg="#375A7F",
            fg="#FFFFFF",
            justify="center",
            width=15,
            height=3
        )
        self.current_number_label.pack(pady=10)

    def update_current_number(self, number):
        self.current_number_label.config(text=number)

    def create_betting_option(self, parent):
        self.bet_entry = tk.StringVar()
        bet_label = tk.Label(
            parent,
            text="Enter bet amount",
            font=("Candara", 13),
            fg="#FFFFFF",
            justify="center"
        )
        bet_label.pack(pady=10)

        bet_entry = ttk.Entry(
            parent,
            font=("Candara", 13),
            textvariable=self.bet_entry
        )
        bet_entry.pack(pady=10)

        place_bet_btn = tk.Button(
            parent,
            text="Place Bet",
            command=self.place_bet,
            bg="#375A7F",
            font=("Candara", 13),
            fg="#FFFFFF",
            justify="center",
            width=10
        )
        place_bet_btn.pack(pady=10)

    def create_messages_output(self, parent):
        self.messages_output = tk.Listbox(
            parent,
            font=("Candara", 13),
            bg="#375A7F",
            fg="#FFFFFF",
            relief="solid",
            width=40,
            height=10
        )
        self.messages_output.pack(padx=10, pady=10)

    def show_message(self, message):
        self.messages_output.insert(tk.END, message)
        self.messages_output.yview(tk.END)

    def button_click(self, row, col):
        self.s.send(bytes(f"{row}, {col}", 'utf-8'))

    def place_bet(self):
        bet_amount = self.bet_entry.get()
        self.s.send(bytes(f"bet {bet_amount}", 'utf-8'))

    def create_back_button(self, parent):
        back_button = tk.Button(
            parent,
            text="Back",
            command=self.back,
            bg="#375A7F",
            font=("Candara", 13),
            fg="#FFFFFF",
            justify="center",
            width=10
        )
        back_button.pack(pady=10)

    def back(self):
        self.s.send(bytes("back", 'utf-8'))
        self.controller.show_frame('ChooseGamePage')
        self.clear()

    def clear(self):
        self.messages_output.delete(0, tk.END)
        self.bet_entry.set("")

    def handle_message(self, data):
        if data is not None:
            if data[0] == SendDataType.STRING:
                msg = data[1].decode()
                if msg[:16] == "Current number: ":
                    self.update_current_number(int(msg[16:]))
                elif msg[:4] == "Your":
                    board = [[sign for sign in row.split()] for row in msg[18:].split('\n') if row]
                    self.update_bingo_numbers(board)
                else:
                    self.show_message(msg)
