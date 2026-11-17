#!/usr/bin/env python3
"""Reconcile saved host evidence for the one exited native unit. No service calls."""
import hashlib
import importlib.util
import json
import os
import re
from decimal import Decimal
from pathlib import Path


HERE = Path(__file__).resolve().parent
NATIVE = HERE.parent / 'e4-native-qualification'
HOST_SHA = '4bb1de52405b3a465461767b4b79599faa935f1ffa46092670ce56229e38a269'
SUPERVISOR_SHA = '7ffeaf1db1ead880401fe4f35f9495e88dfe4e0ad7de0454f639af8ef2630cc8'
DRIVER_SHA = '3328d0b08145bf8a6fa08e0a075d0dc77a24b3c7d6ae31d5eb298fe91db0be0f'
EXPECTED_ARTIFACTS = {
    'SUPERVISOR-STARTED.json': 'b5d7943d7a9a924e8d4f2103d6771efa5d9e67f7724aeefca97312c8ac9bff71',
    'SUPERVISOR-GUARD.json': '9053aa1696d2e510a809a2db91086f6b79afc3a875fc57ed4305fb005d7ea41a',
    'SCOPED-STARTED.json': '83df79b535f870b00751c324e74e5decf729f51069304508624a1da4de3260f3',
    'SCOPED-RESULT.json': '2721dcc4ad93577b2d2c5085dfbcbe3449cbe9d3ed76dbd3a43e25f999043921',
    'SCOPED-TERMINAL.json': 'b8e53ef5ea6fa68f9af56d1643d1f735335c23ae94732e39d80edea524371837',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path, expected=None):
    require(path.is_file() and not path.is_symlink(), f'missing or symlink {path}')
    data = path.read_bytes()
    if expected is not None:
        require(digest(data) == expected, f'hash mismatch {path}')
    return data


def frozen_code(manifest, expected):
    data = read(NATIVE / manifest, expected)
    records = json.loads(data)
    for name, expected_sha in records['files'].items():
        read(NATIVE / name, expected_sha)
    return records


def parse_properties(raw):
    properties = {}
    for line in raw.splitlines():
        key, value = line.split('=', 1)
        require(key not in properties, f'duplicate property {key}')
        properties[key] = value
    return properties


