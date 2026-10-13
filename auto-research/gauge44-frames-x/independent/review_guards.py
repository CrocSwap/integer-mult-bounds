"""Reproduce the assertion-preservation part of the independent guard review.

This compares complete assertion ASTs in their traversal order. It supplements
the semantic centre-interface argument in CENTRE-GUARD-REVIEW.md.
Prepared for icekylinx with OpenAI GPT-6 Astra assistance. Apache-2.0.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pr635', type=Path, required=True, help='Pinned PR635 checkout or supplier directory')
    parser.add_argument('--delta', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    old = args.pr635
    if not (old/'code/assemble.py').exists():
        old = old/'research/complex-571-cold14-st2'
    names = ['assemble.py', 'invoice_allcold.py', 'bind_providers_portable.py',
             'generated_identity.py', 'witness.py']
    records = []
    for name in names:
        a, b = (old/'code'/name).read_bytes(), (args.delta/'code'/name).read_bytes()
        assertions = lambda data: [ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(data))
                                   if isinstance(n, ast.Assert)]
        aa, bb = assertions(a), assertions(b)
        if aa != bb:
            raise RuntimeError('Assertion sequence changed: '+name)
        records.append(dict(file='code/'+name, baseline_sha256=hashlib.sha256(a).hexdigest(),
                            new_sha256=hashlib.sha256(b).hexdigest(), byte_identical=a == b,
                            assert_count=len(aa), all_assertions_identical_in_order=True))
    if records[0]['assert_count'] != 91:
        raise RuntimeError('The expected PR635 assembly has 91 assertions')
    result = dict(status='PASS_PR635_ADMISSION_ASSERTION_PRESERVATION', files=records,
                  centre_interface_review='CENTRE-GUARD-REVIEW.md',
                  scope='Exact syntax preservation for all admission assertions in these five files. The changed emitter/controller centre boundary and single-provider controls require the separate semantic review; assertion counts alone do not prove them.')
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], [r['assert_count'] for r in records])


if __name__ == '__main__':
    main()
