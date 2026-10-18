#!/usr/bin/env python3
"""Exact signed-restoration extension of PR1625. Standard library only.
Prepared for @Pseudoataraxia with substantial OpenAI ChatGPT assistance.
Apache-2.0. The vendor checker is retained unchanged with its own attribution.
This local replay is not the full native/T74 admission; see replay_full.py.
"""
from __future__ import annotations
import argparse,copy,gzip,hashlib,importlib.util,json,tempfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

P=Path(__file__).resolve().parent
N=704

def need(ok:bool,message:str)->None:
    if not ok: raise ValueError(message)

def read(path:Path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)

def payload(obj)->bytes:
    return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()

def build(base,recipe,pid):
    ed=recipe['edit']; w=copy.deepcopy(base); deleted=set(ed['delete'])
    need(len(deleted)==len(ed['delete']) and all(0<=i<len(base['B']) for i in deleted),'deletion indices')
    at={};tags=[]
    for i,g in ed['insert']:
        need(0<=i<=len(base['B']) and g[:3][::2]==['add',554],'insertion grammar')
        at.setdefault(i,[]).append(copy.deepcopy(g))
    out=[]
    for i in range(len(base['B'])+1):
        for g in at.get(i,[]):tags.append((len(out),1));out.append(g)
        if i<len(base['B']) and i not in deleted:out.append(copy.deepcopy(base['B'][i]))
    w['B']=out
    need(not ed.get('prepend'),'unexpected cleanup prepend')
    ins=[]
    for j,g in ed['tail']:
        need(0<=j<=len(w['early_cleanup']),'tail position')
        w['cleanup'].append(copy.deepcopy(g));ins.append((j,len(w['cleanup'])-1))
    for j,ci in sorted(ins):w['early_cleanup'].insert(j,[ci,[]]);tags.append((len(out)+j,-1))
    for section,changes in recipe['words'][pid]['frames'].items():
        need(section in ('B','cleanup','early_cleanup'),'frame section')
        seen=set()
        for i,frame in changes:
            need(i not in seen and 0<=i<len(w[section]),'frame index');seen.add(i)
            w[section][i][-1]=copy.deepcopy(frame)
    w['report'].update(copy.deepcopy(recipe['words'][pid]['report_updates']))
    return w,dict(tags)

def sequence(w):
    return w['B']+[w['cleanup'][i][:-1]+[frame] for i,frame in w['early_cleanup']]

def apply(g,rows):
    t=g[1]
    if g[0]=='add':
        s=g[2];need(t!=s,'self addition');c=Q(g[3],g[4])
        for k,x in list(rows[s].items()):
            y=rows[t].get(k,Q(0))+c*x
            if y:rows[t][k]=y
            else:rows[t].pop(k,None)
    elif g[0]=='scale':
        c=Q(g[2],g[3]);need(c!=0,'zero scaling');rows[t]={k:c*x for k,x in rows[t].items()}
    else:raise ValueError('unknown gate')

def endpoint(w,tags=None):
    rows=[{i:Q(1)} for i in range(N)];observed=[]
    for i,g in enumerate(sequence(w)):
        if tags and i in tags:
            need(g[0]=='add' and g[2]==554,'tag does not read pivot')
            need(rows[554]=={554:Q(tags[i])},'signed initial-pivot boundary')
            observed.append([i,tags[i]])
        apply(g,rows)
    return rows,observed

def verify_word(base,w,tags):
    changed={'B','cleanup','early_cleanup','report'}
    need(set(base)==set(w) and all(base[k]==w[k] for k in base if k not in changed),'unchanged interfaces')
    old,_=endpoint(base);new,observed=endpoint(w,tags)
    need(old==new,'complete B and early-cleanup map differs')
    def remainder(x):
        early={i for i,F in x['early_cleanup']}
        return [g for i,g in enumerate(x['cleanup']) if i not in early]
    need(remainder(base)==remainder(w),'remaining cleanup differs')
    need(Counter(s for i,s in observed)=={1:5,-1:1},'five positive and one negative source access')
    return observed

