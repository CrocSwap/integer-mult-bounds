"""Find small marker sets. This search is not an acceptance check.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import json
from pathlib import Path
import random
import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    verify.need(not args.output.exists(), 'Refuse to overwrite an existing file')
    a, operators, literal = verify.source_checks(verify.load())
    path, _ = verify.path_functions(operators, literal)
    rng = random.Random(5376)
    rows = []
    for count in (1, 2, 3, 4, 5, 6, 7, 8, 9, 18, 19, 32, 64):
        inputs = []
        for _ in range(16):
            inputs.append(rng.getrandbits(8*count+1))
            survivors, peak = verify.marker_path_count(a, operators, literal, path, count, inputs)
            if survivors == 1:
                break
        verify.need(survivors == 1, 'No marker certificate in the declared search budget')
        rows.append(dict(stages=count, markers=inputs, count=survivors, peak=peak))
    args.output.write_text(json.dumps(dict(seed=5376, candidates=rows), indent=2, sort_keys=True)+'\n')
    print('WROTE_MARKER_CANDIDATES')


if __name__ == '__main__':
    main()
