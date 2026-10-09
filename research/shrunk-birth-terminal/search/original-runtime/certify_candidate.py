"""Exact arithmetic for a new R12 complex profile using pinned PR125 assembly.
Chafik Boukhalfa with OpenAI Codex assistance; inherited solver credits retained.
This executes no foreign producer; the unchanged published bit profile remains
a working input and only the new composed complex profile is certified here.
"""
from pathlib import Path
from fractions import Fraction
from hashlib import sha256
import importlib.util,json,math,sys,datetime
W=Path(__file__).resolve().parent;P=W/'repo/research/r12-logical-frames';O=Path(sys.argv[1]).resolve()
spec=importlib.util.spec_from_file_location('r12_exact',P/'certificate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=json.loads((O/'complex-profile.json').read_text());p['child_multiplicities']={int(t):c for t,c in p['child_multiplicities'].items()}
lo,hi=0.0,0.001
for _ in range(70):
 a=(lo+hi)/2
 if math.fsum(c*t*math.expm1(a*math.log(p['m']/t)) for t,c in p['child_multiplicities'].items())<p['deficit']:lo=a
 else:hi=a
n=int(lo*10**12);left,right=n-4,n+5
assert m.contracts(p,Fraction(left,10**12)) and not m.contracts(p,Fraction(right,10**12))
while right-left>1:
 mid=(left+right)//2
 if m.contracts(p,Fraction(mid,10**12)):left=mid
 else:right=mid
m.COMPLEX=Fraction(left,10**12);result=m.js(m.exact(phase=p))
(O/'certificate.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
summary=dict(status='PASS exact own-profile moments and next-grid rejection, all47 strict constraints and7 assembly margins',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),complex_saving=str(m.COMPLEX),kappa=result['kappa'],kappa_decimal=float(Fraction(result['kappa'])),profile_sha256=sha256((O/'complex-profile.json').read_bytes()).hexdigest(),certificate_sha256=sha256((O/'certificate.json').read_bytes()).hexdigest(),solver_sha256=sha256((P/'certificate.py').read_bytes()).hexdigest(),scope='Finite numerical certificate; physical/reflection verification is a separate receipt. Unchanged foreign bit profile is an accepted working input.')
(O/'arithmetic.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print(json.dumps(summary,indent=2))
