"""Check PR210's stream rewrite without importing its transformer.

The comparison retains the exact ordered non-MOVE operations, and compares
each stream's projected trace after telescoping adjacent moves. Disjoint
streams may commute. Only even *payload ADDs* are discarded.
Ross Richardson, with substantial OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter
import gzip
import hashlib
from pathlib import Path
import struct


ROW = struct.Struct("=6i")
TOKEN = struct.Struct("=7i")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_records(path):
    data = gzip.decompress(Path(path).read_bytes())
    require(len(data) % ROW.size == 0, "truncated physical record")
    return data


def trace(data, *, discard_even=False, omit_record=None):
    require(len(data) % ROW.size == 0, "truncated physical record")
    streams = {}
    pending = {}
    gates = hashlib.sha256()
    paid = Counter()
    coefficients = Counter()
    removed = Counter()
    chains = []
    gate_count = 0
    copy = None
    copies = 0

    def emit(stream, token):
        # Keep complete traces for exact equality. Hashes below are receipts,
        # not the acceptance criterion for the mathematical comparison.
        streams.setdefault(stream, bytearray()).extend(TOKEN.pack(*token))

    def boundary(stream):
        if stream not in pending:
            return
        old, new, rank, count, first, last = pending.pop(stream)
        emit(stream, (-1, old, new, rank, 0, 0, 0))
        if count > 1:
            chains.append(dict(stream=stream, old=old, new=new, rank=rank,
                               moves=count, first=first, last=last))

    for index, row in enumerate(ROW.iter_unpack(data)):
        if index == omit_record:
            continue
        op, a, b, c, f, z = row
        require(op in (0, 1, 2, 3), "unknown physical opcode")
        require(0 <= a <= 20107, "invalid stream")
        if op == 1 and c % 2 == 0 and discard_even:
            removed[c] += 1
            continue
        if op == 0:
            require(z == 0 and f >= 0, "invalid MOVE rank or padding")
            if f:
                paid[f] += 1
            if a in pending:
                old, previous, rank, count, first, _ = pending[a]
                require(previous == b, "disconnected same-stream MOVE chain")
                pending[a] = (old, c, rank + f, count + 1, first, index)
            else:
                pending[a] = (b, c, f, 1, index, index)
            continue
        require(0 <= b <= 20107 and a != b, "invalid gate operands")
        boundary(a)
        boundary(b)
        if op == 1:
            require(b != 20107 or copy is not None, "read outside COPY lifetime")
            coefficients[c] += 1
        elif op == 2:
            require(copy is None and b == 20107 and z > 0, "invalid COPY lifetime")
            copy = (a, b, c)
            copies += 1
            paid[z] += 1
        else:
            require(copy == (a, b, c), "ERASE does not match COPY")
            copy = None
        # The ordinal detects moving a stream operation across a retained use.
        token = (gate_count, *row)
        emit(a, token)
        emit(b, token)
        gates.update(ROW.pack(*row))
        gate_count += 1
    require(copy is None, "unterminated COPY")
    for stream in sorted(pending):
        boundary(stream)
    return dict(streams=dict(sorted(streams.items())),
                gates_sha256=gates.hexdigest(), retained_gates=gate_count,
                paid_histogram=dict(sorted(paid.items())),
                paid_calls=sum(paid.values()),
                rank_mass=sum(r * n for r, n in paid.items()),
                coefficients=dict(sorted(coefficients.items())),
                removed_even_additions=sum(removed.values()), copies=copies,
                fused_chains=sorted(chains, key=lambda x: x["stream"]))


def equivalent(before, after):
    for key in ("gates_sha256", "retained_gates", "streams", "coefficients", "copies"):
        require(before[key] == after[key], "stream rewrite differs: " + key)


def audit(directory):
    directory = Path(directory)
    old = read_records(directory / "producer-bit/records.bin.gz")
    new = read_records(directory / "records.bin.gz")
    before = trace(old, discard_even=True)
    after = trace(new)
    equivalent(before, after)
    delta = Counter(after["paid_histogram"])
    delta.subtract(before["paid_histogram"])
    delta = {r: n for r, n in sorted(delta.items()) if n}
    require(delta == {8: -3, 12: -3, 20: 3}, "wrong local paid delta")
    require(before["rank_mass"] == after["rank_mass"] == 434502, "rank mass changed")
    require(before["removed_even_additions"] == 1783196, "wrong even ADD count")
    require(sum(after["coefficients"].values()) == 786621, "wrong retained ADD count")
    require(before["copies"] == after["copies"] == 24, "COPY episodes changed")
    require([c["stream"] for c in before["fused_chains"]] == [2627, 2628, 2631],
            "unexpected fusion streams")
    require(not after["fused_chains"], "candidate leaves consecutive MOVEs")
    # A real-word corruption, separate from the predecessor's controls.
    omitted = next(i for i, row in enumerate(ROW.iter_unpack(new)) if row[0] == 1)
    try:
        equivalent(before, trace(new, omit_record=omitted))
    except ValueError:
        pass
    else:
        raise ValueError("omitted real odd ADD was accepted")
    digest = hashlib.sha256()
    for stream, value in after["streams"].items():
        digest.update(f"{stream}:{hashlib.sha256(value).hexdigest()}\n".encode("ascii"))
    return dict(status="PASS_INDEPENDENT_STREAM_RECONCILIATION",
                producer_records=len(old) // ROW.size, emitted_records=len(new) // ROW.size,
                projected_streams=len(after["streams"]),
                stream_trace_sha256=digest.hexdigest(),
                retained_nonmove_sha256=after["gates_sha256"],
                removed_even_additions=before["removed_even_additions"],
                retained_additions=sum(after["coefficients"].values()),
                copied_center_episodes=after["copies"], rank_mass=after["rank_mass"],
                local_histogram_delta=delta, fused_chains=before["fused_chains"],
                real_word_control={"omitted_odd_add_record": omitted, "rejected": True},
                scope="Exact signed non-MOVE sequence and per-stream telescoped trace equality; "
                      "uses fresh native replay for geometric admission and full construction checks.")
