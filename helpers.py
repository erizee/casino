import pickle
import socket
from enum import Enum

STRING_BUFFER_SIZE = 1024
PICKLE_BUFFER_SIZE = 2048


class SendDataType(Enum):
    STRING = 0
    PICKLE = 1
    NONE = 2


def send_data(data, conn, type):
    if type == SendDataType.STRING:
        msg_len = len(data)
        header_2 = msg_len.to_bytes(4, byteorder='big')
        conn.send(b"type string " + header_2)
        conn.send(data)
    elif type == SendDataType.PICKLE:
        conn.send(b"type pickle ")
        conn.sendall(pickle.dump(data))


def receive_data(conn):
    #  TODO: fix for big networks
    try:
        conn.settimeout(2.0)
        data = conn.recv(16)
        conn.settimeout(None)
    except socket.timeout:
        return None

    msg_len = int.from_bytes(data[12:16], byteorder="big")
    decoded = data[:11].decode().split(" ")

    bytes_recd = 0
    chunks = []
    buff_size = 0
    data_type = SendDataType.NONE

    if decoded[1] == "string":
        buff_size = STRING_BUFFER_SIZE
        data_type = SendDataType.STRING
    else:
        buff_size = PICKLE_BUFFER_SIZE
        data_type = SendDataType.PICKLE

    while bytes_recd < msg_len:
        chunk = conn.recv(min(msg_len - bytes_recd,
                              buff_size))
        if not chunk:
            raise RuntimeError("ERROR")

        chunks.append(chunk)
        bytes_recd += len(chunk)

    mess = b"".join(chunks)

    return data_type, mess
