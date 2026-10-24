#!/usr/bin/env python3
"""Compare pinned concurrent receipts without executing their proof engines.

Prepared for mihir-s-05 with OpenAI Codex assistance. Apache-2.0.
"""
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def frame(basis):
    vectors = {0}
    for value in basis:
        need(type(value) is int and 0 <= value < 512, "binary coordinate")
        vectors |= {x ^ value for x in tuple(vectors)}
    return tuple(sorted(vectors))


def projection(row, start_key, old_key, profiles_key):
    profiles = tuple(sorted(tuple(sorted(p)) for p in row[profiles_key]))
    need(len(set(profiles)) == len(profiles), "no duplicate rank partitions")
    return {
        "index": row["index"], "phase": row["phase"], "roles": row["roles"],
        "coefficients": row["coefficients"],
        "starts": [frame(s) for s in row[start_key]],
        "exits": [frame(s) for s in row["exit_bases"]],
        "contacts": [frame(s) for s in row["contact_bases"]],
        "incumbent": tuple(sorted(row[old_key])), "profiles": profiles,
    }


def main():
    ours = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    expected = [projection(w, "start_bases", "incumbent_ranks", "relaxed_rank_partitions")
                for w in ours["windows"]]
    need(len(expected) == len({w["index"] for w in expected}) == 128, "our complete window census")
    comparisons = []
    for pin in json.loads((HERE / "PEERS.json").read_text(encoding="utf-8"))["receipts"]:
        archive = (HERE / pin["local"]).read_bytes()
        need(hashlib.sha256(archive).hexdigest() == pin["archive_sha256"], "committed peer archive hash")
        raw = gzip.decompress(archive)
        need(hashlib.sha256(raw).hexdigest() == pin["payload_sha256"], "peer payload hash")
        need(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == pin["git_blob"],
             "peer original Git blob")
        peer = json.loads(raw)
        keys = ("start_bases", "incumbent", "terminal_profiles") if pin["pr"] == 4581 else (
            "entrance_bases", "incumbent_profile", "relaxed_profiles")
        actual = [projection(w, *keys) for w in peer["windows"]]
        # JSON canonicalization distinguishes boolean impostors from integers.
        need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
             "all peer identities, full subspaces, incumbent bills and terminal partitions")
        comparisons.append({"pr": pin["pr"], "head": pin["head"], "windows": len(actual),
                            "partitions": sum(len(w["profiles"]) for w in actual),
                            "reported_states": peer["reachable_states"]})
    need(len(comparisons) == 2 and {x["pr"] for x in comparisons} == {4581, 4582}, "two pinned peers")
    print(json.dumps({"status": "PASS_TWO_PINNED_PEER_RECEIPTS", "comparisons": comparisons,
                      "our_states": ours["state_count"], "peer_code_executed": False}, sort_keys=True))


if __name__ == "__main__":
    main()
