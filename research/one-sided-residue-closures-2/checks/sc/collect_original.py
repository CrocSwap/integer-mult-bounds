#!/usr/bin/env python3
# collect.py: parse state/*.json + runs/*.out -> killed.csv, ledger_sc.csv (copy of SPANCOVER/ledger.csv with SC-OK kills), status.txt
import sys,os,json,glob,re,csv
sys.path.insert(0,'<removed>')
from sclib import *
S={}
for f in sorted(glob.glob(SC+'/state/*.json')):
    S[os.path.basename(f)[:-5]]=json.load(open(f))
def verify_pass(k,v):
    # independent re-check: every chunk of the config has an OVERALL line with target<=passT and no CRACK
    bad=0
    for ch in v['chunks']:
        p='%s/runs/%s_M%dr%dJ%dj%d.out'%(SC,k,*ch)
        try: t=open(p).read()
        except Exception: bad+=1; continue
        m=re.search(r'target (\d+) mod',t)
        if 'CRACK?' in t or 'OVERALL' not in t or not m or int(m.group(1))>v['passT']: bad+=1
    return bad==0
killed={}      # row idx -> 'cfg@T'
lines=[]
for k,v in S.items():
    cc=parse_key(k); n=len(v.get('chunks',[]))
    done=0
    for ch in v.get('chunks',[]):
        p='%s/runs/%s_M%dr%dJ%dj%d.out'%(SC,k,*ch)
        try:
            t=open(p).read()
            if 'OVERALL' in t and 'CRACK?' not in t: done+=1
        except Exception: pass
    lines.append('%-14s %-10s lb=%s passT=%s chunks %d/%d'%(k,v.get('status'),v.get('lb'),v.get('passT'),done,n))
    if v.get('status')=='pass' and v.get('passT') and verify_pass(k,v):
        for i in OK:
            if res[i][0]>=v['passT'] and any(le(o,cc) for o in res[i][4]):
                killed.setdefault(i,'%s@T%d'%(k,v['passT']))
    elif v.get('status')=='pass': lines.append('  WARNING: %s pass NOT verified from raw outputs'%k)
with open(SC+'/killed.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['row','d','slack','weights','e','killed_by'])
    for i in sorted(killed):
        r=led[i]; w.writerow([i,r['d'],r['slack'],r['weights'],r['e'],killed[i]])
with open(SC+'/ledger_sc.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['d','slack','weights','e','status'])
    for i,r in enumerate(led):
        st=r['status']
        if i in killed: st='KILLED span SC-OK '+killed[i]
        w.writerow([r['d'],r['slack'],r['weights'],r['e'],st])
dd={}
for i in killed: dd[res[i][0]]=dd.get(res[i][0],0)+1
txt='SC-OK killed %d of %d OK rows (by d: %s)\n'%(len(killed),len(OK),dict(sorted(dd.items())))+'\n'.join(lines)+'\n'
open(SC+'/status.txt','w').write(txt); print(txt)
