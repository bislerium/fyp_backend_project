import enum
import pandas as pd
import random
from itertools import chain

class EGender(enum.Enum):
    MALE = 0
    FEMALE = 1
    ANY = 2

class DataProvider:

    def __init__(self) -> None:
        self.read()
        self.arrange()
        self.extract()

    def read(self):
        self._first_names_df = pd.read_csv('firstnames_en.csv', usecols=['name', 'gender'])
        self._last_names_df = pd.read_csv('lastnames_en.csv', usecols=['Surnames'])

    def arrange(self):
        self._first_names_df.name = self._first_names_df.name.str.title()
        self._last_names_df.Surnames = self._last_names_df.Surnames.str.title()
    
    def extract(self) -> None:
        self.first_names = self._first_names_df.groupby('gender')['name'].apply(list).to_dict()
        self.last_names = self._last_names_df['Surnames'].tolist()

    def first_names(self, num: int = None, gender: EGender = EGender.ANY, is_shuffled: bool = True) -> dict[str, list[str]]:
        data = list(chain.from_iterable(self.first_names.values())) if gender == EGender.ANY else self.first_names[gender.name.title()]
        return random.shuffle(data)[0:num] if is_shuffled else data[0:num]        

    def last_names(self, num: int = None, is_shuffled: bool = True) -> list[str]:
        return random.shuffle(self.last_names)[0:num] if is_shuffled else self.last_names[0:num]

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

