"""Review the changed opposite transform with exact root exponents."""

from hashlib import sha256
from pathlib import Path
import argparse
import json
import subprocess


REVISION = "3ae9a6f3ac74ded022ab3b4872a7357a621af6fb"
SOURCE = "upstream/build/sections/06-transforms.tex"
SOURCE_PIN = "924316e4bc905066281d8f9e8746a49d8829aeb393688608deb1e61c3c87853c"
PROOF_PIN = "c0050de40211bf06ddb386192795d7d2a4ebb0452aa61b1c8139b92f7041cdf5"


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def reverse(value, width):
    return sum(((value >> j) & 1) << (width - 1 - j) for j in range(width))


def path_phase(widths, x, y, r, common_width=False):
    phase, offset = 0, 0
    for width in widths:
        xx = (x >> offset) & ((1 << width) - 1)
        yy = (y >> offset) & ((1 << width) - 1)
        for h in range(width):
            branch = (yy >> h) & 1
            phase += r * ((xx >> h) & 1) * branch
            tail = sum(((xx >> v) & 1) << (width - 1 - v) for v in range(h + 1, width))
            denominator = 1 << ((max(widths) if common_width else width) - h)
            phase += (2 * r // denominator) * branch * tail
        offset += width
    return phase % (2 * r)


def direct_phase(widths, x, y, r):
    phase, offset = 0, 0
    for width in widths:
        mask = (1 << width) - 1
        phase += (2 * r // (1 << width)) * reverse((x >> offset) & mask, width) * ((y >> offset) & mask)
        offset += width
    return phase % (2 * r)


def layout(widths, chunk, ell):
    bottom = (ell - 1) % chunk
    initial = [(i, h) for i, width in enumerate(widths) for h in range(width - 1, -1, -1)]
    prefix = [(i, ell - 1) for i, width in enumerate(widths) if width == ell]
    prefix += [(i, h) for h in range(bottom - 1, -1, -1) for i in range(len(widths))]
    remaining = [slot for slot in initial if slot not in set(prefix)]
    count = (ell - 1) // chunk
    blocks = {(i, j): remaining[(i * count + j) * chunk:(i * count + j + 1) * chunk]
              for i in range(len(widths)) for j in range(count)}
    physical = prefix + [slot for j in range(count) for i in range(len(widths)) for slot in blocks[i, j]]
    require(sorted(physical) == sorted(initial), "the retained L is a slot permutation")
    positions = {slot: k for k, slot in enumerate(physical)}
    checks = 0
    for h in range(bottom, ell - 1):
        axis_positions = [positions[i, h] for i in range(len(widths))]
        require(all(axis_positions[i + 1] - axis_positions[i] == chunk for i in range(len(widths) - 1)),
                "the opposite round has consecutive equal-width chunks")
        require(all((positions[i, h] - len(prefix)) % chunk == chunk - 1 - (h - bottom) % chunk
                    for i in range(len(widths))), "the common selected offset is unchanged")
        checks += 1
    return checks


def main(args):
    raw = subprocess.check_output(["git", "-C", str(args.repo), "show", REVISION + ":" + SOURCE])
    require(sha256(raw).hexdigest() == SOURCE_PIN, "original all-size transform source")
    require(sha256(args.proof.read_bytes()).hexdigest() == PROOF_PIN, "reviewed proof snapshot")
    entry_cases, coefficient_cases, layout_cases, round_cases = [], 0, 0, 0
    # This checks polynomial coefficients, without a finite-field specialization.
    for width in range(1, 31):
        r = 1 << width
        for h in range(width):
            for v in range(width):
                direct = (2 * r // (1 << width)) * (1 << h) * (1 << (width - 1 - v))
                path = r if h == v else ((2 * r // (1 << (width - h))) * (1 << (width - 1 - v)) if h < v else 0)
                require((direct - path) % (2 * r) == 0, "exact all-bit coefficient identity")
                coefficient_cases += 1
    for widths in [(a,) for a in range(1, 7)] + [(3, 2), (3, 3), (4, 3), (2, 2, 1)]:
        n, r = 1 << sum(widths), 1 << max(widths)
        for x in range(n):
            for y in range(n):
                require(path_phase(widths, x, y, r) == direct_phase(widths, x, y, r),
                        "an exact polynomial-ring matrix entry differs")
        entry_cases.append(dict(axis_log_lengths=widths, entries=n*n, normalization_denominator=n, root_modulus=2*r))
    for ell in range(2, 15):
        for chunk in range(1, ell):
            for widths in ((ell, ell), (ell - 1, ell - 1), (ell, ell - 1),
                           (ell - 1, ell, ell - 1), (ell, ell, ell - 1, ell - 1)):
                round_cases += layout(widths, chunk, ell)
                layout_cases += 1
    controls = []
    widths, r, n = (3, 2), 8, 32
    wrong = next((dict(x=x, y=y, correct=direct_phase(widths, x, y, r),
                       wrong=path_phase(widths, x, y, r, True))
                  for x in range(n) for y in range(n)
                  if path_phase(widths, x, y, r, True) != direct_phase(widths, x, y, r)), None)
    require(wrong is not None, "wrong common recursive length control")
    controls.append(dict(name="same_twiddle_length_on_long_and_short_axes", witness=wrong))
    require(reverse(1, 3) != 1, "nontrivial bit reversal")
    require(direct_phase((3,), 1, 1, 8) != 2, "wrong endpoint without input bit reversal")
    controls.append(dict(name="omit_input_bit_reversal_in_endpoint_formula", x=1, y=1,
                         correct=direct_phase((3,), 1, 1, 8), wrong=2))
    result = dict(status="PASS_INDEPENDENT_REVERSED_LABEL_OPPOSITE_REVIEW",
                  revision=REVISION, source_path=SOURCE, source_sha256=SOURCE_PIN,
                  proof_sha256=PROOF_PIN, exact_bit_coefficient_cases=coefficient_cases,
                  exact_ring_entry_cases=entry_cases, layout_cases=layout_cases,
                  common_chunk_round_checks=round_cases, controls=controls,
                  proof_scope="All-size opposite schedule, exact F_plus B_inverse endpoint, retained L layout, long/short axes, and the original contraction/truncation/asymptotic cost proof",
                  not_claimed=["A changed encoded supplier", "A recursively closed past-space code", "An improved kappa", "The other theorems in the reviewed note"])
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(dict(status=result["status"], coefficient_cases=coefficient_cases,
        exact_entries=sum(c["entries"] for c in entry_cases), layout_cases=layout_cases,
        common_chunk_rounds=round_cases), sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "proof", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    main(parser.parse_args())
