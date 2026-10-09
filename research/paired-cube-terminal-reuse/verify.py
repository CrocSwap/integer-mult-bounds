#!/usr/bin/env python3
"""Rebuild both words and certify terminal accumulation plus bit lifetime reuse.

Standard-library Python, without -O. No search and no network access.
Prepared by huxint with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(ROOT/'scripts'))
import bit
import bit_merge
import formal_bit
import parameters
import prime_frames
import terminal
from paired_cube_physical import regenerated_word,physical
from structured_bulk_assembly import js


def require(ok,message):
    if not ok:raise ValueError(message)


def sources():
    paths=list(HERE.glob('*.py'))+list(HERE.glob('*.md'))+[HERE/'NOTICE']
    for directory in ('selected','references'):
        paths.extend(p for p in (HERE/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for directory in ('scripts/paired_cube','references/paired-cube',
                      'references/three-stage-cover/pr117','research/paired-cube-bit/data'):
        paths.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    # Imported network modules also bind historical scalar/interval helpers.
    # Pin their complete top-level Python closure, even when a helper is not
    # called by this selected assembly.
    paths.extend((ROOT/'scripts').glob('*.py'))
    paths.extend(ROOT/p for p in (
        'scripts/paired_cube_producer.py','scripts/paired_cube_physical.py','scripts/paired_cube_network.py',
        'scripts/paired_cube_assembly.py','scripts/three_stage_cover_network.py',
        'scripts/structured_bulk_assembly.py','scripts/audit_community_candidate.py','scripts/certify.py',
        'certificates/paired-cube-complex-input.json','certificates/copied-centers-network.json',
        'research/paired-cube-bit/paired_cube_bit_word.py','research/paired-cube-bit/check_paired_cube_bit.py',
        'research/paired-cube-bit/LEMMA.md','research/paired-cube-bit-descent-168/word.py',
        'research/paired-cube-bit-descent-168/prime_witnesses.py',
        'notes/general-clifford-frames.tex','notes/paired-cube-sharing.tex',
        'notes/paired-cube-construction.tex','notes/paired-cube-assembly.tex',
        'notes/three-stage-cover-bit.tex','notes/three-stage-cover-rows.tex'))
    return {str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}


def manifest():
    return dict(base_pr=169,base_commit='4895ba1104cedc7908b6d6ba64fdd6290e0ed7ae',
                scalar_word_pr=168,scalar_word_commit='98c115b53742b6613ad630de4d493f37b0119da7',
                terminal_lemma_pr=166,terminal_source_commit='4dbc2af5f223a0fbf22542c9d6c3f71442b6a3a6',
                formal_adapter_pr=171,formal_source_commit='89d0c75f8bf97131db21bc610e7546b699afcb9a',
                prior_bit_composition_pr=170,source_sha256=sources(),
                assistance='Prepared by huxint with substantial OpenAI Codex assistance.')


def verify():
    require(not sys.flags.optimize,'Run without -O')
    require(json.loads((HERE/'SOURCE.json').read_text())==manifest(),'Construction/proof source pins differ')
    print('Rebuilding signed complex word, full intersections and scalar decoder...',flush=True)
    g,witness,word,row=regenerated_word()
    frames=json.loads((HERE/'selected/complex/frames.json').read_text())['frames']
    pairs=json.loads((HERE/'selected/complex/pairs.json').read_text())['pairs']
    before=physical(g,witness,word,row,frames,pairs)
    print('Checking independent terminal plan and all rational columns of the actual new executor...',flush=True)
    complex_result=terminal.certify(g,witness,word,row,before,frames,pairs)
    cp=complex_result['profile']
    require(cp['physical_R']==row['R']-len(pairs)-cp['removed_terminal_roles'],'Terminal physical role stock')
    print('Regenerating merged bit word from frozen arcs...',flush=True)
    with tempfile.TemporaryDirectory(prefix='paired-bit-terminal-') as directory:
        base=Path(directory)
        arcs=json.loads((HERE/'selected/bit/arcs.json').read_text())
        merge=bit_merge.regenerate(base,arcs)
        experiment=bit.checked_experiment(HERE/'selected/bit/frames.json',baseline=base)
        bp=experiment.checked_profile
        require(bp==json.loads((HERE/'selected/bit/profile.json').read_text()),'Frozen bit row differs')
        print('Checking every bit column over F2 and Z, and every rational frame determinant...',flush=True)
        formal=formal_bit.certify(experiment)
        primes=prime_frames.certify(experiment)
        records=primes.pop('frame_witnesses')
        primes['all_frame_witnesses_sha256']=sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('Certifying both paid suppliers, finite bridge and 47 strict balanced-assembly inequalities...',flush=True)
    result=parameters.certificate(cp,bp,row)
    bp=dict(bp);bp.pop('numerical_root',None)
    result['construction']=dict(complex=complex_result,
        bit=dict(profile=bp,formal=formal,prime_exclusions=primes,
                 merged_word={k:merge[k] for k in ('merge','checked','input_sha256')}))
    result['source_manifest_sha256']=sha256((HERE/'SOURCE.json').read_bytes()).hexdigest()
    return js(result)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write',action='store_true',help='Write the completely reconstructed certificate')
    p.add_argument('--refresh-sources',action='store_true',help='Explicitly regenerate source pins before checking')
    a=p.parse_args();start=time.monotonic()
    require(not sys.flags.optimize,'Run without -O')
    if a.refresh_sources:(HERE/'SOURCE.json').write_text(json.dumps(manifest(),indent=2,sort_keys=True)+'\n')
    result=verify();encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    target=HERE/'certificate.json'
    if a.write:target.write_text(encoded)
    else:require(target.read_text()==encoded,'Saved certificate differs from complete reconstruction')
    print('PASS kappa=%s; both full formal words, prime witnesses, supplier successors and all 47 strict constraints (%.1fs)'
          %(result['kappa'],time.monotonic()-start),flush=True)


if __name__=='__main__':main()
