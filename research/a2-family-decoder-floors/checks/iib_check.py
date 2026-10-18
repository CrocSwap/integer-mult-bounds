# Case II(b) exact relaxation (m' = 9, no e9 row) and the m >= 10 relaxation (with e9 row), off and on the B-locus.  usage: UNIT=... [A2TRI=a,b,c] python iib_check.py
# Expected (README): II(b) off the locus >= 65 / 62 / 74 (P112 / P104 / E8), on the locus 66 / 63 / 75;  m' >= 10 off the locus >= 68 / 64 / 77 (monotone in m': removing a term never raises the cost).
from iib import *
EXP = {'P112': (65, 66, 68), 'P104': (62, 63, 64), 'E8': (74, 75, 77)}[UNIT]
res = relaxations(range(9, 14))
print(UNIT, 'X', Xs, 'II(b) relaxation (m\'=9, no e9):  off B-locus', res['off'][9], ' on B-locus', res['on'][9])
print(UNIT, 'm\' >= 10 relaxation with e9 row: off', res['off9'], ' on', res['on9'])
assert res['off'][9] == EXP[0] and res['on'][9] == EXP[1], (res['off'][9], res['on'][9], EXP)
off10 = min(res['off9'][m] for m in range(10, 14)); assert res['off9'][10] == off10 == EXP[2], (res['off9'], EXP)
assert all(res['off9'][m] <= res['off9'][m + 1] for m in range(10, 13))
print('PASS II(b) relaxation %s %s: off the B-locus >= %d, on it %d; m >= 10 off the B-locus >= %d (the S+T-only value with e9 is %d; the B-locus m >= 10 case is OPEN, README Scope)' % (UNIT, Xs, EXP[0], EXP[1], EXP[2], res['on9'][10]))
