# SPDX-License-Identifier: Apache-2.0
"""Targeted T37 payload controls against the actual strict runtime assembler.

The honest owner/invoice pair must pass first. Each mutation must then fail
at its named assertion, not at an unrelated pin, schema, or receipt digest.
The bit control validates the pinned bytes before injecting the altered
parsed allowance, as in the inherited PR589 bit-supplier controls.
Prepared with substantial OpenAI Codex assistance; inherited sources and
contracts are credited in NOTICE.md. This does not replace physical replay.
"""
import argparse
import ast
import copy
import importlib.util
import os
from pathlib import Path
import sys

from common import dump, identity, read, require, sha


def assertion_site(path, expression):
    """Find the exact guard by AST, allowing harmless whitespace differences."""
    text = path.read_text()
    wanted = ast.dump(ast.parse(expression, mode='eval').body)
    matches = [node for node in ast.walk(ast.parse(text))
               if isinstance(node, ast.Assert) and ast.dump(node.test) == wanted]
    require(len(matches) == 1, 'Expected exactly one targeted guard: '+expression)
    node = matches[0]
    return dict(line=node.lineno, end_line=node.end_lineno,
                assertion=ast.get_source_segment(text, node))


def targeted_failure(assemble, args, assembler_path, site, name):
    try:
        assemble(*args)
    except AssertionError as error:
        trace = error.__traceback__
        while trace.tb_next is not None:
            trace = trace.tb_next
        actual_path = Path(trace.tb_frame.f_code.co_filename).resolve()
        require(actual_path == assembler_path and
                site['line'] <= trace.tb_lineno <= site['end_line'],
                name+' failed at an unrelated assertion: '+str(actual_path)+':'+str(trace.tb_lineno))
        return dict(name=name, assembler_line=trace.tb_lineno,
                    assertion=site['assertion'], targeted_guard=True)
    raise AssertionError('Invalid payload receipt accepted: '+name)


