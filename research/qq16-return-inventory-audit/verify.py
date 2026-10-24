#!/usr/bin/env python3
"""Independent finite return audit; no complete caller or kappa claim.

Mihir Srivastava, substantial OpenAI Codex assistance. Apache-2.0.
Executed predecessor bodies retain their original source attribution.
"""
import argparse
import ast
import hashlib
import io
import itertools
import json
from pathlib import Path
import sys
import tarfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/qq16-caller-install/"
ADAPTER = "research/qq16-protected-return-caller/adapter.py"
GAUSSIAN = "research/physical-gaussian-leaf/inputs/pr3087.tar"
PROTOCOL = "research/qq16-complete-cost/inputs/PR4172.tar"
PARKING = "research/physical-complex-controller/parking.py"
RWM = ("reads", "writes", "moves")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def authenticate():
    sources = {}
    for entry in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
        if entry["usage"] != "input":
            continue
        raw = (ROOT / entry["path"]).read_bytes()
        need(sha(raw) == entry["sha256"], "source SHA256: " + entry["path"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == entry["git_blob"], "source Git blob: " + entry["path"])
        sources[entry["path"]] = raw
    need(len(sources) == 7, "seven explicit source inputs")
    return sources


def member(raw, name):
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        matches = [m for m in archive.getmembers() if m.name == name]
        need(len(matches) == 1 and matches[0].isfile(), "unique regular member: " + name)
        need(matches[0].size < 8 * 1024 * 1024, "bounded source member")
        return archive.extractfile(matches[0]).read()


def function(raw, name, environment):
    nodes = [n for n in ast.walk(ast.parse(raw))
             if isinstance(n, ast.FunctionDef) and n.name == name]
    need(len(nodes) == 1, "unique retained function: " + name)
    namespace = dict(environment)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "retained/" + name, "exec"), namespace)
    return namespace[name]


def module(name, raw, *, registered=False):
    value = types.ModuleType(name)
    if registered:
        need(name not in sys.modules, "cold source namespace: " + name)
        sys.modules[name] = value
    exec(compile(raw, "retained/" + name + ".py", "exec"), value.__dict__)
    return value


def load(sources):
    raw = member(sources[GAUSSIAN], "inputs/pr3055.tar")
    compact = member(raw, "inputs/pr2899.tar")
    ordinary = member(compact, "inputs/pr2809.tar")
    stem = "inputs/pr2753/predecessor/vendor/"
    words_raw, records_raw = (member(ordinary, stem + n + ".py") for n in ("words", "records"))
    words = module("words", words_raw, registered=True)
    records = module("records", records_raw, registered=True)
    need(records.Tape.__eq__ is object.__eq__, "source Tape equality is identity")
    session = member(compact, "session.py")
    environment = dict(need=need, LEFT=words.LEFT, BLANK=words.BLANK)
    erase = function(session, "erase_marker", environment)
    transfer = function(sources[PARKING], "transfer", {
        **environment, "BODY": (0, 1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13)})
    nested = member(sources[PROTOCOL], "research/qq16-native-history/inputs/PR4167.tar")
    adoption = member(nested, "research/qq16-protocol-comparison/adapter.py")
    api = types.SimpleNamespace(Tape=records.Tape, words=words, transfer=transfer, erase=erase,
        adapter=module("inventory_adapter", sources[ADAPTER]),
        owned=module("installer", sources[PREFIX + "installer.py"]).owned_tapes,
        Storage=module("lifecycle", sources[PREFIX + "lifecycle.py"]).CallerStorage,
        adoption_raw=adoption, environment={**environment, "erase_marker": erase})
    api.adopt = function(adoption, "adopt_return", api.environment)
    hashes = {"words.py": sha(words_raw), "records.py": sha(records_raw),
              "session.py": sha(session), "PR4167.tar": sha(nested), "adoption.py": sha(adoption)}
    need(hashes["adoption.py"] == "77c01376ac43339a7c99ab377c7947cb89b44e96ff4a826becb545cccd045fef",
         "same PR4167 transaction as PR4790")
    return api, hashes


def tape(api, bits):
    result = api.Tape()
    # Test-only loading at canonical origin, excluded from return meters.
    result.cells = bytearray([api.words.LEFT, *bits])
    return result


def payload(t, api):
    body = bytes(t.cells[1:])
    end = body.find(bytes([api.words.BLANK]))
    if end >= 0:
        need(all(x == api.words.BLANK for x in body[end:]), "dense body and blank high-water suffix")
        body = body[:end]
    return body


class Caller:
    def packet(self, target):
        return self.bank.packets[target] if target < self.binding.slots else self.private[target-self.binding.slots]


