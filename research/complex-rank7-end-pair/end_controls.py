"""Reason-specific raw-auditor controls for both new dimension-seven ends.

Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


WORD_SHA = '096ed4abee4bb02c0d6f03bb8191510e57f6b1fcd34e8644f4fd336254e46411'
RECIPE = Path(__file__).resolve().parent / 'data/END-RECIPE.json'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def cases(word, recipe):
    result = []
    endpoint = dict(native='arbitrary-dirt endpoint', independent='all-column endpoint failure')
    nonmonotone = dict(native="'nonmonotone'", independent='frame not monotone')
    profile = dict(native='paid local profile differs from the reported local_profile',
                   independent='paid profile mismatch')

    def add(name, mutation, reasons):
        mutant = copy.deepcopy(word)
        mutation(mutant)
        result.append((name, mutant, reasons))

    def drop_gate(mutant, index):
        mutant['cleanup'].pop(index)
        mutant['early_cleanup'] = [[j - (j > index), frame]
                                   for j, frame in mutant['early_cleanup'] if j != index]

    tails = {word['cleanup'][cleanup_index][1]: (index, cleanup_index, old, new)
             for index, cleanup_index, old, new in recipe['early_cleanup']}
    require(set(tails) == {588, 589}, 'changed tail helpers')
    for q, old, new in recipe['ends']:
        index, cleanup_index, old_tail, new_tail = tails[q]
        require(word['helper_final'][str(q)] == new and word['early_cleanup'][index] ==
                [cleanup_index, new_tail], 'changed end and tail')
        add(f'end-{q}-other-dim7', lambda w: w['helper_final'].__setitem__(str(q), new[:-1] + [1]),
            dict(native='hpe cone pre-check (row / column)', independent='frame not monotone'))
        add(f'end-{q}-drop-cleanup-gate', lambda w: drop_gate(w, cleanup_index), endpoint)
        add(f'end-{q}-wrong-cleanup-coefficient',
            lambda w: w['cleanup'][cleanup_index].__setitem__(3, 2 * w['cleanup'][cleanup_index][3]), endpoint)
        add(f'end-{q}-cleanup-at-full', lambda w: w['early_cleanup'].pop(index),
            dict(native='cleanup on non-FULL end', independent='full cleanup reads a low end'))
        add(f'end-{q}-revert-tail-frame', lambda w: w['early_cleanup'][index].__setitem__(1, old_tail), nonmonotone)
        add(f'end-{q}-removed-end', lambda w: w['helper_final'].pop(str(q)), profile)
    for index, old, new in recipe['B_frames']:
        require(word['B'][index][-1] == new, 'changed B frame')
        reasons = nonmonotone if index in (1018, 1019, 1050, 1051) else profile
        add(f'B-{index}-omitted-lowering', lambda w: w['B'][index].__setitem__(-1, old), reasons)

    def false_profile(mutant):
        mutant['report']['local_profile']['1'] += 2
        mutant['report']['local_profile']['2'] -= 1

    def false_widths(mutant):
        mutant['report']['width_inventory']['7'] -= 1
        mutant['report']['width_inventory']['8'] += 1

    add('false-profile-same-rank-mass', false_profile, profile)
    # The independent raw auditor checks the reported width inventory.
    add('false-width-inventory', false_widths, dict(independent='width inventory mismatch'))
    require(len(result) == 22, 'targeted control count')
    return result


def run_check(args, name, checker, word, expected=None):
    payload = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
    with tempfile.TemporaryDirectory(prefix=f'{name}-{checker}-', dir=args.output) as temporary:
        root = Path(temporary)
        path = root / 'WORD.json.gz'
        path.write_bytes(gzip.compress(payload, compresslevel=9, mtime=0))
        command = [sys.executable, '-I', '-B']
        if checker == 'native':
            command += [str(args.portable_runner), str(args.native_auditor), '--raw', str(path),
                        '--routing', str(args.routing), '--out', str(root / 'native')]
            receipt = root / 'native/SCALAR-FRAME-AUDIT.json'
            error_type = 'AssertionError:'
            hash_key = 'input_content_sha256'
        else:
            receipt = root / 'independent.json'
            command += [str(args.independent_auditor), '--word', str(path), '--output', str(receipt)]
            if args.main is not None:
                command += ['--main', str(args.main)]
            error_type = 'RuntimeError:'
            hash_key = 'content_sha256'
        completed = subprocess.run(command, capture_output=True, text=True, timeout=120)
        log = completed.stdout + completed.stderr
        (args.output / f'{name}.{checker}.log').write_text(log, encoding='utf-8')
        if expected is None:
            require(completed.returncode == 0, f'{checker} rejected the positive control: {log[-1000:]}')
            result = json.loads(receipt.read_text(encoding='utf-8'))
            require(result[hash_key] == WORD_SHA, 'positive control content pin')
            return dict(checker=checker, accepted=True, status=result['status'])
        last_line = log.strip().splitlines()[-1] if log.strip() else ''
        require(completed.returncode == 1 and last_line.startswith(error_type) and expected in last_line,
                f'{name}: {checker} expected {expected!r}, got exit {completed.returncode}: {last_line}')
        return dict(checker=checker, rejected=last_line)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--recipe', type=Path, default=RECIPE)
    parser.add_argument('--independent-auditor', type=Path, required=True)
    parser.add_argument('--native-auditor', type=Path, required=True)
    parser.add_argument('--portable-runner', type=Path, required=True)
    parser.add_argument('--routing', type=Path, required=True)
    parser.add_argument('--main', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = gzip.decompress(args.word.read_bytes())
    require(hashlib.sha256(raw).hexdigest() == WORD_SHA, 'candidate content pin')
    recipe = json.loads(args.recipe.read_text(encoding='utf-8'))
    require(recipe['expected']['output_sha256'] == WORD_SHA, 'recipe output pin')
    word = json.loads(raw)
    args.output.mkdir(parents=True, exist_ok=True)
    positive = [run_check(args, 'positive', checker, word) for checker in ('native', 'independent')]
    rejected = []
    for name, mutant, reasons in cases(word, recipe):
        checks = [run_check(args, name, checker, mutant, expected) for checker, expected in reasons.items()]
        rejected.append(dict(name=name, checks=checks))
        print('rejected', name, flush=True)
    report = dict(status='PASS_DIMENSION_SEVEN_END_PAIR_RAW_CONTROLS', content_sha256=WORD_SHA,
                  checked_helpers=[588, 589], positive_controls=positive,
                  mutations=22, raw_rejections=sum(len(case['checks']) for case in rejected),
                  rejected_controls=rejected,
                  checker_sha256={name: hashlib.sha256(path.read_bytes()).hexdigest()
                                  for name, path in (('independent', args.independent_auditor),
                                                     ('native', args.native_auditor),
                                                     ('portable_runner', args.portable_runner))},
                  scope='Supplemental controls for both dimension-seven ends, both tail gates and frames, all eight B '
                        'lowerings, paid profiles, and reported widths. Inherited controls are counted separately.')
    (args.output / 'END-CONTROLS.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(report['status'], '22 mutants; 43 raw rejections', flush=True)


if __name__ == '__main__':
    main()
