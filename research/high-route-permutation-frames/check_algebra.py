"""Separate exact row-vector semantics, including deliberately bad schedules."""
from fractions import Fraction as F
from itertools import product
import random

from frames import defer, schedule, price, paid_price, need


def evaluate(word, vector):
    row = list(map(F, vector))
    for kind, target, control, value in word:
        if kind == "swap":
            row[target], row[control] = row[control], row[target]
        elif kind == "add":
            row[target] += F(value)*row[control]
        elif kind == "scale":
            row[target] *= F(value)
        else:
            raise ValueError("unknown oracle operation")
    return tuple(row)


def equal(left, right, n):
    return all(evaluate(left, v) == evaluate(right, v)
               for v in (tuple(int(i == j) for i in range(n)) for j in range(n)))


def run():
    rng = random.Random(9)
    coefficients = tuple(map(F, (-4, -2, -1, 1, 2, 4))) + (F(1,2), F(-1,4))
    count = 0
    improved = 0
    for n in range(2, 9):
        for _ in range(120):
            word = []
            for _ in range(rng.randrange(1, 45)):
                t, c = rng.sample(range(n), 2)
                kind = rng.choice(("add", "scale", "swap"))
                word.append((kind, t, c if kind != "scale" else t,
                             F(1) if kind == "swap" else rng.choice(coefficients)))
            chosen, candidate = schedule(word, n), defer(word, n)
            need(equal(word, candidate, n) and equal(word, chosen, n), "exact linear map")
            need(price(chosen) <= price(word), "complete native-call nonregression")
            need(paid_price(chosen,n) <= paid_price(word,n), "paid setup/adapter nonregression")
            need(all(k != "add" or c < t for k,t,c,v in candidate), "ordered candidate ADD")
            need(sorted((k,v) for k,t,c,v in word if k != "swap") ==
                 sorted((k,v) for k,t,c,v in chosen if k != "swap"), "scalar work preserved")
            count += 1
            improved += price(chosen) < price(word)
    # Exhaust every word up to length four in this two-field alphabet.
    alphabet = (("add",0,1,F(1)), ("add",1,0,F(-1)),
                ("swap",0,1,F(1)), ("scale",0,0,F(1,2)))
    exhaustive = 0
    for size in range(5):
        for word in product(alphabet, repeat=size):
            need(equal(word, schedule(word, 2), 2), "exhaustive small exact map")
            exhaustive += 1
    repeated = (("add",0,1,F(1)),)*9
    chosen = schedule(repeated, 2)
    need((price(repeated), price(chosen)) == (18,2), "repeated reverse ADD bill")
    need(chosen[-1][0] == "swap" and not equal(repeated, chosen[:-1], 2),
         "unpaid terminal frame must be rejected")
    bad = list(chosen)
    k,t,c,v = bad[1]
    bad[1] = k,c,t,v
    need(not equal(repeated, bad, 2), "wrong remapped field must be rejected")
    failures = 0
    for w,n in [((("unknown",0,1,1),),2), ((("add",0,0,1),),2),
                ((("scale",0,0,0),),2), ((("swap",0,1,2),),2),
                ((("add",0,2,1),),2), ((),0)]:
        try:
            schedule(w,n)
        except ValueError:
            failures += 1
        else:
            raise ValueError("invalid input accepted")
    return dict(seed=9, random_words=count, strictly_improved=improved,
                exhaustive_words=exhaustive, invalid_controls=failures,
                semantic_controls=2, repeated_add_native_calls=[18,2])
