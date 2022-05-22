"""
Implementation of Fish

See https://esolangs.org/wiki/Fish#Instructions
"""

from collections import defaultdict
from sys import stderr
from itertools import chain
import random

from esoteric.gui import Colors
from esoteric.interpreter import Actions, coord, Interpreter

right = coord(1, 0)
down = coord(0, 1)
left = coord(-1, 0)
up = coord(0, -1)

DELTA_CHANGERS = {
    ">": right,
    "v": down,
    "<": left,
    "^": up,
}

"""
/ mirror:

  ^
> /
(1, 0) -> (0, -1)

/ <
v
(-1, 0) -> (0, 1)

  v
< /
(0, 1) -> (-1, 0)

/ >
^
(0, -1) -> (1, 0)

\\ mirror:

> \\
  v
(1, 0) -> (0, 1)

and so on.
"""

MIRRORS = {
    "|": lambda d: coord(-d.x, d.y) if d.x != 0 else d,
    "_": lambda d: coord(d.x, -d.y) if d.y != 0 else d,
    "/": lambda d: coord(-d.y, -d.x),
    "\\": lambda d: coord(d.y, d.x),
}

BINARY_OPS = {
    # Arithmetic
    "+": lambda a, b: a + b,
    "-": lambda a, b: b - a,
    "*": lambda a, b: b * a,
    "%": lambda a, b: b % a,
    # Comparisons
    "=": lambda a, b: int(b == a),
    ")": lambda a, b: int(b > a),
    "(": lambda a, b: int(b < a),
}

STACK_MODIFIERS = {
    ":": lambda stack: stack.append(stack[-1]),
    "@": lambda stack: stack.extend([stack.pop(), stack.pop(), stack.pop()]),
    "$": lambda stack: stack.extend([stack.pop(), stack.pop()]),
    "~": lambda stack: stack.pop(),
    "l": lambda stack: stack.append(len(stack)),
}

NUMBERS = list(str(i) for i in range(10)) + list("abcdef")

DIRECTIONS = list(DELTA_CHANGERS.values())

COLORS = {
    **{c: Colors.RED for c in "@"},
    **{
        c: Colors.GREEN for c in "'\"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefhijklmnoqrstuvwxyz"
    },
    **{c: Colors.YELLOW for c in chain(DELTA_CHANGERS.keys(), MIRRORS.keys(), "#x!?.")},
    **{c: Colors.BLUE for c in chain(BINARY_OPS.keys(), ",")},
    **{c: Colors.MAGENTA for c in chain(STACK_MODIFIERS.keys(), "r{}[]gp")},
    **{c: Colors.CYAN for c in "noi"},
}


