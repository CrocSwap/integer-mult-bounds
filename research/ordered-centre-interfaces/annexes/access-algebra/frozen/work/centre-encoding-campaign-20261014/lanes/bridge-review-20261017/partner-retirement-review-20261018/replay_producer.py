"""Reproduce the frozen local theorem receipt without changing its files."""

from hashlib import sha256
import json
from pathlib import Path
import runpy
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "controller-followthrough-20261017/partner-retirement-20261018"
FREEZE = "ee4c11882ab042f3101b8ccc21e33cfae0348e48af77dcd1667757b94c403af6"


def main():
    if sha256((SOURCE/"FREEZE.json").read_bytes()).hexdigest() != FREEZE:
        raise ValueError("Frozen theorem pin")
    pins = json.loads((SOURCE/"FREEZE.json").read_text())["files"]
    before = {name:(SOURCE/name).read_bytes() for name in pins}
    for name, raw in before.items():
        if sha256(raw).hexdigest() != pins[name]:
            raise ValueError("Frozen producer artifact: " + name)
    output = {}

    def write_text(path, text, *args, **kwargs):
        if path != SOURCE/"PARTNER-RETIREMENT.json":
            raise ValueError("Unexpected producer output")
        output[path.name] = text.encode()
        return len(text)

    with patch.object(Path, "write_text", write_text):
        runpy.run_path(str(SOURCE/"check_partner_retirement.py"), run_name="__main__")
    if output != {"PARTNER-RETIREMENT.json":before["PARTNER-RETIREMENT.json"]}:
        raise ValueError("Producer receipt is not byte-identical")
    if any((SOURCE/name).read_bytes() != raw for name, raw in before.items()):
        raise ValueError("A frozen producer file changed")
    receipt = {
        "status":"PASS_UNCHANGED_PRODUCER_REPLAY",
        "producer_freeze_sha256":FREEZE,
        "identical_receipt_sha256":sha256(output["PARTNER-RETIREMENT.json"]).hexdigest(),
        "replay_checker_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "frozen_source_bytes_preserved":True,
    }
    (HERE/"PRODUCER-REPLAY.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
