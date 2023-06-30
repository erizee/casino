import socket
import tkinter as tk
import ttkbootstrap as ttk
from helpers import receive_data
import threading
from gameRoom import GAMES
from DiceGUI import DiceGamePage
from RouletteGUI import RouletteGamePage
from BingoGUI import BingoGamePage
from BlackjackGUI import BlackjackGamePage
from BaccaratGUI import BaccaratGamePage
from StatsGUI import StatPage
from PokerGUI import PokerGamePage

HOST = "127.0.0.1"
PORT = 65432
running = True
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class SampleApp(ttk.Window):

    def __init__(self, *args, **kwargs):
        ttk.Window.__init__(self, *args, themename='darkly', **kwargs)

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.s = s
        self.curr_frame = None

        self.width, self.height = 900, 600
        self.geometry(f"{self.width}x{self.height}")
        self.minsize(self.width, self.height)
        self.frames = {}

        self.protocol("WM_DELETE_WINDOW", self.on_exit)

        for F in (
                LoginPage, ChooseGamePage, BaccaratGamePage, DiceGamePage, RouletteGamePage, BingoGamePage,
                BlackjackGamePage, PokerGamePage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self, width=self.winfo_height(), height=self.winfo_height())
            if page_name == "GamePage":
                self.handle_function = self.empty_handler
            self.frames[page_name] = frame
            self.update_idletasks()

        self.frames["stat"] = StatPage(parent=self.container, controller=self, width=self.winfo_height(),
                                       height=self.winfo_height())
        self.update_idletasks()

        self.show_frame("LoginPage")

    def on_exit(self):
        global running
        running = False
        self.destroy()

    def show_frame(self, page_name):
        if self.curr_frame is not None:
            self.curr_frame.grid_forget()
        frame = self.frames[page_name]
        frame.grid(row=0, column=0, sticky="nsew")
        self.curr_frame = frame
        self.handle_function = frame.handle_message

    def empty_handler(self, message):
        pass

    def receive_messages(self):
        global running
        while running:
            try:
                data = receive_data(s)
                if data is not None:
                    print(f"{data[1].decode()}")
                    self.handle_function(data)
            except Exception as e:
                print(e)
                app.destroy()
        print("not running")


class LoginPage(ttk.Frame):

    def __init__(self, parent, controller, width, height):
        ttk.Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller

        self.fn = ('Candara', 13)

        self.main_frame = ttk.Frame(self)

        self.login_header = ttk.Label(self.main_frame, text="Enter your username", font=self.fn)
        self.login_header.pack(anchor='center', expand=True)

        self.login_input_value = tk.StringVar()
        self.login_input = ttk.Entry(self.main_frame, textvariable=self.login_input_value, font=self.fn)
        self.login_input.pack(pady=40, anchor='center', expand=True)

        self.login_button = tk.Button(self.main_frame, text='Login', command=self.login, font=self.fn)
        self.login_button.pack(pady=30, anchor='center', expand=True, ipadx=20)

        self.bind('<Return>', lambda event: self.login())
        self.login_input.bind('<Return>', lambda event: self.login())

        self.main_frame.place(relx=0.5, rely=0.5, anchor='center')

    def login(self):
        value = self.login_input_value.get()
        print(value)
        try:
            if value is not None:
                s.connect((HOST, PORT))
                s.send(bytes(value, "utf-8"))
                receive_thread = threading.Thread(target=self.controller.receive_messages)
                receive_thread.start()
                self.controller.show_frame("ChooseGamePage")
        except:
            self.show_error_message("Could not connect to server, try again")

    def show_error_message(self, message):
        error = ttk.Label(text=message, bootstyle="danger", font=self.fn)
        error.place(relx=0.5, rely=0.2, anchor='n')
        error.after(3000, lambda: error.place_forget())

    def handle_message(self, data):
        pass


class ChooseGamePage(tk.Frame):

    def __init__(self, parent, controller, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)
        buttons = []
        self.controller = controller
        self.parent = parent

        self.fn = ('Candara', 13)

        curr_row = 0
        curr_col = 0
        i = 0

        self.rowconfigure((0, 1, 2), weight=1, uniform='a')
        self.columnconfigure(0, weight=1, uniform='a')

        self.header = ttk.Frame(self)
        self.main = ttk.Frame(self)

        self.main.rowconfigure((0, 1), weight=1, uniform='a')
        self.main.columnconfigure((0, 1, 2), weight=1, uniform='a')

        self.header.grid(row=0, column=0, sticky='nsew')
        self.main.grid(row=1, column=0, rowspan=2, sticky='nsew')

        for game in GAMES:
            buttons.append(tk.Button(self.main, text=f"{game}", font=self.fn))
            buttons[i].grid(row=curr_row, column=curr_col, sticky='nsew', padx=10, pady=10)
            buttons[i].bind(f"<Button-1>", self.callback)

            i += 1
            curr_col += 1
            if curr_col >= 3:
                curr_col = 0
                curr_row += 1

        self.stat_btn = tk.Button(self, text=f"Stat", font=self.fn, command=self.load_stats)
        self.stat_btn.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

    def handle_message(self, data):
        pass

    def load_stats(self):
        self.controller.show_frame("stat")
        s.send(bytes(f"stat", 'utf-8'))

    def callback(self, event):
        clicked_btn = event.widget
        self.load_game(clicked_btn['text'])

    def load_game(self, name):
        print(f"play {name}")
        s.send(bytes(f"play {name}", 'utf-8'))
        self.controller.show_frame(name.title() + "GamePage")


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
