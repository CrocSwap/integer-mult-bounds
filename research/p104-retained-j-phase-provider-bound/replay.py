"""Regenerate and authenticate the exact retained-J provider receipt."""
from hashlib import sha1, sha256
from json import loads
from pathlib import Path
from shutil import copytree
from subprocess import run
from sys import executable
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
ADMISSION = "004331cff6ca8644489d7b7084e5c67439d74a2d283e4d64a9fdb9f88679253d"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate provenance key")
    return result


def verify_provenance():
    evidence = loads((ROOT / "PROVENANCE.json").read_bytes(), object_pairs_hook=unique)
    for name, pin in evidence["files"].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError("Source pin escapes package")
        raw = path.read_bytes()
        blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if sha256(raw).hexdigest() != pin["sha256"] or blob != pin["git_blob"]:
            raise ValueError(f"Changed source provenance {name}")
    for name, pin in evidence["derived_receipts"].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or sha256(path.read_bytes()).hexdigest() != pin["sha256"]:
            raise ValueError(f"Changed derived provenance {name}")
    raw = (ROOT / "inputs/comparator/ADMISSION.json").read_bytes()
    admission = loads(raw, object_pairs_hook=unique)
    if (sha256(raw).hexdigest() != ADMISSION or admission["head"] != HEAD
            or admission["status"] != "exact-complete-receipt-reused"
            or set(admission["checks"]) != {"early", "native", "caller", "frontier"}
            or not all(stage.startswith("PASS_") for stage in admission["checks"].values())):
        raise ValueError("Changed comparator admission")
    for name in ("RESULT.json", "NATIVE-RESULT.json"):
        rel = "research/p104-helper-319-fused-return/" + name
        raw = (ROOT / "inputs/comparator" / name).read_bytes()
        if sha256(raw).hexdigest() != admission["package_sha256"][rel]:
            raise ValueError(f"Changed admitted comparator artifact {name}")


def main():
    verify_provenance()
    command = [executable, "-I", "-B", str(ROOT / "check_contract.py")]
    result = run(command, check=True, capture_output=True, timeout=12)
    if result.stdout != (ROOT / "CONTRACT.json").read_bytes():
        raise ValueError("Changed exact contract receipt")
    with TemporaryDirectory(prefix="retained-j-provider-") as tmp:
        scratch = Path(tmp)
        copytree(ROOT / "inputs", scratch / "inputs")
        runner = scratch / "check_contract.py"
        runner.write_bytes((ROOT / "check_contract.py").read_bytes())
        caller = scratch / "inputs/caller/CALLER.json"
        caller.write_bytes(caller.read_bytes() + b"\n")
        mutation = run([executable, "-I", "-B", str(runner)], capture_output=True, timeout=12)
        if not mutation.returncode or mutation.stdout or b"Changed input inputs/caller/CALLER.json" not in mutation.stderr:
            raise ValueError("Changed caller bytes passed the replay")
    print("PASS_RETAINED_J_PROVIDER_BOUND kappa_change=0 host_rank_floor=4 scalar_top_up_credit=0")


if __name__ == "__main__":
    main()
