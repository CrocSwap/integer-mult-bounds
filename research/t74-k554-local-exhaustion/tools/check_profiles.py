"""Exact frame optimum (PR1186 solver) of both current words equals their published local profiles."""
import json
import _paths
import harness as H
for path, want in [(_paths.BASE, {1: 2348, 2: 500, 3: 416, 4: 130, 5: 82}), (_paths.EXTRA, {1: 2340, 2: 508, 3: 420, 4: 126, 5: 82})]:
    P = H.Pricer(str(path)); assert P.base_profile == want, (path.name, P.base_profile)
    rep = {int(k): v for k, v in P.base['report']['local_profile'].items()}; rep.pop(8); assert rep == want
    print(path.name, 'optimum', P.base_profile, 'cost', P.base_cost)
print('PASS_PROFILES')
