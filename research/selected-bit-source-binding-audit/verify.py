#!/usr/bin/env python3
"""Check the selected PR589 supplier blob binding and one valid pin mutant."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_bytes())


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True,
                          stdout=subprocess.PIPE).stdout


def load_assembler():
    code = ROOT / 'research/gauge44-slots-t16/code'
    source = (ROOT / 'research/complex-sw4-frame8/vendor/main/research/'
              'complex-k492-owner-repair/vendor/multicold')
    os.environ['GAIN_PR564_SOURCE'] = str(source)
    os.environ['WITNESS_SPEC'] = str(ROOT / 'research/gauge44-slots-t16/data/SPEC.json')
    sys.path.insert(0, str(code))
    spec = importlib.util.spec_from_file_location('selected_bit_audit_assemble', code / 'assemble.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify():
    require(not sys.flags.optimize, 'The pinned loader uses assertions; run without -O')
    record = read_json(ROOT / 'certificates/selected-result.json')
    source_manifest = read_json(ROOT / record['source_manifest'])
    certificate = read_json(ROOT / record['certificate'])
    package_sources = read_json(PACKAGE / 'SOURCES.json')
    package_files = {row['path']: row for row in package_sources['files']}
    for relative, row in package_files.items():
        if row['usage'] == 'input':
            require(sha256((ROOT / relative).read_bytes()) == row['sha256'],
                    'Audit package input digest differs: ' + relative)

    # The selected source manifest covers the original PR589 supplier, its T16
    # input copy, and the code which reads and prices that copy.
    source_path = 'research/e8-bit-p111-tuned/tune/EXPECTED.json'
    t16_path = 'research/gauge44-slots-t16/inputs/PR589-EXPECTED.json'
    assembler_path = 'research/gauge44-slots-t16/code/assemble.py'
    for relative in (source_path, t16_path, assembler_path):
        require(relative in source_manifest['files'], 'Selected source inventory omits ' + relative)
        data = (ROOT / relative).read_bytes()
        require(sha256(data) == source_manifest['files'][relative],
                'Selected source inventory digest differs: ' + relative)
        require(relative in package_files and sha256(data) == package_files[relative]['sha256'],
                'Audit package live source pin differs: ' + relative)

    bit_record = certificate['bit_supplier']
    supplier_commit = bit_record['commit']
    merged_commit = bit_record['merged_as']
    merged_path = bit_record['path']
    original_path = 'research/e8-bit-p111/tune/EXPECTED.json'
    source_bytes = git('cat-file', 'blob', supplier_commit + ':' + original_path)
    merged_bytes = git('cat-file', 'blob', merged_commit + ':' + merged_path)
    input_bytes = (ROOT / t16_path).read_bytes()
    require(source_bytes == merged_bytes == input_bytes,
            'PR589 source, merged path, and T16 copy are not byte-identical')

    assembler = load_assembler()
    expected_blob = bit_record['git_blob_sha1']
    require(re.fullmatch(r'[0-9a-f]{40}', expected_blob) is not None,
            'Selected supplier Git blob ID is not syntactically valid')
    require(assembler.BIT_BLOB == expected_blob == assembler.git_blob(input_bytes),
            'Selected supplier blob ID is not bound to the source bytes')
    require(certificate['input_sha256']['package:inputs/PR589-EXPECTED.json'] == sha256(input_bytes),
            'Selected assembly does not bind the T16 supplier input digest')
    parsed = assembler.load_bit(input_bytes)
    require(parsed['nine']['bit_lower'] == certificate['bit_lower'],
            'T16 loader output differs from selected assembly bit lower bound')
    require(record['certificate_sha256'] == sha256((ROOT / record['certificate']).read_bytes()),
            'Selected result no longer pins the assembly certificate')

    # Mutate only the expected digest. The mutant remains a valid 40-hex Git
    # object ID; the production loader must reject the unchanged source bytes.
    mutant_blob = ('0' if expected_blob[0] != '0' else '1') + expected_blob[1:]
    require(re.fullmatch(r'[0-9a-f]{40}', mutant_blob) is not None and mutant_blob != expected_blob,
            'Negative fixture is not a distinct valid Git blob ID')
    assembler.BIT_BLOB = mutant_blob
    try:
        assembler.load_bit(input_bytes)
    except AssertionError as error:
        rejection = str(error)
    else:
        raise ValueError('Production loader accepted the wrong but well-formed Git blob ID')
    finally:
        assembler.BIT_BLOB = expected_blob
    require(rejection == 'bit supplier blob pin', 'Unexpected mutant rejection: ' + rejection)

    return {
        'status': 'PASS_SELECTED_BIT_SOURCE_BINDING_AUDIT',
        'base_commit': package_sources['base_commit'],
        'selected_record_sha256': package_files['certificates/selected-result.json']['sha256'],
        'selected_kappa': record['kappa'],
        'supplier_pr': bit_record['pr'],
        'supplier_head': supplier_commit,
        'supplier_source_path_at_head': original_path,
        'supplier_merge': merged_commit,
        'supplier_path_at_merge': merged_path,
        'supplier_git_blob_sha1': expected_blob,
        'supplier_source_sha256': sha256(source_bytes),
        'selected_bit_lower': certificate['bit_lower'],
        'loaded_bit_lower': parsed['nine']['bit_lower'],
        'mutant_git_blob_sha1': mutant_blob,
        'mutant_rejected_by': 'assemble.load_bit: bit supplier blob pin',
        'scope': 'One source identity binding only; no construction replay or supplier admission.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true',
                        help='write the deterministic result receipt after a successful check')
    args = parser.parse_args()
    result = verify()
    result_path = PACKAGE / 'RESULT.json'
    encoded = json.dumps(result, indent=2) + '\n'
    if args.write_result:
        result_path.write_text(encoded)
    else:
        require(result_path.is_file() and result_path.read_text() == encoded,
                'RESULT.json differs; inspect the sources before refreshing the receipt')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
