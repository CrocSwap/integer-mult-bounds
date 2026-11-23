"""Restore the signed source and replay the fixed 25-bit period profile."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import runpy
from shutil import copyfile
from subprocess import run
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
PINS = {
    "PREDECESSOR-RESULT.json": "4e173fd0a9f4b593baf706a00899cc1336dae5eab922c43e6551775256733f63",
    "upstream_verify.py": "10362de3ceaa651cde5b71c6599fd4683d9f1f4d76cc252178e915b43a098fee",
    "prepare.py": "76f9d4c6bfd880ee49f6ba5bde9138cf0856d669edb4d525e48ca71a9094eec3",
    "PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    "peer8057.tar.gz": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
    "check_cutoff.py": "7f60cba19d4f7c492aa3ab824ea48a5d88071582b47a5cd42dd2ba88aa8d553c",
    "check_stage_seam.py": "128a93719bbfc2d69c442283b8cbaecd9a3ca4c2a2399a7964e4c882bf0bace1",
    "check_ordinary_floor.py": "65e3c3ca4cec73a9462973e651a66127ab894d0bc141c072e26416aedb48b543",
    "UPSTREAM-RESULT.json": "2191321d98438d7618305766c7c702f74c597983f667e40a66a832570ce6e2e3",
}


def authenticate():
    for name, digest in PINS.items():
        if sha256((HERE / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Unexpected #8072 source image: {name}")


def replay(profile, mode):
    authenticate()
    original = runpy.run_path(str(HERE / "upstream_verify.py"))
    with TemporaryDirectory(prefix=f"p104-scaled-{profile}-") as temporary:
        tree = Path(temporary)
        peer = original["restore"](tree)
        runpy.run_path(str(HERE / "prepare.py"))["materialize"](peer)
        runpy.run_path(str(HERE / "retune.py"))["install"](peer, profile)
        copyfile(HERE / "PREDECESSOR-RESULT.json", peer / "PREDECESSOR-RESULT.json")
        if mode == "regenerate":
            runtime = tree / "runtime"
            run([sys.executable, "-IB", str(peer / "bootstrap.py"), str(runtime)], check=True)
            result = run([sys.executable, "-IB", str(peer / "receipt.py"), str(runtime)],
                         check=True, capture_output=True, text=True)
            print(json.dumps(json.loads(result.stdout), indent=2))
            return
        (peer / "RESULT.json").write_bytes((HERE / f"RESULT-{profile}.json").read_bytes())
        run([sys.executable, "-IB", str(peer / "verify.py"), mode], check=True)
        print("PASS_25BIT_PERIOD_SIGNED", mode, flush=True)


def main():
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    modes = ("price", "calendar", "raw", "exterior", "nested", "product", "regenerate")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("profile", choices=("460",))
    parser.add_argument("mode", choices=modes)
    args = parser.parse_args()
    replay(args.profile, args.mode)


if __name__ == "__main__":
    main()