def main():
    recovered = HERE / 'RECOVERED-NATIVE-RECEIPT.json'
    require(not recovered.exists(), 'existing recovery record')
    require(not (NATIVE / 'SUPERVISOR-TERMINAL.json').exists(), 'use original finalized receipt')
    host_raw = read(HERE / 'HOST-POST-READBACK.json', HOST_SHA)
    host = json.loads(host_raw)
    require(host['session'] == 83248 and host['observer_exit_code'] == 143
            and not host['original_supervisor_terminal_present'], 'observer interruption identity')
    require(host['systemctl_show']['exit_code'] == 0, 'unavailable host status')
    post = parse_properties(host['systemctl_show']['output'])
    sup_freeze = frozen_code('SUPERVISOR-FREEZE.json', SUPERVISOR_SHA)
    require(sup_freeze['driver_freeze_sha256'] == DRIVER_SHA, 'driver freeze link')
    frozen_code('FREEZE.json', DRIVER_SHA)
    raw = {name: read(NATIVE / name, sha) for name, sha in EXPECTED_ARTIFACTS.items()}
    launch = json.loads(raw['SUPERVISOR-STARTED.json'])
    guard = json.loads(raw['SUPERVISOR-GUARD.json'])
    started = json.loads(raw['SCOPED-STARTED.json'])
    terminal = json.loads(raw['SCOPED-TERMINAL.json'])
    science = json.loads(raw['SCOPED-RESULT.json'])
    pinned_unit = launch['unit']
    pid = started['pid']
    live = guard['systemd_properties']
    require(launch['supervisor_freeze_sha256'] == SUPERVISOR_SHA, 'original supervisor identity')
    require(pinned_unit == host['original_unit'] == post['Id']
            and str(pid) == live['MainPID'] and guard['verified_while_active'], 'original unit/PID identity')
    require(re.fullmatch(r'[a-f0-9]{32}', post['InvocationID']) is not None, 'host invocation ID')
    argv = ' '.join(launch['driver_argv'])
    require(argv in live['ExecStart'] and argv in post['ExecStart']
            and f'pid={pid} ; code=exited ; status=0' in post['ExecStart'], 'driver command or exit binding')
    require(live['ActiveState'] == 'active' and live['SubState'] == 'running',
            'no authenticated original live-state check')
    expected = {
        'MemoryMax': '2147483648', 'MemorySwapMax': '0', 'TasksMax': '16',
        'CPUAffinity': str(guard['cpu_affinity']), 'CPUQuotaPerSecUSec': '1s',
        'CPUQuotaPeriodUSec': '10ms', 'RuntimeMaxUSec': '1h10min',
        'TimeoutStopUSec': '250ms', 'KillMode': 'control-group', 'OOMPolicy': 'kill',
    }
    for key, value in expected.items():
        require(live[key].replace(' ', '') == post[key].replace(' ', '') == value,
                f'live/final enforced limit differs: {key}')
    require(guard['kernel_limits'] == {
        'cpu.max': '10000 10000', 'cpu.max.burst': '0', 'memory.max': '2147483648',
        'memory.oom.group': '1', 'memory.swap.max': '0', 'pids.max': '16',
    }, 'kernel limits')
    require(started['guard'] == {'cpu_max': [10000,10000], 'memory_max': 2147483648,
                                  'pids_max': 16, 'swap_max': 0}, 'driver limits')
    require(post['ActiveState'] == 'active' and post['SubState'] == 'exited'
            and post['MainPID'] == '0' and post['Result'] == 'success'
            and post['ExecMainCode'] == '1' and post['ExecMainStatus'] == '0'
            and not post['ControlGroup'], 'unit has not exited successfully')
    original_group = '/sys/fs/cgroup' + live['ControlGroup']
    stat = host['original_cgroup_stat']
    require(original_group.endswith('/' + pinned_unit) and stat['exit_code'] == 1
            and original_group in stat['output'] and 'No such file or directory' in stat['output'],
            'exact previously live cgroup absence')

    wall_usec = int(post['ExecMainExitTimestampMonotonic']) - int(post['ExecMainStartTimestampMonotonic'])
    wall = wall_usec / 1_000_000
    cpu_usec = (int(post['CPUUsageNSec']) + 999) // 1000
    peak = int(post['MemoryPeak'])
    child_cpu = sum(Decimal(str(terminal[key])) for key in (
        'cpu_user_seconds', 'cpu_system_seconds',
        'waited_children_cpu_user_seconds', 'waited_children_cpu_system_seconds',
    ))
    require(0 < child_cpu <= Decimal(cpu_usec) / 1_000_000 <= 3600
            and terminal['wall_seconds'] <= wall <= 4200
            and 0 < peak <= 2**31, 'final aggregate or driver-accounting bounds')
    require(len(science['charts']) == 1090 and len(science['controls']) == 19
            and all(ok is True for ok in science['controls'].values()), 'chart/control census')
    pairs = [tuple(row['pair']) for row in science['charts']]
    require(len(set(pairs)) == 1090 and set(pairs) == {
        tuple(pair) for pair in science['pair_manifest']['full_validation_pairs']
    }, 'manifest coverage')
    require(all(row['columns'] == row['adjoint_columns'] == 512 and row['absolute_phase_verified']
                and row['wrong_phase_rejected'] for row in science['charts']), 'native phase coverage')
    require(science['economics']['status'] == 'PASS_E4_18_CALL_INGREDIENT_ECONOMICS_ONLY',
            'ingredient economics status')

    finalizer_path = NATIVE / 'supervisor_finalizer.py'
    read(finalizer_path, sup_freeze['files'][finalizer_path.name])
    spec = importlib.util.spec_from_file_location('frozen_e4_finalizer', finalizer_path)
    finalizer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(finalizer)
    require(finalizer.physical_custody(raw['SCOPED-RESULT.json'], lambda name: read(NATIVE / name)),
            'physical artifacts')

    # Project verified successful main exit and in-limit counters into the
    # original core checker. These flags are not original observer output.
    accounting = finalizer.finalize(
        {'exit_code': 0, 'execution_wall_seconds': wall, 'wall_killed': False, 'cpu_killed': False},
        raw['SCOPED-STARTED.json'], raw['SCOPED-TERMINAL.json'], raw['SCOPED-RESULT.json'],
        DRIVER_SHA, True, True, True, cpu_usec, peak,
    )
    require(accounting.pop('status') == 'PASS_SUPERVISED_INGREDIENT_NATIVE',
            'original core reconciliation')
    del accounting['wall_killed'], accounting['cpu_killed']
    final = {
        **accounting,
        'schema': 'e4-native-recovery/v1',
        'status': 'PASS_RECOVERED_INGREDIENT_NATIVE',
        'original_finalizer_core_status': 'PASS_SUPERVISED_INGREDIENT_NATIVE',
        'measured_within_limits': True,
        'unit': pinned_unit,
        'supervisor_freeze_sha256': SUPERVISOR_SHA,
        'stdout_sha256': digest(read(NATIVE / 'SUPERVISOR-STDOUT.log')),
        'stderr_sha256': digest(read(NATIVE / 'SUPERVISOR-STDERR.log')),
        'aggregate_resource_provenance': 'Final cached accounting on the original successful retained unit, with the exact previously live cgroup absent.',
        'recovery_provenance': {
            'origin': 'retained original unit',
            'observer_exit_code': 143,
            'host_readback_sha256': HOST_SHA,
            'original_supervisor_terminal_present': False,
            'original_unit': pinned_unit,
        },
        'retained_unit_observation': post,
        'original_group': original_group,
        'original_artifact_sha256': EXPECTED_ARTIFACTS,
        'original_driver_and_waited_children_cpu_seconds': str(child_cpu),
        'original_cleanup_observed': False,
        'scope': 'Recovered external accounting and custody for the original completed 18-call ingredient run. The outer interruption cause is unknown. Signed 17-call qualification and any κ gain are separate.',
    }
    require(not (NATIVE / 'SUPERVISOR-TERMINAL.json').exists(), 'original terminal appeared during recovery')
    with recovered.open('x', encoding='utf-8') as output:
        json.dump(final, output, sort_keys=True, indent=2)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())
    print(digest(recovered.read_bytes()), final['status'])


if __name__ == '__main__':
    main()
