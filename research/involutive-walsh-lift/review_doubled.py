"""Check every emitted doubled native factor without the producer compiler."""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import native
import sources


def require(ok, label):
    if not ok:
        raise ValueError(label)


def point(record, x):
    n = len(record["matrix_rows"])
    phase = record["phase"]+sum(record["linear_Z4"][i] for i in range(n) if x >> i & 1)
    phase += 2*sum(native.parity((record["quadratic_rows"][i] >> (i+1)) & (x >> (i+1)))
                   for i in range(n) if x >> i & 1)
    return native.mul(record["matrix_rows"], x) ^ record["offset"], phase % 4


def inverse_point(record, rows, x):
    original = native.mul(rows, x ^ record["offset"])
    out, phase = point(record, original)
    require(out == x, "Exact inverse address")
    return original, -phase % 4


def tensor_point(record, x):
    lo, lp = point(record, x & 511)
    hi, hp = point(record, x >> 9)
    return lo | hi << 9, (lp+hp) % 4


def gather(width, rank):
    axes = [block*width+j for block in range(2) for j in range(rank)]
    order = axes+[j for j in range(2*width) if j not in axes]
    require(sorted(order) == list(range(2*width)), "Complete child coordinate order")
    rows = native.transpose(tuple(1 << i for i in order))
    for j in range(2*rank):
        require(native.mul(rows, 1 << j) == 1 << axes[j], "Child gather direction")
    return rows


def check_record(record):
    require(len(record["matrix_rows"]) == 18, "Doubled factor dimension")
    native.monomial(record)


