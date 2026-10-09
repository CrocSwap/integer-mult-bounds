#!/usr/bin/env python3
"""Is the bit word's donor-reuse pairing maximal? (reproducible diagnostic)

word.py::row() computes

    R = self.R - len(pairs);  W = 2*v + R;   deficit = W*m - mass  (asserted invariant)

so each donation pair lowers W by one at constant rank deficit and strictly
raises the coarse saving a (kappa = a/(1+a)). A pair (recipient b in gauge, dead
donor d) is legal only if, besides the one-to-one, disjointness, ordering and
gate-port conditions of word.py::__init__, the geometry condition

    C.sub(endframe[d], gauge[b].frame)          (word.py::exact_frames)

holds: the donor's end frame must fit inside the recipient's birth frame.

This reports the unpaired gauges by birth-frame dimension and counts how many
donor end frames (out of every distinct donor end frame) are contained in them.

    python3 -B bit_reuse_maximal.py --package <checkout of PR189's package>
"""
from pathlib import Path
from collections import defaultdict
import argparse, importlib.util, json, sys


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", type=Path, required=True,
                    help="checkout of research/paired-cube-twin-local-168")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    PKG = a.package.resolve()
    sys.path.insert(0, str(PKG / "bit"))
    sys.path.insert(0, str(PKG / "arithmetic"))
    bw = module("reuse_maximal_word", PKG / "bit" / "word.py")
    word = bw.Candidate()
    word.exact_frames()
    C = word.C

    recipients = {b for b, _ in word.pairs}
    unpaired = [b for b in word.gauge if b not in recipients]
    by_dim = defaultdict(int)
    for b in unpaired:
        by_dim[C.dimf[word.gauge[b]["frame"]]] += 1
    paired_dim = defaultdict(int)
    for b, _ in word.pairs:
        paired_dim[C.dimf[word.gauge[b]["frame"]]] += 1

    pool = [s for s in range(word.R)
            if s not in word.gauge and s not in word.rootroles and s in word.last]
    donor_frames = {word.endframe[d] for d in pool}

    # Distinct birth frames of unpaired gauges; containment is decided once per
    # (donor end frame, birth frame) pair.
    birth_frames = sorted({word.gauge[b]["frame"] for b in unpaired})
    nondeg_fd = {fd: C.nondeg(fd) for fd in donor_frames}
    contained = []
    for fb in birth_frames:
        if not C.nondeg(fb):
            continue
        hits = [fd for fd in donor_frames
                if C.dimf[fd] <= C.dimf[fb] and nondeg_fd[fd] and C.sub(fd, fb)]
        if hits:
            contained.append(dict(birth_frame=fb, dim=C.dimf[fb], donor_frames=len(hits)))

    print(f"gauges={len(word.gauge)} pairs={len(word.pairs)} unpaired={len(unpaired)}")
    print(f"unpaired by birth-frame dim: {dict(sorted(by_dim.items()))}")
    print(f"paired   by birth-frame dim: {dict(sorted(paired_dim.items()))}")
    print(f"distinct donor end frames (non-gauge, non-root, phase-2 operands): "
          f"{len(donor_frames)}")
    print(f"unpaired birth frames: {len(birth_frames)}; of these, containing at least "
          f"one donor end frame: {len(contained)}")
    print("verdict: " + ("no unpaired gauge can receive a donor"
                         if not contained else "unpaired gauges admit donors (inspect)"))

    if a.out:
        a.out.write_text(json.dumps(dict(
            gauges=len(word.gauge), pairs=len(word.pairs), unpaired=len(unpaired),
            unpaired_by_birth_frame_dim={str(k): v for k, v in sorted(by_dim.items())},
            paired_by_birth_frame_dim={str(k): v for k, v in sorted(paired_dim.items())},
            donor_end_frames=len(donor_frames),
            unpaired_birth_frames=len(birth_frames),
            unpaired_birth_frames_admitting_a_donor=len(contained),
            detail=contained), indent=1) + "\n")


if __name__ == "__main__":
    main()
