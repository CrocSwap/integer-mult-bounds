#!/usr/bin/env python3
"""Shared QQ16 source binder; Apache-2.0.

Adapted from Nick Petalas's PR2181 verify.py at
 e18ca76987f5945c6a4b5b6bebbe73cdab3c4561.
The source extraction, Gram checks and chart-swap checks retain his credit.
Prepared for commdata2338, with substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
import gzip
import hashlib
import io
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKET = "research/joint-query/certificate.json.gz"
PINS = {
    'research/joint-query/evidence/JOINT-QUERY-TRANSFER.md': '9e13e73ebf3192a6548798c2f1d13bd4d83957e8db0dc34de12b1a5311a52a75',
    PACKET: "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7",
    "research/joint-query/evidence/QQ16-SELECTED-WITNESS.md":
        "52f2ee565320f05282c637aa79eee100606c24240b1b5866f0c8d62e7913c9fc",
    "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json":
        "e35e5868a1322e406191079c0675975b139692ba50b1e2e5fb8a40b6480519f4",
    "research/joint-query/evidence/QQ16-RATIONAL-OBSERVATION-REVIEW.md":
        "9a06ff40830ef80d3566fce77c78639cb64d519d487a0a7f57d543c3146e2c49",
}
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
U = tuple(p for p in range(112) if p not in A + T)
IDENTITY = tuple(1 << i for i in range(25))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_packet(repo):
    raw_packet = None
    for name, expected in PINS.items():
        path = repo / name
        need(path.is_file() and path.stat().st_size <= 1_048_576,
             "source size: " + name)
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == expected, "source pin: " + name)
        if name == PACKET:
            raw_packet = raw
    need(raw_packet is not None, "missing packet")
    with gzip.GzipFile(fileobj=io.BytesIO(raw_packet)) as stream:
        payload = stream.read(16_777_217)
    need(len(payload) <= 16_777_216, "decompressed packet size")
    return json.loads(payload)


def apply(columns, vector):
    result = 0
    # Every vector is in the validated 25-axis space.
    for _ in range(25):
        if not vector:
            return result
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    need(vector == 0, "binary vector bound")
    return result


def compose(left, right):
    return tuple(apply(left, c) for c in right)


def route(packet, event):
    need(event[0] == "cover_map", "cover map event")
    columns = packet["map_registry"][event[2]]["owner_right_matrix_columns"]
    need(len(columns) == 73 and all(type(c) is int for c in columns),
         "73 integer route columns")
    need(all(0 < c < 1 << 25 for c in columns[:25]), "active route axes")
    need(columns[25:] == [1 << i for i in range(25, 73)],
         "route must fix all 48 spectator axes")
    return tuple(columns[:25])


def packet_data(packet):
    need((tuple(packet["A_ports"]), tuple(packet["T_ports"]),
          tuple(packet["U_ports"])) == (A, T, U), "selected partition")
    need(len(packet["R_rows"]) == 8, "eight query rows")
    R = [[Q(row.get(str(p), 0)) for p in range(112)]
         for row in packet["R_rows"]]
    need(all(x.denominator == 1 for row in R for x in row), "integer query")
    R = [[int(x) for x in row] for row in R]
    routes = [[IDENTITY] * 112]
    for stage in (1, 2):
        word = packet["programs"][f"F_{stage}"]
        need(word[113][:2] == ["cover_sweep", "X_A_fused_query"],
             "forward alignment cut")
        events = word[1:113]
        need([e[1] for e in events] == [["L", p] for p in range(112)],
             "forward port order")
        routes.append([route(packet, e) for e in events])
    need(packet["programs"]["F_0"][1][:2] ==
         ["cover_sweep", "X_A_fused_query"], "stage-zero identity cut")
    word = packet["programs"]["B_1_2"]
    need(len(word) <= 40_000, "backward event bound")
    future = next(i for i, e in enumerate(word)
                  if e[:2] == ["cover_sweep", "future_E_t"])
    current = next(i for i, e in enumerate(word)
                   if e[:2] == ["cover_sweep", "Y_U_from_X_T"])
    for stage, events in ((2, word[future - 112:future]),
                          (1, word[current - 120:current - 8])):
        need([e[1] for e in events] == [["L", 112+p] for p in range(112)],
             "backward port order")
        need([route(packet, e) for e in events] == routes[stage],
             "forward/backward route binding")
    return R, routes


def dot(left, right):
    return sum(x*y for x, y in zip(left, right))


def check_grams(R):
    for ports, scale in ((U, 48), (A, 4), (T, 4)):
        matrix = [[sum(R[i][p]*R[j][p] for p in ports)
                   for j in range(8)] for i in range(8)]
        need(matrix == [[scale*int(i == j) for j in range(8)]
                        for i in range(8)], "query Gram")
    need([sum(R[i][p]**2 for i in range(8)) for p in U] == [4]*96,
         "ordinary column norms")


def check_swap_charts(routes):
    """A separate certificate: chart swaps and disjoint external axes."""
    charts = []
    for p in U:
        chart = tuple(routes[1][p][9+i] for i in range(8))
        need(all(0 < c < 512 for c in chart), "nine-axis chart")
        need(all((x & y).bit_count() % 2 == int(i == j)
                 for i, x in enumerate(chart) for j, y in enumerate(chart)),
             "orthonormal chart")
        for stage, start in ((1, 9), (2, 17)):
            need(tuple(routes[stage][p][start+i] for i in range(8)) == chart,
                 "common stage chart")
            normals = tuple(chart[i] ^ (1 << (start+i)) for i in range(8))
            rebuilt = []
            for axis in range(25):
                x, out = 1 << axis, 1 << axis
                for n in normals:
                    if (x & n).bit_count() % 2:
                        out ^= n
                rebuilt.append(out)
            need(tuple(rebuilt) == routes[stage][p], "literal chart swap")
            need(compose(routes[stage][p], routes[stage][p]) == IDENTITY,
                 "route involution")
        charts.append(chart)
    need(len(set(charts)) == 96, "distinct ordinary charts")
    return len(set(charts))
