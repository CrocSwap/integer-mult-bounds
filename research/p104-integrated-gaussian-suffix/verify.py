#!/usr/bin/env python3
"""Authenticate a pinned source bundle and run one declared scientific scope.

All source construction and generated logs live in a fresh temporary directory.
The wrapper validates each named scope's recorded exit and stdout digest; it does
not promote an individual successful check to a claim about the other scopes.
"""

from argparse import ArgumentParser
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from io import BytesIO
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
import json
import shutil
import subprocess
import sys
import tarfile


if not __debug__ or sys.flags.optimize:
    raise SystemExit("Verification requires Python assertions; do not use -O or -OO.")

HERE = Path(__file__).resolve().parent
ARCHIVE_SHA256 = "1ffaf4eed67cfe2271820bc94d62721573ff715829c829c5d9936b561eacb270"
MANIFEST_SHA256 = "ba961383f648a6d7dcbf9caaee4240d4b74486050a2d9d1bc0e100bd2bff6ca5"
ADDENDUM_SHA256 = "bacfc6ec44616063eae1584e6af07a1dbbfaf7948df1745bc059aa4510c7c9a0"
ADDENDUM_MANIFEST_SHA256 = "dfe65dbea792691d82e7c1265cae8e82f374e8c48f644c220643cbaaac978507"
SCOPES = {
    "price": ("invoice", "independent_price", "placement"),
    "calendar": ("cutoff", "calendar", "ownership", "stages", "ordinary_floor", "corrupted_owner"),
    "raw": ("raw",),
    "exterior": ("exterior",),
    "nested": ("nested",),
    "product": ("product",),
    "setup": ("setup",),
}
ADDENDUM_SCOPES = ("source_invoice", "ordinary_tariff", "stage_caps", "invoice",
                   "independent_price", "cutoff", "corrupted_owner")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "duplicate JSON key: " + key)
        value[key] = item
    return value


def read_json(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique_object)


def digest(data):
    return sha256(data).hexdigest()


def canonical_path(name):
    require(isinstance(name, str) and "\\" not in name and "\x00" not in name,
            "invalid archive path")
    path = PurePosixPath(name)
    require(bool(path.parts) and not path.is_absolute() and ".." not in path.parts
            and path.as_posix() == name and path.parts[0] == "six-column-8073"
            and len(path.parts) >= 2, "noncanonical archive path: " + name)
    return path


def validate_peer(data, pins):
    """Independently check the complete immediate #8057 tar inventory."""
    require(digest(data) == pins["archive_sha256"], "peer archive digest mismatch")
    files = pins["files_sha256"]
    require(isinstance(files, dict) and len(files) == 88, "unexpected peer inventory")
    directories = set()
    for name in files:
        path = PurePosixPath(name)
        require(not path.is_absolute() and ".." not in path.parts and "\\" not in name
                and path.as_posix() == name and len(path.parts) > 1, "invalid peer manifest path")
        directories.update(PurePosixPath(*path.parts[:i]).as_posix() for i in range(1, len(path.parts)))
    seen, found = set(), set()
    with tarfile.open(fileobj=BytesIO(data), mode="r:gz") as bundle:
        for member in bundle:
            name = member.name
            path = PurePosixPath(name)
            require(bool(path.parts) and not path.is_absolute() and ".." not in path.parts
                    and "\\" not in name and path.as_posix() == name, "invalid peer path: " + name)
            require(name not in seen, "duplicate peer member: " + name)
            seen.add(name)
            if member.isdir():
                require(name in directories, "unexpected peer directory: " + name)
                continue
            require(member.isfile() and name in files and member.size <= 10_000_000,
                    "unexpected peer member: " + name)
            stream = bundle.extractfile(member)
            require(stream is not None, "missing peer payload: " + name)
            payload = stream.read(member.size + 1)
            require(len(payload) == member.size and digest(payload) == files[name],
                    "peer member digest mismatch: " + name)
            found.add(name)
    require(found == set(files), "peer archive is missing whitelisted files")


