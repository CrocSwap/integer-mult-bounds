"""Exact raw selected-source PAID/MOVE bindings, compiled before runtime.

No nested product/remap token is silently substituted. Prepared for
@CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from functools import lru_cache
import gzip
from hashlib import sha256
import json
from all_leaf_sources import activate, need

S = activate()


@lru_cache(maxsize=1)
def catalog():
    raw = (S.selected/"WORD.json.gz").read_bytes()
    word = json.loads(gzip.decompress(raw))
    events, stats = S.ir.current_local(word)
    entries = {}
    for i, event in enumerate(events):
        if event.op != "PAID":
            continue
        token = event.token
        need(len(token) == 3 and token[0] == "local" and token[2][0] == "MOVE",
             "every raw selected paid event is an actual MOVE child")
        pc, original = token[1:]
        need(tuple(word["program"][pc]) == original and len(event.fields) == 1,
             "exact selected source operand")
        left, right = events[i-1], events[i+1]
        need(left.op == right.op == "SERVICE" and left.fields == right.fields == event.fields
             and left.token == ("move-in",)+token and right.token == ("move-out",)+token,
             "complete consecutive source triple")
        need(1 <= event.rank <= 8 and pc not in entries, "positive selected rank and unique source index")
        entries[pc] = (left, event, right)
    moves = {i for i, row in enumerate(word["program"]) if row[0] == "MOVE"}
    need(set(entries) == moves and len(entries) == 3453, "all selected raw MOVE/PAID occurrences")
    pairs = sorted({tuple(word["program"][pc][2:4]) for pc in entries})
    need(len(pairs) == 2886, "complete selected directed chart family")
    report = dict(raw_moves=len(entries), distinct_chart_pairs=len(pairs),
                  word_gzip_sha256=sha256(raw).hexdigest(),
                  source_program_events=len(word["program"]),
                  paid_rank_occurrences=dict(sorted(Counter(t[1].rank for t in entries.values()).items())),
                  raw_source_only=True, product_or_nested_caller_claim=False)
    return word, entries, pairs, report


@lru_cache(maxsize=None)
def frame(index):
    return S.clifford.canonical_frame(9, tuple(catalog()[0]["frames"][index]))


@lru_cache(maxsize=None)
def inverse_frame(index):
    return frame(index).adjoint()


@lru_cache(maxsize=None)
def chart(start, stop):
    op = inverse_frame(start).then(frame(stop))
    record, _compiled = S.clifford.lower_child(op)
    word = catalog()[0]
    rank = abs(len(word["frames"][stop])-len(word["frames"][start]))
    need(record["rank"] == rank and 1 <= rank <= 8,
         "actual Clifford rank equals the retained source paid rank")
    return op, record


def bind_paid(event):
    token = event.token
    need(type(token) is tuple and len(token) == 3 and token[0] == "local"
         and type(token[1]) is int, "exact raw current_local token shape")
    word, entries, _pairs, _report = catalog()
    need(token[1] in entries, "actual selected raw paid source index")
    triple = entries[token[1]]
    need(S.core.same_event(event, triple[1]), "typed paid owner/rank/source record")
    raw = word["program"][token[1]]
    op, record = chart(raw[2], raw[3])
    return triple, op, record


def bind_move(triple):
    need(len(triple) == 3, "complete source MOVE triple")
    actual, op, record = bind_paid(triple[1])
    need(all(S.core.same_event(a, b) for a, b in zip(triple, actual)),
         "exact source entrance/child/exit chronology")
    return actual, op, record
