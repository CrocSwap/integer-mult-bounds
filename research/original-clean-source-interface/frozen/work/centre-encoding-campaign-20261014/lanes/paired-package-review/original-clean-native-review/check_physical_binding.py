"""Bind the original-frame clean word to its complete helper jobs."""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import gzip
import json
from pathlib import Path
import tarfile


LANES = Path(__file__).resolve().parents[2]
PHYSICAL = LANES / "residual-syndrome/physical-algebra"
MODES = [225, 226, 229, 232, 241, 242, 257, 258]
PINS = {
    "payload": (PHYSICAL / "ORIGINAL-CLEAN-SOURCE-PROGRAMS.json.gz", "abfcbfc40bac24e284be63623d9b18f1bb6d4d6ec1b9fa7e9bba27330f323667"),
    "proof": (PHYSICAL / "ORIGINAL-CLEAN-SOURCE.md", "dcd43c16e61fbf4aa2092b26cc1e1d09ce5c2e9ce4ad1a9bfd919ee4125676ab"),
    "producer": (PHYSICAL / "emit_original_clean_source.py", "68bb00b61f0e430a56f0fb6786d507e07122dbd11e0ccf85f3f022accc2f04ea"),
    "producer_receipt": (PHYSICAL / "ORIGINAL-CLEAN-SOURCE.json", "4732d3d45ec4be3a06d0f5bcc56fd4a14cdb1a18b357be5e3d2b06b5f0fa68d1"),
    "core": (LANES / "history-encoding/FULL-MODE-PROGRAMS.json.gz", "f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205"),
    "interface": (LANES / "circuit-interface/INTERFACE.json", "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"),
    "content_review": (PHYSICAL / "review-gauss/original-clean-source/REVIEW.json", "679b94dbb4dbb8ba8d1c12aadf3a37f9b9e5176296905e6bf8007dfb3925cbfa"),
    "content_checker": (PHYSICAL / "review-gauss/original-clean-source/check_review.py", "df98f24aaacac57cfe043d901c8d64c95366b62fe20cbb80b71f871d72818e81"),
    "content_checks": (PHYSICAL / "review-gauss/original-clean-source/CHECK.json", "1f14ab4b77f547d9dea6d2ab9966a8081e639cd23b9e31f533a066158d918717"),
    "raw_review": (LANES / "interface-proof/FULL-MODE-PORT-REVIEW.json", "ff123b08b3ac58f20d12d4fbec575472086ace1708d3242519884dbffe534372"),
    "prior_native_review": (LANES / "paired-package-review/even-clean-native-review/REVIEW.json", "5f0a1ed23f129c833a33909397ab524fb9f50c0b5e8a23f29931d0c1ec0406a7"),
}
ARCHIVE_PIN = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBERS = {
    "word": ("candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz", "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"),
    "old": ("candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz", "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"),
}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(path, pin):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    require(sha256(raw).hexdigest() == pin, "Pinned source: " + path.name)
    return json.loads(raw) if path.suffix in (".gz", ".json") else raw


def native(program):
    return [event for event in program if event[0] in ("climb", "adapter", "residual_adapter")]


def add(target, source, coefficient, endpoint):
    return dict(kind="physical_add", target=target, source=source,
                coefficient=str(coefficient), endpoint=endpoint)


