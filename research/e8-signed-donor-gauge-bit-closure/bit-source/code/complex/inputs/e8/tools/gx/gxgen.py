"""gxgen.py: gcert/1 JSON -> Lean data modules for `GXD.Raw` (Work/GCert/Data/Raw.lean)
in SEGMENTS, the kernel-check modules of gx-scalar and gx-labels (one module per kernel evaluation), the
kernel-counted block histogram and the interface (Cert) module; after the Python MIRROR of both checks (gxcore).

usage: gxgen.py <gcert1.json[.gz]> <Name> [mirror-only] [gseg=<gates per replay segment>] [batches=<scalar batches>]
                [tsplit=<j: table checked in 2^j subtries>] [frames=1] [seg=<bytes per data module>] [out=<dir>]
   writes <out>/Gen/<Name>/S<i>.lean   data segments (namespace GXD.<Name>)
          <out>/Gen/<Name>.lean        `raw : GXD.Raw`
          <out>/Gen/<Name><Check>.lean one per kernel evaluation (table BIND in gxbind.py)
          <out>/Gen/<Name>Hist.lean, <out>/<Name>Cert.lean
          <GX_OUT>/logs/gen-<Name>.json   everything the rate / instance generator (gxrate.py) needs
"""
import sys, os, json
import gxpaths
import gxcore as gc
import gxunit as gu
import gxbind as gb

ROOT = gxpaths.OUT
MY = ROOT
SEG = 1000000          # bytes of Lean text per data module: measured 0.55 GB + 1.15 GB per MB, 26 s per MB (NOTES.md)
PER = 250              # items per list literal


# ---- derived data: an orthonormal basis through every port (questions.md Q1) -------------------------------
def dot(a, b):
    return bin(a & b).count('1') & 1


def obase(p, h):
    """h masks, first = p, pairwise dots = delta.  W = current complement (basis), c = its characteristic vector."""
    full = (1 << h) - 1
    gc.need(gc.par(p) and p != full, 'obase: port %d is even or all-ones' % p)
    W, c, out, x = [1 << i for i in range(h)], full, [], p
    while True:
        out.append(x)
        c ^= x
        nw = []
        for y in W:                       # project W onto x^perp, keep a basis
            y ^= x if dot(y, x) else 0
            for b in nw:
                y = min(y, y ^ b)
            if y:
                nw.append(y)
        W = nw
        if not W:
            break
        cand = [y for y in W if gc.par(y)] + [a ^ b for i, a in enumerate(W) for b in W[:i] if gc.par(a ^ b)]
        cand = [y for y in cand if y != c or len(W) == 1]
        gc.need(cand, 'obase: no odd vector left (port %d)' % p)
        x = cand[0]
    gc.need(len(out) == h and all(dot(a, b) == (i == j) for i, a in enumerate(out) for j, b in enumerate(out)),
            'obase: not orthonormal (port %d)' % p)
    return out


# ---- Lean text ---------------------------------------------------------------------------------------------
def ll(xs):
    return '[' + ', '.join(xs) + ']'


