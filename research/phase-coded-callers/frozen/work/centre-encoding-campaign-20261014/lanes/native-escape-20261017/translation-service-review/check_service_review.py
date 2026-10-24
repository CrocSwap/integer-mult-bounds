"""Review the literal one-field translation service without producer imports."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "owner-review/centre-schur-probe"
PINS = {
    "TRANSLATION-SERVICE.md": "57d38fd23aae563b107f4924250fb975f2d4f9b6bcc5357735943ff10527a0d0",
    "TRANSLATION-SERVICE.json": "45273e561954139ece2c40697cc2d419aabc4db01c2013a38ef5379f35cc6599",
    "check_translation_service.py": "18cae3387c3a83c716ce2a43e47ec082ce72904e1a2516944278ab032c5de2a8",
    "TRANSLATION-SERVICE-PROGRAMS.json.gz": "7566388bfb2167b21a5632cd12f4f71004df9c95d5d823f2f0604a6d0847d0e5",
    "SCHUR-PROBE.json": "ebff70f4ff3d28c345080a4d7b1d90cd952a6208b7f6449037b96dbf3531c024",
}
A = [0, 7, 20, 27, 36, 46, 57, 111]
ODD_PATH = HERE.parents[1] / "independent-review-20261017/odd-grid-a8-20261017/A8-ODD-GRID.md"
ODD_PIN = "e0210105ba6c6246f1f84c8ce2d92cfd07aa6cc8a161ca27d7fcc8e0183cfb01"


def need(ok, label):
    if not ok:
        raise ValueError(label)


def read(path, pin):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == pin, "Source hash: " + str(path))
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


for name, pin in PINS.items():
    need(sha256((SOURCE / name).read_bytes()).hexdigest() == pin, "Frozen producer input")
need(sha256(ODD_PATH.read_bytes()).hexdigest() == ODD_PIN, "Exact odd-grid backend source")
receipt = read(SOURCE / "TRANSLATION-SERVICE.json", PINS["TRANSLATION-SERVICE.json"])
payload = read(SOURCE / "TRANSLATION-SERVICE-PROGRAMS.json.gz", PINS["TRANSLATION-SERVICE-PROGRAMS.json.gz"])
probe = read(SOURCE / "SCHUR-PROBE.json", PINS["SCHUR-PROBE.json"])
primary = {key: read(Path(item["path"]), item["sha256"]) for key, item in receipt["source_pins"].items()}


def accumulate(target, key, value):
    result = target.get(key, F(0)) + value
    if result:
        target[key] = result
    else:
        target.pop(key, None)


def body_kernel(word):
    # Only C0 has an address code. The eight sources stay unchanged.
    scratch = {(16, 0): F(1)}
    outputs = [{(8 + i, 0): F(1)} for i in range(8)]
    invoice = Counter()
    maximum = F(1)
    for gate in word:
        kind, target = gate[:2]
        need(target == 16 or 8 <= target < 16, "Only C0 and target bank can change")
        invoice[kind] += 1
        if kind == "ADD":
            source, coefficient = gate[2], F(gate[3])
            need(abs(coefficient) in (1, F(1, 2)), "Admitted scalar ADD")
            invoice["scalar_primitives"] += 8 if abs(coefficient) == 1 else 10
            if target == 16:
                need(0 <= source < 8, "A source read for C0")
                accumulate(scratch, (source, 0), coefficient)
            else:
                need(source == 16, "Every target update uses C0")
                for key, value in scratch.items():
                    accumulate(outputs[target - 8], key, coefficient * value)
        elif kind == "COPY":
            need(target == 16 and 0 <= gate[2] < 8, "Copy one unchanged source")
            scratch = {(gate[2], 0): F(1)}
            invoice["scalar_primitives"] += 2
        elif kind == "CLEAR":
            need(target == 16, "Only owned C0 is clearable")
            scratch = {}
            invoice["scalar_primitives"] += 2
        elif kind == "SCALE2":
            need(target == 16 and gate[2] in (-1, 1), "One binary scale on C0")
            scratch = {key: F(2)**gate[2] * value for key, value in scratch.items()}
            invoice["scalar_primitives"] += 2
        elif kind == "DIVIDE_ODD":
            need(target == 16 and gate[2] == 2145, "Exact fixed odd division")
            scratch = {key: value / 2145 for key, value in scratch.items()}
            invoice["real_odd_division_scans"] += 2
        else:
            need(kind == "TRANSLATE" and target == 16 and 0 < gate[2] < 512, "A literal native-zero translation")
            scratch = {(origin, delta ^ gate[2]): value for (origin, delta), value in scratch.items()}
            invoice["translation_maps"] += 1
        row = scratch if target == 16 else outputs[target - 8]
        maximum = max(maximum, sum(map(abs, row.values())))
    need(not scratch, "Owned zero endpoint")
    need(not any(origin == 16 for row in outputs for origin, delta in row), "Arbitrary owned input does not reach data")
    return outputs, dict(invoice), str(maximum)


words = payload["bodies"]
checked = {}
for kind in ("T", "few_maps", "few_scalars"):
    entries = probe["kernels"]["translation" if kind == "T" else "inverse"]["entries"]
    for sign, suffix in ((1, "plus"), (-1, "minus")):
        name = kind + "_" + suffix
        expected = [{(8 + i, 0): F(1)} for i in range(8)]
        for delta, target, source, value in entries:
            accumulate(expected[target], (source, delta), sign * F(value))
        actual, invoice, maximum = body_kernel(words[name])
        need(actual == expected, "All arbitrary live and owned columns: " + name)
        wanted = receipt["cases"][name]
        need(all(wanted["counts"][key] == value for key, value in invoice.items()), "Literal complete invoice: " + name)
        need(maximum == wanted["maximum_intermediate_row_one_norm"], "Prefix coefficient bound: " + name)
        checked[name] = dict(invoice=invoice, maximum_row_norm=maximum)


def exchange_banks(word):
    result = []
    for instruction in word:
        instruction = list(instruction)
        if instruction[1] < 16:
            instruction[1] = (instruction[1] + 8) % 16
        if instruction[0] in ("ADD", "COPY") and instruction[2] < 16:
            instruction[2] = (instruction[2] + 8) % 16
        result.append(instruction)
    return result


for kind in ("few_maps", "few_scalars"):
    for suffix, opposite in (("plus", "minus"), ("minus", "plus")):
        first = exchange_banks(words["T_" + suffix])
        middle = words[kind + "_" + opposite]
        name = "exchange_" + kind + "_" + suffix
        need(words[name] == first + middle + first, "Literal exchange has exactly the three checked shears")
        counts = Counter(checked["T_" + suffix]["invoice"])
        counts.update(checked[kind + "_" + opposite]["invoice"])
        counts.update(checked["T_" + suffix]["invoice"])
        need(dict(counts) == receipt["cases"][name]["counts"], "Exchange invoice includes every instruction")
        checked[name] = dict(invoice=dict(counts))


def apply(columns, vector):
    result = 0
    for i, column in enumerate(columns):
        if vector >> i & 1:
            result ^= column
    return result


view_table = {(view["stage"], view["port"]): view for view in primary["views"]["views"] if view["side"] == "X" and view["port"] in A}
need(len(view_table) == 64, "All selected completed views")
for (stage, port), view in view_table.items():
    columns, delta = view["route_columns"], view["translation_after_route"]
    need(len(columns) == 73, "Native address dimension")
    transpose = [sum(((column >> i) & 1) << j for j, column in enumerate(columns)) for i in range(73)]
    need([apply(columns, column) for column in columns] == [1 << i for i in range(73)], "Route inverse")
    need(columns == transpose, "Orthogonal symmetric route")
    need(apply(columns, view["translation_before_route"]) == delta, "Correct affine order")
    def phase(character):
        return (apply(transpose, character).bit_count() + 2 * (delta & character).bit_count() - character.bit_count()) % 4
    need(phase(0) == 0, "Zero phase constant")
    need(all(phase(1 << i) == 0 for i in range(73)), "All linear phase coefficients")
    need(all(phase((1 << i) | (1 << j)) == 0 for i in range(73) for j in range(i)), "All quadratic phase coefficients")
for stage in range(1, 9):
    enter = [["VIEW", row, stage, A[row % 8], False] for row in range(16)]
    leave = [["VIEW", row, stage, A[row % 8], True] for row in reversed(range(16))]
    need(payload["stage_wrappers"][str(stage)] == dict(enter=enter, leave=leave), "Exact complete physical wrapper")

need(receipt["rank_one_children"] == receipt["native_wrapper_maps"] == 0, "No omitted native calls")
need(receipt["completed_view_maps_per_call"] == 32, "All physical view maps charged")
for name, pin in PINS.items():
    need(sha256((SOURCE / name).read_bytes()).hexdigest() == pin, "Frozen producer input unchanged")
result = dict(status="PASS_INDEPENDENT_TRANSLATION_SERVICE_REVIEW", source_pins=PINS,
              odd_grid_source=dict(path=str(ODD_PATH), sha256=ODD_PIN),
              all_live_columns=16, arbitrary_owned_inputs=1, untouched_borrowed_fields="Every owner outside 0..16",
              completed_view_checks=64, body_checks=checked,
              exchange_method="Literal three-shear decomposition plus independently checked all-width T inverse",
              full_supplier_admission=False, checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
(HERE / "REVIEW.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(result["status"])
