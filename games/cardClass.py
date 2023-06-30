import random
import time
from abc import ABC, abstractmethod

FIGURES = ["J", "Q", "K"]


class Deck:
    def __init__(self, card_class, num_of_decks):
        self.cards = []
        self.num_of_decks = num_of_decks
        self.card_class = card_class

        self.fill_deck()
        random.seed(time.time())

    def fill_deck(self):
        self.cards = []
        for deck in range(self.num_of_decks):
            for suit in ["♠", "♥", "♦", "♣"]:
                for value in range(1, 14):
                    self.cards.append(self.card_class(suit, value))
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) <= 7:
            self.fill_deck()

        return self.cards.pop()


def value_to_figure(value):
    if value == 1:
        return "A"
    elif value <= 10:
        return str(value)
    else:
        return FIGURES[value - 11]


class Card(ABC):
    def __init__(self, suit, val):
        self._suit = suit
        self._value = val

    def __str__(self):
        return f"{value_to_figure(self._value)}{self._suit}"

    def __repr__(self):
        return f"{value_to_figure(self._value)}{self._suit}"

    @property
    @abstractmethod
    def value(self):
        pass


class CardBaccarat(Card, ABC):
    @property
    def value(self):
        return self._value if self._value <= 10 else 0


class CardBlackjack(Card, ABC):
    @property
    def value(self):
        return self._value if self._value <= 10 else 10


class CardPoker(Card, ABC):
    @property
    def value(self):
        return self._value

    @property
    def suit(self):
        return self._suit
