#!/usr/bin/env python3
"""Exact constructive range, shortest loops, and selected dirty-word witness."""
import argparse
import hashlib
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent))
import algebra as A
import common as C
import independent as I
import selected_word


def mathematical_report():
    records = []
    for n, z in ((2, 1), (3, 1), (3, 2)):
        result, representatives = A.census(n, z)
        result['independent'] = I.joint_census(n, z, representatives)
        records.append(result)
    parabolic = []
    for n in range(2, 6):
        for z in range(1, min(3, n-1)+1):
            count = 0
            maximum = 0
            digest = hashlib.sha256()
            for p in A.all_parabolic(n, z):
                word = A.joint_word(A.identity(n), p, z)
                A.need(A.word_matrix(n, word) == A.identity(n) and A.word_matrix(n, word, z) == p,
                       'identity-fiber constructor')
                A.need(I.evaluate(n, word) == tuple(range(1 << n)), 'literal raw identity')
                A.need(I.evaluate(n, [g for g in word if g[0] < z]) == I.from_rows(p), 'literal projected identity fiber')
                digest.update(C.canonical([list(p), word]))
                count += 1
                maximum = max(maximum, len(word))
            A.need(count == A.order_gl(z)*(1 << (z*(n-z))), 'parabolic inventory')
            parabolic.append(dict(n=n, z=z, matrices=count, maximum_loop_gates=maximum, sha256=digest.hexdigest()))
    fixtures = []
    for z, q in ((1, 1), (1, 7), (2, 1), (7, 1), (3, 5), (5, 3), (8, 8),
                 (16, 1), (1, 16), (16, 16), (31, 1), (1, 31), (32, 32)):
        n = z+q
        for seed in range(3):
            def gates(count, destinations, tag):
                out = []
                for j in range(count):
                    h = hashlib.sha256(C.canonical([n, z, seed, tag, j])).digest()
                    d = int.from_bytes(h[:8], 'little') % destinations
                    s = int.from_bytes(h[8:16], 'little') % (n-1)
                    s += s >= d
                    out.append((d, s))
                return out
            raw = A.word_matrix(n, gates(3*n, n, 'raw'))
            projected = A.word_matrix(n, gates(4*n, z, 'projected'))
            word = A.joint_word(raw, projected, z)
            A.need(A.word_matrix(n, word) == raw and A.word_matrix(n, word, z) == projected, 'larger constructor')
            columns = I.source_columns(n, [('add', d, s) for d, s in word])
            shadow = I.source_columns(n, [('add', d, s) for d, s in word if d < z])
            A.need(tuple(I.transpose_columns(columns)) == raw and tuple(I.transpose_columns(shadow)) == projected,
                   'independent larger columns')
            bound = n*(n-1)+3*(n-1)+6*(z*(n-1)+3*(z-1))
            A.need(len(word) <= bound, 'constructive length bound')
            fixtures.append(dict(n=n, z=z, seed=seed, gates=len(word), bound=bound,
                                 endpoint_sha256=C.digest([raw, projected]), word_sha256=C.digest(word)))
    return dict(censuses=records, short_relations=A.short_relations(), parabolic_fibers=parabolic,
                larger_fixtures=fixtures, total_joint_states=sum(x['states'] for x in records),
                total_joint_edges=sum(x['edges'] for x in records),
                total_parabolic_matrices=sum(x['matrices'] for x in parabolic))


def compare(got, wanted, label):
    C.need(C.canonical(got) == C.canonical(wanted), 'certificate mismatch: '+label)


def run(work):
    pins = C.sources()
    C.need(not work.exists(), 'output directory already exists')
    work.mkdir(parents=True)
    math = mathematical_report()
    print('PASS_ALL_DIMENSION_CONSTRUCTOR states='+str(math['total_joint_states'])+
          ' parabolic_matrices='+str(math['total_parabolic_matrices']), flush=True)
    selected = selected_word.report(work)
    print(selected['status'], flush=True)
    result = dict(status='PASS_PROJECTED_CLEANUP_FIBERS', admitted=False, source_sha256=pins,
                  mathematics=math, selected_word=selected)
    compare(result, C.read(C.PACKAGE/'EXPECTED.json'), 'complete result')
    C.write(work/'RECEIPT.json', result)
    print(result['status']+' receipt_sha256='+C.digest(result), flush=True)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, help='New output directory; existing paths are preserved')
    args = ap.parse_args()
    if args.work:
        run(args.work.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='projected-cleanup-') as parent:
            run(Path(parent)/'replay')


if __name__ == '__main__':
    main()
