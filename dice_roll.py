"""Dice roller"""
from abc import ABCMeta
from typing import List , Optional , Union, Tuple, ValuesView
import random
import re


class GenericDice():
    """Base class for every dice roll."""

    def __init__(self, count, dice) -> None:
        self.count = count
        self.dice = dice
        self._n_rerolls = 0
        self._results = self._roll()
        self._numeric = sum(self._results)

    # Properties
    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        if is_natural_number(value):
            self._count = value
        else:
            raise ValueError(
                "Argument <count> must be positive integer value.")
            
    @property
    def dice(self):
        return self._dice

    @dice.setter
    def dice(self, value):
        if is_natural_number(value):
            self._dice = value
        else:
            raise ValueError(
                "Argument <dice> must be positive integer value.")

    @property
    def results(self):
        return self._results

    @property
    def n_rerolls(self):
        return self._n_rerolls

    @property
    def numeric(self):
        return self._numeric

    # Methods
    def _roll(self)-> Tuple[int]:
        """Roll dice with <dice> edges <count> times."""
        rolls = [random.randint(1 , self.dice) for _ in range(self.count)]
        return tuple(rolls)

    def reroll(self)-> None:
        """Reroll current dices"""
        self._n_rerolls += 1
        self._results = self._roll()
        self._numeric = sum(self._results)

    @staticmethod
    def roll_list(roll_list: List[tuple])-> List["GenericDice"]:
        """Бросает дайсы из списка возвращая список брошенных кубов.
        :roll_list: List[Tiple[int]]
            List containing tuples of view (count_dices, dice)

        :return:
            List of BaseDice objects
        """

        results = []
        for count, dice in roll_list:
            dice = GenericDice(count, dice)
            results.append(dice)
        return results
    
    def __add__(self , value):
        '''+'''
        if isinstance(value, __class__):
            value = value.numeric
        return self.numeric + value

    def __radd__(self , value):
        '''+'''
        if isinstance(value, __class__):
            value = value.numeric
        return self.numeric + value

    def __sub__(self, value):
        '''-'''
        if isinstance(value, __class__):
            value = value.numeric
        return self.numeric - value

    def __rsub__(self, value):
        '''-'''
        if isinstance(value, __class__):
            value = value.numeric
        return value - self.numeric

    def __mul__(self, value):
        '''*'''
        if isinstance(value, __class__):
            value = value.numeric
        return self.numeric * value

    def __rmul__(self, value):
        '''*'''
        if isinstance(value, __class__):
            value = value.numeric
        return self.numeric * value

    def __truediv__(self, value):
        '''<self>/<value>'''
        if isinstance(value, __class__):
            value = value.numeric
        return self.numeric / value

    def __rtruediv__(self, value):
        '''<value>/<self>'''
        if isinstance(value, __class__):
            value = value.numeric
        return value / self.numeric


class DND5Dice(GenericDice):
    @property
    def dice(self):
        return self._dice

    @dice.setter
    def dice(self, value):
        cond_base = is_natural_number(value)
        cond_dnd = value in [2, 4, 6, 8, 10, 12, 20, 30, 100]
        if cond_dnd and cond_base:
            self._dice = value
        else:
            message = """Argument <dice> must be positive
            integer value of dnd5 types.
            [d2, d4, d6, d8, d10, d12, d20, d100]""".replace("\n", " ")
            raise ValueError(message)

    @staticmethod
    def roll_list(roll_list: List[tuple])-> List["DND5Dice"]:
        # TODO Переписать на англйском
        """Бросает дайсы из списка возвращая список брошенных кубов.
        :roll_list: List[Tiple[int]]
            List containing tuples of view (count_dices, dice)

        :return:
            List of BaseDice objects
        """
        results = []
        for count, dice in roll_list:
            dice = DND5Dice(count, dice)
            results.append(dice)
        return results

    @staticmethod
    def roll_stats(n_stats: int=6)-> Tuple[Tuple[list, int]]:
        # TODO Переписать на англимйском
        """Генерирует значения для статок в ДНД5.
        Алгоритм описанный в книги:
            1. Бросается d6 4 раза (=<Полный бросок>)
            2. Откидывается наименьшее значение
            3. Сумма значений оставшихся кубов
            и есть <Итоговое значение> для статки.

        :n_stats:
            количество статок для которых будет сгенерированно значение.
        
        :return:
            Возвращает кортеж содержащий DND5Dice 
            с измённёным numeric в соответвие с алгоритмом.
        """
        result_stats = []
        for _ in range(n_stats):
            roll = DND5Dice(4, 6)
            completed_result = list(roll.results)
            completed_result.remove(min(completed_result))
            roll._numeric = sum(completed_result)
            result_stats.append(roll)

        return tuple(result_stats)


