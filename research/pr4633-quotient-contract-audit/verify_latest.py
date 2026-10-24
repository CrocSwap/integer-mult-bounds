#!/usr/bin/env python3
"""Audit the b390d64abfc delta using independent quotient cosets. Apache-2.0."""
from collections import Counter
from copy import deepcopy
import gzip
import importlib.util
import json
import struct
import verify as audit

HERE = audit.HERE
VENDOR = HERE/'sources-current/research/bit-ambient-quotient'


def span(basis):
    out = {0}
    for x in basis:
        out |= {x ^ y for y in tuple(out)}
    return frozenset(out)


def main():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            audit.need(audit.sha256((audit.ROOT/row['path']).read_bytes()).hexdigest()
                       == row['sha256'], 'Live source pin: '+row['path'])
    a = json.loads(gzip.decompress((VENDOR/'QUOTIENT-BIT-WORD.json.gz').read_bytes()))
    w = json.loads(gzip.decompress((audit.SOURCE/'WORD.json.gz').read_bytes()))
    frames = json.loads((audit.SOURCE/'records/frames.json').read_text())['frames']
    kernel = span([150, 102, 255])
    audit.need(len(kernel) == 8 and a['kernel_basis'] == [150, 102, 255], 'Three-dimensional kernel')
    table, image = {}, {}
    for k, f in frames.items():
        # Cosets are independent of the author's annihilator-basis algorithm.
        key = frozenset(min(x ^ y for y in kernel) for x in audit.nullspace_mod2(f['A']))
        if key not in table:
            table[key] = len(table)
        image[int(k)] = table[key]
    full = image[1]
    table[frozenset(range(256))] = len(table)
    padded = len(table)-1
    image = {k: padded if i == full else i for k, i in image.items()}
    dims = {i: len(s).bit_length()-1 for s, i in table.items()}
    audit.need({str(k): v for k, v in dims.items()} == a['frame_dims'], 'Independent coset dimensions')
    for boundary in ('start', 'final'):
        audit.need([image[x] for x in w[boundary]] == a[boundary], 'Independent '+boundary)
    actual = {i: span(b) for i, b in enumerate(a['frame_bases'])}
    audit.need(all(len(s) == 2**dims[i] for i, s in actual.items()), 'Declared bases have promised ranks')
    records = list(struct.iter_unpack('<6i', (audit.SOURCE/'records/249-records.bin').read_bytes()))
    rewritten = []
    for op, x, y, c, f, z in records:
        if op == 0:
            old, new = image[y], image[c]
            audit.need(actual[old] <= actual[new], 'Current binary containment control')
            rewritten.append([op, x, old, new, dims[new]-dims[old], z])
        elif op == 1:
            rewritten.append([op, x, y, c, image[f], z])
        else:
            rewritten.append([op, x, y, image[c], image[f], z])
    audit.need(rewritten == a['records'], 'Every current rewritten record')
    lost = [i for i in range(111) if dims[a['start'][i]] == 0]
    erased_rank = audit.rank_q([w['lines'][i] for i in lost])
    audit.need(len(lost) == 41 and erased_rank == 8, 'A rank-three rational kernel cannot erase rank eight')
    pairs = Counter((dims[a['final'][i]]-dims[a['start'][i]],
                     dims[a['final'][111+i]]-dims[a['start'][111+i]]) for i in range(111))
    audit.need(pairs == {(7, 8): 8, (8, 4): 41, (7, 4): 62}, 'All retained main ports still fail')
    spec = importlib.util.spec_from_file_location('current_author_verifier', VENDOR/'verify.py')
    author = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(author)
    author.SOURCE = audit.SOURCE
    positive = audit.run_author(author, a)
    audit.need(positive['quotient_paid_mass'] == 4842 and
               abs(positive['quotient_kappa']-.032249423394893) < 1e-12, 'Current positive control')
    mutant = deepcopy(a)
    changed = 0
    for record in mutant['records']:
        if record[0] == 0 and record[4] > 0:
            record[4] = 0
            changed += 1
    bad = audit.run_author(author, mutant)
    audit.need(changed == 2184 and bad['quotient_kappa'] == .25, 'Current free-MOVE false acceptance')
    geometry = deepcopy(a)
    geometry['frame_bases'] = [[] for _ in geometry['frame_bases']]
    no_geometry = audit.run_author(author, geometry)
    audit.need(no_geometry == positive, 'Current verifier ignores frame bases')
    result = dict(status='PASS_PR4633_LATEST_AUDIT_COUNTEREXAMPLES',
                  reviewed_head='b390d64abfcdba1a3816b86fc763cbc95d43c12c',
                  quotient_reconstructed_by_cosets=True, erased_rational_ports=lost,
                  erased_rational_span_rank=erased_rank,
                  port_transport_width_pairs={str(k): v for k, v in pairs.items()},
                  positive_control=positive,
                  free_move_mutation=dict(changed_records=changed, author_accepts=True,
                                          reported_kappa=bad['quotient_kappa']),
                  all_empty_frame_bases_accepted=True,
                  scope='Counterexamples survive the three-dimensional update; no supplier or kappa claim.')
    if (HERE/'EXPECTED-LATEST.json').exists():
        audit.need(result == json.loads((HERE/'EXPECTED-LATEST.json').read_text()), 'Current exact receipt')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
