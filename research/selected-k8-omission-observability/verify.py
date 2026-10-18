#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact single-event observability of the selected k8 scalar program.

Prepared for Adam Gall with substantial OpenAI Codex assistance. This is a
separately implemented diagnostic, not a replacement for supplier admission.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/t16-owner-audit-seed67/inputs/k8-seven-slot-word.json.gz'
AUDITOR = 'research/gauge44-slots/independent/audit_local.py'
SLOT_PINS = 'research/gauge44-slots/construction/slots/SLOT-PINS-k8.json'
SELECTED_MANIFEST = 'research/community-frontier1094-audit/SELECTED-SOURCE.json'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def load_word(root=ROOT):
    sources = json.loads((HERE / 'SOURCES.json').read_bytes())
    for source in sources['files']:
        if source['usage'] != 'input':
            continue
        path = root / source['path']
        need(digest(path.read_bytes()) == source['sha256'], 'source pin: ' + source['path'])
    payload = gzip.decompress((root / WORD).read_bytes())
    pins = json.loads((root / SLOT_PINS).read_bytes())
    need(digest(payload) == pins['word_sha256'], 'selected slot word content')
    selected = json.loads((root / SELECTED_MANIFEST).read_bytes())['files']
    for path in (AUDITOR, SLOT_PINS, 'research/gauge44-slots/construction/slots/verify_slots.py'):
        need(digest((root / path).read_bytes()) == selected[path], 'selected manifest binding: ' + path)
    word = json.loads(payload)
    need((word['report']['v'], word['report']['R']) == (112, 480), 'selected dimensions')
    return word


def decode(raw, section, index):
    """A gate is (section, source index, destination, source-or-None, scalar)."""
    if raw[0] == 'add':
        _, dst, src, numerator, denominator, _ = raw
        need(dst != src, 'self addition')
    elif raw[0] == 'scale':
        _, dst, numerator, denominator, _ = raw
        src = None
    else:
        raise ValueError('unknown scalar primitive')
    scalar = Fraction(numerator, denominator)
    need(scalar != 0, 'zero scalar')
    return section, index, dst, src, scalar


def oriented(gate, dual):
    section, index, dst, src, scalar = gate
    if dual:
        if src is None:
            scalar = 1 / scalar
        else:
            dst, src, scalar = src, dst, -scalar
    return section, index, dst, src, scalar


def add_vector(dst, src, scalar):
    for column, value in src.items():
        total = dst.get(column, 0) + scalar * value
        if total:
            dst[column] = total
        else:
            dst.pop(column, None)


def advance(rows, gate):
    _, _, dst, src, scalar = gate
    if src is None:
        rows[dst] = {k: scalar * value for k, value in rows[dst].items()}
    else:
        add_vector(rows[dst], rows[src], scalar)


def identity(n):
    return [{i: Fraction(1)} for i in range(n)]


def program_from_word(word):
    """Derive entrance compensation from dirty-helper response, not a receipt."""
    v, n = word['report']['v'], 2 * word['report']['v'] + word['report']['R']
    sections = {name: [decode(raw, name, i) for i, raw in enumerate(word[name])]
                for name in ('precondition', 'A', 'cut', 'B', 'cleanup')}
    for section in sections.values():
        need(all(0 <= gate[2] < n and (gate[3] is None or 0 <= gate[3] < n)
                 for gate in section), 'register range')
    dirty = [{} if i < 2 * v else {i: Fraction(1)} for i in range(n)]
    for name in ('A', 'cut', 'B'):
        for gate in sections[name]:
            advance(dirty, gate)
    dirty = [row if v <= i < 2 * v else {} for i, row in enumerate(dirty)]
    for gate in sections['precondition']:
        advance(dirty, gate)
    compensation = []
    for dst in range(v, 2 * v):
        for src, scalar in sorted(dirty[dst].items()):
            compensation.append(('compensation', len(compensation), dst, src, -scalar))
    early = [entry[0] for entry in word['early_cleanup']]
    need(len(set(early)) == len(early) and all(0 <= i < len(sections['cleanup']) for i in early),
         'early cleanup indices')
    early_set = set(early)
    tail = [('early_cleanup', i, *sections['cleanup'][i][2:]) for i in early]
    cleanup = [gate for i, gate in enumerate(sections['cleanup']) if i not in early_set]
    return (sections['precondition'] + compensation + sections['A'] + sections['cut'] +
            sections['B'] + tail + cleanup)


