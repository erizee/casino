import socket
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, scrolledtext, TOP, NW
from helpers import receive_data, SendDataType
import threading
from gameRoom import GAMES
import tkinter.font as font
from PIL import Image, ImageTk

class RouletteGamePage(tk.Frame):

    def __init__(self, parent, controller, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller
        self.s = self.controller.s

        self.isBetTime = 0
        self.ft = ('Candara', 13)
        self.roulette_fonts = {'red':'black', 'black':'red', 'green':'black'}

        self.middle_frame = tk.Frame(self)
        self.middle_frame.place(relx=0.5, rely=0.55, relwidth=0.8, relheight=0.8, anchor='center')

        roulette_outcome = tk.Label(self.middle_frame, font=self.ft, fg="#333333", justify='center', text="", width=9, height=4)
        self.roulette_outcome = roulette_outcome
        self.roulette_outcome.place(relx=0.5, rely=0.3, anchor='center')

        bet_entry = tk.Entry(self.middle_frame, bg="#375A7F", font=self.ft, fg="#FFFFFF", justify='center', borderwidth="1px", text="Entry")
        self.bet_entry = bet_entry
        self.bet_entry.place(relx=0.5, rely=0.55, anchor='center')

        self.buttons_frame = tk.Frame(self.middle_frame)
        self.buttons_frame.place(relx=0.5, rely=0.79, anchor='center', relwidth=1, relheight=0.2)

        red_btn = tk.Button(self.buttons_frame, bg="#375A7F", font=self.ft, fg="#FFFFFF", justify='center', text="Red", width=10)
        red_btn["command"] = lambda: self.bet_handler("red")
        self.red_btn = red_btn
        self.red_btn.place(relx=0, y=0, anchor='nw')

        green_btn = tk.Button(self.buttons_frame,bg="#375A7F", font=self.ft, fg="#FFFFFF", justify='center', text="Green", width=10)
        green_btn["command"] = lambda: self.bet_handler("green")
        self.green_btn = green_btn
        self.green_btn.place(relx=0.5, y=0, anchor='n')

        black_btn = tk.Button(self.buttons_frame, bg="#375A7F", font=self.ft, fg="#FFFFFF", justify='center', text="Black", width=10)
        black_btn["command"] = lambda: self.bet_handler("black")
        self.black_btn = black_btn
        self.black_btn.place(relx=1, y=0, anchor='ne')

        back_btn = tk.Button(self, bg="#375A7F", font=self.ft, fg="#FFFFFF", justify='center', text="Back",
                                  command=self.back, width=10)
        self.back_btn = back_btn
        self.back_btn.place(x=20, y=20)


        self.messages_output = tk.Listbox(self.middle_frame, font=self.ft, fg="#FFFFFF", justify='center', borderwidth="1px")
        #self.messages_output.place(relx=0.5, rely=0.8, anchor='n')

    def bet_handler(self, type):
        if self.bet_entry.get() is not None and self.bet_entry.get().isnumeric():
            self.s.send(bytes(f"bet {type} {self.bet_entry.get()}", 'utf-8'))
        self.bet_entry.delete(0, tk.END)

        self.ft = font.Font(family='Times', size=10)

    def handle_message(self, data):
        message_body = data[1].decode()
        message_split = message_body.split(" ")

        if "Number rolled:" in message_body:
            self.roulette_outcome['text'] = message_split[2]
            self.roulette_outcome['bg'] = message_split[4]
            font_color = self.roulette_fonts.get(message_split[4], 'black')
            self.roulette_outcome['fg'] = font_color
        elif "You lost" in message_body:
            self.display_alert(f"{message_body}\n", "danger")
        elif "You won" in message_body:
            self.display_alert(f"{message_body}\n", "success")
        else:
            self.display_alert(f"{message_body}\n", "light")

        #self.messages_output.insert(tk.END, f"{message_body}\n")

    def back(self):
        self.s.send(bytes("back", 'utf-8'))
        self.controller.show_frame('ChooseGamePage')

    def display_alert(self, message, color):
        error = ttk.Label(text=message, bootstyle=color, font=('Candara', 13))
        error.place(relx=0.5, rely=0.16, anchor='n')
        error.after(4000, lambda: error.place_forget())