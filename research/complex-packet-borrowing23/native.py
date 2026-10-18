"""Rebuild a coded cell and its direct control inside the pinned native word.

Apache-2.0. NeoKazuya, with substantial OpenAI Codex assistance.
The constructor and auditor retain their upstream attribution (see NOTICE.md).
Run through verify.py, which checks pins and enables inherited assertions.
"""
import contextlib
import io
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONSTRUCTOR = "research/complex-k492-owner-repair/code/construct_k_triangle.py"
AUDITOR = "research/complex-sw4-frame8/local/hpe_audit_and_transport.py"
INPUTS = "research/direct-delivery504-global/inputs/hamming"
SCHEDULE = "research/complex-k492-owner-repair/data/TRI-SCHEDULE.json"
ROUTING = ("research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/"
           "complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz")


def rebuild_and_audit(geometry, work):
    if not __debug__:
        raise RuntimeError("inherited constructor and auditor require assertions")
    cell = next(c for c in geometry["cases"] if [c["pair"], c["sign"]] == geometry["selected"])
    assert geometry["selected"] == [[6, 7], 1]
    assert [[Fraction(q) for q in row] for row in cell["coefficients"]] == [
        [Fraction(i != j) for j in range(6)] for i in range(6)]
    witness = json.loads((HERE / "CODED-CELL.json").read_bytes())
    schedule = json.loads((ROOT / SCHEDULE).read_bytes())
    reads = []
    for target in cell["targets"]:
        own = next(s for s in cell["leavers"] if s["raw120_register"] == target["own_register"])
        reads.append([target["port112_index"], own["block"], own["local_register"]])
    # These six entries declare delayed own reads; the replacement below emits
    # every actual read from the independently replayed circuit fixture.
    schedule["triangles"].append({"p": [6, 7], "e": 1, "reads": reads, "coded": True})
    schedule_path = work / "coded-schedule.json"
    schedule_path.write_text(json.dumps(schedule, indent=2) + "\n", encoding="utf-8")
    bindings = {f"x{i}": ("source", s["block"], s["local_register"])
                for i, s in enumerate(cell["leavers"])}
    bindings.update({f"y{i}": ("target", t["root_index"]) for i, t in enumerate(cell["targets"])})
    source = (ROOT / CONSTRUCTOR).read_text(encoding="utf-8")

    def replace(old, new):
        nonlocal source
        assert source.count(old) == 1, ("constructor recipe no longer unique", old)
        source = source.replace(old, new)

    # The fifth raw triangle removes three packet copies; reserve one of those
    # slots for our helper. Its baseline counterpart is present but stays idle.
    replace("NH=504-3*len(FULLT)+len(COPYL)", "NH=504-3*len(FULLT)+len(COPYL)+1")
    replace("tri_join_counts=Counter()",
            "tri_join_counts=Counter()\ncoded_shadow_slot=None\ncoded_target_edges=[]")
    insertion = '''    if tr.get('coded'):
        aux=len(cur);cur.append(());rows.append({})
        coded_shadow_slot=len(shadow);shadow.append(None)
        bindings={}
        for name,binding in CODED_BINDINGS.items():
            bindings[name]=maps[tuple(binding[1])][binding[2]] if binding[0]=='source' else v+binding[1]
        bindings['h0']=aux
        for tn,sn,q in CODED_CORE:
            target,source=bindings[tn],bindings[sn]
            F=basis(cur[target]+cur[source])
            for register in (target,source):
                if v<=register<2*v:assert inside(F,hyper(P[register-v])),('coded frame',register,F)
            add(target,source,q,F)
            if sn.startswith('y'):coded_target_edges.append((target,source,Q(q)))
        continue
'''
    replace("for tr in TRI['triangles']:\n    p,eps=tuple(tr['p']),tr['e']",
            "for tr in TRI['triangles']:\n" + insertion + "    p,eps=tuple(tr['p']),tr['e']")
    replace("        if tuple(key) in FULLT:skip();continue", '''        if tuple(key) in FULLT:
            if tuple(key)==((6,7),1) and shadow[coded_shadow_slot] is None:
                shadow[coded_shadow_slot]=nxt[0];nxt[0]+=1
            else:skip()
            continue''')
    # Invert the extra target basis in both the input precondition and center
    # scatter. Helper dirt compensation is recomputed by the separate auditor.
    replace("for r in range(len(cur)):climb(r,hyper(P[r-v]) if v<=r<2*v else FULL)",
            '''for target,source,q in reversed(coded_target_edges):
    scatter[target-v]=[a-q*b for a,b in zip(scatter[target-v],scatter[source-v])]
    precondition.append(['add',target,source,-q.numerator,q.denominator,[]])
for r in range(len(cur)):climb(r,hyper(P[r-v]) if v<=r<2*v else FULL)''')
    audit = runpy.run_path(str(ROOT / AUDITOR))["run"]
    results = {}
    for label, core in (("coded", witness["core"]), ("same_stock_direct", witness["direct"])):
        raw, checked = work / (label + "-raw"), work / (label + "-audit")
        old_argv = sys.argv[:]
        try:
            sys.argv = [str(ROOT / CONSTRUCTOR), str(ROOT / INPUTS), str(raw), str(schedule_path)]
            namespace = {"__name__": "__main__", "__file__": str(ROOT / CONSTRUCTOR),
                         "CODED_BINDINGS": bindings, "CODED_CORE": core}
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(source, str(ROOT / CONSTRUCTOR), "exec"), namespace)
                audit(raw / "FULL-WORD.json.gz", ROOT / ROUTING, checked)
        finally:
            sys.argv = old_argv
        receipt = json.loads((checked / "SCALAR-FRAME-AUDIT.json").read_bytes())
        assert receipt["status"] == "PASS_CHANGED_WORD_ALL_COLUMNS_AND_NATIVE_FRAMES"
        assert receipt["helpers"] == 490 and receipt["live_columns_each_orientation"] == 714
        assert receipt["widths"] == [9] * 490
        # Discard elapsed time only; every mathematical receipt field is retained.
        receipt.pop("seconds")
        receipt["helper_widths"] = {"9": len(receipt.pop("widths"))}
        results[label] = receipt
    delta = Counter({int(k): v for k, v in results["coded"]["local_profile"].items()})
    delta.subtract({int(k): v for k, v in results["same_stock_direct"]["local_profile"].items()})
    delta = {str(k): v for k, v in sorted(delta.items()) if v}
    assert delta == {"1": -16, "2": 5, "3": 5, "9": -1}, delta
    assert results["coded"]["local_rank_mass"] == results["same_stock_direct"]["local_rank_mass"] == 6266
    results["coded_minus_direct_profile"] = delta
    return results
