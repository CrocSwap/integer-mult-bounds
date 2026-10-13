# Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0.
"""Parameterise PR #510's nine-stage chain (PR #463's global_k / audit_parent_k / emit_k / audit_hosted_k and PR #510's
assemble9) for a word with v <= 120 live ports and nine totals of any copy rank, the way PR #545's code/adapt.py
parameterises PR #493's eleven-stage chain.  Every change is an exact string edit of a vendored file (each anchor must
occur exactly once); nothing is read from the environment.  V comes from the word (global_k) or the parent GLOBAL.json;
the decoder constant CST (the sum of the nine COPY ranks) is replayed from the records (global_k, audit_parent_k) or
from the template's local programs, which the parent audit checks against the records (emit_k, audit_hosted_k); the
assembly reads the rank-mass deficit T (2 K v - L CST) from the hosted audit and checks that it fits nine copy ranks.
For v = 120 and nine rank-8 totals every adapted script computes what the vendored one computes.
usage: adapt9p.py VENDORED_CODE_DIR (e8-r715-eleven-stage-whole/code) PR510_CODE_DIR (e8-r480-nine-stage/code)
                  AUDIT_PARENT_K (PR #510's adapted copy) OUTDIR"""
import sys
from pathlib import Path

code, c510, apk, out = (Path(x).resolve() for x in sys.argv[1:5])
EDITS = {
    'global_k.py': (code / 'global_k.py', [
        ("sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../e8-r740-replica32/code'))",
         "sys.path.insert(0, %r); sys.path.insert(0, %r)" % (str(code.parents[1] / 'e8-r740-replica32/code'), str(code))),
        ("    DEFICIT=T*(2*K*120-9*H*L)\n", "    DEFICIT=None   # T*(2*K*V-L*CST), set after the local replay gives CST\n"),
        ("    assert (w['h'],V,w['form'])==(8,120,'<x,y>/2')",
         "    assert (w['h'],w['form'])==(8,'<x,y>/2') and 100<=V<=120"),
        ("    streams={}; checks={}; localH=None\n", "    streams={}; checks={}; localH=None; CSTD=[]\n"),
        ("norm=[1]*LOCAL+[0]; maxnorm=1; center=None; hist=Counter(); events=[]; copies=0; adds=0\n",
         "norm=[1]*LOCAL+[0]; maxnorm=1; center=None; hist=Counter(); events=[]; copies=0; adds=0; crs=[]\n"),
        ("copy_rank=abs(dim(c)-dim(f)); assert copy_rank==8", "copy_rank=abs(dim(c)-dim(f)); assert 0<copy_rank<=H"),
        ("hist[copy_rank]+=1; copies+=1; events.append", "hist[copy_rank]+=1; copies+=1; crs.append(copy_rank); events.append"),
        ("        assert center is None and copies==9 and adds==ADDS\n",
         "        assert center is None and copies==9 and adds==ADDS; CSTD.append(sum(crs))\n"),
        ("    assert sum(r*n for r,n in localH.items())==H*R-ENT+72+2*V*(H-1)\n",
         "    assert CSTD[0]==CSTD[1]; CST=CSTD[0]; DEFICIT=T*(2*K*V-L*CST)   # the records' COPY ranks\n"
         "    assert sum(r*n for r,n in localH.items())==H*R-ENT+CST+2*V*(H-1)\n"),
        ("data_route='owner (replica*%d + (2*pair+side)*120+port, d*rho_stage,port)'%(2*K*V)",
         "data_route='owner (replica*%d + (2*pair+side)*%d+port, d*rho_stage,port)'%(2*K*V,V)"),
    ]),
    'audit_parent_k.py': (apk, [
        ("    assert V==120\n    DEFICIT=T*(2*K*V-9*8*L)\n", "    assert 100<=V<=120\n"),
        ("    assert t['local_programs']==expected\n",
         "    assert t['local_programs']==expected\n"
         "    CST=sum(e[5] for e in expected['forward'] if e[0]==2); assert CST==sum(e[5] for e in expected['reverse'] if e[0]==2)\n"
         "    DEFICIT=T*(2*K*V-L*CST)   # CST: the nine COPY ranks of the records\n"),
        ("assert family==rep*(2*K*V)+(2*p+side)*120+i%120 and route==['data',st,i%120]",
         "assert family==rep*(2*K*V)+(2*p+side)*V+i%V and route==['data',st,i%V]"),
        ("lambda q:q['calls'][0]['owners'].__setitem__(241,q['calls'][0]['owners'][240])",
         "lambda q:q['calls'][0]['owners'].__setitem__(2*V+1,q['calls'][0]['owners'][2*V])"),
        ("lambda q:q['calls'][0]['owners'][240][1].__setitem__(3,-1)", "lambda q:q['calls'][0]['owners'][2*V][1].__setitem__(3,-1)"),
    ]),
    'emit_k.py': (code / 'emit_k.py', [
        ("HERE = Path(__file__).resolve().parent\n", "HERE = Path(%r)\n" % str(code)),
        ("H, V = 8, 120\n", "H, V = 8, None   # V: the parent GLOBAL.json\n"),
        ("    L, T, M, R = t['stages'], t['replicas'], t['m'], g['R']; K = (L - 1) // 2; DATA = 2 * K * V * T\n"
         "    assert M == 1 + 7 * L and g['v'] == V and L % 2 == 1\n"
         "    DEFICIT = T * (2 * K * V - 9 * H * L)\n",
         "    global V\n    V = g['v']\n"
         "    L, T, M, R = t['stages'], t['replicas'], t['m'], g['R']; K = (L - 1) // 2; DATA = 2 * K * V * T\n"
         "    assert M == 1 + 7 * L and 100 <= V <= 120 and L % 2 == 1\n"
         "    CST = sum(z[5] for z in t['local_programs']['forward'] if z[0] == 2)\n"
         "    assert CST == sum(z[5] for z in t['local_programs']['reverse'] if z[0] == 2)\n"
         "    DEFICIT = T * (2 * K * V - L * CST)\n"),
        ("'projector of data family r*%d+(2*pair+side)*120+port (copy = side*120+port); s lies strictly between '",
         "'projector of data family r*%d+(2*pair+side)*%d+port (copy = side*%d+port); s lies strictly between '"),
        ("'the last local/bridge touch of that pair and the child; the child keeps the remaining coordinates.' % (2 * K * V)),",
         "'the last local/bridge touch of that pair and the child; the child keeps the remaining coordinates.' % (2 * K * V, V, V)),"),
    ]),
    'audit_hosted_k.py': (code / 'audit_hosted_k.py', [
        ("V=120\n", "V=CST=None   # set in main(): V from the parent GLOBAL.json, CST from the parent template's local programs\n"),
        ("DATA=2*K*V*T; DEFICIT=T*(2*K*V-9*8*L)", "DATA=2*K*V*T; DEFICIT=T*(2*K*V-L*CST)"),
        ("def main():\n    par,bd,out=", "def main():\n    global V,CST\n    par,bd,out="),
        ("    t=template(bd/'GLOBAL-TEMPLATE.json.gz');g=read(bd/'GLOBAL.json');pg=read(par/'nine/GLOBAL.json')\n",
         "    t=template(bd/'GLOBAL-TEMPLATE.json.gz');g=read(bd/'GLOBAL.json');pg=read(par/'nine/GLOBAL.json')\n"
         "    V=pg['v'];CST=sum(z[5] for z in pt['local_programs']['forward'] if z[0]==2)\n"
         "    assert 100<=V<=120 and CST==sum(z[5] for z in pt['local_programs']['reverse'] if z[0]==2)\n"),
        ("    DEFICIT=T*(2*K*V-9*8*L)\n", "    DEFICIT=T*(2*K*V-L*CST)\n"),
    ]),
    'assemble9.py': (c510 / 'assemble9.py', [
        ("T, R, V = pg['replicas'], pg['R'], 120;", "T, R, V = pg['replicas'], pg['R'], pg['v'];"),
        ("DEPTH = bg['halving_depth']; DEFICIT = T * (2 * K * V - 9 * 8 * L)",
         "DEPTH = bg['halving_depth']; DEFICIT = audit['deficit']   # T (2 K v - L CST), CST replayed by the audits\n"
         "CST, rem = divmod(2 * K * V - DEFICIT // T, L); assert rem == 0 and DEFICIT % T == 0 and 9 <= CST <= 72"),
    ]),
}
out.mkdir(parents=True, exist_ok=True)
n = 0
for dst, (src, edits) in EDITS.items():
    text = src.read_text()
    for old, new in edits:
        assert text.count(old) == 1, (dst, old, text.count(old))
        text = text.replace(old, new)
        n += 1
    (out / dst).write_text("# Adapted from PR #510's vendored %s by research/e8-bit-p111/code/adapt9p.py. Apache-2.0.\n"
                           % src.name + text)
print('   adapted %d nine-stage files with %d listed edits (each anchor found exactly once)' % (len(EDITS), n))
