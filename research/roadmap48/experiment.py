"""Rebuild ROADMAP's 48 frame edits and check their actual accounting.

Only standard-library Python is needed. Supplier admission is deliberately
distinct from local correctness and arithmetic on a hypothetical profile.
Liamia supplied theoretical guidance and corrections; OpenAI Codex performed
the concrete implementation and verification. Apache-2.0.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tarfile

# These retained source packages have exact file inventories. Imports must
# not add bytecode files to them, including under ordinary unittest discovery.
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / "research/community-frontier799-audit/pr799-replay.tar.gz"
ARCHIVE_SHA = "4dff69f3509ca81ab768ebf4b39bb6313b331995e4b2a412729b541a39c8459a"
PREFIX = "pr799-global-fresh/global/"
WORD_MEMBER = PREFIX + "base/providers/gauge44/FULL-WORD.json.gz"
WORD_SHA = "1e1d99ba7aab877d6b573c41f7030ee73de9a52fee51d0a822ddaae71251999f"
OWNER_SHA = "99d1c4caf85855c353d30f122d9efbd9e51562914facded13027f347b18a6082"
FULL = (256, 128, 64, 32, 16, 8, 4, 2, 1)
CENTERS = (60, 61, 63, 224, 31, 240, 23, 256)
HELPERS = (
    (28, 20, 12, 36, 68, 108), (29, 21, 4, 44, 76, 100),
    (13, 37, 5, 45, 92, 84), (69, 109, 77, 101, 93, 85),
    (15, 71, 7, 79, 95, 52), (39, 111, 47, 103, 400, 53),
    (272, 320, 352, 368, 87, 55), (288, 304, 336, 384, 416, 432),
)
OLD_PROFILE = {1: 2548, 2: 338, 3: 430, 4: 194, 5: 56, 8: 8}
NEW_PROFILE = {1: 2492, 2: 338, 3: 430, 4: 138, 5: 112, 9: 8}
ROADMAP_PROFILE = {1: 179425, 2: 24336, 3: 30961, 4: 9936,
                   5: 8064, 9: 576, 44: 1, 48: 2384}
X4_KAPPA = Q("0.001661634653669567")
ROADMAP_KAPPA = Q("0.001672153593380162")


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def dump_compressed(path, value):
    path.write_bytes(gzip.compress(encode(value), mtime=0))


def retain_audit_receipt(path):
    """Retain semantic audit evidence without timing or gzip-container claims."""
    receipt = json.loads(path.read_bytes())
    receipt.pop("elapsed_seconds", None)
    receipt.pop("compressed_sha256", None)
    dump(path, receipt)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUDIT = load_module(ROOT / "research/gauge44-frames-x/independent/audit_local.py", "roadmap_scalar_audit")
PROMOTION = load_module(ROOT / "research/gauge44-frames-x/construction/promo/build_promotion.py", "roadmap_promotion")


@lru_cache(maxsize=32768)
def basis(vectors):
    require(all(type(x) is int and 0 < x < 512 for x in vectors), "invalid F2^9 vector")
    return AUDIT.basis(vectors)


@lru_cache(maxsize=32768)
def join(a, b):
    return basis(a + b)


def ints(profile):
    return {int(k): v for k, v in profile.items()}


def rank_mass(profile):
    return sum(r * n for r, n in ints(profile).items())


def read_source(archive=ARCHIVE):
    require(digest(archive.read_bytes()) == ARCHIVE_SHA, "X4 replay archive pin")
    with tarfile.open(archive) as tar:
        def member(name):
            hits = [m for m in tar.getmembers() if m.name == name]
            require(len(hits) == 1 and hits[0].isfile(), "unique regular replay member: " + name)
            require(hits[0].size <= 16 * 1024 * 1024, "oversize replay member")
            return tar.extractfile(hits[0]).read()
        compressed = member(WORD_MEMBER)
        data = gzip.decompress(compressed)
        require(digest(data) == WORD_SHA, "X4 decompressed word pin")
        word = json.loads(data)
        plan = json.loads(member(PREFIX + "PLAN.json"))
        owners_receipt = json.loads(member(PREFIX + "audit/OWNERS-AND-PROFILE.json"))
    require(ints(word["report"]["local_profile"]) == OLD_PROFILE, "X4 local profile")
    require(word["centers"] == list(CENTERS), "X4 ordered centers")
    return word, plan, owners_receipt


def frame_state(word):
    v, h, R = (word["report"][k] for k in ("v", "h", "R"))
    require((v, h, R) == (112, 9, 504), "source geometry")
    start = [(p,) for p in word["ports"]] + [()] * (v + R)
    for r, f in word["start_extra"].items():
        start[int(r)] = basis(tuple(f))
    end = [FULL] * v + [basis(tuple(x for x in range(1, 512)
                                      if (x & p).bit_count() % 2 == 0))
                       for p in word["ports"]] + [FULL] * R
    for r, f in word["helper_final"].items():
        end[int(r)] = basis(tuple(f))
    return start, end


def replay_frames(word):
    """Literal frame chain including center descents; no declared profile input."""
    cur, end = frame_state(word)
    start = cur.copy()
    paid, events, last = Counter(), [], {}

    def climb(r, frame, phase, index):
        frame = basis(tuple(frame))
        require(join(cur[r], frame) == frame, f"nonmonotone {phase}:{index} register {r}")
        d = len(frame) - len(cur[r])
        if d:
            paid[d] += 1
            events.append(dict(register=r, phase=phase, index=index,
                               before=list(cur[r]), after=list(frame), rank=d,
                               last_touch=last.get(r)))
        cur[r] = frame
        if phase != "END":
            last[r] = [phase, index]

    for part in ("A", "B"):
        if part == "B":
            levels = {int(t): basis(tuple(f)) for t, f in word["target_levels"].items()}
            require(all(cur[112+t] == levels.get(t, ()) for t in range(112)), "target levels")
            for r, frame in zip(word["centers"], word["center_frames"]):
                f = basis(tuple(frame))
                require(cur[r] == f, "center declaration")
                served = {levels.get(e[1]-112, ()) for e in word["cut"] if e[2] == r}
                for smaller in sorted(served, key=lambda x: -len(x)):
                    require(join(f, smaller) == f, "nested center descent")
                    if f != smaller:
                        paid[len(f)-len(smaller)] += 1
                    f = smaller
        for i, gate in enumerate(word[part]):
            for r in AUDIT.registers(gate):
                climb(r, gate[-1], part, i)
    for i, (cleanup_index, frame) in enumerate(word["early_cleanup"]):
        for r in AUDIT.registers(word["cleanup"][cleanup_index]):
            climb(r, frame, "T", i)
    for r, frame in enumerate(end):
        climb(r, frame, "END", r)
    widths = Counter(len(end[r])-len(start[r]) for r in range(224, 728))
    return dict(profile=dict(sorted(paid.items())), mass=rank_mass(paid),
                widths=dict(sorted(widths.items())), events=events)


def refresh_report(word):
    recount = replay_frames(word)
    report = word["report"]
    report["local_profile"] = {str(k): n for k, n in recount["profile"].items()}
    report["local_rank_mass"] = recount["mass"]
    report["width_inventory"] = {str(k): n for k, n in recount["widths"].items()}
    report["centre_ranks"] = [len(basis(tuple(f))) for f in word["center_frames"]]
    report["cst"] = sum(report["centre_ranks"])


def check_report(word):
    recount = replay_frames(word)
    report = word["report"]
    require(ints(report["local_profile"]) == recount["profile"], "paid profile mismatch")
    require(report["local_rank_mass"] == recount["mass"], "local rank mass mismatch")
    require(ints(report["width_inventory"]) == recount["widths"], "width inventory mismatch")
    ranks = [len(basis(tuple(f))) for f in word["center_frames"]]
    require(report["centre_ranks"] == ranks and report["cst"] == sum(ranks), "stale center ranks/cst")
    return recount


def build_word(source):
    """Pinned recipe, using the original promotion builder; repair center fees."""
    require(ints(source["report"]["local_profile"]) == OLD_PROFILE, "X4 base profile")
    require(len(source["A"]) == 4283, "X4 A gate count")
    edits = []
    for block, (center, helpers) in enumerate(zip(CENTERS, HELPERS)):
        old = source["center_frames"][block]
        require(len(basis(tuple(old))) == 8, "X4 center dimension")
        for offset, helper in enumerate(helpers):
            index = 4235 + 6*block + offset
            gate = source["A"][index]
            require(gate[:-1] == ["add", center, helper, 1, 1], "48-gate scalar pin")
            require(basis(tuple(gate[-1])) == basis(tuple(old)), "48-gate frame pin")
            edits.append(["A", index, old, list(FULL)])
    require(digest(encode(source)) == WORD_SHA, "full X4 source content pin")
    recipe = dict(input_content_sha256=WORD_SHA, entrances={}, gate_frames=edits)
    word = PROMOTION.apply(source, recipe)
    word["center_frames"] = [list(FULL) for _ in CENTERS]
    refresh_report(word)  # original builder excludes changed center descents
    require(ints(word["report"]["local_profile"]) == NEW_PROFILE, "48-edit profile")
    require(word["report"]["local_rank_mass"] == 5642, "48-edit rank mass")
    for key in source:
        if key not in {"A", "center_frames", "report"}:
            require(source[key] == word[key], "unexpected mutation: " + key)
    require([e[:-1] for e in source["A"]] == [e[:-1] for e in word["A"]], "changed scalar program")
    recipe["expected"] = dict(output_content_sha256=digest(encode(word)),
                              local_profile=word["report"]["local_profile"],
                              width_inventory=word["report"]["width_inventory"],
                              local_rank_mass=5642, centre_ranks=[9]*8, cst=72)
    return word, recipe


def recount_idle(plan, owners, word):
    """Recount every retained physical owner's occupied cells and remainder."""
    cur, end = frame_state(word)
    widths = [len(end[r])-len(cur[r]) for r in range(224, 728)]
    order = [tuple(x) for x in plan["order"]]
    times = {x: t for t, x in enumerate(order)}
    require(len(times) == len(order) == 72, "72 distinct calls")
    used, helpers, families = defaultdict(set), defaultdict(set), defaultdict(set)
    require(len(owners) == 72*504, "all physical helper roles")
    for z in owners:
        call = (z["stage"], z["replica"])
        h, i, rep, port = (z[k] for k in ("helper", "child", "owner_replica", "port"))
        require(call in times and 0 <= h < 504 and 0 <= rep < 8 and 0 <= port < 112, "owner domain")
        require(z["time"] == times[call] and h not in helpers[call], "unique timed helper")
        require(z["family"] not in families[call], "one helper per family")
        helpers[call].add(h); families[call].add(z["family"])
        cap, allowed = plan["windows"][f"{rep},{i}"]
        require(z["time"] in allowed and z["width"] == widths[h], "owner width/window")
        require(z["copy"] == rep*112+port, "owner copy identity")
        family = rep*896+(2*plan["pairs"][str(i)]+plan["sides"][str(i)])*112+port
        require(z["family"] == family, "owner family identity")
        off, width = z["offset"], z["width"]
        require(0 <= off and off+width <= cap, "owner capacity")
        cells = set(range(off, off+width))
        key = (i, rep, port)
        require(not used[key] & cells, "owner cell overlap")
        used[key].update(cells)
    require(set(helpers) == set(order) and all(hs == set(range(504)) for hs in helpers.values()), "complete owner calls")
    idle = Counter()
    for key, (cap, _) in plan["windows"].items():
        rep, i = map(int, key.split(","))
        for port in range(112):
            cells = used[i, rep, port]
            require(cells == set(range(len(cells))), "contiguous occupied owner cells")
            left = cap-len(cells)
            if left:
                idle[left] += 1
    return dict(sorted(idle.items()))


