# Parameterises PR #493's hosted-bit chain (emit, audit, local audit, assembly, hosting nominator, the two geometries,
# the independent checker and one record mutant) for a word with v <= 120 live ports and nine totals of any copy rank.
# Every change is an exact string edit of a pinned parent file; each anchor must occur exactly the listed number of
# times.  Nothing is read from the environment: V, R and the sum of the nine copy ranks come from the word, or, in
# scripts that never see the word, from the exported records.  For v = 120 and nine rank-8 totals (PR #493, PR #503)
# every adapted script computes exactly what the parent computes (verify.py, step 7, compares the outputs byte for byte).
# Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; the parent files are PR #493's / #472's. Apache-2.0.
"""usage: adapt.py PARENT_PACKAGE WORD.json.gz OUTDIR
   OUTDIR/emit.py, audit.py, local_audit.py, assemble.py, host_select.py, nine_geometry.py, eleven_geometry.py
   OUTDIR/chk/checkword.py (+ relax.py)  the pinned independent checker with ONE assertion changed (v == 120 -> v <= 120)
   OUTDIR/mutate_records.py              the record mutants, the 'cheaper COPY rank' one made relative to the true rank
   WORD is baked into local_audit.py (the word whose records are audited), as PR #503's adapt.py does."""
import sys
from pathlib import Path

PARENT, WORD, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
HERE = Path(__file__).resolve().parent                    # punct_cfg.py lives here
H_EMIT = str(PARENT / 'code/hub/e8-r740-replica32/code'); H_HOST = str(PARENT / 'code/hub/idle-axis-hosting')
PKG = str(PARENT)
PC = "sys.path.insert(0,%r)\nimport punct_cfg as PC\n" % str(HERE)

