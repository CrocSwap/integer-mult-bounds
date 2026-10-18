#!/usr/bin/env python3
"""Audit omitted evidence in the pinned PR741 composition binding.

Lucas (@ljste), with substantial OpenAI Codex assistance. Apache-2.0.
This replays archived finite evidence, not the multiplication construction.
"""
import argparse
import ast
from collections.abc import Callable
from functools import partial
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import Literal, Protocol, TypedDict, cast

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / 'research/community-frontier741-audit/composed-replay-evidence.tar.gz'
PRODUCER = ROOT / 'research/complex-sw4-frame8/verify.py'
BASE_COMMIT = '7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261'
SEED = 72


class Stage(TypedDict):
    name: str
    exit_code: int
    seconds: float
    log_sha256: str


class Receipt(TypedDict):
    status: str
    manifest_sha256: str
    spec_sha256: str
    stages: list[Stage]
    artifacts: dict[str, str]


class Coverage(TypedDict):
    stages: list[str]
    artifacts: list[str]


class SourcePin(TypedDict):
    sha256: str
    git_blob: str
    role: Literal['runtime', 'base-selection-context']


class Binding(Protocol):

    def check(self, bit: Path, complex_dir: Path) -> dict[str, object]: ...


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_json(path: Path) -> object:
    return json.loads(path.read_bytes())


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def read_receipt(directory: Path) -> Receipt:
    return cast(Receipt, read_json(directory / 'RECEIPT.json'))


def check_sources() -> dict[str, SourcePin]:
    sources = cast(dict[str, SourcePin], read_json(HERE / 'SOURCES.json'))
    for relative, pin in sources.items():
        require(pin['role'] in {'runtime', 'base-selection-context'}, 'Unknown source role: ' + relative)
        if pin['role'] == 'runtime':
            require(digest(ROOT / relative) == pin['sha256'], 'Audited source changed: ' + relative)
        else:
            require(relative == 'certificates/selected-result.json', 'Unexpected selection context')
    return sources


def load_binding() -> Binding:
    spec = importlib.util.spec_from_file_location(
        'audited_frontier741_binding', ROOT / 'scripts/verify_frontier741_bindings.py')
    if spec is None or spec.loader is None:
        raise ValueError('Cannot load pinned binding')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cast(Binding, module)


def extract_evidence(destination: Path) -> None:
    with tarfile.open(ARCHIVE) as archive:
        for member in archive:
            require(member.isfile() or member.isdir(), 'Replay contains a nonordinary member')
            target = (destination / member.name).resolve()
            require(target.is_relative_to(destination.resolve()), 'Replay member escapes directory')
            if member.isfile():
                stream = archive.extractfile(member)
                if stream is None:
                    raise ValueError('Replay member has no payload')
                target.parent.mkdir(parents=True, exist_ok=True)
                with stream:
                    target.write_bytes(stream.read())


def coverage_contract(directory: Path) -> Coverage:
    receipt = read_receipt(directory)
    contract: Coverage = {
        'stages': [stage['name'] for stage in receipt['stages']],
        'artifacts': sorted(receipt['artifacts']),
    }
    tree = ast.parse(PRODUCER.read_text(encoding='utf-8'))
    calls = [node.value for node in tree.body if isinstance(node, ast.Expr)
             and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
             and node.value.func.id == 'run']
    names = [ast.literal_eval(call.args[0]) for call in calls]
    require(names == contract['stages'] and len(names) == 22,
            'Archived stage coverage differs from pinned producer')
    inventories = [node.value for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == 'files'
                           for target in node.targets)]
    require(len(inventories) == 1, 'Pinned producer has an unexpected artifact declaration')
    fixed = cast(list[str], ast.literal_eval(inventories[0]))
    dynamic = set(contract['artifacts']) - set(fixed)
    require(set(fixed) <= set(contract['artifacts']) and len(fixed) == 34
            and len(dynamic) == 10 and all(name.startswith('local/') for name in dynamic),
            'Archived artifact coverage differs from pinned producer')
    return contract


def check_coverage(directory: Path, contract: Coverage) -> None:
    receipt = read_receipt(directory)
    require([stage['name'] for stage in receipt['stages']] == contract['stages'],
            'Required replay stages differ')
    require(set(receipt['artifacts']) == set(contract['artifacts']),
            'Required replay artifact inventory differs')
    require(read_json(directory / 'STAGES.json') == receipt['stages'],
            'Receipt stages differ from recorded execution stages')


