"""Exercise archive and scope-receipt rejection without changing the source bundle."""

from copy import copy
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("integrated_gaussian_verify", ROOT / "verify.py")
verify = module_from_spec(spec)
spec.loader.exec_module(verify)


def must_fail(action, text):
    try:
        action()
    except ValueError as error:
        if text not in str(error):
            raise AssertionError("unexpected rejection: " + str(error)) from error
    else:
        raise AssertionError("malformed input accepted: " + text)


def altered_bundle(source, destination, kind):
    with tarfile.open(source, "r:gz") as old, tarfile.open(destination, "w:gz") as new:
        members = old.getmembers()
        if kind == "absolute":
            bad = tarfile.TarInfo("/six-column-8073/absolute")
            bad.size = 1
            new.addfile(bad, BytesIO(b"x"))
            return
        for item in members:
            payload = BytesIO(old.extractfile(item).read()) if item.isfile() else None
            new.addfile(copy(item), payload)
        item = members[0]
        payload = BytesIO(old.extractfile(item).read()) if item.isfile() else None
        new.addfile(copy(item), payload)


def fake_runner(tree, printed, receipt=None):
    combined = tree / "combined"
    combined.mkdir()
    (combined / "run_successor.py").write_text("print(" + repr(printed) + ")\n")
    logs = combined / "successor/logs"
    logs.mkdir(parents=True)
    if receipt is not None:
        (logs / "setup.json").write_text(json.dumps(receipt))
        (logs / "setup.out").write_bytes(b"scope-output")
    return combined


def main():
    optimized = subprocess.run([sys.executable, "-I", "-O", "-B", str(ROOT / "verify.py"), "setup"],
                               capture_output=True, text=True)
    if optimized.returncode == 0 or "do not use -O" not in optimized.stderr + optimized.stdout:
        raise AssertionError("optimized Python was not rejected")
    with TemporaryDirectory(prefix="gaussian-guard-") as temporary:
        tree = Path(temporary)
        case = tree / "case"
        (case / "source").mkdir(parents=True)
        shutil.copyfile(ROOT / "source/archive-members.json", case / "source/archive-members.json")
        shutil.copytree(ROOT / "source-view", case / "source-view")
        original = ROOT / "source/six-column-8073-public.tar.gz"
        archive = case / "source/six-column-8073-public.tar.gz"
        verify.HERE = case
        shutil.copyfile(original, archive)
        archive.write_bytes(archive.read_bytes() + b"corrupt")
        must_fail(lambda: verify.unpack(tree / "bad-hash"), "archive digest mismatch")
        for kind, message in (("absolute", "noncanonical archive path"),
                              ("duplicate", "duplicate archive member")):
            altered_bundle(original, archive, kind)
            verify.ARCHIVE_SHA256 = sha256(archive.read_bytes()).hexdigest()
            must_fail(lambda: verify.unpack(tree / kind), message)

        with tarfile.open(original, "r:gz") as bundle:
            peer = bundle.extractfile("six-column-8073/peer8057.tar.gz").read()
            peer_pins = json.loads(bundle.extractfile("six-column-8073/source8073/PEER-SOURCE.json").read())
        nested = tree / "peer.tar.gz"
        nested.write_bytes(peer)
        for kind, message in (("absolute", "invalid peer path"), ("duplicate", "duplicate peer member")):
            variant = tree / (kind + "-peer.tar.gz")
            altered_bundle(nested, variant, kind)
            data = variant.read_bytes()
            pins = dict(peer_pins, archive_sha256=sha256(data).hexdigest())
            must_fail(lambda: verify.validate_peer(data, pins), message)

        one = tree / "selector"
        one.mkdir()
        must_fail(lambda: verify.run_scopes(fake_runner(one, "raw 0 0.1"), ("setup",)),
                  "scope output does not match selection")
        record = {"mode": "setup", "code": 1,
                  "started_at": "2026-01-01T00:00:00+00:00",
                  "finished_at": "2026-01-01T00:00:01+00:00", "output_sha256": "bad"}
        two = tree / "failed"
        two.mkdir()
        must_fail(lambda: verify.run_scopes(fake_runner(two, "setup 0 0.1", record), ("setup",)),
                  "scope failed or mislabeled")
        record["code"] = 0
        three = tree / "digest"
        three.mkdir()
        must_fail(lambda: verify.run_scopes(fake_runner(three, "setup 0 0.1", record), ("setup",)),
                  "scope output digest mismatch")
    print("PASS_ARCHIVE_AND_RECEIPT_GUARDS")


if __name__ == "__main__":
    main()