def unpack(tree):
    archive = HERE / "source/six-column-8073-public.tar.gz"
    manifest_path = HERE / "source/archive-members.json"
    require(digest(archive.read_bytes()) == ARCHIVE_SHA256, "archive digest mismatch")
    require(digest(manifest_path.read_bytes()) == MANIFEST_SHA256, "member manifest digest mismatch")
    pins = read_json(manifest_path)
    require(isinstance(pins, dict) and len(pins) == 28, "unexpected member inventory")
    for name, entry in pins.items():
        canonical_path(name)
        require(set(entry) == {"sha256", "size"} and isinstance(entry["size"], int)
                and 0 <= entry["size"] <= 3_000_000, "invalid member pin: " + name)
    seen = set()
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle:
            name = member.name
            path = canonical_path(name)
            require(name not in seen, "duplicate archive member: " + name)
            require(member.isfile() and name in pins, "unexpected archive member: " + name)
            require(member.size == pins[name]["size"], "member length mismatch: " + name)
            fileobj = bundle.extractfile(member)
            require(fileobj is not None, "missing member payload: " + name)
            data = fileobj.read(member.size + 1)
            require(len(data) == member.size and digest(data) == pins[name]["sha256"],
                    "member digest mismatch: " + name)
            relative = PurePosixPath(*path.parts[1:])
            if relative.as_posix() != "peer8057.tar.gz":
                visible = HERE / "source-view" / Path(*relative.parts)
                require(visible.is_file() and not visible.is_symlink()
                        and digest(visible.read_bytes()) == pins[name]["sha256"],
                        "review copy differs: " + relative.as_posix())
            output = tree / Path(*path.parts)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(data)
            seen.add(name)
    require(seen == set(pins), "archive is missing whitelisted members")
    visible = {p.relative_to(HERE / "source-view").as_posix()
               for p in (HERE / "source-view").rglob("*") if p.is_file()}
    wanted = {PurePosixPath(*canonical_path(n).parts[1:]).as_posix() for n in pins
              if n != "six-column-8073/peer8057.tar.gz"}
    require(visible == wanted, "unexpected or missing review copy")
    source = tree / "six-column-8073"
    validate_peer((source / "peer8057.tar.gz").read_bytes(), read_json(source / "source8073/PEER-SOURCE.json"))
    return source


def unpack_addendum(tree):
    archive = HERE / "source/six-column-8076-addendum.tar.gz"
    manifest_path = HERE / "source/addendum-members.json"
    require(digest(archive.read_bytes()) == ADDENDUM_SHA256, "addendum archive digest mismatch")
    require(digest(manifest_path.read_bytes()) == ADDENDUM_MANIFEST_SHA256,
            "addendum member manifest digest mismatch")
    pins = read_json(manifest_path)
    require(isinstance(pins, dict) and len(pins) == 31, "unexpected addendum inventory")
    seen = set()
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle:
            name = member.name
            path = PurePosixPath(name)
            require(bool(path.parts) and not path.is_absolute() and ".." not in path.parts
                    and "\\" not in name and path.as_posix() == name
                    and len(path.parts) >= 2 and path.parts[0] == "six-column-8076",
                    "noncanonical addendum path: " + name)
            require(name not in seen, "duplicate addendum member: " + name)
            require(member.isfile() and name in pins, "unexpected addendum member: " + name)
            entry = pins[name]
            require(set(entry) == {"sha256", "size"} and type(entry["size"]) is int
                    and 0 <= member.size <= 1_000_000 and member.size == entry["size"],
                    "addendum member length mismatch: " + name)
            stream = bundle.extractfile(member)
            require(stream is not None, "missing addendum payload: " + name)
            data = stream.read(member.size + 1)
            require(len(data) == member.size and digest(data) == entry["sha256"],
                    "addendum member digest mismatch: " + name)
            relative = PurePosixPath(*path.parts[1:])
            visible = HERE / "source-view-8076" / Path(*relative.parts)
            require(visible.is_file() and not visible.is_symlink() and digest(visible.read_bytes()) == entry["sha256"],
                    "addendum review copy differs: " + relative.as_posix())
            destination = tree / Path(*path.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            seen.add(name)
    require(seen == set(pins), "addendum is missing whitelisted members")
    visible = {p.relative_to(HERE / "source-view-8076").as_posix()
               for p in (HERE / "source-view-8076").rglob("*") if p.is_file()}
    wanted = {PurePosixPath(*PurePosixPath(n).parts[1:]).as_posix() for n in pins}
    require(visible == wanted, "unexpected or missing addendum review copy")
    return tree / "six-column-8076"


def invoke(script, *args):
    result = subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, args)],
                            capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("failed command " + script.name + ": " + result.stderr[-4000:]
                           + "\n" + result.stdout[-4000:])
    return result.stdout


