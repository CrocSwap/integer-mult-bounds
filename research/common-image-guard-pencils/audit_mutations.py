"""Run real private-copy changes through the same semantic control entry point."""
import json
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
FAULTS = [
    ("laws.py", "(q + 1 - k)", "(q + 2 - k)", "five-direction anchor"),
    ("laws.py", "(b**d - a**d)", "b**d", "five-direction anchor"),
    ("laws.py", "(q - 1) * a**(m - 1)", "a**(m - 1)", "five-direction anchor"),
    ("laws.py", "(-1)**i * comb(k - j, i)", "comb(k - j, i)", "five-direction mask spectrum"),
    ("laws.py", "3*b2**d", "2*b2**d", "independent ternary triple"),
    ("dependency.py", "(-1)**c * q**", "q**", "independent ternary triple"),
    ("dependency.py", "q**(c*(c - 1)//2)", "1", "independent ternary triple"),
    ("dependency.py", "all(field.dot(row, x) != 0", "any(field.dot(row, x) != 0", "independent ternary triple"),
    ("dependency.py", "q**dim + (q - 1)*support", "q**dim + support", "independent ternary triple"),
    ("dependency.py", "field.dot(row, y) != 1", "field.dot(row, y) != 0", "prefix rank and final coordinate"),
    ("dependency.py", "(q - 1)*sum(n", "sum(n", "prefix rank and final coordinate"),
    ("dependency.py", "if len(span) == r - 1", "if len(span) <= r - 1", "prefix rank and final coordinate"),
    ("windows.py", "after - 1], ties=ties", "after], ties=ties", "q4 triple boundary"),
    ("headers.py", "for n in range(1, m)", "for n in range(1, m + 1)", "literal five-direction matrix guard"),
    ("headers.py", "field.neg[row[j]] if i == 0", "row[j] if i == 0", "literal five-direction matrix guard"),
    ("headers.py", "strata[det][mask] += 1", "strata[1][mask] += 1", "determinant-conditioned histogram"),
    ("source/6701-PROOF.md", "Binary common-image full-guard family", "Changed common-image full-guard family", "source bytes or Git blob"),
    ("triples.py", "(q - 2)*(along_line - n)", "0*(along_line - n)", "affine box triple anchor"),
    ("laws.py", "**(2*(d - j))", "**(d - j)", "full affine flat anchor"),
    ("laws.py", "q*a**mid <= b**mid", "a**mid <= b**mid", "ternary dense-size anchor"),
    ("ternary.py", "4*Fraction(17, 35)**4", "5*Fraction(17, 35)**4", "ternary tail threshold"),
]


def invoke(root, optimized, expected):
    args = [sys.executable, "-I", *(["-O"] if optimized else []), "-W", "error", "-B",
            str(root/"verify.py"), "--controls"]
    proc = subprocess.run(args, cwd=root, text=True, encoding="utf8", capture_output=True, timeout=30)
    if expected is None:
        if proc.returncode or json.loads(proc.stdout)["status"] != "PASS_PENCIL_SEMANTIC_CONTROLS":
            raise ValueError("unmodified private-copy control: " + proc.stderr[-300:])
    elif not proc.returncode or ("ValueError: " + expected) not in proc.stderr:
        raise ValueError(f"wrong rejection for {expected}: exit={proc.returncode} {proc.stderr[-300:]}")


def main():
    with TemporaryDirectory(prefix="guard-pencil-faults-") as tmp:
        root = Path(tmp)/"package"
        shutil.copytree(HERE, root, copy_function=shutil.copyfile,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for optimized in (False, True):
            invoke(root, optimized, None)
        for name, before, after, message in FAULTS:
            file = root/name
            original = file.read_bytes()
            if original.count(before.encode()) != 1:
                raise ValueError("fault site not unique: " + before)
            file.write_bytes(original.replace(before.encode(), after.encode()))
            for optimized in (False, True):
                invoke(root, optimized, message)
            file.write_bytes(original)
        for optimized in (False, True):
            invoke(root, optimized, None)
    print(json.dumps(dict(status="PASS_GUARD_PENCIL_MUTATIONS", fault_sites=len(FAULTS),
                          rejected_probes=2*len(FAULTS), positive_controls=4)))


if __name__ == "__main__":
    main()
