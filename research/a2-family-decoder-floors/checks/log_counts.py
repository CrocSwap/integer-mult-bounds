# Headline lines of the shipped RECORDED logs (HUNT-A2 robust CP-SAT / CEGAR runs; not re-run by verify.sh).  Content is pinned by MANIFEST.sha256.
import os, re
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','evidence','logs','hunt-a2')
def rd(n): return open(os.path.join(root,n+'.log.txt')).read()
ok=True
def chk(name,cond,msg):
    global ok
    print(('PASS ' if cond else 'FAIL ')+msg); ok&=bool(cond)
for s in ('gen','s2','s8','s10'):
    chk(s,re.search(r'it 0 status INFEASIBLE -> no robust assignment <= 63',rd('P112_cegar_'+s)),'P112 robust CEGAR (%s): no square decoder of cost <= 63 for any parameter in this stratum'%s)
    chk(s,'relaxation min below 64 : None' in rd('P112_opt_'+s),'P112 exact duality B&B (%s member): nothing below 64'%s)
t=rd('P112_cegar64_s2'); chk('tie',('CANDIDATE saved' in t) and 'Fraction(37, 6)' in t and 'Fraction(29, 2), Fraction(-33, 2)' in t,'P112 cap-64 CEGAR (s2) found a realisable cost-64 assignment at theta=(37/6,0,-11/2,4/3), zX=(0,29/2,-33/2)')
for s in ('gen','s2','s4','s6'):
    chk(s,'INFEASIBLE -> no robust assignment <= 71' in rd('E8_cegar_'+s),'E8 robust CEGAR (%s): no square decoder of cost <= 71'%s)
chk('e8gen2','INFEASIBLE -> no robust assignment <= 71' in rd('E8_cegar2_gen'),'E8 robust CEGAR (second run, generic): no cost <= 71')
for s in ('gen','s2'): chk(s,'CANDIDATE saved' in rd('E8_cegar72_'+s),'E8 cap-72 CEGAR (%s): realisable cost-72 assignment found'%s)
chk('sp112','row-special 2' in rd('P112_specall') and 'z-special 6' in rd('P112_specall') and 'col theta-special (not in B-locus) 0' in rd('P112_specall'),'P112 special-locus census: 2 row-special sets, 0 column theta-special, 6 z-special')
chk('sp104','row-special 4' in rd('P104_specall') and 'z-special 6' in rd('P104_specall') and 'col theta-special (not in B-locus) 0' in rd('P104_specall'),'P104 special-locus census: 4 row-special sets, 0 column theta-special, 6 z-special')
chk('spe8','row-special 0' in rd('E8_specall') and 'z-special 6' in rd('E8_specall') and 'col theta-special (not in B-locus) 0' in rd('E8_specall'),'E8 special-locus census: 0 row-special, 0 column theta-special, 6 z-special')
raise SystemExit(0 if ok else 1)
