#!/usr/bin/env python3
"""Retarget unchanged ambient semantics to immutable PR71 words at the PR73 pin.

This is an explicit metadata adapter, not a modification of any certificate.
The only synthesized files are read-only interface views of pinned certificates.
Existing freshly checked CRT profiles are reused; no CRT computation occurs.
"""
import argparse
from hashlib import sha256
import gzip
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True
import full_ambient
import forward_local
import reverse_local

FRONTIER_PIN='253ecc88faeed55a950c76026d1fe67a7f690123'
NETWORK_PIN='1bef94fd40a746452548c84a4a8f8834670a3113'


def require(ok,msg):
    if not ok:raise ValueError(msg)


def digest(p):return sha256(p.read_bytes()).hexdigest()


def pinned(upstream,name):
    path=upstream/name
    raw=subprocess.check_output(['git','show',FRONTIER_PIN+':'+name],cwd=upstream)
    require(raw==path.read_bytes(),'Modified frontier source: '+name)
    return path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--frontier',required=True,type=Path)
    p.add_argument('--geometry-upstream',required=True,type=Path)
    p.add_argument('--audit-dir',required=True,type=Path)
    p.add_argument('--output-dir',required=True,type=Path)
    a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    geometry_sources=full_ambient.pinned_sources(a.geometry_upstream.resolve())
    for name,expected in geometry_sources.items():
        require(digest(pinned(a.frontier,name))==expected,'Frontier changed inherited geometry: '+name)
    require(subprocess.run(['git','merge-base','--is-ancestor',NETWORK_PIN,FRONTIER_PIN],cwd=a.frontier).returncode==0,'PR71 network is not ancestor of PR73')
    candidate_path=pinned(a.frontier,'research/round6-pr71/parameter-certificate.json')
    candidate=json.loads(candidate_path.read_text())
    compiler_path=pinned(a.frontier,'certificates/split-pair-compiler.json')
    compiler=json.loads(compiler_path.read_text())
    prior_path=a.audit_dir/'pr71-73-independent-receipt.json'
    prior=json.loads(prior_path.read_text())
    require(prior['source_pin']==FRONTIER_PIN,'Independent audit source pin')
    assembly_path=a.audit_dir/'pr71-profile-assembly.json'
    assembly=json.loads(assembly_path.read_text())
    manifest={'upstream_pin':FRONTIER_PIN,'network_pin':NETWORK_PIN,'words':{},
              'scope':'Schema adapter of exact pinned PR71/73 files, not a new compiler or profile certificate.'}
    views={}; input_files={}; paths={}
    for h in (23,25):
        base='certificates/split-pair-'
        word=pinned(a.frontier,base+f'word-{h}.json.gz')
        profile=pinned(a.frontier,base+f'profiles-{h}.json')
        transitions=pinned(a.frontier,base+f'transitions-{h}.json')
        raw_hash=sha256(gzip.decompress(word.read_bytes())).hexdigest()
        saved=compiler['axes'][str(h)]
        independent=next(row for row in prior['axes'] if row['h']==h)
        require(raw_hash==saved['word_sha256']==independent['raw_word_sha256'],'Frontier raw word hash')
        require(digest(word)==saved['gzip_sha256'],'Frontier packed word hash')
        require(independent['complete_both_orientations'],'Missing prior complete dirty-basis replay')
        for file in [word,profile,transitions]:
            name=str(file.relative_to(a.frontier))
            require(digest(file)==independent['inputs'][name],'Independent source hash: '+name)
            input_files[name]=digest(file)
        require(digest(profile)==assembly['profile_input_sha256'][str(profile.relative_to(a.frontier))],'Paid assembly profile source')
        manifest['words'][str(h)]={'word_sha256':raw_hash,'gzip_sha256':digest(word)}
        views[h]=dict(saved,profile=json.loads(profile.read_text()),transitions=json.loads(transitions.read_text()))
        paths[h]=word
    adapters=a.output_dir/'schema-views';adapters.mkdir(exist_ok=True)
    manifest_path=adapters/'source-word-manifest.json'
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    receipt_paths={}
    for h,view in views.items():
        receipt_paths[h]=adapters/f'axis-{h}.json'
        receipt_paths[h].write_text(json.dumps(view,indent=2)+'\n')
    def binary(h):return a.audit_dir/'profile-inputs'/f'pr71-{h}.bin'
    f=forward_local.audit(paths[23],manifest_path,receipt_paths[23],binary(23))
    print('PASS frontier forward h23',flush=True)
    r=reverse_local.audit(paths[25],manifest_path,receipt_paths[25],binary(25))
    print('PASS frontier physical inverse+bank rename h25',flush=True)
    g=forward_local.audit(paths[25],manifest_path,receipt_paths[25],binary(25))
    # Explicit field-name view of independent assembly, preserving every count.
    selected_view={'bit':dict(assembly,total_rank=assembly['rank_mass'])}
    complete=full_ambient.profile(selected_view,f,r,views)
    for key in ['m','N','W','total_rank','deficit','parts','child_multiplicities']:
        require(complete[key]==candidate['bit'][key], 'Direct public parameter-certificate binding: '+key)
    require(max(map(int,complete['child_multiplicities']))==candidate['bit']['maxchild'],'Public maximum child')
    result=dict(status='PASS',selected_profile='PR71 network / PR73 parameters',source_pin=FRONTIER_PIN,
        network_pin=NETWORK_PIN,checker_sha256=digest(Path(__file__)),
        public_parameter_certificate_sha256=digest(candidate_path),public_kappa=candidate['kappa'],
        direct_public_parameter_certificate_profile_binding=True,
        source_files=input_files,compiler_certificate_sha256=digest(compiler_path),
        independent_audit_sha256=digest(prior_path),independent_profile_assembly_sha256=digest(assembly_path),
        unchanged_geometry_pin=full_ambient.PIN,unchanged_geometry_files=geometry_sources,
        actual_lines=[full_ambient.actual_lines(23),full_ambient.actual_lines(25)],
        controlled_basis=full_ambient.controlled_corner(),ambient=full_ambient.algebra(),
        complete_profile=complete,
        local_reports={'forward23':f,'reverse25':r,'forward25_flag_and_profile_reference':g},
        schema_adapter={'manifest':'Exact pinned compiler word hashes and pins','axis':'Pinned compiler axis object plus pinned profile and transition objects','assembly':'Independent assembly object with total_rank alias for rank_mass; no numerical changes'},
        scope='Same complete compact ambient schedule and exact residual/profile correspondence as PR64, now bound to actual immutable PR71 words at PR73. Fresh CRT/profile verification comes from the separate independent audit; no CRT repeated and no analytic or tape-cost theorem asserted here.')
    (a.output_dir/'full-ambient-pr71-73.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS frontier complete ambient profile',result['complete_profile']['W'],result['complete_profile']['total_rank'],flush=True)

if __name__=='__main__':main()