def caller(api, packets, native):
    value = Caller()
    fresh = lambda: tape(api, (1, 0, 1))
    value.binding = types.SimpleNamespace(slots=1)
    value.bank = types.SimpleNamespace(packets=(packets[0],), output=fresh(),
                                      pool=types.SimpleNamespace(tapes=(fresh(),)))
    value.private = (packets[1],)
    value.roles = {"current": fresh(), "header": fresh()}
    value.capsule, value.output = {"current": fresh()}, fresh()
    value.native_child = native
    value.parked = (*value.roles.values(), *value.bank.packets, *value.private)
    value.parking = types.SimpleNamespace(roles=value.parked, stack=fresh(), reverse=fresh())
    return value


def physical(c):
    """Independent explicit fixture inventory, not predecessor graph traversal."""
    return (*c.roles.values(), *c.bank.packets, *c.private, *c.capsule.values(),
            c.output, c.bank.output, *c.bank.pool.tapes, c.parking.stack, c.parking.reverse)


def fixture(api, permutation, lengths, *, mode="adopt", adapter=None, adopt=None):
    moving = [tape(api, ((i+j) % 2 for j in range(lengths[i]))) for i in range(5)]
    positions = [moving[i] for i in permutation]
    native = types.SimpleNamespace(output=positions[4], fixed=(tape(api, (0, 1)),), closed=True)
    parent, service = caller(api, positions[:2], native), caller(api, positions[2:4], native)
    auxiliary = (tape(api, (1,)), tape(api, (0,)))
    installation = types.SimpleNamespace(service=service, native_child=native)
    # Vary saved traversal order; the contract requires membership, not one enumeration.
    s, n = physical(service), (native.output, *native.fixed)
    shift = sum((j+1)*x for j, x in enumerate(permutation)) % len(s)
    s = s[shift:] + s[:shift]
    n = n[::-1] if permutation[0] % 2 else n
    installation.engine_roles = s, n
    installation.storage = api.Storage(api.Tape, None, None, api.words.BLANK, api.transfer,
        None, outputs=2, private=1, external_roles=(*s, *n, *auxiliary), engines=(service, native))
    protocol = (adapter or api.adapter).ReturnProtocol(parent, installation, api.owned,
        adopt or api.adopt, api.transfer, api.erase, mode=mode)
    fixed = tuple(t for t in (*physical(parent), *physical(service), *native.fixed,
                             *auxiliary, *installation.storage.roles) if t not in moving)
    return types.SimpleNamespace(parent=parent, service=service, native=native, i=installation,
        protocol=protocol, moving=moving, fixed=fixed, auxiliary=auxiliary)


def roles(f):
    return (f.parent.packet(0), f.parent.packet(1), f.service.packet(0),
            f.service.packet(1), f.native.output)


def meter(tapes):
    return tuple(sum(getattr(t.meter, k) for t in tapes) for k in RWM)


def snapshot(tapes):
    return tuple((id(t), bytes(t.cells), t.head) for t in tapes)


def oracle(f, expected):
    need(all(a is b for a, b in zip(roles(f), expected, strict=True)), "oracle role permutation")
    expected_owners = (set(physical(f.service)), {f.native.output, *f.native.fixed})
    need(tuple(map(set, f.i.engine_roles)) == expected_owners, "oracle engine ownership")
    need(set(physical(f.parent)).isdisjoint(set.union(*expected_owners)), "oracle producer separation")
    need(f.i.storage.external_roles == (*f.i.engine_roles[0], *f.i.engine_roles[1], *f.auxiliary),
         "oracle external bindings")
    for c in (f.parent, f.service):
        need(c.parked == (*c.roles.values(), *c.bank.packets, *c.private) == c.parking.roles,
             "oracle parked bindings")
    need(len(set((*physical(f.parent), *physical(f.service), f.native.output,
                  *f.native.fixed, *f.auxiliary, *f.i.storage.roles))) == len(f.fixed)+5,
         "oracle entire physical inventory conserved")


def edge(api, permutation, selected, lengths, *, adapter=None, adopt=None):
    f = fixture(api, permutation, lengths, adapter=adapter, adopt=adopt)
    expected = list(roles(f))
    old, result = expected[selected], expected[4]
    untouched = (*f.fixed, *(t for t in f.moving if t not in (old, result)))
    unchanged, result_image = snapshot(untouched), (bytes(result.cells), result.head)
    expected[selected], expected[4] = expected[4], expected[selected]
    before = meter((*f.fixed, *f.moving))
    c = f.parent if selected < 2 else f.service
    f.protocol(c, selected % 2, result)
    measured = tuple(a-b for a,b in zip(meter((*f.fixed, *f.moving)), before, strict=True))
    oracle(f, expected)
    need((bytes(result.cells), result.head) == result_image, "result physically preserved")
    need(old.head == 1 and all(x == api.words.BLANK for x in old.cells), "old body and marker retired")
    need(snapshot(untouched) == unchanged, "untouched physical roles preserved")
    return measured


