"""Run the frozen rank checker and compare outputs without changing them."""

from hashlib import sha256
import json
from pathlib import Path
import runpy
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "history-encoding/terminal-line-fusion-20261018"
FREEZE = "15621e9a16d7390fb6073ad79d97dc7b09237263fb7d5c7be399047877590f08"


def main():
    freeze = SOURCE / "FROZEN.json"
    if sha256(freeze.read_bytes()).hexdigest() != FREEZE:
        raise ValueError("Producer freeze pin")
    pins = json.loads(freeze.read_text())["files"]
    before = {name: (SOURCE/name).read_bytes() for name in pins}
    for name, raw in before.items():
        if sha256(raw).hexdigest() != pins[name]:
            raise ValueError("Source pin: " + name)
    wanted = {"PURE-CYCLE-RANK-DATA.json", "PURE-CYCLE-RANK.json"}
    captured = {}

    def write_bytes(path, raw):
        if path.parent != SOURCE or path.name not in wanted:
            raise ValueError("Unexpected output: " + str(path))
        captured[path.name] = raw
        return len(raw)

    def write_text(path, text, *args, **kwargs):
        return write_bytes(path, text.encode())

    with patch.object(Path, "write_bytes", write_bytes), patch.object(Path, "write_text", write_text):
        runpy.run_path(str(SOURCE / "check_pure_cycle_rank.py"), run_name="__main__")
    if set(captured) != wanted:
        raise ValueError("Producer output coverage")
    for name in pins:
        if (SOURCE/name).read_bytes() != before[name]:
            raise ValueError("Frozen source changed: " + name)
    for name, raw in captured.items():
        if raw != before[name]:
            raise ValueError("Producer reproduction mismatch: " + name)
    receipt = {
        "status": "PASS_UNCHANGED_PRODUCER_REPLAY",
        "producer_freeze_sha256": FREEZE,
        "replay_checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "identical_outputs": {name: sha256(raw).hexdigest() for name, raw in sorted(captured.items())},
        "frozen_source_bytes_preserved": True,
    }
    (HERE/"PRODUCER-REPLAY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
