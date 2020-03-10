"""Dice roller"""
from typing import List , Optional , Union
import random
import re


class Dice:
    """Roll any dice and stores data about it.

    Attributes
    ----------
    count: int
        The count of dice roll.
            =None if it's typeroll is stat
    dice: int
        The number of faces dices 
        -typeroll=stat-
            =None 
    result: tuple
        Result of rolling
        -typeroll=stat-
            list is full so include in minimal value
            (Which not included in result_sum)
    result_sum: int
        Sum of result
        -typeroll=stat-
            except minimal value of result
    ---Optinal---
    consequences: Consequences(obj , adv)
        For anything doubleroll(Example: roll with advantage/disadvantage)
    allrolls: list
        List with 2(Always) throw, include in result inappropriate consequences.
    typeroll: str
        Name type of dice or special roll 

    Methods
    -------
    Roll(count_dice: str)-> Dice
        Roll any dices by template ndn(n - nature numbers)
    
    rollStats()-> Dice
         Roll stats for dnd5.
        (4d6 roll and remove minimal dice of it)
        Note:
            Have not consequences
    
    rollFateDice()-> Dice
         Roll fudge dice.
        (4d3 with values [+] [-] [])
    """
    count: int
    dice: int
    result: tuple
    result_sum: int
    #Optional
    consequences: 'Consequences'
    allrolls: list
    typeroll: str

    def __init__(self , adv:Optional[bool] = None):
        self.consequences = Consequences(obj=self , adv=adv)
        

    def Roll(self, count_dice: str)-> 'Dice':
        """Roll any dice by template(ndn ,  n - natural number).
        Can rolling dice with consequences

        Parameters
        ----------
        count_dice: str
            template is ndn , n - nature number.
        """

        # mult = 2 if throw with adv/disadv
        mult = 2 if self.consequences!=None else 1

        # unpack data 
        count_roll, dice = count_dice.split('d')
        count_roll = int(count_roll)
        dice = int(dice)

        allrolls = []
        for rolls in range(mult):
            rolls = [random.randint(1 , dice) for roll in range(count_roll)]
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


    def rollStats(self)-> 'Dice':
        '''Roll simple stats of dnd5.
        (4d6 roll and remove minimal dice of it)
        
        result attr = len(list = 4)
        result_sum attr = sum(len(list) = 3)

        Example
        -------
        4d6 -> [4 , 5 , 2 , 1] - min -> [4 , 5 , 2] = 11
        4d6 -> [1 , 1 , 1 , 1] - min -> [1 , 1 , 1] = 3
        '''
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


    def rollFateDice(self)-> 'Dice':
        '''Roll fudge dice.(4d3 with values [+] [-] [])
        '''
        # mult = 2 if throw with adv/disadv
        mult = 2 if self.consequences!=None else 1
        values = (1, 
                 0, 
                 -1,
                )

        allrolls = []
        for rolls in range(mult):
            rolls = [
                values[int(Dice().Roll('1d3')) - 1] for roll in range(4)
                ]
            allrolls.append(rolls)

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
        return self.count

    def __contains__(self , item):
        return item in self.result

    def __str__(self):
        '''Formating obj for read

        Examples
        --------
        classic
            5d20
            [10] [20] [1] [12] [6]
        fatedice
            [+] [ ] [-] [ ]
        stat
            [5] [<b>1</b>] [4] [2]
        '''
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
    '''Type for adv/dadv/without

    Attributes
    ----------
    adv: bool , None
        True - with advantage
        False - with disadvantage
        None - without
    obj: Dice
        Object with data about rolls
    
    Methods
    -------
    result()-> int
        Set index result by advantage/disadvantage
        and return it. 
    '''
    adv: Union[bool , None]
    obj: 'Dice'

    def __init__(self , obj , adv=None):
        self.adv = adv
        self.obj = obj
    

    def __eq__(self, value):
        '''=='''
        if self.adv == value: return True
        else: return False


    def __ne__(self, value):
        '''!='''
        if self.adv != value: return True
        else: return False


    def __bool__(self):
        return self.adv


    def result(self)-> int:
        '''Set index result by advantage/disadvantage
        and return it. Function use for find in allrolls 
        max(adv)/min(disadv)/None(without)

        Returns
        -------
        index: int
            allrolls[index] = result
        '''
        if self.adv == None:
            return 0
        prior = max if self.adv else min
        arsum = [sum(x)for x in self.obj.allrolls]
        index = arsum.index(prior(arsum))
        return index