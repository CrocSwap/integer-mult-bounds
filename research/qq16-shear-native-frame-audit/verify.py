#!/usr/bin/env python3
"""Audit the literal QQ16 F0/B1 scalar shear against native endpoint types.

Apache-2.0. Prepared for Charles Bethin with substantial OpenAI Codex
assistance. Ali Romman supplies the retained QQ16 maps; Cinna Davis supplies
PR2216's logical shear. No predecessor executable is imported.
"""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
MARKER = "PASS_QQ16_SHEAR_NATIVE_FRAME_AUDIT"


def need(value, message):
    # Remain active under -O and -OO.
    if not value:
        raise ValueError(message)


def terms_key(terms):
    out = {}
    for axis, coefficient in terms:
        out[axis] = (out.get(axis, 0) + coefficient) % 4
    return tuple(sorted((axis, c) for axis, c in out.items() if c))


def phase(polynomial, frequency):
    """Evaluate stored coefficients without importing their generator."""
    result = sum(
        c for i, c in enumerate(polynomial["linear_Z4"])
        if (frequency >> i) & 1
    )
    for i, row in enumerate(polynomial["quadratic_rows"]):
        if (frequency >> i) & 1:
            result += 2 * (row & frequency).bit_count()
    return result % 4


def neg(vector):
    return [(-a, -b) for a, b in vector]


