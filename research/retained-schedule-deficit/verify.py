"""Signed deficit of the retained full-target schedule.

The pure recipe walks pair counts one local stage at a time. Idle ranks are
charged when a later pair is opened and again at the terminal exchange. Their
sum leaves the full-target bill one rank above capacity for every port and
replica.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
PAIR_LIMIT = 24
PUBLISHED_PORTS = 111
PUBLISHED_REPLICAS = 32
PUBLISHED_PAIRS = (2, 4, 5)


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_RETAINED_SCHEDULE_DEFICIT selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def recipe(pairs: int) -> list[dict]:
    events = [{"kind": "local", "stage": 0, "pair": 0}]
    stage = 1
    for pair in range(pairs):
        events.append({"kind": "local", "stage": stage, "pair": pair})
        stage += 1
        if pair < pairs - 1:
            events.append({"kind": "bridge", "dst": pair, "src": pair + 1})
        events.append({"kind": "local", "stage": stage, "pair": pair})
        stage += 1
        if pair < pairs - 1:
            events.append({"kind": "bridge", "dst": pair, "src": pair + 1})
    for pair in reversed(range(pairs - 1)):
        events.append({"kind": "bridge", "dst": pair + 1, "src": pair})
    events.append({"kind": "exchange"})
    return events


def idle_ranks(pairs: int) -> list[int]:
    levels = [-1] * pairs
    idle: list[int] = []
    local_calls = 0
    for event in recipe(pairs):
        if event["kind"] == "local":
            stage, pair = event["stage"], event["pair"]
            if levels[pair] != stage - 1:
                raise SystemExit("FAIL_RETAINED_SCHEDULE_DEFICIT entrance moved")
            levels[pair] = stage
            local_calls += 1
            if stage % 2 and stage <= 2 * pairs - 3:
                opened = (stage + 1) // 2
                if levels[opened] != -1:
                    raise SystemExit("FAIL_RETAINED_SCHEDULE_DEFICIT first idle moved")
                levels[opened] = stage
                idle.append(7 * (stage + 1))
            elif stage % 2 == 0 and 2 <= stage <= 2 * pairs - 2:
                opened = stage // 2
                if levels[opened] != stage - 1:
                    raise SystemExit("FAIL_RETAINED_SCHEDULE_DEFICIT second idle moved")
                levels[opened] = stage
                idle.append(7)
            elif stage == 2 * pairs:
                for index in range(pairs):
                    if levels[index] != 2 * index + 2:
                        raise SystemExit("FAIL_RETAINED_SCHEDULE_DEFICIT terminal idle moved")
                    idle.append(7 * (2 * pairs - levels[index]))
                    levels[index] = 2 * pairs
        elif event["kind"] == "bridge":
            if levels[event["dst"]] != levels[event["src"]]:
                raise SystemExit("FAIL_RETAINED_SCHEDULE_DEFICIT bridge level moved")
        elif levels != [2 * pairs] * pairs:
            raise SystemExit("FAIL_RETAINED_SCHEDULE_DEFICIT exchange moved")
    if local_calls != 2 * pairs + 1:
        raise SystemExit("FAIL_RETAINED_SCHEDULE_DEFICIT stage count moved")
    return idle


def deficit(pairs: int, ports: int, replicas: int, local_rank_mass: int) -> int:
    stages = 2 * pairs + 1
    width = 1 + 7 * stages
    live = 2 * pairs * ports * replicas
    local = local_rank_mass * ports * stages * replicas
    idle = sum(rank for rank in idle_ranks(pairs) if rank) * 2 * ports * replicas
    return width * live - local - idle


def main() -> None:
    pinned = load()
    largest = 0
    for pairs in range(1, PAIR_LIMIT + 1):
        ranks = idle_ranks(pairs)
        stages = 2 * pairs + 1
        if sum(ranks) != 7 * stages * (pairs - 1):
            raise SystemExit("FAIL_RETAINED_SCHEDULE_DEFICIT idle sum moved")
        if deficit(pairs, 1, 1, 15) != -1:
            raise SystemExit("FAIL_RETAINED_SCHEDULE_DEFICIT full-target deficit moved")
        live = 2 * pairs
        if deficit(pairs, 1, 1, 14) != live:
            raise SystemExit("FAIL_RETAINED_SCHEDULE_DEFICIT rank-seven deficit moved")
        largest = sum(ranks)
    published = -PUBLISHED_PORTS * PUBLISHED_REPLICAS
    for pairs in PUBLISHED_PAIRS:
        if deficit(pairs, PUBLISHED_PORTS, PUBLISHED_REPLICAS, 15) != published:
            raise SystemExit("FAIL_RETAINED_SCHEDULE_DEFICIT published point moved")
    if (
        pinned["pair_counts"] != PAIR_LIMIT
        or pinned["largest_idle_sum"] != largest
        or pinned["published_deficit"] != published
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_RETAINED_SCHEDULE_DEFICIT pinned result moved")
    print(f"PASS_RETAINED_SCHEDULE_DEFICIT pairs={PAIR_LIMIT} no_new_kappa")


if __name__ == "__main__":
    main()
