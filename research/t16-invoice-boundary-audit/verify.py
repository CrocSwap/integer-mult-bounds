"""Replay real-file mutations against the unchanged selected T16 invoice.

Tairitsu-Aya, with substantial OpenAI Codex assistance. Apache-2.0.
Follows Josie Elliston's PR1959 invoice handoff. No frozen checker is patched.
"""
import argparse
import ast
from collections import Counter
import contextlib
import gzip
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import runpy
import sys
import tarfile
import tempfile
import traceback

from cases import build_cases, copy

if not __debug__:
    raise RuntimeError('Assertions must remain enabled')

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STAGE = ROOT / 'research/complex-t16-rare-pattern-exchanges'
ARCHIVE = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
ENGINES = ROOT / 'research/complex-k492-owner-repair/vendor/multicold'
RETAINED = ENGINES / 'vendor/pr558/vendor/pr552/complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json'
MEMBERS = {
    'code/invoice_allcold.py': '71eb57514e28ced97251e0507105f654f59885ec4d40486a780bf166098858a8',
    'code/assemble.py': '15f6986a476bac76bcdc0bfcf51da115389b46f1950d2766b6822f757888b13a',
    'code/audit_allcold.py': '1467a2acb654e62552c69fb9a7c4c85f70a02120881d222313865058ab71a6cc',
    'code/witness.py': '779c5172894b992131e85be1e592ed2a1aec8c287b872ff42007d36a7291e444',
    'code/generated_identity.py': 'c8af22719c0f3097a991a3f6ccac8f090afd2faba554745733d9ea88f2c25708',
    'verify_t16.py': '050e2dfba59911b8f29fd94422833d421367a0ad01c5e4ae916a75a235ee5e46',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def write(path, value):
    data = (json.dumps(value, indent=2) + '\n').encode('utf-8')
    path.write_bytes(gzip.compress(data, mtime=0, compresslevel=1) if path.suffix == '.gz' else data)


def normalized(value):
    return json.loads(json.dumps(value))


def quiet(call, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        return call(*args)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract(tmp):
    pins = [f for f in read(HERE / 'SOURCES.json')['files'] if f['usage'] == 'input']
    assert len(pins) == 9
    for item in pins:
        assert sha(ROOT / item['path']) == item['sha256'], 'Input changed: ' + item['path']
    source = tmp / 'source'
    source.mkdir()
    with tarfile.open(STAGE / 'upstream1087.tar.gz') as archive:
        for member in archive.getmembers():
            assert member.isfile() and (source / member.name).resolve().is_relative_to(source.resolve())
        archive.extractall(source, filter='data')
    for name in ('OWNERS.json.gz', 'PLAN.json', 'SPEC.json'):
        (source / 'data' / name).write_bytes((STAGE / 'data' / name).read_bytes())
    for name, expected in MEMBERS.items():
        assert sha(source / name) == expected, 'Frozen member changed: ' + name
    fixture = tmp / 'global'
    with tarfile.open(ARCHIVE) as archive:
        for member in archive.getmembers():
            prefix = 'candidate/strict/global/'
            if member.isfile() and member.name.startswith(prefix):
                target = fixture / member.name[len(prefix):]
                assert target.resolve().is_relative_to(fixture.resolve())
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(member).read())
        assembly = json.load(archive.extractfile('candidate/strict/ASSEMBLY.json'))
    return source, fixture, assembly


def rejection(error, sources):
    frames = [f for f in traceback.extract_tb(error.__traceback__)
              if Path(f.filename).name in sources]
    assert frames, 'Rejection outside the pinned checker: ' + repr(error)
    frame = frames[-1]
    result = dict(result='REJECTED', exception=type(error).__name__,
                  source=Path(frame.filename).name, line=frame.lineno,
                  statement=frame.line, message=str(error)[:500])
    tb = error.__traceback__
    while tb:
        if Path(tb.tb_frame.f_code.co_filename).name == 'invoice_allcold.py':
            values = tb.tb_frame.f_locals
            if 'inequalities' in values:
                result['inequalities'] = values['inequalities']
            for key in ('required_prefix', 'payload', 'row'):
                if key in values:
                    result[key] = values[key]
        tb = tb.tb_next
    return result


def finite_implications():
    """Check the integer bounds used in README's quantified implication proof."""
    compiler = 64 * 74**3
    stock_max = 2**4487 - 1
    mass_max = 73 * stock_max - 1
    logical_max = 2**6050 - 1
    total_max = mass_max + 2**100000
    bounds = dict(
        router=compiler * (logical_max + 1) * (stock_max + 1)**2,
        literal=2 * 2**30000 * stock_max**2 + 8 * mass_max + 4 * stock_max + 4 + 32 * 73,
        mass=total_max,
        precision=32 * 73 * total_max**2,
        tape=2 * total_max + 18,
    )
    powers = dict(router=15049, literal=38976, mass=100001, precision=200014, tape=100003)
    for name, bound in bounds.items():
        assert 0 < bound < 2**powers[name]
    assert 2 * stock_max.bit_length() + 11185 == 20159
    assert 2 * (stock_max + 1).bit_length() + 11185 == 20161
    assert compiler < 2**25
    return dict(hypotheses='Integer S>=1, 0<=M<73*S, 0<=L<2**6050, 2*bit_length(S)+11185<20161',
                stock_bit_limit=4487, strict_upper_bound_powers_of_two=powers)


def run(tmp):
    source, fixture, archived_assembly = extract(tmp)
    os.environ.update(WITNESS_SPEC=str(source / 'data/SPEC.json'),
                      GAIN_PR564_SOURCE=str(ENGINES), PYTHONINTMAXSTRDIGITS='0')
    for key in ('WITNESS_DISCOVER', 'WITNESS_RECORD'):
        os.environ.pop(key, None)
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    sys.path.insert(0, str(source / 'code'))
    invoice = load('frozen_invoice', source / 'code/invoice_allcold.py')
    assembly = load('frozen_assembly', source / 'code/assemble.py')
    retained = tmp / 'retained-invoice.json'
    retained.write_bytes(RETAINED.read_bytes())
    paths = dict(template=fixture / 'hosted/GLOBAL-TEMPLATE.json.gz',
                 summary=fixture / 'hosted/HOSTED.json',
                 owner=fixture / 'audit/OWNERS-AND-PROFILE.json',
                 controller=fixture / 'audit/ASYNC-AUDIT.json',
                 parent=fixture / 'base/split-centres/GLOBAL-TEMPLATE.json.gz',
                 programs=fixture / 'base/providers/gauge44/LOCAL-PROGRAMS.json.gz',
                 checks=fixture / 'base/providers/gauge44/LOCAL-CHECKS.json',
                 native=fixture / 'base/providers/gauge44/INDEPENDENT-LOCAL-REPLAY.json',
                 retained=retained)
    original = {key: path.read_bytes() for key, path in paths.items()}
    baseline = {key: read(path) for key, path in paths.items()}
    assert copy(baseline) == baseline
    archived_invoice = read(fixture / 'audit/PREFIX-AND-INVOICE.json')
    out = tmp / 'invoice'

    def calculate():
        return quiet(invoice.run, fixture / 'base', fixture / 'hosted', fixture / 'audit', out, retained)

    assert normalized(calculate()) == archived_invoice, 'Honest invoice does not reproduce'
    positive_assembly = normalized(quiet(assembly.assemble, baseline['owner'],
        read(out / 'PREFIX-AND-INVOICE.json'), sha(paths['owner']), sha(out / 'PREFIX-AND-INVOICE.json')))
    # Only the regenerated JSON container's hash can differ across newline conventions.
    assert positive_assembly['input_sha256']['fresh_invoice'] == sha(out / 'PREFIX-AND-INVOICE.json')
    positive_assembly['input_sha256']['fresh_invoice'] = archived_assembly['input_sha256']['fresh_invoice']
    assert positive_assembly == archived_assembly, 'Honest assembly does not reproduce'

    argv = sys.argv
    report = tmp / 'controller-positive/ASYNC-AUDIT.json'
    sys.argv = [str(source / 'code/audit_allcold.py'), str(fixture / 'base'),
                str(fixture / 'hosted'), str(report)]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            controller = runpy.run_path(str(source / 'code/audit_allcold.py'), run_name='__main__')
    finally:
        sys.argv = argv
    ignored = {'mutation_controls_run', 'mutations_rejected'}
    fresh = read(report)
    assert fresh['mutation_controls_run'] is False and fresh['mutations_rejected'] == []
    assert {k:v for k,v in fresh.items() if k not in ignored} == {
        k:v for k,v in baseline['controller'].items() if k not in ignored}

    # Execute this one original final-binding predicate separately; do not call
    # it a replay of verify_t16.py or of its producer stages.
    driver = source / 'verify_t16.py'
    node, = [n for n in ast.parse(driver.read_text()).body if isinstance(n, ast.Assert) and n.lineno == 103]
    driver_predicate = compile(ast.Module(body=[node], type_ignores=[]), str(driver), 'exec')
    exec(driver_predicate, {'audit': baseline['controller']})
    retained_pin = read(source / 'data/UPSTREAM-PINS.json')[RETAINED.relative_to(ROOT).as_posix()]
    assert retained_pin == sha(RETAINED)

    results = []
    for name, mutate, rebind in build_cases(baseline, archived_invoice, invoice):
        data = copy(baseline)
        mutate(data)
        changed = [key for key in paths if data[key] != baseline[key]]
        assert changed, 'No-op mutant: ' + name
        result = dict(name=name, changed_inputs=changed, links_rebound=rebind)
        try:
            for key in changed:
                write(paths[key], data[key])
            if 'programs' in changed:
                program_sha = sha(paths['programs'])
                data['native']['local_programs_sha256'] = program_sha
                write(paths['native'], data['native'])
                data['template']['local_providers']['gauge44']['local_programs_sha256'] = program_sha
                write(paths['template'], data['template'])
                for key in ('programs', 'checks', 'native'):
                    artifact = 'providers/gauge44/' + paths[key].name
                    for receipt in ('owner', 'summary'):
                        data[receipt]['source_artifacts'][artifact] = sha(paths[key])
            if rebind and 'template' in changed:
                digest = invoice.contenthash(paths['template'])
                data['summary']['template_sha256'] = digest
                data['owner']['template_sha256'] = digest
                data['controller']['template_sha256'] = digest
                data['controller']['complex_template_sha256'] = digest
                for key in ('summary', 'controller'):
                    write(paths[key], data[key])
            if rebind:
                data['owner']['controller_audit_sha256'] = sha(paths['controller'])
                write(paths['owner'], data['owner'])
            try:
                output = calculate()
            except Exception as error:
                result['invoice'] = rejection(error, {'invoice_allcold.py', 'witness.py'})
                output = None
            if output is not None:
                result['invoice'] = dict(result='ACCEPTED',
                    changed_keys=[k for k in output if normalized(output[k]) != archived_invoice.get(k)],
                    pervertex_bits=output['conservative_pervertex_used'].bit_length(),
                    prefix_bits=output['global_prefix_bits'], finite=output['finite'])
                if output['conservative_pervertex_used'].bit_length() <= 64:
                    result['invoice']['pervertex'] = output['conservative_pervertex_used']
                try:
                    assembled = quiet(assembly.assemble, read(paths['owner']),
                                      read(out / 'PREFIX-AND-INVOICE.json'),
                                      sha(paths['owner']), sha(out / 'PREFIX-AND-INVOICE.json'))
                    result['assembly'] = dict(result='ACCEPTED', kappa=assembled['kappa'])
                except Exception as error:
                    result['assembly'] = rejection(error, {'assemble.py', 'witness.py'})
            if 'template' in changed and 'parent' not in changed and 'programs' not in changed:
                try:
                    controller['audit'](read(paths['template']))
                    result['upstream_controller'] = dict(result='ACCEPTED')
                except Exception as error:
                    result['upstream_controller'] = rejection(error, {'audit_allcold.py'})
            if name in ('controller mutations flag false', 'controller mutation list empty'):
                try:
                    exec(driver_predicate, {'audit': read(paths['controller'])})
                    result['isolated_driver_predicate'] = dict(result='ACCEPTED')
                except AssertionError as error:
                    result['isolated_driver_predicate'] = rejection(error, {'verify_t16.py'})
            if 'retained' in changed:
                result['changed_retained_bytes_fail_upstream_pin'] = sha(paths['retained']) != retained_pin
            results.append(result)
        finally:
            for key, path in paths.items():
                path.write_bytes(original[key])
        print(len(results), name, result['invoice']['result'], flush=True)

    assert all(path.read_bytes() == original[key] for key, path in paths.items())
    assert normalized(calculate()) == archived_invoice, 'Original fixture was not restored'
    counts = Counter(row['invoice']['result'] for row in results)
    downstream = Counter(row['assembly']['result'] for row in results if 'assembly' in row)
    return dict(status='PASS_T16_INVOICE_BOUNDARY_AUDIT', member_sha256=MEMBERS,
                positive=dict(invoice_all_fields_equal=True, assembly_all_proof_fields_equal=True,
                              assembly_only_normalized_field='input_sha256.fresh_invoice',
                              controller_equal_except_mutation_run_fields=True,
                              kappa=archived_assembly['kappa'], prefix_bits=archived_invoice['global_prefix_bits'],
                              physical_row_coefficient=archived_invoice['finite']['physical_row_coefficient']),
                summary=dict(cases=len(results), invoice=dict(counts), assembly=dict(downstream)),
                finite_implications=finite_implications(), cases=results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Regenerate EXPECTED.json')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='t16-invoice-audit-') as directory:
        actual = run(Path(directory))
    payload = json.dumps(actual, indent=2, ensure_ascii=False) + '\n'
    expected = HERE / 'EXPECTED.json'
    if args.write:
        expected.write_text(payload, encoding='utf-8', newline='\n')
    else:
        assert actual == read(expected), 'Receipt differs from EXPECTED.json'
    print(actual['status'], json.dumps(actual['summary'], sort_keys=True))


if __name__ == '__main__':
    main()
