"""Dump for any different fun"""
from typing import Type , List
import random
import re

class Dice:
    """Roll any dice and stores data about it.
    Attributes:
    Args:
    Raises
    """
    count: int
    dice: int
    result: tuple
    result_sum: int
    #Optional
    consequences: Type
    allrolls: list
    typeroll: str

    def __init__(self , adv = None):
        self.consequences = Consequences(obj=self , adv=adv)
        

    def Roll(self, count_dice: str):
        """Roll any dice by template(ndn ,  n - natural number)"""
        # mult = 2 if throw with adv/disadv
        mult = 2 if self.consequences!=None else 1

        # unpack data 
        count_roll, dice = count_dice.split('d')
        count_roll = int(count_roll)
        dice = int(dice)

        allrolls = []
        for rolls in range(mult):
            rolls = []
            for roll in range(count_roll):
                roll = random.randint(1, dice)
                rolls.append(roll)
            allrolls.append(rolls.copy())

        # Make adv/disadv/base
        self.allrolls = tuple(allrolls)
        index = self.consequences.result()

        self.count = count_roll
        self.dice = dice
        self.result = tuple(allrolls[index])
        self.result_sum = sum(allrolls[index])
        self.typeroll = 'classic'

        return self


    def rollStats(self, *arg):
        '''Rolling simple stats of dnd5'''
        self.consequences = Consequences(self , adv=None)
        self.Roll('4d6')
        roll = list(self.result)
        # extract min value
        min_r = min(roll)
        roll.remove(min_r)

        self.count = None
        self.dice = None
        self.result_sum = sum(roll)
        self.typeroll = 'stat'
        self.allrolls = None

        return self


    def rollFateDice(self):
        '''Rolling fudge dice'''
        # mult = 2 if throw with adv/disadv
        mult = 2 if self.consequences!=None else 1
        values = (1, 
                 0, 
                 -1,
                )

        allrolls = []
        arsum = []
        for rolls in range(mult):
            rolls = []
            for roll in range(4):
                roll = Dice()
                roll.Roll('1d3')
                rolls.append(values[sum(roll.result)-1])
            allrolls.append(rolls)
            arsum.append(sum(rolls))

        # Make adv/disadv/base
        self.allrolls = tuple(allrolls)
        index = self.consequences.result()

        self.count = 4
        self.dice = 'F'
        self.result = tuple(allrolls[index])
        self.result_sum = sum(allrolls[index])
        self.allrolls = allrolls
        self.typeroll = 'fatedice'

        return self

    def __add__(self , value):
        '''+'''
        return self.result_sum + value

    def __sub__(self, value):
        '''-'''
        return self.result_sum - value

    def __mul__(self, value):
        '''*'''
        return self.result_sum * value

    def __truediv__(self, value):
        '''/'''
        return self.result_sum / value

    # def __lt__(self, value):
    #     '''<'''
    #     return self.result_sum < value

    # def __le__(self, value):
    #     '''<='''
    #     self.result_sum <= value

    # def __eq__(self, value):
    #     '''=='''
    #     self.result_sum == value

    # def __ne__(self, value):
    #     '''!='''
    #     self.result_sum != value

    # def __gt__(self, value):
    #     '''>'''
    #     self.result_sum > value

    # def __ge__(self, value):
    #     '''>='''
    #     self.result_sum >= value

    def __int__(self):
        return self.result_sum

    def __len__(self):
        return self.count * self.dice

    def __contains__(self , item):
        return item in self.result

    def __str__(self):
        '''Formating obj for read'''
        # remove ' and , out of result str
        text = re.sub(r'[\',\,]', '', str(self.result)[1:-1])
        text = re.sub(r'-?\d+', lambda x: f'[{x.group(0)}]', text)

        if self.typeroll == 'fatedice':
            # change the numbers to sign
            val_sign = {
                '0': ' ',
                '1': '+',
                '-1': '-',
            }
            text = re.sub(r'-?\d', lambda x: val_sign[x.group(0)], text)

        elif self.typeroll == 'stat':
            # Maked min number bolding
            min_num = min(self.result)
            text = re.sub(
                f'{min_num}',
                lambda x: f'<b>{x.group(0)}</b>',
                text,
                count=1,
            )

        return text


class Consequences:
    '''Type for adv/dadv/without'''
    def __init__(self , obj , adv=None):
        self.adv = adv
        self.obj = obj
    
    def __eq__(self, value):
        if self.adv == value: return True
        else: return False

    def __ne__(self, value):
        if self.adv != value: return True
        else: return False

    def __bool__(self):
        return self.adv

    def result(self):
        if self.adv == None:
            return 0
        prior = max if self.adv else min
        arsum = [sum(x)for x in self.obj.allrolls]
        index = arsum.index(prior(arsum))
        return index

#print(Dice().rollFateDice())
#print(Dice().rollStats())
print(Dice().Roll('1d20'))
