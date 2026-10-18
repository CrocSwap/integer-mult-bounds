#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Combine PR2152's coalesced frames with PR2219's private-descent idea.

New successor implementation by SHIN09-git with OpenAI Codex assistance.
Predecessor scalar word, charts and the reuse mechanism retain their credit.
This module independently replays rational rows and binary-frame chronology.
"""
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json

HELPER, PRIVATE, SOURCE = 711, 738, 133
TARGETS = {148: Q(2), 203: Q(2), 159: Q(-1)}
ZERO = frozenset({0})

def require(ok, message):
    if not ok:
        raise ValueError(message)

def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def span(basis):
    result = {0}
    for x in basis:
        require(type(x) is int and 0 <= x < 512, "invalid frame vector")
        result |= {y ^ x for y in tuple(result)}
    return frozenset(result)

def dim(frame):
    n = len(frame)
    require(n > 0 and n & (n-1) == 0, "invalid subspace size")
    return n.bit_length()-1

def basis(frame):
    values, reached = [], ZERO
    for x in sorted(frame):
        if x not in reached:
            values.append(x)
            reached = span(values)
    require(reached == frame, "frame is not a binary subspace")
    return values

def add_row(target, source, coefficient):
    # Copy source entries so even a self-add has well-defined exact semantics.
    for j, x in list(source.items()):
        value = target.get(j, Q(0)) + coefficient*x
        if value:
            target[j] = value
        else:
            target.pop(j, None)

def scalar_events(built):
    return [e for e in built["scalar_operations"] if e["kind"] != "transport"]

def transform(built, fault=None):
    original = scalar_events(built)
    contacts = [dict(e) for e in original if e["kind"] == "add"
                and e["phase"] == "fanout contact" and e["registers"][1] == HELPER]
    require({e["registers"][0]: Q(e["coefficient"]) for e in contacts} == TARGETS,
            "exact three helper contacts changed")
    require(len(contacts) == 3, "duplicate helper contact")
    contacts.sort(key=lambda e: dim(span(e["frame"])), reverse=True)
    require([dim(span(e["frame"])) for e in contacts] == [7, 6, 3],
            "coalesced contact dimensions changed")
    require(span(contacts[2]["frame"]) <= span(contacts[1]["frame"]) <= span(contacts[0]["frame"]),
            "contact frames do not form a private descent")
    removed = Counter()
    removed_indices = []
    result = []
    inserted = False
    lineage = []
    for k, event in enumerate(original):
        e = dict(event)
        uses_helper = e["kind"] in ("add", "scale", "private_copy") and HELPER in e["registers"]
        if uses_helper:
            require(e["kind"] == "add", "unexpected helper operation")
            expected = {"entry compensation": 7, "fanout helper seed": 1,
                        "fanout contact": 3, "helper restoration": 1}
            require(e["phase"] in expected, "unexpected helper dependence")
            if fault == "retain_dirty_compensation" and e["phase"] == "entry compensation":
                result.append(e); lineage.append(k)
            removed[e["phase"]] += 1
            removed_indices.append(k)
            continue
        result.append(e); lineage.append(k)
        if e["kind"] == "scale" and e["registers"] == [PRIVATE]:
            require(not inserted and Q(e["coefficient"]) == Q(-1, 2),
                    "private normalization or lifetime changed")
            inserted = True
            new_contacts = list(reversed(contacts)) if fault == "ascending_private" else contacts
            for i, contact in enumerate(new_contacts):
                if fault == "omit_contact" and i == 0:
                    continue
                direct = dict(contact, registers=[contact["registers"][0], PRIVATE],
                              phase="private query serves coalesced fanout contact")
                if fault == "contact_coefficient" and i == 0:
                    direct["coefficient"] = str(Q(direct["coefficient"]) + 2)
                result.append(direct); lineage.append(None)
    require(inserted and removed == Counter({"entry compensation":7, "fanout helper seed":1,
                                            "fanout contact":3,"helper restoration":1}),
            "wrong exact deletion set")
    require(all(HELPER not in e.get("registers", []) for e in result)
            or fault == "retain_dirty_compensation", "freed helper still used")
    return result, {"removed_by_phase":dict(sorted(removed.items())),
                    "removed_scalar_indices":removed_indices,
                    "retained_scalar_indices":[i for i in lineage if i is not None],
                    "contact_frames":[{"target":e["registers"][0], "coefficient":e["coefficient"],
                                       "basis":e["frame"], "dimension":dim(span(e["frame"]))}
                                      for e in contacts]}

def replay(events, initial, final, live, *, fault=None):
    n = len(initial)
    require(n == 735 and len(final) == n, "public stock changed")
    current = [frozenset(f) for f in initial]
    final = [frozenset(f) for f in final]
    rows = [{i: Q(1)} for i in range(n)]
    private_frames, private_rows = {}, {}
    paid, private_paid = Counter(), Counter()
    edges, operations, paths = [], [], []
    active_path = None
    peak = created = 0
    discarded = []
    def transport(r, target, phase):
        nonlocal active_path
        private = r >= n
        require(not private or r in private_frames, "uninitialized private register")
        old = private_frames[r] if private else current[r]
        require(target <= old if private else old <= target,
                "private descent/public ascent violates frame inclusion")
        if not private:
            require(target <= final[r], "public operation exceeds final frame")
        rank = abs(dim(target)-dim(old))
        if rank:
            e = {"occurrence":len(edges), "register":r, "source_frame":basis(old),
                 "target_frame":basis(target), "rank":rank, "private":private, "phase":phase}
            edges.append(e)
            operations.append({"kind":"transport","occurrence":e["occurrence"],"phase":phase})
            (private_paid if private else paid)[rank] += 1
            if private:
                require(active_path is not None, "private transport outside lifetime")
                active_path.append(e)
        if private:
            private_frames[r] = target
        else:
            current[r] = target
    def row(r):
        return rows[r] if r < n else private_rows[r]
    for event in events:
        e = dict(event)
        kind, phase = e["kind"], e["phase"]
        frame = span(e["frame"])
        require(basis(frame) == e["frame"], "noncanonical event frame")
        if kind == "private_init":
            r = e["register"]
            require(type(r) is int and r >= n and r not in private_frames and active_path is None,
                    "invalid private initialization")
            if fault == "missing_private_init" and created == 0:
                created += 1
                continue
            private_frames[r], private_rows[r] = frame, {}
            active_path = []
            created += 1
            peak = max(peak, len(private_frames))
        elif kind == "private_discard":
            r = e["register"]
            require(r in private_frames, "discard without ownership")
            transport(r, frame, phase)
            paths.append(active_path)
            active_path = None
            discarded.append(r)
            del private_frames[r], private_rows[r]
        elif kind in ("add", "scale", "private_copy"):
            rr = e["registers"]
            require(len(rr) == (1 if kind == "scale" else 2), "wrong scalar arity")
            require(all(type(r) is int and 0 <= r < n+8 for r in rr), "invalid scalar register")
            for r in rr:
                transport(r, frame, phase)
            require(all((current[r] if r < n else private_frames[r]) == frame for r in rr),
                    "scalar operands differ in frame")
            coefficient = Q(e["coefficient"])
            require(bool(coefficient), "zero scalar coefficient")
            if kind == "private_copy":
                require(rr[0] >= n and rr[1] < n and not row(rr[0]),
                        "COPY needs a cleared owned register and public source")
                private_rows[rr[0]] = {i: coefficient*x for i,x in row(rr[1]).items()}
            elif kind == "scale":
                scaled = {i: coefficient*x for i,x in row(rr[0]).items()}
                if rr[0] < n: rows[rr[0]] = scaled
                else: private_rows[rr[0]] = scaled
            else:
                add_row(row(rr[0]), row(rr[1]), coefficient)
        else:
            raise ValueError("unknown event kind: "+kind)
        operations.append(e)
    for r in range(n):
        transport(r, final[r], "final public boundary")
    require(not private_frames and not private_rows and active_path is None, "private state still live")
    require(created == len(discarded) == len(paths) == 8 and peak == 1,
            "eight sequential private lifetimes required")
    for r in range(n):
        expected = {r:Q(1)}
        if r-112 in live:
            expected[r-112] = Q(1)
        require(rows[r] == expected, "exact endpoint mismatch at public register "+str(r))
    require(current == final, "wrong final frames")
    require(sum(k*v for k,v in private_paid.items()) == 56, "private COPY rank mass is not 56")
    require([e for path in paths for e in path] == [e for e in edges if e["private"]],
            "private path coverage differs from events")
    profile = lambda c:{str(k):v for k,v in sorted(c.items()) if v}
    report = {"public_registers":n, "endpoint_columns_checked":n, "live_targets":len(live),
              "exact_endpoint_identity":True, "dirty_restoration":True, "common_scalar_frames":True,
              "public_profile":profile(paid), "private_profile":profile(private_paid),
              "public_rank_mass":sum(k*v for k,v in paid.items()), "private_rank_mass":56,
              "scalar_adds":sum(e["kind"]=="add" for e in operations),
              "private_copies":created, "peak_private_copies":peak,
              "transport_occurrences":len(edges), "word_sha256":digest(operations),
              "transports_sha256":digest(edges),
              "complete_public_widths":[dim(final[r])-dim(initial[r]) for r in range(n)]}
    return {"report":report,"scalar_operations":operations,"transport_edges":edges,
            "private_paths":paths,"initial":initial,"final":final}

def native_witness(built, ports):
    edges = [dict(register=str(e["register"]), old=e["source_frame"], new=e["target_frame"],
                  occurrence=e["occurrence"], private=e["private"], rank=e["rank"])
             for e in built["transport_edges"]]
    lookup = {e["occurrence"]:e for e in edges}
    return {"transports":edges,
            "private_paths":[[lookup[e["occurrence"]] for e in p] for p in built["private_paths"]],
            "scalar_operations":built["scalar_operations"],"ports":ports,
            "scalar_operation_word_sha256":built["report"]["word_sha256"],
            "transport_occurrences_sha256":built["report"]["transports_sha256"],
            "public_profile":built["report"]["public_profile"],
            "private_profile":built["report"]["private_profile"]}