def strengthened_check(binding: Binding, bit: Path, directory: Path,
                       contract: Coverage) -> dict[str, object]:
    check_coverage(directory, contract)
    return binding.check(bit, directory)


def outcome(check: Callable[[], object]) -> str:
    try:
        check()
    except (ValueError, OSError) as error:
        if isinstance(error, OSError):
            return type(error).__name__
        return type(error).__name__ + ': ' + str(error).split(': ')[0]
    return 'accepted'


def save_receipt(directory: Path, receipt: Receipt) -> None:
    write_json(directory / 'RECEIPT.json', receipt)


def omit_artifact(directory: Path, name: str, delete: bool) -> None:
    receipt = read_receipt(directory)
    del receipt['artifacts'][name]
    if delete:
        (directory / name).unlink()
    save_receipt(directory, receipt)


def substitute_stage(directory: Path, index: int) -> None:
    receipt = read_receipt(directory)
    stage = receipt['stages'][index]
    (directory / (stage['name'] + '.log')).unlink()
    stage['name'] = 'unrelated-successful-command'
    log = directory / (stage['name'] + '.log')
    with log.open('w', encoding='utf-8') as stream:
        process = subprocess.run(
            [sys.executable, '-I', '-B', '-c', "print('Unrelated command completed successfully.')"],
            stdout=stream, stderr=subprocess.STDOUT, check=False)
    require(process.returncode == 0, 'Unrelated stage command failed')
    stage['exit_code'] = process.returncode
    stage['log_sha256'] = digest(log)
    write_json(directory / 'STAGES.json', receipt['stages'])
    receipt['artifacts']['STAGES.json'] = digest(directory / 'STAGES.json')
    save_receipt(directory, receipt)


def remove_inventory(directory: Path, delete: bool) -> None:
    receipt = read_receipt(directory)
    if delete:
        for name in receipt['artifacts']:
            if name not in {'RESULT.json', 'global-replay/ASSEMBLY.json'}:
                (directory / name).unlink()
    receipt['artifacts'] = {}
    save_receipt(directory, receipt)


def control_mutation(directory: Path, name: str) -> None:
    receipt = read_receipt(directory)
    if name == 'missing_stage':
        receipt['stages'].pop()
    elif name == 'failed_stage':
        receipt['stages'][0]['exit_code'] = 1
    elif name == 'wrong_source_pin':
        receipt['manifest_sha256'] = '0' * 64
    elif name == 'wrong_listed_hash':
        receipt['artifacts']['INDEPENDENT-LOCAL.json'] = '0' * 64
    elif name == 'missing_still_listed_file':
        (directory / 'INDEPENDENT-LOCAL.json').unlink()
    elif name == 'wrong_kappa_with_rehashed_artifact':
        assembly_path = directory / 'global-replay/ASSEMBLY.json'
        assembly = cast(dict[str, object], read_json(assembly_path))
        assembly['kappa'] = '1/100'
        write_json(assembly_path, assembly)
        receipt['artifacts']['global-replay/ASSEMBLY.json'] = digest(assembly_path)
    elif name == 'inconsistent_execution_stage_record':
        stages = receipt['stages'][1:] + receipt['stages'][:1]
        write_json(directory / 'STAGES.json', stages)
        receipt['artifacts']['STAGES.json'] = digest(directory / 'STAGES.json')
    else:
        raise ValueError('Unknown control')
    save_receipt(directory, receipt)


def rotated(values: list[str]) -> list[str]:
    offset = SEED % len(values)
    return values[offset:] + values[:offset]


