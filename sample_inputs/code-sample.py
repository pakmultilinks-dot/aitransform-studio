import math


def circle_area(radius):
    """Return the area of a circle."""
    return math.pi * radius * radius


class Shop:
    """A tiny shop that tracks items and their prices."""

    def __init__(self):
        self.items = []

    def add(self, name, price):
        self.items.append((name, price))

    def total(self):
        s = 0
        for _, price in self.items:
            s += price
        return s
