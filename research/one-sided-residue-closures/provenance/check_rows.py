# multiset comparison: d>=4 rows of open_rows.json vs ../data/rows_input.csv
import csv, json, sys, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(sys.argv[1]))
a = Counter((d, k, tuple(sorted(ws, reverse=True)), e) for d, k, ws, e in L if d >= 4)
b = Counter((int(r['d']), int(r['slack']), tuple(sorted(eval(r['weights']), reverse=True)), int(r['e']))
            for r in csv.DictReader(open(os.path.join(HERE, '..', 'data', 'rows_input.csv'))))
print('filter d>=4 survivors:', sum(a.values()), ' rows_input.csv rows:', sum(b.values()))
if a == b: print('PASS d>=4 survivors of the dominance filter equal rows_input.csv (multiset)')
else:
    print('FAIL only in filter:', list((a-b).items())[:5], ' only in csv:', list((b-a).items())[:5]); sys.exit(1)
