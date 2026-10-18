#!/usr/bin/env python3
"""Structural controls for the depth-zero weight arm. No coefficient execution."""

import importlib.util
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("odd_prime_unit_root", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


GOOD = """
def weight(self, index):
    if level.zero():
        self.values.push(self.root_unit)
        continue
    if reverse:
        self.step(level)
"""

REVERSE = """
def weight(self, index):
    if level.zero():
        reverse
        self.values.push(self.root_unit)
        continue
    if reverse:
        pass
"""

FALLTHROUGH = """
def weight(self, index):
    if level.zero():
        self.values.push(self.root_unit)
    if reverse:
        pass
"""

EXTRA = """
def weight(self, index, rows):
    if level.zero():
        self.values.push(self.root_unit)
        continue
    if reverse:
        pass
"""


def expect_failure(source, label):
    try:
        verify.zero_level_facts(source)
    except SystemExit as error:
        if label not in str(error):
            raise SystemExit("wrong rejection for " + label + ": " + str(error))
        return
    raise SystemExit("accepted a depth-zero arm that should fail: " + label)


def main():
    facts = verify.zero_level_facts(GOOD)
    if facts != {"arguments": ["self", "index"], "returns": "root_unit", "reverse_unreachable": True}:
        raise SystemExit("good arm receipt changed")
    expect_failure(REVERSE, "reads reverse")
    expect_failure(FALLTHROUGH, "falls through")
    expect_failure(EXTRA, "row or depth argument")
    with tarfile.open(verify.ARCHIVE, "r:") as tar:
        controller = tar.extractfile(verify.CONTROLLER).read()
    pinned = verify.zero_level_facts(controller)
    if pinned["arguments"] != ["self", "index"] or not pinned["reverse_unreachable"]:
        raise SystemExit("pinned controller arm changed")
    print("PASS_SELECTED_ODD_PRIME_UNIT_ROOT_TESTS groups=4")


if __name__ == "__main__":
    main()
