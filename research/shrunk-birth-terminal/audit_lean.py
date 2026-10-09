#!/usr/bin/env python3
"""Bind the unchanged Lean companion to the actual selected word and certificate.

This checks exact input derivation, generation and saved compile provenance;
fresh Lean kernel compilation belongs to make formal-historical-verify.
"""
from pathlib import Path
from hashlib import sha256
from collections import Counter
from fractions import Fraction as Q
import gzip, json, re, shutil, subprocess, sys, tempfile
if sys.flags.optimize:raise RuntimeError('Assertions must remain enabled')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];L=HERE/'lean'
read=lambda p:json.loads(p.read_text())
sha=lambda p:sha256(p.read_bytes()).hexdigest()
def require(ok,reason):
    if not ok:raise ValueError(reason)
def main():
    source=L/'ShrunkBirthTerminal.lean';verification=read(L/'verification.json');data=read(L/'input.json')
    require(sha(source)==verification['source_sha256'],'Lean source digest')
    require(sha(L/'generate.py')==verification['generator_sha256'],'Lean generator digest')
    require(sha(L/'input.json')==verification['input_sha256'],'Lean input digest')
    require(source.read_bytes()==(ROOT/'formal/lean/KappaCheck/ShrunkBirthTerminal.lean').read_bytes(),'Integrated Lean module differs')
    aliases={'work/r12-audit/canonical-joint-expansion/joint-expansion/certificate.json':HERE/'audit/independent-prepackage-certificate.json'}
    aliases['work/r12-terminal/joint-expansion/word.json.gz']=HERE/'selected/word.json.gz'
    aliases['work/r12-terminal/joint-expansion/physical-audit.json']=HERE/'audit/discovery-physical-audit.json'
    aliases['work/r12-terminal/joint-expansion/READOUT_COST.json']=HERE/'audit/discovery-scalar-bill.json'
    require(set(aliases)==set(data['pins']),'Lean source mapping incomplete')
    for name,path in aliases.items():require(sha(path)==data['pins'][name],'Lean pinned input: '+name)
    require(data['certificate']==read(HERE/'audit/independent-prepackage-certificate.json'),'Lean certificate snapshot')
    current=read(HERE/'certificate.json')
    math_fields=['profile','complex_saving','next_complex_rejected','first_moment','independent_moment','actual_bit_saving','assembly_bit','beta','eta','backoff','kappa','assembly','cutoffs','fixed_profile_family_ceiling']
    for key in math_fields:
        require(key in current and current[key]==data['certificate'][key],'Lean/current certificate mathematical mismatch: '+key)
    bridge=json.loads(json.dumps(current['finite_bridge']));oldbridge=json.loads(json.dumps(data['certificate']['finite_bridge']))
    # Only these two prose contracts were reworded in the portable schema.
    for x in [bridge,oldbridge]:
        x['rows'].pop('contract');x['semantic'].pop('exact_grid')
    require(bridge==oldbridge,'Lean/current finite bridge numeric mismatch')
    require(current['finite_bridge']['complex']['scalar_group_upper']==read(HERE/'selected/READOUT_COST.json')['global_scalar_group_upper']==read(HERE/'audit/discovery-scalar-bill.json')['global_scalar_group_upper'],'Corrected billing metadata changed the Lean scalar charge')
    word=json.loads(gzip.decompress((HERE/'selected/word.json.gz').read_bytes()));audit=read(HERE/'selected/physical-audit.json')
    exterior=Counter(len(word['frames'][word['initial_frames'][2*word['v']+role]]) for role in word['physical_roles'])
    forward={int(k):n for k,n in audit['forward_frame']['histogram'].items()}
    require({str(k):v for k,v in exterior.items()}==data['initial_frame_dimension_histogram'],'Lean exterior counts not from actual word')
    require({str(k):v for k,v in forward.items()}==data['forward_histogram'],'Lean forward counts not from actual audit')
    require((word['virtual_roles'],len(word['birth_pairs']),len(word['eliminated_terminal_roles']))==(data['virtual_roles'],data['births'],data['terminals']),'Lean role counts')
    h=word['h'];v=word['v'];m=h*h;counts=Counter({k:2*v*n for k,n in forward.items()})
    for k,n in exterior.items():counts[m-h+k]+=2*v*n
    counts[(h-1)**2]+=2*v*v;counts[1]+=v*v
    require({str(k):n for k,n in counts.items()}==current['profile']['child_multiplicities'],'Lean complete paid histogram')
    require(Q(verification['kappa'])==Q(current['kappa']),'Lean kappa')
    expected=re.findall(r'^#print axioms (\S+)\s*$',source.read_text(),re.M)
    require(len(expected)==len(set(expected))==240,'Lean theorem audit roster')
    for name,digest in verification['compile_receipts'].items():require(sha(L/name)==digest,'Lean saved compile receipt: '+name)
    require((L/'receipts/compile/exit-code').read_text().strip()=='0','Lean saved compile exit')
    output=(L/'receipts/compile/output.log').read_text()
    rows=re.findall(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",output,re.M)
    allowed={'propext','Classical.choice','Quot.sound'}
    require(len(rows)==len(expected) and {n for n,_ in rows}==set(expected),'Lean saved axiom coverage')
    require(all({x.strip() for x in text.split(',')}-{''}<=allowed for _,text in rows),'Lean forbidden saved axiom')
    with tempfile.TemporaryDirectory(prefix='shrunk-terminal-lean-') as folder:
        destination=Path(folder)
        for name in ['generate.py','input.json']:shutil.copy2(L/name,destination/name)
        subprocess.run([sys.executable,str(destination/'generate.py')],check=True,capture_output=True,text=True)
        require((destination/'ShrunkBirthTerminal.lean').read_bytes()==source.read_bytes(),'Lean generation differs')
    print('PASS unchanged Lean module, actual complete physical-count arrays, exact certificate linkage, deterministic generation and 240 saved axiom records')
if __name__=='__main__':main()