def audit(binding: Binding, baseline: Path, work: Path, contract: Coverage) -> dict[str, object]:
    serial = 0

    def case(label: str, mutate: Callable[[Path], None], accepted: bool,
             public_cli: bool = False) -> dict[str, object]:
        nonlocal serial
        serial += 1
        directory = work / str(serial)
        shutil.copytree(baseline, directory)
        bit = directory / 'bit'
        complex_dir = directory / 'complex'
        mutate(complex_dir)
        original = outcome(lambda: binding.check(bit, complex_dir))
        supplemented = outcome(lambda: strengthened_check(binding, bit, complex_dir, contract))
        require((original == 'accepted') == accepted, 'Unexpected original outcome: ' + label)
        require(supplemented != 'accepted', 'Supplement accepted a mutation: ' + label)
        row: dict[str, object] = {
            'case': label, 'original_binding': original, 'coverage_supplement': supplemented,
        }
        if public_cli:
            output = directory / 'BINDING.json'
            process = subprocess.run(
                [sys.executable, '-I', '-B', str(ROOT / 'scripts/verify_frontier741_bindings.py'),
                 '--bit', str(bit), '--complex', str(complex_dir), '--out', str(output)],
                capture_output=True, text=True, check=False)
            require(process.returncode == 0 and not process.stderr, 'Public binding CLI rejected: ' + label)
            certificate = cast(dict[str, object], read_json(output))
            require(certificate['status'] == 'PASS_REBUILT_PR589_PR741_COMPOSITION',
                    'Public binding CLI did not certify composition')
            row['public_cli'] = {'exit_code': process.returncode, 'stdout': process.stdout.strip(),
                                 'certificate_status': certificate['status']}
        shutil.rmtree(directory)
        return row

    bit = baseline / 'bit'
    complex_dir = baseline / 'complex'
    result = strengthened_check(binding, bit, complex_dir, contract)
    stage_cases = []
    for name in rotated(contract['stages']):
        index = contract['stages'].index(name)
        stage_cases.append(case(name, partial(substitute_stage, index=index), True,
                                public_cli=name == 'all-native-phase-edges'))
    omission_cases = []
    deletion_cases = []
    for name in rotated(contract['artifacts']):
        omission_cases.append(case(name, partial(omit_artifact, name=name, delete=False), True))
        if name not in {'RESULT.json', 'global-replay/ASSEMBLY.json'}:
            deletion_cases.append(case(name, partial(omit_artifact, name=name, delete=True), True))
    combined = [case('empty_inventory', lambda directory: remove_inventory(directory, False), True),
                case('empty_inventory_and_42_missing_files',
                     lambda directory: remove_inventory(directory, True), True, public_cli=True),
                case('inconsistent_execution_stage_record',
                     lambda directory: control_mutation(directory, 'inconsistent_execution_stage_record'), True)]
    controls = [case(name, partial(control_mutation, name=name), False)
                for name in ['missing_stage', 'failed_stage', 'wrong_source_pin', 'wrong_listed_hash',
                             'missing_still_listed_file', 'wrong_kappa_with_rehashed_artifact']]
    return {
        'status': 'PASS_SCOPED_PR741_RECEIPT_COVERAGE_AUDIT',
        'base_commit': BASE_COMMIT,
        'assignment_seed': SEED,
        'selected_kappa': result['kappa'],
        'pristine_original_and_supplement': 'accepted',
        'coverage_contract': contract,
        'substituted_stages': stage_cases,
        'omitted_inventory_entries': omission_cases,
        'omitted_entries_and_deleted_artifacts': deletion_cases,
        'combined_omissions': combined,
        'negative_controls': controls,
        'scope': 'Pinned archived evidence coverage, not a cold construction replay or theorem audit.',
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-expected', action='store_true')
    parser.add_argument('--check', type=Path, default=HERE / 'EXPECTED.json')
    parser.add_argument('--coverage-check', nargs=2, type=Path, metavar=('BIT', 'COMPLEX'))
    args = parser.parse_args()
    check_sources()
    binding = load_binding()
    with tempfile.TemporaryDirectory(prefix='pr741-coverage-') as temporary:
        work = Path(temporary)
        baseline = work / 'baseline'
        baseline.mkdir()
        extract_evidence(baseline)
        contract = coverage_contract(baseline / 'complex')
        if args.coverage_check:
            bit, complex_dir = args.coverage_check
            strengthened_check(binding, bit.resolve(), complex_dir.resolve(), contract)
            print('PASS_PR741_COMPOSITION_WITH_REQUIRED_EVIDENCE_COVERAGE')
            return
        result = audit(binding, baseline, work, contract)
    if args.write_expected:
        write_json(args.check, result)
    else:
        require(read_json(args.check) == result, 'Audit receipt differs from expected evidence')
    print(result['status'], '111 altered-evidence cases accepted by original; '
          '117 mutations rejected by supplement; pristine accepted')


if __name__ == '__main__':
    main()
