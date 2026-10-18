"""Fixed selected labels and explicit owner-to-common numerical specifications."""
from dataclasses import dataclass, replace
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json

from routes import compile_route
from sources import ROOT, Template, compile_specification, identity, independent_columns, product
from words import need


def split_basis(base, rank, q):
    size = len(base)
    complement = [[F(i == j)-base[i][j] for j in range(size)] for i in range(size)]
    image, kernel = independent_columns(base, q), independent_columns(complement, q)
    need((len(image), len(kernel)) == (rank, size-rank), "source projector rank")
    basis = [[base[i][j] for j in image]+[complement[i][j] for j in kernel] for i in range(size)]
    projected = [[basis[i][j] if j < rank else F(0) for j in range(size)] for i in range(size)]
    need(product(base, basis) == projected and len(independent_columns(basis, q)) == size,
         "fixed source split basis")
    return tuple(map(tuple, basis))


def common_template(template):
    basis = split_basis(template.base, template.rank, template.q)
    need(tuple(map(tuple, product(template.chart, basis))) == template.preparation,
         "original owner preparation provenance")
    return replace(template, chart=tuple(map(tuple, identity(len(template.base)))), preparation=basis,
                   record=template.record+("common-after-owner-route",))


def owner_common(template, owner_low, request, vocabulary):
    route = compile_route(owner_low, template.chart, vocabulary)
    owner_code = vocabulary.encode(request, False, route.low)
    common_code = vocabulary.encode(request, True, route.target_low)
    owner = compile_specification(owner_code, template, route.low)
    common = compile_specification(common_code, common_template(template), route.target_low)
    need(owner.good == common.good, "same physical low projector branch")
    return owner, common, route


@dataclass(frozen=True)
class Episode:
    source: int
    targets: tuple
    private: int
    records: tuple
    sha256: str
    source_family: int
    target_families: tuple
    chart: tuple
    template: object
    request: int = 1


def selected_episode(q=3):
    path = ROOT / "research/pr589-five-helper-hosting/verify.py"
    spec = importlib.util.spec_from_file_location("selected_source_packet_labels", path)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    word, host = old.read(old.WORD), old.read(old.HOST)
    call = host["calls"][0]
    need(call["orientation"] == "forward", "selected episode orientation")
    records = host["local_programs"]["forward"][21881:21938]
    digest = sha256(json.dumps(records, separators=(",", ":")).encode()).hexdigest()
    need(digest == "e622fdcb880ed9e39962929f64272937cc4ccdd6bafd7def1dc1d7a68512b35e",
         "selected literal COPY511 episode")
    need(records[0] == [2,473,661,511,0,7,0] and records[-1] == [3,473,661,511,0,0,0],
         "exact transported COPY and ERASE")
    targets = tuple(record[1] for record in records[1:-1])
    need(len(targets) == len(set(targets)) == 55 and
         all(record == [1, target, 661, 1, 0, 0] and target not in (473,661)
             for target, record in zip(targets, records[1:-1])), "immutable COPY source and private value")
    family, route = call["owners"][473]
    need(family == 527 and route == ["hosted",2,16,8], "selected COPY source owner")
    idle = next(event for event in host["schedule"] if event["kind"] == "idle" and event["idx"] == 2)
    support = old.pending_axes(idle)[16:24]
    need(support == list(range(17,25)), "selected source support")
    permutation = list(range(64))
    for i, j in enumerate(support):
        permutation[i], permutation[j] = j, i
    chart = tuple(tuple(F(permutation[j] == i) for j in range(64)) for i in range(64))
    target_families = tuple(call["owners"][target][0] for target in targets)
    need(target_families == targets and family not in target_families and
         all(call["owners"][target][1] == ["data",0,target % 111] for target in targets),
         "disjoint stage-zero target families")
    local, rank = old.projection([word["lines"][i] for i in word["frames"][511]])
    need(rank == 7, "selected COPY511 rank")
    key = sha256(json.dumps(["local", rank, [[str(x) for x in row] for row in local]],
                            sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    need(key == "f256295f6139080a4b55eeb08cd459385c08060fbee5b1cf318379d6ee9b5cbf",
         "selected COPY511 projector label")
    base = [[F(0) for _ in range(64)] for _ in range(64)]
    for i in range(8):
        base[i][:8] = local[i]
    basis = split_basis(base, rank, q)
    record = ("COPY",0,21881,473,28416,511,0,key,7,"common",tuple(support),-1)
    template = Template(q, rank, record, tuple(map(tuple, base)),
                        tuple(map(tuple, identity(64))), basis)
    return Episode(473, targets, 661, tuple(map(tuple, records)), digest, family,
                   target_families, chart, template)