def check_graph(api):
    identity = tuple(range(5))
    reached, todo, edges = {identity}, [identity], 0
    while todo:
        state = todo.pop()
        for selected in range(4):
            lengths = tuple((11*i + edges) % 17 for i in range(5))
            edge(api, state, selected, lengths)
            after = list(state)
            after[selected], after[4] = after[4], after[selected]
            key = tuple(after)
            if key not in reached:
                reached.add(key)
                todo.append(key)
            edges += 1
    need(reached == set(itertools.permutations(range(5))), "complete five-role permutation quotient")
    return {"states": len(reached), "directed_edges": edges, "max_payload_bits": 16}


def check_tariffs(api):
    count = 0
    for m, n, selected in itertools.product(range(13), range(13), range(4)):
        lengths = [3]*5
        lengths[selected], lengths[4] = m, n
        adopted = edge(api, tuple(range(5)), selected, lengths)
        f = fixture(api, tuple(range(5)), lengths, mode="fixed")
        c = f.parent if selected < 2 else f.service
        old, result = c.packet(selected % 2), f.native.output
        data = payload(result, api)
        positions = roles(f)
        untouched = (*f.fixed, *(t for t in f.moving if t not in (old, result)))
        unchanged = snapshot(untouched)
        before = meter((*f.fixed, *f.moving))
        f.protocol(c, selected % 2, result)
        fixed = tuple(a-b for a,b in zip(meter((*f.fixed, *f.moving)), before, strict=True))
        need(payload(old, api) == data and old.head == 1 and old.cells[0] == api.words.LEFT,
             "fixed-copy logical target")
        need(result.head == 1 and all(x == api.words.BLANK for x in result.cells), "fixed retired output")
        oracle(f, positions)
        need(snapshot(untouched) == unchanged, "fixed-copy untouched roles")
        need(tuple(a-b for a,b in zip(fixed, adopted, strict=True)) == (5*n+2, 2*n, 4*n+2),
             "unequal-length complete return tariff")
        count += 1
    return {"paired_fixtures": count, "old_and_return_lengths": [0, 12],
            "saved_reads": "5*n+2", "saved_writes": "2*n", "saved_moves": "4*n+2"}


def check_reuse(api):
    """An Euler tour executes every directed ownership edge on ONE fixture."""
    identity = tuple(range(5))
    remaining = {p: list(range(4)) for p in itertools.permutations(range(5))}
    stack, incoming, reverse = [identity], [], []
    while stack:
        state = stack[-1]
        if remaining[state]:
            selected = remaining[state].pop()
            after = list(state)
            after[selected], after[4] = after[4], after[selected]
            stack.append(tuple(after))
            incoming.append((state, selected))
        else:
            stack.pop()
            if incoming:
                reverse.append(incoming.pop())
    tour = list(reversed(reverse))
    need(len(tour) == len(set(tour)) == 480, "each directed edge exactly once in reuse tour")
    f = fixture(api, identity, (2, 3, 4, 5, 6))
    fixed_image = snapshot(f.fixed)
    for step, (state, selected) in enumerate(tour):
        need(tuple(f.moving.index(t) for t in roles(f)) == state, "continuous reuse state")
        result = f.native.output
        need(result.head == 1, "next fixture child receives canonical native output")
        # Test environment supplies the next completed return. This does not
        # implement or charge a C child, and preserves historical backing.
        bits = bytes((step+j) % 2 for j in range((7*step+5) % 19))
        size = max(len(result.cells), len(bits)+1)
        result.cells[:] = bytes([api.words.LEFT]) + bits + bytes([api.words.BLANK])*(size-len(bits)-1)
        expected = list(roles(f))
        old = expected[selected]
        expected[selected], expected[4] = expected[4], expected[selected]
        c = f.parent if selected < 2 else f.service
        f.protocol(c, selected % 2, result)
        oracle(f, expected)
        need(payload(result, api) == bits and result.head == 1, "reuse returned value")
        need(old.head == 1 and all(x == api.words.BLANK for x in old.cells), "reuse owned retirement")
        need(snapshot(f.fixed) == fixed_image, "reuse fixed physical roles")
    need(tuple(f.moving.index(t) for t in roles(f)) == identity, "closed reuse tour")
    return {"consecutive_returns": len(tour), "max_payload_bits": 18,
            "tour_sha256": sha(json.dumps(tour, separators=(",", ":")).encode()),
            "child_refills": "unmetered test environment; no C child executed"}


def rejects(call, message):
    try:
        call()
    except ValueError as error:
        need(str(error) == message, "wrong rejection: " + str(error))
    else:
        raise ValueError("control accepted: " + message)


