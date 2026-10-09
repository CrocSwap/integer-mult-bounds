#!/usr/bin/env python3
"""Regenerate the complex source-aligned increment from pinned source.

GPT-6 Astra, for icekylinx, 2026-10-09. The frozen source producer is
PR168 fd25adb7fbaa12ee761d02c733c54d1d2a7687ee. Its own source notices and
exact source-pin checks are retained. This driver does not fetch a repo.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PIN = 'fd25adb7fbaa12ee761d02c733c54d1d2a7687ee'


def read(p):
    return json.loads(p.read_text())


def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data,separators=(',',':'))+'\n')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(name, *args):
    subprocess.run([sys.executable,str(HERE/name),*map(str,args)],check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,default=ROOT/'public/pr168_fd25adb7')
    ap.add_argument('--work',type=Path,default=ROOT/'shared/complex_reproduction')
    ap.add_argument('--base-cache',type=Path,help='Optional already regenerated pinned graph/frames/selection cache.')
    a = ap.parse_args()
    if sys.flags.optimize:
        raise ValueError('Assertions are part of the finite certificate; do not use -O.')
    source,work = a.source.resolve(),a.work.resolve()
    if (source/'.git').exists():
        head = subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
        assert head == PIN, ('Use the pinned source commit',head,PIN)
    base = a.base_cache.resolve() if a.base_cache else work/'pinned_base_cache'
    if not a.base_cache:
        sys.path.insert(0,str(source/'scripts'))
        from paired_cube_physical import regenerated_word
        g,w,word,record = regenerated_word()
        for name,value in zip(('graph.json','frames.json','selection.json','record.json'),(g,w,word,record)):
            write(base/name,value)
    aligned = work/'aligned_parity'
    run('source_aligned_local.py','--tree',source,'--cache',base,'--out',aligned,
        '--pairs',HERE/'complex_source_aligned_physical_pairs.json')
    profile = work/'aligned_parity_purified_flow.result.json'
    witness = profile.with_suffix('.witness.json')
    run('complex_frame_flow.py','--tree',aligned,'--cache',aligned/'cache','--out',profile,
        '--witness','--purify-source-donors','--recycle-kernels',
        '--kernel-pairs',HERE/'complex_source_aligned_kernel_pairs.json')
    expected = read(HERE/'complex_source_aligned_profile.json')
    actual = read(profile)
    assert actual['local_histogram'] == expected['local_histogram']
    assert actual['child_histogram'] == expected['child_histogram']
    assert actual['new_R'] == expected['physical_R']
    assert actual['new_W'] == expected['W_per_vertex']
    assert actual['deficit'] == expected['deficit_per_vertex']
    # The large source caches are intentionally omitted from the handoff.
    # The compact flow witness is included; its exact checksum binds all
    # node, edge, read, erasure and chosen reuse-coordinate records.
    assert sha(witness) == sha(HERE/'aligned_parity_purified_flow.result.witness.json')
    lift = work/'aligned_parity_exact_lift.result.json'
    run('exact_complex_flow_lift.py','--witness',witness,'--profile',profile,'--out',lift)
    exact = read(lift)
    assert exact['exact_scalar_program_sha256'] == expected['exact_scalar_program_sha256']
    normalized = work/'complex_source_aligned_profile.json'
    run('certify_complex_flow_contract.py','--tree',aligned,'--cache',aligned/'cache',
        '--witness',witness,'--flow-profile',profile,'--lift-profile',lift,'--out',normalized)
    final = read(normalized)
    for key in ('local_histogram','source_data_histogram','target_data_histogram','child_histogram',
                'physical_R','W_per_vertex','deficit_per_vertex','contract_checks','scalar_coefficients'):
        assert final[key] == expected[key],key
    print(json.dumps(dict(status='PASS exact complex increment regeneration',source_commit=PIN,
                          profile=str(normalized),physical_R=final['physical_R'],
                          deficit=final['deficit_per_vertex'],
                          exact_scalar_program_sha256=final['exact_scalar_program_sha256']),indent=2))


if __name__=='__main__':
    main()
