"""Check one cover response at all nine fresh three-leg cuts."""

from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tarfile


HERE = Path(__file__).resolve().parent
BRIDGE = HERE.parent
BASE_PIN = "9510c5624dfb51d98767728084851e4ee75a135e6d7b546569a47fe458485111"
N = 73


def need(test, label):
    if not test:
        raise ValueError(label)


def load():
    path = BRIDGE / "check_bridge_access.py"
    need(sha256(path.read_bytes()).hexdigest() == BASE_PIN, "Phase source pin")
    spec = importlib.util.spec_from_file_location("cycle_cover_phase_source", path)
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    need(sha256(base.ARCHIVE.read_bytes()).hexdigest() == base.ARCHIVE_PIN, "Supplier source archive")
    with tarfile.open(base.ARCHIVE) as archive:
        name, pin = base.MEMBERS["phases"]
        raw = archive.extractfile(name).read()
        need(sha256(raw).hexdigest() == pin, "Actual port and entry phase ledger")
        phases = json.loads(raw)["recipes"]
    return base, phases


def transpose(columns):
    return [sum(((columns[j] >> i) & 1) << j for j in range(N)) for i in range(N)]


def compose(base, left, right):
    return [base.act(left, v) for v in right]


def phase(base, terms, columns=None):
    return base.product([(base.act(columns, v) if columns else v, exponent) for v, exponent in terms])


def difference(base, wanted, given):
    gap = base.add_phase(wanted, base.negative(given))
    need(gap[0] == 0 and gap[2] == 0, "The complete phase defect is a translation")
    return gap[1]


def cut_terms(base, q, v0, stage):
    if not stage:
        return [(q, 1)], [(v0, 1)]
    source = [(v, 1) for v in base.UNIT[:9 + 8 * (stage - 1)]]
    target = source + [(q, -1), (base.UNIT[9 + 8 * (stage - 1)], 1)]
    return source, target


def one_port(base, recipe, port):
    q = recipe["q"]
    basis = base.chart(q)
    need(basis[1:9] == recipe["idle_children"][0]["orthogonal_axes"][:8], "Literal complement chart")
    v0 = basis[1]
    cycle = [q, v0] + [base.UNIT[9 + 8 * j] for j in range(8)]
    need(all((x & y).bit_count() % 2 == int(i == j)
             for i, x in enumerate(cycle) for j, y in enumerate(cycle)), "The ten cycle vectors are orthonormal")
    columns = []
    for e in base.UNIT:
        image = e
        for j, v in enumerate(cycle):
            if (v & e).bit_count() & 1:
                image ^= v ^ cycle[(j + 1) % 10]
        columns.append(image)
    inverse = transpose(columns)
    need(compose(base, columns, inverse) == compose(base, inverse, columns) == base.UNIT,
         "The cycle is orthogonal and both inverse orders hold")
    need([base.act(columns, v) for v in cycle] == cycle[1:] + cycle[:1], "Exact cycle orientation")
    powers = [q]
    for _ in range(10):
        powers.append(base.act(columns, powers[-1]))
    need(powers[-1] == q and len(set(powers[:-1])) == 10, "The cycle has order ten")
    cuts = []
    for stage in range(9):
        source, target = cut_terms(base, q, v0, stage)
        source_phase = phase(base, source)
        target_phase = phase(base, target)
        transported_target = phase(base, target, inverse)
        delta = difference(base, transported_target, source_phase)
        need(base.add_phase(source_phase, base.line(delta, 2)) == transported_target,
             "The literal translation gives the complete physical transfer")
        rho = base.route(basis, stage)
        if stage:
            entry = base.act(rho, recipe["stage_alignment"][stage]["entry_X"])
            need(recipe["stage_alignment"][stage]["entry_X"] == recipe["stage_alignment"][stage]["entry_Y"],
                 "Both current entries use the same translation")
        else:
            entry = 0
        exterior = [(v, 1) for v in base.UNIT[9:9 + 8 * stage]]
        need(base.add_phase(phase(base, source, rho), base.line(entry, 2))
             == phase(base, exterior + [(q, 1)]), "Actual source cut is exterior times C_q")
        need(base.add_phase(phase(base, target, rho), base.line(entry, 2))
             == phase(base, exterior + [(v0, 1)]), "Actual target cut is exterior times C_v0")
        body_route = compose(base, rho, compose(base, inverse, rho))
        need(compose(base, rho, body_route) == compose(base, inverse, rho), "Source-body to target-body equation")
        need(compose(base, body_route, transpose(body_route)) == base.UNIT, "The body route is a cover permutation")
        cuts.append({"stage": stage, "source_rank": 8 * stage + 1,
                     "target_rank": 8 * stage + 1, "translation_in_source_cover_coordinates": delta,
                     "source_body_to_target_body_columns": body_route,
                     "entry_translation_after_route": entry,
                     "omitted_translation_fails": source_phase != transported_target})
    full = [(v, 1) for v in base.UNIT]
    forward_source_delta = difference(base, phase(base, full, inverse), phase(base, full))
    forward_output_delta = base.act(columns, forward_source_delta)
    need(forward_output_delta == difference(base, phase(base, full), phase(base, full, columns)),
         "FULL forward source and output conventions agree")
    inverse_output_delta = difference(base, phase(base, full), phase(base, full, inverse))
    need(inverse_output_delta == forward_source_delta, "FULL inverse correction")
    need(base.act(inverse, q) == cycle[-1], "The decoder source line is the first axis of E8")
    return {"port": port, "q": q, "v0": v0, "cycle_vectors": cycle,
            "L_columns": columns, "L_inverse_columns": inverse, "stage_cuts": cuts,
            "FULL_E_output_translation": forward_output_delta,
            "FULL_E_inverse_output_translation": inverse_output_delta,
            "terminal_source_line_at_output_h": cycle[-1], "terminal_target_line_at_output_h": q}


def main():
    base, phases = load()
    records = [one_port(base, recipe, p) for p, recipe in enumerate(phases)]
    need(len(records) == 112, "All supplier ports")
    payload = {"schema": "common-cycle-cover-response-v1", "phase_source_sha256": BASE_PIN,
               "source_phase_member_sha256": base.MEMBERS["phases"][1],
               "logical_operator": "(E f)_p(h)=f_p(h L_p)",
               "logical_inverse": "(E^-1 f)_p(h)=f_p(h L_p^-1)",
               "payload_action_of_logical_code": "identity", "records": records}
    raw = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode()
    (HERE / "CYCLE-COVER-PROGRAMS.json").write_bytes(raw)
    receipt = {"status": "PASS_COMMON_CYCLE_COVER_RESPONSE", "ports": 112,
               "stages_per_port": 9, "complete_translation_phase_checks": 1008,
               "entry_frame_checks": 2016, "body_route_bijections": 1008,
               "FULL_code_phase_checks": 224, "cycle_order": 10,
               "nonzero_cut_translation_controls": sum(c["omitted_translation_fails"] for r in records for c in r["stage_cuts"]),
               "native_mass_per_fresh_local_call": 1792, "fresh_child_profile": {"1": 112, "7": 112, "8": 112},
               "new_native_children_for_transfer": 0, "transfer_complex_ADDs": 112,
               "terminal_rank_one_children_per_four_pair_replica": 896,
               "source_archive_sha256": base.ARCHIVE_PIN, "phase_source_sha256": BASE_PIN,
               "program_sha256": sha256(raw).hexdigest(),
               "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "scope": "Actual cover and complete phase interface. Fresh native leg emission, global schedule, and full price are separate dependencies."}
    (HERE / "CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
