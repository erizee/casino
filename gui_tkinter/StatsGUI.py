import tkinter as tk
import ttkbootstrap as ttk


class StatPage(ttk.Frame):

    def __init__(self, parent, controller, width, height):
        ttk.Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller
        self.total = 100
        self.total_str = tk.StringVar()

        self.fn = ('Candara', 13)

        self.frame = ttk.Frame(self, padding=20)
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        games = ["baccarat", "poker", "blackjack", "bingo", "roulette", "dice"]
        headers = ["Game", "Games Lost", "Games Won", "Sum of Money Won", "Sum of Money Lost"]
        self.table_objects = {}

        # Create table headers
        for col, header in enumerate(headers):
            label = ttk.Label(self.frame, text=header, anchor=tk.CENTER, width=20,font=self.fn)
            label.grid(row=0, column=col, sticky="nsew")

        # Create table rows
        for row, game in enumerate(games):
            label_game = ttk.Label(self.frame, text=game, anchor=tk.CENTER, width=20,font=self.fn)
            label_game.grid(row=row + 1, column=0, sticky="nsew")

            label_lost = ttk.Label(self.frame, text="0", anchor=tk.CENTER, width=20,font=self.fn)
            label_lost.grid(row=row + 1, column=1, sticky="nsew")

            label_won = ttk.Label(self.frame, text="0", anchor=tk.CENTER, width=20,font=self.fn)
            label_won.grid(row=row + 1, column=2, sticky="nsew")

            label_sum_won = ttk.Label(self.frame, text="0", anchor=tk.CENTER, width=20,font=self.fn)
            label_sum_won.grid(row=row + 1, column=3, sticky="nsew")

            label_sum_lost = ttk.Label(self.frame, text="0", anchor=tk.CENTER, width=20,font=self.fn)
            label_sum_lost.grid(row=row + 1, column=4, sticky="nsew")

            self.table_objects[game] = {
                'label_game': label_game,
                'label_lost': label_lost,
                'label_won': label_won,
                'label_sum_won': label_sum_won,
                'label_sum_lost': label_sum_lost}

        button = ttk.Button(self, text="Back", command=self.back)
        button.pack(anchor="nw", padx=10, pady=10)

        label_total = ttk.Label(self, text="Total: ", anchor=tk.CENTER, width=20, textvariable=self.total_str,font=self.fn)
        label_total.pack(anchor="s")
    def show_error_message(self, message):
        error = ttk.Label(text=message, bootstyle="danger", font=self.fn)
        error.place(relx=0.5, rely=0.2, anchor='n')
        error.after(3000, lambda: error.place_forget())

    def handle_message(self, data):
        message_body = data[1].decode()
        message_split = message_body.split(":")
        try:
            if "Stat" in message_body:
                stats = eval(message_split[1])
                for stat in stats:
                    gui_object = self.table_objects.get(stat[0])
                    if gui_object is not None:
                        gui_object['label_lost']['text'] = str(stat[1]-stat[2])
                        gui_object['label_won']['text'] = str(stat[2])
                        gui_object['label_sum_won']['text'] = str(stat[3])
                        gui_object['label_sum_lost']['text'] = str(stat[4])
                        self.total = self.total + stat[3] - stat[4]
                        self.total_str.set("Balance: " +str(self.total))
        except Exception as e:
            print(e)

    def back(self):
        self.total = 100
        self.controller.show_frame("ChooseGamePage")