def global_profile(local, idle, calls=72):
    require(type(calls) is int and calls > 0, "positive call count")
    return dict(sorted((Counter({r: calls*n for r, n in ints(local).items()}) + Counter(ints(idle))).items()))


def validate_global(candidate, local, idle):
    require(ints(candidate) == global_profile(local, idle), "global profile not supported by retained owner map")


def price(profile, engines, bit):
    helper, mercator, base_two, outer = engines
    require(__debug__, "Pricing requires normal Python: retained engines use assertions")
    H = ints(profile)
    deficit = 73*7168-rank_mass(H)
    root = mercator.certify(H, 73, 7168, False)
    b = Q(root["lower"])
    checks = helper.moment_checks(mercator, base_two, H, 73, 7168, b, deficit, False)
    assembly = helper.outer47(bit, b, outer)
    return dict(profile=H, mass=rank_mass(H), deficit=deficit,
                bracket={k: root[k] for k in ("lower", "upper", "strict_rational_signs")},
                exact_moments=checks, outer=assembly,
                gain_over_x4_percent=helper.decimal(100*(Q(assembly["kappa"])/X4_KAPPA-1)))


def pricing_engines():
    helper_path = ROOT / "research/gauge44-frames-x/independent/price_profile.py"
    helper = load_module(helper_path, "roadmap_price_helper")
    folder = ROOT / helper.SOURCE / "engines"
    pins = json.loads((ROOT / "research/gauge44-frames-x/data/UPSTREAM-PINS.json").read_bytes())
    source_hashes = {}
    for name in ("moment", "base_two_moment", "outer"):
        path = folder / (name+".py")
        normalized = path.read_bytes().replace(b"\r\n", b"\n")
        key = path.relative_to(ROOT).as_posix()
        require(digest(normalized) == pins[key], "retained pricing engine pin: " + name)
        source_hashes[key] = digest(normalized)
    bit_raw = helper.BIT_PATH.read_bytes().replace(b"\r\n", b"\n")
    blob = hashlib.sha1(b"blob "+str(len(bit_raw)).encode()+b"\0"+bit_raw).hexdigest()
    require(blob == helper.BIT_BLOB, "unchanged PR589 bit blob pin")
    record = json.loads(bit_raw)
    bit = record["nine"]
    bit_H = ints(bit["profile"])
    bit_D = helper.pr589_deficit(record["word"], bit["bit"]["live"])
    require(rank_mass(bit_H) == bit["bit"]["rank_mass"], "bit mass")
    modules = tuple(helper.load(folder, n) for n in ("moment", "base_two_moment", "outer"))
    c = Q(bit["bit_lower"])
    bit_checks = helper.moment_checks(modules[0], modules[1], bit_H, 64, bit["bit"]["live"], c, bit_D, True)
    return (helper, *modules), c, dict(source_sha256=source_hashes, bit_git_blob=blob,
                                      bit_c=str(c), bit_checks=bit_checks,
                                      price_helper_sha256=digest(helper_path.read_bytes().replace(b"\r\n", b"\n")))


