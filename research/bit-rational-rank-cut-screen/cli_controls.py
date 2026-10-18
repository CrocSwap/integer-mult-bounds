"""Exercise the actual CLI in disposable copies, including failed receipts."""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent


def run(script, arguments, expected):
    result = subprocess.run(
        [sys.executable, "-I", "-O", "-B", str(script), *arguments],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode != expected or "Traceback" in result.stderr:
        raise ValueError((arguments, result.returncode, result.stdout, result.stderr))
    return result


def input_controls(script, temporary):
    fixtures = [
        (
            "pass",
            '{"address_dimension":1,"paid_frames":[[[1]],[[1]]],'
            '"target_frames":[[[3]]]}',
            0,
        ),
        (
            "type",
            '{"address_dimension":1,"paid_frames":[[[true]]],"target_frames":[[[1]]]}',
            2,
        ),
        ("nested", "[" * 2000 + "0" + "]" * 2000, 2),
        ("oversize", " " * 65537, 2),
        ("duplicate", '{"address_dimension":1,"address_dimension":2}', 2),
    ]
    for name, content, expected in fixtures:
        path = temporary / f"{name}.json"
        path.write_text(content, encoding="utf-8")
        result = run(script, ["--input", str(path)], expected)
        if (
            expected == 0
            and json.loads(result.stdout)["status"] != "PASS_NECESSARY_CUTS_ONLY"
        ):
            raise ValueError("passing screen overclaimed")
    run(script, ["--input", str(temporary / "missing.json")], 2)
    return len(fixtures) + 1


def main():
    with TemporaryDirectory() as directory:
        temporary = Path(directory)
        for name in ("verify.py", "EXAMPLE.json", "RESULT.json"):
            shutil.copyfile(HERE / name, temporary / name)
        script = temporary / "verify.py"
        receipt = temporary / "RESULT.json"
        original = receipt.read_bytes()
        run(script, [], 0)
        rejected = run(script, ["--input", str(temporary / "EXAMPLE.json")], 1)
        witness = json.loads(rejected.stdout)["witness"]
        if [witness["paid_nonzero"], witness["target_nonzero"]] != [2, 3]:
            raise ValueError("wrong CLI witness")
        count = input_controls(script, temporary)
        run(script, ["--write", "--input", str(temporary / "EXAMPLE.json")], 2)
        if receipt.read_bytes() != original:
            raise ValueError("read-only CLI changed receipt")
        for mutant in (False, 0.0):
            value = json.loads(original)
            value["direct_word"]["minimum_margin"] = mutant
            receipt.write_text(json.dumps(value), encoding="utf-8")
            result = run(script, [], 2)
            if "receipt mismatch" not in result.stderr:
                raise ValueError("type mutation failed for the wrong reason")
        print(f"PASS_RANK_CUT_CLI inputs={count} receipt_mutants=2 exit_codes=0,1,2")


if __name__ == "__main__":
    main()
