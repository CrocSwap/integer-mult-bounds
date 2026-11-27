"""Replay the numerical tape multiplier package from the checkout containing this file."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
LOCK = json.loads((ROOT / "dependencies.json").read_text())
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}


def run(*args, cwd=ROOT, env=None, capture=False):
    result = subprocess.run(args, cwd=cwd, env=env, check=True, text=True,
                            stdout=subprocess.PIPE if capture else None)
    return result.stdout.strip() if capture else None


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def mathlib_checkout():
    pin = LOCK["mathlib"]
    supplied = os.environ.get("TAPE_MATHLIB_DIR")
    if supplied:
        library = Path(supplied).resolve()
    else:
        cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home()/".cache")) / "numerical-tape-overhead"
        cache.mkdir(parents=True, exist_ok=True)
        library = cache / pin
        if not library.exists():
            with tempfile.TemporaryDirectory(dir=cache) as tmp:
                repo = Path(tmp) / "mathlib"
                run("git", "init", "-q", repo)
                run("git", "remote", "add", "origin", "https://github.com/leanprover-community/mathlib4.git", cwd=repo)
                run("git", "fetch", "-q", "--depth=1", "origin", pin, cwd=repo)
                run("git", "checkout", "-q", "--detach", "FETCH_HEAD", cwd=repo)
                try:
                    repo.rename(library)
                except OSError:
                    if not library.exists():
                        raise
    check_revision(library, pin)
    return library


def check_revision(repo, pin):
    actual = run("git", "rev-parse", "HEAD", cwd=repo, capture=True)
    require(actual == pin, f"Wrong revision in {repo}: {actual}, expected {pin}")
    run("git", "diff", "--quiet", "HEAD", "--", cwd=repo)


def sources():
    local = {str(p.relative_to(ROOT).with_suffix("")).replace("/", "."): p
             for folder in ("OAI", "S008") for p in (ROOT/folder).rglob("*.lean")}
    local["Review"] = ROOT / "Review.lean"
    for rel, expected in LOCK["openai_blobs"].items():
        data = (ROOT/rel).read_bytes()
        if rel in LOCK["import_changes"]:
            change = LOCK["import_changes"][rel]
            prefix = change["packaged"].encode()
            require(data.startswith(prefix), f"Unexpected imports in {rel}")
            data = change["upstream"].encode() + data[len(prefix):]
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == expected, f"OpenAI source hash mismatch: {rel}")
    require(set(LOCK["openai_blobs"]) == {str(p.relative_to(ROOT)) for m,p in local.items()
                                         if m.startswith("OAI.")}, "OpenAI source manifest mismatch")
    order, seen, external = [], set(), set()

    def visit(name):
        if name in seen:
            return
        seen.add(name)
        for dep in re.findall(r"^import ([A-Za-z0-9_.]+)$", local[name].read_text(), re.M):
            if dep in local:
                visit(dep)
            else:
                require(dep.startswith("Mathlib."), f"Missing source for {dep}")
                external.add(dep)
        order.append(local[name])

    visit("Review")
    require(seen == set(local), f"Modules outside the replay: {sorted(set(local)-seen)}")
    return order, sorted(external)


def dependency_path(library, external):
    # Lake materializes its transitive git checkouts from mathlib's committed manifest.
    path = run("lake", "env", "printenv", "LEAN_PATH", cwd=library, capture=True)
    manifest = json.loads((library/"lake-manifest.json").read_text())
    for pkg in manifest["packages"]:
        require(pkg["type"] == "git", f"Unpinned dependency: {pkg['name']}")
        check_revision(library/manifest["packagesDir"]/pkg["name"], pkg["rev"])
    needs = [name.replace(".", "/") for name in external]
    built = library/".lake/build/lib/lean"
    if any(not (built/(name+".olean")).exists() for name in needs):
        run("lake", "exe", "cache", "get", *(name+".lean" for name in needs), cwd=library)
    return path


def audit_axioms(transcript):
    expected = set(re.findall(r"^#print axioms (\S+)$", (ROOT/"Review.lean").read_text(), re.M))
    actual = set()
    for name, axioms in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", transcript):
        used = {a.strip() for a in axioms.split(",") if a.strip()}
        require(used <= ALLOWED, f"{name} uses unexpected axioms: {used-ALLOWED}")
        actual.add(name)
    actual.update(re.findall(r"'([^']+)' does not depend on any axioms", transcript))
    require(actual == expected, f"Axiom report mismatch: {actual ^ expected}")
    print(f"Axioms checked for {len(expected)} designated declarations.", flush=True)


def main():
    os.environ.pop("LEAN_PATH", None)
    version = run("lean", "--version", capture=True)
    require(f"version {LOCK['lean']}," in version and LOCK["lean_commit"] in version, version)
    print(version, flush=True)
    print("Submission", run("git", "rev-parse", "HEAD", capture=True), flush=True)
    order, external = sources()
    library = mathlib_checkout()
    base = dependency_path(library, external)
    print(f"Mathlib {LOCK['mathlib']} and its locked dependencies verified.", flush=True)
    with tempfile.TemporaryDirectory(prefix="tape-overhead-") as build:
        env = {**os.environ, "LEAN_PATH": build + os.pathsep + base}
        for source in order:
            relative = source.relative_to(ROOT)
            output = (Path(build)/relative).with_suffix(".olean")
            output.parent.mkdir(parents=True, exist_ok=True)
            is_review = relative == Path("Review.lean")
            print(f"Checking {relative}", flush=True)
            receipt = run("lean", "-j1", "-DwarningAsError=true", "-o", output, relative,
                          env=env, capture=is_review)
            if is_review:
                print(receipt, flush=True)
                audit_axioms(receipt)
        print("Replaying all transitive declarations in a fresh kernel.", flush=True)
        run("leanchecker", "--fresh", "Review", env=env)
        print(f"PASS fresh kernel, {len(order)} packaged modules.", flush=True)
    checks = ROOT/"checks"
    for name in ("cutoff", "cutoff_independent", "exponents", "address-native-staircase",
                 "profile-limit", "routing-outer-space", "address-axis-window", "check-child-volume",
                 "schoolbook", "address-dyadic-words", "address-dyadic-caller", "recount-carry", "word-toom"):
        print(f"Checking {name}", flush=True)
        run(sys.executable, "-I", "-B", checks/(name+".py"), cwd=checks)
    for inputs in ("reference", "boundaries"):
        run(sys.executable, "-I", "-B", checks/"recount-system.py", "--inputs", inputs, cwd=checks)
    print("PASS arithmetic, adjacent cutoffs and four full-product fixtures.", flush=True)


if __name__ == "__main__":
    main()
