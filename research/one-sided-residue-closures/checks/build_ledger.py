# consolidated ledger for the 603 d>=4 rows (input data/rows_input.csv)
import csv, ast, json, os
from paths import DATA
from collections import Counter
rows=list(csv.DictReader(open(os.path.join(DATA,'rows_input.csv'))))
rrc=json.load(open('rrc_results.json'))
lp=json.load(open('lemp_results.json'))
key=lambda d,ws:(int(d),tuple(sorted(ws)))
def keyset(fn,wcol='weights'):
    try: return {key(r['d'],ast.literal_eval(r[wcol])) for r in csv.DictReader(open(fn))}
    except FileNotFoundError: return set()
scA2=keyset(os.path.join(DATA,'src_scA2_killed.csv')); scB2=keyset(os.path.join(DATA,'src_scB2_killed.csv')); s7b=keyset(os.path.join(DATA,'src_s7b_killed.csv'))
LP_OK=True   # set False if covering facts fail (see REPORT)
out=[]; cnt=Counter()
for i,r in enumerate(rows):
    ws=ast.literal_eval(r['weights']); k=key(r['d'],ws); src=[]; cert=[]
    st=r['status']
    if st.startswith('KILLED span'): src.append('earlier span-cover run (6,6,5)s0@T7 [prior, not re-audited]')
    o=rrc[i]
    if o[4]==True:
        tags=[]
        for tag,c in o[5]:
            if c[0]=='IMM': tags.append('%s:IMM K=%s'%(tag,list(c[1])))
            else: tags.append('%s:j=%d K0(g)=%s |F|=%d'%(tag,c[2],list(c[1]),len(c[4])))
        lab='RRC'
        if st.startswith('CIRCUIT-proven'): lab='root-count immediate rule / RRC'
        if k in s7b: lab='RRC with K0 empty'
        if k in scB2: lab='RRC (class B)'
        src.append(lab+' [audited]'); cert.append(' ; '.join(tags))
    if LP_OK and lp[str(i)]:
        v=lp[str(i)]
        if k in scA2: src.append('Lemma P/P\' [audited; original class-A kill]')
        else: src.append('Lemma P at T-level [audited lemma, new application]')
        cert.append('LemmaP %s S=%s e\'=%d m=%d'%(v[0],v[1],v[2],v[3]))
    status='KILLED' if any('[audited' in s for s in src) else ('KILLED(prior-only)' if src else 'OPEN')
    cnt[(status)]+=1
    out.append([i,r['d'],r['slack'],r['weights'],r['e'],st,status,' | '.join(src),' || '.join(cert)])
with open('ledger_recomputed.csv','w',newline='') as f:
    w=csv.writer(f,lineterminator='\n'); w.writerow(['row','d','slack','weights','e','earlier_status','audit_status','killed_by','certificates']); w.writerows(out)
print(cnt)
c2=Counter((r[2],r[6]) for r in out); print(sorted(c2.items()))
op=[r for r in out if r[6]=='OPEN']; print('OPEN by orig class',Counter(r[5] for r in op))
