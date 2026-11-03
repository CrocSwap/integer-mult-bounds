"""Receipt adapter for the independently frozen39 loader controls."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(1, str(Path(__file__).resolve().parent.parent / 'loader'))
from custody import need, write_json
import frozen_input_controls


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-root', required=True)
    parser.add_argument('--receipt', required=True)
    args = parser.parse_args()
    Path(args.output_root).mkdir(mode=0o700)
    result = frozen_input_controls.run_controls()
    need(result['status'] == 'LOADER_CONTROLS_PASS' and result['count'] == 39, 'loader controls mismatch')
    write_json(Path(args.receipt), result)


if __name__ == '__main__':
    main()