def analysis(profile, certified_lower):
    """Numerical diagnostics, separate from exact sign and outer certificates."""
    with localcontext() as ctx:
        ctx.prec = 60
        H = ints(profile); S = Decimal(rank_mass(H)); M = Decimal(73*7168)
        b = Decimal(certified_lower)
        terms = [(Decimal(r*n), (Decimal(73)/Decimal(r)).ln()) for r, n in H.items()]
        mu = sum(s*x for s, x in terms)/S
        var = sum(s*(x-mu)**2 for s, x in terms)/S
        log_gap = (M/S).ln()
        first = log_gap/mu
        second = 2*log_gap/(mu+(mu*mu+2*var*log_gap).sqrt())
        derivative = sum(s*x*(b*x).exp() for s, x in terms)
        unit_capacity_price = 1/derivative/(1+b)**2
        return {k: str(v) for k, v in dict(mu=mu, variance=var,
                first_order_b=first, second_order_b=second,
                first_error_percent=100*(first/b-1), second_error_percent=100*(second/b-1),
                moment_derivative=derivative, kappa_per_capacity_unit=unit_capacity_price,
                relative_mass_elasticity=M/(b*(1+b)*derivative)).items()}


def cut_collision(word, center):
    """Exact full-state witnesses: drop one center, and two cut states collide.

    No 728x728 elimination: A is a product of invertible scalar primitives.
    The original roadmap explicitly starts from ident(), i.e. arbitrary columns.
    These witnesses do not address a smaller clean/entrance-constrained domain.
    """
    require(center in word["centers"], "declared center")
    rows = [{center: Q(1)} if i == center else {} for i in range(728)]
    for gate in reversed(word["A"]):
        AUDIT.apply(AUDIT.invert(gate), rows)
    inverse_column = {i: row[center] for i, row in enumerate(rows) if row.get(center)}
    image = deepcopy(rows)
    for gate in word["A"]:
        AUDIT.apply(gate, image)
    require(all(row == ({center: Q(1)} if i == center else {}) for i, row in enumerate(image)), "exact inverse cut column")
    return dict(center=center, input_difference={str(i): str(q) for i, q in inverse_column.items()},
                cut_difference={str(center): "1"}, all_other_cut_registers_equal=True,
                domain="all 728 rational entering coordinates; clean/entrance restrictions not assumed")


