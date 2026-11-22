"""Count whole-field phase passes added by changing the large-copy dilation."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from pathlib import Path
import json
import sys

def phase_census(atlas):
    """Return signed, occurrence-weighted I instructions for each graph role."""
    counts = defaultdict(Counter)
    def visit(label, tape, inverse=False):
        for op in tape:
            if op[0] == "I":
                residue = ((-1 if inverse else 1) * op[1]) % 4
                counts[label][residue] += 1
    calls = [r for r in atlas.instructions() if r[0] == "NATIVE"]
    shape = tuple(map(len, atlas.regs))
    assert all(tuple(map(len, r[3])) == shape for r in calls)
    for node in atlas.graph["schedule"]:
        if node in atlas.moves:
            _, right, left = atlas.factors[atlas.moves[node]]
            visit("paid, right", right)
            visit("paid, left", left)
    for i, pair in enumerate(zip(atlas.graph["initial"],atlas.graph["final"],strict=True)):
        if i not in atlas.main:
            _, right, left = atlas.factors[pair]
            visit("helper, inverse right", right, True)
            visit("helper, inverse left", left, True)
    for p, regs in enumerate(atlas.regs):
        move, correct = atlas.contacts[p]
        for k in range(len(regs)):
            visit("main, contact", move)
            visit("main, inverse contact", move, True)
            visit("main, correction", correct)
            if k % 2 == 0:
                visit("main, producer", atlas.port[p][0])
            else:
                visit("main, consumer", atlas.port[p][1])
    # The only rank-dependent branch in a chart's phase-dispatch count
    # is I. S and CZ always issue once. Multiplicity is independent of
    # graph binding; each binding has the same count of each port parity.
    per_group = Counter()
    by_role = {}
    for label, row in sorted(counts.items()):
        per_group[label.split(",")[0]] += row[1] + row[3]
        by_role[label] = [row[x] for x in range(4)]
    return {
        "native_graphs_per_copy":len(calls),
        "main_slot_counts":dict(sorted(Counter(shape).items())),
        "graph_issued_roles":[len(atlas.moves),len(atlas.graph["initial"])-len(atlas.main),len(atlas.main)],
        "signed_I_exponents_per_graph":by_role,
        "odd_I_by_role_per_graph":dict(per_group),
        "all_copy_delta_at_residue_2":len(calls)*sum(per_group.values()),
        "all_copy_delta_at_residue_0":0,
    }

def dynamic(atlas, widths):
    # Use the unmodified chart and graph generators for one bound call.
    # A null payload charges callback invocations. These tests do not price
    # the non-phase instructions, field lengths, or the recursive child.
    from periodic import Job
    from raw48 import ComplexRaw
    class Columns:
        window = 1
        offset = suffix = 0
        def row(self, *args): pass
    class Field:
        def __init__(self, counter): self.counter = counter
        def copy(self): return Field(self.counter)
        blank = copy
        def clear(self): pass
        def retire(self): pass
        def replace(self, other): pass
        def scale(self, *args): pass
        def scale_add(self, *args): pass
        def phase(self, fn, suffix):
            self.counter["all_phase_calls"] += 1
            if fn(0) % 4:
                self.counter["nonzero_constant_at_zero"] += 1
    class Raw(ComplexRaw):
        def align(self, field, job, canonical): return ()
        def unalign(self, field, route): pass
        @staticmethod
        def axis_list(cols, axes): return range(cols * len(axes))
    clock,row = next((i,r) for i,r in enumerate(atlas.instructions()) if r[0]=="NATIVE")
    _, call, color, bound = row
    rows = {}
    for cols, bundle in widths:
        counts = Counter()
        roots={r:Field(counts) for group in bound for r in group}
        jobs = {("helper",clock,call,atlas.layout["source_labels"][i]):Job(i,())
                for i in range(len(atlas.graph["initial"])) if i not in atlas.main}
        fields = {j.owner:Field(counts) for j in jobs.values()}
        machine=Raw(atlas,fields,Columns(),low=0,bundle=bundle,slots=153*cols)
        issued=sum(1 for _ in machine.graph(clock,call,color,bound,jobs,roots,cols))
        assert issued == len(atlas.moves)
        rows[f"columns={cols},bundle={bundle}"] = dict(counts,returned_paid=issued)
    return rows

def main():
    parser=ArgumentParser()
    parser.add_argument("machine", type=Path)
    args=parser.parse_args()
    sys.path.insert(0,str(args.machine.resolve()))
    from upstream import install,HERE
    _, _, _, source=install()
    from strong_complex import artifacts
    atlas=artifacts(source/"research/grade14-native-realization", HERE/"inputs")
    report=phase_census(atlas)
    assert report["native_graphs_per_copy"]==48
    assert report["odd_I_by_role_per_graph"]=={"paid":3042,"helper":697,"main":200}
    probes=dynamic(atlas,[(2*8,1),(2*79,1),(2*79,2)])
    old,large,even_bundle=probes.values()
    assert large["all_phase_calls"]-old["all_phase_calls"]==sum(report["odd_I_by_role_per_graph"].values())
    assert large["nonzero_constant_at_zero"]==3939 and even_bundle==old
    report["one_real_graph_callbacks"] = probes
    print(json.dumps(report,indent=2))
if __name__ == "__main__": main()
