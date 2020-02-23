"""Dump for any different fun"""
import random


class Dice:
    """Roll dice and stores data about it"""
    count: int
    dice: int
    isprior: bool
    all_rolls: tuple
    result: tuple

    def Roll(self, count_dice: str):
        """Roll any dice by template"""
        # Variables
        prior = None
        all_rolls = []
        all_sum_rolls = []
        # unloading array
        if count_dice[0] == 'd':
            count_dice = '1' + count_dice
            print(count_dice)
        count_roll, dice = count_dice.split('d')
        count_roll = int(count_roll)
        # try dice make int
        try:
            mult = 1
            dice = int(dice)
        # if dice make except that
        # in dice have char - advantage or disadvantage
        except:
            mult = 2
            # set adv or disadv
            if dice[-1] in ('A', 'Adv', 'adv'):
                prior = max
            elif dice[-1] in ('D', 'Disadv', 'disadv'):
                prior = min
            # else: raise Error
            # exclude char
            dice = int(dice[:-1])
        rolls = []
        # Roll with adv/dadv and  without
        for y in range(mult):
            # Roll every dice
            for x in range(count_roll):
                roll = random.randint(1, dice)
                rolls.append(roll)
            all_rolls.append(rolls.copy())
            all_sum_rolls.append(sum(rolls))
            rolls.clear()
        #
        print('All rolls :', str(all_rolls))
        # Make adv/disadv
        if prior != None:
            index = all_sum_rolls.index(prior(all_sum_rolls))
            self.isprior = True
        # Make without
        else:
            self.isprior = False
            index = 0
        # Set var
        self.count = count_roll
        self.dice = dice
        self.all_rolls = tuple(all_rolls)
        self.result = tuple(all_rolls[index])
        self.isstats = False

    # def rollStats(self, *arg):
    #     '''Rolling simple stats of dnd5'''
    #     self.Roll('4d6')
    #     self.isstats = True
    #     roll = list(self.result)
    #     min_r = min(roll)
    #     roll.remove(min_r)
    #     self.exc_id = self.result.index(min_r)
    #     self.result_stats = sum(roll)

    def rollFateDice(self) -> tuple:
       pass

    def __str__(self):
        text = 'count : %d\ndice : %d\nresult : %r' % (self.count,
                                                       self.dice,
                                                       self.result
                                                       )
        return text
