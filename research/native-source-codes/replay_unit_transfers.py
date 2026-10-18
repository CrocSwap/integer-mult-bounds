"""Replay the published examples and the two finite-order unit transfers."""

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
    source, original, algebra, native, producer, verifier = [load_module(name) for name in
        ("source_data", "input_logger", "verify_input_logger", "native_verify", "unit_transfer", "verify_unit_transfer")]
    data = source.reconstruct(args.repo)
    certificate = original.load_certificate(HERE)
    extension = producer.load_certificate(HERE)
    original_payload = original.produce(data, certificate)
    original_checks = algebra.verify(data, certificate, original_payload)
    native_checks = native.verify(data, certificate)
    payload = producer.produce(data, certificate, original)
    checks = verifier.verify(data, certificate, extension, payload, algebra, native)
    args.out.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    compressed = BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", filename="", mtime=0) as archive:
        archive.write(raw)
    programs = compressed.getvalue()
    (args.out / "UNIT-TRANSFER-PROGRAMS.json.gz").write_bytes(programs)
    outputs = {
        "CLEAN-J-CHECKS.json": write_json(args.out / "CLEAN-J-CHECKS.json", data["checks"]),
        "PUBLISHED-EXAMPLE-CHECKS.json": write_json(args.out / "PUBLISHED-EXAMPLE-CHECKS.json", original_checks),
        "PUBLISHED-NATIVE-CHECKS.json": write_json(args.out / "PUBLISHED-NATIVE-CHECKS.json", native_checks),
        "UNIT-TRANSFER-CHECKS.json": write_json(args.out / "UNIT-TRANSFER-CHECKS.json", checks),
        "UNIT-TRANSFER-PROGRAMS.json.gz": sha256(programs).hexdigest(),
    }
    code_files = ("source_data.py", "input_logger.py", "verify_input_logger.py", "native_verify.py", "replay.py",
                  "unit_transfer.py", "verify_unit_transfer.py", "replay_unit_transfers.py")
    report = {"status": "PASS_UNIT_TRANSFER_EXTENSION", "base": source.BASE,
              "published_source_commit": extension["published_source_commit"],
              "source_archive_sha256": source.ARCHIVE_SHA256,
              "original_certificate_sha256": original.CERTIFICATE_SHA256,
              "extension_certificate_sha256": producer.CERTIFICATE_SHA256,
              "published_program_payload_sha256": sha256(json.dumps(original_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
              "unit_transfer_program_payload_sha256": sha256(raw).hexdigest(), "outputs": outputs,
              "code_sha256": {name: sha256((HERE / name).read_bytes()).hexdigest() for name in code_files},
              "claim": "Exact local B/F unit-transfer companions with an order-six source code; all four published source-code examples remain verified",
              "not_checked": ["Changing routed charts and global controller closure", "Final source decoding",
                              "Complete address, precision, storage and child-hosting costs", "A new supplier or kappa bound"]}
    write_json(args.out / "UNIT-TRANSFER-REPLAY.json", report)
    print(report["status"])
    print("Four published examples and both unit transfers passed all 712 formal input columns.")
    print("The eight positive and eight inverse native recipes passed all 8192 Gaussian columns.")
    print("The complete supplier and kappa calculation are unchanged.")


if __name__ == "__main__":
    main()
