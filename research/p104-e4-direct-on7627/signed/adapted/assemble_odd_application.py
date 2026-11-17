"""Join disjoint native-catalogue certificates to the exact 8+9 application."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
import json

root=Path(__file__).resolve().parent
def read(name):
    return json.loads((root/name).read_bytes())
word=root.parent/"WORD.json.gz"
word_sha=sha256(word.read_bytes()).hexdigest()
binding=read("ODD-PHYSICAL-BINDING.json")
b=binding["occurrence_and_geometry"]
precision=read("ODD-PRECISION.json")
partial=read("ODD-ADMISSION-PARTIAL.json")
f=read("ODD-FIXED-TAPE-COUNTS.json")
g=partial["compiler_outer"]
replay=read("ODD-TYPE-AB-REPLAY.json")
assert not replay["replay"]["bad_outputs"]
grid=read("ODD-CALLER-EXACT-GRID.json")
assert grid["caller_sha256"]==replay["caller_sha256"] and int(grid["caller_odd_scale"])>1
assert f["caller_odd_scale"]==int(grid["caller_odd_scale"]) and partial["ordinary"]["charged_caller_odd_conversions"]>0
assert all(r["caller_sha256"]==replay["caller_sha256"] for r in (binding,precision,partial,f))
catalogue=[]
for path in sorted(root.glob("SHORT-CATALOGUE-*-*.log")):
    text=path.read_text()
    p=text.find("\n{")
    assert p>=0,path
    c=json.loads(text[p:])
    assert c["word_sha256"]==word_sha and c["status"]=="PASS_CURRENT_NATIVE_CATALOGUE_SLICE"
    assert c["checked_maps"]==c["slice_stop"]-c["slice_start"] and c["phase_control_rejected"]
    catalogue.append(c|{"log_sha256":sha256(path.read_bytes()).hexdigest()})
catalogue.sort(key=lambda c:c["slice_start"])
assert catalogue and catalogue[0]["slice_start"]==0
assert all(a["slice_stop"]==b["slice_start"] for a,b in zip(catalogue,catalogue[1:]))
assert len({c["catalogue_digest"] for c in catalogue})==1
size=catalogue[-1]["catalogue_size"]
assert all(c["catalogue_size"]==size for c in catalogue)
assert catalogue[-1]["slice_stop"]==size==sum(c["checked_maps"] for c in catalogue)
assert sum(c["main_boundary_pairs"] for c in catalogue)==104
assert binding["aliased_main_rejected"]
assert b["native_calls"]==17 and b["rank_surplus"]>0
assert b["paid_positions"]==sum(partial["invoice"]["P"].values())
assert b["productive_fields"]==sum(partial["invoice"]["T"].values())
assert Q(g["claim"])<Q(g["tested"])<Q(g["raw_bracket"][0]) and Q(g["outer"]["minimum_margin"])>0
assert f["context_c"]==precision["context_c"] and f["context_bound_bits"]<f["H"]
assert partial["finite_rank9_fields"] and {r["width"] for r in partial["finite_rank9_fields"]}=={1,2,3}
with (root/"ODD-8X9-APPLICATION-CHECKS.json").open("x") as f:
    json.dump({"status":"PASS_8X9_EXACT_COMPONENT_APPLICATION_CHECKS",
               "candidate":g["claim"],"caller_sha256":replay["caller_sha256"],
               "native_canonical_sha256":replay["source_word_sha256"],"native_archive_sha256":word_sha,
               "catalogue":catalogue,"physical_binding":b,"fixed_tape_counts":read("ODD-FIXED-TAPE-COUNTS.json"),
               "source_unit_ordinary":partial["ordinary"],"numeric_gate":g,
               "assumptions":["native_all_columns","owned_erasure","compiler","precision_tape","analytic_recovery"],
               "scope":"Conditional component application to the exact 8+9 source with the selected completed BIT predecessor and inherited five assumptions. Checks every normalized endpoint, every paid/helper nested chart map up to exact signed Pauli and absolute phase, caller occurrence/phase, precision, finite scalar and route bounds, and numeric gates. Does not run a compiled Turing machine, select an upstream frontier, or claim human/formal review."},f,indent=2)
print("PASS complete 8+9 component application checks",g["claim"],size,b["paid_positions"],flush=True)
