"""Exact cut for a shared Type B stage-9 Walsh basis through clock 2866."""
from collections import Counter, deque
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PIN = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
NATIVE = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
SIGNED = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PREDECESSOR = "c44a551b92786725cc2b805d6cf3b2547e66d711"
STAGE, TARGET, EVENTS, ROLES = 9, 2866, 4783, 36
WALSH, ORIGINAL = -2, -1


def timeout(*_):
    raise TimeoutError("60-second stage-9 forced cut")


def contact_graph(tape, roles):
    latest = dict.fromkeys(roles, ORIGINAL)
    edges = []
    rewards = {}
    boundaries = []
    types = Counter()
    for clock, op in enumerate(tape):
        kind = op[0]
        if kind == "A":
            continue
        if kind == "J":
            assert len(op) == 4 and len(op[3]) == 4
            touched = op[3][:2]
            if op[1] == STAGE:
                boundaries.append(clock)
            operation = "J"
        else:
            assert kind == "B"
            _, operation, first, *args = op
            touched = [first]
            if operation == "SWAP":
                second, = args
                assert first != second and first in latest and second in latest
                latest[first], latest[second] = latest[second], latest[first]
                types[operation] += 1
                continue
            if operation == "ADD":
                second, coefficient = args
                assert Fraction(coefficient)
                touched.append(second)
            elif operation == "QUERY":
                second, exponent = args
                assert exponent in (-1,1)
                touched.append(second)
                boundaries.append(clock)
            elif operation in ("IDLE_ONE","IDLE_ODD"):
                mask = args[0]
                assert mask and len(set(mask)) == len(mask) and all(1 <= s <= 18 for s in mask)
                if operation == "IDLE_ODD":
                    assert len(args) == 2 and args[1] in (-1,1)
                elif STAGE in mask:
                    rewards[clock] = 8*len(mask)
            else:
                assert operation in ("SCALE","LAMBDA") and len(args) == 1
                assert Fraction(args[0])
        assert all(role in latest for role in touched) and len(set(touched)) == len(touched)
        for role in touched:
            edges.append((latest[role],clock))
            latest[role] = clock
        types[operation] += 1
    edges.extend((last,ORIGINAL) for last in latest.values())
    return edges,rewards,boundaries,types


def arc(graph, a, b, capacity):
    graph.setdefault(a,Counter())[b] += capacity
    graph.setdefault(b,Counter())[a] += 0


def solve(edges, rewards, anchors, forced):
    graph = {}
    inf = len(edges)+len(rewards)+1
    for a,b in edges:
        if a != b:
            arc(graph,a,b,1)
            arc(graph,b,a,1)
    for v in rewards:
        arc(graph,WALSH,v,1)
    for v in anchors:
        arc(graph,v,ORIGINAL,inf)
    arc(graph,WALSH,forced,inf)
    raw = {v: e.copy() for v,e in graph.items()}
    paths = []
    while True:
        parents = {WALSH:None}
        queue = deque([WALSH])
        while queue and ORIGINAL not in parents:
            a = queue.popleft()
            for b, available in graph[a].items():
                if available and b not in parents:
                    parents[b] = a
                    queue.append(b)
        if ORIGINAL not in parents:
            side = set(parents)
            break
        path = [ORIGINAL]
        while path[-1] != WALSH:
            path.append(parents[path[-1]])
        path.reverse()
        amount = min(graph[a][b] for a,b in zip(path,path[1:]))
        for a,b in zip(path,path[1:]):
            graph[a][b] -= amount
            graph[b][a] += amount
        paths.append((amount,path))
    cut = sum(c for a,arcs in raw.items() if a in side for b,c in arcs.items() if b not in side)
    flow = sum(amount for amount,_ in paths)
    assert cut == flow
    assert ORIGINAL not in side and forced in side and not set(anchors)&side
    active = sorted(v for v in rewards if v in side)
    transitions = [(a,b) for a,b in edges if (a in side)!=(b in side)]
    assert cut == len(rewards)-len(active)+len(transitions)
    return {"cut":cut,"flow_paths":paths,"walsh_clocks":sorted(side-{WALSH}),
            "credited_clocks":active,"transitions":transitions,
            "upper_h8_units_per_port":len(active)-len(transitions)}


def main():
    assert __debug__
    signal(SIGALRM,timeout)
    alarm(60)
    raw = (ROOT/"inputs"/"CALLER.json").read_bytes()
    assert sha256(raw).hexdigest() == PIN
    caller = loads(raw)
    tape = caller["events"]
    typ = caller["types"]["B"]
    assert len(tape) == EVENTS and tape[TARGET] == ["B","IDLE_ONE",36,[9]]
    assert typ["offset"] == typ["roles"] == ROLES
    ports = typ["ports"]
    assert ports == [15,17,27,34,35,42,47,55]
    edges,rewards,boundaries,types = contact_graph(tape,range(ROLES,2*ROLES))
    assert types["J"] == 17 and boundaries == [3058] and rewards[TARGET] == 8
    # Known-good and missing-return control have identical input and gain.
    control = [(ORIGINAL,0),(0,ORIGINAL)]
    assert solve(control,{0:8},[],0)["upper_h8_units_per_port"] == -1
    assert solve(control[:-1],{0:8},[],0)["upper_h8_units_per_port"] == 0
    result = solve(edges,rewards,boundaries,TARGET)
    alarm(0)
    print(dumps({"native_head":NATIVE,"signed_head":SIGNED,"predecessor":PREDECESSOR,
                 "pins":{"inputs/CALLER.json":PIN},"ports":ports,"tape_events":EVENTS,
                 "roles":ROLES,"forced":TARGET,"stage":STAGE,"anchors":boundaries,
                 "runner_cap_seconds":60,"edge_count":len(edges),"typed_events":types,
                 "rewards":rewards,"discount_upper":"H(r)-H(r-8) <= H(8) for 0<kappa<1",
                 "uncredited_odd_relaxation":"either basis, no credit",**result},
                indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