class FudgeDice(GenericDice):
    def __init__(self, count) -> None:
        self.count = count
        self._n_rerolls = 0
        self._results = self._roll_fudge()
        self._numeric = sum(self._results)

    def _roll_fudge(self) -> Tuple[int]:
        results = GenericDice(self.count, 3).results
        return tuple([res-2 for res in results])

    @staticmethod
    def roll_list(roll_list: List[int])-> List["FudgeDice"]:
        # TODO Переписать на англйском
        """Бросает дайсы из списка возвращая список брошенных кубов.
        :roll_list: List[Tiple[int]]
            List containing tuples of view (count_dices, dice)

        :return:
            List of BaseDice objects
        """
        results = []
        for count in roll_list:
            dice = FudgeDice(count)
            results.append(dice)
        return results


class CustomDice(GenericDice):
    def __init__(self, count, dice, dmap) -> None:
        super().__init__(count, dice)
        self.dmap = dmap
        self._results = [self.dmap[res] for res in self.results]
        self._numeric = None

    @property
    def numeric(self):
        return None

    @property
    def dmap(self):
        return self._dmap

    @dmap.setter
    def dmap(self, value):
        if not isinstance(value, dict):
            raise ValueError("<map> must be dict object.")
        elif not all([key in range(1, self.dice+1) for key in value.keys()]):
            raise ValueError("<map> incorrect form.")
        self._dmap = value

    def _roll_custom(self) -> Tuple[int]:
        result = super()._roll()
        return tuple([self.dmap[res] for res in result])

    def reroll(self) -> None:
        super().reroll()
        self._results = [self.dmap[res] for res in self.results]

    @staticmethod
    def roll_list(roll_list: List[tuple])-> List["CustomDice"]:
        # TODO Переписать на англйском
        """Бросает дайсы из списка возвращая список брошенных кубов.
        :roll_list: List[Tiple[int]]
            List containing tuples of view (count_dices, dice)

        :return:
            List of BaseDice objects
        """
        results = []
        for count, dice, dmap in roll_list:
            dice = CustomDice(count, dice, dmap)
            results.append(dice)
        return results

    def __add__(self , value):
        '''+'''
        raise SyntaxError("Operation + is not avaliable for this object")

    def __radd__(self , value):
        '''+'''
        raise SyntaxError("Operation + is not avaliable for this object")

    def __sub__(self, value):
        '''-'''
        raise SyntaxError("Operation - is not avaliable for this object")

    def __rsub__(self, value):
        '''-'''
        raise SyntaxError("Operation - is not avaliable for this object")

    def __mul__(self, value):
        '''*'''
        raise SyntaxError("Operation * is not avaliable for this object")
    
    def __rmul__(self, value):
        '''*'''
        raise SyntaxError("Operation * is not avaliable for this object")

    def __truediv__(self, value):
        '''/'''
        raise SyntaxError("Operation / is not avaliable for this object")

    def __rtruediv__(self, value):
        '''/'''
        raise SyntaxError("Operation / is not avaliable for this object")
        

def is_natural_number(value):
    cond1 = value > 0
    cond2 = value.__class__ == int
    return cond1 and cond2

if __name__ == "__main__":
    data = [
        (1, 2, {1:"один", 2:"два"}),
        (2, 3, {1:"один", 2:"два", 3:"три"})
    ]
    for r in CustomDice.roll_list(data):
        print(r.results)