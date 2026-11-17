"""Build one candidate from the pinned #7610 edit list and #7605 word."""
import argparse
from gzip import compress, decompress
from hashlib import sha256
import json
from pathlib import Path
import signal

SOURCE_PIN = "37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d"
CANONICAL_PIN = "e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd"
EDITS_PIN = "a49e9962e32d13fd91cd8715d888bb1f4305003e63dd25485aa413905e00b8d9"


def digest(data):
    return sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--peer-edits", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    signal.alarm(30)
    source, edits = args.source.read_bytes(), args.peer_edits.read_bytes()
    assert digest(source) == SOURCE_PIN and digest(edits) == EDITS_PIN
    raw = decompress(source)
    assert digest(raw) == CANONICAL_PIN
    word, plan = json.loads(raw), json.loads(edits)
    tape = word["program"]
    assert len(tape) - plan["base_events"] == 5
    assert not plan["append"]
    deletes, inserts = dict(plan["delete"]), dict(plan["insert_before"])
    assert sorted(deletes) == [45367, 45368, 45370, 47953]
    assert sorted(inserts) == [0, 45372, 47953]
    for old, event in deletes.items():
        assert tape[old + 5] == event
    assert tape[45377] == ["ADD", 818, 1456, "1", 245]
    assert tape[47959] == ["ADD", 1019, 46, "1", 127]
    adjusted_inserts = {k + 5 if k else 0: v for k, v in inserts.items()}
    removed = {k + 5 for k in deletes}
    word["program"] = [
        operation for clock, original in enumerate(tape)
        for operation in adjusted_inserts.get(clock, []) + ([original] if clock not in removed else [])
    ]
    candidate = canonical(word)
    payload = compress(candidate, mtime=0)
    args.output.write_bytes(payload)
    print(json.dumps({"status": "LITERAL_CANDIDATE_EMITTED_VERIFICATION_PENDING",
                      "word_gzip_sha256": digest(payload), "word_canonical_sha256": digest(candidate),
                      "source_word_gzip_sha256": SOURCE_PIN, "source_word_canonical_sha256": CANONICAL_PIN,
                      "peer_edits_sha256": EDITS_PIN, "old_event_count": len(tape),
                      "new_event_count": len(word["program"])}, sort_keys=True))
    signal.alarm(0)


if __name__ == "__main__":
    main()
