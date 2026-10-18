# SPDX-License-Identifier: Apache-2.0
"""Source-bound fixed-word native extraction-space equality; standard library only."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
from algebra import PRIME, constraints, need, quotient, replay, same_kernel
from operators import certify

PACKAGE = Path(__file__).resolve().parent


def load_words(package=PACKAGE):
    words = {}
    for record in json.loads((package / 'INPUTS.json').read_text()):
        path = package / record['path']
        need(not path.is_symlink(), 'input must be a regular file')
        data = path.read_bytes()
        need(hashlib.sha256(data).hexdigest() == record['sha256'], 'source input digest')
        if path.suffix == '.gz':
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
                decoded = stream.read(800001)
            need(len(decoded) <= 800000, 'word size limit')
            words[path.stem.split('.')[0]] = json.loads(decoded)
    need(set(words) == {'base', 'extra'}, 'both providers')
    return words


def matrix_digest(matrix):
    payload = [[r, [[c, operator, str(a)] for (c, operator), a in sorted(row.items())]]
               for r, row in sorted(matrix.items())]
    return hashlib.sha256(json.dumps(payload, separators=(',', ':')).encode()).hexdigest()


def check(word):
    matrix = replay(word)
    aliases, operators = certify(word)
    native = quotient(matrix, aliases)
    # Positive native warps are not identities, so the scalar M0 is unchanged.
    need(aliases[0] == 0 and all(aliases[i] != 0 for i in aliases if i), 'no new scalar terms')
    fr, fl, helpers, live = constraints(matrix, word)
    nr, nl, helpers2, live2 = constraints(native, word)
    need((helpers, live) == (helpers2, live2), 'same input/output domains')
    result = {'operators': operators,
              'free_matrix_sha256': matrix_digest(matrix),
              'grouped_matrix_sha256': matrix_digest(native),
              'free_terms': sum(map(len, matrix.values())),
              'grouped_terms': sum(map(len, native.values())),
              'changed_term_count_rows': [r for r in matrix if len(matrix[r]) != len(native[r])],
              'right': same_kernel(fr, nr, helpers),
              'left': same_kernel(fl, nl, live)}
    need(result['right']['nullity'] == 119 and result['left']['nullity'] == 181,
         'pinned extraction-space dimensions')
    need(operators['rank'] == 59, 'pinned operator dimension')
    return result


def run(package=PACKAGE):
    results = {tag: check(word) for tag, word in sorted(load_words(package).items())}
    return {'status': 'PASS_NATIVE_WARP_EXTRACTION_BOUNDARY', 'prime': PRIME,
            'providers': results, 'new_kappa': False,
            'scope': 'Fixed six-skip M; rational scalar two-sided extraction, protected H and Cv=0; finite native K_G columns.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run()
    data = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(data)
    else:
        need(result == json.loads((PACKAGE / 'RESULT.json').read_text()), 'stored receipt comparison')
    print('PASS_NATIVE_WARP_EXTRACTION_BOUNDARY providers=2 independent_operators=59 right_nullity=119 left_nullity=181 no_new_kappa')


if __name__ == '__main__':
    main()
