import os
import re

class Details:
    def __init__(self, brackets=("[", "]"), crit=True, space=" ", html_highlight=("<b>", "</b>")) -> None:
        self.template = "{open}{html_open}{value}{html_close}{close}{space}"
        self.brackets = brackets
        self.space = space
        self.html_highlight = html_highlight
        self.crit = crit

    def get(self, dice)-> str:
        result = ""
        for value in dice.results:
            # TODO min value for custom
            if (value == dice.dice) or (value == dice.min_value) and self.crit:
                html_open, html_close = self.html_highlight
            else:
                html_open = html_close = ""
            result += self.template.format(
                    html_open=html_open, value=value, html_close=html_close,
                    open=self.brackets[0], close=self.brackets[1],
                    space=self.space
                    )
        return result
                

class GenericDiceParser:
    def __init__(self, message_template, sep=":", details_parser=Details()) -> None:
        self.message_template = message_template
        self.sep = sep
        self.details_parser = details_parser

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

    def pasrse_output(self, result_dices, verbosity):
        if verbosity == 1:
            details_dices = [str(dice.numeric) for dice in result_dices]
        elif verbosity == 2:
            details_dices = [self.details_parser.get(dice) for dice in result_dices]

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

        