# (anchor, replacement[, expected count])
EDITS = {
    'code/eleven/emit.py': ('emit.py', [
        ('sys.path.insert(0,str(HERE.parent/"hub/e8-r740-replica32/code"))\n', "sys.path.insert(0,%r)\n" % H_EMIT),
        ('sys.path.insert(0,str(HERE.parent/"hub/idle-axis-hosting"))\n', "sys.path.insert(0,%r)\n" % H_HOST),
        ("import hosting_core as HC\n\nH,L,K,T,M=8,11,5,8,78\n", "import hosting_core as HC\n" + PC + "\nH,L,K,T,M=8,11,5,8,78\n"),
        # V is the word's port count (a punctured word carries its live labels in ports_geom); config from the word
        ("    assert (w['h'],V,w['form'])==(8,120,'<x,y>/2')\n",
         "    assert (w['h'],w['form'])==(8,'<x,y>/2'); CFG=PC.config(w,%r); assert (CFG['v'],CFG['R'])==(V,R)\n" % PKG),
        # the COPY rank of a total is the dimension of its frame (8 for #493 / #503, 7 for the star unit); the sum is derived
        ("    streams={}; checks={}; localH=None\n", "    streams={}; checks={}; localH=None; CSTD=[]\n"),
        ("norm=[1]*LOCAL+[0]; maxnorm=1; center=None; hist=Counter(); events=[]; copies=0; adds=0",
         "norm=[1]*LOCAL+[0]; maxnorm=1; center=None; hist=Counter(); events=[]; copies=0; adds=0; crs=[]"),
        ("copy_rank=abs(dim(c)-dim(f)); assert copy_rank==8", "copy_rank=abs(dim(c)-dim(f)); assert 0<copy_rank<=H"),
        ("hist[copy_rank]+=1; copies+=1; events.append", "hist[copy_rank]+=1; copies+=1; crs.append(copy_rank); events.append"),
        ("        assert center is None and copies==9 and adds==ADDS\n",
         "        assert center is None and copies==9 and adds==ADDS; CSTD.append(sum(crs))\n"),
        ("    assert sum(r*n for r,n in localH.items())==H*R-ENT+72+2*V*(H-1)\n",
         "    assert CSTD[0]==CSTD[1]==sum(CFG['copy_ranks']); CST=CSTD[0]   # records' COPY ranks == the word's totals map\n"
         "    assert sum(r*n for r,n in localH.items())==H*R-ENT+CST+2*V*(H-1)\n"),
        ("assert M*LIVE-mass==(2*K*V-L*72)*T", "assert M*LIVE-mass==(2*K*V-L*CST)*T"),
        ("[(rep*1200+2*d*V+port,rep*1200+2*ss*V+port),(rep*1200+(2*ss+1)*V+port,rep*1200+(2*d+1)*V+port)]",
         "[(rep*(2*K*V)+2*d*V+port,rep*(2*K*V)+2*ss*V+port),(rep*(2*K*V)+(2*ss+1)*V+port,rep*(2*K*V)+(2*d+1)*V+port)]"),
        ("data_route='owner (replica*1200 + (2*pair+side)*120+port, d*rho_stage,port)'",
         "data_route='owner (replica*%d + (2*pair+side)*%d+port, d*rho_stage,port)'%(2*K*V,V)"),
        ("rank_mass=mass,deficit=(2*K*V-L*72)*T,", "rank_mass=mass,deficit=(2*K*V-L*CST)*T,"),
    ]),
    'code/eleven/audit.py': ('audit.py', [
        ("from local_audit import local_audit\n", PC + "from local_audit import local_audit\n"),
        ("K,L,M,T,V,R=5,11,78,8,120,489\nDATA=2*K*V*T\n",
         "K,L,M,T=5,11,78,8\nV=R=DATA=CST=None   # set in main(): V ports and R helpers from the records, CST from their COPY ranks\n"),
        ("==T*(2*K*V-72*L)", "==T*(2*K*V-CST*L)"),
        ("def main():\n    par,geometry_parent,out=", "def main():\n    global V,R,DATA,CST\n    par,geometry_parent,out="),
        ("    widths=[8-fs[str(state['initial'][str(h)])]['dim'] for h in range(240,240+R)]\n",
         "    V=state['v'];R=state['n']-2*V;DATA=2*K*V*T\n"
         "    cr=lambda o:sum(z[5] for z in pt['local_programs'][o] if z[0]==2)   # the audit's own replay of the records\n"
         "    CST=cr('forward');assert CST==cr('reverse')\n"
         "    widths=[8-fs[str(state['initial'][str(h)])]['dim'] for h in range(2*V,2*V+R)]\n"),
        ("len(geo['ports'])==120", "len(geo['ports'])==V"),
        ("==(9600,9609,L*T*R,0,3264)", "==(DATA,DATA+9,L*T*R,0,T*(2*K*V-CST*L))"),
        ("lambda q:q['calls'][0]['owners'][240].__setitem__(0,q['calls'][0]['owners'][240][0]+1200)",
         "lambda q:q['calls'][0]['owners'][2*V].__setitem__(0,q['calls'][0]['owners'][2*V][0]+2*K*V)"),
        ("lambda q:q['calls'][0]['owners'][0].__setitem__(0,1200)", "lambda q:q['calls'][0]['owners'][0].__setitem__(0,2*K*V)"),
        ("lambda q:q['calls'][0]['owners'][240][1].__setitem__(2,99)", "lambda q:q['calls'][0]['owners'][2*V][1].__setitem__(2,99)"),
        ("lambda q:q['calls'][0]['owners'][240][1].__setitem__(0,'bank')", "lambda q:q['calls'][0]['owners'][2*V][1].__setitem__(0,'bank')"),
        ("live=9600,physical=9609,hosted_residuals=L*T*R", "live=DATA,physical=DATA+9,hosted_residuals=L*T*R"),
        ("deficit=3264,maxchild=max(P),geometry_routes=1320", "deficit=T*(2*K*V-CST*L),maxchild=max(P),geometry_routes=11*V"),
    ]),
    'code/eleven/local_audit.py': ('local_audit.py', [
        ("ROOT=Path(__file__).resolve().parents[2]\n", "ROOT=Path(%r)\n" % PKG + PC),
        ("cc['formal_columns_checked']==969", "cc['formal_columns_checked']==2*state['v']+state['n']"),
        ("word=json.loads(gzip.decompress((ROOT/'data/bit/bitE8mut-r489.json.gz').read_bytes()))",
         "word=PC.load(%r);assert (word['v'],word['R'])==(state['v'],state['n']-2*state['v']);PC.check_word(word,%r)" % (str(WORD), PKG)),
        ("range(729)", "range(state['n'])"),
        ("validate_isometries(iso,word['frames'],word['lines'],dims)==set(initial[240:])",
         "validate_isometries(iso,word['frames'],word['lines'],dims)==set(initial[2*state['v']:])"),
        ("rank=sum(dims[f] for f in initial[240:])", "rank=sum(dims[f] for f in initial[2*state['v']:])"),
        ("PASS_EXACT_R489_LOCAL_PROJECTORS'", "PASS_EXACT_R%d_LOCAL_PROJECTORS'%(state['n']-2*state['v'])"),
    ]),
    'code/eleven/assemble.py': ('assemble.py', [
        ("T, L, V, K = 8, 11, 120, 5\n", "T, L, V, K = 8, 11, pg['v'], 5   # the BIT port count; the cited complex suppliers carry no v\n"),
        # the rank-mass deficit comes from the audit (which derives CST from the records); it must fit nine copy ranks
        ("mass = sum(r * z for r, z in P.items()); assert m * W - mass == (2 * K * V - L * 72) * T",
         "mass = sum(r * z for r, z in P.items()); assert m * W - mass == audit['deficit']\n"
         "CST, rem = divmod(2 * K * V - audit['deficit'] // T, L); assert rem == 0 and audit['deficit'] % T == 0 and 9 <= CST <= 72"),
        # optional 6th argument: the cited-suppliers file (default: the parent's data/complex-b.json)
        ('cited = {s["name"]: s for s in json.loads((root / "data/complex-b.json").read_text())["suppliers"]}',
         'cited = {s["name"]: s for s in json.loads((Path(sys.argv[6]) if len(sys.argv) > 6 else root / "data/complex-b.json").read_text())["suppliers"]}'),
    ]),
    'discovery/host_select.py': ('host_select.py', [
        ('sys.path.insert(0, str(HERE.parent / "code" / "hub" / "idle-axis-hosting"))', "sys.path.insert(0, %r)" % H_HOST),
        ("H, L, K, T, M, V = 8, 11, 5, 8, 78, 120\n", "H, L, K, T, M = 8, 11, 5, 8, 78\n"),
        ("    R = w['R']\n", "    R = w['R']; V = w['v']\n"),
    ]),
    'code/bit/independent/checkword.py': ('chk/checkword.py', [
        ("assert len(lines)==v==120 and h==8",
         "assert len(lines)==v and 100<=v<=120 and h==8   # v live ports of the 120 E8 lines\n"
         "# the live labels must be E8 root lines: members of the 120-line system of PR #493's word (the lines PR #370's checker accepts)\n"
         "CANON={tuple(x) for l in json.load(gzip.open(%r,'rt'))['lines'] for x in (l,[-y for y in l])}\n"
         "assert all(tuple(a) in CANON for a in lines), 'a label is not one of the 120 E8 root lines'" % str(PARENT / 'data/bit/bitE8mut-r489.json.gz')),
        ("print('labels: 120 distinct lines of norm 2 (pairwise |ip| <= 1), spanning rank 8')",
         "print('labels: %d distinct lines of norm 2 (pairwise |ip| <= 1), spanning rank 8'%v)"),
    ]),
    'code/bit/mutate_records.py': ('mutate_records.py', [
        ("lambda e:e.__setitem__(5,7)", "lambda e:e.__setitem__(5,e[5]-1)"),
    ]),
}
# the geometries build every port isometry by BFS over all 120 lines; only the live ports are emitted, re-indexed 0..v-1
GEOM = lambda: [
    ("ap.add_argument('--out',type=Path,required=True); a=ap.parse_args(); t0=time.monotonic()",
     "ap.add_argument('--out',type=Path,required=True); ap.add_argument('--word',type=Path,default=None); a=ap.parse_args(); t0=time.monotonic()"),
    ("    assert len(gs)==120\n",
     "    assert len(gs)==120\n"
     "    if a.word is None: LIVE=list(range(120))\n"
     "    else:\n"
     "        ww=json.loads(gzip.decompress(a.word.read_bytes())); LIVE=list(ww['ports_geom']) if 'ports_geom' in ww else list(range(120))\n"
     "        assert len(LIVE)==ww['v'] and all(ww['lines'][i]==list(map(int,lines[p])) for i,p in enumerate(LIVE))\n"),
    ("    for t,q in enumerate(lines):\n        g=gs[t]; assert", "    for t,src in enumerate(LIVE):\n        q=lines[src]; g=gs[src]; assert"),
    ("exact_bit_endpoint_operator_checks=240,", "exact_bit_endpoint_operator_checks=2*len(LIVE),"),
    ("missing_route_factor_controls=120,", "missing_route_factor_controls=len(LIVE),"),
]
EDITS['code/nine/geometry.py'] = ('nine_geometry.py', GEOM() + [("route_checks=1080,", "route_checks=9*len(LIVE),")])
EDITS['code/hub/r740-hosted-eleven/code/geometry.py'] = ('eleven_geometry.py', GEOM() + [("route_checks=1320,", "route_checks=11*len(LIVE),")])

OUT.mkdir(parents=True, exist_ok=True); (OUT / 'chk').mkdir(exist_ok=True)
n = 0
for src, (dst, edits) in EDITS.items():
    text = (PARENT / src).read_text()
    for e in edits:
        old, new = e[0], e[1]; cnt = e[2] if len(e) > 2 else 1
        assert text.count(old) == cnt, (src, old, text.count(old))
        text = text.replace(old, new); n += 1
    (OUT / dst).write_text("# Adapted from PR #493's %s by research/e8-punctured111-star/code/adapt.py. Apache-2.0.\n" % src + text)
(OUT / 'chk/relax.py').write_bytes((PARENT / 'code/bit/independent/relax.py').read_bytes())
print('   adapted %d parent files with %d listed edits (each anchor found exactly the listed number of times)' % (len(EDITS), n))
