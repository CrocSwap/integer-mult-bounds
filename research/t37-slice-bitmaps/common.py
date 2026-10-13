"""Strict data/source admission and immutable archive inputs. Apache-2.0."""
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def invalid(value):
    raise ValueError("nonfinite JSON: " + value)


def load(path):
    data = Path(path).read_bytes()
    if Path(path).suffix == ".gz":
        data = gzip.decompress(data)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def same(a, b, message):
    need(canonical(a) == canonical(b), message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def pins(root=ROOT):
    manifest = load(HERE / "SOURCES.json")
    for name, expected in manifest["files"].items():
        need(sha(Path(root) / name) == expected, "source hash mismatch: " + name)
    for name, expected in manifest["implementation"].items():
        need(sha(HERE / name) == expected, "implementation hash mismatch: " + name)
    return manifest


def materialize(root, output, manifest):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    archives = {}
    for row in manifest["members"]:
        archives.setdefault(row["archive"], {})[row["member"]] = row
    for archive, wanted in archives.items():
        seen = set()
        # Read-only member access; never extract archive paths or execute files.
        with tarfile.open(Path(root) / archive, "r|gz") as stream:
            for member in stream:
                if member.name not in wanted:
                    continue
                row = wanted[member.name]
                need(member.isfile() and member.name not in seen and member.size == row["size"], "archive member admission")
                data = stream.extractfile(member).read()
                need(hashlib.sha256(data).hexdigest() == row["sha256"], "archive member hash")
                target = output / row["destination"]
                need(target.resolve().is_relative_to(output.resolve()), "archive destination")
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as f:
                    f.write(data)
                seen.add(member.name)
        need(seen == set(wanted), "missing archive member")
    return output


def input_pins(inputs, manifest):
    for row in manifest["members"]:
        need(sha(Path(inputs) / row["destination"]) == row["sha256"], "immutable input hash: " + row["destination"])


def normalize(report, manifest):
    # Retain every original receipt field; only machine-specific input path
    # keys become eight fixed logical source names after exact hash admission.
    expected = manifest["logical_input_hashes"]
    actual = report["input_sha256"]
    need(len(actual) == len(expected) and sorted(actual.values()) == sorted(expected.values()), "receipt input inventory")
    result = dict(report)
    result["input_sha256"] = dict(expected)
    return result
