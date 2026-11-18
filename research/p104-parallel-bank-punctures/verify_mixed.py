"""Replay the signed caller and reconstruct its chronological instruction stream. Apache-2.0."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mixed_application import verify_caller, verify_expansion
from mixed_caller import instructions, layout_bindings, place_roots, split_templates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent,
                        help='P104 package that contains common.py, data and vendor')
    parser.add_argument('--stages', type=int, default=1024)
    parser.add_argument('--full-readback', action='store_true',
                        help='also read every emitted instruction at the requested batch size')
    parser.add_argument('--write-json', type=Path, help='write the detailed caller receipt')
    parser.add_argument('--emit', type=Path, help='write the complete program as JSON lines')
    args = parser.parse_args()
    sys.path.insert(0, str(args.package.resolve()))
    from common import inputs, read
    from caller16 import signed_caller
    _, layout, *_ = inputs()
    caller = read('data/CALLER.json.gz')
    legacy = signed_caller(caller, layout, 2025, 9)
    census, envelope, proof = verify_caller(caller, layout, args.stages, legacy,
                                            read('data/CALLER-PHASE-BASES.json'))
    expansion = verify_expansion(caller, layout, args.stages if args.full_readback else 32)
    if args.emit:
        words, roots = split_templates(caller), place_roots(caller, args.stages)
        bindings, offsets, _ = layout_bindings(words, roots, layout, args.stages)
        with args.emit.open('w', encoding='utf8') as stream:
            for event in instructions(words, roots, bindings, offsets):
                stream.write(json.dumps(event, separators=(',', ':')) + '\n')
    if args.write_json:
        receipt = dict(signed=census, envelope=envelope, proof=proof, expansion=expansion)
        args.write_json.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n', encoding='utf8')
    print('PASS_MIXED_CALLER', args.stages, census['root_owners'],
          proof['occurrence_weighted_component_divisions'], expansion['event_stream_sha256'])


if __name__ == '__main__':
    main()