def endpoint(n, v, dual):
    rows = identity(n)
    for i in range(v):
        rows[i if dual else v + i][v + i if dual else i] = Fraction(-1 if dual else 1)
    return rows


def support(row):
    return sum(1 << k for k in row)


def vector_record(row):
    return [[k, str(value)] for k, value in sorted(row.items())]


def scalar_replay(program, n, input_column, dual=False, omit=None):
    """Literal scalar execution on one basis input, independent of factorization."""
    values = [Fraction(int(i == input_column)) for i in range(n)]
    for i, gate in enumerate(program):
        if i == omit:
            continue
        _, _, dst, src, scalar = oriented(gate, dual)
        if src is None:
            values[dst] *= scalar
        else:
            values[dst] += scalar * values[src]
    return values


def census(program, n, v, dual=False, check_endpoint=True):
    """For P then gate G then S, omission defect is S(I-G)P, rank at most one."""
    gates = [oriented(gate, dual) for gate in program]
    rows = identity(n)
    right_factors = []
    right_hash = hashlib.sha256()
    for gate in gates:
        _, _, dst, src, _ = gate
        row = rows[dst if src is None else src]
        need(row, 'zero prefix row')
        column = min(row)
        right_factors.append((support(row), column, row[column]))
        right_hash.update(canonical(vector_record(row)) + b'\n')
        advance(rows, gate)
    if check_endpoint:
        need(rows == endpoint(n, v, dual), 'independent complete scalar endpoint')
    target_mask = ((1 << v) - 1) << (0 if dual else v)
    data_mask = (1 << (2 * v)) - 1
    source_mask = ((1 << v) - 1) << (v if dual else 0)
    columns = identity(n)
    counts = Counter()
    by_section = {}
    examples = {}
    left_hash = hashlib.sha256()
    for i in range(len(gates) - 1, -1, -1):
        section, index, dst, src, scalar = gates[i]
        left = columns[dst]
        right_mask, input_column, right_value = right_factors[i]
        left_mask = support(left)
        factor = 1 - scalar if src is None else -scalar
        labels = ['events', 'scale' if src is None else 'add']
        if factor:
            need(left, 'zero suffix column')
            labels.append('nonzero_defects')
            if not left_mask & target_mask:
                labels.append('target_invisible')
            if not left_mask & data_mask:
                labels.append('all_data_invisible')
            if not right_mask & data_mask:
                labels.append('clean_helpers_invisible')
            if not right_mask & source_mask:
                labels.append('source_only_invisible')
            if 'all_data_invisible' in labels and 'clean_helpers_invisible' in labels:
                labels.append('data_and_clean_helpers_invisible')
        else:
            labels.append('identity_omissions')
        counts.update(labels)
        by_section.setdefault(section, Counter()).update(labels)
        left_hash.update(canonical(vector_record(left)) + b'\n')
        for label in labels:
            if label in ('target_invisible', 'all_data_invisible', 'clean_helpers_invisible',
                         'data_and_clean_helpers_invisible'):
                delta = {k: factor * right_value * value for k, value in left.items()}
                examples[label] = dict(event=i, section=section, source_index=index,
                                       input_column=input_column, delta=vector_record(delta),
                                       output_support=left_mask.bit_count(),
                                       input_support=right_mask.bit_count())
                if label == 'data_and_clean_helpers_invisible' and section == 'cleanup':
                    examples['cleanup_data_and_clean_helpers_invisible'] = examples[label]
        # Right-multiply the current suffix by this event; matrices are stored as columns.
        if src is None:
            columns[dst] = {k: scalar * value for k, value in columns[dst].items()}
        else:
            add_vector(columns[src], columns[dst], scalar)
    transposed = [{j: rows[j][i] for j in range(n) if i in rows[j]} for i in range(n)]
    need(columns == transposed, 'prefix/suffix complete matrix disagreement')
    for example in examples.values():
        before = scalar_replay(program, n, example['input_column'], dual)
        after = scalar_replay(program, n, example['input_column'], dual, example['event'])
        observed = {k: b - a for k, (a, b) in enumerate(zip(before, after)) if a != b}
        need(vector_record(observed) == example['delta'], 'literal omission witness disagreement')
    return dict(counts=dict(sorted(counts.items())),
                sections={k: dict(sorted(value.items())) for k, value in sorted(by_section.items())},
                prefix_rows_sha256=right_hash.hexdigest(),
                suffix_columns_reverse_sha256=left_hash.hexdigest(), examples=examples)


