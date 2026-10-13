"""Validate the immutable upstream source before importing or compiling it.

Generated certificate metadata may differ in the checkout; executable source
and source manifests may not. No checkout files are reset or rewritten.
"""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

PIN = "ad0f25ff7b23cff7f08ad237c2254e6ecf74257e"
PR60_PIN = "e7a492dd8bee4e6f574ced784a62af2ce735edc4"
PACKAGE = Path(__file__).resolve().parents[1]
SOURCE_SUFFIXES = {".py", ".cpp", ".cc", ".c", ".h", ".hpp"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def source_path(name):
    return Path(name).suffix in SOURCE_SUFFIXES or Path(name).name == "SOURCE.json"


def validate_checkout(root, pin=PIN):
    require(not sys.flags.optimize, "Assertions must remain enabled")
    require(sys.version_info >= (3, 10), "Python 3.10 or newer is required")
    root = Path(root).resolve()
    require(git(root, "rev-parse", "HEAD").decode().strip() == pin,
            "Upstream HEAD must equal pinned commit " + pin)
    tracked = git(root, "ls-tree", "-r", "--name-only", "-z", pin).decode().split("\0")
    # Validate all tracked executable source, not merely the top-level wrapper.
    # This covers Python imports, C++ headers and inherited source manifests.
    changed = []
    hashes = {}
    for name in tracked:
        if not name or not source_path(name):
            continue
        expected = git(root, "show", pin + ":" + name)
        path = root / name
        if not path.is_file() or path.read_bytes() != expected:
            changed.append(name)
        hashes[name] = sha256(expected).hexdigest()
    require(not changed, "Dirty pinned source: " + ", ".join(changed))
    untracked = git(root, "ls-files", "--others", "--exclude-standard", "-z").decode().split("\0")
    extra = [name for name in untracked if name and source_path(name)]
    require(not extra, "Untracked source can shadow pinned imports: " + ", ".join(extra))
    return root, hashes


def validate_upstream(root):
    root, hashes = validate_checkout(root)
    manifest = json.loads((PACKAGE / "finite-frames/source-word-manifest.json").read_text())
    require(manifest["upstream_pin"] == PIN, "Manifest upstream pin mismatch")
    for name, digest in manifest["sources"].items():
        raw = git(root, "show", PIN + ":" + name)
        require(sha256(raw).hexdigest() == digest, "Manifest source digest mismatch: " + name)
        require((root / name).read_bytes() == raw, "Dirty manifest source: " + name)
    compiler = (root / "scripts/experiments/binary_frame_compiler.py").read_text()
    transform = manifest["compiler_transform"]
    require(compiler.count(transform["old"]) == transform["replacements"] == 1,
            "Compiler transform must replace one exact occurrence")
    derived = compiler.replace(transform["old"], transform["new"])
    require(sha256(derived.encode()).hexdigest() == transform["derived_source_sha256"],
            "Transformed compiler digest mismatch")
    return root, manifest, hashes, derived


def generated_directory(path, upstream):
    destination = Path(path).resolve()
    require(destination != upstream and upstream not in destination.parents,
            "Generated outputs must be outside the pinned upstream checkout")
    destination.mkdir(parents=True, exist_ok=True)
    return destination
