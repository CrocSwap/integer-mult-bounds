#!/usr/bin/env python3
"""Explicit immutable source and finite-input closure for the indexed-cycle witness."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
NAMES=('indexed_cycle_graph.py','indexed_cycle_compiler.py','indexed_cycle_engine.py',
       'indexed_cycle_nodeops.py','indexed_cycle_compose.py','verify_indexed_cycle.py',
       'pin_indexed_cycle_sources.py','split_pair_arithmetic.py','joint_dual_reclaim_compiler.py',
       'binary_frame_math.py','binary_frame_replay.py','binary_frame_profile_prepare.py','binary_frame_profiles.cpp',
       'audit_indexed_cycle_completion.py','audit_indexed_cycle_exchange.py','audit_indexed_cycle_cycles.py',
       'audit_indexed_cycle_retired.py','audit_indexed_cycle_pending.py')

def required_paths():
    names={'scripts/experiments/'+n for n in NAMES}
    names.update(('.gitattributes','Makefile','README.md','NOTICE','.github/workflows/verify.yml',
        'tests/test_indexed_cycle.py','tests/test_indexed_cycle_coordinates.py',
        'research/indexed-cycle/README.md','research/indexed-cycle/PROOF.md',
        'research/indexed-cycle/parameters.json','research/indexed-cycle/engine-provenance.json',
        'research/indexed-cycle/discovery-selection.json','research/indexed-cycle/coordinate-search.py',
        'research/indexed-cycle/reported-comparisons.json','certificates/indexed-cycle-compiler.json'))
    for h in (23,25):
        names.update((f'research/indexed-cycle/config-{h}.json',f'research/indexed-cycle/parent-result-{h}.json'))
        names.update(f'certificates/indexed-cycle-{kind}-{h}.{ext}' for kind,ext in (('word','json.gz'),('profiles','json'),('transitions','json')))
    for prior in ('pr48','pr59-split-operation','pr65','pr67','pr68','pr69','pr70','pr71','pr74','pr78','pr79','indexed-r5'):
        path=Path('references/frame-compiler')/prior
        manifest=json.loads((ROOT/path/'SOURCE.json').read_text())
        names.add(str(path/'SOURCE.json'));names.update(str(path/name) for name in manifest['files'])
    return names

def run():
    manifest=dict(author='Chafik Boukhalfa with OpenAI Codex assistance',
        pr79_construction='9a58e62cf9e8954a4dde3c9b1372d733c276a6d1',
        pr74_node_order='3f78d8967c009153f2df5c6a6577b6ab1d37e2ca',
        pr78_coordinate_flags='1c1f1e4ee87a6895eaea622e1a33dcd4b0aa62cf',
        discovery_selection_sha256='7bfb5b01851f3f80cb1946bb691383d0861f9801043ceb866ed43c86b45bac8a',
        scope='Exact source and finite-input freeze; all original contributor archives remain immutable; derived arithmetic and validation receipts excluded.',
        files={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(required_paths())})
    (ROOT/'research/indexed-cycle/SOURCE.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print('Pinned',len(manifest['files']),'sources and finite inputs')
if __name__=='__main__':run()
