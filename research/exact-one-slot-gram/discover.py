"""Optional exact candidate producer (requires python-flint==0.9.0).

Acceptance is performed separately by verify.py using integer Horner evaluation.
This file is not imported by the verifier and writes only the requested output.
"""
import argparse
import json
from pathlib import Path
import time
from hashlib import sha256
import sys

import flint
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import (read_query, symmetries, label_orbits, sector, dense_matrix,
                   zero_matrices, SOURCE_SHA256, require)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    roots, ports = read_query()
    generators = symmetries(roots, ports)
    orbits = label_orbits(generators)
    print('label orbits', [(v[0], len(v)) for v in orbits], flush=True)
    result = {'operator': 'B=4*A_1', 'sectors': []}
    if args.output.exists():
        result = json.loads(args.output.read_text())
        require(result.get('operator') == 'B=4*A_1', 'resume operator')
    done = {(x['c'], x['t'], x['s']) for x in result['sectors']}
    for orbit in orbits:
        c = orbit[0]
        if not c:
            continue
        for t in (0, 1):
            for s in (1, -1):
                if (c,t,s) in done:
                    continue
                start = time.monotonic()
                addresses, targets, signs = sector(c,t,s,ports)
                matrix = dense_matrix(roots, targets, signs)
                polynomial = flint.fmpz_mat(matrix.tolist()).minpoly()
                coefficients = [int(x) for x in polynomial.coeffs()]
                result['sectors'].append({'c':c, 't':t, 's':s, 'coefficients':coefficients})
                args.output.write_text(json.dumps(result, indent=2)+'\n')
                print('sector',c,t,s,'degree',polynomial.degree(),'seconds',round(time.monotonic()-start,2),flush=True)
    zero = flint.fmpz_poly([1])
    seen = set()
    for matrix in zero_matrices(roots, ports):
        key = tuple(int(x) for x in matrix.reshape(-1))
        if key in seen:
            continue
        seen.add(key)
        p = flint.fmpz_mat(matrix.tolist()).minpoly()
        zero = (zero*p)//zero.gcd(p)
    result['zero'] = {'coefficients': [int(x) for x in zero.coeffs()]}
    total = zero
    for item in result['sectors']:
        p = flint.fmpz_poly(item['coefficients'])
        total = (total*p)//total.gcd(p)
    result['schema_version'] = 1
    result['source_sha256'] = SOURCE_SHA256
    result['degree'] = total.degree()
    result['polynomial_sha256'] = sha256(json.dumps([int(x) for x in total.coeffs()],separators=(',',':')).encode()).hexdigest()
    result['sectors'].sort(key=lambda item: (item['c'],item['t'],-item['s']))
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('CANDIDATE_ONLY', 'degree', total.degree(), 'run verify.py separately',flush=True)


if __name__ == '__main__':
    main()
