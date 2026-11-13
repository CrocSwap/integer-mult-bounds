"""Verify exact forward and independent common-plane receipts."""
from gzip import decompress
from hashlib import sha256
from json import loads
from pathlib import Path, PurePosixPath
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent


def unique(pairs):
    values = dict(pairs)
    assert len(values) == len(pairs), "duplicate JSON key"
    return values


def read(name):
    raw = (ROOT / name).read_bytes()
    return loads(decompress(raw) if name.endswith(".gz") else raw, object_pairs_hook=unique)


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3, 12)
    manifest = read("PINS.json")
    files = {f.relative_to(ROOT).as_posix() for folder in ("inputs", "receipts")
             for f in (ROOT / folder).iterdir() if f.is_file()}
    scripts = {"lead.py", "independent.py", "cut_flow.py", "endpoint_replay.py", "reverse_inventory.py"}
    assert set(manifest) == files | scripts | {"PROVENANCE.json"}
    for name, digest in manifest.items():
        path = PurePosixPath(name)
        assert not path.is_absolute() and ".." not in path.parts
        assert sha256((ROOT / path).read_bytes()).hexdigest() == digest, name

    lead_raw = run([executable, "-I", "-B", str(ROOT/"lead.py")], check=True,
                   capture_output=True, timeout=65).stdout
    lead = loads(lead_raw, object_pairs_hook=unique)
    expected_lead = read("receipts/LEAD.json.gz")
    for result in (lead, expected_lead):
        if "SAVED-PLANES.json" in result["pins"]:
            result["pins"]["R226-PLANES.json"] = result["pins"].pop("SAVED-PLANES.json")
    assert lead == expected_lead
    independent_raw = run([executable, "-I", "-B", str(ROOT/"independent.py"),
                           str(ROOT/"receipts/LEAD.json.gz")], check=True,
                          capture_output=True, timeout=65).stdout
    independent = loads(independent_raw, object_pairs_hook=unique)
    assert independent == read("receipts/INDEPENDENT.json")
    assert lead["benchmark_head"] == "89eaa9d8cae37c1540de98f2d29a3abaabb96a2b"
    assert not lead["capped"] and not independent["capped"] and lead["witness"] is None
    assert len(lead["records"]) == len(independent["rows"]) == 256
    assert len(lead["ranking"]) == 1014 and len(lead["open_planes"]) == 758
    assert all(record["excluded"] for record in lead["records"])
    assert all(lower == 0 and (upper == 0 or vertices == [0]*18)
               for _, _, lower, upper, vertices in independent["rows"])
    print("PASS_ENDPOINT_PLANE_GROWTH: 256 ranked planes excluded; 758 saved planes untested")


if __name__ == "__main__":
    main()
