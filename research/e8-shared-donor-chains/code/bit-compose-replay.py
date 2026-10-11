"""Replay only the new PR376-helper-reuse / PR381-nine-stage composition.
No upstream verify.sh, public baseline regressions, publication or cleanup.
Usage: python -B bit-compose-replay.py OUT --pr381 PACKAGE381 --reuse PACKAGE376_REUSE
Set BOOST_INCLUDE if Boost is not installed in compiler search paths.
"""
from pathlib import Path
from hashlib import sha256
import argparse, gzip, importlib.util, json, os, shutil, subprocess, sys
assert __debug__, 'Do not disable assertions'
sys.dont_write_bytecode=True

def digest(p): return sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text())
def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('output',type=Path)
    a.add_argument('--pr381',type=Path,required=True)
    a.add_argument('--reuse',type=Path,required=True)
    a.add_argument('--complex',default='999240641319551/1000000000000000000')
    x=a.parse_args();p=x.pr381.resolve();r=x.reuse.resolve();o=x.output.resolve()
    assert not o.exists(), 'Use a fresh output path; prior artifacts are preserved'
    assert not o.is_relative_to(p) and not o.is_relative_to(r)
    o.mkdir(parents=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    for k in ('PYTHONOPTIMIZE','PR315'):env.pop(k,None)
    checks=[]
    def run(name,cmd,expect_failure=False):
        log=o/(name+'.log')
        with log.open('w',encoding='utf-8') as f:
            q=subprocess.run([str(c) for c in cmd],env=env,stdout=f,stderr=subprocess.STDOUT)
        assert (q.returncode!=0) if expect_failure else q.returncode==0,(name,q.returncode,log)
        checks.append(name)
    def py(name,script,*args):run(name,[sys.executable,'-B',script,*args])
    def compile(name,source,*flags):
        binary=o/(name+('.exe' if os.name=='nt' else ''))
        include=['-I'+str(p/'code/bit/checkers')]
        if env.get('BOOST_INCLUDE'):include+=['-I'+env['BOOST_INCLUDE']]
        run('compile-'+name,[env.get('CXX','g++'),'-O2','-std=c++17',*flags,*include,source,'-o',binary])
        return binary
    source=p/'data/bit/bitE8-r865.json.gz'
    assert digest(source)=='1fb726ea3818fe0837cceb0dd22a71a0814f064e5e781628104610d6468e0e55'
    assert digest(r/'frame-selection.json')=='a83d4880579fb1f8cffb701d1d685c157b7fa14ef9d6642e42ff1e4f5a1b8c5c'
    assert digest(r/'reuse-selection.json')=='0b300bab47cf0d69cbc7965bf01c2a27c96b97677ee651334470d8c968b603f1'
    fr=module('composition_frame_replay',r/'frame_replay.py')
    rr=module('composition_reuse_replay',r/'reuse_replay.py')
    fs=read(r/'frame-selection.json');rs=read(r/'reuse-selection.json')
    retimed=fr.reconstruct(source.read_bytes(),fs);word=rr.reconstruct(retimed,rs)
    controls=fr.negative_controls(source.read_bytes(),fs)+rr.negative_controls(retimed,rs)
    wh=sha256(word).hexdigest()
    assert wh=='9974db5500941456e49030a5e5f374f34c707f76a40904fe1833df4f893a1c69'
    (o/'word.json').write_bytes(word);(o/'word.json.gz').write_bytes(gzip.compress(word,mtime=0))
    B=p/'code/bit';CK=B/'checkers';rec=o/'records';cin=o/'cin';cout=o/'cout'
    py('export',B/'export_records.py',o/'word.json',rec)
    expected={'249-records.bin':'9d40536b6cbbedbf11ff3eaa051482db5f2e7a1774ac05bb3ae5e3bbedda44bf','249-states.json':'fb27f6f39e2b835ad6266309bafe14e855a573577dd597ee9f231c9ddfa21a0e','frames.json':'884480e45865a9d9d57f5f7198844a64271b046bc95e9820efbefb9e10878330'}
    assert {n:digest(rec/n) for n in expected}==expected
    py('stage',B/'regression/stage_cohort.py',rec,rec,cin,cout)
    columns=compile('columns-b4-r822',CK/'columns_k.cpp','-DHDIM=8','-DNCOPY=9','-DVPORTS=120','-DRHELP=822','-DKPAIRS=4')
    legal=compile('legality-r822',CK/'legality_h.cpp','-DHDIM=8','-DNCOPY=9')
    legal8=compile('legality-ncopy8',CK/'legality_h.cpp','-DHDIM=8')
    run('columns',[columns,rec/'249-records.bin',o/'columns.json'])
    run('legality',[legal,cin,cout,o/'legality.json'])
    # Six permanent record-level falsifiers: preserve every mutant and its log.
    import struct
    raw=(rec/'249-records.bin').read_bytes();rows=[list(t) for t in struct.iter_unpack('<6i',raw)]
    phaseB=[i for i,e in enumerate(rows) if e[0]==1 and e[5]==4]
    dirt=next(i for i,e in enumerate(rows) if e[0]==1 and e[5]==1)
    changes=[('drop-phase-B',phaseB[len(phaseB)//2],None,'columns'),('bad-add-frame',phaseB[0],(4,0),'legality'),('bad-move-rank',next(i for i,e in enumerate(rows) if e[0]==0 and e[4]>1),(4,-1),'legality'),('cheap-copy',next(i for i,e in enumerate(rows) if e[0]==2),(5,7),'legality'),('drop-dirt',dirt,None,'columns'),('wrong-copy-count',None,None,'legality8')]
    for name,at,change,kind in changes:
        d=o/('mutant-'+name);shutil.copytree(cout,d)
        altered=[t[:] for t in rows]
        if at is not None:
            if change is None:del altered[at]
            elif change==(4,-1):altered[at][4]-=1
            else:altered[at][change[0]]=change[1]
        f=d/'COHORT249-RECORDS.bin';f.write_bytes(b''.join(struct.pack('<6i',*t) for t in altered))
        cmd=[columns,f,d/'rejected.json'] if kind=='columns' else [legal8 if kind=='legality8' else legal,cin,d,d/'rejected.json']
        run(name,cmd,True)
    py('gram',CK/'gram_frames.py',rec,'--gram','e8ham','--h','8','--positive')
    py('geometry',CK/'geometry_k.py','4',o/'word.json.gz','unsplit')
    py('banks',CK/'tile_k.py',rec,'4','8','3')
    py('pricing',CK/'certify_bit_k.py',rec,x.complex,'4','8','3',o/'kappa.json','unsplit')
    py('finite-input',B/'receipts_k.py',o/'word.json.gz',rec,o/'legality.json',o/'columns.json',o/'kappa.json',o/'finite-input.json')
    py('finite',CK/'finite_k.py','e8',o/'finite-input.json',o/'finite.json')
    kap=read(o/'kappa.json');col=read(o/'columns.json');leg=read(o/'legality.json');fin=read(o/'finite.json')
    assert (kap['W'],kap['m'],kap['T'],kap['halving_degree'])==(5346,72,3,2)
    assert kap['bit_coarse']=='255384852701747/250000000000000000'
    assert col['formal_columns_checked']==1782 and col['independent_dirty_registers']==822
    assert len(col['negative_controls'])==18 and leg['copies']==leg['erasures']==9
    assert fin['coefficient']==71903549469403 and fin['row_reserve']['internal_coefficient']==10370
    result={'status':'PASS_NEW_PR376_R822_PR381_B4_COMPOSITION','word_sha256':wh,'record_sha256':expected,'checks':checks,'witness_controls':controls,'pricing':kap,'finite':fin,'method_origin':'PR376 helper lifetime reuse composed with PR381 nine-stage bit bridge; no new local mechanism attributed','scope':'Conditional finite composite; all inherited E8/ninth-centre/bank/compiler/chart/rows/recovery/precision/analytic interfaces remain. No signed source527 defining decoder or full multiplication theorem is newly proved.'}
    (o/'BIT-COMPOSITION-RECEIPT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],kap['kappa'],kap['bit_coarse'])
if __name__=='__main__':main()
