"""Independent audit of the proposed selected-bit matching extension.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
This finite counterfactual is not a whole-job or kappa certificate.
"""
from hashlib import sha256
from itertools import product
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'sources/grouped_route-before-overlap-audit.py'


def main():
    before = SOURCE.read_bytes()
    spec = importlib.util.spec_from_file_location('audit_grouped_controls', SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    K, G = 6, 2
    B = 1 << G
    good = [a + B*b for a, b in product(range(B-1), repeat=2)]
    count = 0
    failure = None
    for y, u, t, b in product(range(32, 48), good, good, [0, 1, 15]):
        # The two guard ranges are individually good, but overlap.
        assert all(8 <= ((y >> (p+1)) & 31) <= 23 for p in [0, 1])
        expected = y ^ (((y >> 2) & 1) << 0) ^ (((y >> 3) & 1) << 1)
        out, invoice = module.paired_control_word((u, t, y, b), [0, 1], [2, 3], K, G)
        count += 1
        if out != (u, t, expected, b):
            failure = dict(input=[u, t, y, b], expected=[u, t, expected, b],
                           actual=list(out), invoice=invoice)
            break
    assert SOURCE.read_bytes() == before, 'Source changed during audit'
    result = dict(status='OVERLAPPING_TARGET_WINDOW_COUNTERFACTUAL',
                  tested=count, counterexample=failure,
                  source_sha256=sha256(before).hexdigest(),
                  script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Individual good guards do not grant disjoint target windows. '
                        'Any arbitrary-matching extension must schedule nonoverlapping '
                        'guard windows or supply a stronger proof. No kappa claim.')
    (HERE/'ROUTE-OVERLAP.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n',
                                        encoding='utf-8', newline='\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
