"""Assertion-enabled replay of the pinned inherited native auditor."""
import contextlib
import copy
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import runpy
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def main(package, auditor, routing, out):
    require(__debug__, "the inherited auditor requires assertions; run without -O")
    audit = runpy.run_path(str(auditor))['run']
    expected = read(package/'NATIVE-EXPECTED.json')
    construction = read(package/'CONSTRUCTION-RECORD.json')
    core = read(package/'CODED-CELL.json')['core']
    words, receipts = {}, {}
    for name in sorted(expected):
        path = package/'words'/f'{name}.json.gz'
        words[name] = read(path)
        cell = construction[name]['coded_cell']
        bindings, indexes = cell['bindings'], cell['core_gate_indexes']
        require(len(indexes) == len(core) == 28 and indexes == sorted(set(indexes)),
                f"coded core index list: {name}")
        embedded = [['add', bindings[t], bindings[s], Q(q).numerator, Q(q).denominator]
                    for t, s, q in core]
        require([words[name]['B'][i][:-1] for i in indexes] == embedded,
                f"coded core embedding: {name}")
        with (out/f'{name}.log').open('w', encoding='utf-8') as log:
            with contextlib.redirect_stdout(log):
                audit(path, routing, out/name)
        receipt = read(out/name/'SCALAR-FRAME-AUDIT.json')
        receipt.pop('seconds')
        require(receipt == expected[name], f"native receipt mismatch: {name}")
        receipts[name] = receipt

    positive, negative = words['positive-ck'], words['negative-ck']
    provenance = construction['positive-ck']
    corrections = provenance['entry_correction']['gates']
    require(positive['B'][:len(corrections)] == corrections, "entry correction location")
    cleanup = provenance['full_frame_cleanup_correction']['gates']
    require(positive['cleanup'][-len(cleanup):] == cleanup, "cleanup correction location")
    cases = []
    bad = copy.deepcopy(positive)
    del bad['B'][:len(corrections)]
    cases.append(('omit_entry_correction', bad, 'zero-frame compensation reads an entering helper'))
    bad = copy.deepcopy(positive)
    del bad['cleanup'][-len(cleanup):]
    cases.append(('omit_full_cleanup_correction', bad, 'arbitrary-dirt endpoint'))
    bad = copy.deepcopy(positive)
    lift = provenance['cold_end_transfer']['end_lifts'][0]
    bad['helper_final'][str(lift['helper'])] = lift['old_frame']
    cases.append(('restore_old_cold_end', bad, 'hpe cone pre-check'))
    bad = copy.deepcopy(negative)
    gate = next(e for e in bad['cleanup'] if e[0] == 'add' and e[1] == 448 and e[3])
    gate[3] = 0
    cases.append(('omit_coded_helper_cleanup', bad, 'arbitrary-dirt endpoint'))
    bad = copy.deepcopy(positive)
    bad['report']['local_profile']['2'] -= 1
    cases.append(('understate_paid_profile', bad, 'paid local profile differs'))
    rejected = {}
    for name, bad, reason in cases:
        path = out/f'{name}.json'
        path.write_text(json.dumps(bad), encoding='utf-8')
        with (out/f'{name}.log').open('w', encoding='utf-8') as log:
            try:
                with contextlib.redirect_stdout(log):
                    audit(path, routing, out/name)
            except AssertionError as error:
                require(reason in str(error), f"wrong failure for {name}: {error}")
                rejected[name] = str(error)
            else:
                raise ValueError(f"negative control accepted: {name}")

    # Generated gzip identity is its entire decompressed payload, not its header.
    source = package/'words'/'positive-ck.json.gz'
    recompressed = out/'recompressed.json.gz'
    recompressed.write_bytes(gzip.compress(gzip.decompress(source.read_bytes()),
                                          compresslevel=1, mtime=123456789))
    require(recompressed.read_bytes() != source.read_bytes(), "recompression control unchanged")
    with (out/'recompressed.log').open('w', encoding='utf-8') as log:
        with contextlib.redirect_stdout(log):
            audit(recompressed, routing, out/'recompressed')
    receipt = read(out/'recompressed'/'SCALAR-FRAME-AUDIT.json')
    receipt.pop('seconds')
    require(receipt == receipts['positive-ck'], "recompression changed mathematical receipt")
    result = {'receipts': receipts, 'controls_rejected': rejected,
              'recompression_control': 'PASS', 'assertions_enabled': __debug__}
    (out/'NATIVE-RESULT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    require(len(sys.argv) == 5, "expected package, auditor, routing and output paths")
    main(*(Path(x).resolve() for x in sys.argv[1:]))
