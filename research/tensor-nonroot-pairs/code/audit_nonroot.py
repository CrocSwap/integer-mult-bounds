"""Rebuild and independently audit the local auxiliary-line provider.
Usage: audit_nonroot.py PACKAGE_ROOT SOURCE_WORD SELECTION OUTPUT --cxx g++ --boost-include PATH
The PACKAGE_ROOT is the retained tensor-syndrome-portfolio/tensor-retimed-basis package.
This checks the local provider. Whole-pair hosting and the outer assembly are separate checks.
"""
import argparse, hashlib, json, os, subprocess, sys
from pathlib import Path

def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('package',type=Path);ap.add_argument('source',type=Path);ap.add_argument('selection',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--cxx',default='g++');ap.add_argument('--boost-include');a=ap.parse_args()
    here=Path(__file__).resolve().parent;pkg=a.package.resolve();out=a.out.resolve();runtime=pkg/'vendor/runtime';native=pkg/'vendor/native';env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONPATH']=str(pkg/'code')+os.pathsep+str(here)
    commands=[]
    def run(args,log):
        commands.append([Path(str(x)).name if Path(str(x)).is_absolute() else str(x) for x in args])
        result=subprocess.run(list(map(str,args)),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        log.write_text(result.stdout,encoding='utf-8');assert result.returncode==0,(log.name,result.returncode,result.stdout[-2000:])
    assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True)
    temp=out.parent/(out.name+'-constructor.log');run([sys.executable,here/'nonroot_constructor.py',a.source,a.selection,out],temp);temp.rename(out/'constructor.log')
    rec=out/'records';cin=out/'cin';cout=out/'cout';bin=out/'bin';bin.mkdir()
    run([sys.executable,runtime/'export_records.py',out/'word.json',rec],out/'export.log')
    run([sys.executable,runtime/'stage_cohort.py',rec,rec,cin,cout],out/'stage.log')
    builds=[('legality_h','legality',[]),('columns_h','columns',['-DVPORTS=120','-DRHELP=715']),('columns_k','columns_k5',['-DVPORTS=120','-DRHELP=715','-DKPAIRS=5'])]
    for source,name,flags in builds:
        exe=bin/(name+('.exe' if os.name=='nt' else''));cmd=[a.cxx,'-O2','-std=c++17','-DHDIM=8','-DNCOPY=9',*flags,'-I'+str(native)]
        if a.boost_include:cmd+=['-I'+a.boost_include]
        run(cmd+[native/(source+'.cpp'),'-o',exe],out/(name+'-compile.log'))
        args=[cin,cout,cout/(name+'.json')]if name=='legality'else[cout/'COHORT249-RECORDS.bin',cout/(name+'.json')]
        run([exe,*args],out/(name+'.log'))
    run([sys.executable,native/'gram_frames.py',rec,'--gram','e8ham','--h','8','--positive'],out/'gram.log')
    run([sys.executable,here/'mix_auxiliary_check.py',runtime,out/'word.json',rec,out/'MIX-AUXILIARY.json'],out/'mix.log')
    sources={str(p.relative_to(pkg)).replace('\\','/'):digest(p)for p in [runtime/'export_records.py',runtime/'stage_cohort.py',runtime/'e8core.py',runtime/'mix_check.py',native/'legality_h.cpp',native/'columns_h.cpp',native/'columns_k.cpp',native/'gram_frames.py',native/'json.hpp',pkg/'code/schur_constructor.py']}
    sources.update({p.name:digest(p)for p in [here/'nonroot_constructor.py',here/'mix_auxiliary_check.py',Path(__file__)]})
    receipts={str(p.relative_to(out)).replace('\\','/'):digest(p)for p in out.rglob('*')if p.is_file()and p.suffix!='.exe'}
    report=dict(status='PASS_FRESH_NATIVE_AUXILIARY_PROVIDER',source_sha256=digest(a.source),selection_sha256=digest(a.selection),candidate_sha256=digest(out/'word.json'),source_hashes=sources,receipts=receipts,commands=commands,scope='Finite provider geometry, positive Gram, independent dirty scalar columns, integer operand spans, source-bound reconstruction and22 omission controls. Whole-pair hosting and global pricing must be checked separately.')
    (out/'LOCAL-AUDIT-MANIFEST.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(report['status'],report['candidate_sha256'])
if __name__=='__main__':main()
