#!/usr/bin/env python3
"""Caller-domain admissibility of the published cut-9047 witnesses.

Standard library only. Does not replay the native word and does not change kappa.
The coframed rows are the pinned #5546 table. The entrance is the pinned #5402
input basis, preceded by scalar 2 on each mode owner.
"""
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORD = ROOT / "research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz"
PROVIDER = ROOT / "research/native-rank8-helper-provider/PROVIDER.json"
ROWS = ROOT / "research/shared-crossing-cut9047-20261025/expected/RESULT.json"
WORD_SHA = "7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05"
PAYLOAD_SHA = "cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd"
PROVIDER_SHA = "676de7551d3364598f4a7e29ae97cae0e4364348786bbe70435b84294ba7dd65"
ROWS_SHA = "70a30ac467a8d9a2b15e54d88b519258ef5bfff98fed11832a208c31c4fd0c81"
MODES = (224, 225, 227, 229, 240, 241, 256, 257)


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sparse_add(row, key, coefficient):
    value = row.get(key, F(0)) + coefficient
    if value:
        row[key] = value
    else:
        row.pop(key, None)


def load():
    require(sha256(WORD) == WORD_SHA, "ACTUAL-WORD compressed hash")
    payload = gzip.decompress(WORD.read_bytes())
    require(hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA, "ACTUAL-WORD payload hash")
    require(sha256(PROVIDER) == PROVIDER_SHA, "PROVIDER.json hash")
    require(sha256(ROWS) == ROWS_SHA, "#5546 RESULT.json hash")
    provider = json.loads(PROVIDER.read_text(encoding="utf-8"))
    result = json.loads(ROWS.read_text(encoding="utf-8"))
    require(provider["source_payload_sha256"] == PAYLOAD_SHA, "provider binds the same word payload")
    require(result["source_decompressed_sha256"] == PAYLOAD_SHA, "#5546 rows bind the same word payload")
    require(result["source_compressed_sha256"] == WORD_SHA, "#5546 rows bind the compressed word")
    require(tuple(provider["mode_owners"]) == MODES, "eight mode owners")
    roles = provider["basis_roles"]
    require(len(roles) == len(set(roles)) == 122, "122 distinct basis owners")
    require(set(MODES) <= set(roles), "modes lie in the basis")
    require(all(224 <= owner < 632 for owner in roles), "basis owners are helpers")
    program = provider["input_basis_program"]
    require(len(program) == 834, "834 entrance instructions")
    require(all(ins[0] in ("add", "scale") for ins in program), "basis uses only add and scale")
    require(all(F(ins[2]) != 0 for ins in program if ins[0] == "scale"), "every scale is nonzero")
    touched = set()
    for ins in program:
        if ins[0] == "add":
            touched.add(ins[1])
            touched.add(ins[2])
        else:
            touched.add(ins[1])
    require(touched == set(roles), "basis support equals basis_roles")
    return provider, result, roles, program


def published_rows(result):
    rows = {}
    for owner, terms in result["selected_rows"].items():
        row = {}
        for term in terms:
            require(term["warp_word"] == [], "published rows are empty-warp")
            key = int(term["input"][1:])
            require(term["input"] == "L" + str(key), "published input name")
            sparse_add(row, key, F(term["numerator"], term["denominator"]))
        rows[int(owner)] = row
    require(set(rows) == {19, 300, 301}, "coframed owners L19, L300, L301")
    require(rows[19] == {19: F(1)}, "row D")
    require(rows[300] == {19: F(1), 293: F(1, 2), 298: F(-1), 300: F(1), 505: F(1, 4)}, "row R300")
    require(rows[301] == {
        19: F(1), 226: F(-1), 288: F(-1, 2), 293: F(1, 2), 296: F(1, 2),
        298: F(-1), 301: F(1), 302: F(-1, 2), 303: F(1),
    }, "row R301")
    return rows


def warp_blind(program, public):
    """Rational owner map: scale each mode by 2, then run the basis in place."""
    state = {owner: coefficient for owner, coefficient in public.items() if coefficient}
    for owner in MODES:
        if owner in state:
            state[owner] *= 2
            if state[owner] == 0:
                state.pop(owner)
    for ins in program:
        if ins[0] == "add":
            destination, source, coefficient = ins[1], ins[2], F(ins[3])
            if source in state:
                sparse_add(state, destination, coefficient * state[source])
        else:
            field, coefficient = ins[1], F(ins[2])
            if field in state:
                updated = state[field] * coefficient
                if updated:
                    state[field] = updated
                else:
                    state.pop(field)
    return state


def bare_columns(roles, program):
    """Empty-warp columns of non-mode public helpers. Mode keys are omitted."""
    rows = {}
    for owner in roles:
        rows[owner] = {(owner, "mode"): F(2)} if owner in MODES else {(owner, "bare"): F(1)}
    for ins in program:
        if ins[0] == "add":
            destination, source, coefficient = ins[1], ins[2], F(ins[3])
            for key, value in rows[source].items():
                sparse_add(rows[destination], key, coefficient * value)
        else:
            field, coefficient = ins[1], F(ins[2])
            rows[field] = {
                key: value * coefficient
                for key, value in rows[field].items()
                if value * coefficient
            }
    columns = {}
    for source in roles:
        if source in MODES:
            continue
        column = {}
        for owner, terms in rows.items():
            coefficient = terms.get((source, "bare"), F(0))
            if coefficient:
                column[owner] = coefficient
        columns[source] = column
    return columns


