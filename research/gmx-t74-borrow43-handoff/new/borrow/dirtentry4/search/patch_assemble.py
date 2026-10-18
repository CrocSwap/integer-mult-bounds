# scratch-only (discovery): read the 1e-3000 floors of the exact moment roots instead of the 1e-24 discovery endpoints (as PR2833 did)
import sys,json
p,e=sys.argv[1],sys.argv[2];s=open(p).read()
old="if DISCOVER:b=Q(M.certify(H,73,owner['live'],False)['lower']);conservative_b=Q(M.certify(H,73,owner['live'],True)['lower'])"
assert old in s
new="if DISCOVER:_E=json.load(open(%r));b=Q(int(_E['complex']),10**3000);conservative_b=Q(int(_E['conservative']),10**3000)"%e
open(p,'w').write(s.replace(old,new));print('patched scratch assemble')