def source_controls(word, program, result, root=ROOT):
    """Invoke the unmodified complete source auditor, not an extracted predicate."""
    examples = {name: result['examples'][name] for name in
                ('data_and_clean_helpers_invisible', 'cleanup_data_and_clean_helpers_invisible')}
    candidates = {'original': word}
    for name, example in examples.items():
        section, index = example['section'], example['source_index']
        need(section in ('A', 'B', 'cut', 'precondition', 'cleanup'), 'source fixture section')
        mutant = json.loads(json.dumps(word))
        del mutant[section][index]
        if section == 'cleanup':
            mutant['early_cleanup'] = [[j - int(j > index), frame]
                                       for j, frame in mutant['early_cleanup'] if j != index]
        mutated_program = program_from_word(mutant)
        expected_program = program[:example['event']] + program[example['event'] + 1:]
        # Source indices shift after deletion; mathematical primitive sequence must not.
        need([gate[2:] for gate in mutated_program] == [gate[2:] for gate in expected_program],
             'source mutation changed more than the omitted event')
        candidates[name] = mutant
    records = {}
    with tempfile.TemporaryDirectory(prefix='k8-omission-') as temp:
        temp = Path(temp)
        for name, candidate in candidates.items():
            input_path, output_path = temp / (name + '.json.gz'), temp / (name + '.receipt.json')
            input_path.write_bytes(gzip.compress(canonical(candidate), mtime=0))
            run = subprocess.run([sys.executable, '-I', '-O', '-B', str(root / AUDITOR),
                                  '--word', str(input_path), '--output', str(output_path)],
                                 capture_output=True, text=True, timeout=180)
            if name == 'original':
                need(run.returncode == 0 and output_path.is_file(), 'source positive control: ' + run.stderr)
                receipt = json.loads(output_path.read_bytes())
                need(receipt['checked_columns'] == 704, 'source complete input coverage')
                records[name] = dict(exit_code=run.returncode, status=receipt['status'],
                                     checked_columns=receipt['checked_columns'])
            else:
                failure = next((line for line in run.stderr.splitlines()
                                if line.startswith('RuntimeError: all-column endpoint failure ')), None)
                need(run.returncode != 0 and failure and not output_path.exists(),
                     'source must reject at full endpoint predicate: ' + run.stderr)
                example = examples[name]
                records[name] = dict(exit_code=run.returncode, failure=failure,
                                     section=example['section'], source_index=example['source_index'],
                                     scalar_event=example['event'])
    return records


def audit(root=ROOT):
    word = load_word(root)
    program = program_from_word(word)
    n, v = 704, 112
    forward = census(program, n, v)
    dual = census(program, n, v, dual=True)
    return dict(status='PASS_SELECTED_K8_OMISSION_OBSERVABILITY', registers=n,
                helpers=480, word_content_sha256=digest(gzip.decompress((root / WORD).read_bytes())),
                forward=forward, inverse_transpose=dual,
                source_controls=source_controls(word, program, forward, root),
                scope='Finite single scalar-event omissions only; no production bug, supplier change or new kappa.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='Write a new deterministic receipt; refuse an occupied path')
    args = parser.parse_args()
    if args.write:
        need(not args.write.exists(), 'receipt path already exists')
    result = audit()
    if args.write:
        with args.write.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        need(result == json.loads((HERE / 'EXPECTED.json').read_bytes()), 'expected receipt differs')
    print(result['status'])
    for name in ('forward', 'inverse_transpose'):
        print(name, json.dumps(result[name]['counts'], sort_keys=True))
    print('source_original=PASS source_omission=REJECTED no_new_kappa')


if __name__ == '__main__':
    main()
