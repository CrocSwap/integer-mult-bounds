"""Assertion-enabled construction and independent inherited native replay."""
from pathlib import Path
from collections import Counter
import contextlib
import gzip
import json
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from construct import construct, encode, read, require

BASE = ROOT / 'research/complex-k492-owner-repair'
ROUTING = BASE / 'vendor/multicold/vendor/pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'


def main(out):
    require(__debug__, 'Native auditor requires enabled assertions')
    auditor = ROOT / 'research/complex-sw4-frame8/local/hpe_audit_and_transport.py'
    audit = runpy.run_path(str(auditor))['run']
    receipts, constructions = {}, {}
    for name in ('positive-ck', 'positive-jp8', 'negative-ck', 'negative-jp8'):
        source = HERE / 'vendor/pr855/words' / (name + '.json.gz')
        word, proof = construct(source)
        path = out / (name + '.json.gz')
        def save():
            path.write_bytes(gzip.compress(encode(word), mtime=0))
        save()
        # A discovery run may fail only at the expected old-profile guard.
        # Every scalar, endpoint, frame and cone guard before it must pass.
        try:
            with (out / (name + '-discovery.log')).open('w', encoding='utf-8') as log, contextlib.redirect_stdout(log):
                audit(path, ROUTING, out / (name + '-discovery'))
        except AssertionError as error:
            require(str(error) == 'paid local profile differs from the reported local_profile',
                    'Construction rejected before profile discovery: ' + str(error))
            tb = error.__traceback__
            while tb.tb_next:
                tb = tb.tb_next
            paid = tb.tb_frame.f_locals['paid']
            word['report']['local_profile'] = {str(r): n for r, n in sorted(paid.items())}
            word['report']['local_rank_mass'] = sum(r*n for r, n in paid.items())
        else:
            raise ValueError('Retimed construction unexpectedly retained old profile')
        inventory = word['report']['width_inventory']
        require(inventory['9'] > 0, 'Original coded helper width')
        inventory['9'] -= 1
        inventory['8'] = inventory.get('8', 0) + 1
        save()
        with (out / (name + '.log')).open('w', encoding='utf-8') as log, contextlib.redirect_stdout(log):
            audit(path, ROUTING, out / name)
        receipt = read(out / name / 'SCALAR-FRAME-AUDIT.json')
        receipt.pop('seconds')
        require(Counter(receipt['widths']) == Counter({int(r): n for r, n in inventory.items()}), 'Audited width inventory')
        require(receipt['local_rank_mass'] == word['report']['local_rank_mass'], 'Audited rank mass')
        require(448 in receipt['cold_hyperplane_ended_helpers'], 'Missing cold endpoint')
        receipts[name] = receipt
        constructions[name] = proof
        print('PASS_NATIVE_EARLY8', name, flush=True)
    result = dict(receipts=receipts, constructions=constructions, assertions_enabled=__debug__)
    (out / 'NATIVE-RESULT.json').write_bytes((json.dumps(result, indent=2) + '\n').encode())


if __name__ == '__main__':
    out = Path(sys.argv[1]).resolve()
    require(out.is_dir(), 'Prepared output directory required')
    main(out)
