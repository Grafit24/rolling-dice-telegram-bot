import os
import sys
from typing import Iterable
import unittest
import random as rand
sys.path.append(os.getcwd())
from dice_roll import *

class GenericDiceTest(unittest.TestCase):
    def test_init(self):
        tests = generate_test_set(
            [[-10, 0], [-100, 0]],
            n_samples=20,
            extra=[
                [0, 0],
                [-1, 0],
                [0, 1],
                [0.5, 2],
                [2, 0.6],
                ["da", 1],
                [0, "net"],
            ])
        for test in tests:
            with self.assertRaises(ValueError):
                GenericDice(*test)

    def test_properties(self):
        tests = generate_test_set(
            [[-10, 0], [-100, 0]],
            n_samples=20,
            extra=[
                [0, 0],
                [0, 2],
                [0, 1],
                [0.5, 2],
                [2, 0.6],
                ["da", 1],
                [0, "net"],
            ])
        for test in tests:
            with self.assertRaises(ValueError):
                r = GenericDice(2, 10)
                r.count = test[0]
                r.dice = test[1]

            with self.assertRaises(
                AttributeError, msg="<n_rerolls> changable"):
                r = GenericDice(2, 10)
                r.n_rerolls = 1
            with self.assertRaises(
                AttributeError, msg="<numeric> changable"):
                r = GenericDice(2, 10)
                r.numeric = 1
            with self.assertRaises(
                AttributeError, msg="<results> changable"):
                r = GenericDice(2, 10)
                r.results = (1, 2, 3)
            

    def test_base_roll(self):
        tests = generate_test_set([[1, 1000], [1, 1000]])
        for count, dice in tests:
            dice_range = range(1, dice+1)
            r = GenericDice(count, dice)
            result = r.results
            self.assertEqual(count, len(result), "<count> doesn't equal real len.")
            for res in result:
                self.assertIn(res, dice_range, f"Real dice range doesn't accord.")

    def test_reroll(self):
        test_set = generate_test_set([[1, 20], [1, 100]], n_samples=1)
        test = GenericDice(*test_set[0])
        original_test_numeric = test.numeric
        equal = 0
        not_equal = 0
        for i in range(100):
            test.reroll()
            if test.numeric == original_test_numeric:
                equal += 1
            else:
                not_equal += 1
            self.assertEqual(test.n_rerolls, i+1, "<n_rerolls> calculate wrong!")

        self.assertFalse(not_equal==0, "<rerolls> method doesn't work")

    def op_reverse(self, operation, v1, v2):
        """На вход берёт два объекта и операцию в виде строк 
        над ними возвращает список сток (для eval)"""
        operations_dice_dice = [
            str(v1) + operation + str(v2),
            str(v2) + operation + str(v1),
        ]
        return operations_dice_dice

    def operation_test(self, operation):
        test1 = generate_test_set([[1, 20], [1, 100]], n_samples=1)[0]
        test2 = generate_test_set([[1, 30], [100, 300]], n_samples=1)[0]
        # positive and negative, int and float numbers
        scalars = [rand.randint(-100, 100) for _ in range(50)] +\
            [((-1)**rand.randint(1, 2))*rand.random() for _ in range(20)]

        scalars = filter(lambda x: x!=0, scalars)
        a = GenericDice(*test1)
        b = GenericDice(*test2)

        # test obj x obj 
        for s_test, s_right in zip(
                self.op_reverse(operation, "a" , "b"), 
                self.op_reverse(operation, "a.numeric", "b.numeric")
                ):
            self.assertEqual(eval(s_test), eval(s_right))

        # obj x (int, float)
        for scalar in scalars:
            t = rand.choice([a, b])

            for s_test, s_right in zip(
                    self.op_reverse(operation, "scalar" , "t"), 
                    self.op_reverse(operation, "scalar", "t.numeric")
                ):
                self.assertEqual(eval(s_test), eval(s_right))


    def test_sum(self):
        self.operation_test("+")

    def test_product(self):
        self.operation_test("*")

    def test_divide(self):
        self.operation_test("/")

    def test_minus(self):
        self.operation_test("-")

    def test_roll_list(self):
        test_args = [
            (1, 2),
            (2, 20),
            (10, 100),
            (1, 1000)
        ]
        roll_list = GenericDice.roll_list(test_args)
        for r, args in zip(roll_list, test_args):
            self.assertEqual(r.count, args[0])
            self.assertEqual(r.dice, args[1])
        

