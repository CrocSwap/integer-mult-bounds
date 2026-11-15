# Exact: X starts on <q_p>, Y ends on q_p^perp, q_p.q_p = 1  =>  no chart F with <q_p> <= F <= q_p^perp (X and Y never share a chart
# that is both above X-birth and below Y-end).  Also: which charts X and Y actually share during the word.
import sys
sys.path.insert(0, '../../PRICEKIT')
import pricekit as pk
W = pk.load('../../ATTACK/STACK7616/best7616.json.gz')
def span(b):
    s = {0}
    for v in b: s |= {x ^ v for x in s}
    return frozenset(s)
sp = [span(b) for b in W['frames']]
dot = lambda a, b: bin(a & b).count('1') & 1
ok_line = ok_perp = aniso = 0
for i, r in enumerate(W['live']):
    q = W['ports'][i]
    ok_line += sp[W['initial'][r]] == frozenset({0, q})
    ok_perp += sp[W['final'][r + 112]] == frozenset(v for v in range(512) if not dot(v, q))
    aniso += dot(q, q)
print('ports', len(W['live']), 'X starts on <q_p>:', ok_line, ' Y ends on q_p^perp:', ok_perp, ' q_p.q_p = 1:', aniso)
X2Y2 = sum(sp[W['initial'][x]] == frozenset({0, W['ports'][W['live'].index(l)]}) for x, l in
           zip(W['hosted']['X2'], [W['live'][i] for i in W['hosted']['Dports']]))
print('X2 starts on its port line (assuming X2 order = Dports order):', X2Y2, 'of', len(W['hosted']['X2']))
# direct X<->Y same-chart ADDs on the same port
cur = list(W['initial']) + [None] * W['owned_fields']; pair = 0; cross = 0
partner = {r: r + 112 for r in W['live']}; partner.update({r + 112: r for r in W['live']})
for e in W['program']:
    if e[0] == 'MOVE': cur[e[1]] = e[3]
    elif e[0] in ('ADD', 'COPY') and partner.get(e[1]) == e[2]: pair += 1
print('direct ADDs between a port\'s own X and Y:', pair)