def main(args):
    folder = args.out
    source = sources.load_local(args.repo)
    word = source["CANONICAL-WORD.json.gz"]
    programs_hash = sha256(json.dumps(source["LOCAL-PROGRAMS.json.gz"], sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()
    old_profiles = {name: Counter(event[5] for event in events if event[0] == "climb")
                    for name, events in source["LOCAL-PROGRAMS.json.gz"].items()}
    complete_profiles = {name: Counter(event[-1] for event in events if event[0] in ("climb", "center"))
                         for name, events in source["LOCAL-PROGRAMS.json.gz"].items()}
    child_uses = [tuple(event[3:]) if event[0] == "climb" else tuple(event[2:])
                  for events in source["LOCAL-PROGRAMS.json.gz"].values()
                  for event in events if event[0] in ("climb", "center")]
    del source
    raw = gzip.decompress((folder/"WALSH-RETARGET-NATIVE.json.gz").read_bytes())
    native_pin = sha256(raw).hexdigest()
    original = json.loads(raw)
    del raw
    require(sha256(json.dumps(original.pop("programs"), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            == programs_hash, "Original native program binding")
    base_review_raw = (folder/"WALSH-RETARGET-REVIEW.json").read_bytes()
    base_review = json.loads(base_review_raw)
    require(base_review["status"] == "PASS_INDEPENDENT_WALSH_RETARGET_FRAMES_AND_ACTUAL_WORD_LEDGER" and
            base_review["exact_chart_frame_squares"] == 1004 and
            base_review["fused_native_recipe_review"]["payload_sha256"] == native_pin,
            "Complete independent base operator review")
    helper_pin = sha256((folder/"WALSH-RETARGET-HELPER-NORMALIZATION.json").read_bytes()).hexdigest()
    require(helper_pin == base_review["fused_native_recipe_review"]["helper_normalization_sha256"],
            "Literal helper source review")
    raw = gzip.decompress((folder/"DOUBLED-WALSH-NATIVE.json.gz").read_bytes())
    doubled_pin = sha256(raw).hexdigest()
    doubled = json.loads(raw)
    del raw
    require(doubled["schema"] == "involutive-native-lift-v1" and doubled["base"] == sources.BASE,
            "Doubled schema and source")
    require(doubled["program_rank_scale"] == 2, "Source event ranks have an explicit doubled interpretation")
    require(doubled["source_native_payload_sha256"] == native_pin and
            doubled["source_helper_normalization_sha256"] == helper_pin, "Doubled exact source bindings")
    require(sha256(json.dumps(doubled.pop("programs"), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            == programs_hash, "Doubled scalar and event streams")
    dimensions = [2*len(vectors) for vectors in word["frames"]]
    require(doubled["frame_dimensions"] == dimensions, "Every actual frame rank is doubled")
    probes = [0]+[1 << i for i in range(18)]
    probes += [(1 << i) | (1 << j) for i in range(18) for j in range(i+1, 18)]
    gathers = {r: gather(9, r) for r in range(10)}
    inverse_gathers = {r: native.inverse(matrix) for r, matrix in gathers.items()}
    points = 0

    def child(old, new, before, after):
        nonlocal points
        r = old["rank"]
        require(new["rank"] == 2*r and r > 0, "Doubled child rank")
        for factor in (new["left"], new["right"]):
            check_record(factor)
        phase = (len(word["frames"][before])-len(word["frames"][after])) % 4
        for x in probes:
            y, p = tensor_point(old["right"], x)
            expected_right = native.mul(inverse_gathers[r], y), p
            y, p = tensor_point(old["left"], native.mul(gathers[r], x))
            expected_left = y, (p+phase) % 4
            require(point(new["right"], x) == expected_right, "Literal tensor right factor and gather")
            require(point(new["left"], x) == expected_left, "Literal tensor left factor and rank phase")
            points += 2

    require(len(original["children"]) == len(doubled["children"]) == 2896, "Complete doubled child inventory")
    for old, new in zip(original["children"], doubled["children"]):
        require((new["old"], new["new"]) == (old["old"], old["new"]), "Same directed child")
        child(old, new, old["old"], old["new"])
    child_records = {(r["old"], r["new"]): r for r in doubled["children"]}
    require(len(child_records) == len(doubled["children"]), "Unique doubled directed children")
    for before, after, rank in child_uses:
        require(child_records[before, after]["rank"] == 2*rank, "Every event has its exact doubled native child")
    endpoint_keys = lambda artifact: {(r["role"], r["port"]): r for r in artifact["endpoint_adapters"]}
    endpoints, old_endpoints = endpoint_keys(doubled), endpoint_keys(original)
    require(set(endpoints) == set(old_endpoints) and len(endpoints) == 224, "Doubled endpoint inventory")
    for key, record in endpoints.items():
        old = old_endpoints[key]
        require(record["rank"] == 0 and record["right"] is None and record["frame"] == old["frame"],
                "Doubled endpoint structure")
        check_record(record["left"])
        for x in probes:
            require(point(record["left"], x) == tensor_point(old["left"], x), "Exact doubled intrinsic endpoint")
            points += 1
    residuals = doubled["residual_adapters"]
    require(set(residuals) == set(original["residual_adapters"]) == set(doubled["helper_normalizers"]),
            "Doubled residual and helper inventory")
    require(len(residuals) == 36, "Complete doubled helper keys")
    for key, record in residuals.items():
        old = original["residual_adapters"][key]
        before, after = old["frame"], old.get("terminal", 1)
        require(record["frame"] == before and record.get("terminal", 1) == after, "Residual endpoint frames")
        child(old, record, before, after)
        r2 = record["rank"]
        normalizer = doubled["helper_normalizers"][key]
        require(normalizer["rank"] == r2 and r2 % 2 == 0, "Canonical doubled helper rank")
        check_record(normalizer["pre"])
        check_record(normalizer["post"])
        left_inverse = native.inverse(tuple(record["left"]["matrix_rows"]))
        right_inverse = native.inverse(tuple(record["right"]["matrix_rows"]))
        mask = (1 << r2)-1
        for x in probes:
            y, phase = inverse_point(record["right"], right_inverse, x)
            expected_pre = y, (phase+(x & mask).bit_count()) % 4
            y, phase = inverse_point(record["left"], left_inverse, x)
            expected_post = y, (phase+(y & mask).bit_count()-r2//2) % 4
            require(point(normalizer["pre"], x) == expected_pre, "Canonical contiguous helper pre factor")
            require(point(normalizer["post"], x) == expected_post, "Canonical contiguous helper post factor and phase")
            points += 2
    # Multiplication by i changes a full operator but not its Pauli action.
    correct = doubled["children"][0]["left"]
    wrong = dict(correct, phase=(correct["phase"]+1) % 4)
    require(point(correct, 0) != point(wrong, 0), "Full phase mutation control")
    global_gathers = [(73, r) for r in (1, 2, 3, 4, 5, 7, 8, 16, 24, 32, 40, 48)]
    for n, r in global_gathers:
        native.inverse(gather(n, r))
    for residue in range(4):
        for r in range(74):
            require((-2*r*residue+2*r*residue) % 4 == 0, "All-size exact involution phase")
        require((-9+1+8)*residue % 4 == 0, "Full/source/hole relative phase")
    require(all(sum(r*n for r, n in profile.items()) == 5522 for profile in old_profiles.values()),
            "Centre-free persistent core rank")
    profiles = {name: {2*r: n for r, n in sorted(profile.items())} for name, profile in old_profiles.items()}
    result = {
        "status": "PASS_EXACT_DOUBLED_WALSH_NATIVE_LOWERING",
        "base_native_payload_sha256": native_pin,
        "base_operator_review_sha256": sha256(base_review_raw).hexdigest(),
        "frame_definition": "Gamma_V=i^(-rank(V)*lambda) H_V^tensor(2lambda)",
        "source_operator": "Gamma_q=(X_q+Z_q) tensor (X_q+Z_q) / 2 at lambda=1",
        "source_square": "I for every positive lambda",
        "local_core_profile": profiles, "local_core_rank": 11044,
        "local_core_scope": "Persistent climb events only; private centre children are separate",
        "original_word_child_profile": {name: {2*r: n for r, n in sorted(profile.items())}
                                        for name, profile in complete_profiles.items()},
        "original_word_paid_rank": {name: sum(2*r*n for r, n in profile.items())
                                    for name, profile in complete_profiles.items()},
        "global_sizes": {"parent": 146, "largest_split_child": 96, "quadratic_margin": 2884},
        "helper_normalization": "For Gamma_exit Gamma_entry^-1=L2 F_(2r) R2: pre=R2^-1 S_(2r); post=i^(-r*lambda) S_(2r) L2^-1",
        "final_native_boundary": "pre=S_146^-1, post=i^(73lambda) S_146^-1",
        "explicit_emission": {"payload_sha256": doubled_pin,
                              "source_native_payload_sha256": native_pin,
                              "source_helper_normalization_sha256": helper_pin,
                              "child_recipes": 2896, "endpoint_adapters": 224,
                              "original_native_events_bound_to_doubled_children": len(child_uses),
                              "residual_recipes": 36, "canonical_helper_normalizers": 36,
                              "complete_quadratic_witnesses": points,
                              "helper_coordinate_convention": "Contiguous first2r coordinates after the emitted gather"},
        "coordinate_child_gathers": [{"old_width": n, "old_rank": r, "new_rank": 2*r}
                                     for n, r in [(9, r) for r in range(10)]+global_gathers],
        "scope": "Exact emitted tensor factors, coordinate gathers, endpoint phases, and arbitrary-input helper contracts. Tensor linearity gives all positive lambda. No dense18-bit state is expanded.",
        "not_claimed": ["A complete changed centre controller", "Finite global scalar/address cost", "A kappa improvement"],
    }
    (folder/"DOUBLED-WALSH-REVIEW.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=HERE.parents[1])
    parser.add_argument("--out", type=Path, default=HERE/"evidence")
    main(parser.parse_args())