class DND5DiceTest(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(ValueError):
            r = DND5Dice(2, 3)
        
        with self.assertRaises(ValueError):
            r = DND5Dice(2, 6)
            r.dice = 21

    def test_roll_list(self):
        test_args = [
            (1, 2),
            (2, 20),
            (10, 100),
            (1, 8)
        ]
        roll_list = DND5Dice.roll_list(test_args)
        for r, args in zip(roll_list, test_args):
            self.assertEqual(r.count, args[0])
            self.assertEqual(r.dice, args[1])

    def test_roll_stats(self):
        stats = DND5Dice.roll_stats()
        self.assertTrue(len(stats)==6)
        for r in stats:
            res = sorted(list(r.results))[1:]
            self.assertEqual(sum(res), r.numeric)
            self.assertEqual(len(r.results), 4)


class FudgeDiceTest(unittest.TestCase):
    def test_roll_fudje(self):
        r = FudgeDice(10)
        self.assertEqual(r.count, len(r.results))
        for res in r.results:
            self.assertIn(res, [-1, 0, 1])

    def test_roll_lists(self):
        raw_test_set = generate_test_set([[1, 10]])
        test_set = list(map(lambda x: x[0], raw_test_set))
        results = FudgeDice.roll_list(test_set)
        self.assertEqual(len(results), len(test_set))
        for r in results:
            self.assertIsInstance(r, FudgeDice)


class CustomDiceTest(unittest.TestCase):
    def test_init(self):
        right_test = (1, 4, {1:"one", 2:"two", 3:"three", 4:"four"})
        r = CustomDice(*right_test)
        self.assertIn(r.results[0], list(right_test[2].values()))

        false_tests = []
        false_tests.append((1, 4, {-1:"one", 2:"two", 3:"three", 4:"four"}))
        false_tests.append((1, 4, {1:"one", 2:"two", 3:"three", 4:"four", 5:"five"}))
        false_tests.append((1, 4, 1))

        for test in false_tests:
            with self.assertRaises(ValueError,
                msg=f"ValueError not raised : args={test}"):
                CustomDice(*test)

        with self.assertRaises(ValueError):
            r.dmap = {1:"one", 2:"two", 3:"three", 4:"four", 5:"five"}

    def test_reroll(self):
        right_test = (1, 5, {1:"one", 2:"two", 3:"three", 4:"four", 5:"five"})
        r = CustomDice(*right_test)
        r.reroll()
        self.assertIn(r.results[0], list(right_test[2].values()))
    
    def test_roll_custom(self):
        right_test = (1, 5, {1:"one", 2:"two", 3:"three", 4:"four", 5:"five"})
        r = CustomDice(*right_test)
        res =  r._roll_custom()
        self.assertIn(res[0], list(right_test[2].values()))

    def test_roll_list(self):
        tests = [
            (1, 2, {1:"один", 2:"два"}),
            (2, 3, {1:"один", 2:"два", 3:"три"})
        ]
        rolls = CustomDice.roll_list(tests)
        for r in rolls:
            self.assertIsInstance(r, CustomDice)

def generate_test_set(value_range: List[Tuple[int]], n_samples=100, extra=None):
    """Список переменных и value_range 
    для каждой из них вида [a, b]
    """
    tests = []
    for _ in range(n_samples):
        args = [rand.randint(r1, r2) for r1, r2 in value_range]
        tests.append(args)
    return tests



if __name__ == "__main__":
    unittest.main(verbosity=2)