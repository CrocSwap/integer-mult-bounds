"""Git-free replay of the two exact residual rank-five endpoint cohorts."""
from argparse import ArgumentParser
from hashlib import sha1, sha256
from json import loads
from pathlib import Path, PurePosixPath
from runpy import run_path
from shutil import copyfile
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
STAGES = (
    ("preflight/freeze.py", "preflight/FROZEN.json", "FROZEN.json"),
    ("lead/pairs.py", "lead/RESULT.json", "RATIONAL.json"),
    ("independent/singleton.py", "independent/RESULT.json", "FORWARD.json"),
    ("independent/compare.py", "independent/AGREEMENT.json", "AGREEMENT.json"),
)


def unique(rows):
    result = dict(rows)
    if len(result) != len(rows):
        raise ValueError("duplicate package key")
    return result


def read_json(path):
    return loads(path.read_bytes(), object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def relative(name):
    path = PurePosixPath(name)
    if path.is_absolute() or path.as_posix() != name or ".." in path.parts:
        raise ValueError(f"invalid relative path {name}")
    return path


def authenticate():
    pins = read_json(ROOT / "LOCAL-PINS.json")
    for name, expected in pins.items():
        data = (ROOT / relative(name)).read_bytes()
        if digest(data) != expected:
            raise ValueError(f"changed package dependency {name}")
    prov = read_json(ROOT / "PROVENANCE.json")
    for name, source in prov["files"].items():
        data = (ROOT / relative(name)).read_bytes()
        assert digest(data) == pins[name] == source["sha256"]
        if "git_blob" in source:
            assert sha1(f"blob {len(data)}\0".encode()+data).hexdigest() == source["git_blob"]
    for name, source in prov["regenerated_predecessor_receipts"].items():
        manifest = read_json(ROOT / relative(source["manifest"]))
        assert manifest[source["receipt"]] == pins[name]
    control = prov["historical_control"]
    assert pins[control["path"]] == control["sha256"]
    return pins


def command(root, script):
    return run([sys.executable, "-I", "-B", str(root/script)], cwd=root,
               capture_output=True, timeout=35)


def reject(root, path, script):
    target = root/path
    original = target.read_bytes()
    try:
        target.write_bytes(original+b"\n")
        proc = command(root,script)
        assert proc.returncode == 1 and not proc.stdout
        assert b"changed dependency" in proc.stderr and target.name.encode() in proc.stderr
    finally:
        target.write_bytes(original)


def replay(root):
    pins = authenticate()
    expected = read_json(ROOT/"receipts/SHA256.json")
    assert set(expected) == {name for _,_,name in STAGES}
    for name in pins:
        if not name.startswith(("inputs/","preflight/","lead/","independent/")):
            continue
        target = root/relative(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        copyfile(ROOT/name,target)
    for name in run_path(str(root/"preflight/freeze.py"))["PINS"]:
        local = root/"preflight"/relative(name)
        local.parent.mkdir(parents=True, exist_ok=True)
        source = "inputs/OLD-WITNESS.json" if name == "inputs/CHART118-CONTROL.json" else name
        copyfile(root/source,local)
    outputs = {}
    for script, path, name in STAGES:
        result = command(root,script)
        if result.returncode:
            sys.stderr.write(result.stderr.decode(errors="replace"))
            result.check_returncode()
        assert not result.stderr and digest(result.stdout) == expected[name], ("changed receipt",name)
        (root/path).write_bytes(result.stdout)
        outputs[name] = result.stdout
    frozen = read_json(root/"preflight/FROZEN.json")
    agreement = read_json(root/"independent/AGREEMENT.json")
    assert frozen["case_count"] == agreement["case_agreements"] == 14
    assert agreement["suffix_required"] == agreement["unresolved"] == 0
    for target, script in [
        ("preflight/inputs/PR7375-SECOND.json","preflight/freeze.py"),
        ("preflight/FROZEN.json","independent/singleton.py"),
        ("inputs/7334-WORD.json.gz","lead/pairs.py"),
    ]:
        reject(root,target,script)
    return outputs


def main():
    parser = ArgumentParser()
    parser.add_argument("--out",type=Path,help="write the four regenerated receipts to a fresh directory")
    args = parser.parse_args()
    assert __debug__ and sys.version_info[:2] == (3,12)
    with TemporaryDirectory(prefix="rank-five-pairing-") as directory:
        outputs = replay(Path(directory))
    if args.out:
        args.out.mkdir(parents=True,exist_ok=True)
        if any(args.out.iterdir()):
            raise ValueError("receipt output directory must be empty")
        for name, raw in outputs.items():
            (args.out/name).write_bytes(raw)
    print("PASS_RANK_FIVE_SINGLETON_RESIDUAL 14 exact prefixes excluded; 0 unresolved; 3 mutation controls")


if __name__ == "__main__":
    main()
