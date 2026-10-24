#!/usr/bin/env python3
"""Rebuild owner timelines without importing the certificate checker.

THU New Media Research Center (@thu-nmrc), with substantial OpenAI Codex
assistance in a separate research context. Apache-2.0. This is a second
finite source check, not independent human or proof-kernel acceptance.
"""
from collections import defaultdict
import gzip
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz"
PAYLOAD = "cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def span(basis):
    result = {0}
    for vector in basis:
        result |= {value ^ vector for value in tuple(result)}
    return result


def scalar_owners(event):
    gate = event[1]
    operands = gate[1:3] if gate[0] in ("add", "copy") else gate[1:2]
    return [operand[1] for operand in operands if operand[0] == "L"]


def audit():
    body = gzip.decompress(SOURCE.read_bytes())
    need(sha256(body).hexdigest() == PAYLOAD, "independent source payload")
    source = json.loads(body)
    canonical = source["canonical"]
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    directions = {}
    for direction in ("forward", "backward"):
        program = [event for event in source["programs"][direction]
                   if event[0] != "climb"]
        timelines = [[] for _ in range(632)]
        for index, event in enumerate(program):
            if event[0] == "scalar":
                for owner in scalar_owners(event):
                    timelines[owner].append((index, "scalar"))
            elif event[0] == "warp":
                timelines[event[1][1]].append((index, "warp"))
        graph = defaultdict(set)
        for owner, timeline in enumerate(timelines):
            for (left, kind_left), (right, kind_right) in zip(timeline, timeline[1:]):
                if kind_left == kind_right == "scalar":
                    graph[left].add(right)
            if 112 <= owner < 224 and timeline and timeline[-1][1] == "scalar":
                graph[timeline[-1][0]].add(("Y", owner))
        cases = []
        for case in certificate["cases"]:
            start = case["next_scalar"]
            seen, queue = {start}, [start]
            for node in queue:
                for successor in graph[node]:
                    if successor not in seen:
                        seen.add(successor)
                        queue.append(successor)
            exits = sorted(node[1] for node in seen if isinstance(node, tuple))
            kernel = set(range(512))
            for owner in exits:
                kernel &= span(canonical["frames"][canonical["final"][owner]])
            need(kernel == {0, case["input_vector"]}, "complete reachable-exit kernel")
            links = 0
            for witness in case["witnesses"]:
                for left, right, owner in zip(witness["nodes"], witness["nodes"][1:],
                                              witness["roles"]):
                    timeline = timelines[owner]
                    if right[0] == "exit":
                        need(owner == right[1] and timeline[-1] == (left[1], "scalar"),
                             "independent literal terminal link")
                    else:
                        position = timeline.index((left[1], "scalar"))
                        need(timeline[position + 1] == (right[1], "scalar")
                             and right[1] > left[1], "independent literal consecutive link")
                    links += 1
            cases.append({"operator": case["operator"], "reachable_main_Y_exits": len(exits),
                          "kernel": sorted(kernel), "certified_path_links": links})
        directions[direction] = cases
    return {"status": "PASS_INDEPENDENT_INVERSE_PRELUDE_EXIT_KERNELS_AND_ALL_PATH_OWNERS",
            "payload_sha256": PAYLOAD, "directions": directions,
            "cases": sum(map(len, directions.values())),
            "path_links": sum(case["certified_path_links"]
                              for cases in directions.values() for case in cases)}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    receipt = audit()
    path = HERE / "INDEPENDENT.json"
    if arguments.write:
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        need(receipt == json.loads(path.read_text()), "independent deterministic receipt")
    print(json.dumps({key: receipt[key] for key in ("status", "cases", "path_links")},
                     sort_keys=True))
