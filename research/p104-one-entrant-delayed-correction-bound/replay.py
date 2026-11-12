"""Replay the delayed-cut exclusions using only the registered package."""
from gzip import decompress
from hashlib import sha256
from json import loads
from pathlib import Path
from shutil import copyfile
from subprocess import run
from sys import executable
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    "R206": "a5ad6b1d6a0aeb376ca9b945de03f44e40fb177225133b0fdd3a6466313b2fa3",
    "R207-independent": "1c2193b302e6ec8e26d755c03e6c7e462cd3fb44af9d73dad438834a0a900ac6",
    "R207-lead": "f2af3d476dd24e49653b7bff45276d308a3067aa2bfc86cdef7c24bcff79d2a3",
    "augmented": "125ee63c390ec7a62bce9d14181bd4b66cfc0fcd89e1d48ef396cc7a93ec3ef2",
    "alternate": "72d244dc76debc2fd46f1b8d1c205a4b1179daa3d2c2bd463d2177b1d0544dbd",
}


def digest(raw):
    return sha256(raw).hexdigest()


def checked_inputs():
    pins = {}
    for line in (ROOT / "PINS.txt").read_text().splitlines():
        value, name = line.split()
        assert name not in pins and digest((ROOT / name).read_bytes()) == value, name
        pins[name] = value
    assert set(pins) == {
        file.relative_to(ROOT).as_posix()
        for path in ("engines", "inputs")
        for file in (ROOT / path).iterdir()
        if file.is_file()
    }


def materialize(work, files):
    (work / "inputs").mkdir(parents=True)
    for src, dst in files:
        copyfile(ROOT / src, work / dst)


def replay(work, program, label, timeout):
    proc = run([executable, "-I", "-B", str(work / program)], check=True,
               capture_output=True, timeout=timeout)
    assert not proc.stderr and digest(proc.stdout) == EXPECTED[label], (label, digest(proc.stdout))
    return proc.stdout


def main():
    assert __debug__
    checked_inputs()
    common = [(f"inputs/{name}", f"inputs/{name}")
              for name in ("7334-WORD.json.gz", "R204.json")]
    with TemporaryDirectory(prefix="p104-delayed-") as path:
        ind, lead = Path(path) / "independent", Path(path) / "lead"
        materialize(ind, common + [
            ("inputs/R200.json", "inputs/R200.json"),
            ("inputs/STAGE2.json", "inputs/STAGE2.json"),
            ("inputs/R203-INDEPENDENT.json", "inputs/R203.json"),
            ("engines/engine206.py", "engine206.py"),
            ("engines/independent207.py", "independent207.py"),
        ])
        stage1 = decompress((ROOT / "inputs/STAGE1.json.gz").read_bytes())
        (ind / "inputs/STAGE1.json").write_bytes(stage1)
        r206 = replay(ind, "engine206.py", "R206", 65)
        (ind / "inputs/R206.json").write_bytes(r206)
        r207 = loads(replay(ind, "independent207.py", "R207-independent", 55))
        materialize(lead, common + [
            ("inputs/R203-LEAD.json", "inputs/R203.json"),
            ("engines/LEAD-PINS.txt", "PINS"),
            ("engines/lead207.py", "lead207.py"),
            ("engines/bank_gate.py", "bank_gate.py"),
            ("engines/peel.py", "peel.py"),
            ("engines/augmented.py", "augmented.py"),
            ("engines/alternate.py", "alternate.py"),
        ])
        (lead / "inputs/R206.json").write_bytes(r206)
        replay(lead, "lead207.py", "R207-lead", 25)
        rank = loads(replay(lead, "augmented.py", "augmented", 35))
        replay(lead, "alternate.py", "alternate", 10)
        selected = r207["span"]["clocks"]
        assert rank["clocks"] == selected and rank["rank"] == 203
        assert not r207["span"]["result"]["span"]
        assert [key for key in r207["pre_span_unresolved"] if key != selected] == [
            [41805, 41807, 43313], [41944, 41946, 43419],
            [40430, 40432, 46222], [43091, 43093, 46566],
        ]
        # Corrupt the actual frozen R206 receipt, then demand explicit pin rejection.
        (ind / "inputs/R206.json").write_bytes(r206.replace(b'"cut":', b'"mutated_cut":', 1))
        rejected = run([executable, "-I", "-B", str(ind / "independent207.py")],
                       capture_output=True, timeout=5)
        assert rejected.returncode and b"AssertionError: inputs/R206.json" in rejected.stderr
    print("PASS_DELAYED_BANK: 119 surveyed, 115 exact exclusions, 4 unresolved")


if __name__ == "__main__":
    main()
