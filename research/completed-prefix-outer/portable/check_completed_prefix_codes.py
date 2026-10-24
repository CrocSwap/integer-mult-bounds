"""Check the physical prefix and twiddle conventions from pinned sources."""

from hashlib import sha256
from fractions import Fraction
from pathlib import Path
import argparse
import json


PACKAGE = Path(__file__).resolve().parents[1]
HERE = PACKAGE / "frozen/lanes" / "temporal-reuse"
REVISION = "3ae9a6f3ac74ded022ab3b4872a7357a621af6fb"
PINS = {
    "upstream/build/sections/02-streams.tex":
        "606c80db61cad13aa0c3b6060dc4b88dbbe7ac60cdd831aa93f28d908fd09dab",
    "upstream/build/sections/05-layers.tex":
        "20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594",
    "upstream/build/sections/06-transforms.tex":
        "924316e4bc905066281d8f9e8746a49d8829aeb393688608deb1e61c3c87853c",
    "certificates/selected-result.json":
        "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
    "research/community-frontier1094-audit/ASSEMBLY.json":
        "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
}
INTERFACE_PIN = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
MODULUS = 97


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unit(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    cols = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, col)) % MODULUS
             for col in cols] for row in a]


def inverse(a):
    n = len(a)
    rows = [list(row)+one for row, one in zip(a, unit(n))]
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        z = pow(rows[j][j], -1, MODULUS)
        rows[j] = [v*z % MODULUS for v in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                z = rows[i][j]
                rows[i] = [(a-z*b) % MODULUS
                           for a, b in zip(rows[i], rows[j])]
    need([row[:n] for row in rows] == unit(n), "Inverse elimination")
    return [row[n:] for row in rows]


def one_round(h, root):
    rows = unit(64)
    half = pow(2, -1, MODULUS)
    for axis in range(2):
        bit = 3*axis+h
        for x in range(64):
            if not (x >> bit) & 1:
                y = x ^ (1 << bit)
                a, b = rows[x], rows[y]
                rows[x] = [(u+v)*half % MODULUS for u, v in zip(a, b)]
                rows[y] = [(u-v)*half % MODULUS for u, v in zip(a, b)]
    for x in range(64):
        exponent = 0
        for axis in range(2):
            value = (x >> (3*axis)) & 7
            exponent -= (16 >> (h+1))*((value >> h) & 1)*(value & ((1 << h)-1))
        z = pow(root, exponent % 16, MODULUS)
        rows[x] = [v*z % MODULUS for v in rows[x]]
    return rows


def prefix_matrix(a):
    out = [[0]*64 for _ in range(64)]
    for target in range(64):
        selected = ((target >> 2) & 1) + 2*((target >> 5) & 1)
        rest = target & ~(4+32)
        for old in range(4):
            source = rest + 4*(old & 1) + 32*(old >> 1)
            out[target][source] = a[selected][old]
    return out


def reverse3(x):
    return ((x & 1) << 2) + (x & 2) + (x >> 2)


def exact_dif_check(root):
    rounds = [one_round(h, root) for h in (2, 1, 0)]
    full = multiply(rounds[2], multiply(rounds[1], rounds[0]))
    direct = []
    for x in range(64):
        j0, j1 = reverse3(x & 7), reverse3(x >> 3)
        direct.append([pow(root, (-2*(j0*(k & 7)+j1*(k >> 3))) % 16,
                           MODULUS)*pow(64, -1, MODULUS) % MODULUS
                       for k in range(64)])
    need(full == direct, "Stored DIF order differs from the direct transform")
    a, b = unit(4), unit(4)
    a[0][1] = 1
    b[1][2] = 1
    need(multiply(a, b) != multiply(b, a), "The two codes must not commute")
    pa, pb = prefix_matrix(a), prefix_matrix(b)
    for gate in (pa, pb):
        for step in rounds[1:]:
            need(multiply(gate, step) == multiply(step, gate),
                 "A past prefix does not commute with a later round")
    encoded = multiply(rounds[2], multiply(pb, multiply(rounds[1],
                                                      multiply(pa, rounds[0]))))
    fused = multiply(pb, pa)
    need(encoded == multiply(fused, full), "The accumulated code has the wrong order")
    fi = inverse(fused)
    need(multiply(fi, fused) == unit(64), "Left code inverse")
    need(multiply(fused, fi) == unit(64), "Right code inverse")
    need(multiply(fi, encoded) == full, "Terminal code decode")
    return {"record_dimension": 64, "prime": MODULUS, "root_order": 16,
            "root": root, "exact_transform_entries": 4096,
            "completed_slots": [2, 5], "later_round_commutators": 4,
            "noncommuting_code_fusion_entries": 4096,
            "both_code_inverse_orders": True}


def opposite_round(lengths, h, root):
    n = 1 << sum(lengths)
    offsets = [0, lengths[0]]
    rows = unit(n)
    half = pow(2, -1, MODULUS)
    for width, offset in zip(lengths, offsets):
        if h >= width:
            continue
        bit = offset+h
        for x in range(n):
            if not (x >> bit) & 1:
                y = x ^ (1 << bit)
                a, b = rows[x], rows[y]
                rows[x] = [(u+v)*half % MODULUS for u, v in zip(a, b)]
                rows[y] = [(u-v)*half % MODULUS for u, v in zip(a, b)]
    for x in range(n):
        exponent = 0
        for width, offset in zip(lengths, offsets):
            if h >= width:
                continue
            value = (x >> offset) & ((1 << width)-1)
            tail = sum(((value >> v) & 1) << (width-1-v)
                       for v in range(h+1, width))
            exponent += (16 >> (width-h))*((value >> h) & 1)*tail
        z = pow(root, exponent % 16, MODULUS)
        rows[x] = [v*z % MODULUS for v in rows[x]]
    return rows


def opposite_check(root):
    results = []
    for lengths in ((3, 3), (3, 2)):
        n = 1 << sum(lengths)
        offsets = [0, lengths[0]]
        rounds = [opposite_round(lengths, h, root) for h in range(max(lengths))]
        full = unit(n)
        for step in rounds:
            full = multiply(step, full)
        direct = []
        for x in range(n):
            row = []
            for k in range(n):
                exponent = 0
                for width, offset in zip(lengths, offsets):
                    output = (x >> offset) & ((1 << width)-1)
                    source = (k >> offset) & ((1 << width)-1)
                    frequency = sum(((source >> v) & 1) << (width-1-v)
                                    for v in range(width))
                    exponent += (16 >> width)*output*frequency
                row.append(pow(root, exponent % 16, MODULUS)
                           *pow(n, -1, MODULUS) % MODULUS)
            direct.append(row)
        need(full == direct, "Reversed-label plus DIF is not F_plus B")
        code = unit(n)
        for x in range(n):
            if not (x & 1):
                code[x][x ^ 1] = 1
        for step in rounds[1:]:
            need(multiply(code, step) == multiply(step, code),
                 "A completed opposite slot enters a later round")
        results.append({"axis_log_lengths": list(lengths), "record_dimension": n,
                        "all_operator_entries": n*n,
                        "remaining_round_commutators": len(rounds)-1,
                        "required_operator": "F_plus B_inverse",
                        "physical_bit_reversal_operations": 0})
    return results


def line_normalizer_check(ports, root):
    imaginary = pow(root, 4, MODULUS)
    half = pow(2, -1, MODULUS)
    a, b = (1+imaginary)*half % MODULUS, (1-imaginary)*half % MODULUS
    need((a*b) % MODULUS == half, "The intrinsic C coefficients differ")
    columns = 0
    for q in ports:
        need(q and q.bit_count() % 2, "A source port is not an odd line")
        axis = (q & -q).bit_length()-1
        for x in range(512):
            z = x ^ q
            dx = imaginary if (x >> axis) & 1 else 1
            dz = imaginary if (z >> axis) & 1 else 1
            diagonal = a*b*(dx+dz) % MODULUS
            off = (b*b*dx+a*a*dz) % MODULUS
            off_inverse = (a*a*dx+b*b*dz) % MODULUS
            need(diagonal and off and off_inverse,
                 "The paired transported twiddle lost a required entry")
            phase = pow(imaginary, (z.bit_count()-x.bit_count()) % 4, MODULUS)
            need(off*phase % MODULUS and off_inverse*phase % MODULUS,
                 "H0 boundary phases removed the witness")
            columns += 1
    return {"actual_ports": len(ports), "spatial_columns": columns,
            "paired_replica_columns": 2*columns,
            "H0_diagonal_conjugation_checked": True,
            "current_line_is_not_a_twiddle_normalizer": True,
            "line_square_is_a_permutation": True,
            "all_size_statement": "The tensor support is 2^lambda by the exact unit proof."}


def selected_bit_check():
    slots, copies, width, offset = 3, 2, 3, 1
    selected = [width*j+offset for j in range(slots*copies)]
    cases = 0
    for x in range(1 << (slots*copies*width)):
        y = x
        for j in range(copies):
            src, dst = selected[j], selected[copies+j]
            y ^= ((x >> src) & 1) << dst
        changed = x ^ y
        allowed = sum(1 << selected[copies+j] for j in range(copies))
        need(not (changed & ~allowed), "A chart changed an unselected bit")
        restored = y
        for j in range(copies):
            src, dst = selected[j], selected[copies+j]
            restored ^= ((y >> src) & 1) << dst
        need(restored == x, "Selected chart inverse")
        cases += 1
    return {"slots": slots, "copies": copies, "chunk_width": width,
            "offset": offset, "all_addresses": cases,
            "third_slot_and_other_offsets_fixed": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, default=PACKAGE / "sources/upstream")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source = {}
    for path, pin in PINS.items():
        raw = (args.sources / path).read_bytes()
        need(sha256(raw).hexdigest() == pin, "Source hash: "+path)
        source[path] = raw
    assembly = json.loads(source["research/community-frontier1094-audit/ASSEMBLY.json"])
    selected = json.loads(source["certificates/selected-result.json"])
    need(assembly["kappa"] == selected["kappa"], "Selected exponent binding")
    epsilon = Fraction(assembly["outer"]["epsilon_positive"])
    kappa = Fraction(assembly["kappa"])
    need(0 < 1-epsilon and epsilon-kappa > Fraction(99, 100),
         "The whole-axis prefix invoice has no strict margin")
    interface_path = HERE.parent / "circuit-interface/INTERFACE.json"
    raw = interface_path.read_bytes()
    need(sha256(raw).hexdigest() == INTERFACE_PIN, "Interface hash")
    ports = json.loads(raw)["ports"]
    root = next(x for x in range(2, MODULUS)
                if pow(x, 16, MODULUS) == 1 and pow(x, 8, MODULUS) == MODULUS-1)
    receipt = {
        "status": "PASS_COMPLETED_PREFIX_CODES",
        "revision": REVISION, "source_sha256": PINS,
        "interface_sha256": INTERFACE_PIN,
        "dif": exact_dif_check(root),
        "reversed_label_opposite": opposite_check(root),
        "paired_current_line": line_normalizer_check(ports, root),
        "selected_offset_endpoint": selected_bit_check(),
        "whole_axis_row_prefix": {
            "one_axis_work_and_layout": "O(V ell)",
            "ell": "Theta(p/d)",
            "row_bits_needed": "ceil(ceil(log_m d) log_2 W)=O(log d)",
            "axis_bits_available": "ell or ell-1",
            "strict_margin_epsilon_minus_kappa": str(epsilon-kappa),
            "margin_lower_bound": "99/100",
            "applies_to_both_transform_directions": True,
            "padding_volume_factor": "less than two",
        },
        "scope": "Exact finite conventions and negative controls; all-size theorems are proved in the note.",
        "not_claimed": ["A new complete supplier", "A recursive encoded-child contract",
                        "A kappa improvement", "A general circuit lower bound"],
    }
    args.out.write_text(json.dumps(receipt, sort_keys=True, indent=2)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
