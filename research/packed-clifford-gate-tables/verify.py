#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Full unchanged packed checker plus every actual P/D table versus scalar formulas."""
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
A = types.ModuleType('authenticated_adapter')
A.__file__ = str(HERE / 'adapter.py')
exec(compile((HERE/'adapter.py').read_bytes(), A.__file__, 'exec'), A.__dict__)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def result_from_replay(result):
    keys = ('source_sha256', 'executed_kernel_sha256', 'adapter_sha256',
            'legacy_result_sha256', 'legacy_receipts_sha256',
            'unique_tables_audited', 'table_calls', 'caches')
    output = {key:result[key] for key in keys}
    output.update(status='PASS_PACKED_CLIFFORD_GATE_TABLE_INTEGRATION',
                  scalar_table_entries=512*sum(result['unique_tables_audited'].values()),
                  children=2896, adapters=224, columns=512,
                  scope='Opt-in exact gate-table integration for the pinned PR1781 record checker; not a new table algorithm, certificate, full cold replay or multiplication theorem.')
    return output


def main():
    result, _ = A.full_replay('candidate', audit=True)
    expected = json.loads((HERE/'RESULT.json').read_bytes())
    A.need(canonical(result_from_replay(result)) == canonical(expected), 'typed integration result differs')
    print(result['checker_stdout'], end='')
    print('PASS_PACKED_CLIFFORD_GATE_TABLE_INTEGRATION entries='+str(expected['scalar_table_entries']))


if __name__ == '__main__':
    main()