def check_guards(api):
    def missing(f):
        s,n=f.i.engine_roles; f.i.engine_roles=(s,n[:-1])
    def duplicate(f):
        s,n=f.i.engine_roles; f.i.engine_roles=(s,(*n,n[0]))
    def external(f):
        f.i.storage.external_roles=f.i.storage.external_roles[::-1]
    def storage_alias(f):
        f.i.storage.outputs=(f.native.output,*f.i.storage.outputs[1:])
    def producer_alias(f):
        f.parent.roles["current"] = f.native.fixed[0]
        f.parent.parked = (*f.parent.roles.values(), *f.parent.bank.packets, *f.parent.private)
        f.parent.parking.roles = f.parent.parked
    def engine_alias(f):
        f.native.fixed = (f.service.bank.output,)
        f.i.engine_roles = f.i.engine_roles[0], (f.native.output, *f.native.fixed)
    def parked(f):
        f.parent.parking.roles=f.parent.parked[::-1]
    def opened(f):
        f.native.closed=False
    def head(f):
        f.native.output.head=2
    controls = ((missing,"current complete engine inventory"),
                (duplicate,"current complete engine inventory"),
                (external,"current complete external inventory"),
                (storage_alias,"exclusive physical caller/native/wrapper inventory"),
                (producer_alias,"producer disjoint from current engine inventories"),
                (engine_alias,"disjoint current engine inventories"),
                (parked,"complete current parked-role bindings"),
                (opened,"closed original protected return"),
                (head,"canonical adopted return and target heads"))
    for change, message in controls:
        f=fixture(api,tuple(range(5)),(2,3,4,5,6)); change(f)
        before=snapshot((*f.fixed,*f.moving))
        rejects(lambda: f.protocol(f.parent,0,f.native.output),message)
        need(snapshot((*f.fixed,*f.moving)) == before,"precondition failure must preserve payload/head")
    f=fixture(api,tuple(range(5)),(2,3,4,5,6))
    rejects(lambda:f.protocol(object(),0,f.native.output),"one of the two installed callers")
    rejects(lambda:f.protocol(f.parent,0,f.parent.output),"closed original protected return")
    return {"rejected_preconditions":len(controls)+2}


def replace_once(raw, old, new):
    text=raw.decode()
    need(text.count(old)==1,"unique mutation site")
    return text.replace(old,new).encode()


def check_mutants(api, sources):
    mutations = (
        ("native-cache", ADAPTER, "native = self.exchange(native, result, old)", "pass"),
        ("service-cache", ADAPTER, "service = self.exchange(service, old, result)", "pass"),
        ("external-cache", ADAPTER, "i.storage.external_roles = (*service, *native, *self.auxiliary)", "pass"),
        ("parked-cache", "adoption", "self.parking.roles = self.parked", "pass"),
        ("backend-output", "adoption", "self.native_child.output = old", "pass"),
        ("owned-erasure", "adoption", "erase_marker(old)", "pass"),
    )
    expected = {"native-cache": "current complete engine inventory",
                "service-cache": "current complete engine inventory",
                "external-cache": "current complete external inventory",
                "parked-cache": "current complete engine inventory",
                "backend-output": "current complete engine inventory",
                "owned-erasure": "old body and marker retired"}
    caught=[]
    for label, source, old, new in mutations:
        adapter,adopt=api.adapter,api.adopt
        if source==ADAPTER:
            adapter=module("mutant_adapter",replace_once(sources[ADAPTER],old,new))
        else:
            adopt=function(replace_once(api.adoption_raw,old,new),"adopt_return",api.environment)
        try:
            edge(api,tuple(range(5)),2,(2,3,4,5,6),adapter=adapter,adopt=adopt)
        except ValueError as error:
            need(str(error) == expected[label], "mutant must fail at expected semantic boundary")
            caught.append({"mutation":label,"rejected_by":str(error)})
        else:
            raise ValueError("semantic mutant survived: "+label)
    return caught


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json",action="store_true")
    args=parser.parse_args()
    sources=authenticate()
    api,nested=load(sources)
    result={"scope":"finite return-boundary audit; no whole-caller or kappa claim",
            "nested_source_sha256":nested,"graph":check_graph(api),
            "reuse":check_reuse(api),"tariffs":check_tariffs(api),"guards":check_guards(api),
            "semantic_mutations":check_mutants(api,sources)}
    need(authenticate()==sources,"inputs remain unchanged")
    if args.json:
        print(json.dumps(result,indent=2,sort_keys=True))
    else:
        print("PASS_QQ16_RETURN_INVENTORY_AUDIT states=120 edges=480 reuse=480 tariffs=676 guards=11 mutants=6 no_new_kappa")


if __name__=="__main__":
    main()
