"""Substitute the exact caller counts into the reviewed finite-tape bounds."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

root=Path(__file__).resolve().parent
def read(name):
    return json.loads((root/name).read_text())
cpath=root/"ODD-TYPE-AB-CALLER.json"
caller=read(cpath.name)
partial=read("ODD-ADMISSION-PARTIAL.json")
precision=read("ODD-PRECISION.json")
binding=read("ODD-PHYSICAL-BINDING.json")
native=json.loads(gzip.decompress((root.parent/"WORD.json.gz").read_bytes()))
nhash=sha256(json.dumps(native,sort_keys=True,separators=(",",":")).encode()).hexdigest()
chash=sha256(cpath.read_bytes()).hexdigest()
assert all(r["caller_sha256"]==chash and r["native_sha256"]==nhash for r in (partial,precision,binding))
g=partial["compiler_outer"]
b=binding["occurrence_and_geometry"]
assert g["outer"]["strict_count"]==54 and g["outer"]["functional_count"]==4 and Q(g["outer"]["minimum_margin"])>0
assert b["paid_positions"]==sum(partial["invoice"]["P"].values())
assert b["productive_fields"]==sum(partial["invoice"]["T"].values())
assert b["rank_surplus"]==partial["invoice"]["S"] and partial["invoice"]["empty_root_credits"]==0
assert b["ambient"]==caller["ambient_rank"] and b["ambient"]<=153
L=b["native_calls"]
native_scalars=sum(e[0]!="MOVE" for e in native["program"])
caller_macros=sum(len(caller["types"][e[0]]["ports"]) for e in caller["events"] if e[0]!="J")
conversions=2*L*native["public"]+2*sum(t['roles']*len(t['ports']) for t in caller['types'].values())
signed_idle=sum(len(caller["types"][e[0]]["ports"]) for e in caller["events"] if e[:2]==["B","IDLE_ODD"])
scalar_services=32*(L*native_scalars+caller_macros+conversions)
map_slots=(2*b["paid_positions"]+2*b["productive_fields"]+b["native_contact_boundaries"]
           +2*b["idle_uses"]+3*b["query_uses"]+b["lambda_uses"]+signed_idle)
records_per_map=4*(b["ambient"]+1)**2
paid_record_ceiling=map_slots*records_per_map
# Use the same upper ambient 153 as the inherited compiler, even though
# each actual paid or target map is on at most 137 axes.
H=int(g["H"])
carrier_power=1920
kstar=carrier_power*153**carrier_power*(H+1)**2
cc=precision["context_c"]
assert cc<=4096 and (4096*kstar).bit_length()<H
assert max(v["strict_power_of_two"] for v in precision["rounded_caller"]["bounds"].values())<H
scalars=[Q(e[-1]) for e in caller["events"] if e[0]!="J" and e[1] in ("ADD","SCALE")]
scalars.extend(Q(e[2] if e[0]=="SCALE" else e[3]) for e in native["program"] if e[0] in ("ADD","COPY","SCALE"))
scalars.append(Q(1125))
odd_scale=int(read("ODD-CALLER-EXACT-GRID.json")["caller_odd_scale"])
scalars.extend((Q(odd_scale),Q(1,odd_scale)))
scalars.append(Q(1,1125))
bits=max(abs(q.numerator).bit_length() for q in scalars)
assert bits<=24
result={"native_sha256":nhash,"caller_sha256":chash,"tested_claim":g["claim"],"actual_ambient":b["ambient"],
        "compiler_ambient_cap":153,"H":H,"log_power":g["written_log_power"],"Kstar_bits":kstar.bit_length(),
        "context_c":cc,"context_bound_bits":(cc*kstar).bit_length(),
        "native_invocations":L,"caller_odd_scale":odd_scale,"owned_banks_per_raw_occurrence":b["reserved_native_banks"],
        "scalar_macro_inputs":{"native":L*native_scalars,"caller":caller_macros,"conversions":conversions},
        "scalar_services_upper":scalar_services,"scalar_steps_coefficient":scalar_services*2**20,
        "monomial_map_slots":map_slots,"elementary_records_per_map_upper":records_per_map,
        "elementary_records_upper":paid_record_ceiling,
        "max_scalar_numerator_bits":bits,"common_grid":{"fractional":"p+D","signed_width":"p+h+2D+3","temp_padding":26},
        "scope":"Exact finite-cost and common-format substitutions in the selected #7000 conditional application proof, using the conservative primitive movement and scalar constants there. The premise is the complete signed native/physical binding and retained compiler, BIT, stock, and outer contracts. This script counts the raw occurrence, not an enumerated top-level compiled multiplier."}
with (root/"ODD-FIXED-TAPE-COUNTS.json").open("x") as f:json.dump(result,f,indent=2)
print("PASS finite tariff substitution",scalar_services,paid_record_ceiling,"precision",cc,flush=True)
