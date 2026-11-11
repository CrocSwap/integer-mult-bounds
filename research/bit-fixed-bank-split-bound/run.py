"""Run the checkpointed BIT experiment under a subprocess watchdog."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from time import monotonic

ROOT = Path(__file__).resolve().parent


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dependency_root', type=Path)
    parser.add_argument('output_dir', type=Path)
    parser.add_argument('--adapter-root', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=120, choices=range(10, 121))
    args = parser.parse_args()
    start = monotonic()
    args.output_dir.mkdir()
    # Reserve two seconds for terminating the worker and recording status.
    soft_deadline = start + args.seconds - 2
    command = [
        sys.executable, '-I', '-B', str(ROOT/'worker.py'),
        str(args.dependency_root.resolve()), str(args.adapter_root.resolve()),
        str(args.output_dir.resolve()), str(soft_deadline-1),
    ]
    with (args.output_dir/'WORKER.stderr').open('wb') as err, (args.output_dir/'WORKER.stdout').open('wb') as out:
        try:
            exit_code = subprocess.run(
                command, stdout=out, stderr=err, timeout=max(0.01, soft_deadline-monotonic()),
            ).returncode
        except subprocess.TimeoutExpired:
            exit_code = 124
    elapsed = monotonic()-start
    result = {
        'elapsed_seconds': round(elapsed, 3), 'hard_cap_seconds': args.seconds,
        'worker_exit_code': exit_code, 'watchdog_triggered': exit_code == 124,
        'inventory_checkpoint': (args.output_dir/'INVENTORY.json').is_file(),
        'price_checkpoint': (args.output_dir/'PRICE.json').is_file(),
        'assignment_checkpoint': (args.output_dir/'SUPPORT.json').is_file(),
        'worker_summary': (args.output_dir/'DONE.json').is_file(),
    }
    assert elapsed < args.seconds, result
    (args.output_dir/'WATCHDOG.json').write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps(result, sort_keys=True))
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
