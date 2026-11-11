"""Price-ranked one-helper fusion geometry. No rational support solver."""
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import tarfile
import time

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
OLD_WORD = "0358b9f6e0340fb3e5aa46c747c558b32a5280cbf9cd92c3b9de627dd18a9a4f"
NEW_WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
RANK_PRICE = "4a7841699dd17688f6aada5c902a2a91e94558b2b1b4460c46b0e55aa95b3f9f"
PROTECTED = {319, 863, 1355, 1568}
PAIR_CAP = 64
RUN_CAP = 25


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def roles(event):
    return event[1:3] if event[0] in ("ADD", "COPY") else event[1:2]


def span(basis):
    out = {0}
    for a in basis:
        out.update(a ^ b for b in tuple(out))
    return out


class Geometry:
    def __init__(self, word, protected):
        self.program = word["program"]
        self.n = word["public"]
        self.protected = protected
        self.initial = word["initial"]
        self.final = word["final"]
        self.rank = list(map(len, word["frames"]))
        self.spaces = [span(basis) for basis in word["frames"]]
        self.boundary = (set(word["live"]) | {r + 112 for r in word["live"]} |
                         set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"]))
        self.contacts = defaultdict(list)
        self.moves = defaultdict(list)
        self.banks = defaultdict(list)
        self.first_at_bank = {}
        self.parents = {}
        aux_end = self.n + word["owned_fields"]
        self.available = set(range(self.n, aux_end))
        self.availability = [(-1, min(self.available) if self.available else None)]
        self.owned = {}
        for clock, event in enumerate(self.program):
            op, role = event[:2]
            if op == "MOVE":
                self.moves[role].append(clock)
                if role >= self.n:
                    require(self.owned.get(role) == event[2], "owned MOVE chart mismatch")
                    self.owned[role] = event[3]
                continue
            for r in roles(event):
                self.contacts[r].append(clock)
            if op in ("INIT", "CLEAR"):
                require(self.n <= role < aux_end, "owner outside stock")
                if op == "INIT":
                    self.available.remove(role)
                    self.owned[role] = event[-1]
                else:
                    require(self.owned.pop(role) == event[-1], "mismatched owned chart")
                    self.available.add(role)
                self.availability.append((clock, min(self.available) if self.available else None))
                continue
            require(op in ("ADD", "SCALE", "COPY"), "unexpected scalar op")
            self.parents[clock] = clock
            for r in roles(event):
                key = (event[-1], r)
                if key in self.first_at_bank:
                    self.parents[self.parent(clock)] = self.parent(self.first_at_bank[key])
                else:
                    self.first_at_bank[key] = clock
        require(not self.owned, "source owner leak")
        self.owned_cuts = [clock for clock, _ in self.availability]
        for clock in self.parents:
            self.banks[self.parent(clock)].append(clock)

    def parent(self, clock):
        while self.parents[clock] != clock:
            self.parents[clock] = self.parents[self.parents[clock]]
            clock = self.parents[clock]
        return clock

    def stock(self):
        rows = []
        for h, clocks in self.moves.items():
            if h >= self.n or h in self.protected or h in self.boundary:
                continue
            for first, second in zip(clocks, clocks[1:]):
                _, _, a, b, own1 = self.program[first]
                _, _, origin, c, own2 = self.program[second]
                if own1 or own2 or b != origin or not (self.rank[a] < self.rank[b] < self.rank[c]):
                    continue
                left = bisect_right(self.contacts[h], first)
                right = bisect_left(self.contacts[h], second)
                if left == right:
                    continue
                before = self.contacts[h][left:right]
                if any(self.program[t][-1] != b for t in before):
                    continue
                r1, r2 = self.rank[b] - self.rank[a], self.rank[c] - self.rank[b]
                if r1 + r2 <= 9:
                    rows.append((h, first, second, a, b, c, r1, r2))
        return rows

    def first_idle(self, lo, hi):
        i = bisect_left(self.owned_cuts, lo) - 1
        while i < len(self.availability):
            t, label = self.availability[i]
            cut = max(lo, t + 1)
            if cut > hi:
                return None
            if label is not None:
                return cut, label
            i += 1
        return None

    def geometry(self, row):
        h, first, second, a, b, c, r1, r2 = row
        require(self.spaces[a] < self.spaces[b] < self.spaces[c], "source ascents not nested")
        block = self.banks[self.parent(self.first_at_bank[b, h])]
        members = sorted({r for t in block for r in roles(self.program[t])})
        if len(block) > 24 or len(members) > 20:
            return "component_limit", None
        if set(members) & self.protected or members[-1] >= self.n:
            return "protected_or_owned_component", None
        if any(self.program[t][0] == "COPY" for t in block):
            return "copy_in_component", None

        lo, hi = 0, len(self.program)
        low, high, routes = [], [], {}
        block_members = set(block)
        for r in members:
            contacts = self.contacts[r]
            used = [t for t in block if r in roles(self.program[t])]
            i = bisect_left(contacts, used[0])
            j = bisect_right(contacts, used[-1])
            if contacts[i:j] != used:
                return "external_intervening_contact", None
            left = contacts[i - 1] if i else -1
            right = contacts[j] if j < len(contacts) else len(self.program)
            lo, hi = max(lo, left + 1), min(hi, right)
            if lo > hi:
                return "empty_common_clock", None
            route = self.moves[r]
            m = route[bisect_right(route, left):bisect_left(route, right)]
            old_start = self.program[left][-1] if left >= 0 else self.initial[r]
            old_end = self.program[right][-1] if right < len(self.program) else self.final[r]
            charts = [old_start]
            for t in m:
                _, _, src, dst, own = self.program[t]
                if own or charts[-1] != src or not self.spaces[src] < self.spaces[dst]:
                    return "literal_route_mismatch", None
                charts.append(dst)
            if charts[-1] != old_end or b not in charts or charts.count(b) != 1:
                return "literal_route_mismatch", None
            gap = charts.index(b)
            if any(t not in block_members for t in self.contacts[r][i:j]):
                return "external_intervening_contact", None
            if any(m[slot] > used[0] for slot in range(gap)) or any(
                m[slot] < used[-1] for slot in range(gap, len(m))
            ):
                return "body_chart_not_contiguous", None
            routes[r] = {"move_clocks": m, "charts": charts}
            if r == h:
                if not first < used[0] <= used[-1] < second:
                    return "pivot_block_outside_lifts", None
            else:
                if a in charts[:gap]:
                    low.append(r)
                if c in charts[gap + 1:]:
                    high.append(r)
        if not low or not high:
            return "missing_low_or_high_stock", None
        idle = self.first_idle(lo, hi)
        if idle is None:
            return "no_idle_owned_label", None
        cut, aux = idle
        return "geometry_survivor", {
            "key": f"{h}:{first}:{second}", "h": h, "chart_path": [a, b, c],
            "move_clocks": [first, second], "rank_pair": [r1, r2],
            "block": block, "roles": members, "boundary_roles": sorted(self.boundary.intersection(members)),
            "low": low, "high": high, "clock": cut, "clock_range": [lo, hi], "aux": aux,
            "original_routes": routes,
        }


def run_control(archive):
    with tarfile.open(archive) as tf:
        raw = gzip.decompress(tf.extractfile("research/p104-funded-863-return/WORD.json.gz").read())
    require(digest(raw) == OLD_WORD, "wrong predecessor canonical word")
    word = json.loads(raw)
    engine = Geometry(word, PROTECTED - {319})
    row = (319, 43029, 46308, 1089, 207, 127, 5, 1)
    require(row in engine.stock(), "known-good source stock")
    reason, result = engine.geometry(row)
    require(reason == "geometry_survivor" and len(result["block"]) == 18 and len(result["roles"]) == 14,
            "known-good exact maximal coframe block")
    require(result["clock_range"] == [44616, 45718] and 1081 in result["low"] and
            {1081, 1467} <= set(result["high"]), "known-good stock or common clock")
    t = result["clock"]
    for r in [1567]:
        events = [op[0] for op in word["program"][:t] if op[1] == r and op[0] in ("INIT", "CLEAR")]
        require(not events or events[-1] == "CLEAR", "known-good owned label is not idle")
    blocked = result["block"][0]
    original = word["program"][blocked]
    word["program"][blocked] = ["COPY", *original[1:3], 207]
    mutated = Geometry(word, PROTECTED - {319})
    require(mutated.geometry(row)[0] == "copy_in_component", "COPY control did not reject")
    word["program"][blocked] = original
    available = engine.availability
    engine.availability = [(clock, None) for clock, _ in available]
    require(engine.geometry(row)[0] == "no_idle_owned_label", "dirty auxiliary control did not reject")
    return {"status": "PASS_KNOWN_GOOD_AND_CONTROLS", "known_good": result,
            "copy_control": "rejected", "no_idle_owned_control": "rejected"}


def run_candidate(args):
    require(args.admission and args.admission_sha, "exact admission required before candidate decoding")
    admission = args.admission.read_bytes()
    require(digest(admission) == args.admission_sha and HEAD.encode() in admission, "wrong exact admission")
    price_bytes = args.price.read_bytes()
    require(digest(price_bytes) == RANK_PRICE, "wrong predecode price")
    price = json.loads(price_bytes)
    prices = price["rank_prices"]
    packed = args.word.read_bytes()
    require(digest(packed) == NEW_WORD, "wrong candidate word")
    start = time.monotonic()
    word = json.loads(gzip.decompress(packed))
    engine = Geometry(word, PROTECTED)
    public_moves = sum(len(clocks) for role, clocks in engine.moves.items() if role < engine.n)
    require(public_moves == price["public_paid_moves"] == 6232, "wrong public MOVE stock")

    def key(row):
        r1, r2 = sorted(row[-2:])
        return f"{r1}+{r2}"

    stock = engine.stock()
    stock.sort(key=lambda row: (-Fraction(prices[key(row)]["credit"][1]), row[:3]))
    visited, survivors = [], []
    for row in stock:
        if len(visited) >= PAIR_CAP or time.monotonic() - start >= RUN_CAP:
            break
        reason, result = engine.geometry(row)
        visited.append({"key": ":".join(map(str, row[:3])), "rank_type": key(row), "reason": reason})
        if result is not None:
            survivors.append(result)
    unvisited = [{"key": ":".join(map(str, row[:3])), "rank_type": key(row),
                  "credit_upper": prices[key(row)]["credit"][1]} for row in stock[len(visited):]]
    return {
        "status": "EXHAUSTED" if not unvisited else "CAPPED",
        "comparator_head": HEAD, "word_sha256": NEW_WORD, "price_sha256": RANK_PRICE,
        "admission_sha256": args.admission_sha, "public_moves": public_moves,
        "eligible_paid_pairs_before_geometry": len(stock),
        "inventory_by_rank_type": dict(Counter(map(key, stock))),
        "case_cap": PAIR_CAP, "runner_cap_seconds": RUN_CAP,
        "visited": visited, "unvisited": unvisited, "unresolved": len(unvisited),
        "disposition": dict(Counter(row["reason"] for row in visited)), "survivors": survivors,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--control-archive", type=Path)
    p.add_argument("--word", type=Path)
    p.add_argument("--price", type=Path)
    p.add_argument("--admission", type=Path)
    p.add_argument("--admission-sha")
    args = p.parse_args()
    result = run_control(args.control_archive) if args.control_archive else run_candidate(args)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
