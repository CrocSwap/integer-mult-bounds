#!/usr/bin/env python3
"""Explicit immutable source and finite-input closure for the final-frame witness."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
NAMES=('final_frame_graph.py','final_frame_compiler.py','final_frame_engine.py',
       'final_frame_nodeops.py','final_frame_compose.py','verify_final_frame.py',
       'pin_final_frame_sources.py','split_pair_arithmetic.py','joint_dual_reclaim_compiler.py',
       'binary_frame_math.py','binary_frame_replay.py','binary_frame_profile_prepare.py','binary_frame_profiles.cpp',
       'audit_final_frame_completion.py','audit_final_frame_exchange.py','audit_final_frame_cycles.py',
       'audit_final_frame_retired.py','audit_final_frame_pending.py','audit_final_frame_three_cycles.py','audit_final_frame_pricing.py')

def required_paths():
    names={'scripts/experiments/'+n for n in NAMES}
    names.update(('.gitattributes','Makefile','README.md','NOTICE','.github/workflows/verify.yml',
        'tests/test_final_frame.py','tests/test_final_frame_coordinates.py','tests/test_final_frame_order.py',
        'research/final-frame/README.md','research/final-frame/PROOF.md',
        'research/final-frame/parameters.json','research/final-frame/engine-provenance.json',
        'research/final-frame/discovery-selection.json','research/final-frame/word-bindings.json','research/final-frame/discovery-source-audit.json','research/final-frame/selected-discovery-clearance.json',
        'research/final-frame/reported-comparisons.json','certificates/final-frame-compiler.json'))
    for h in (23,25):
        names.update((f'research/final-frame/config-{h}.json',f'research/final-frame/parent-result-{h}.json',f'research/final-frame/scalar-{h}.json'))
        names.update(f'certificates/final-frame-{kind}-{h}.{ext}' for kind,ext in (('word','json.gz'),('profiles','json'),('transitions','json')))
    for prior in ('pr48','pr59-split-operation','pr65','pr67','pr68','pr69','pr70','pr71','pr74','pr78','pr79','pr82','pr84','indexed-r5','final-r10'):
        path=Path('references/frame-compiler')/prior
        manifest=json.loads((ROOT/path/'SOURCE.json').read_text())
        names.add(str(path/'SOURCE.json'));names.update(str(path/name) for name in manifest['files'])
    return names

def run():
    manifest=dict(author='Chafik Boukhalfa with OpenAI Codex assistance',
        pr84_construction='88ca39571907343a49e97f328971ec7bcd26fbfd',
        pr74_node_order='3f78d8967c009153f2df5c6a6577b6ab1d37e2ca',
        pr78_coordinate_flags='1c1f1e4ee87a6895eaea622e1a33dcd4b0aa62cf',
        discovery_selection_sha256='c05715807ad48d2c292f6e3431c338c39d4e7ae80b9758a8c3f8ace520178e23',
        scope='Exact source and finite-input freeze; all original contributor archives remain immutable; derived arithmetic and validation receipts excluded.',
        files={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(required_paths())})
    (ROOT/'research/final-frame/SOURCE.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print('Pinned',len(manifest['files']),'sources and finite inputs')
if __name__=='__main__':run()
