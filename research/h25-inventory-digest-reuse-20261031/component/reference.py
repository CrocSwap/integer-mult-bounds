"""Literal pinned v4 inventory extraction; no full-driver import."""
import hashlib
import stat


def need(condition, message):
    if not condition:
        raise RuntimeError(message)



def sha(data):
    return hashlib.sha256(data).hexdigest()



def inventory(root, pins, *, exact=True):
    need(root.is_dir() and not root.is_symlink(), "Missing or symlinked input root")
    files = {}
    for path in sorted(root.rglob("*")):
        need(not path.is_symlink(), "Symlink in frozen inputs: " + str(path))
        if path.is_file():
            relative = str(path.relative_to(root))
            if relative not in pins:
                need(not exact, "Undeclared frozen input: " + relative)
                continue
            raw = path.read_bytes()
            expected = pins[relative][0] if type(pins[relative]) is list else pins[relative]
            need(sha(raw) == expected, "Frozen input digest changed: " + relative)
            files[relative] = {"sha256": sha(raw), "mode": stat.S_IMODE(path.stat().st_mode), "bytes": len(raw)}
    need(set(files) == set(pins), "Frozen input inventory incomplete")
    return files

