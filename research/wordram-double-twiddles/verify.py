"""Fixed-template, full-memory corroboration of constant-two specialization.

Executes the authenticated original builder/ISA and credited unit transformer.
It does not import the predecessor verifier or re-prove its supplier premises.
"""
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
PACKAGE = Path(__file__).resolve().parent
MANIFEST_SHA = 'ff4abac9cb7044059e6b324a0aab89c012866d94fe67bc05597c0bdf5618d899'
PINNED = {
    'vendor/PR6802-PROOF.md': (6396, 'dce63dfbf52a1da9b9218878d2d03bfb31d4c3e11aad99cd7edfcc637bcf1946', '9467bc69fb8ad0316257faa33cf0c4dfe72dc97d'),
    'vendor/PR6802-README.md': (7151, 'de6cea5553b5d2e3b22d420e57e8bbbbdb624d1edd625b202bfd9675a15f5f85', '1088fab13c773b5afced478d56d78d20f557aa4e'),
    'vendor/source/NOTICE.txt': (529, 'c7a35a43ceeca4d0b820c00e5b3c589d119033748a46de91769f284e869ac33b', 'b0dc94cb9d5ed24d2ebddc2eae0f41792a2abe69'),
    'vendor/source/PROOF.txt': (8908, 'f1d6549b55337e6704b575806fb6be6cec8bbc9a761a6bf3a320aec40cbee9df', 'd0d0d6486e833fb4711fcdd22a5aaa1853815189'),
    'vendor/source/ntt/exact_ntt.py': (5471, 'b512200d63c736c5d347247028eb1b1f3431cea44aba01c86f2772910d6b41bf', '5982128975472dfeb472dbe848c5d3617076662b'),
    'vendor/source/ram/PROOFS.txt': (8926, 'e62d76c0caaa4e24651d2282a7a19cb935c63e16932c90a14cb74182d3934df8', '21907aa9c4aa4c135a49ff5652bbfa08e722b757'),
    'vendor/source/ram/wordram_kernel.py': (5888, 'b1a6133e505e5faf5832a5274eea23f96b033257c3d16cc24479c4a4c7059a2e', 'f5c6e00699db701f02c23c0d776f6db9d8a28854'),
    'vendor/source/ram_multiplier.py': (4604, '6c3ae23ad90c92741f5a505ae9dd85a4bbaaafb72ebdf50291e07d1ae4c52476', '09ca74343b741af876043059d0cd0d1db8b393ed'),
    'vendor/unit_refine.py': (3445, '5c62f1d7ed451ff7b86172bbe37686975b2a96cfac18b66c5e42acc3bdf1a60a', '1a0aeb321407517ea0636fc895eb84dceef81248'),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON object key')
        result[key] = value
    return result


def no_number(text):
    raise ValueError('noninteger JSON number: ' + text)


def authenticate():
    raw = (PACKAGE / 'SOURCE-PINS.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA, 'source manifest bytes')
    manifest = json.loads(raw, object_pairs_hook=unique, parse_float=no_number, parse_constant=no_number)
    require(type(manifest['schema_version']) is int and manifest['schema_version'] == 1, 'source version')
    require(len(manifest['files']) == 9, 'source inventory size')
    require({row['local_path'] for row in manifest['files']} == set(PINNED), 'source inventory paths')
    for row in manifest['files']:
        path = PACKAGE / row['local_path']
        require(path.is_file() and not path.is_symlink(), 'source regular file')
        data = path.read_bytes()
        actual = (len(data), hashlib.sha256(data).hexdigest(),
                  hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest())
        require(actual == PINNED[row['local_path']], 'source bytes: ' + row['local_path'])
        require(actual == (row['bytes'], row['sha256'], row['git_blob'])
                and row['mode'] == '100644', 'source pin fields')
    return len(manifest['files'])


def load_models():
    # All nine source bodies and their manifest are authenticated first.
    sys.path.insert(0, str(PACKAGE))
    import refine as double
    sys.path.insert(0, str(PACKAGE / 'vendor'))
    import unit_refine as unit
    sys.path.insert(0, str(PACKAGE / 'vendor' / 'source'))
    import ram_multiplier as producer
    from ram import wordram_kernel as kernel
    from ntt import exact_ntt as ntt
    locations = ((double, PACKAGE / 'refine.py'),
                 (unit, PACKAGE / 'vendor' / 'unit_refine.py'),
                 (producer, PACKAGE / 'vendor/source/ram_multiplier.py'),
                 (kernel, PACKAGE / 'vendor/source/ram/wordram_kernel.py'),
                 (ntt, PACKAGE / 'vendor/source/ntt/exact_ntt.py'))
    for module, expected in locations:
        require(Path(module.__file__).resolve() == expected.resolve(), 'imported model path')
    return producer, kernel, unit, double


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


def local_program(kernel, coefficient=2):
    builder = kernel.Builder()
    builder.setup()
    builder.literal(100, coefficient)
    start = len(builder.code)
    builder._mul(101, 100, kernel.VALUE)
    stop = len(builder.code)
    builder.emit('sub', 100, 100, 100)
    builder.accept()
    return builder.program(), start, stop


def accepted(kernel, program, memory):
    result = kernel.run(program, memory)
    require(result is not None and result.accepted, 'literal execution did not accept within budget')
    return result


def local_checks(kernel, double):
    old, start, stop = local_program(kernel)
    compiled = double.refine(old)
    require(len(compiled.replacements) == 1 and compiled.replacements[0][0] == start, 'one local site')
    new = compiled.program
    require(len(old) - len(new) == 45, 'local static saving')
    transcript = hashlib.sha256()
    for value in range(double.P):
        dirty = {cell: (kernel.MASK - cell) & kernel.MASK for cell in kernel.SCRATCH}
        dirty.update({101: value, 100: kernel.MASK - value, kernel.VALUE: kernel.MASK,
                      kernel.TEMP: value ^ 0x1555, -77: value + 4, 777777: kernel.MASK - 9})
        before, after = accepted(kernel, old, dirty), accepted(kernel, new, dirty)
        require(before.memory == after.memory, 'local complete memory')
        require(before.writes == after.writes, 'local write frame')
        require(before.steps - after.steps == 30, 'local executed saving')
        require(after.memory[kernel.VALUE] == (2 * value) % double.P, 'local value oracle')
        require(after.memory[kernel.TEMP] == (2 * value - double.P) & kernel.MASK, 'local TEMP oracle')
        transcript.update((str(value) + ':' + str(before.steps) + ':' + str(after.steps) + '\n').encode())
    return dict(residues=double.P, static_saving=45, executed_saving=30,
                transcript_sha256=transcript.hexdigest()), old, new, start, stop


def source_site_metadata(plan, double):
    lifetimes = double.double_lifetimes(plan.program)
    sites, ordinal = {}, 0
    per_transform = plan.butterflies // 3
    require(plan.butterflies % 3 == 0 and per_transform > 0, 'three fused transform domains')
    names = ('forward_left', 'forward_right', 'inverse_products')
    for pc, instruction in enumerate(plan.program):
        if instruction[0] != 'mul' or instruction[1] != double.VALUE:
            continue
        if instruction[3] in lifetimes:
            within = ordinal % per_transform
            stage = within // (plan.n // 2)
            width = 1 << (stage + 1)
            position = within % (plan.n // 2)
            require(ordinal // per_transform < 3, 'transform ordinal')
            sites[pc] = dict(original_pc=pc, direction=names[ordinal // per_transform],
                             stage_width=width, block=position // (width // 2),
                             twiddle_exponent=position % (width // 2),
                             coefficient_cell=instruction[3], data_cell=instruction[2])
        ordinal += 1
    require(ordinal == plan.butterflies, 'source VALUE-multiply/butterfly correspondence')
    require(sites, 'actual constant-two butterfly presence')
    return sites


def compile_fixed(producer, kernel, unit, double):
    plan = producer.build_multiplier(256, 256, fused=True)
    require(plan.n == 512 and plan.fused, 'fixed template')
    original_static, original_sha = len(plan.program), digest(plan.program)
    original_sites = source_site_metadata(plan, double)
    unit_result = unit.refine(plan.program)
    baseline = unit_result.program
    unit_count = len(unit_result.replacements)
    sites = {unit_result.old_to_new[pc]: data for pc, data in original_sites.items()}
    require(unit_count == 3 * (plan.n - 1), 'credited unit site census')
    plan.program = []  # Release the original list before another full relocation map.
    del unit_result
    baseline_sha = digest(baseline)
    compiled = double.refine(baseline)
    require({row[0] for row in compiled.replacements} == set(sites), 'all and only source double sites')
    lifetimes = double.double_lifetimes(baseline)
    records = []
    for pc, coefficient, data in compiled.replacements:
        require(sites[pc]['coefficient_cell'] == coefficient and sites[pc]['data_cell'] == data, 'site operands')
        records.append(dict(sites[pc], baseline_pc=pc, new_pc=compiled.old_to_new[pc],
                            coefficient_lifetime=list(lifetimes[coefficient])))
    new = compiled.program
    del compiled
    count = len(records)
    require(len(baseline) - len(new) == 45 * count, 'whole static saving')
    profile = dict(lengths=[256, 256], n=512, fused=True, original_static=original_static,
                   original_program_sha256=original_sha, baseline_static=len(baseline),
                   baseline_program_sha256=baseline_sha, new_static=len(new),
                   new_program_sha256=digest(new), replacements=records,
                   replacement_count=count, new_static_saving=45 * count,
                   new_executed_saving=30 * count,
                   credited_unit_sites=unit_count, credited_unit_executed_saving=31 * unit_count)
    return plan, baseline, new, profile


def evaluate(digits):
    value = 0
    for digit in reversed(digits):
        value = 16 * value + digit
    return value


def whole_checks(plan, baseline, new, kernel, replacement_count):
    zero, maximum = [0] * 256, [15] * 256
    fixtures = [('zero', zero, zero), ('maximum', maximum, maximum),
                ('pattern', [(3 * i + 1) % 16 for i in range(256)],
                 [(5 * i + 2) % 16 for i in range(256)])]
    allowed = plan.temporaries | kernel.SCRATCH | set(plan.output)
    rows = []
    for name, left, right in fixtures:
        memory = {cell: (kernel.MASK - cell) & kernel.MASK for cell in allowed}
        memory.update(zip(plan.left, left))
        memory.update(zip(plan.right, right))
        memory.update({-77: kernel.MASK, 777777: 123456})
        before, after = accepted(kernel, baseline, memory), accepted(kernel, new, memory)
        require(before.memory == after.memory, 'whole complete memory: ' + name)
        require(before.writes == after.writes and after.writes <= allowed, 'whole write frame')
        require(before.steps - after.steps == 30 * replacement_count, 'whole executed saving')
        digits = [after.memory[cell] for cell in plan.output]
        require(all(type(x) is int and 0 <= x < 16 for x in digits), 'output digits')
        require(evaluate(digits) == evaluate(left) * evaluate(right), 'whole multiplication oracle')
        require(all(after.memory[cell] == 0 for cell in plan.temporaries | kernel.SCRATCH), 'whole cleanup')
        require(all(after.memory.get(cell, 0) == value for cell, value in memory.items()
                    if cell not in allowed), 'operands/exterior preservation')
        rows.append(dict(fixture=name, baseline_steps=before.steps, new_steps=after.steps,
                         executed_saving=before.steps - after.steps, output_sha256=digest(digits),
                         complete_memory_sha256=digest(sorted(after.memory.items())),
                         writes_sha256=digest(sorted(after.writes))))
    return rows


def rejected(double, name, program, expected):
    try:
        double.refine(program)
    except ValueError as error:
        require(str(error) == expected, 'wrong structural failure: ' + name + ': ' + str(error))
        return dict(name=name, outcome='REJECTED', reason=str(error))
    raise ValueError('structural mutation accepted: ' + name)


def structural_controls(kernel, double, old, start):
    wrong_value, _, _ = local_program(kernel, 3)
    controls = [rejected(double, 'literal_three_not_two', wrong_value, 'no constant-two sites')]
    mutation = old.copy()
    mutation[-2] = ('sub', 100, double.ZERO, double.ZERO)
    controls.append(rejected(double, 'missing_self_clear_lifetime', mutation, 'no constant-two sites'))
    mutation = old.copy()
    mutation[start + 1] = ('sub', double.TEMP, double.VALUE, 20)
    controls.append(rejected(double, 'wrong_threshold', mutation, 'generic reduction macro'))
    mutation = old.copy()
    mutation[start + 2] = ('bltz', double.TEMP, start + 5)
    controls.append(rejected(double, 'wrong_internal_branch', mutation, 'generic reduction macro'))
    mutation = old.copy()
    mutation[0] = ('bltz', 101, start + 1)
    controls.append(rejected(double, 'exterior_branch_into_removed_interior', mutation, 'branch into removed macro'))
    mutation = old.copy()
    mutation[start] = ('mul', double.VALUE, double.TEMP, 100)
    controls.append(rejected(double, 'data_scratch_alias', mutation, 'data/coefficient ABI'))
    return controls


def semantic_controls(kernel, double, old, new, start, stop):
    memory = {101: 0, 100: 999, double.VALUE: 42, double.TEMP: 17, -77: 123}
    omitted = old[:start] + [old[start]] + old[stop:]
    before, after = accepted(kernel, old, memory), accepted(kernel, omitted, memory)
    require(before.memory[double.VALUE] == after.memory[double.VALUE] == 0, 'TEMP-control payload')
    require(before.memory[double.TEMP] != after.memory[double.TEMP], 'TEMP omission not detected')
    first = dict(name='omit_TEMP_effect', outcome='DETECTED_COMPLETE_MEMORY_DIFFERENCE',
                 witness=dict(residue=0, value=0, expected_TEMP=before.memory[double.TEMP],
                              actual_TEMP=after.memory[double.TEMP]))
    memory[101] = double.P  # Deliberately outside the inherited residue premise.
    before, after = accepted(kernel, old, memory), accepted(kernel, new, memory)
    require(before.memory[double.VALUE] == 0 and after.memory[double.VALUE] == double.P,
            'out-of-domain control did not distinguish endpoints')
    second = dict(name='outside_residue_domain', outcome='DETECTED_DIFFERENCE_OUTSIDE_PREMISE',
                  witness=dict(input=double.P, permitted=[0, double.P - 1],
                               generic_value=before.memory[double.VALUE],
                               short_value=after.memory[double.VALUE],
                               generic_TEMP=before.memory[double.TEMP], short_TEMP=after.memory[double.TEMP]))
    return [first, second]


def package_hashes():
    hashes = {}
    for path in sorted(PACKAGE.rglob('*')):
        require(not path.is_symlink(), 'package symlink')
        if path.is_file():
            hashes[path.relative_to(PACKAGE).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    require(len(sys.argv) == 1, 'no command-line arguments supported')
    source_count = authenticate()
    producer, kernel, unit, double = load_models()
    local, old_local, new_local, start, stop = local_checks(kernel, double)
    faults = structural_controls(kernel, double, old_local, start)
    faults += semantic_controls(kernel, double, old_local, new_local, start, stop)
    del old_local, new_local
    plan, baseline, new, profile = compile_fixed(producer, kernel, unit, double)
    whole = whole_checks(plan, baseline, new, kernel, profile['replacement_count'])
    packet = dict(status='PASS_WORDRAM_DOUBLE_TWIDDLES', schema_version=1,
                  scope='fixed 512-point fused post-unit constant-two full-memory refinement',
                  authenticated_vendor_inputs=source_count, local=local, template=profile,
                  whole_cases=whole, control_count=len(faults), controls=faults,
                  source_execution=['original Builder and build_multiplier', 'original literal ISA run',
                                    'credited PR6802 unit_refine.refine'],
                  predecessor_verifier_executed=False, all_length_pairs_exhausted=False,
                  package_sha256=package_hashes())
    print(json.dumps(packet, sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, ImportError, json.JSONDecodeError) as error:
        print('FAIL_WORDRAM_DOUBLE_TWIDDLES: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