def compose(source):
    invoke(source / "compose8073.py")
    return source / "combined"


def run_scopes(combined, names):
    output = invoke(combined / "run_successor.py", *names)
    lines = [line.split() for line in output.splitlines() if line.strip()]
    require(len(lines) == len(names) and all(len(row) == 3 for row in lines)
            and [row[0] for row in lines] == list(names)
            and all(row[1] == "0" for row in lines), "scope output does not match selection")
    logs = combined / "successor/logs"
    require({p.stem for p in logs.glob("*.json")} == set(names), "scope receipt set differs")
    records = {}
    for name in names:
        record = read_json(logs / (name + ".json"))
        require(record.get("mode") == name and type(record.get("code")) is int
                and record["code"] == 0, "scope failed or mislabeled: " + name)
        stdout = (logs / (name + ".out")).read_bytes()
        require(record.get("output_sha256") == digest(stdout), "scope output digest mismatch: " + name)
        for field in ("started_at", "finished_at"):
            stamp = datetime.fromisoformat(record[field])
            require(stamp.utcoffset() is not None, "scope receipt has no timezone: " + name)
        require(datetime.fromisoformat(record["started_at"]) <= datetime.fromisoformat(record["finished_at"]),
                "scope timestamps out of order: " + name)
        records[name] = {key: record[key] for key in
                         ("code", "started_at", "finished_at", "output_sha256")}
    return records


def check_json_output(script, reference, *args, keys=None):
    observed = json.loads(invoke(script, *args), object_pairs_hook=unique_object)
    expected = read_json(reference)
    if keys is not None:
        observed = {key: observed[key] for key in keys}
        expected = {key: expected[key] for key in keys}
    require(observed == expected, "independent result differs: " + script.name)


def rebuild_eight(tree, source):
    root = tree / "eight-column"
    root.mkdir()
    shutil.copytree(source / "source8073", root / "source8073")
    shutil.copyfile(source / "peer8057.tar.gz", root / "source8073/peer8057.tar.gz")
    (root / "overlay").mkdir()
    for name in ("weighted_suffix.py", "independent_gaussian.py", "check_combined_seams.py"):
        shutil.copyfile(HERE / "appendix" / name, root / "overlay" / name)
    shutil.copyfile(HERE / "appendix/rebuild_e8.py", root / "rebuild_e8.py")
    output = invoke(root / "rebuild_e8.py")
    require("PASS_SOURCE_RECONSTRUCTION" in output and "PASS_COMBINED_RECEIPT" in output,
            "eight-column reconstruction did not report its two checks")
    require(read_json(root / "RESULT-8073.json") == read_json(HERE / "data/eight-column-invoice.json"),
            "eight-column signed invoice differs")
    return root


