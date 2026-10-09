#!/usr/bin/env python3
"""Explicit immutable source and finite-input closure for the aligned-composition witness."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
NAMES=('aligned_composition_graph.py','aligned_composition_compiler.py','aligned_composition_engine.py',
       'aligned_composition_nodeops.py','aligned_composition_compose.py','verify_aligned_composition.py',
       'pin_aligned_composition_sources.py','split_pair_arithmetic.py','joint_dual_reclaim_compiler.py',
       'binary_frame_math.py','binary_frame_replay.py','binary_frame_profile_prepare.py','binary_frame_profiles.cpp',
       'audit_aligned_composition_completion.py','audit_aligned_composition_exchange.py','audit_aligned_composition_cycles.py',
       'audit_aligned_composition_retired.py','audit_aligned_composition_pending.py','audit_aligned_composition_three_cycles.py','audit_aligned_composition_pricing.py','audit_aligned_composition_lean.py')

def required_paths():
    names={'scripts/experiments/'+n for n in NAMES}
    names.update(('.gitattributes','Makefile','README.md','NOTICE','.github/workflows/verify.yml',
        'tests/test_aligned_composition.py','tests/test_aligned_composition_coordinates.py','tests/test_aligned_composition_order.py','tests/test_aligned_composition_partitions.py',
        'research/aligned-composition/README.md','research/aligned-composition/PROOF.md',
        'research/aligned-composition/parameters.json','research/aligned-composition/engine-provenance.json',
        'research/aligned-composition/discovery-selection.json','research/aligned-composition/word-bindings.json','research/aligned-composition/discovery-source-audit.json','research/aligned-composition/selected-discovery-clearance.json',
        'research/aligned-composition/reported-comparisons.json','certificates/aligned-composition-compiler.json'))
    for h in (23,25):
        names.update((f'research/aligned-composition/config-{h}.json',f'research/aligned-composition/parent-result-{h}.json',f'research/aligned-composition/scalar-{h}.json'))
        names.update(f'certificates/aligned-composition-{kind}-{h}.{ext}' for kind,ext in (('word','json.gz'),('profiles','json'),('transitions','json')))
    for prior in ('pr48','pr59-split-operation','pr65','pr67','pr68','pr69','pr70','pr71','pr74','pr78','pr79','pr82','pr84','pr88','pr74-aligned','indexed-r5','final-r10','aligned-r11'):
        path=Path('references/frame-compiler')/prior
        manifest=json.loads((ROOT/path/'SOURCE.json').read_text())
        names.add(str(path/'SOURCE.json'));names.update(str(path/name) for name in manifest['files'])
    names.update(str(p.relative_to(ROOT)) for p in (ROOT/'research/aligned-composition/lean').rglob('*') if p.is_file())
    names.update(('formal/lean/KappaCheck/AlignedFrameComposition.lean','formal/lean/KappaCheck.lean','formal/lean/AuditAll.lean','formal/lean/sources.py','formal/lean/SOURCES.md','scripts/check_lean_axioms.py','tests/test_lean_axiom_output.py'))
    return names

def run():
    manifest=dict(author='Chafik Boukhalfa with OpenAI Codex assistance',
        pr88_construction='3ffd9b1dc7ef2978fa1831fe3850cd4f534aea70',
        pr74_aligned_partition='428b5c167686b42a83f1abf7003c6d17aec561ea',
        pr78_coordinate_flags='1c1f1e4ee87a6895eaea622e1a33dcd4b0aa62cf',
        discovery_selection_sha256='43a762adf17b2338b2d7ec486fd6eb17d00d1d221e7f1e4041711cbce9964ea7',
        scope='Exact source and finite-input freeze; all original contributor archives remain immutable; derived arithmetic and validation receipts excluded.',
        files={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(required_paths())})
    (ROOT/'research/aligned-composition/SOURCE.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print('Pinned',len(manifest['files']),'sources and finite inputs')
if __name__=='__main__':run()