def empty_warp_image(columns, public):
    image = {}
    for source, coefficient in public.items():
        if coefficient == 0:
            continue
        require(source not in MODES, "empty-warp witness sets every mode input to zero")
        column = columns.get(source)
        if column is None:
            sparse_add(image, source, coefficient)
        else:
            for owner, value in column.items():
                sparse_add(image, owner, coefficient * value)
    return image


def dots(rows, image):
    return {
        owner: sum(image.get(native, F(0)) * coefficient for native, coefficient in row.items())
        for owner, row in rows.items()
    }


def rank(program, roles):
    columns = [warp_blind(program, {owner: F(1)}) for owner in roles]
    matrix = [[column.get(owner, F(0)) for column in columns] for owner in roles]
    width = len(roles)
    rank_value = 0
    for column in range(width):
        pivot = None
        for row in range(rank_value, width):
            if matrix[row][column] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank_value], matrix[pivot] = matrix[pivot], matrix[rank_value]
        lead = matrix[rank_value][column]
        matrix[rank_value] = [value / lead for value in matrix[rank_value]]
        for row in range(width):
            if row == rank_value:
                continue
            factor = matrix[row][column]
            if factor == 0:
                continue
            matrix[row] = [
                matrix[row][index] - factor * matrix[rank_value][index]
                for index in range(width)
            ]
        rank_value += 1
    return rank_value


def controls(program, roles, rows, columns):
    rejected = []
    broken = [list(ins) for ins in program]
    scale = next(ins for ins in broken if ins[0] == "scale")
    scale[2] = "0"
    require(rank(broken, roles) < 122, "a zero scale must drop the entrance rank")
    rejected.append("zero_scale_drops_rank")

    leaked = empty_warp_image(columns, {300: F(1), 505: F(-4)})
    require(dots(rows, leaked) == {19: F(0), 300: F(0), 301: F(-3, 8)}, "uncorrected witness leaves R301=-3/8")
    require(leaked.get(300) == 1 and leaked.get(505) == -4, "uncorrected image still moves L300 and L505")
    rejected.append("verbatim_L300_witness_not_an_empty_warp_separator")

    wrong_505 = empty_warp_image(columns, {300: F(1), 505: F(-3), 226: F(-3, 8)})
    require(dots(rows, wrong_505)[300] != 0, "a wrong L505 coefficient must move R300")
    rejected.append("wrong_L505_coefficient")

    cleared = empty_warp_image(columns, {505: F(-4), 226: F(-3, 8)})
    require(cleared.get(300, F(0)) == 0, "without public L300 the pure coordinate stays fixed")
    rejected.append("missing_public_L300")
    return rejected


def main():
    provider, result, roles, program = load()
    rows = published_rows(result)
    require(rank(program, roles) == 122, "owner-rational entrance rank")
    blind = warp_blind(program, {300: F(1), 240: F(-1, 2), 505: F(-4)})
    require(blind == {300: F(1), 505: F(-4)}, "warp-blind preimage of the published L300 witness")
    blind_301 = warp_blind(program, {301: F(1), 226: F(1)})
    require(blind_301 == {301: F(1), 226: F(1)}, "warp-blind image of the published L301 witness")

    columns = bare_columns(roles, program)
    require(300 in roles and 300 not in MODES, "L300 is a bare basis helper")
    for owner in (226, 293, 301, 505):
        require(owner not in roles and owner not in MODES and owner >= 224, "free helper " + str(owner))
    require(19 < 224 and 19 not in roles, "L19 is a main and is not mixed by the basis")
    require(columns[300].get(300) == 1, "public L300 reaches native L300 with coefficient 1")
    require(all(source == 300 or columns[source].get(300, F(0)) == 0 for source in columns),
            "no other bare public reaches native L300")

    corrected = empty_warp_image(columns, {300: F(1), 505: F(-4), 226: F(-3, 8)})
    require(dots(rows, corrected) == {19: F(0), 300: F(0), 301: F(0)}, "corrected bare witness fixes every coframed row")
    require(corrected.get(300) == 1 and corrected.get(301, F(0)) == 0, "corrected witness moves only the L300 target")
    carried = empty_warp_image(columns, {301: F(1), 226: F(1)})
    require(carried == {301: F(1), 226: F(1)}, "L301 witness is unchanged by the entrance")
    require(dots(rows, carried) == {19: F(0), 300: F(0), 301: F(0)}, "L301 witness fixes every coframed row")
    rejected = controls(program, roles, rows, columns)
    print("PASS_CUT9047_CALLER_WITNESS_DOMAIN")
    print(json.dumps({
        "entrance_rank": 122,
        "warp_blind_L300_public": {"L300": "1", "L240": "-1/2", "L505": "-4"},
        "empty_warp_L300_public": {"L300": "1", "L505": "-4", "L226": "-3/8"},
        "empty_warp_L301_public": {"L301": "1", "L226": "1"},
        "verbatim_empty_warp_R301": "-3/8",
        "controls": rejected,
        "new_kappa": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
