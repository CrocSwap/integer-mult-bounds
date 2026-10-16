"""Read-only default replay of the complete routed observation certificate."""
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit import run, need


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true', help='create a new receipt, refusing overwrite')
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result, sort_keys=True, separators=(',', ':'), allow_nan=False)
    path = Path(__file__).with_name('RESULT.json')
    if args.write_result:
        with path.open('x', encoding='utf-8', newline='\n') as output:
            json.dump(result, output, indent=2, sort_keys=True, allow_nan=False)
            output.write('\n')
    else:
        expected = json.loads(path.read_text(encoding='utf-8'))
        need(encoded == json.dumps(expected, sort_keys=True, separators=(',', ':'), allow_nan=False),
             'complete committed receipt mismatch')
    print('PASS_QQ16_SIXTEEN_RECORD_CUT retained=16 live=208 arrays=224 native_columns=16384 controls=10')


if __name__ == '__main__':
    main()
