import tkinter as tk
from helpers import SendDataType


class PokerGamePage(tk.Frame):
    def __init__(self, parent, controller, width, height, **kw):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.running = 1

        self.parent = parent
        self.controller = controller
        self.s = self.controller.s

        self.label = tk.Label(self, text="Welcome to the Poker game!")
        self.label.pack()

        self.bet_entry = tk.Entry(self)
        self.bet_entry.pack()

        self.bet_button = tk.Button(self, text="Bet", command=self.place_bet)
        self.bet_button.pack(pady=5)

        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack()

        self.fold_button = tk.Button(self.buttons_frame, text="Fold", command=self.send_fold)
        self.fold_button.pack(side="left", padx=5)

        self.call_button = tk.Button(self.buttons_frame, text="Call", command=self.send_call)
        self.call_button.pack(side="left", padx=5)

        self.raise_button = tk.Button(self.buttons_frame, text="Raise", command=self.place_raise)
        self.raise_button.pack(side="left", padx=5)

        self.check_button = tk.Button(self.buttons_frame, text="Check", command=self.send_check)
        self.check_button.pack(side="left", padx=5)

        self.discard_button = tk.Button(self, text="Discard", command=self.send_discard)
        self.discard_button.pack(pady=5)

        self.hand_text = tk.Text(self, width=30, height=10)
        self.hand_text.pack(pady=5)

        self.cmd_text = tk.Text(self, width=30, height=10)
        self.cmd_text.pack(pady=5)

        self.back_button = tk.Button(self, text="Go back", command=self.back)
        self.back_button.pack(pady=5)

    def place_bet(self):
        bet_amount = self.bet_entry.get()
        self.s.send(bytes(f"bet {bet_amount}", "utf-8"))

    def place_raise(self):
        raise_amount = self.bet_entry.get()
        self.s.send(bytes(f"raise {raise_amount}", "utf-8"))

    def send_discard(self):
        cards_to_discard = self.bet_entry.get()
        print(cards_to_discard)
        self.s.send(bytes("discard"+cards_to_discard, "utf-8"))

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
