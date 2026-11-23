#!/usr/bin/env python3
"""Compare a candidate with a fresh #8088 bootstrap from its exact Git head.

Usage: python3.12 -I -B verify_bootstrap.py SOURCE_CHECKOUT CANDIDATE_ROOT
The checkout must contain commit 06691302af526a488f3dee0298035f86b6e69c51.
"""

from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory

HEAD = "06691302af526a488f3dee0298035f86b6e69c51"
PKG = "research/p104-shortcut-word-lift-20bit"
SOURCE_PINS = {
    "verify.py": "a6a03bccedfbbfa1739ccc8ef3052853accdc91e8f329969de3a3d17ae8219c7",
    "prepare.py": "3524bade68458207f78f3cd4040d06cc16334a8fb085a5570e0d391e384b9305",
    "PEER-SOURCE.json": "798c2e6394c258986484a116198cc542a6d2b4c1f289e5816de2cfecf5141c51",
    "peer8057.tar.gz": "0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c",
    "w5669_shortcut5.json.gz": "6ef741c346ea075c4f2ed11f9d42d7076103e72d4a9e5059d495f1cb990fd149",
    "check_cutoff.py": "51ffd638ee01377cc72718469007e556f7fb5b646bfd5258301dc0e29755fea1",
    "check_ordinary_floor.py": "417c9e4f1be8fd6be197a93aa136e527765a65032d7845eda653bdc89132edee",
    "check_stage_seam.py": "ba0427d889081c12993a16f491e32fffb5e22fe9a37b6baade8f2c8c2c0878f3",
}


def entries(root):
    result = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Unexpected symlink under {root}")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            result[path.relative_to(root).as_posix()] = sha256(path.read_bytes()).hexdigest()
    return result


def main(source, candidate, frozen=False):
    if not __debug__:
        raise ValueError("Run with assertions enabled")
    if frozen:
        package = source
        for name, expected in SOURCE_PINS.items():
            assert sha256((package / name).read_bytes()).hexdigest() == expected, name
    else:
        excluded = {"GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE", "GIT_CEILING_DIRECTORIES",
                    "GIT_COMMON_DIR", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT"}
        env = {k: v for k, v in os.environ.items()
               if k not in excluded and not k.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))}
        env["GIT_NO_REPLACE_OBJECTS"] = "1"
        git = ["git", "--no-replace-objects", "-C", str(source)]
        assert subprocess.run(git + ["rev-parse", "HEAD"], env=env, check=True,
                              capture_output=True, text=True).stdout.strip() == HEAD
        package = source / PKG
        for name, expected in SOURCE_PINS.items():
            working = (package / name).read_bytes()
            committed = subprocess.run(git + ["cat-file", "blob", f"{HEAD}:{PKG}/{name}"],
                                       env=env, check=True, capture_output=True).stdout
            assert committed == working and sha256(committed).hexdigest() == expected, name
    with TemporaryDirectory(prefix="ordinary-bootstrap-") as tmp:
        tree = Path(tmp)
        peer = runpy.run_path(str(package / "verify.py"))["restore"](tree)
        runpy.run_path(str(package / "prepare.py"))["materialize"](peer)
        subprocess.run([sys.executable, "-I", "-B", "-X", f"pycache_prefix={tree / 'cache'}",
                        str(peer / "bootstrap.py"), str(tree / "runtime")], check=True)
        expected_runtime = tree / "runtime"
        candidate_runtime = candidate / "runtime"
        before, after = entries(expected_runtime), entries(candidate_runtime)
        assert before.keys() == after.keys()
        changed = [name for name in sorted(before) if before[name] != after[name]]
        assert changed == ["installations.py", "raw_binary_stage.py"]

        prior_line = b'TERMINAL = Profile((62186, 986008, 1048575), 66037, Q(".003899574328473"))'
        next_line = b'TERMINAL = Profile((8192, 106000, 1681001), 85406, Q(39, 10000), eta=Q(1, 256))'
        old_install = (expected_runtime / "installations.py").read_bytes()
        assert old_install.count(prior_line) == 1
        assert old_install.replace(prior_line, next_line) == (candidate_runtime / "installations.py").read_bytes()
        old_raw = (expected_runtime / "raw_binary_stage.py").read_bytes()
        assert old_raw.count(b"level_floor=4474") == 1
        assert old_raw.replace(b"level_floor=4474", b"level_floor=18960") == (candidate_runtime / "raw_binary_stage.py").read_bytes()

        candidate_peer = candidate / "research/frequency-weighted-native-multiplier"
        peer_before, peer_after = entries(peer), entries(candidate_peer)
        added = {"check_cutoff.py", "check_ordinary_floor.py", "check_stage_seam.py"}
        assert peer_after.keys() == peer_before.keys() | added
        assert all(peer_before[name] == peer_after[name] for name in peer_before)
        assert all((candidate_peer / name).read_bytes() == (package / name).read_bytes() for name in added)
        tiered = tree / "research/tiered-native-multiplier"
        candidate_tiered = candidate / "research/tiered-native-multiplier"
        assert entries(tiered) == entries(candidate_tiered)
        # Detect candidate mutation during the comparison, excluding ignored pyc.
        assert after == entries(candidate_runtime) and peer_after == entries(candidate_peer)
        print(json.dumps({
            "status": "PASS_PINNED_BOOTSTRAP_COMPARISON", "source_head": HEAD,
            "source_git_objects_checked": 0 if frozen else len(SOURCE_PINS), "runtime_files_checked": len(before),
            "runtime_deltas": [{"path": name, "before_sha256": before[name], "after_sha256": after[name]}
                               for name in changed],
            "frequency_files_checked": len(peer_before), "copied_upstream_checks": sorted(added),
            "tiered_files_checked": len(entries(tiered)),
            "scope": "Fresh #8088 source reconstruction and exact byte comparison; no physical product or source admission follows.",
        }, indent=2, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4) or (len(sys.argv) == 4 and sys.argv[3] != "--frozen-bytes"):
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), len(sys.argv)==4)
