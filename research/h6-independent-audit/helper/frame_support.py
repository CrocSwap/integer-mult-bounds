"""Exact scoped support/frame obstruction, with a restricted-label control.

This is not a lower bound for a fused Walsh arithmetic DAG. Run from any cwd
with a NumPy-capable Python. It reads frozen inputs and writes only beside
this script. Checks remain active with -O.
"""
from pathlib import Path
import hashlib
import json
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT / "research/niemeier-lattices/code/e8_cubed.py"
sys.path.insert(0, str(INPUT.parent))
import e8_cubed as e
import numpy as np


def require(value, message):
    if not value:
        raise ValueError(message)


def rank_witness(indices, packed):
    basis = {}
    witness = []
    for i in indices:
        v = int(packed[i])
        for pivot in sorted(basis, reverse=True):
            if (v >> pivot) & 1:
                v ^= basis[pivot]
        if v:
            basis[v.bit_length() - 1] = v
            witness.append(int(i))
    return len(basis), witness


roots, _, shell, profiles = e.construct_shell()
ports = shell[(profiles & 4) == 0, :16].astype(np.int64)
_, packed, fitting = e.binary_labels(roots, ports)
require(len(ports) == 30960 and fitting["dimension"] == 17, "Pinned H6 domain")
records = []
for coordinate in range(16):
    support = np.flatnonzero(ports[:, coordinate])
    rank, witnesses = rank_witness(support, packed)
    require(rank == 17, "Full coordinate support span")
    require(all(ports[i, coordinate] != 0 for i in witnesses), "Witness support")
    require(rank_witness(witnesses, packed)[0] == 17, "Independent rank-17 witness")
    mutant = witnesses[:-1] + witnesses[:1]
    require(rank_witness(mutant, packed)[0] == 16, "Repeated witness negative control")
    records.append(dict(coordinate=coordinate, support_count=len(support),
                        binary_support_span=rank, common_target_cap_dimension=17-rank,
                        witness_ports=witnesses,
                        witness_packed_labels=[int(packed[i]) for i in witnesses]))

# A final FWHT output at one address label has a different support from a
# global character decoder column. This positive control prevents confusing
# the two architectures: every target in this bucket has the same address.
label = int(packed[0])
restricted = np.flatnonzero(packed == label)
rank, witnesses = rank_witness(restricted, packed)
require(rank == 1, "Single label decoder support rank")
control = dict(label=label, target_ports=restricted.tolist(),
               binary_support_span=rank, common_target_cap_dimension=16,
               full_to_common_cap_rank=1, witness_ports=witnesses)

result = dict(
    status="PASS_SCOPED_CHARACTER_SUPPORT_FRAME_WITNESSES",
    source_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(),
    ports=30960, frame_dimension=17,
    interpretation="The decoder column D_c(i)*(-1)^(l_i M a) has support P[i,c]!=0 because the character sign is nonzero. Its target caps intersect in the zero frame. The encoder support is the same coordinate set and spans FULL. An isolated character aggregate therefore has FULL gathering frame and zero common scatter frame, requiring a rank-17 private descent under this architecture.",
    coordinate_supports=records, restricted_label_positive_control=control,
    scope="Private character-column factorizations only. A final FWHT output label bucket has cap dimension16, as the positive control shows. Cross-channel cancellation, low-frame routing, shared DAGs, virtual entrances and alternative factorizations are not excluded.",
    negative_controls={"repeat_one_span_witness": "rank16 instead of required17"},
)
destination = Path(__file__).with_name("FRAME-SUPPORT.json")
destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(dict(status=result["status"], coordinate_support_spans=[r["binary_support_span"] for r in records],
                     single_label_cap_dimension=control["common_target_cap_dimension"],
                     output=str(destination)), sort_keys=True))
