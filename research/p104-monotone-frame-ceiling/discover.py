"""Find a dual candidate. This optional numerical search is not a proof.

The recorded discovery used NumPy 2.5.4 and SciPy 1.18.1.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from frames import graph
from model import model
from verify import model_hash, source_bytes


def run(args):
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    from math import log

    spec = json.loads((HERE/'CASES.json').read_text())[args.case]
    raw = source_bytes(HERE/'input'/spec['word'], spec['sha256'])
    word = json.loads(gzip.decompress(raw))
    variables, cost, eq, ub, tariffs = model(word, graph(word), float(spec['kappa']))
    if args.derivative:
        cost = [0.]*len(variables)
        for j, weight, rank in tariffs:
            cost[j] = (0. if not rank else -weight*rank*log(rank) if weight >= 0
                       else -weight*rank**(1-.0034)*log(rank))

    def sparse(rows):
        rr, cc, dd = [], [], []
        for i, (row, _) in enumerate(rows):
            for j, value in row.items():
                rr.append(i)
                cc.append(j)
                dd.append(value)
        return coo_matrix((dd, (rr, cc)), shape=(len(rows), len(cost))).tocsr()

    result = linprog(cost, A_ub=sparse(ub), b_ub=[b for _, b in ub],
                     A_eq=sparse(eq), b_eq=[b for _, b in eq], bounds=(0, 1),
                     method='highs', options={'time_limit':60})
    if not result.success:
        raise RuntimeError(result.message)
    scale = 10**10
    certificate = {'model_sha256':model_hash(variables, eq, ub, tariffs), 'scale':scale}
    for key, values in [('eq', result.eqlin.marginals), ('ub', result.ineqlin.marginals)]:
        rows = []
        for i, value in enumerate(values):
            coefficient = round(float(value)*scale)
            if key == 'ub':
                coefficient = min(0, coefficient)
            if coefficient:
                rows.append([i, coefficient])
        certificate[key] = rows
    with args.output.open('x') as stream:
        json.dump(certificate, stream, indent=2)
        stream.write('\n')
    print('DISCOVERY_ONLY', spec['name'], result.fun, args.output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', type=int, choices=[0, 1], required=True)
    parser.add_argument('--derivative', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args())
