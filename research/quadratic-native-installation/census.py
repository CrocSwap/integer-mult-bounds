"""Count the fixed quadratic elimination, chart words and monotone finite-tape allowances."""

from collections import Counter
import json
import sys
import band_product as bp
from gauss_phase import Quadratic, matrix_element
from phase_atlas import monomial_phase
from sparse_helpers import split

records = Counter()
maxima = Counter()


def observe(frame, event, result):
    if event != "call":
        return
    code = frame.f_code
    if code is matrix_element.__code__:
        f = frame.f_locals
        records["matrix_elements"] += 1
        maxima["circuit_gates"] = max(maxima["circuit_gates"], len(f["circuit"]))
        maxima["path_choices"] = max(
            maxima["path_choices"], sum(z[0] == "C" for z in f["circuit"])
        )
        maxima["coordinates"] = max(maxima["coordinates"], f["n"])
        records["circuit_gates"] += len(f["circuit"])
    elif code is Quadratic.sum.__code__:
        records["gauss_eliminations"] += 1
        maxima["free_bits"] = max(
            maxima["free_bits"], frame.f_locals["self"].active.bit_count()
        )
    elif code is monomial_phase.__code__:
        records["signed_monomials"] += 1
    elif code is split.__code__:
        records["helper_splits"] += 1


sys.setprofile(observe)
try:
    s = bp.production_supplier(19000, 10**21)
finally:
    sys.setprofile(None)
a = s.physical
assert len(a.factors) == 2971 and len(a.port) == 104
assert (
    records["matrix_elements"] <= 4 * (2971 + 2 * 104) and records["helper_splits"] == 2
)
assert (
    maxima["circuit_gates"] <= 128
    and maxima["free_bits"] <= maxima["path_choices"] <= 128
)
prefixes = 0
max_prefix = 0
distinct = 0
emitted = 0
for seq in (s.word.targets, s.word.paid):
    stored = {}
    for prefix, arr in seq.segments:
        stored[id(arr)] = len(arr)
        prefixes += 1
        if prefix:
            max_prefix = max(max_prefix, len(prefix))
    distinct += sum(stored.values())
    emitted += len(seq)
assert emitted == 334176 and distinct == 25621 and prefixes == 145 and max_prefix == 3
driver = Counter(row[0] for row in a.instructions())
routes = [col for pair in (*a.contacts, *a.port) for col in pair]
routes.extend(col for _, right, left in a.factors.values() for col in (right, left))
max_route = max(map(len, routes))
sites = len(a.graph["initial"]) + len(a.graph["schedule"]) + len(a.moves) + 1
donors = sum(len(row) for row in a.forms.values())
raw_visits = (sum(driver.values()) + 1) * 64 + driver["NATIVE"] * (
    32 * sites * (max_route + 1) + 8 * donors
)
assert driver["NATIVE"] == 48 and raw_visits < 2**60
positive_size = 2 * emitted
# Each emitted port rebuilds one short tag. Even a sequential lookup that reads the full
# fixed set of segments, roots and 5674 body lines at every use fits this pass budget.
assert 2 * positive_size * (distinct + prefixes) * 256 * 256 < 2**52
# The fixed generator has at most 2^68 indexed actions, including both sources.
# Each can append two input-sized data strings plus bounded headers.
actions = 2**68
bits = 2**38
store = actions * 4 * bits
assert store == 2**108
# Four monotonically scanned tapes and a 128-bit cursor per cell.
assert 8 * store * 512 * 128 < 2**129
# A fixed record product uses two word slots for its unreduced value. Euclid at width
# 2w+2 finishes in <=4w+4 divisions. Charge a schoolbook shift/subtract cycle per bit pair.
assert 8 * (4 * bits + 4) * (2 * bits + 2) ** 2 * 2**16 < 2**138
payer = 2**140
assert (2**129 + 2**138 + 2**120) < payer
# This retains all of the predecessor's 2^32 multiplicative reserve for parsing, ordering,
# hashing, scratch allocation and cleanup rather than relying on a zero-cost host primitive.
assert (actions + 1) * payer * 2**32 < 2**241
print(
    json.dumps(
        {
            "actions": dict(records),
            "maxima": dict(maxima),
            "specialization": {
                "stored_role_entries": distinct,
                "segments": prefixes,
                "generated_logical_ports": emitted,
                "two_copy_extra_control_bound": 2**52,
            },
            "setup_exponent": 241,
            "one_copy_chart_visit_bound_before_expansion": raw_visits,
            "installed_bits_le_log2": 108,
            "array_form_fields": sum(len(row) for row in a.forms.values()),
        },
        indent=2,
    )
)