def verify(owner_path, invoice_path, source_package, runtime=None):
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    require(os.environ.get('WITNESS_DISCOVER') != '1', 'Strict witness mode required')
    require(not os.environ.get('WITNESS_RECORD'), 'Discovery bookkeeping must be disabled')
    spec_env = os.environ.get('WITNESS_SPEC')
    if runtime is None:
        require(spec_env is not None, '--runtime or WITNESS_SPEC is required')
        runtime = Path(spec_env).resolve().parents[1]/'code'
    runtime = runtime.resolve()
    spec = Path(spec_env).resolve() if spec_env else runtime.parent/'data/SPEC.json'
    require(spec.is_file(), 'Runtime SPEC is missing: '+str(spec))
    assembler_path = (runtime/'assemble.py').resolve()
    require(assembler_path.is_file(), 'Runtime assembler is missing')
    os.environ['WITNESS_SPEC'] = str(spec)
    os.environ['GAIN_PR564_SOURCE'] = str(source_package.resolve())
    if 'witness' in sys.modules:
        require(Path(sys.modules['witness'].__file__).resolve() == runtime/'witness.py',
                'A different runtime witness is already imported')
    sys.path.insert(0, str(runtime))
    module_spec = importlib.util.spec_from_file_location('t37_payload_assembly', assembler_path)
    assembly = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(assembly)
    require(not assembly.DISCOVER, 'Runtime assembler must use strict pins')

    expressions = {
        'old_complex_payload512': "0<invoice['global_prefix_bits']<=invoice['charged_prefix_bits']==1024",
        'stale_row_prefix_extra1024': "invoice['row_prefix_extra']==2048",
        'stale_row16469': "finite['physical_row_coefficient']==2*stock.bit_length()+9909+252+2048",
        'old_global_prefix491': "invoice['global_prefix_bits']==max(z['prefix_bits']for p in invoice['providers'].values()for z in p['local'].values())+37+333+333+4",
        'bit_allowance1024': "bit['bit']['two_level_coefficient_bits']<bit['bit']['charged_two_level_coefficient_bits']==512 and bit['bit']['row_coefficient']<20161",
    }
    sites = {name: assertion_site(assembler_path, test) for name, test in expressions.items()}
    assembler_hash, spec_hash = sha(assembler_path), sha(spec)
    owner, invoice = read(owner_path), read(invoice_path)
    original_owner_hash, original_invoice_hash = sha(owner_path), sha(invoice_path)
    baseline = assembly.assemble(owner, invoice, original_owner_hash, original_invoice_hash)
    require((invoice['global_prefix_bits'], invoice['charged_prefix_bits'],
             invoice['row_prefix_extra'], invoice['finite']['physical_row_coefficient']) ==
            (779, 1024, 2048, 17495), 'Honest T37 payload values')
    require(baseline['status'] == 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY', 'Honest assembly status')

    mutations = [
        ('old_complex_payload512', lambda o, i: i.__setitem__('charged_prefix_bits', 512)),
        ('stale_row_prefix_extra1024', lambda o, i: i.__setitem__('row_prefix_extra', 1024)),
        ('stale_row16469', lambda o, i: i['finite'].__setitem__('physical_row_coefficient', 16469)),
        ('old_global_prefix491', lambda o, i: i.__setitem__('global_prefix_bits', 491)),
    ]
    checks = []
    for name, mutate in mutations:
        o, i = copy.deepcopy(owner), copy.deepcopy(invoice)
        mutate(o, i)
        owner_hash = identity(o)
        i['owner_audit_sha256'] = owner_hash
        checks.append(targeted_failure(assembly.assemble, (o, i, owner_hash, identity(i)),
                                       assembler_path, sites[name], name))

    # Validate the real pinned bytes before altering only the decoded field.
    # Merely changing bytes would stop at the blob pin and miss this guard.
    bit_data = assembly.BIT_PATH.read_bytes()
    real_load = assembly.load_bit
    real_record = real_load(bit_data)
    require(real_record['nine']['bit']['charged_two_level_coefficient_bits'] == 512,
            'Pinned bit allowance must remain512')
    calls = []

    def changed_bit_allowance(data):
        require(data == bit_data, 'Unexpected bit supplier input')
        record = copy.deepcopy(real_load(data))
        record['nine']['bit']['charged_two_level_coefficient_bits'] = 1024
        calls.append(True)
        return record

    try:
        assembly.load_bit = changed_bit_allowance
        o, i = copy.deepcopy(owner), copy.deepcopy(invoice)
        owner_hash = identity(o)
        i['owner_audit_sha256'] = owner_hash
        name = 'bit_allowance1024'
        checks.append(targeted_failure(assembly.assemble, (o, i, owner_hash, identity(i)),
                                       assembler_path, sites[name], name))
    finally:
        assembly.load_bit = real_load
    require(calls == [True], 'Bit control must reach the checked parsed-record injection exactly once')
    require(assembly.load_bit(bit_data) == real_record, 'Pinned bit loader restoration')
    require(read(owner_path) == owner and read(invoice_path) == invoice and
            sha(owner_path) == original_owner_hash and sha(invoice_path) == original_invoice_hash,
            'Input receipts changed during controls')
    require(sha(spec) == spec_hash and sha(assembler_path) == assembler_hash,
            'Runtime source or specification changed during controls')
    return dict(
        status='PASS_T37_PAYLOAD_TARGETED_NEGATIVE_CONTROLS',
        valid_receipt_kappa=baseline['kappa'],
        honest_assembly_passed=True,
        rejected_controls=[check['name'] for check in checks],
        targeted_failures=checks,
        owner_hash_rebound_for_each_mutation=True,
        bit_injection_after_original_blob_pin=True,
        bit_loader_restored=True,
        input_sha256=dict(owner=original_owner_hash, invoice=original_invoice_hash,
                          runtime_spec=spec_hash, bit_supplier=sha(assembly.BIT_PATH)),
        assembler_sha256=assembler_hash,
        scope='Five parsed-receipt mutations against the actual strict runtime assembler. The honest invoice passes first; each mutation reaches its named assertion. No physical construction, source pin, or mathematical coverage is replaced by these controls.',
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-package', type=Path, required=True)
    parser.add_argument('--owner', type=Path, required=True)
    parser.add_argument('--invoice', type=Path, required=True)
    parser.add_argument('--runtime', type=Path, help='Materialized runtime/code directory; otherwise inferred from WITNESS_SPEC')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Control output must be new')
    result = verify(args.owner, args.invoice, args.source_package, args.runtime)
    dump(args.out, result)
    print(result['status'], len(result['rejected_controls']))
