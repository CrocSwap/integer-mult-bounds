#!/usr/bin/env python3
"""Optional numerical dual discovery. The exact verifier decides validity.

Jerry Chen / @CubeJerry, substantial OpenAI GPT-6 Astra Pro assistance.
Apache-2.0. Tested with numpy==2.3.5, scipy==1.17.0; no network calls.
"""
import argparse
import json
import math
from pathlib import Path

from model import CapacityModel, INTERVALS, need


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    need(args.output.resolve() != Path(__file__).with_name('dual-certificate.json').resolve(),
         'write a candidate elsewhere; do not overwrite the frozen certificate')
    import numpy as np
    from scipy.optimize import linprog
    scale = 10**8
    discovery_kappa = '.0033718004755'
    costs = np.array([(8*(b-a+1))**(1-float(discovery_kappa)) for a,b in INTERVALS])
    matrix = np.array([[int(c<=a and b<=d) for c,d in INTERVALS]
                       for a,b in INTERVALS], dtype=float)
    diagonal = [k for k,(a,b) in enumerate(INTERVALS) if a==b]
    engine = CapacityModel(); cases = []
    for a in range(9):
        for b in range(9,18):
            caps, demands, _ = engine.case(a,b)
            result = linprog(costs, A_ub=matrix, b_ub=caps,
                             A_eq=matrix[diagonal], b_eq=demands,
                             bounds=(0,None), method='highs')
            need(result.success, 'numerical discovery failed: '+result.message)
            cases.append({'a':a,'b':b,
                          'alpha':[math.floor(float(x)*scale) for x in result.ineqlin.marginals],
                          'beta':[math.floor(float(x)*scale)-4 for x in result.eqlin.marginals]})
    candidate = {'schema_version':1,'scale':scale,'discovery_kappa':discovery_kappa,
                 'verification_kappa':'.00337180','cases':cases}
    args.output.write_text(json.dumps(candidate, separators=(',',':'))+'\n')
    print(json.dumps({'status':'CANDIDATE_ONLY','cases':len(cases),
                      'numpy':np.__version__,'output':str(args.output)}))


if __name__ == '__main__':
    main()
