import socket
import select
import queue
from clientClass import Client
from databaseClass import Database
from errorDefinitions import *
import gameRoom
from _thread import *
from helpers import SendDataType
from helpers import send_data
import time


def start_room(game_room):
    start_new_thread(lambda x: x.start(), (game_room,))


class Server:
    def __init__(self, MAX_USERS_CONNECTED, SERVER_IP, SERVER_PORT):
        self.MAX_USERS_CONNECTED = MAX_USERS_CONNECTED
        self.SERVER_IP = SERVER_IP
        self.SERVER_PORT = SERVER_PORT
        self.num_of_connected_clients = 0
        self.database = Database()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_socket()

        self.connected_clients = {}

        self.database_calls = []

        self.inputs = [self.s]
        self.outputs = []
        self.message_queues = {self.s: queue.Queue()}
        self.game_rooms: [gameRoom.GameRoom] = []

    def init_socket(self):
        self.s.bind((self.SERVER_IP, self.SERVER_PORT))
        self.s.setblocking(0)
        self.s.listen(self.MAX_USERS_CONNECTED)

    def generate_client(self, response: str, conn: socket.socket(), addr):
        balance = self.database.get_balance_by_name(response)
        if not balance:
            balance = self.database.create_client(response)

        return Client(conn, addr, response, balance)

    def start(self):
        while self.inputs:
            readable, writable, exceptions = select.select(self.inputs, self.outputs, self.inputs, 1)
            for s in readable:
                if s == self.s:
                    try:
                        conn, addr = self.s.accept()
                        default_timeout = conn.gettimeout()
                        conn.settimeout(5)
                        identification_response = conn.recv(1024)
                        if not identification_response: raise InvalidResponseException
                        decoded_response = identification_response.decode()

                        new_client = self.generate_client(decoded_response, conn, addr)
                        self.connected_clients[conn] = new_client
                        self.message_queues[conn] = queue.Queue()
                        self.inputs.append(conn)

                        conn.settimeout(default_timeout)
                        conn.setblocking(0)
                        self.num_of_connected_clients += 1
                        print("Player connected")
                    except socket.timeout:
                        conn.close()
                        continue
                    except InvalidResponseException:
                        conn.close()
                        continue
                    except Exception as e:
                        print(e)
                        conn.close()
                        continue
                else:
                    try:
                        response = s.recv(1024)
                    except ConnectionResetError:
                        exceptions.append(s)
                        continue
                    if response:
                        decoded_response = response.decode()
                        try:
                            self.handle_client_response(decoded_response, s)
                            # print(f"New response: {decoded_response} from client {self.connected_clients[s].name}")
                        except InvalidResponseException:
                            print("Invalid response")
                        except InvalidUserException:
                            print("Invalid user id")

            for s in writable:
                try:
                    next_msg = self.message_queues[s].get_nowait()
                except queue.Empty:
                    self.outputs.remove(s)
                else:
                    send_data(next_msg[0], s, next_msg[1])

            for s in exceptions:
                print("exception in gameServer")
                self.disconnect_client(s)
                self.num_of_connected_clients -= 1

            self.update_database()

            if not (readable or writable or exceptions):
                continue

    def transfer_client(self, game_room, s):
        self.inputs.remove(s)
        if s in self.outputs:
            self.outputs.remove(s)
        game_room.add_player(self.connected_clients[s], s)
        print("transfered player")

    def untransfer_client(self, s):
        self.inputs.append(s)
        print(f"untransfered player")
        self.message_queues[s].put((b"Disconnected from game, welcome to server lobbby!", SendDataType.STRING))
        self.outputs.append(s)

    def change_balance(self, client_name, balance):
        self.database_calls.append((self.database.change_balance, [client_name, balance]))

    def add_game_history(self, client_name, game_name, win, earnings, loss):
        self.database_calls.append((self.database.insert_game_history, [client_name, game_name, win, earnings, loss]))

    def update_database(self):
        tmp = self.database_calls.copy()
        self.database_calls = []

        for call in tmp:
            test_var = call[0](*call[1])
            print(test_var)


    def disconnect_client(self, s):
        if s in self.inputs:
            self.inputs.remove(s)
        if s in self.outputs:
            self.outputs.remove(s)
        if self.connected_clients[s]:
            del self.connected_clients[s]
        if self.message_queues[s]:
            del self.message_queues[s]
        s.close()
        print("player disconnected")

    def handle_client_response(self, response, s):

        data = response.split(" ")
        try:
            if data[0] == "play":
                found_rooms = gameRoom.search_game_room(self.game_rooms, data[1])
                print("znalezione pokoje:", found_rooms)
                if not found_rooms:
                    new_room = gameRoom.create_game_room(data[1], self)
                    self.game_rooms.append(new_room)
                    found_rooms = [new_room]
                    start_room(new_room)
                self.transfer_client(found_rooms[0], s)
            elif data[0] == "exit":
                self.disconnect_client(s)
            elif data[0] == "stat":
                data = self.database.get_player_stats(self.connected_clients[s].name)
                if s not in self.outputs:
                    self.outputs.append(s)
                    self.message_queues[s].put((bytes("Stat:" + str(data), "utf-8"), SendDataType.STRING))
            else:
                raise InvalidResponseException

        except IndexError:
            print("IndexError")
            raise InvalidResponseException
        except InvalidResponseException:
            print("InvalidResponseException")
            raise InvalidResponseException
        except InvalidGameName:
            print("InvalidGameName")
            raise InvalidResponseException

        return 0


if __name__ == "__main__":
    server = Server(4, "127.0.0.1", 65432)
    server.start()
