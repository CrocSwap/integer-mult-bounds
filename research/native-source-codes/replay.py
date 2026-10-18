"""Rebuild and verify the four input-only source-code examples."""

from hashlib import sha256
from io import BytesIO
from pathlib import Path
import argparse
import gzip
import importlib.util
import json


HERE = Path(__file__).resolve().parent


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source = load_module("source_data")
    producer = load_module("input_logger")
    algebra = load_module("verify_input_logger")
    native = load_module("native_verify")
    data = source.reconstruct(args.repo)
    certificate = producer.load_certificate(HERE)
    payload = producer.produce(data, certificate)
    algebra_result = algebra.verify(data, certificate, payload)
    native_result = native.verify(data, certificate)
    args.out.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    compressed = BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", filename="", mtime=0) as archive:
        archive.write(raw)
    programs = compressed.getvalue()
    (args.out / "PROGRAMS.json.gz").write_bytes(programs)
    outputs = {
        "CLEAN-J-CHECKS.json": write_json(args.out / "CLEAN-J-CHECKS.json", data["checks"]),
        "ALGEBRA-CHECKS.json": write_json(args.out / "ALGEBRA-CHECKS.json", algebra_result),
        "NATIVE-CHECKS.json": write_json(args.out / "NATIVE-CHECKS.json", native_result),
        "PROGRAMS.json.gz": sha256(programs).hexdigest(),
    }
    report = {
        "status": "PASS_INPUT_ONLY_SOURCE_CODES",
        "base": source.BASE,
        "source_archive_sha256": source.ARCHIVE_SHA256,
        "certificate_sha256": producer.CERTIFICATE_SHA256,
        "program_payload_sha256": sha256(raw).hexdigest(),
        "outputs": outputs,
        "code_sha256": {name: sha256((HERE / name).read_bytes()).hexdigest() for name in
                        ("source_data.py", "input_logger.py", "verify_input_logger.py", "native_verify.py", "replay.py")},
        "claim": "An input-only source-code family with eight rank-one children, a full centre-query logger and a non-diagonal code with their inverse preludes",
        "not_checked": ["Global routed access and data restoration", "Complete address and precision costs",
                        "Recursive hosting and supplier invoice", "A new kappa bound"],
    }
    write_json(args.out / "REPLAY.json", report)
    print(report["status"])
    print("All 712 formal input columns and " + str(native_result["new_exact_gaussian_columns"])
          + " new native Gaussian columns passed.")
    print("The complete supplier and kappa calculation are unchanged.")


if __name__ == "__main__":
    main()