def line(vector, label, sign):
    """Physical Gaussian-integer convolution, with no phase-polynomial input.

    Apply ((1 + sign*i) I + (1 - sign*i) T_label)/2.
    These character fixtures stay in the Gaussian integers at every step.
    """
    result = []
    for z, (a, b) in enumerate(vector):
        c, d = vector[z ^ label]
        real = a - sign * b + c + sign * d
        imag = sign * a + b - sign * c + d
        need(real % 2 == imag % 2 == 0, "nonintegral Gaussian fixture")
        result.append((real // 2, imag // 2))
    return result


def walk(events):
    """Visit only the literal retained wrapper; no core expansion is claimed."""
    for event in events:
        if event[0] in ("cover_sweep", "private_sweep"):
            yield from walk(event[2])
        else:
            yield event


def bind_boundary(packet, full_id):
    """Bind the inherited core boundary to the relevant literal wrappers."""
    forward = packet["programs"]["F_0"]
    need(forward[0][:3] == ["retained_core", "forward", 0], "F0 core boundary")
    untouched_y = {112 + p for p in T}
    for event in walk(forward[1:]):
        if event[0] == "scalar":
            target = event[1][1]
        elif event[0] in ("cover_map", "native_line"):
            target = event[1]
        else:
            raise ValueError("unexpected F0 wrapper event " + str(event[0]))
        need(
            not (target[0] == "L" and target[1] in untouched_y),
            "F0 wrapper changes a Y_T field",
        )
        if target[0] == "L" and target[1] in A + T:
            need(
                event[0] == "scalar" and event[2] == full_id,
                "F0 preserves selected X frame",
            )

    # B1 explicitly converts these X_T fields into their corresponding Y types.
    normalizations = {}
    for target, event in zip(T, packet["programs"]["B_1_2"][:8], strict=True):
        need(
            event[:3] == ["native_line", ["L", target], "inverse_" + str(target)],
            "initial B1 normalization order",
        )
        normalizations[target] = event
    return normalizations


def run(root):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for record in manifest["files"]:
        if record["usage"] == "input":
            actual = hashlib.sha256((root / record["path"]).read_bytes()).hexdigest()
            need(actual == record["sha256"], "source pin " + record["path"])

    packet = json.loads(gzip.decompress(
        (root / "research/joint-query/certificate.json.gz").read_bytes()
    ))
    need(packet["A_ports"] == A and packet["T_ports"] == T, "selected partition")
    frames = packet["native_frame_registry"]
    lines = packet["native_line_recipes"]
    full = tuple((1 << j, 1) for j in range(9))
    frame_keys = {terms_key(v["line_terms_Z4"]): k for k, v in frames.items()}
    full_id = frame_keys[full]
    normalizations = bind_boundary(packet, full_id)
    receipts = []

    for source, target in zip(A, T, strict=True):
        native = lines["inverse_" + str(target)]
        q = native["label"]
        need(
            native["port"] == target and native["sign"] == -1 and 0 < q < 512,
            "actual inverse native line",
        )
        y_id = frame_keys[terms_key(list(full) + [(q, -1)])]
        need(
            normalizations[target][3:] == [full_id, y_id],
            "B1 X_T normalization binds the corresponding Y_T type",
        )
        w = q & -q  # A concrete binary frequency with q dot w = 1.
        source_phase = phase(frames[full_id], w)
        target_phase = phase(frames[y_id], w)
        need((target_phase - source_phase) % 4 == 3, "inverse-line phase mismatch")
        need(
            phase(frames[full_id], 0) == phase(frames[y_id], 0) == 0,
            "constant payload blind spot",
        )
        need(
            all(
                (phase(frames[y_id], v) - phase(frames[full_id], v)) % 4
                == (-((q & v).bit_count() % 2)) % 4
                for v in range(512)
            ),
            "all active-character phase differences",
        )

        # Independently apply the nine physical lines to an explicit array.
        character = [(-1 if (w & z).bit_count() % 2 else 1, 0) for z in range(512)]
        physical = character
        for axis in range(9):
            physical = line(physical, 1 << axis, 1)
        units = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        rx, ix = units[source_phase]
        ry, iy = units[target_phase]
        need(
            physical == [(rx * c, ix * c) for c, _ in character],
            "physical F0 source versus stored polynomial",
        )
        desired = [(-ry * c, -iy * c) for c, _ in character]
        bare = neg(physical)
        need(bare != desired, "bare subtraction must differ from logical subtraction")
        mismatch = next(i for i in range(512) if bare[i] != desired[i])

        # This source adaptation is a semantic control, not a free native primitive.
        adapted = neg(line(physical, q, -1))
        wrong_sign = neg(line(physical, q, 1))
        need(adapted == desired, "inverse-line semantic positive control")
        need(wrong_sign != desired, "positive-line sign negative control")
        # Decode the bare Y result physically, using (F C_q^-1)^-1 = C_q F^-1.
        decoded_y = bare
        for axis in reversed(range(9)):
            decoded_y = line(decoded_y, 1 << axis, -1)
        decoded_y = line(decoded_y, q, 1)
        sum_change = [(c + a, b) for (c, _), (a, b) in zip(character, decoded_y)]
        need(
            sum_change == [(c, -c) for c, _ in character],
            "bare paired updates violate logical sum conservation",
        )
        constant = [(1, 0)] * 512
        need(line(constant, q, -1) == constant, "constant-payload control")

        receipts.append({
            "A_port": source,
            "T_port": target,
            "q": q,
            "X_frame": full_id,
            "Y_frame": y_id,
            "frequency_mask": w,
            "source_phase_Z4": source_phase,
            "target_phase_Z4": target_phase,
            "physical_counterexample_index": mismatch,
            "bare_target": list(bare[mismatch]),
            "desired_target": list(desired[mismatch]),
            "logical_sum_change_at_witness": list(sum_change[mismatch]),
            "X_T_add_legal": True,
            "Y_T_add_legal": False,
            "inverse_line_semantic_control": "PASS",
            "positive_line_control": "REJECTED",
        })

    return {
        "status": MARKER,
        "literal_shear_scalar_additions": 16,
        "same_frame_X_additions": 8,
        "unadapted_Y_additions_rejected": 8,
        "phase_characters_checked": 4096,
        "physical_character_vectors": 8,
        "owner": "identity",
        "tensor_payload_layers": 1,
        "receipts": receipts,
        "scope": (
            "Counterexamples to the literal sixteen-scalar native implementation "
            "on arbitrary payloads. PR2216 logical payload-constant rank result "
            "is not refuted. Fused or redesigned implementations remain open; "
            "no child-count lower bound or new kappa."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = run(ROOT)
    path = HERE / "RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(json.loads(path.read_text()) == result, "frozen complete receipt differs")
    print(
        MARKER + " rejected_Y_adds=8 same_frame_X_updates=8"
        " character_phases=4096 physical_vectors=8"
    )


if __name__ == "__main__":
    main()
