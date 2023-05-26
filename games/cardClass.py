import random
import time
from abc import ABC, abstractmethod

FIGURES = ["J", "Q", "K"]

class Deck:
    def __init__(self, CardClass, num_of_decks):
        self.cards = []
        self.num_of_decks = num_of_decks
        self.CardClass = CardClass

        self.fillDeck()
        random.seed(time.time())

    def fillDeck(self):
        self.cards = []
        for deck in range(self.num_of_decks):
            for suit in ["♠", "♥", "♦", "♣"]:
                for value in range(1, 14):
                    self.cards.append(self.CardClass(suit, value))
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) <= 7:
            self.fillDeck()

        return self.cards.pop()


class Card(ABC):
    def __init__(self, suit, val):
        self._suit = suit
        self._value = val

    def __str__(self):
        return f"{self.valueToFigure(self._value)}{self._suit}"

    def __repr__(self):
        return f"{self.valueToFigure(self._value)}{self._suit}"

    @property
    @abstractmethod
    def value(self):
        return self._value if self._value <= 10 else 0

    @abstractmethod
    def valueToFigure(self,value):
        pass


class CardBaccarat(Card, ABC):
    def valueToFigure(self, value):
        if value == 1:
            return "A"
        elif value <= 10:
            return str(value)
        else:
            return FIGURES[value - 11]

    @property
    def value(self):
        return self._value if self._value <= 10 else 0


class CardBlackjack(Card, ABC):

    @property
    def value(self):
        return self._value if self._value <= 10 else 10

    def valueToFigure(self, value):
        if value == 1:
            return "A"
        elif value <= 10:
            return str(value)
        else:
            return FIGURES[value - 11]