def rejection(action,label):
    try:action()
    except (ValueError,RuntimeError,AssertionError,KeyError,IndexError):return label
    raise ValueError('negative control accepted: '+label)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);a=ap.parse_args()
    if a.out:need(not a.out.exists(),'output directory already exists')
    rec=read(P/'RECIPE.json');spec=importlib.util.spec_from_file_location('retained_audit',P/'vendor/audit_local.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
    records=[];controls=[]
    with tempfile.TemporaryDirectory(prefix='p554-exact-') as tmp:
        T=Path(tmp)
        for pid in ('gauge44','extra'):
            bp=P/'inputs'/(pid+'-1625.json.gz');raw=bp.read_bytes();pin=rec['words'][pid]
            need(hashlib.sha256(raw).hexdigest()==pin['source_sha256'],'original source pin')
            need(hashlib.sha256(gzip.decompress(raw)).hexdigest()==pin['source_content_sha256'],'original content pin')
            base=read(bp);w,tags=build(base,rec,pid);data=payload(w)
            need(hashlib.sha256(data).hexdigest()==pin['target_content_sha256'],'target content pin')
            observed=verify_word(base,w,tags)
            wp=T/(pid+'.json.gz');wp.write_bytes(gzip.compress(data,mtime=0));rp=T/(pid+'-audit.json');audit.run(wp,rp)
            ar=read(rp);old={int(r):n for r,n in base['report']['local_profile'].items()};new={int(r):n for r,n in ar['local_profile'].items()}
            delta={r:new.get(r,0)-old.get(r,0) for r in set(old)|set(new) if new.get(r,0)!=old.get(r,0)}
            need(delta=={1:1,2:-2,3:1},'paid profile delta')
            need(sum(r*n for r,n in old.items())==sum(r*n for r,n in new.items()),'rank mass')
            need(sum(old.values())==sum(new.values()),'recursive call count')
            for i in range(5):
                mutant=copy.deepcopy(rec);mutant['edit']['insert'].pop(i)
                def check_mut(m=mutant):
                    z,tt=build(base,m,pid);verify_word(base,z,tt)
                controls.append(rejection(check_mut,pid+'/omit-B-'+str(i)))
            for label,mutate in [('omit-tail',lambda e:e['tail'].clear()),('wrong-positive-closing',lambda e:e['tail'][0][1].__setitem__(3,1)),('close-too-early',lambda e:e['tail'][0].__setitem__(0,83)),('retain-deleted-read',lambda e:e['delete'].clear())]:
                m=copy.deepcopy(rec);mutate(m['edit'])
                controls.append(rejection(lambda m=m:verify_word(base,*build(base,m,pid)),pid+'/'+label))
            for label,mutate in [('bad-frame',lambda z:z['B'][520].__setitem__(-1,[24])),('missing-child-charge',lambda z:z['report']['local_profile'].__setitem__('2',new[2]-1))]:
                m=copy.deepcopy(w);mutate(m);mp=T/(pid+'-'+label+'.gz');mp.write_bytes(gzip.compress(payload(m),mtime=0))
                controls.append(rejection(lambda:audit.run(mp,T/'mutant-audit.json'),pid+'/'+label))
            records.append(dict(provider=pid,columns=N,signed_reads=observed,profile=new,content_sha256=pin['target_content_sha256']))
            if a.out:
                a.out.mkdir(parents=True,exist_ok=True);(a.out/(pid+'.json.gz')).write_bytes(wp.read_bytes())
    result=dict(status='PASS_P554_SIGNED_RESTORATION',providers=records,controls=controls,scope='Exact local finite construction; full T74 admission is a separate replay.')
    if a.out:(a.out/'LOCAL-RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('PASS_P554_SIGNED_RESTORATION providers=2 columns=704 controls='+str(len(controls))+' delta=H1+1,H2-2,H3+1')

if __name__=='__main__':main()
