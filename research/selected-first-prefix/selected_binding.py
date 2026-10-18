"""Compile call zero from the selected archive; no payload-dependent decoding."""
import ast
from hashlib import sha256
import gzip
import json
from math import prod
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PHASE_SOURCE = "research/e8-signed-prefix/code/data_phases.py"
PHASE_SHA = "04154b12eff7d762d12535663cfef5dcfe7a3dfa68801bf2f9b22c16a910a6a8"
MEMBERS = (
    ("hosted/GLOBAL-TEMPLATE.json.gz", "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760"),
    ("base/providers/gauge44/LOCAL-PROGRAMS.json.gz", "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"),
    ("base/providers/gauge44/CANONICAL-WORD.json.gz", "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"),
    ("base/work/complex-nine-native/DATA-PHASES.json", "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"),
)
GAMMA = (1 << 1296)*prod((1 << (2*i))-1 for i in range(1, 37))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def inputs():
    need(sha256((ROOT/ARCHIVE).read_bytes()).hexdigest() == ARCHIVE_SHA, "selected archive")
    result = []
    with tarfile.open(ROOT/ARCHIVE) as archive:
        for relative, digest in MEMBERS:
            name = "candidate/strict/global/"+relative
            members = [entry for entry in archive.getmembers() if entry.name == name]
            need(len(members) == 1 and members[0].isfile(), "unique regular selected member")
            raw = archive.extractfile(members[0]).read()
            need(sha256(raw).hexdigest() == digest, "selected member bytes")
            result.append(json.loads(gzip.decompress(raw) if relative.endswith(".gz") else raw))
    return result


def mv(rows, vector):
    return sum(((row & vector).bit_count() & 1) << i for i, row in enumerate(rows))


def transpose(rows, width):
    return tuple(sum(((row >> j) & 1) << i for i, row in enumerate(rows)) for j in range(width))


def phase_functions():
    raw = (ROOT/PHASE_SOURCE).read_bytes()
    need(sha256(raw).hexdigest() == PHASE_SHA, "retained data-phase source")
    names = {"normal", "shift_adapter", "basis", "rho", "stage_frame", "desired"}
    nodes = [node for node in ast.parse(raw).body if isinstance(node, ast.FunctionDef) and node.name in names]
    need(len(nodes) == len(names), "exact pure phase definition inventory")
    namespace = dict(H=9, M=73, K=4, L=9, mv=mv, transpose=transpose,
                     parity=lambda value: value.bit_count() & 1)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), PHASE_SOURCE, "exec", optimize=0), namespace)
    return namespace


def validate(template, programs, word, phases, functions):
    call = template["calls"][0]
    provider = template["local_providers"]["gauge44"]
    need(tuple(call[k] for k in ("stage", "replica", "pair", "time", "orientation", "provider_id"))
         == (0, 0, 0, 0, "forward", "gauge44"), "actual first selected call")
    need(call["window"] == dict(local_axes=list(range(9)), prefix_axes=[]), "first-call window")
    need(template["execution_schedule"][0] == dict(
        entry_exit_phase_adapters="DATA-PHASES.recipes[port].stage_alignment[stage]",
        kind="local_cover_sweep", provider_id="gauge44", replica=0,
        replicas=[0], source_event=0, stage=0, time=0), "actual first scheduled cover sweep")
    need(template["cover"] == "all matrices d in O(73,2), in lexicographic row order",
         "actual cover enumeration")
    need(template["route_semantics"]["data"] ==
         "physical cover class d*rho(stage,port); rho is the exact orthogonal involution from data_phases.py",
         "actual data route convention")
    need((template["m"], template["live"], template["physical"]) == (73, 14336, 14826), "selected dimensions")
    owners = call["owners"]
    need(len(owners) == 704 and len({owner[0] for owner in owners}) == 704, "distinct complete call owners")
    need(all(type(owner[0]) is int and 0 <= owner[0] < 14336 for owner in owners), "live owner range")
    need(owners[119] == [119, [1, 0, 7]] and owners[169] == [169, [1, 0, 57]], "selected target/source owners")
    need((provider["v"], provider["h"], provider["R"]) == (112, 9, 480), "selected provider")
    need(provider["local_programs"] == programs, "embedded literal programs")
    need(provider["local_programs_sha256"] == MEMBERS[1][1] and
         provider["canonical_word_sha256"] == MEMBERS[2][1] and
         template["exact_data_phase_recipe_sha256"] == MEMBERS[3][1], "selected member pins")
    need(provider["ports"] == word["ports"], "provider port vocabulary")
    digest = sha256(canonical(programs["forward"])).hexdigest()
    need(digest == call["local_program_sha256"] == provider["local_program_checks"]["forward"]["sha256"]
         == "071ecdacc0bb3ac16046aad4119ed551a945cb0ed6c57002a548a3e2232503d8", "actual forward stream")
    need(programs["forward"][:3] == [
        ["phase", "zero_frame_precondition"],
        ["scalar", ["scale", ["L", 119], -1, 2], 0],
        ["scalar", ["add", ["L", 119], ["L", 169], 1, 2], 0],
    ], "literal first two scalar events")
    need(word["start"][119] == word["start"][169] == 0 and word["frames"][0] == [], "native frame-zero operands")
    identity = tuple(1 << i for i in range(73))
    for port, q in ((7, 21), (57, 56)):
        record = phases["recipes"][port]
        need(record["port"] == port and record["q"] == word["ports"][port] == q, "actual data port")
        need(record["stage_alignment"][0] == dict(entry_X=0, entry_Y=0, exit_X=0, exit_Y=0), "zero entrance translations")
        need(functions["rho"](q, 0) == identity, "actual data chart identity")
        entrance = functions["desired"](q, -1, "Y")
        native = functions["stage_frame"](q, 0, "0")
        need(entrance == native == [] and functions["shift_adapter"](entrance, native) == 0,
             "exact zero Y entrance including global phase")
    need((1 << 2627) < GAMMA < (1 << 2628), "selected cover cardinality")
    return dict(families=14336, target=119, source=169, distinct_owners=704,
                raw_rows=[1, 2], ports=[7, 57], port_labels=[21, 56], frame=0,
                data_chart="I73", entry_Y=[0, 0], next_raw_row=3,
                forward_sha256=digest, cover_cardinality_bits=GAMMA.bit_length())


def compile_selected():
    return validate(*inputs(), phase_functions())