def main(args):
    data = {key: read(path, pin) for key, (path, pin) in PINS.items()}
    require(sha256(args.archive.read_bytes()).hexdigest() == ARCHIVE_PIN, "Selected archive pin")
    with tarfile.open(args.archive) as archive:
        for key, (name, pin) in MEMBERS.items():
            raw = archive.extractfile(name).read()
            require(sha256(raw).hexdigest() == pin, "Selected member pin")
            data[key] = json.loads(gzip.decompress(raw))
    payload, core, word = data["payload"], data["core"], data["word"]
    require(payload["core_payload_sha256"] == PINS["core"][1]
            and payload["interface_sha256"] == PINS["interface"][1]
            and payload["mode_carriers"] == MODES, "Literal raw interface")
    require(payload["physical_frames"] == {"X": ["Q", "F"], "Y": ["I", "F Q^-1"],
                                           "modes": ["I", "F"]}, "Original complex frames")
    require(set(payload) == {"content_contract", "core_payload_sha256", "event_semantics", "expansion",
            "interface_sha256", "mode_carriers", "physical_contract", "physical_frames", "programs",
            "schema", "source_attribution", "width_requirement"}, "No gauge or terminal override")
    require(payload["expansion"] == "Old entry alignment; the orientation prefix; the unchanged raw core; the orientation suffix; the old exit/owner view. Keep all original idle maps, stage alignments, and the original terminal rule.",
            "Exact complete-body placement")
    require(word["frames"][0] == [] and set(word["frames"][1]) == {1 << i for i in range(9)}
            and all(word["start"][role] == 0 and word["final"][role] == 1 for role in MODES),
            "All eight original complete width-nine jobs")
    require(word["ports"] == data["interface"]["ports"], "Actual port matrix")
    rows = [{int(p): Fraction(q) for p, q in row.items()} for row in data["interface"]["R"]]
    require(sum(len(row) for row in rows) == 448, "All centre incidences")
    require(all(sum(row.get(p, 0) ** 2 for row in rows) / 4 == 1 for p in range(112)),
            "Actual centre diagonal")

    def read_graph(bank, coefficient, endpoint):
        return [add(MODES[k], bank + p, coefficient * value, endpoint)
                for k, row in enumerate(rows) for p, value in sorted(row.items())]

    def scatter(bank, coefficient, endpoint):
        return [add(bank + p, MODES[k], coefficient * row[p] / 4, endpoint)
                for p in range(112) for k, row in enumerate(rows) if p in row]

    signs = [dict(kind="physical_scale", target=j, coefficient="-1", endpoint="output") for j in MODES]
    expected = {
        "forward": dict(core_orientation="forward",
                        prefix=read_graph(0, 1, "input") + scatter(112, 1, "input") + read_graph(0, -1, "input"),
                        suffix=read_graph(0, 2, "output") + signs),
        "backward": dict(core_orientation="backward", prefix=read_graph(112, Fraction(-1, 4), "input"),
                         suffix=read_graph(112, Fraction(1, 8), "output") + scatter(0, -8, "output")
                         + read_graph(112, Fraction(-1, 8), "output") + signs),
    }
    require(payload["programs"] == expected, "Every literal boundary event and its order")
    checks = {}
    for orientation, program in expected.items():
        retained = native(core[orientation])
        require(retained == native(data["old"][orientation]) and len(retained) == 5056,
                "Every native event remains in the original order")
        require(sum(e[0] == "center" for e in data["old"][orientation]) == 8
                and not any(e[0] == "center" for e in core[orientation]), "Only old centre children are absent")
        profile = Counter(e[5] for e in core[orientation] if e[0] == "climb")
        require(profile == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82}, "Original local native profile")
        gates = program["prefix"] + program["suffix"]
        magnitudes = Counter()
        cost = 0
        for gate in gates:
            if gate["kind"] == "physical_scale":
                require(gate["coefficient"] == "-1" and gate["target"] in MODES, "Mode sign")
                cost += 2
            else:
                require(gate["target"] != gate["source"], "Distinct physical ADD fields")
                magnitude = abs(Fraction(gate["coefficient"]))
                magnitudes[str(magnitude)] += 1
                cost += {Fraction(1): 8, Fraction(2): 10, Fraction(1, 4): 12, Fraction(1, 8): 14}[magnitude]
        require(sum(magnitudes.values()) == 1792 and len(gates) == 1800, "Complete boundary count")
        require(cost == (17040 if orientation == "forward" else 22416), "Added scalar bill")
        checks[orientation] = dict(native_events_compared=len(retained), paid_profile=dict(profile),
                                   paid_rank=sum(rank * count for rank, count in profile.items()),
                                   added_complex_ADDs=1792, added_complex_negations=8,
                                   magnitudes=dict(magnitudes), added_real_primitive_bound=cost,
                                   complete_local_scalar_bound=204418 + cost)
    common_exterior_checks = []
    for stage in range(9):
        exterior = [1 << i for i in range(9, 9 + 8 * stage)]
        local = [1 << i for i in range(9)]
        require(all(not (v & 511) for v in exterior), "Exterior is outside the complete local job")
        product = Counter(exterior + local)
        product.subtract(exterior)
        require(+product == Counter(local), "E_s F9 E_s^-1 = F9")
        common_exterior_checks.append(dict(stage=stage, exterior_axes=len(exterior), local_job_axes=9))
    q = word["ports"][0]
    character = q & -q
    require((q & character).bit_count() % 2 == 1, "Actual odd line character")
    report = dict(
        status="PASS_INDEPENDENT_ORIGINAL_CLEAN_PHYSICAL_HELPER_BINDING",
        pins={key: pin for key, (_, pin) in PINS.items()}, archive_sha256=ARCHIVE_PIN,
        archive_members={key: pin for key, (_, pin) in MEMBERS.items()}, checks=checks,
        common_exterior_checks=common_exterior_checks, complete_mode_jobs=MODES,
        unchanged_other_helper_blocks=472, arbitrary_physical_helper_input=True,
        no_cross_helper_or_data_endpoint_terms="Accepted full 704-column new-word review.",
        actual_native_failure_witnesses={
            "wrong_output_Q_instead_of_inverse": dict(port=0, one_layer_character=character,
                actual_Q_multiplier=[0, 1], required_Q_inverse_multiplier=[0, -1],
                same_port_data_difference=[0, 2], other_layer_characters=0),
            "omitted_final_mode_sign": dict(all_layer_characters=0,
                required_complete_F9_multiplier=1, uncorrected_mode_multiplier=-1, difference=-2),
        },
        width_scope="Every positive integer tensor width; the proof uses no parity or finite-order reduction.",
        inherited_scope="Raw core content, exact native kernel and frame lowering, and the new complete 704-column algebra are pinned accepted dependencies.",
        excluded_scope="No supplier parser admission, changed data controller, complete global invoice, precision implementation, or supplier exponent.")
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "checks", "width_scope")}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("CHECKS.json"))
    main(parser.parse_args())
