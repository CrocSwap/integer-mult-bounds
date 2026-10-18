#!/usr/bin/env python3
"""Source-bound exact private-free and expanded native-cone audit of PR2979.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_io as io
import checks
import lifetimes as life


def audit(provider, blobs, run, progress):
    data = io.artifacts(blobs, provider, run)
    source = io.load(blobs, io.PRIOR + "source.py", "private_free_retained_source")
    native = io.load(blobs, io.PRIOR + "native.py", "private_free_retained_native")
    kernel = io.load(blobs, io.KERNEL, "private_free_exact_kernel")
    previous = json.loads(blobs[io.PRIOR + "RESULT-" + provider + ".json"])
    result = {}
    for orientation in ("forward", "backward"):
        backward = orientation == "backward"
        events, metadata = source.bind(data["word"], data["canonical"], data["programs"][orientation], backward)
        closure = life.provenance(events, metadata["start"])
        old = previous["orientations"][orientation]
        io.require(all(closure["old_pair"][k] == old[k] for k in ("event_indices", "boundary_inputs")),
                   "independent forward provenance agrees with predecessor two-root scope")
        values = life.values(events, metadata["start"], backward)
        io.require(len(values["frees"]) == 91 and values["peak_live_private"] == 91, "literal private stock")
        io.require(values["helper249"] == [["L249", [], "1"]], "preserved original helper root")
        io.require(set(closure["free_roots"]) == metadata["private"], "all source private frees covered")
        paid = Counter(e[5] if e[0] == "climb" else e[4] for e in events if e[0] in ("climb", "center"))
        claimed = json.loads(blobs["research/rank7-joint-endframes/CLAIM.json"])["local_profile"]
        io.require({str(k): v for k, v in paid.items()} == claimed, "literal complete local paid profile")
        control = checks.value_controls(events, metadata["start"], backward, closure)
        native_result = checks.native_coverage(native, kernel, events, closure, data, backward, progress)
        result[orientation] = {"source_bound_events": len(events), "source_events_sha256": io.digest(events),
            "values": values, "old_pair": life.summary(events, closure["old_pair"]),
            "all_frees": life.summary(events, closure["all_frees"]),
            "expanded": life.summary(events, closure["expanded"]), "native": native_result, "controls": control,
            "complete_local_paid_profile": {str(k): v for k, v in sorted(paid.items())}}
    return {"status": "PASS_ALL_PRIVATE_FREES_AND_EXPANDED_NATIVE_CONE", "provider": provider,
            "scientific_head": "be191346391661f4d35fc0d1508d0a6029572576",
            "predecessor_head": "c7d0d7be056ba77fda1c168641b2bcffb10cf43d",
            "orientations": result, "invoice_trace": checks.invoice(blobs, 91),
            "input_sha256": {p: hashlib.sha256(b).hexdigest() for p, b in sorted(blobs.items())},
            "new_supplier": False, "new_kappa": False,
            "scope": "Exact finite normalized private frees and native chart realization. Physical scalar/COPY/CLEAR, backing ownership, precision/tape, full supplier and all-size obligations remain."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("base", "extra"), required=True)
    parser.add_argument("--artifacts", type=Path, help="reuse generated artifacts with complete source/receipt authentication")
    parser.add_argument("--emit", action="store_true", help="print deterministic evidence instead of comparing committed evidence")
    parser.add_argument("--progress", action="store_true")
    args = parser.parse_args()
    blobs = io.inputs()
    if args.artifacts is None:
        with tempfile.TemporaryDirectory(prefix="peer-private-audit-") as directory:
            run = io.generate(blobs, args.provider, Path(directory))
            result = audit(args.provider, blobs, run, args.progress)
    else:
        result = audit(args.provider, blobs, args.artifacts, args.progress)
    io.require(blobs == io.inputs(), "source inputs stable throughout replay")
    if args.emit:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        expected = io.read(io.PACKAGE / ("RESULT-" + args.provider + ".json"))
        io.require(result == expected, "deterministic complete receipt equality")
        counts = [result["orientations"][o]["native"]["expanded_classes"] for o in ("forward", "backward")]
        print(result["status"] + " provider=" + args.provider + " private_frees=182 native_classes=" + str(sum(counts)))


if __name__ == "__main__":
    main()
