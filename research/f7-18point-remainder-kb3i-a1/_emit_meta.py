"""Emit the drawn catalogue card verbatim and the provenance blob pins at the
base commit, so TASK.json original_card equals the pinned card object exactly
and SOURCES.json provenance rows bind through the base-commit git blobs."""

import hashlib
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = "d8e0f83f00191df62174b641e9fff055c357f641"
CAT = "docs/research/agent-task-catalog.json"
SEL = "certificates/selected-result.json"


def git_blob_sha(path):
    return subprocess.run(["git", "rev-parse", BASE + ":" + path],
                          capture_output=True, check=True).stdout.decode().strip()


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    catalog = json.load(open(CAT, encoding="utf-8"))
    wanted = "bit-new-register-model"
    cards = [t for tr in catalog["tracks"] for t in tr["tasks"] if t["id"] == wanted]
    assert len(cards) == 1, ("card count", len(cards))
    card = cards[0]
    with open("research/f7-18point-remainder-kb3i-a1/_card.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(card, f, indent=2, ensure_ascii=False)
    print("CARD id=%s track-scope-key=%s" % (card["id"], card.get("scope_key")))
    rows = []
    for p in (CAT, SEL):
        rows.append({"path": p, "git_blob": git_blob_sha(p), "sha256": sha256_file(p),
                     "usage": "provenance"})
    print("PROVENANCE_ROWS=" + json.dumps(rows))
    print("BASE=" + BASE)


if __name__ == "__main__":
    main()
