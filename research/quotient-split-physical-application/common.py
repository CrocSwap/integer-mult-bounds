"""Read the fixed composition and bind its compact public interface."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))
import physical

GRAPH = "5183479ecac34a1cb5c046f202e19d7161679265fe121b4a0af922fe344d8fc1"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(name):
    raw = (HERE / name).read_bytes()
    return json.loads(gzip.decompress(raw) if str(name).endswith(".gz") else raw)


def digest(value):
    return sha256(physical.encoded(value)).hexdigest()


def receipt(name, value):
    actual = json.loads(json.dumps(value))
    need(actual == read(f"results/{name}.json"), "receipt mismatch: " + name)


def inputs():
    graph, layout = read("data/GRAPH.json.gz"), read("data/LAYOUT.json")
    n, first = len(graph["initial"]), graph["first_output"]
    need(digest(graph) == GRAPH and n == layout["public"] == len(graph["final"]) == 1470
         and first == 154768, "fixed graph and public namespace")
    need(layout["frames"] == graph["frames"] and len(layout["live"]) == len(layout["ports"]) == 104,
         "port inventory")
    h = layout["hosted"]
    hosted, planes = set(h["Dports"]), list(zip(h["X2"], h["Y2"], strict=True))
    need(len(hosted) == len(planes) == 96, "hosted ports")
    mains = set(layout["live"]) | {x + 112 for x in layout["live"]} | set(h["X2"]) | set(h["Y2"])
    need(len(mains) == 400 and mains <= set(range(n)), "main labels")
    frames, initial, final = graph["frames"], graph["initial"], graph["final"]
    for x, q in zip(layout["live"], layout["ports"], strict=True):
        y = x + 112
        need(frames[initial[x]] == [q] and frames[initial[y]] == []
             and frames[final[x]] == [1 << j for j in range(9)] and len(frames[final[y]]) == 8
             and all((v & q).bit_count() % 2 == 0 for v in frames[final[y]]), "main frames")
    for i, pair in zip(h["Dports"], planes, strict=True):
        need(all(graph[boundary][a] == graph[boundary][b] for boundary in ("initial", "final")
                 for a, b in zip((layout["live"][i], layout["live"][i] + 112), pair, strict=True)),
             "hosted frames")
    labels = layout["source_labels"]
    need(len(labels) == len(set(labels)) == n, "distinct source owners")
    for old in (325, 1087):
        r = labels.index(old)
        need(r not in mains and (initial[r], final[r]) == (3, 237), "protected helper")
    for r, a, b in ((126, 3, 498), (278, 3, 595), (1468, 498, 127), (1469, 595, 127)):
        need(r not in mains and (initial[r], final[r]) == (a, b), "split owner")
    moves = {k: (a, b) for k, a, b in graph["moves"]}
    rows = {k: [(d, physical.exact_coefficient(q)) for d, q in row] for k, row in graph["forms"]}
    terminals = set(range(first, first + n))
    need(len(moves) == len(graph["moves"]) == 6054 and all(0 <= k < first for k in moves), "paid slots")
    need(len(rows) == len(graph["forms"]) == len(moves) + n and set(rows) == set(moves) | terminals
         and len(graph["schedule"]) == len(rows) and set(graph["schedule"]) == set(rows), "row inventory")
    need(all([d for d, _ in row] == sorted({d for d, _ in row}) for row in rows.values()), "donor order")
    return graph, layout, moves, rows, (mains, hosted, planes)


def jobs(graph, mains, moves):
    frames = graph["frames"]
    helpers = [(a, b) for r, (a, b) in enumerate(zip(graph["initial"], graph["final"], strict=True))
               if r not in mains]
    pairs = set(moves.values()) | set(helpers)
    spans = {i: physical.chart_span(frames[i]) for i in {j for pair in pairs for j in pair}}
    need(all(spans[a] < spans[b] for a, b in helpers), "positive helper orientation")
    need(all(spans[a] < spans[b] or spans[b] < spans[a] for a, b in pairs), "nested paid routes")
    def rank(pair):
        a, b = pair
        return abs(len(frames[a]) - len(frames[b]))
    return Counter(map(rank, moves.values())), Counter(map(rank, helpers)), pairs


def owner_stages(layout, mains, caller):
    h = layout["hosted"]
    second = dict(zip(h["Dports"], zip(h["X2"], h["Y2"], strict=True), strict=True))
    seen, stages = set(), []
    for event in caller["events"]:
        if event[0] != "J":
            continue
        _, stage, group_a, group_b = event
        bound = {}
        for i, x in enumerate(layout["live"]):
            for slot, role in zip((x, x + 112) + second.get(i, ()),
                                  group_a if i in second else group_b[:2], strict=True):
                need(slot not in bound, "main owner alias")
                bound[slot] = (i, role)
        need(bound.keys() == mains and len(set(bound.values())) == 400, "signed main owners")
        fresh = {(stage, layout["source_labels"][r]) for r in range(layout["public"]) if r not in mains}
        need(len(fresh) == 1070 and fresh.isdisjoint(seen), "distinct stage helper owners")
        seen.update(fresh)
        stages.append([stage, len(bound), len(fresh)])
    need([s[0] for s in stages] == list(range(1, 17)), "complete stages")
    return stages


def provenance():
    pins = read("SOURCE-PINS.json")
    for pin in pins:
        raw = (HERE / pin["path"]).read_bytes()
        need(sha256(raw).hexdigest() == pin["sha256"], "source bytes: " + pin["path"])
    for pin in read("SOURCES.json")["files"]:
        if pin["usage"] == "input":
            need(sha256((HERE.parents[1] / pin["path"]).read_bytes()).hexdigest() == pin["sha256"],
                 "external input: " + pin["path"])
    return len(pins)
