import socket
import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk


class DiceGamePage(tk.Frame):

    def __init__(self, parent, controller, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller
        self.s = self.controller.s
        self.isRollTime = 0
        self.isBetTime = 0
        self.isMeShooter = 0
        # Gui variables
        self.bet_entry = tk.StringVar()
        self.dice_imgs = self.init_dice_imgs()
        self.ft = ('Candara', 13)
        self.gui_elements = {}
        self.roll_frame = self.create_roll_frame()
        self.back_btn = self.create_back_button()
        self.bet_frame = self.create_bet_frame()
        self.messages_output = self.create_messages_output()
        self.back_btn.tkraise()

        self.roll_btn = self.gui_elements["roll_btn"]
        self.dice_1 = self.gui_elements["dice_1"]
        self.dice_2 = self.gui_elements["dice_2"]

    def create_back_button(self):
        self.gui_elements["back_button"] = tk.Button(
            self,
            text="Back",
            command=self.back,
            bg="#375A7F",
            font=self.ft,
            fg="#FFFFFF",
            justify="center",
            width=10,
        )
        self.gui_elements["back_button"].place(x=10, y=10, width=70)
        return self.gui_elements["back_button"]

    def create_roll_frame(self):
        self.gui_elements["roll_frame"] = roll_frame = tk.Frame(self)
        self.gui_elements["roll_frame"].place(relx=0, rely=0.5, relwidth=0.5, relheight=0.8, anchor='w')

        self.gui_elements["fake_label_top_roll"] = tk.Label(roll_frame)
        self.gui_elements["fake_label_top_roll"].pack(expand=True)

        self.create_dice_frame()
        self.gui_elements["roll_btn"] = tk.Button(
            roll_frame,
            text="Roll",
            command=self.roll,
            bg="#375A7F",
            font=self.ft,
            fg="#FFFFFF",
            justify='center',
            width=10
        )
        self.gui_elements["roll_btn"].pack(pady=10)

        self.gui_elements["fake_label_bottom_roll"] = tk.Label(roll_frame)
        self.gui_elements["fake_label_bottom_roll"].pack(expand=True)

        return roll_frame

    def create_dice_frame(self):
        self.gui_elements["dice_frame"] = dice_frame = tk.Frame(self.gui_elements["roll_frame"])
        self.gui_elements["dice_frame"].pack(pady=20)

        self.gui_elements["dice_1"] = tk.Label(dice_frame, image=self.dice_imgs[0], fg="#FFFFFF", justify='center')
        self.gui_elements["dice_1"].pack(side='left', padx=10)

        self.gui_elements["dice_2"] = tk.Label(dice_frame, image=self.dice_imgs[0], fg="#FFFFFF", justify='center')
        self.gui_elements["dice_2"].pack(side='left', padx=10)

        return dice_frame

    def create_bet_frame(self):
        self.gui_elements["bet_frame"] = bet_frame = tk.Frame(self)
        self.gui_elements["bet_frame"].place(relx=0.5, y=7, relwidth=0.5, relheight=1, anchor='nw')

        self.gui_elements["fake_label_top"] = tk.Label(bet_frame)
        self.gui_elements["fake_label_top"].pack(expand=True)

        self.gui_elements["bet_label"] = tk.Label(bet_frame, font=self.ft, fg="#FFFFFF", justify='center',
                                                  text="Enter bet amount")
        self.gui_elements["bet_label"].pack(pady=20)

        self.gui_elements["bet_entry"] = ttk.Entry(bet_frame, font=self.ft, textvariable=self.bet_entry)
        self.gui_elements["bet_entry"].pack(pady=20)

        self.create_button_frame()

        self.gui_elements["fake_label_bottom"] = tk.Label(bet_frame)
        self.gui_elements["fake_label_bottom"].pack(expand=True)

        return bet_frame

    def create_button_frame(self):
        self.gui_elements["btn_frame"] = btn_frame = tk.Frame(self.gui_elements["bet_frame"])
        self.gui_elements["btn_frame"].pack(pady=30)

        self.gui_elements["pass_btn"] = tk.Button(btn_frame, background="#375A7F", font=self.ft, fg="#FFFFFF",
                                                  justify='center',
                                                  text="pass",
                                                  command=self.pass_handler, width=10)
        self.gui_elements["pass_btn"].pack(side='left', expand=True, padx=20)

        self.gui_elements["dpass_btn"] = tk.Button(btn_frame, background="#375A7F", font=self.ft, fg="#FFFFFF",
                                                   justify='center',
                                                   text="dpass", command=self.dpass_handler, width=10)
        self.gui_elements["dpass_btn"].pack(side='left', expand=True, padx=20)

        return btn_frame

    def create_messages_output(self):
        self.gui_elements["messages_output"] = messages_output = tk.Listbox(self, borderwidth='1px', font=self.ft,
                                                                            fg="#FFFFFF", justify='center',
                                                                            height=5, bg="#000000")
        self.gui_elements["messages_output"].place(relx=0.5, y=10, relwidth=0.7, anchor='n')
        return messages_output

    def show_message(self, message):
        self.messages_output.insert(tk.END, f"{message}\n")
        self.messages_output.yview(tk.END)

    def init_dice_imgs(self):
        return [ImageTk.PhotoImage(Image.open(f"assets/dice-{i}.png").resize((110, 110))) for i in range(1, 7)]

    def dpass_handler(self):
        if self.bet_entry.get() is not None and self.bet_entry.get().isnumeric() and self.isBetTime:
            self.s.send(bytes(f"dpass {self.bet_entry.get()}", 'utf-8'))
        self.bet_entry.set("")

    def pass_handler(self):
        if self.bet_entry.get() is not None and self.bet_entry.get().isnumeric() and self.isBetTime:
            self.s.send(bytes(f"pass {self.bet_entry.get()}", 'utf-8'))
        self.bet_entry.set("")

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
            print("shooter")
        elif message_split[0] == "Disconnected":
            self.controller.show_frame('ChooseGamePage')
        elif message_body == "Bets ended, time for shooter to roll!":
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
            if self.isMeShooter:
                self.roll_btn['bg'] = 'green'
        if "Rolled" not in message_body:
            self.show_message(message_body)
        if "wins" in message_body:
            self.isMeShooter = 0

    def back(self):
        self.s.send(bytes("back", 'utf-8'))
        self.controller.show_frame('ChooseGamePage')
        self.clear()

    def clear(self):
        self.messages_output.delete(0, tk.END)
        self.bet_entry.set("")
        self.roll_btn['bg'] = "#375A7F"
