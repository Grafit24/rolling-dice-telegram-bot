import os
import re

from abc import ABC, abstractmethod
from unittest import result

class Details:
    def __init__(self, brackets=("[", "]"), crit=True, space=" ", html_highlight=("<b>", "</b>")) -> None:
        self.template = "{open}{html_open}{value}{html_close}{close}{space}"
        self.brackets = brackets
        self.space = space
        self.html_highlight = html_highlight
        self.crit = crit
        self._washighlight = False

    def get(self, dice, func)-> str:
        result = ""
        for value in dice.results:
            if func(value, dice) and self.crit:
                html_open, html_close = self.html_highlight
            else:
                html_open = html_close = ""
            result += self.template.format(
                    html_open=html_open, value=value, html_close=html_close,
                    open=self.brackets[0], close=self.brackets[1],
                    space=self.space
                    )
        self._washighlight = False
        return result

    @staticmethod
    def classic_roll_crit(value, dice):
        return (value == dice.min_value) or (value == dice.dice)

    def highlight_dnd5stat(self, value, dice):
        delta = sum(dice.results) - dice.numeric
        cond = (delta == value) and not self._washighlight
        if cond:
            self._washighlight = True
        return cond
                

class DiceParser(ABC):

    def __init__(self, message_template, sep, details_parser) -> None:
        self.message_template = message_template
        self.sep = sep
        self.details_parser = details_parser

    @abstractmethod
    def parse_input(self, input_message):
        pass

    @abstractmethod
    def parse_output(self, result, verbosity):
        pass 


class GenericDiceParser(DiceParser):
    def parse_input(self, input_message):
        message = re.sub(r'\s+', ' ', input_message).strip()
        dice_operation = re.findall(r'((\d*)d(\d+))+', message)
        self.details_template = re.sub(r'(\d*d\d+)+', '%s', message)
        self.dices = []
        for _, count, dim in dice_operation:
            count = int(count) if count != "" else 1
            dim = int(dim)
            self.dices.append((count, dim))
        return self.dices

    def parse_output(self, result_dices, verbosity):
        if verbosity == 1:
            details_dices = [str(dice.numeric) for dice in result_dices]
        elif verbosity == 2:
            details_dices = [
                self.details_parser.get(dice, Details.classic_roll_crit) 
                for dice in result_dices
                ]

        formula = self.details_template % tuple([dice.numeric for dice in result_dices])
        if (verbosity == 0) or (self.details_template == "%s"):
            message = self.message_template.format(
                result=eval(formula),
                details="", sep=""
                )
        else:
            message = self.message_template.format(
                result=eval(formula),
                details=(self.details_template % tuple(details_dices)), 
                sep=self.sep
                )

        return message

        
class DND5RollsParser(DiceParser):

    # TODO make more hard parsing (/rN +6 = 1dN + 6 не 6dN)
    def parse_input(self, input_message):
        message = re.sub(r'\s+', ' ', input_message).strip()
        args = message.split()[1:]
        self.test_args(args)
        self.len_args = len(args)
        count = int(args[0]) if len(args) >= 1 else 1
        self.add = int(args[1]) if len(args) > 1 else 0
        return count

    def parse_output(self, result_dice, verbosity):
        result = result_dice.numeric + self.add
        if (verbosity > 0) and (self.len_args):
            if self.add != 0:
                sign = "+" if self.add > 0 else "-"
                additional = f"{sign} {abs(self.add)}"
            else:
                additional = ""

            if verbosity == 1:
                details = f"{result_dice.numeric} {additional}"
            elif verbosity > 1:
                details = f"{self.details_parser.get(result_dice, Details.classic_roll_crit)} {additional}"

            message = self.message_template.format(
                result=result, sep=self.sep, 
                details=details
                )
        else:
            message = self.message_template.format(
                result=result, sep="", 
                details=""
                )
        return message

    def test_args(self, args):
        if len(args) > 2:
            raise ValueError("Too many arguments!")
        try:
            [int(arg) for arg in args]
        except ValueError:
            raise ValueError("Incorrect arguments!")
        
        if (len(args) > 0) and (int(args[0]) < 0):
            raise ValueError("Incorrect count(<0)")


class DND5StatsParser(DiceParser):
    def __init__(self, message_template, row_template, sep, details_parser, default_nstats=6) -> None:
        super().__init__(message_template, None, details_parser)
        self.default_nstats = default_nstats
        self.row_template = row_template
        self.sep = sep

    def parse_input(self, input_message):
        message = re.sub(r'\s+', ' ', input_message).strip()
        args = message.split()[1:]
        self.test_args(args)
        count = int(args[0]) if len(args) > 0 else self.default_nstats
        return count

    def parse_output(self, result_stats, verbosity):
        message_base = ""
        for stat in result_stats:
            if verbosity == 0:
                message_base += self.row_template.format(
                    result=stat.numeric, details="", sep=""
                ) + "\n"
            else:
                details = self.details_parser.get(
                    stat, self.details_parser.highlight_dnd5stat
                    )
                message_base += self.row_template.format(
                    result=stat.numeric, details=details, sep=self.sep
                    ) + "\n"
        # remove last \n
        stats = message_base[:-1]
        return self.message_template.format(
            stats=stats
        )

    def test_args(self, args):
        if len(args) > 1:
            raise ValueError("Too many arguments!")
        elif len(args) == 1:
            if not isinstance(args[0], int):
                raise ValueError("Argument must be Integer!")
            elif int(args[0]) <= 0:
                raise ValueError(f"Incorrect value {args[0]}<=0!")

