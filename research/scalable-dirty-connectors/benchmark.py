"""Generate connector programs and run them through the packed C++ backend."""

import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
from time import perf_counter


HERE = Path(__file__).resolve().parent
CONNECTOR = HERE / "connector.py"


def load_connector():
    if not CONNECTOR.is_file():
        raise FileNotFoundError(f"connector source not found: {CONNECTOR}")
    spec = importlib.util.spec_from_file_location("scalable_dirty_connectors", CONNECTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load connector source: {CONNECTOR}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def serialize(operations):
    return "".join(f"{kind} {a} {b}\n" for kind, a, b in operations)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("n", type=int, choices=(6, 8), help="number of source rows")
    parser.add_argument("length", type=int, help="row width in bits, a positive multiple of 64")
    parser.add_argument("backend", type=Path, help="path to a compiled backend.cpp executable")
    parser.add_argument("--seed", type=int, help="deterministic fixture seed")
    parser.add_argument("--baseline", choices=("extra", "gray"), default="extra",
                        help="one-root comparator; extra keeps the same minimum B count")
    args = parser.parse_args()
    if args.length <= 0 or args.length % 64 or args.length > 65536:
        parser.error("row width must be a positive multiple of 64, at most 65536")
    backend = args.backend.expanduser().resolve()
    if not backend.is_file():
        parser.error(f"backend executable does not exist: {backend}")

    started = perf_counter()
    connector = load_connector()
    star = connector.star(args.n)
    baseline = (connector.extra_readout_baseline(args.n) if args.baseline == "extra"
                else connector.gray_baseline(args.n))
    star_payload = serialize(star.operations)
    baseline_payload = serialize(baseline.operations)
    with tempfile.TemporaryDirectory(prefix="scalable-dirty-connectors-") as temp_dir:
        temp = Path(temp_dir)
        star_path = temp / f"star{args.n}.ops"
        baseline_path = temp / f"{args.baseline}{args.n}.ops"
        star_path.write_text(star_payload)
        baseline_path.write_text(baseline_payload)
        elapsed_ms = (perf_counter() - started) * 1000
        print(
            f"PROGRAM_PREP n={args.n} elapsed_ms={elapsed_ms:.3f} "
            f"baseline={args.baseline} star_ops={len(star.operations)} baseline_ops={len(baseline.operations)} "
            f"star_event_file_bytes={len(star_payload)} "
            f"baseline_event_file_bytes={len(baseline_payload)}",
            flush=True,
        )
        command = [str(backend), str(args.n), str(args.length), str(star_path), str(baseline_path), args.baseline]
        if args.seed is not None:
            command.append(str(args.seed))
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
