"""Read the full emitted batch and test its absolute port actions on two characters."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import inputs, read, receipt
from mixed_application import verify_expansion
from full_batch_probe import verify as finite_probe


def verify():
    caller = read("data/CALLER.json.gz")
    _, layout, *_ = inputs()
    return dict(expansion=verify_expansion(caller, layout, read("PRICE.json")["calls"]),
                characters=finite_probe(caller, layout, read("data/CALLER-PHASE-BASES.json")))


if __name__ == "__main__":
    result = verify()
    receipt("batch", result)
    print("PASS_FULL_BATCH", result["expansion"]["emitted_events"])
