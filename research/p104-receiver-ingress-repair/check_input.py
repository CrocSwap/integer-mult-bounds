"""Evaluate a nine-coordinate separator on the literal original paid word."""
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from word import read_word, require


POINT = {770: -2, 663: -2, 825: -1, 780: -1, 1288: -Fraction(1,845660160),
         1055: Fraction(218,1395), 1225: Fraction(17,2), 1238: Fraction(1888,333),
         1239: Fraction(64,27)}


def evaluate(w, forms, point):
    values = {~j: point.get(j,0) for j in range(len(w['initial']))}
    for k in w['schedule']:
        values[k] = sum(q*values[j] for j,q in forms[k].items())
    return values


def main():
    w, forms, moves, terminals = read_word()
    values = evaluate(w, forms, POINT)
    local = {~j for j,c in enumerate(w['initial']) if c in (11,58)}
    local.update(k for k,(a,b) in moves.items() if b in (11,58) or (a,b) == (3,278))
    receiver = {k for k,(a,b) in moves.items() if b == 127 and k != 88}
    outgoing = {k for k,(a,b) in moves.items() if a == 278 and k != 95914}
    require((len(local),len(receiver),len(outgoing)) == (18,901,9), 'full local and receiving stocks')
    require(not any(values[k] for k in local | receiver | outgoing), 'annihilator')
    require(values[155442] == 1 and terminals[155442] == 127, 'required output separates zero')
    require(evaluate(w, forms, {})[155442] == 0, 'zero control')
    mutated = evaluate(w, forms, {j:q for j,q in POINT.items() if j != 1288})
    require(any(mutated[k] for k in local | receiver), 'omitting the large-denominator atom')
    print('PASS nine-coordinate input kills all 18 possible stock directions,')
    print('all 901 old receiver arrivals and all nine old egresses. Required output is one.')


if __name__ == '__main__':
    main()
