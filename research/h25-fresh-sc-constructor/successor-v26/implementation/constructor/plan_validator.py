"""Pure validation of concrete producer SOURCE plans, never a runtime schedule.

No original definitions are imported or extracted. All generation/nonce values
are DATA, neither issued nor reserved. This validator performs no filesystem I/O.
"""
import hashlib
import json
import posixpath

CLAIMS = {'runtime_admission': False, 'C07': False, 'full_C05': False,
          'full_V03': False, 'original_credit': 0}
RUNTIME_NAMES = ['proposed-runtime', 'session', 'export', 'group01',
                 'failure_variants', 'producer-output']
ROLES = ['group01', 'failure_variants']
PYTHON = '/usr/bin/python3.12'
GCC = '/usr/bin/x86_64-linux-gnu-gcc-13'
FLAGS = ['-nostartfiles', '-shared', '-fPIC', '-O3', '-std=c11',
         '-Wall', '-Wextra', '-Werror', '-I/usr/include/python3.12']
ROUND = '/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/c05-v03-source-binding-20261103T1426Z'


def need(value, message):
    if value is not True:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii') + b'\n'


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def clean_absolute(value):
    need(type(value) is str and value.startswith('/')
         and posixpath.normpath(value) == value and '//' not in value
         and all(32 <= ord(c) < 127 for c in value), 'plan absolute path')
    return value


def derive_command(mode, role, stage, producer, pins):
    """Source-predicate argv derivation only; never launches a producer."""
    argv = [PYTHON, '-S', '-s', '-P', '-B']
    if mode == 'optimized':
        argv.append('-O')
    driver = 'scientific_driver.py' if role == 'group01' else 'variant_driver_v1.py'
    argv += [stage + '/integration/full_driver.py', '--root-sha256',
             pins['integration/full_driver.py'], '--provider',
             stage + '/integration/probe_binding_v3.py', pins['integration/probe_binding_v3.py'],
             '--driver', stage + '/integration/' + driver,
             pins['integration/' + driver], '--integration', stage + '/integration', '--']
    if role == 'group01':
        argv += ['--lanes', 'candidate', '--finite-only', '--output', producer['output_directory']]
    else:
        argv += ['--output', producer['output_directory'], '--generation',
                 str(producer['generation']), '--launch-nonce', producer['launch_nonce']]
    return argv


def derive_variant_compilers(stage, output):
    return [[GCC] + FLAGS + [stage + '/areas/field-negative-variants-v1/' + kind
            + '/dict_probe_fields_v1.c', '-o', output + '/' + kind
            + '/_h25_dict_probe.cpython-312-x86_64-linux-gnu.so']
            for kind in ('pyinit_failure', 'exec_failure')]