def build(out):
    out.mkdir(parents=True, exist_ok=True)
    source, plan, owners_receipt = read_source()
    word, recipe = build_word(source)
    path = out / "COMBINED-FIXED2.json.gz"
    path.write_bytes(gzip.compress(encode(word), mtime=0))
    dump(out / "UNLOCK-RECIPE-48.json", recipe)
    (out / "X4.json.gz").write_bytes(gzip.compress(encode(source), mtime=0))
    owner_path = ROOT / "research/gauge44-frames-x/data/OWNERS.json.gz"
    require(digest(owner_path.read_bytes()) == OWNER_SHA, "retained owner map pin")
    owners = json.loads(gzip.decompress(owner_path.read_bytes()))
    old_idle = recount_idle(plan, owners, source)
    new_idle = recount_idle(plan, owners, word)
    require(old_idle == new_idle == {1: 1, 3: 1, 44: 1, 48: 2396}, "fresh physical idle recount")
    validate_global(plan["profile"], OLD_PROFILE, old_idle)
    require(ints(owners_receipt["paid_profile"]) == ints(plan["profile"]), "retained owner receipt binding")
    actual = global_profile(NEW_PROFILE, new_idle)
    source_frames, final_frames = frame_state(word)
    chain_mass = sum(len(f)-len(s) for s, f in zip(source_frames, final_frames))
    center_volume = sum(len(basis(tuple(f))) for f in word["center_frames"])
    require(chain_mass == 5570 and center_volume == 72, "direct telescoping mass")
    require(rank_mass(actual) == 72*(chain_mass+center_volume)+rank_mass(new_idle), "direct final mass equation")
    claimed_idle = {r: n-72*NEW_PROFILE.get(r, 0) for r, n in ROADMAP_PROFILE.items()
                    if n-72*NEW_PROFILE.get(r, 0)}
    dump(out / "PROFILES.json", dict(x4=ints(plan["profile"]), local=NEW_PROFILE,
         retained_owner_idle=new_idle, retained_owner_global=actual,
         roadmap_hypothetical_global=ROADMAP_PROFILE, roadmap_implied_idle=claimed_idle,
         omitted_idle_children=12, omitted_rank_mass=576,
         helper_roles_recounted=len(owners), calls=72, new_center_rank_sum=72,
         report_corrections_beyond_roadmap=["centre_ranks", "cst"]))
    dump(out / "FINAL-CONSTRUCTION.json", dict(
        word="COMBINED-FIXED2.json.gz", word_content_sha256=digest(encode(word)),
        dimensions=dict(v=112, h=9, helpers=504, registers=728, parent_scale=73, live_volume=7168),
        center_frames=word["center_frames"], center_rank_sum=center_volume,
        frame_increment_mass=chain_mass, helper_width_sum=sum(len(final_frames[r])-len(source_frames[r]) for r in range(224,728)),
        local_paid_children=sum(NEW_PROFILE.values()), local_paid_mass=5642,
        complete_invocations=72, idle_children=new_idle, idle_mass=rank_mass(new_idle),
        total_paid_mass=rank_mass(actual), capacity=73*7168, deficit=1984,
        mass_equation="S = 72*(5570 + centerVolume) + 115056",
        deficit_equation="D = 73*7168 - S = 7168 - 72*centerVolume",
        compatibility_used_in_cost_calculation=False,
        assumptions="All72 whole-helper roles and current data/controller capacity; replacing these produces a different construction whose ledger must be supplied."))
    return source, word, plan, actual, path


