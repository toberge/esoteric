from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum, auto
from sys import stdin
from typing import Union


@dataclass(frozen=True, order=True)
class coord:
    x: int
    y: int

    def __add__(self, other):
        return coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return coord(self.x - other.x, self.y - other.y)

    def __mod__(self, other):
        return coord(self.x % other.x, self.y % other.y)


class Actions(Enum):
    NONE = auto()
    STRING_INPUT = auto()
    INT_INPUT = auto()
    OUTPUT = auto()
    HALT = auto()
    ERROR = auto()


StepResult = Union[tuple[coord, int, int], tuple[coord, int, chr]]


class Interpreter(ABC):
    pos = coord(0, 0)
    halted = False

    def __init__(self, board: list[list[str]]):
        # Normalize shape
        width = max(len(line) for line in board)
        for line in board:
            line.extend([" "] * (width - len(line)))
        self.board = board
        self.maxpos = coord(width, len(board))

    @classmethod
    def from_string(cls, board: str):
        return cls([list(line) for line in board.splitlines()])

    @property
    def cell(self):
        return self.board[self.pos.y][self.pos.x]

    @abstractmethod
    def step(self) -> StepResult:
        pass

    @abstractmethod
    def recv(self, value: Union[int, str]):
        pass

    @abstractmethod
    def internal_state(self) -> list[str]:
        pass

    def __iter__(self):
        while not self.halted:
            yield self.step()

    def run(self):
        while not self.halted:
            _, action, value = self.step()
            if action == Actions.STRING_INPUT:
                self.recv(stdin.read(1))
            elif action == Actions.INT_INPUT:
                self.recv(int(stdin.read(1)))
            elif action == Actions.OUTPUT:
                print(str(value), end="")
            elif action == Actions.HALT:
                self.halted = True
            elif action == Actions.ERROR:
                raise Exception(value)

    def eval(self):
        output = []
        while not self.halted:
            _, action, value = self.step()
            if action == Actions.STRING_INPUT:
                self.recv(stdin.read(1))
            elif action == Actions.INT_INPUT:
                self.recv(int(stdin.read(1)))
            elif action == Actions.OUTPUT:
                output.append(str(value))
            elif action == Actions.HALT:
                self.halted = True
            elif action == Actions.ERROR:
                raise Exception(value)
        return "".join(output)