def validate_source_plans(selection, rows):
    need(type(selection) is dict, 'selection record')
    need(selection.get('schema') == 'joined-two-mode-producer-source-plans-v2', 'selection schema')
    need(type(selection.get('claims')) is dict and canonical(selection['claims']) == canonical(CLAIMS), 'plan non-admission claims')
    need(selection.get('runtime_schedule_complete') is False, 'complete runtime schedule remains unadmitted')
    need(selection.get('mode_order') == ['normal', 'optimized'], 'serial proposed mode order')
    need(selection.get('source_plan_only') is True, 'source plan label')
    need(type(selection.get('runtime_schedule_unresolved')) is list
         and len(selection['runtime_schedule_unresolved']) > 0, 'remaining runtime obligations')
    need(selection.get('forbidden_runtime_names') == RUNTIME_NAMES, 'runtime ownership names')
    approved = selection.get('approved_preparation')
    need(type(approved) is dict and approved.get('stage_name') == 'full-stage', 'approved stage name')
    need(type(approved.get('parents')) is dict and set(approved['parents']) == {'normal', 'optimized'}, 'approved parents')
    need(type(approved.get('destinations')) is dict and set(approved['destinations']) == {'normal', 'optimized'}, 'approved destinations')
    modes = selection.get('modes')
    need(type(modes) is dict and set(modes) == {'normal', 'optimized'}, 'two distinct plan modes')
    pins = {r['installed_relative_path']: r['sha256'] for r in rows}
    required = ['integration/' + n for n in ('full_driver.py', 'probe_binding_v3.py',
                'scientific_driver.py', 'variant_driver_v1.py')]
    need(all(path in pins for path in required), 'selected source pins')
    proposal_data = selection.get('generation_and_nonce')
    need(type(proposal_data) is dict and proposal_data.get('issued') is False
         and proposal_data.get('reserved') is False
         and proposal_data.get('kind') == 'PROPOSED_DATA_NOT_ISSUED', 'top-level generation/nonce DATA')
    roots, outputs, generations, nonces = set(), set(), set(), set()
    for mode in ('normal', 'optimized'):
        plan = modes[mode]
        need(type(plan) is dict and plan.get('mode') == mode, 'mode identity collision')
        parent = ROUND + '/validation/preparation-' + mode
        stage = parent + '/full-stage'
        session = ROUND + '/proposed-runtime/' + mode + '/session'
        export = ROUND + '/proposed-runtime/' + mode + '/export'
        need(approved['parents'][mode] == parent and approved['destinations'][mode] == stage,
             'concrete preparation parent/stage')
        need(plan.get('stage') == stage, 'plan stage')
        need(plan.get('session_directory') == session, 'session collision or derivation')
        need(plan.get('export_directory') == export, 'export collision or derivation')
        need(plan.get('source_plan_only') is True, 'mode source plan label')
        need(plan.get('producer_order') == ROLES, 'producer order')
        obligation = plan.get('group01_positive_three_build_obligation')
        need(type(obligation) is dict and obligation.get('count') == 3
             and obligation.get('separate_from_variant_two') is True
             and obligation.get('source_module') == 'integration/native_packet.py'
             and obligation.get('source_sha256') == pins.get('integration/native_packet.py'),
             'separate group01 three-build obligation')
        for path in (parent, stage, session, export):
            clean_absolute(path)
            need(path not in roots, 'plan root collision')
            roots.add(path)
        producers = plan.get('producers')
        need(type(producers) is dict and set(producers) == set(ROLES), 'two selected producers')
        for role in ROLES:
            producer = producers[role]
            need(type(producer) is dict and producer.get('role') == role, 'producer role')
            need(type(producer.get('generation')) is int and producer['generation'] > 0,
                 'generation DATA integer')
            need(producer['generation'] not in generations, 'generation collision')
            generations.add(producer['generation'])
            nonce = producer.get('launch_nonce')
            need(type(nonce) is str and len(nonce) == 64
                 and all(c in '0123456789abcdef' for c in nonce) and nonce not in nonces, 'nonce DATA collision')
            nonces.add(nonce)
            need(producer.get('issued') is False and producer.get('reserved') is False
                 and producer.get('kind') == 'PROPOSED_DATA_NOT_ISSUED', 'nonce or generation issued')
            evidence, output = session + '/' + role, session + '/' + role + '/producer-output'
            need(producer.get('evidence_directory') == evidence and producer.get('output_directory') == output,
                 'output collision or evidence/output relation')
            need(output not in outputs and evidence not in outputs, 'producer output collision')
            outputs.update((output, evidence))
            command = derive_command(mode, role, stage, producer, pins)
            need(producer.get('command') == command, 'inconsistent derived command')
            need(producer.get('command_sha256') == digest(command), 'command binding')
            need(producer.get('plan_sha256') == digest({k: v for k, v in producer.items() if k != 'plan_sha256'}),
                 'producer plan binding')
        need(plan.get('gcc_variant_argv') == derive_variant_compilers(stage, producers['failure_variants']['output_directory']),
             'ordered variant two compiler commands')
        positive = [[GCC] + FLAGS[1:] + [stage + '/areas/cache-validity/probe-native/' + filename,
                    '-o', producers['group01']['output_directory'] + '/cold-native-metadata/'
                    + module + '.cpython-312-x86_64-linux-gnu.so']
                    for filename, module in (('dict_probe_v2.c', '_h25_dict_probe'),
                    ('probe_watcher_fixture.c', '_h25_probe_watch_fixture'),
                    ('probe_bounds_fixture_v2.c', '_h25_probe_bounds_fixture'))]
        need(plan.get('group01_positive_argv') == positive, 'separate ordered group01 three compiler commands')
    need(len(outputs) == 8 and not (roots & outputs), 'complete plan path separation')
    return True