class Emit:
    """collects definitions (text, bytes) and packs them into segment modules"""

    def __init__(s, name, cos):
        s.name, s.defs = name, []
        s.co = {k: 'k%d' % i for i, k in enumerate(cos)}

    def add(s, nm, typ, body):
        s.defs.append('noncomputable def %s : %s := %s' % (nm, typ, body))

    def lst(s, nm, typ, items, fmt, per=PER, nested=False):
        """`nm : List typ` as a concatenation of literals of `per` items; nested=True: `nm : List (List typ)`"""
        parts = []
        for i in range(0, max(len(items), 1), per):
            pn = '%s_%d' % (nm, i // per)
            parts.append(pn)
            s.add(pn, 'List (%s)' % typ, ll(map(fmt, items[i:i + per])))
        if nested:
            s.add(nm, 'List (List (%s))' % typ, ll(parts))
        else:
            s.add(nm, 'List (%s)' % typ, ' ++ ('.join(parts) + ')' * (len(parts) - 1))      # right-nested appends

    def trie(s, nm, vals, d, low=8):
        """`nm : SSC.Trie` of depth d (key bit 0 first: left = even keys), leaf i = vals[i], 0 beyond; literals of
        2^low leaves named nm_<i>.  Returns the list of subtries at every depth (for the split table check)."""
        vals = list(vals) + [0] * ((1 << d) - len(vals))
        cnt = [0]

        def lit(vs):
            return '.leaf %d' % vs[0] if len(vs) == 1 else '.node (%s) (%s)' % (lit(vs[0::2]), lit(vs[1::2]))

        def go(vs, depth, path):
            if depth <= low:
                pn = '%s_%d' % (nm, cnt[0])
                cnt[0] += 1
                s.add(pn, 'SSC.Trie', lit(vs))
                return pn
            l, r = go(vs[0::2], depth - 1, path + '0'), go(vs[1::2], depth - 1, path + '1')
            pn = nm if not path else '%s_n%s' % (nm, path)
            s.add(pn, 'SSC.Trie', '.node %s %s' % (l, r))
            return pn
        root = go(vals, d, '')
        if root != nm:
            s.add(nm, 'SSC.Trie', root)

    def cf(s, k):
        return s.co[k]

    def gate(s, g):
        pr = lambda x: '(%d, %s)' % (x[0], s.co[x[1]])
        if g[0] == 'out':
            return '.out %d %d %s %s' % (g[1], g[2], ll(map(pr, g[3])), ll(map(str, g[4])))
        return '.inn %d %d %s' % (g[1], g[2], ll(map(pr, g[3])))

    def modules(s, seg):
        mods, cur, size = [], [], 0
        for d in s.defs:
            if cur and size + len(d) > seg:
                mods.append(cur)
                cur, size = [], 0
            cur.append(d)
            size += len(d)
        return mods + [cur]


def coefs(D):
    cs = []
    def see(k):
        if k not in cs:
            cs.append(k)
    for g in D['A'] + D['B']:
        for _, k in g[3]:
            see(k)
    if D['scat'][0] == 'star':
        see(D['scat'][1]), see(D['scat'][2])
    else:
        for row in D['scat'][1]:
            for _, k in row:
                see(k)
    return cs


def data(D, M, name, opt):
    E = Emit(name, coefs(D))
    for k, nm in E.co.items():
        E.add(nm, 'Co', '⟨%s, %d, %d⟩' % ('true' if k[0] else 'false', k[1], k[2]))
    num, pair = str, lambda x: '(%d, %d)' % x
    E.lst('ports', 'Nat', D['ports'], num)
    E.lst('start', 'Nat', D['start'], num)
    E.lst('final', 'Nat', D['final'], num)
    E.lst('ret', 'Nat × Nat', D['ret'], pair)
    E.lst('ext', 'Nat × Nat', D['ext'], pair)
    if D['scat'][0] == 'star':
        E.add('scat', 'Scat', '.star %s %s' % (E.cf(D['scat'][1]), E.cf(D['scat'][2])))
    else:
        E.lst('scatRows', 'List (Nat × Co)', D['scat'][1], lambda r: ll('(%d, %s)' % (k, E.cf(c)) for k, c in r), per=60)
        E.add('scat', 'Scat', '.table scatRows')
    E.lst('obase', 'List Nat', [obase(p, D['h']) for p in D['ports']], lambda b: ll(map(str, b)), per=60)
    if opt.get('frames') == '1':
        E.lst('frames', 'List Nat', D['frames'], lambda f: ll(map(str, f)), per=150, nested=True)
    else:
        E.add('frames', 'List (List (List Nat))', '[]')
    # replay segments = the chunks of raw.A / raw.B (gx-labels: a cut state between two chunks)
    G, nA, cuts, L = D['A'] + D['B'], len(D['A']), M['cuts'], M['lab']
    ch = {'A': [], 'B': []}
    for i, (a, b) in enumerate(zip(cuts, cuts[1:])):
        E.lst('seg%d' % i, 'Gate', G[a:b], E.gate, per=150)
        E.lst('rs%d' % i, 'Nat', L['rs'][i], num)
        ch['A' if b <= nA else 'B'].append('seg%d' % i)
    E.add('gA', 'List (List Gate)', ll(ch['A']))
    E.add('gB', 'List (List Gate)', ll(ch['B']))
    E.lst('fins', 'Gate', L['fins'], E.gate, per=150)
    E.lst('rF', 'Nat', L['rF'], num)
    E.add('pairs', 'List (List (Nat × Nat))', '[]')
    E.add('cuts', 'List (Nat × List Nat)', '[]')
    # gx-labels: frame table as codes, register states as tries
    h, n = D['h'], 2 * D['v'] + D['R']
    dF, d = bits(len(D['frames'])), bits(n)
    ts = min(int(opt.get('tsplit', gu.TSPLIT)), max(0, dF - 2))
    E.trie('tab', [gb.code(h, f) for f in D['frames']], dF, low=min(8, dF - ts - 1))
    for i, st in enumerate(M['states'] + [D['final']]):
        E.trie('st%d' % i, st, d)
    return E, dict(dF=dF, d=d, nseg=len(cuts) - 1, nsegA=len(ch['A']), K=h * L['most'], ts=ts)


def bits(n):
    d = 0
    while (1 << d) < n:
        d += 1
    return d


HEAD = '''/-! gcert/1 certificate `%(name)s` (h = %(h)d, v = %(v)d ports, R = %(R)d slots, N = %(N)d unit moves): %(what)s.
Source: %(src)s.  Generated by checks/wht26/gx-data/py/gxgen.py (do not edit). -/
set_option maxRecDepth 100000
'''


def write_data(D, M, name, src, out, opt):
    E, npc = data(D, M, name, opt)
    E.npc = npc
    mods = E.modules(int(opt.get('seg', SEG)))
    d = '%s/Gen/%s' % (out, name)
    os.makedirs(d, exist_ok=True)
    base = out[len(ROOT):].replace('/', '.')
    info = dict(name=name, h=D['h'], v=D['v'], R=D['R'], N=D['N'], src=src)
    sizes = []
    for i, m in enumerate(mods):
        imp = 'import Work.GCert.Data.Raw\nimport Work.SharedSumChecker.Check\n' + ('import %s.Gen.%s.S%d\n' % (base, name, i - 1) if i else '')
        txt = imp + HEAD % dict(info, what='data segment %d of %d' % (i, len(mods))) + \
            'namespace GXD.%s\nopen GXD\n' % name + '\n'.join(m) + '\nend GXD.%s\n' % name
        open('%s/S%d.lean' % (d, i), 'w').write(txt)
        sizes.append(len(txt.encode()))
    txt = ('import %s.Gen.%s.S%d\n' % (base, name, len(mods) - 1) + HEAD % dict(info, what='the record `raw : GXD.Raw`') +
           'namespace GXD.%s\nopen GXD\n/-- the certificate -/\nnoncomputable def raw : Raw :=\n' % name +
           '  { h := %d, v := %d, R := %d, N := %d, cst := %d, ports := ports, frames := frames, start := start,\n'
           '    final := final, ret := ret, scat := scat, A := gA, B := gB, pairs := pairs, cuts := cuts, ext := ext,\n'
           '    obase := obase }\n' % (D['h'], D['v'], D['R'], D['N'], D['cst']) + 'end GXD.%s\n' % name)
    open('%s/Gen/%s.lean' % (out, name), 'w').write(txt)
    return ['%s.Gen.%s.S%d' % (base, name, i) for i in range(len(mods))] + ['%s.Gen.%s' % (base, name)], sizes, npc


def main():
    path, name = sys.argv[1], sys.argv[2]
    opt = dict(a.split('=') for a in sys.argv[3:] if '=' in a)
    out = opt.get('out', ROOT + 'Work/GCert/Data').rstrip('/')
    D = gc.normal(gc.load(path))
    plan = gu.plan(D, opt)
    try:
        M = gc.mirror(D, gmax=plan['gseg'], batches=plan['batches'])
    except gc.Reject as e:
        print('REJECTED by the Python mirror (nothing written):', e)
        sys.exit(2)
    print('%s: mirror accepts; h=%d v=%d R=%d N=%d; pairs=%d; replay segments=%d; scalar batches=%d'
          % (name, D['h'], D['v'], D['R'], D['N'], len(M['pairs']), len(M['visits']), len(M['scal']['batches'])))
    if 'mirror-only' in sys.argv:
        return
    src = os.path.basename(path)
    mods, sizes, npc = write_data(D, M, name, src, out, opt)
    S = gb.spar(D, path)
    chk = gb.write_checks(D, M, name, src, out, npc, S, plan)
    hist = gb.write_hist(D, M, name, src, out, npc)
    price = gb.write_price(D, M, name, src, out, npc)
    cert, scalok = gb.write_cert(D, M, name, src, out, chk, npc)
    info = dict(name=name, src=path, h=D['h'], v=D['v'], R=D['R'], N=D['N'], cst=D['cst'], nc=len(D['ret']),
                hist={str(r): n for r, n in M['hist'].items()}, H={k: {str(r): n for r, n in w.items()} for k, w in M['H'].items()},
                data_modules=mods, data_bytes=sizes, check_modules=chk, hist_module=hist, price_module=price, cert_module=cert, scalok_module=scalok,
                spar=S, lab=npc, cuts=M['cuts'], visits=M['visits'], batches=M['scal']['batches'], per_batch=M['scal']['per_batch'])
    json.dump(info, open(MY + 'logs/gen-%s.json' % name, 'w'), indent=1)
    print('wrote %d data modules (%s bytes), %d check modules, %s, %s' % (len(mods), sizes, len(chk), hist, cert))
    print('build order: ' + ' '.join(mods + [c[0] for c in chk] + [hist, price, cert, scalok]))


if __name__ == '__main__':
    main()
