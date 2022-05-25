import enum
import pandas as pd

class EGender(enum.Enum):
    MALE = 0
    FEMALE = 1
    ANY = 2

class DataProvider:

    def __init__(self) -> None:
        animes = pd.read_csv("anime.csv")
        ratings = pd.read_csv("rating.csv")

def first_name(num: int = None, gender: EGender = EGender.ANY) -> dict[str, set[str]]:
    pass

def last_name(num: int = None) -> set[str]:
    pass

def address(num: int = None) -> set[str]:
    pass

def geo(num: int = None) -> set[tuple[float, float]]:
    pass

def ngo_name(num: int = None) -> set[str]:
    pass

def bank_name(num: int = None) -> set[str]:
    pass

def bank_branch(num: int = None) -> set[str]:
    pass

