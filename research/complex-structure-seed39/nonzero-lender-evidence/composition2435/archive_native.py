#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Archive a completed changed-word native replay with exact source/output pins."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
EXPECTED = [tag+'-'+stage for tag in ('base','extra') for stage in
            ('transport','emit','independent','wrappers','phases','recipes','orientations')] + ['lemmag']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if not __debug__:
        raise RuntimeError('Assertions required')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--native',type=Path,required=True)
    a=ap.parse_args(); native=a.native.resolve()
    steps=json.loads((native/'STEPS.json').read_text())
    assert [s['step'] for s in steps]==EXPECTED and all(s['exit_code']==0 for s in steps)
    for s in steps:
        assert (native/s['log']).is_file()
    for tag in ('base','extra'):
        assert gzip.decompress((native/tag/'FULL-WORD.json.gz').read_bytes()) == gzip.decompress((HERE/'interface'/('COMPOSED-'+tag+'.json.gz')).read_bytes())
        rec=json.loads((native/tag/'INDEPENDENT-LOCAL-REPLAY.json').read_text())
        assert rec['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
        assert rec['canonical_word_sha256']==sha(native/tag/'CANONICAL-WORD.json.gz')
        assert rec['local_programs_sha256']==sha(native/tag/'LOCAL-PROGRAMS.json.gz')
        for orientation in ('forward','backward'):
            assert rec['local'][orientation]['all_exact_columns']==652
            assert rec['local'][orientation]['zero_buffers_returned_to_zero']==76
            assert rec['local'][orientation]['private_work_erased']
    archive=HERE/'native-evidence'
    if archive.exists():
        assert {str(p.relative_to(archive)):sha(p) for p in archive.rglob('*') if p.is_file()} == {str(p.relative_to(native)):sha(p) for p in native.rglob('*') if p.is_file()}, 'existing archive differs'
    else:
        shutil.copytree(native,archive)
    original=HERE.parent.parent/'anticipatory-stage-evidence/interface/pr2269'
    sources=[HERE/'replay_native.py',HERE/'orientation_composed.py',HERE.parent/'transport_lifted.py',
             HERE/'interface/check_composition.py',HERE/'interface/COMPOSED-base.json.gz',
             HERE/'interface/COMPOSED-extra.json.gz',original/'FETCH.json',original.parent/'lemmag_stage.py',original/'lemmag_checks.py']
    sources += [original/n for n in ('bw_emit.py','bw_audit_local.py','bw_adapters.py','bw_phases.py','bw_check_recipes.py')]
    result=dict(status='PASS_FINITE_NATIVE_COMPOSED_FOUR428_ENTRANCE24_NO_GLOBAL_ADMISSION',
                base_commit='7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261',seed=39,
                source_pr2435_head='324d7d3590dc21003940a44cb0cbdc32b3620f25',
                attribution='Tekalign (@tekuuu), with substantial OpenAI Codex assistance; PR2435 entrance24 by Jeremy Kothe, FOUR428 aliases and inherited source notices retained.',
                steps=steps,stage_names=EXPECTED,
                input_sha256={str(p.relative_to(HERE.parent.parent)):sha(p) for p in sources},
                outputs_sha256={str(p.relative_to(archive)):sha(p) for p in archive.rglob('*') if p.is_file()},
                scope='Fresh full native replay on both changed words, all652 arbitrary columns, both orientations, exact phases and wrappers, explicit recipes and Lemma G. No global owner admission, outer kappa, or formal all-size theorem is asserted by this receipt.')
    (HERE/'NATIVE-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])

if __name__=='__main__':
    main()
