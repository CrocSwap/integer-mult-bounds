"""Verify the case split excluding two added coframe ADDs on pinned F6824."""
import json
from pathlib import Path

root=Path(__file__).resolve().parent
files={
 "first_order":"PR6824-MIXED-FIRST-ORDER-HOST-CONTACTS.json",
 "one_zero":"PR6824-TWO-EDIT-MIXED-CANCELLATION.json",
 "both_zero":"PR6824-TWO-CONTACT-DARK-REACHABILITY.json",
}
data={name:json.loads((root/path).read_text()) for name,path in files.items()}
assert len(data["first_order"]["ports"])==104
assert all(not r["contacts_by_support"] for r in data["first_order"]["ports"].values())
assert not data["one_zero"]["first_suffix_zero_candidates"]
assert not data["one_zero"]["second_donor_zero_candidates"]
assert not data["both_zero"]["reachable_ports"]
proof=[
    "Two additions at ordered cuts give endpoint delta c1 B1 A1 + c2 B2 A2 + c1 c2 h B2 A1, where A are baseline donor rows, B are baseline suffix columns and h is the interposed scalar transfer.",
    "To have nonzero x,y coefficient, the mixed term must supply it because no baseline single ADD has nonzero x,y derivative. Hence B2[x] and A1[y] are nonzero, B1[x] and A2[y] are zero, and the interposed coefficient is nonzero.",
    "If B1 and A2 are both nonzero, the two suffix columns are independent (their x coordinates differ by zero/nonzero), and the rows A1 and A2 + c1 h A1 are independent (A2 has no y). The endpoint delta has rank two, contradicting the rank-one repair.",
    "If only B1 is zero, B2 must be an isolated X+Y suffix and the non-Y part of A1 must cancel the nonzero A2. The chronological mixed-cancellation census excludes every such signature.",
    "If only A2 is zero, A1 must be pure Y and the nonzero B1 must match the residual after normalizing B2 at X. The chronological mixed-cancellation census excludes every such signature.",
    "If B1 and A2 are both zero, the pure-Y first donor and isolated X+Y second sink must be connected via the dark scratch path. The generous support transfer scan excludes it."
]
with (root/"PR6824-TWO-ADD-HOST-OBSTRUCTION.json").open("x") as out:
    json.dump({"status":"PASS_FIXED_CHRONOLOGY_TWO_ADD_HOST_OBSTRUCTION",
               "ports":104,"evidence":files,"proof":proof,
               "scope":"Exact normalized scalar circuit with the fixed chronological MOVE/COPY/INIT/CLEAR schedule. The required repair is one specified same-port rank-one F-to-HOST entrance transvection. At most two newly inserted distinct-register coframe ADDs. Changing MOVE timing or chart shape, scalings, cross-port block outputs, or adding three or more contacts is outside scope."},out,indent=2)
print("PASS_FIXED_CHRONOLOGY_TWO_ADD_HOST_OBSTRUCTION 104")
