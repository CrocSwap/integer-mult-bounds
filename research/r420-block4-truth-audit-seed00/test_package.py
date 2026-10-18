"""Small controls for the independent Boolean replay primitives."""

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("seed00_independent_test", HERE / "independent.py")
if spec is None or spec.loader is None:
    raise RuntimeError("could not load independent.py")
independent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(independent)


def main():
    two_wire_xor = [(0, 1)]
    rows = independent.linear_rows(two_wire_xor, 2)
    receipt = independent.truth_table(two_wire_xor, [0, 1], rows, 2)
    independent.need(rows == [3, 2], "small XOR matrix")
    independent.need(receipt["checked_inputs"] == 4 and receipt["first_mismatch"] is None,
                     "all four two-bit inputs")
    omitted = independent.truth_table([], [0, 1], rows, 2)
    reversed_gate = independent.truth_table([(1, 0)], [0, 1], rows, 2)
    independent.need(omitted["first_mismatch"] is not None, "omission rejected")
    independent.need(reversed_gate["first_mismatch"] is not None, "direction mutation rejected")
    independent.need(independent.positive_cost(two_wire_xor, 2) == 3,
                     "forward/reverse positive-norm peak")
    print("PASS_BOOLEAN_REPLAY_CONTROLS inputs=4 omitted=rejected reversed=rejected")


if __name__ == "__main__":
    main()