def price_checks(tree, source, combined):
    invoice = read_json(combined / "successor/logs/invoice.out")
    require(invoice == read_json(HERE / "data/six-column-invoice.json"),
            "six-column signed invoice differs")
    check_json_output(HERE / "checks/check_referee.py", HERE / "data/referee-price.json", "price",
                      "--base-runtime", combined / "runtime", keys=("mode", "predecessor_runtime", "result"))
    check_json_output(HERE / "checks/actual_six_grant.py", HERE / "data/referee-six-grant.json",
                      "--base-runtime", combined / "runtime",
                      keys=("H", "L", "sender_band", "recipient_band", "r", "k", "source_level",
                            "recipient_level", "overlap", "precision_bits", "records"))
    check_json_output(HERE / "checks/all_stage_caps.py", HERE / "data/seven-stage.json")
    check_json_output(HERE / "checks/minimum_signed_invoice.py", HERE / "data/minimal-clock.json")
    rebuild_eight(tree, source)
    old = read_json(source / "source8073/RESULT.json")
    earlier = read_json(HERE / "data/8072-invoice.json")
    eight = read_json(HERE / "data/eight-column-invoice.json")
    table = read_json(HERE / "data/seven-stage.json")
    old_ceiling = Fraction(table["published_8073_family"]["three_stage_exact_stopped_supremum"])
    for candidate in (invoice, eight):
        require(Fraction(candidate["terminal"]["kappa"]) > old_ceiling,
                "candidate does not clear the pinned stopped ceiling")
        require(Fraction(candidate["terminal"]["kappa"]) < Fraction(39, 10000),
                "unexpected target crossing")
    require(invoice["complete_log2_C"] == 318291611 and old["complete_log2_C"] == 318291911
            and earlier["complete_log2_C"] == 318292011 and eight["complete_log2_C"] == 318291851,
            "complete clock comparison differs")


def calendar_checks(combined):
    base = combined / "runtime"
    six = combined / "successor/runtime"
    check_json_output(HERE / "checks/check_referee.py", HERE / "data/referee-events.json", "events",
                      "--base-runtime", base, "--six-runtime", six,
                      keys=("mode", "predecessor_runtime", "result"))


