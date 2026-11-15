rows="""# NETC19 features (inherits rows 65-86)
| # | feature | status | note |
|---|---|---|---|
| 87 | Unit-level route census `plan19x.py`,`cen19.py` | DONE | (content,G) pairs 5,705 vs 5,790 units; exact chain cover (t1 asc + nested frames) 5,790->5,403 projective; hot content 2,953 gives = 53 V-mix helpers |
| 88 | Chain merge with giveq `m19.py`,`run19.py` | DONE (exact) | q=1 chain EXACT+accxfast; scaled distinct-receiver pair EXACT; scaled repeated-receiver chains FAIL V-mix |
| 89 | Exact builds q=1 chains 1/10/96 | DONE (exact) | D0 -13.7/-116.9/-548.0 vs control 40,558.2 (4.066x -> 4.011x), accxfast PASS all |
| 90 | Route-packing planner | NOT BUILT | ceiling 548 (q=1) to 1,757 (any q, partly unsettled), overlaps NETC15 |
"""
assert rows.count('\n')==7 and '| 90 |' in rows
open('FEATURES.md','w').write(rows)