def run(out):
    require(__debug__, "Use normal Python, not -O, for retained assertion-based engines")
    source, word, plan, actual, path = build(out)
    print("48 edits built; running independent 728-column forward/dual audit", flush=True)
    AUDIT.run(path, out / "LOCAL-AUDIT.json")
    retain_audit_receipt(out / "LOCAL-AUDIT.json")
    # Compatibility is diagnostic only. The final cost does not depend on it.
    try:
        AUDIT.check_parent_interface(word, ROOT)
    except RuntimeError as exc:
        interface = dict(status="REJECTED", reason=str(exc), old_dimensions=[8]*8, new_dimensions=[9]*8)
    else:
        interface = dict(status="COMPATIBLE")
    print("Local audit passed; repricing retained-owner and hypothetical profiles", flush=True)
    engines, bit, provenance = pricing_engines()
    old_price = price(ints(plan["profile"]), engines, bit)
    require(Q(old_price["outer"]["kappa"]) == X4_KAPPA, "X4 reference price")
    actual_price = price(actual, engines, bit)
    hypothetical = price(ROADMAP_PROFILE, engines, bit)
    require(Q(hypothetical["outer"]["kappa"]) == ROADMAP_KAPPA, "ROADMAP hypothetical price")
    stated_b = Q("0.001674954374355989549644")
    bracket_claim = engines[1].moment(ROADMAP_PROFILE, 73, 7168, stated_b)
    require(bracket_claim[0] > 1, "ROADMAP claimed lower endpoint must be rejected")
    receipt = dict(status="PASS_LOCAL_AND_DIRECT_COST_REPLAY",
        source_archive_sha256=ARCHIVE_SHA, source_word_content_sha256=WORD_SHA,
        output_word_content_sha256=digest(encode(word)), source_owner_sha256=OWNER_SHA,
        local_profile=NEW_PROFILE, local_mass=5642, helper_widths_unchanged=True,
        parent_interface=interface, x4_price=old_price, retained_owner_price=actual_price,
        roadmap_hypothetical_price=hypothetical, pricing_provenance=provenance,
        roadmap_claimed_b_check=dict(value=str(stated_b), status="REJECTED_ABOVE_ROOT",
            residual_interval=[str(x-1) for x in bracket_claim]),
        own_construction_model=dict(ambient_frame_dimension=9, parent_scale=73,
            live_volume=7168, complete_local_invocations=72, center_ranks=[9]*8,
            helper_roles=36288, helper_widths=word["report"]["width_inventory"],
            idle_children={1: 1, 3: 1, 44: 1, 48: 2396},
            paid_profile=actual, rank_mass=rank_mass(actual), deficit=73*7168-rank_mass(actual),
            cost_equation="sum_r r*n_r*(73/r)^b = 73*7168",
            interface_policy="Old-parent compatibility is a diagnostic; it is not used to accept/reject the cost model.",
            assumptions="Declared paid-child recurrence and retained outer transfer/bit hypotheses; local exact checks do not prove all-size realization."),
        hypothetical_required_change=dict(rank48_idle_children_to_remove=12,
            rank_mass_to_remove=576, status="CONSTRUCTION_NOT_SUPPLIED",
            reason="Same helper widths and occupied cells leave exactly the same idle remainders; a new construction may change these inputs."),
        scope="Finite exact local scalar/frame audit and direct conditional cost of the final 9-center construction. No full multiplication theorem is asserted.")
    dump(out / "RESULT.json", receipt)
    dump(out / "MOMENT-ANALYSIS.json", dict(
        retained_owner=analysis(actual, actual_price["bracket"]["lower"]),
        hypothetical=analysis(ROADMAP_PROFILE, hypothetical["bracket"]["lower"])))
    old_ends = [e for e in replay_frames(source)["events"] if e["phase"] == "END"]
    new_ends = [e for e in replay_frames(word)["events"] if e["phase"] == "END"]
    removed = sorted({e["register"] for e in old_ends}-{e["register"] for e in new_ends})
    require(len(old_ends) == 490 and len(new_ends) == 434 and len(removed) == 56, "END merge map")
    dump_compressed(out / "END-MERGES.json.gz", dict(before_count=490, after_count=434, merged_pairs=56,
        merged_registers=removed, before=old_ends, after=new_ends,
        scope="Literal END increment map; not a claim of exhaustive optimization or removable rank mass."))
    dump_compressed(out / "PAID-EVENTS.json.gz", dict(events=replay_frames(word)["events"],
        center_descent_ranks=[9]*8, local_profile=NEW_PROFILE,
        scope="Every positive A/B/early-tail/END increment, plus eight center descents; register-local chains telescope."))
    dump(out / "CUT-COLLISIONS.json", dict(status="EXACT_FULL_STATE_COLLISION_CERTIFICATES",
        full_cut_rank=728, reason="A is a product of nonzero scales and distinct-register additions",
        witnesses=[cut_collision(word, c) for c in CENTERS],
        recovery_cost="No zero-cost decoder inferred from linear dependence on a restricted input domain."))
    family = []
    for blocks in range(9):
        local = Counter(OLD_PROFILE)
        local[1] -= 7*blocks; local[4] -= 7*blocks; local[5] += 7*blocks
        local[8] -= blocks; local[9] += blocks
        local = {r: n for r, n in local.items() if n}
        row = price(global_profile(local, {1: 1, 3: 1, 44: 1, 48: 2396}), engines, bit)
        family.append(dict(promoted_blocks=blocks, gate_edits=6*blocks,
            merged_pairs=7*blocks, center_rank_sum=64+blocks,
            local_children=sum(local.values()), rank_mass=row["mass"], deficit=row["deficit"],
            complex_b=row["bracket"]["lower"], kappa=row["outer"]["kappa_decimal"],
            gain_over_x4_percent=row["gain_over_x4_percent"]))
    dump(out / "CARRY-COST-TABLE.json", dict(
        assumptions="Same helper owner cells, m=73, W=7168; all subsets with the same block count have this profile.",
        variants=family, scope="Exact price of each declared profile; no claim of optimality over other constructions."))
    print(receipt["status"], "retained-owner kappa", actual_price["outer"]["kappa_decimal"],
          "hypothetical kappa", hypothetical["outer"]["kappa_decimal"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "build/roadmap48")
    parser.add_argument("--build-only", action="store_true")
    args = parser.parse_args()
    (build if args.build_only else run)(args.out.resolve())
