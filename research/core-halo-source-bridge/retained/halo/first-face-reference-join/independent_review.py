"""Independent global-grid review of the streamed B/C codec.

External test fixture/oracle only; no production payload regrouping is used.
Prepared for @CubeJerry with separate source-aware OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from math import prod
from pathlib import Path
import sys
from time import perf_counter

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


O = load('independent_join_full_grid_oracle', ROOT / 'full_grid_oracle.py')
encoded, expected_after_core, full_grid, need = O.encoded, O.expected_after_core, O.full_grid, O.need
J = load('independent_join_under_review', ROOT / 'join.py')
B, M, T = J.B, J.M, J.T


def synthetic_matrix(n, axis):
    holes = {4, 11, n - 10}
    rows = [[Q(0) for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for offset, value in (
            (-1, Q(1 if (r + axis) % 2 else -1, 10)),
            (0, Q((r + axis) % 3 - 1, 16)),
            (1, Q(-1 if (r + axis) % 3 else 1, 11)),
        ):
            c = (r + offset) % n
            if r not in holes and c not in holes:
                rows[r][c] = value
    need(rows[0][n - 1] and rows[n - 1][0], 'genuine wrap interaction')
    return tuple(tuple(row) for row in rows)


def original_words(size, bits):
    unit = 2 ** max(0, bits - 9)
    return tuple((((17 * r + 3) % 201 - 100) * unit,
                  ((29 * r + 7) % 151 - 75) * unit) for r in range(size))


def forbidden(*args, **kwargs):
    raise RuntimeError('production used forbidden diagnostic or allocated a new tape')


def fixture(ell, ks, spectator_width, boundary, halo, terms, *, fault=None):
    start = perf_counter()
    plans = tuple(M.Plan(2 ** (ell + k), 1, 9, j, 1, Q(1, 2), 1)
                  for k, j in zip(ks, terms))
    need(len(plans) == len(ks), 'complete plan fixture')
    matrices = tuple(synthetic_matrix(p.period, axis) for axis, p in enumerate(plans))
    size = (2 ** spectator_width) * prod(p.period for p in plans)
    words = original_words(size, plans[0].bits)
    if fault == 'negative_zero':
        words = ((0, words[0][1]),) + words[1:]
    expected, target_count = expected_after_core(matrices, plans, words, ell, boundary, 2 ** spectator_width)
    source = ''.join(encoded(pair, plans[0].data_width) + '#' for pair in words)
    if fault == 'negative_zero':
        source = '1' + source[1:]
    coordinate_tape = '0' * spectator_width + '&' + ''.join('@' + '0' * k + '#' + '0' * ell + ';' for k in ks)
    width = ell + 2
    transport = B.Program(source, coordinate_tape,
                          format(2 ** ell, '0' + str(width) + 'b'),
                          format(boundary, '0' + str(width) + 'b'),
                          format(halo, '0' + str(width) + 'b'))
    transport.gather(); transport.sort(transport.saved)
    shape = J.Shape(ell, ks, spectator_width, boundary, halo, 2 * plans[0].data_width)
    if fault == 'source_suffix':
        B.home(transport.saved)
        for _ in range(shape.prefix_width + shape.g * (ell + 2) + shape.coordinate_width - 1):
            transport.saved.move(1)
        bit = transport.saved.read()
        need(bit in '01', 'source suffix mutation site')
        transport.saved.write('1' if bit == '0' else '0')
        B.home(transport.saved)
    saved_before = transport.saved.inspect()
    transport.core_complement_test_double()
    need(transport.source.inspect() == ''.join('#' if x == '#' else ('1' if x == '0' else '0') for x in source), 'core really destroyed original payloads')
    bill = M.Bill()
    old_tables = []
    def tables():
        for axis, plan in enumerate(plans):
            table, _ = M.prepare_table(plan, lambda r, c, axis=axis: matrices[axis][r][c], 'independent synthetic axis ' + str(axis), bill)
            old_tables.append(table)
            yield table
    archive = T.pack_tables(tables(), bill)
    archive_before = archive.tape.snapshot()
    pool = T.TensorWorkspace.create(bill)
    ids_before = tuple(map(id, pool.roles))
    codec = J.Codec(transport, shape, archive, pool, bill)
    old = B.Tape.__init__, B.Tape.inspect, M.Tape.__init__, M.Tape.snapshot
    B.Tape.__init__ = B.Tape.inspect = M.Tape.__init__ = M.Tape.snapshot = forbidden
    try:
        codec.run()
        need(old[1](transport.saved) == saved_before, 'saved payloads and keys preserved by codec')
        transport.merge_returns()
        transport.erase_work()
    finally:
        B.Tape.__init__, B.Tape.inspect, M.Tape.__init__, M.Tape.snapshot = old
    need(transport.final.inspect() == expected, 'whole-grid rounded oracle differs')
    need(codec.returned_records == target_count, 'boundary target cardinality')
    need(codec.rectangles == (2 ** (spectator_width + sum(ks))) * 2 * len(ks), 'all first-face rectangles consumed exactly once')
    need(tuple(map(id, pool.roles)) == ids_before, 'fixed pool identity')
    need(all(t.head == 0 and t.live_bits == 0 and not t.readonly and not any(t.snapshot()) for t in pool.roles), 'all eight local roles erased at origin')
    need(archive.tape.head == 0 and archive.tape.readonly and archive.tape.snapshot() == archive_before, 'archive preserved at origin')
    need(all(t.tape.head == 0 and t.tape.live_bits == 0 and not any(t.tape.snapshot()) for t in old_tables), 'prepared table erasure')
    need(all(t is transport.final or t.inspect() == '' for t in transport.roles), 'all nonoutput transport roles erased')
    archive.tape.readonly = False; archive.tape.clear()
    need(not any(archive.tape.snapshot()), 'archive erasure')
    receipt = codec.receipt()
    receipt.update(periods=[p.period for p in plans], terms=list(terms), halo=halo,
                   consumer_halos=[p.halo for p in plans], spectator_width=spectator_width,
                   source_records=size, checked_returned_bits=target_count * shape.payload_width,
                   exact_full_grid_match=True, constructors_and_observers_disabled=True,
                   consumer_bit_actions=bill.reads + bill.writes + bill.moves,
                   transport_finite_alphabet_actions=sum(t.actions[k] for t in transport.roles for k in ('read', 'write', 'move')),
                   seconds=round(perf_counter() - start, 3))
    return receipt


def actual_reference():
    oracle = load('independent_source_fixture', ROOT / 'oracle.py')
    _, raw, h, gap, source_receipt = oracle.source_fixture()
    matrix = tuple(tuple(Q(int(r == c)) - h[r][c] for c in range(64)) for r in range(64))
    words = oracle.fixture_words(64, 28)
    actual, plan, receipt = J.execute(raw, gap, words)
    expected = full_grid((matrix,), (plan,), words)
    need(all(actual[row] == expected[row] for row in actual), 'actual reference exact full-grid rounding mismatch')
    need(set(actual) == {r for r in range(64) if r % 32 < 5 or r % 32 >= 27}, 'actual target set')
    holes = source_receipt['identity_holes']
    need(holes and source_receipt['periodic_nonzero_coordinates'], 'actual holes and wrap')
    return dict(actual_reference=True, checked_targets=len(actual), holes=holes,
                periodic_nonzeros=len(source_receipt['periodic_nonzero_coordinates']),
                exact_full_grid_match=True, codec=receipt['codec'])


def main():
    cases = []
    for parameters in ((4, (1,), 1, 2, 1, (2,)),
                       (4, (1, 1), 0, 2, 1, (2, 1)),
                       (4, (1, 1), 0, 3, 2, (2, 3))):
        result = fixture(*parameters)
        cases.append(result)
        print(json.dumps(result, sort_keys=True), flush=True)
    controls = []
    for fault, message in (('negative_zero', 'noncanonical negative zero'),
                           ('source_suffix', 'canonical source suffix binds saved offset')):
        try:
            fixture(4, (1,), 0, 2, 1, (2,), fault=fault)
        except ValueError as e:
            need(str(e) == message, 'wrong control failure: ' + str(e))
            controls.append(fault)
        else:
            raise ValueError('mutation escaped: ' + fault)
    actual = actual_reference()
    print(json.dumps(actual, sort_keys=True), flush=True)
    print('PASS_INDEPENDENT_JOIN_FULL_GRID')
    print(json.dumps(dict(cases=len(cases), controls=controls,
                         files={str(path.relative_to(ROOT.parent)): sha256(path.read_bytes()).hexdigest()
                                for path in (ROOT / 'join.py', ROOT.parent / 'shrinking-reference-halo/engine.py',
                                             ROOT.parent / 'shrinking-reference-halo/tensor.py',
                                             ROOT.parent / 'sparse-halo-tape-transaction/tapes.py')}), sort_keys=True))


if __name__ == '__main__':
    main()
