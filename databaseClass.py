import sqlite3
import os

class Database:
    START_BALANCE = 100
    DB_NAME = 'casino_database.db'

    def __init__(self):
        check_file = os.path.isfile('./' + self.DB_NAME)
        self.conn = sqlite3.connect('casino_database.db')
        if not check_file:
            self.create_database()

    def create_database(self):
        self.conn.execute('''CREATE TABLE Clients
                     (ClientID INT PRIMARY KEY     NOT NULL,
                     ClientName     varchar(50) UNIQUE   NOT NULL,
                     Balance          INT     NOT NULL);''')

        self.conn.execute('''CREATE TABLE Game
        (
        GameID INT PRIMARY KEY     NOT NULL,
        GameName varchar(50)       NOT NULL
        )
        ''')

        self.conn.execute('''CREATE TABLE GamesHistory
                     (GamesHistoryID INT PRIMARY KEY   NOT NULL,
                     GameID INT                 NOT NULL,
                     ClientID INT               NOT NULL,
                     DatePlayed date            NOT NULL,
                     Win bit                    NOT NULL,
                     Earnings INT               NOT NULL,
                     Loss INT                   NOT NULL,
                     FOREIGN KEY (GameID) REFERENCES Game(GameID),
                     FOREIGN KEY (ClientID) REFERENCES Clients(ClientID)
                     );''')

        self.insert_mock_data()
        self.insert_games()

    def insert_games(self):
        curr_game_id = 0
        for game_name in ["roulette", "baccarat", "bingo", "dice", "blackjack", "poker"]:
            self.conn.execute("INSERT INTO Game (GameID, GameName) \
                  VALUES (?, ?)", (curr_game_id, game_name))
            self.conn.commit()

            curr_game_id += 1

    def insert_mock_data(self):
        for datapack in [["sus", 1000],["guest", 2000],["jack05", 100]]:
            self.create_client(datapack[0], datapack[1])

    def get_balance_by_name(self, client_name):
        cursor = self.conn.execute("SELECT Balance FROM Clients where ClientName = ?", (client_name, ))
        balance = 0
        try:
            for client in cursor:
                balance = client[0]
        except:
            balance = None
        return balance

    def create_client(self, client_name, balance=START_BALANCE):
        cursor = self.conn.execute("SELECT MAX(ClientID) FROM Clients")
        try:
            for row in cursor:
                client_id = int(row[0]) + 1
        except TypeError:
            client_id = 0

        self.conn.execute("INSERT INTO Clients (ClientID, ClientName, Balance) \
                  VALUES (?, ?, ?)", (client_id, client_name, balance))
        self.conn.commit()

        return balance

    def insert_game_history(self, client_name, game_name, win, earnings, loss):
        try:
            cursor = self.conn.execute("SELECT ClientID FROM Clients WHERE ClientName = ?", (client_name,))
            for row in cursor:
                client_id = row[0]

            cursor = self.conn.execute("SELECT GameID FROM Game WHERE GameName = ?", (game_name,))
            for row in cursor:
                game_id = row[0]

            cursor = self.conn.execute("SELECT MAX(GamesHistoryID) FROM GamesHistory")
            try:
                for row in cursor:
                    games_history_id = int(row[0]) + 1
            except TypeError:
                games_history_id = 0

            self.conn.execute("INSERT INTO GamesHistory (GamesHistoryID, GameID, ClientID, DatePlayed, Win, Earnings, Loss) \
                  VALUES (?, ?, ?, date(), ?, ?, ?)", (games_history_id, game_id, client_id, win, earnings, loss))
            self.conn.commit()
        except Exception as e:
            print(e)

    def change_balance(self, client_name, amount):  # amount should be positive if add, negative if subtract
        try:
            cursor = self.conn.execute("SELECT ClientID FROM Clients WHERE ClientName = ?", (client_name,))
            for row in cursor:
                client_id = row[0]
            cursor = self.conn.execute("SELECT Balance FROM Clients WHERE ClientID = ?", ( client_id, ))
            for row in cursor:
                balance = row[0]
            balance += amount
            self.conn.execute("UPDATE Clients set Balance = ? where ClientID = ?", (balance, client_id))
            self.conn.commit()
            return balance
        except Exception as e:
            print(e)

    def get_player_stats(self, player_name):
        query = '''
        SELECT g.GameName,COUNT(gh.GamesHistoryID) AS TotalGames, SUM(gh.Win) AS TotalWins, SUM(gh.Earnings) AS TotalEarnings, SUM(gh.Loss) AS TotalLosses
        FROM Clients AS c
        JOIN GamesHistory AS gh ON c.ClientID = gh.ClientID
        JOIN Game AS g ON g.GameID = gh.GameID
        WHERE c.ClientName = ?
        GROUP BY g.GameName
        '''

        try:
            cursor = self.conn.execute(query, (player_name,))
            stats = cursor.fetchall()
            return stats
        except Exception as e:
            print(e)
            return None


if  __name__ == "__main__":
    a = Database()
    print(a.get_player_stats("sus"))
    # a.create_client("rob")
    # a.create_client("bob")
    # game_history = [
    #     ("bob", "poker", 0, 0, 100),
    #     ("rob", "blackjack", 1, 1000, 0),
    #     ("bob", "bingo", 1, 200, 0),
    #     ("rob", "roulette", 0, 0, 300),
    #     ("bob", "dice", 1, 300, 0),
    #     ("rob", "roulette", 0, 0, 200),
    #     ("bob", "bingo", 1, 100, 0),
    #     ("rob", "blackjack", 1, 500, 0),
    #     ("bob", "dice", 0, 0, 75),
    #     ("rob", "baccarat", 1, 1000, 0)
    # ]
    #
    # for record in game_history:
    #     a.insert_game_history(*record)



