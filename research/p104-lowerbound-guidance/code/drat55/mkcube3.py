"""mkcube3.py base.cnf mask out.cnf [fixes]  -- OWN implementation (no LOOSE code run) of the sound cube for inactive set I=mask:
base body + 16 units used[z,8]=[z in I] + (optional value fixes 'z:a,z:a' meaning d_z=a) + d-lex-leader over Stab(I) only
(Stab(I) = non-identity p in perms.pkl with ind(p[j])=ind(j) for all j).  Same lex encoding as zsat_sym.py (d >=lex d o p, positions ascending)."""
import pickle, sys
T55='code/tight55/'
base, mask, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
fixes = [tuple(map(int, x.split(':'))) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 and sys.argv[4] else []
U = pickle.load(open(base + '.map', 'rb'))['used']
uz = lambda z, i: U[(z, i)]
P = [tuple(p) for p in pickle.load(open(T55 + 'perms.pkl', 'rb'))]
ind = [mask >> j & 1 for j in range(16)]
stab = [p for p in P if all(ind[p[j]] == ind[j] for j in range(16)) and any(p[j] != j for j in range(16))]
with open(base) as fh:
    hdr = fh.readline().split(); body = fh.read().rstrip('\n') + '\n'
nv = int(hdr[2]); nc = int(hdr[3]); cls = []
for z in range(16): cls.append([uz(z, 8)] if ind[z] else [-uz(z, 8)])
for z, a in fixes:      # d_z = a  <=>  used[z,a-1] (if a>0) and not used[z,a] (if a<9)
    if a > 0: cls.append([uz(z, a - 1)])
    if a < 9: cls.append([-uz(z, a)])
for p in stab:
    prev = None
    for j in range(16):
        if p[j] == j: continue
        nv += 1; e = nv; pre = [] if prev is None else [-prev]
        for v in range(9): cls.append(pre + [-uz(p[j], v), uz(j, v)])
        ss = []
        for v in range(9):
            nv += 1; ss.append(nv); cls.append([-nv, uz(j, v)]); cls.append([-nv, -uz(p[j], v)])
        cls.append(pre + [e] + ss); prev = e
with open(out, 'w') as fh:
    fh.write(f'p cnf {nv} {nc+len(cls)}\n' + body + ''.join(' '.join(map(str, c)) + ' 0\n' for c in cls))
print('stab order', len(stab) + 1)