class Fish(Interpreter):
    delta = coord(1, 0)
    stack = []
    stackstack = []
    register = None
    stringmode = False

    def __init__(self, board: list[list[str]], value=None):
        super().__init__(board)
        # Initialize infinite board w/numeric values
        self.grid = defaultdict(int)
        for y, row in enumerate(board):
            for x, cell in enumerate(row):
                # Only assign cells with something non-default in them
                if cell != " ":
                    self.grid[coord(x, y)] = ord(cell)
        self.minpos = coord(0, 0)
        if value is not None:
            self.stack = [value]

    # Need to override this property to account for the infinite grid
    @property
    def cell(self):
        return chr(self.grid[self.pos])

    def color_of(self, position: coord) -> int:
        try:
            # TODO properly color strings (which is kinda impossible)
            return COLORS[chr(self.grid[position])]
        except KeyError:
            return 8

    def step(self):
        try:
            res = self._step()
            if res[1] == Actions.HALT:
                self.halted = True
        except Exception as err:
            print(self.pos, self.delta, self.cell, self.stack, file=stderr)
            print("something smells fishy...", file=stderr)
            raise err
        return res

    # TODO "something smells fishy..." on error
    # TODO unrelated but maybe some "do you want to quit" on program halt
    def _step(self):
        action = Actions.NONE
        value = None

        trampoline = False
        teleported = False

        # Values
        if self.stringmode:
            if self.cell in "'\"":
                self.stringmode = False
            else:
                # Stringmode overrides everything
                self.stack.append(ord(self.cell))
        elif self.cell in "'\"":
            self.stringmode = True
        elif self.cell in NUMBERS:
            # Note that Fish supports hexadecimal numbers
            self.stack.append(int(self.cell, 16))

        # Execution
        elif self.cell == ";":
            return (self.pos, Actions.HALT, None)

        # Input/output
        elif self.cell == "n":
            action = Actions.OUTPUT
            value = str(self.stack.pop())
        elif self.cell == "o":
            action = Actions.OUTPUT
            value = chr(self.stack.pop())
        elif self.cell == "i":
            action = Actions.INT_INPUT  # TODO push -1 if no input available

        # Push cell value to stack
        elif self.cell == "g":
            y, x = self.stack.pop(), self.stack.pop()
            self.stack.append(self.grid[coord(x, y)])
        # Update cell value, complicated since this is on an infinite grid
        elif self.cell == "p":
            y, x, v = self.stack.pop(), self.stack.pop(), self.stack.pop()
            self.grid[coord(x, y)] = v
            # Update displayed board as well, if this change is within limits
            # and the value does not correspond to some control character
            if 0 <= x < self.limit.x and 0 <= y < self.limit.y and chr(v).isprintable():
                # Extend board if necessary
                # (remember that coordinates are zero-indexed)
                if x >= self.maxpos.x or y >= self.maxpos.y:
                    ext = (
                        coord(max(x + 1, self.maxpos.x), max(y + 1, self.maxpos.y))
                        - self.maxpos
                    )
                    for line in self.board:
                        line.extend([" "] * ext.x)
                    for _ in range(ext.y):
                        self.board.extend([[" "] * (self.maxpos.x + ext.x)])
                # Update board cell
                self.board[y][x] = chr(v)
            # Update extents of grid
            self.minpos = coord(min(self.minpos.x, x), min(self.minpos.y, y))
            self.maxpos = coord(max(self.maxpos.x, x), max(self.maxpos.y, y))

        # Movement
        elif self.cell in DELTA_CHANGERS:
            self.delta = DELTA_CHANGERS[self.cell]
        elif self.cell in MIRRORS:
            self.delta = MIRRORS[self.cell](self.delta)
        elif self.cell in "x#":
            self.delta = random.choice(DIRECTIONS)
        elif self.cell == ".":  # Teleport
            y, x = self.stack.pop(), self.stack.pop()
            self.pos = coord(x, y)
            teleported = True
        elif self.cell == "!":  # Skip
            trampoline = True
        elif self.cell == "?":  # Skip if stack head is 0
            trampoline = self.stack.pop() == 0 if len(self.stack) else False

        # Operators
        elif self.cell in BINARY_OPS:
            self.stack.append(BINARY_OPS[self.cell](self.stack.pop(), self.stack.pop()))
        elif self.cell == ",":  # Division
            a, b = self.stack.pop(), self.stack.pop()
            if a == 0:
                # If division by 0, this is an error
                action = Actions.ERROR
                value = "Division by zero"
            else:
                self.stack.append(b / a)

        # Stack & storage
        elif self.cell in STACK_MODIFIERS:
            STACK_MODIFIERS[self.cell](self.stack)
        elif self.cell == "r":
            self.stack = list(reversed(self.stack))
        elif self.cell == "{":
            self.stack = self.stack[1:] + [self.stack[0]]  # Shift left
        elif self.cell == "}":
            self.stack = [self.stack[-1]] + self.stack[:-1]  # Shift right
        elif self.cell == "[":
            # Push new stack
            n = self.stack.pop()
            self.stackstack.append((self.stack[:-n], self.register))
            self.stack = self.stack[-n:]
            self.register = None
        elif self.cell == "]":
            if len(self.stackstack) > 0:
                # Pop stack and move values to old stack
                newstack, newreg = self.stackstack.pop()
                self.stack = newstack + self.stack
                self.register = newreg
            else:
                # Empty stack & reg if no other stack
                self.stack = []
                self.register = None
        elif self.cell == "&":
            if self.register is None:
                self.register = self.stack.pop()
            else:
                self.stack.append(self.register)
                self.register = None

        # Update position
        if trampoline and not self.stringmode:
            self.pos = self.pos + self.delta + self.delta
        elif not teleported:
            self.pos = self.pos + self.delta

        # Wrap around source code (account for possible negative coordinates)
        self.pos = (self.pos + self.minpos) % (self.maxpos - self.minpos) - self.minpos

        return (self.pos, action, value)

    def recv(self, value):
        self.stack.append(value)

    def internal_state(self):
        return [str(i) for i in reversed(self.stack)]
