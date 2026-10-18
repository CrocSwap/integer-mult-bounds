"""Independent exhaustive pattern enumeration and isolated rejection controls."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import product
import argparse, gzip, hashlib, json, shutil, subprocess, sys, tempfile

ap=argparse.ArgumentParser()
ap.add_argument('--package',type=Path,required=True)
ap.add_argument('--work',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
args=ap.parse_args();P=args.package.resolve();SEED=args.work.resolve();OUT=args.out.resolve();OUT.mkdir(parents=True,exist_ok=True)
read = lambda p: json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='ceiling-controls-') as td:
    root=Path(td);pkg=root/'pkg';work=root/'work';(pkg/'code').mkdir(parents=True);(pkg/'data').mkdir();work.mkdir()
    for name in ('check_ceiling.py','exact_intervals.py'):
        shutil.copyfile(P/'code'/name,pkg/'code'/name)
    shutil.copyfile(P/'data/PLAN.json',pkg/'data/PLAN.json')
    shutil.copyfile(SEED/'RESULT.json',work/'RESULT.json')
    for pid in ('jp8','atm3'):
        (work/f'{pid}-local').mkdir()
        for name in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz'):
            shutil.copyfile(SEED/f'{pid}-local'/name,work/f'{pid}-local'/name)
    def run():
        return subprocess.run([sys.executable,'-I','-O','-B',str(pkg/'code/check_ceiling.py'),'--work',str(work)],capture_output=True,text=True)
    control=run();assert control.returncode==0,control.stderr
    cert=read(work/'EXACT-CEILING.json')
    # Five bounded integer loops, independent of the certificate's DP recurrence.
    widths=(4,5,7,8,9);weights=(-4,-41,-19,-8,3);best={};count=0
    for ns in product(*(range(49//w+1)for w in widths)):
        used=sum(n*w for n,w in zip(ns,widths))
        if used>48:continue
        count+=1;value=sum(n*w for n,w in zip(ns,weights));best[used]=max(best.get(used,-10**9),value)
    rows={(x['capacity'],x['remainder']):x for x in cert['pattern_remainder_checks']}
    assert set(rows)=={(c,c-s)for c in(8,16,32,48)for s in best if s<=c}
    assert len(rows)==92
    for(c,r),row in rows.items():
        assert row['maximum_pattern_weight']==best[c-r]
        assert sum(row['maximizing_pattern'])==c-r
        assert sum(dict(zip(widths,weights))[w]for w in row['maximizing_pattern'])==best[c-r]
        assert Q(row['lower_margin'])>0 if r not in(0,48)else Q(row['lower_margin'])==0
    lower=Q(1626010676080313339567,10**24);upper=Q(cert['upper_kappa'])
    assert 0<upper-lower<Q(51,10**24)
    mutations=[]
    def mutate(name,rel,change,expected):
        path=(pkg if rel.startswith('data/')else work)/rel;original=path.read_bytes();x=read(path);change(x)
        raw=(json.dumps(x)+'\n').encode();path.write_bytes(gzip.compress(raw,mtime=0)if path.suffix=='.gz'else raw)
        response=run();path.write_bytes(original)
        assert response.returncode!=0 and expected in response.stderr,(name,response.stderr)
        mutations.append(dict(name=name,exit_code=response.returncode,reason=expected))
    mutate('wrong_width_registry','data/PLAN.json',lambda x:x['provider_registry']['jp8']['widths'].__setitem__(0,1),'actual widths')
    mutate('wrong_capacity','data/PLAN.json',lambda x:x['windows'][next(iter(x['windows']))].__setitem__(0,9),'fixed capacity geometry')
    mutate('wrong_baseline_profile','RESULT.json',lambda x:x['global_profile'].__setitem__('1',x['global_profile']['1']+1),'actual baseline profile')
    mutate('invalid_upper_endpoint','RESULT.json',lambda x:x.__setitem__('complex_lower','0'),'upper endpoint must violate moment')
    def remove_paid(x):
        i=next(i for i,g in enumerate(x['backward'])if g[0]in('climb','center'));x['backward'].pop(i)
    mutate('backward_profile_changed','jp8-local/LOCAL-PROGRAMS.json.gz',remove_paid,'both orientations')
    assert run().returncode==0
record=dict(status='PASS_INDEPENDENT_ENUMERATION_AND_REJECTIONS',integer_multisets=count,
            remainder_cases=len(rows),exact_gap=str(upper-lower),rejections=mutations,
            check_ceiling_sha256=sha(P/'code/check_ceiling.py'),optimized_python=True)
(OUT/'CEILING-CONTROLS.json').write_text(json.dumps(record,indent=2)+'\n')
print(record['status'],count,'multisets;',len(mutations),'rejections')
