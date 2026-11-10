"""Fresh exact-grid and defect bounds for the shortened caller."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from types import ModuleType
import gzip
import json
import sys

root=Path(__file__).resolve().parent
vendor=root/"admission-source"
manifest=json.loads((vendor/"INDEPENDENT-SOURCES.json").read_bytes())
for e in manifest["files"]:
    if e["path"].startswith("retained/"):
        assert sha256((vendor/e["path"]).read_bytes()).hexdigest()==e["sha256"],e["path"]
from signed_model import module
bind=vendor/"retained/query-only-precision-envelope"
binding=module("source_binding",bind/"source_binding.py")
grid=module("short_grid",vendor/"retained/odd-native-common-grid/independent_bounds.py",(
    ('elif op != "IDLE_ONE":','elif op not in ("IDLE_ONE", "IDLE_ODD"):'),
))
envpath=bind/"envelopes.py"
s=envpath.read_text()
def patch(a,b,expected=1):
    global s
    assert s.count(a)==expected,(a,s.count(a))
    s=s.replace(a,b)
patch('elif op in ("LAMBDA", "IDLE_ONE"):','elif op in ("LAMBDA", "IDLE_ONE", "IDLE_ODD"):',2)
patch('all(0 <= r < 38 for r in ar) and all(38 <= r < 76 for r in br[:2])',
      'all(caller["types"]["A"]["offset"] <= r < caller["types"]["A"]["offset"] + caller["types"]["A"]["roles"] for r in ar) and all(caller["types"]["B"]["offset"] <= r < caller["types"]["B"]["offset"] + caller["types"]["B"]["roles"] for r in br[:2])')
patch('all(1 <= k <= 18 for k in e[3])','all(1 <= k <= caller["stages"] for k in e[3])')
patch('need(j_order == list(range(1, 19)), "exact eighteen native calls")',
      'need(j_order == list(range(1, caller["stages"] + 1)), "all chronological native calls")')
patch('word["public"] - len(mains) == 1061','word["public"] - len(mains) == expected_helper_count')
patch('physical_main_inputs=3952, fresh_arbitrary_helpers=18 * 1061,',
      'physical_main_inputs=sum(t["roles"] * len(t["ports"]) for t in caller["types"].values()), fresh_arbitrary_helpers=caller["stages"] * expected_helper_count,')
patch('need(len(e[3]) == len(set(e[3]))','need(op != "IDLE_ODD" or (len(e[3]) == 1 and e[4] == -1), "signed child signature")\n                    need(len(e[3]) == len(set(e[3]))')
env=ModuleType("short_envelope")
env.__file__=str(envpath)
sys.modules[env.__name__]=env
cpath=root/"ODD-TYPE-AB-CALLER.json"
c=json.loads(cpath.read_bytes())
r=json.loads((root.parent/"RESULT.json").read_text())
w=json.loads(gzip.decompress((root.parent/"WORD.json.gz").read_bytes()))
sha=sha256(json.dumps(w,sort_keys=True,separators=(",",":")).encode()).hexdigest()
assert sha==r["word_canonical_sha256"]
assert abs(Q(c["types"]["A"]["alpha2"]))==1
env.expected_helper_count=sum(r["native"]["helpers"].values())
exec(compile(s,str(envpath),"exec"),env.__dict__)
previous=json.loads((root/"SHORT-PRECISION.json").read_text())
grid_receipt=json.loads((root/"ODD-CALLER-EXACT-GRID.json").read_text())
assert previous["native_sha256"]==sha and grid_receipt["caller_sha256"]==sha256(cpath.read_bytes()).hexdigest()
wg=previous["native_grid"]
wr=previous["rounded_native"]
wp={key:(Q(v["exact"]),v["witness"]) for key,v in wr["bounds"].items()}
cp,cr=env.caller_envelope(c,wp,w)
cg=grid_receipt
odd=cg["caller_odd_scale_bits"]
height=cg["grid_exponents"][0]+wg["dyadic_height"]
mass=binding.strict_power(cp["M_context"][0])+odd+(1125).bit_length()
record={"native_sha256":sha,"caller_sha256":sha256(cpath.read_bytes()).hexdigest(),
        "native_grid":wg,"caller_grid":cg,"context_height":height,"context_mass_bits":mass,
        "context_c":2*max(height,mass),"rounded_native":wr,"rounded_caller":cr,
        "precision_program_sha256":sha256(s.encode()).hexdigest(),
        "scope":"Fixed integer Laurent grid with charged odd caller scale, and pinned attributed forward/adjoint all-fibre defect engine applied to the emitted 17-stage caller. Each LAMBDA, QUERY and signed/unsigned idle is one unitary with one child defect. The caller allocation assumes independent stage helpers. Full physical application remains separate."}
with (root/"ODD-PRECISION.json").open("x") as f:json.dump(record,f,indent=2)
print("PASS short precision",height,mass,record["context_c"],flush=True)
