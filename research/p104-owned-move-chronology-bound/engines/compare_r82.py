"""Reconcile every R82 cut and individual blocker across both engines."""

from hashlib import sha256
from json import dumps, loads
from pathlib import Path
import sys

PINS = {
    "lead/RESULT.json": "664c3824078877c6b9e6ace20d8b03202a250e67e0f09b66a7304ce1ab8a5d00",
    "independent/RESULT.json": "46ca45e212115320ab20c3c252d980ece539900d452cb223dd8caa68864662a3",
}


def verify(root, name):
    raw = (root / name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name], name

    def unique(pairs):
        d = dict(pairs)
        assert len(d) == len(pairs)
        return d

    return loads(raw, object_pairs_hook=unique)


def main():
    assert __debug__
    root = Path(sys.argv[1])
    lead = verify(root, "lead/RESULT.json")
    reverse = verify(root, "independent/RESULT.json")
    assert lead["status"] == "EXHAUSTED" and reverse["complete"]
    assert not lead["survivors"] and not reverse["survivors"]
    assert not lead["unvisited"] and not reverse["unvisited"]
    assert reverse["unvisited_literal_interval"] is None
    for field in ("head", "price_sha256", "word_sha256"):
        assert lead[field] == reverse[field]
    forward = {tuple(row["key"]): row for row in lead["decisions"]}
    assert len(forward) == len(lead["decisions"]) == reverse["visited_cuts"] == 51
    matched = []
    for placement in reverse["placements"]:
        for cut in placement["cuts"]:
            key = tuple(placement["key"] + [cut["cut"]])
            f = forward.pop(key)
            assert f["decision"] == "excluded" and cut["status"] != "survivor"
            assert f["peer"] == placement["peer"] and f["required_chart"] == placement["required_chart"]
            assert f["actual_peer_chart"] == cut["peer_chart"]
            life = placement["peer_lifetime"]
            expected_lifetime = (None if not cut["same_peer_lifetime"] else -1 if life == "public" else life[0])
            assert f["peer_lifetime"] == expected_lifetime
            assert f["original_add"][0] == placement["add_clock"]
            assert [[x[0], x[1]] for x in f["crossed_incident_barriers"]] == [
                [x[0], x[3]] for x in cut["crossed_blockers"]
            ]
            failures = []
            if not cut["cochart"]:
                failures.append("counterpart chart")
            if not cut["same_peer_lifetime"]:
                failures.append("changed lifetime")
            if cut["crossed_blockers"]:
                failures.append("crossed incident barrier")
            assert failures == f["failures"]
            matched.append({"key": key, "peer_chart": cut["peer_chart"],
                            "peer_lifetime": expected_lifetime, "failures": failures})
    assert not forward
    failure_counts = {reason: sum(reason in row["failures"] for row in matched) for reason in (
        "counterpart chart", "changed lifetime", "crossed incident barrier"
    )}
    assert failure_counts == {"counterpart chart": 51, "changed lifetime": 4, "crossed incident barrier": 10}
    print(dumps({"input_sha256": PINS, "matched": matched, "failure_counts": failure_counts,
                 "survivors": 0, "unresolved": 0, "compatible_price": "0"},
                sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