def run_addendum(tree):
    source = unpack_addendum(tree)
    comparison_path = tree / "cross-runtime.json"
    comparison_output = invoke(HERE / "checks/compare_cold_runtimes.py", "--predecessor-archive",
                               HERE / "source/six-column-8073-public.tar.gz", "--addendum-archive",
                               HERE / "source/six-column-8076-addendum.tar.gz", "--output", comparison_path)
    require(comparison_output.rstrip().endswith("PASS 105 of 106 runtime files; 84 of 88 peer files"),
            "cross-source comparison did not pass")
    comparison = read_json(comparison_path)
    require(comparison == read_json(source / "physical-equivalence.json")
            and comparison["runtime"]["identical_files"] == 105
            and comparison["peer"]["identical_files"] == 84,
            "cross-source comparison differs")
    out = tree / "addendum-receipt"
    output = invoke(source / "replay8076.py", "--predecessor-archive",
                    HERE / "source/six-column-8073-public.tar.gz", "--output", out,
                    "--scope", *ADDENDUM_SCOPES)
    require(output.rstrip().endswith("PASS 7 scopes"), "addendum scope output differs")
    receipt = read_json(out / "cold-result.json")
    require(receipt.get("pass") is True
            and receipt.get("source_head") == "d502eb21637717fe22fc16d4c4e3ede6ec59a106"
            and receipt.get("verified_addendum_files") == 30
            and receipt.get("pr8076_scientific_blobs") == 15
            and receipt.get("pr8057_peer_files") == 88
            and set(receipt.get("tested", {})) == set(ADDENDUM_SCOPES),
            "addendum receipt does not match the requested scopes")
    extras = {"source_invoice", "ordinary_tariff", "stage_caps"}
    records = {}
    for name in ADDENDUM_SCOPES:
        record = receipt["tested"][name]
        require(record.get("mode") == name and type(record.get("code")) is int and record["code"] == 0,
                "addendum scope failed or mislabeled: " + name)
        path = out / (name + ".out") if name in extras else out / "logs" / (name + ".out")
        require(record.get("output_sha256") == digest(path.read_bytes()),
                "addendum scope output digest mismatch: " + name)
        for field in ("started_at", "finished_at"):
            require(datetime.fromisoformat(record[field]).utcoffset() is not None,
                    "addendum scope receipt has no timezone: " + name)
        require(datetime.fromisoformat(record["started_at"]) <= datetime.fromisoformat(record["finished_at"]),
                "addendum timestamps out of order: " + name)
        records[name] = {key: record[key] for key in ("code", "started_at", "finished_at", "output_sha256")}
    source_invoice = read_json(out / "source_invoice.out")
    invoice = read_json(out / "logs/invoice.out")
    require(source_invoice == read_json(source / "source8076/RESULT.json")
            and invoice == read_json(source / "candidate-result.json"), "addendum invoice differs")
    require(Fraction(invoice["terminal"]["kappa"]) == Fraction(".003898226579820971")
            and Fraction(source_invoice["terminal"]["kappa"]) == Fraction(".003898223617430")
            and Fraction(invoice["terminal"]["kappa"]) > Fraction(invoice["previous_exact_ceiling"])
            and invoice["complete_log2_C"] == source_invoice["complete_log2_C"] == 318291900
            and invoice["entry_price_surcharge"] == 516
            and Fraction(invoice["ordinary_finite_debit"]) == Fraction(11178, 8192)
            and Fraction(invoice["gaussian"]["raw_loss"]) == Fraction(125645, 1048576),
            "addendum signed comparison differs")
    return records


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=(*SCOPES, "addendum"))
    mode = parser.parse_args().mode
    started = datetime.now(timezone.utc).isoformat()
    addendum_records = None
    with TemporaryDirectory(prefix="gaussian-suffix-") as tmp:
        tree = Path(tmp)
        source = unpack(tree)
        if mode == "addendum":
            records = run_addendum(tree)
        else:
            combined = compose(source)
            records = run_scopes(combined, SCOPES[mode])
            if mode == "price":
                price_checks(tree, source, combined)
                addendum_records = run_addendum(tree)
            elif mode == "calendar":
                calendar_checks(combined)
            elif mode == "setup":
                require(invoke(HERE / "checks/guard_controls.py").strip() == "PASS_ARCHIVE_AND_RECEIPT_GUARDS",
                        "archive and receipt controls did not pass")
    result = {"mode": mode, "started_at": started, "finished_at": datetime.now(timezone.utc).isoformat(),
              "archive_sha256": ARCHIVE_SHA256, "verified_scopes": records}
    if mode == "price":
        result["additional_checks"] = ["independent_integral_prices", "one_to_seven_stage_caps",
                                       "minimum_integer_invoice", "eight_column_signed_invoice",
                                       "actual_positive_grant", "8076_addendum_economics",
                                       "fresh_cross_source_runtime_comparison"]
        result["addendum_scopes"] = addendum_records
        result["addendum_not_run_by_this_mode"] = ["placement", "calendar", "ownership", "exterior", "nested",
                                                   "raw", "product", "stages", "ordinary_floor", "setup"]
    if mode == "calendar":
        result["additional_checks"] = ["literal_event_identity"]
    if mode == "setup":
        result["additional_checks"] = ["archive_and_receipt_guards"]
    if mode == "addendum":
        result["addendum_archive_sha256"] = ADDENDUM_SHA256
        result["additional_checks"] = ["fresh_cross_source_runtime_comparison"]
        result["not_run_by_this_mode"] = ["placement", "calendar", "ownership", "exterior", "nested",
                                          "raw", "product", "stages", "ordinary_floor", "setup"]
    print(json.dumps(result, indent=2))
    print("PASS_INTEGRATED_GAUSSIAN_" + mode.upper())


if __name__ == "__main__":
    main()
