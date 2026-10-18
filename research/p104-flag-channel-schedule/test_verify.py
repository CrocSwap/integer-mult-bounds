#!/usr/bin/env python3
"""The schedule comparison, without the channel file."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_flag_channel_schedule", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    program = [
        ["add", "Y34", "Q1", "1/4", []],
        ["transport", "X0", [232], [8], 4],
    ]
    first, _last, joint = verify.schedule(program)
    if not first["Y34"] < first["X0"] or joint != 0:
        raise SystemExit("the sample schedule changed")
    if verify.coefficients(program, "X0") != [] or verify.coefficients(program, "Y34") != ["1/4"]:
        raise SystemExit("coefficient reading changed")
    print("PASS_P104_FLAG_CHANNEL_SCHEDULE_TESTS groups=2")


if __name__ == "__main__":
    main()
