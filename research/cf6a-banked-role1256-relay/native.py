#!/usr/bin/env python3
"""Qualify the complete role-1256 relay's ordered physical native maps."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import resource
import sys
from time import process_time


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
SUPPORT = HERE / "native_support"
DONOR = "28b2af322a1fab01b3734365988930920f9dda48"
HEAD = "7d84799a447867d36137d12ef7ca5646154d763c"
SOURCE = "ae62d5d8bef6f7146454b4b3643e487a58380c606a16c5baef7bf0dcf9df1472"
SOURCE_PACKED = "50c1facfc5626c060560e2f354b71bd92d0bb1c1e853b2aad72abcbaaa5328a5"
CERTS = "39ef28b708cd8bf1166b111d656809407b370dd11cd81a8e43820779f995aca3"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
CALLER_PACKED = "d889996a337f648087208ab51c98eaf052705d4fca88b5d01b6e9257a829897a"
PARENT = "72705b094d83d2ba24006661bbb031786a691b776bedb94515b1321e1535105f"
PARENT_PACKED = "c86288cddb4b80af3c8128c9a0d2f7a1e82bae64c5152a0d96a19d166afaab1d"
CHILD = "8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf"
CHILD_PACKED = "0177c25371181e3b1f2c13325eb8434fbf6384a9ab99a612849efd5d0f6ab2cc"
PR7682 = "1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150"
PR7697 = "d5dab11bb773bf5beb8ae2998be1282b243e2d1606c5257896a037c9b52c5c3b"
RELEASE = "progress.kappa-successor-7697-20261118t1202z.00000024"
OLD_FIRST, OLD_SECOND, DIRECT = (476, 878), (878, 127), (476, 127)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(raw):
    return sha256(raw).hexdigest()


def load(path, *, packed=None, decoded=None, canonical=None):
    raw = path.read_bytes()
    require(packed is None or digest(raw) == packed, f"exact bytes for {path.name}")
    source = gzip.decompress(raw) if path.suffix == ".gz" else raw
    require(decoded is None or digest(source) == decoded, f"exact decoded bytes for {path.name}")
    value = json.loads(source)
    require(canonical is None or digest(encode(value)) == canonical, f"canonical custody for {path.name}")
    return value


def put(path, raw):
    with path.open("xb") as handle:
        handle.write(raw)
    return digest(raw)


def ordered(frames, pair):
    return tuple(tuple(frames[i]) for i in pair)


def old_recipe_inputs():
    old = load(SUPPORT / "PR7682-GRAPH.json.gz", canonical=PR7682,
               packed="8e28c1d403145ca5d72521f4acd7e068603598334c87f18f2fefb738844a1970")
    phase = load(SUPPORT / "PR7682-PHASE-RESULT.json",
                 packed="50b05bdc2805d709761ce5c4b42e7ec352141366f5cc6031df9f8779e8872735")
    require(phase["status"] == "PASS_PAIRED_BANK24_EXACT_NATIVE_MAPS"
            and phase["graph_pins"]["candidate"] == PR7682 and phase["source_head"] == DONOR
            and phase["caller_sha256"] == CALLER, "retained #7682 physical body custody")
    records = load(SUPPORT / "PR7682-BANK-RECIPES.json.gz", packed=phase["artifact_sha256"]["BANK-RECIPES.json.gz"])
    archive = {}
    for item in records:
        require(item["compared_signed_pauli_and_absolute_phase"], "prior checked body")
        archive.setdefault(ordered(old["frames"], item["pair"]), item)
    require(len(records) == phase["forward_union"] + phase["diagnostic_only_pivot_orientations"],
            "complete prior recipe archive")
    main = load(SUPPORT / "PR7682-MAIN-BOUNDARIES.json", packed=phase["artifact_sha256"]["MAIN-BOUNDARIES.json"])
    return old, archive, main


def read_sources():
    p = load(DATA / "PARENT-GRAPH.json.gz", packed=PARENT_PACKED, canonical=PARENT)
    c = load(DATA / "CANDIDATE-GRAPH.json.gz", packed=CHILD_PACKED, canonical=CHILD)
    word = load(DATA / "WORD.json.gz", packed=SOURCE_PACKED, canonical=SOURCE)
    certs = load(DATA / "CERTS.json", packed=CERTS)
    caller = load(DATA / "CALLER.json.gz", decoded=CALLER, packed=CALLER_PACKED)
    require(certs["candidate_canonical_sha256"] == SOURCE and len(certs["clear_event_index"]) == 235,
            "all original CLEAR witnesses are bound to the literal word")
    require(all(g["metadata"]["source_word_sha256"] == SOURCE
                and g["metadata"]["source_pr_head"] == HEAD
                and g["metadata"]["source_clear_certificates_sha256"] == CERTS
                and g["metadata"]["caller_sha256"] == CALLER for g in (p,c))
            and c["metadata"]["source_banked_graph_sha256"] == PARENT, "physical source and candidate metadata")
    require(all(p[k] == c[k] == word[k] for k in ("frames", "initial", "final"))
            and p["first_output"] == c["first_output"] == len(word["program"]) == 154768,
            "source and candidate have identical ordered port charts")
    return p, c, word, certs, caller


def move_inventory(graph):
    result = {k: (a, b) for k, a, b in graph["moves"]}
    require(len(result) == len(graph["moves"]), "unique physical paid MOVE keys")
    return result


def raw_relay(p, c, word, certs):
    before, after = move_inventory(p), move_inventory(c)
    own, remove, keep = 1256, 95828, 104442
    raw_moves = {clock: (e[2], e[3]) for clock, e in enumerate(word["program"]) if e[0] == "MOVE"}
    require(raw_moves == before and len(before) == 6144 and len(after) == 6143,
            "every original paid key and ordered pair agrees with the served WORD")
    require(word["program"][remove] == ["MOVE", own, *OLD_FIRST, False]
            and word["program"][keep] == ["MOVE", own, *OLD_SECOND, False],
            "actual old chronological same-owner relay")
    require(after == {k: DIRECT if k == keep else pair for k,pair in before.items() if k != remove}
            and DIRECT not in before.values(), "only the merged direct paid edge is new on this word")
    for clock in range(remove + 1, keep):
        event = word["program"][clock]
        require(event[1] != own and (event[0] not in {"ADD", "COPY"} or event[2] != own),
                f"no live role-1256 observation between relay legs at {clock}")
    require(not any(remove < int(clock) < keep and str(own) in witness
                    for clock, witness in certs["clear_event_index"].items()),
            "no intermediate role-1256 observation in the original CLEAR certificates")
    forms_p, forms_c = dict(p["forms"]), dict(c["forms"])
    require(forms_p[keep] == [[remove, "1"]]
            and [k for k, row in forms_p.items() if any(d == remove for d, _ in row)] == [keep],
            "identity sole reader at the middle chart")
    require(forms_c == {k: forms_p[remove] if k == keep else row
                        for k, row in forms_p.items() if k != remove},
            "the direct MOVE uses the old first MOVE's complete source form")
    return before, after, {"owner": own, "removed_key": remove, "kept_key": keep,
                           "old_pairs": [OLD_FIRST, OLD_SECOND], "candidate_pair": DIRECT,
                           "old_retained_productive_charts": [word["initial"][own], word["final"][own]],
                           "intermediate_scalar_or_clear_observers": 0}


def chart_spans(frames):
    spans = []
    for axes in frames:
        members = {0}
        for v in axes:
            require(type(v) is int and 0 < v < 512 and v not in members, "independent ordered axis")
            members |= {w ^ v for w in members}
        spans.append(members)
    return spans


def binding_inventory(word, caller, archived_main, old_frames, compiler, checker, spans):
    layout = load(SUPPORT / "PR7697-CALLER-LAYOUT.json",
                  packed="622c6f458eba2dab0fdfd6050303cbc16ad684ab8b834c7df568264e4cf01db6")
    phase = load(SUPPORT / "PR7697-CALLER-RESULT.json",
                 packed="cbef124e8b495b4bec9a1343500766af33b245121a486fff4a619c8eb284f2ad")
    require(all(word[k] == layout[k] for k in ("public", "live", "ports", "hosted"))
            and phase["status"] == "PASS_CHART595_ACTUAL16_CALLER"
            and phase["caller_sha256"] == CALLER and PR7697 in phase["graphs"].values(),
            "identical literal phase-contact context and proof binding")
    h = word["hosted"]
    hosted = dict(zip(h["Dports"], zip(h["X2"], h["Y2"], strict=True), strict=True))
    frames = word["frames"]
    main_roles, main_rows = set(), []
    for j, (x, q, prior) in enumerate(zip(word["live"], word["ports"], archived_main, strict=True)):
        y = x + 112
        a,b,c,d = (word["initial"][x], word["initial"][y], word["final"][x], word["final"][y])
        require(frames[a] == [q] and not frames[b]
                and spans[d] == {s for s in range(512) if (s & q).bit_count() % 2 == 0}, "ordered main port axes")
        before,_ = compiler.lower_child(compiler.cgate(9, q, 1).adjoint()
                                         .then(compiler.canonical_frame(9, tuple(frames[a]))))
        after,_ = compiler.lower_child(compiler.canonical_frame(9, tuple(frames[d])).adjoint()
                                        .then(compiler.cgate(9, q, -1).then(compiler.fourier(9))))
        require(before["rank"] == after["rank"] == 0, "rank-zero physical main adapters")
        checker.equal(checker.recipe(before), (("C", q, -1),) + checker.frame(frames[a], 9), f"main ingress {j}")
        checker.equal(checker.recipe(after), checker.adjoint(checker.frame(frames[d], 9))
                      + (("C", q, -1),) + checker.fourier(9), f"main return {j}")
        checker.equal(checker.frame(frames[c], 9), checker.fourier(9), f"main full Fourier output {j}")
        second = hosted.get(j)
        require(prior["j"] == j and prior["q"] == q and prior["main_roles"] == [x,y]
                and prior["hosted_roles"] == (list(second) if second else None)
                and ordered(frames,(a,b,c,d)) == ordered(old_frames, prior["charts"]),
                "the previously checked contact uses the exact same ordered charts and main roles")
        roles = (x,y)
        if second:
            u,v = second
            require((word["initial"][u], word["initial"][v], word["final"][u], word["final"][v]) == (a,b,c,d),
                    "the second plane has the same exact ordered physical frames")
            roles += second
        require(not main_roles.intersection(roles) and len(set(roles)) == len(roles), "distinct main roles")
        main_roles.update(roles)
        main_rows.append((j, roles))
    require(len(main_rows) == 104 and len(hosted) == 96 and len(main_roles) == 400, "main boundary denominator")
    helpers = set(range(word["public"])) - main_roles
    require(len(helpers) == 1101 and 1256 in helpers, "actual native helper inventory")
    require(caller["stages"] == 16 and caller["ambient_rank"] == 137 and caller["roles"] == 68
            and caller["types"]["A"]["ports"] == h["Dports"], "the same sixteen signed caller stages")
    owner_sets = {kind: set(range(s["offset"], s["offset"] + s["roles"])) for kind,s in caller["types"].items()}
    all_helpers = set()
    roots = set()
    stages, contacts = [], 0
    for clock, event in enumerate(caller["events"]):
        if event[0] != "J":
            continue
        _, stage, binds_a, binds_b = event
        require(stage == len(stages) + 1 and len(set(binds_a)) == len(binds_a) == 4 and set(binds_a) <= owner_sets["A"]
                and len(binds_b) == 4 and len(set(binds_b[:2])) == 2 and set(binds_b[:2]) <= owner_sets["B"]
                and tuple(map(Fraction, binds_b[2:])) == (-1, Fraction(1,2)), "literal injective main stage binding")
        owners = {(j, owner) for j, roles in main_rows for _, owner in
                  zip(roles, binds_a if j in hosted else binds_b[:2], strict=True)}
        require(len(owners) == 400, "exact stage-local main aliases")
        roots.update(owners)
        all_helpers.update((stage,role) for role in helpers)
        contacts += 4 * (len(main_rows) + len(hosted))
        stages.append([clock, stage])
    require(len(stages) == 16 and len(roots) == 3280 and len(all_helpers) == 17616
            and contacts == phase["owners"]["main_contacts"] == 12800,
            "literal complete main contact and helper owner denominators")
    return helpers, {"main_boundary_pairs": len(main_rows), "native_main_roles": len(main_roles),
                     "hosted_correspondences": len(hosted), "native_helper_roles": len(helpers),
                     "literal_stage_sites": stages, "root_owners_bound_in_native_calls": len(roots),
                     "fresh_helper_owner_tags": len(all_helpers), "exact_retained_phase_contacts": contacts,
                     "phase_context_reference": PR7697, "phase_contact_digest": phase["owners"]["main_contact_digest"]}


def columns(checker, left, right, label):
    digests = {}
    for direction, a, b in (("forward",left,right), ("adjoint",checker.adjoint(left),checker.adjoint(right))):
        result = sha256()
        for k in range(512):
            l, r = checker.state(a,k), checker.state(b,k)
            require(l == r, f"{label} {direction} column {k}")
            result.update(encode([k, sorted(r[0].items()),r[1]]) + b"\n")
        digests[direction] = result.hexdigest()
    return digests


def verify(out):
    parent, child, word, certs, caller = read_sources()
    old, archive, archived_main = old_recipe_inputs()
    for path, expected in (("clifford_exact.py", "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"),
                           ("native_verify.py", "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38")):
        require(digest((SUPPORT / path).read_bytes()) == expected, f"unchanged attributed producer or verifier {path}")
    sys.path.insert(0,str(SUPPORT))
    import clifford_exact as compiler
    import native_verify as checker

    require(Path(compiler.__file__).parent == Path(checker.__file__).parent == SUPPORT, "pinned exact engine imports")
    old_moves, moves, relay = raw_relay(parent,child,word,certs)
    frames = word["frames"]
    spans = chart_spans(frames)
    helpers,binding = binding_inventory(word,caller,archived_main,old["frames"],compiler,checker,spans)
    targets = defaultdict(list)
    for r in sorted(helpers):
        a,b = (word["initial"][r],word["final"][r])
        require(spans[a] < spans[b], f"strictly ascending target {r}")
        targets[a,b].append(r)
    occurrences = {"parent": defaultdict(list), "candidate": defaultdict(list)}
    for kind, slots in (("parent",old_moves),("candidate",moves)):
        for key,pair in slots.items():
            occurrences[kind][pair].append(key)
    source = set(old_moves.values()) | set(targets)
    used = set(moves.values()) | set(targets)
    pair_union = source | used

    @cache
    def rank(pair):
        a,b = pair
        require(spans[a] < spans[b] or spans[b] < spans[a], f"strict native nesting for {pair}")
        return abs(len(frames[b])-len(frames[a]))

    @cache
    def frame(i):
        return checker.frame(frames[i], 9)

    @cache
    def make(i):
        return compiler.canonical_frame(9, tuple(frames[i]))

    p_bill, c_bill = Counter(map(rank,old_moves.values())), Counter(map(rank,moves.values()))
    delta = {r: c_bill[r]-p_bill[r] for r in p_bill.keys()|c_bill.keys() if c_bill[r]!=p_bill[r]}
    require(delta == {3:-2,6:1} and [rank(pair) for pair in (OLD_FIRST,OLD_SECOND,DIRECT)] == [3,3,6],
            "exact positive recursive invoice consequence")
    records, fresh, relevant = [], [], {}
    for pair in sorted(pair_union):
        a,b = pair
        prior = archive.get(ordered(frames,pair))
        force = pair == DIRECT or prior is None
        recipe = compiler.lower_child(make(a).adjoint().then(make(b)))[0] if force else prior["recipe"]
        require(recipe["rank"] == rank(pair), f"compiled positive rank {pair}")
        actual = checker.recipe(recipe)
        ideal = checker.adjoint(frame(a)) + frame(b)
        checker.equal(actual, ideal, f"signed Pauli and global phase {pair}")
        column_hashes = columns(checker,actual,ideal,f"fresh {pair}") if force else None
        record = {"pair": pair, "ordered_bases": ordered(frames,pair), "recipe": recipe,
                  "parent_moves": occurrences["parent"].get(pair, []), "candidate_moves": occurrences["candidate"].get(pair, []),
                  "productive_roles": targets.get(pair, []), "fresh_column_sha256": column_hashes,
                  "previous_ordered_pair": None if force else prior["pair"]}
        records.append(record)
        if force:
            fresh.append(pair)
        if pair in (OLD_FIRST,OLD_SECOND,DIRECT):
            relevant[pair] = actual, recipe
    direct, recipe = relevant[DIRECT]
    chronology = relevant[OLD_FIRST][0] + relevant[OLD_SECOND][0]
    composite = columns(checker,direct,chronology,"rank-six contraction equals the original chronological product")
    wrong = deepcopy(recipe)
    wrong["left"]["phase"] = (wrong["left"]["phase"]+1) % 4
    wrong_circuit = checker.recipe(wrong)
    require(checker.tableau(wrong_circuit) == checker.tableau(direct), "phase fault leaves signed Pauli action fixed")
    try:
        checker.equal(wrong_circuit,direct,"absolute phase fault in surviving role-1256 MOVE")
    except ValueError as error:
        require(str(error).endswith("exact global phase"), "strict exact phase control rejection")
    else:
        raise ValueError("incorrect absolute relay phase accepted")
    native_raw = encode({"candidate_graph_sha256": CHILD, "parent_graph_sha256": PARENT, "pairs": records})
    packed = gzip.compress(native_raw, mtime=0)
    packed_sha = put(out / "RECIPES.json.gz", packed)
    relay.update({"ranks": [3,3,6], "chronological_product_exact_columns": composite,
                  "wrong_absolute_phase_control_rejected": True})
    return {"status":"PASS_ROLE1256_COMPLETE_ORDERED_NATIVE_PHASE", "source_head":HEAD, "raw_word_sha256":SOURCE,
            "parent_graph_sha256":PARENT,"candidate_graph_sha256":CHILD,"caller_sha256":CALLER,
            "parent_map_pairs":len(source),"candidate_map_pairs":len(used),"checked_source_candidate_union":len(pair_union),
            "fresh_exact_512_pairs":fresh,"reused_bodies_checked_again":len(pair_union)-len(fresh),
            "parent_native_paid_histogram":p_bill,"candidate_native_paid_histogram":c_bill,
            "paid_delta_native":delta,"native_productive_histogram":Counter({r:sum(len(v) for pair,v in targets.items()
                                                                               if rank(pair)==r) for r in range(1,10)}),
            "relay":relay,"physical_binding":binding,"recipes_decoded_sha256":digest(native_raw),
            "recipes_gzip_sha256":packed_sha}


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    require(sys.flags.optimize == 0, "exact producer assertions enabled")
    args.out.mkdir(parents=True,exist_ok=True)
    start = {"started_at":stamp(),"release":RELEASE,"candidate_graph_sha256":CHILD,
             "runner_sha256":digest(Path(__file__).read_bytes())}
    start_sha = put(args.out / "START.json", encode(start)+b"\n")
    t0 = process_time()
    try:
        result = verify(args.out)
    except Exception as error:
        put(args.out / "FAILURE.json", encode({**start, "error":str(error), "completed_at":stamp(),
                                                "cpu_seconds":process_time()-t0})+b"\n")
        raise
    result.update({"started_at": start["started_at"],"completed_at":stamp(),"start_sha256":start_sha,
                   "cpu_seconds":process_time()-t0,"peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    put(args.out / "NATIVE.json", encode(result)+b"\n")
    print(result["status"], CHILD, result["checked_source_candidate_union"], len(result["fresh_exact_512_pairs"]), flush=True)


if __name__ == "__main__":
    main()
