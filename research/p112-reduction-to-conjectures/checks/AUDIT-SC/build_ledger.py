# consolidated ledger for the 603 d>=4 rows (original SPANCOVER/ledger.csv untouched)
import csv, ast, json
from collections import Counter
rows=list(csv.DictReader(open('../SPANCOVER/ledger.csv')))
rrc=json.load(open('rrc_results.json'))
lp=json.load(open('lemp_results.json'))
key=lambda d,ws:(int(d),tuple(sorted(ws)))
def keyset(fn,wcol='weights'):
    try: return {key(r['d'],ast.literal_eval(r[wcol])) for r in csv.DictReader(open(fn))}
    except FileNotFoundError: return set()
scA=keyset('../SC-A/killed.csv'); scA2=keyset('../SC-A2/killed2.csv'); scB2=keyset('../SC-B2/killed.csv'); s7b=keyset('../SC-S7B/killed.csv')
scok=keyset('../SC-OK/killed.csv')
LP_OK=True   # set False if covering facts fail (see REPORT)
out=[]; cnt=Counter()
for i,r in enumerate(rows):
    ws=ast.literal_eval(r['weights']); k=key(r['d'],ws); src=[]; cert=[]
    st=r['status']
    if st.startswith('KILLED span'): src.append('SPANCOVER span (6,6,5)s0@T7 [prior, not re-audited]')
    if k in scok: src.append('SC-OK span [prior]')
    o=rrc[i]
    if o[4]==True:
        tags=[]
        for tag,c in o[5]:
            if c[0]=='IMM': tags.append('%s:IMM K=%s'%(tag,list(c[1])))
            else: tags.append('%s:j=%d K0(g)=%s |F|=%d'%(tag,c[2],list(c[1]),len(c[4])))
        lab='RRC'
        if st.startswith('CIRCUIT-proven'): lab='CIRCUIT S7a + RRC'
        if k in s7b: lab='SC-S7B + RRC'
        if k in scB2: lab='SC-B2 RRC (class B)'
        src.append(lab+' [audited]'); cert.append(' ; '.join(tags))
    if LP_OK and lp[str(i)]:
        v=lp[str(i)]
        if k in scA2: src.append('SC-A/SC-A2 Lemma P/P\' [audited]')
        else: src.append('Lemma P (SC-A) applied by AUDIT-SC [audited lemma, new application]')
        cert.append('LemmaP %s S=%s e\'=%d m=%d'%(v[0],v[1],v[2],v[3]))
    status='KILLED' if any('[audited' in s for s in src) else ('KILLED(prior-only)' if src else 'OPEN')
    cnt[(status)]+=1
    out.append([i,r['d'],r['slack'],r['weights'],r['e'],st,status,' | '.join(src),' || '.join(cert)])
with open('ledger_consolidated.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['row','d','slack','weights','e','orig_status','audit_status','killed_by','certificates']); w.writerows(out)
print(cnt)
c2=Counter((r[2],r[6]) for r in out); print(sorted(c2.items()))
op=[r for r in out if r[6]=='OPEN']; print('OPEN by orig class',Counter(r[5] for r in op))
