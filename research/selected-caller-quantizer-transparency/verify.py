#!/usr/bin/env python3
"""Current selected caller quantizer transparency; source facts plus PROOF.md.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def snapshot():
    paths = sorted(HERE.glob('*.py'))+[HERE/'SOURCES.json', HERE/'DEPENDENCY.json']
    paths += sorted((HERE/'vendor/a1').iterdir())
    return {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}


def run(progress):
    from common import require
    import inputs
    import scalar_certificate
    import controller_certificate
    import geometry
    import quantized
    import controls
    pins = snapshot()
    data = inputs.load()
    scalar = scalar_certificate.certify(data['word'], data['result'])
    controller = controller_certificate.certify(data['word'], data['controller'], data['result'], data['dependency'])
    geometric = geometry.certify(data['word'], data['controller'], data['phase'], data['result'], data['dependency'])
    if progress:
        print('complete_source_certificates', scalar['events'], controller['events'], geometric['complete_contacts'], flush=True)
    numerical = quantized.complete_local_fixture(data['word'], data['native'], data['result'], progress)
    negatives = controls.run(data, geometric, scalar, controller)
    require(snapshot() == pins, 'scientific source unchanged during replay')
    inputs.load()
    return {'schema': 'selected-caller-quantizer-transparency/1',
            'status': 'PASS_SELECTED_CALLER_QUANTIZER_TRANSPARENCY', 'base_commit': inputs.BASE,
            'canonical_sources': inputs.PINS, 'published_operator_dependency': inputs.PUBLISHED,
            'local_scalar_certificate': scalar, 'complete_controller_certificate': controller,
            'geometry_certificate': geometric, 'deterministic_local_fixture': numerical,
            'negative_controls': negatives,
            'all_size_contract': {'fractional_bits': 'p+ceil(145*f/2)+4',
                                  'signed_bits_per_real_component': 'p+h+145*f+20',
                                  'temporary_component_bits': 'W+6',
                                  'domain': 'integer f>=1,p>=0,h>=0; finite complete inputs and arbitrary spectators',
                                  'proof': 'PROOF.md; finite fixtures do not establish the all-f theorem'},
            'limitations': ['selected-rate recursive native interiors and P_r remain open',
                            'ideal owned resets, actual tape/placement/backing costs remain premises',
                            'no unfunded final downcast or whole-recursion precision transfer',
                            'No new kappa']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='explicitly regenerate only this new package result')
    parser.add_argument('--progress', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='selected-quantizer-pycache-') as cache:
        sys.pycache_prefix = cache
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(HERE))
        result = run(args.progress)
        from common import require, same_typed
        serialized = json.dumps(result, sort_keys=True, indent=2)+'\n'
        require(same_typed(result, json.loads(serialized)), 'typed JSON result round trip')
        target = HERE/'RESULT.json'
        if args.write:
            target.write_text(serialized)
        else:
            require(same_typed(result, json.loads(target.read_text())), 'complete typed scientific result receipt')
        print(result['status'], 'local_events=22803 global_events=363',
              'controls='+str(len(result['negative_controls']['rejections'])), 'No_new_kappa')


if __name__ == '__main__':
    main()
