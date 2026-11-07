# Modified 2026-11-07: Clear1nsight, with OpenAI Codex and ChatGPT Pro assistance. See NOTICE.md.
"""Exact adopted full-source command projection and terminal parent receiver.

This module never imports a scientific image, issues execution permission or
changes its input domain.  The authenticated parent loads it as source.  The
normal image's original SC4 entry qualifies live disposition after its finally;
the parent additionally requires actual exit/wait, relay EOF and all writer
closure.  A full receipt written before a later exception cannot pass here.
"""
from pathlib import Path

W = Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
R = W / 'outputs/caller-proof-completion-20261107T0155Z'
ROOT = W / 'outputs/h25-data-handling-20261028'
STAGE_BASE = R / 'implementation/bindings/stages'
ADOPTED = W / 'outputs/s03-frozen-source-selection-20261104T1210Z/implementation'
NAME = 'IndependentPrefixDATAComposedV1'
FLAGS = ('-S', '-s', '-P', '-B')
ROOT_SHA = 'f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0'
PROVIDER_SHA = '9cbb7368f89e71d1e6cc46db5dc77efed3e03ed2a801c98c88fe316e4d9f3ef2'
BASELINE_SHA = '9bbafe3f53febec7a984751b9e06741e06df34e2e6fa7c328c805b9eea700bd7'
SELECTIONS = {
    'normal': ('joined-full-candidate-v1', '1a0dd86bffc5cd4d',
               '4804814035aea33eeb1a26ca51ddf82555423e8d275636d6a274f43541aa5977',
               'fa9f473320e9df3a2328bd8388f12eca4e7fc3eeed9289f7fdbf2eeb32a7452f',
               'full:candidate', False),
    'optimized': ('joined-full-candidate-refusal-v1', 'b1497bfaaf2cedca',
                  'da49427ab8cce9d552f4dc64d6031adb60ed52c006ebcd1627ed409e9c632cc4',
                  '92b507a2667b0d0085f63fb35176167806272934fef8149da691043411c81db0',
                  'optimized-refusal:candidate', True),
}
ADOPTION_PATH = W / 'outputs/s03-adoption-proof-review-20261104T1255Z/review/FINAL-ACTUAL-SOURCE-ADOPTION-ACCEPTANCE-v1.json'
ADOPTION_SHA = '99b856e02dd05a0fe576a052c976f8ee98de5db71b4dcddf44ab32532c4d62b2'
CATALOG_SHA = '97af356321e9dabe465c70f6a475e6b957735152d293359e9713cf01c7733d96'
MANIFEST_SHA = 'e4e4f461794b4a8e09291a421ae4765446ff4c25431728df7609999e2ef4fed3'
COMMANDS_SHA = '5872d8d79247356e2ac8c9a41fc1de875f292426dfd2d2174145c14561ffc942'
REFUSAL = b'RuntimeError: SC4 fixed assertion-on fresh candidate full invocation required\n'


def need(value, reason):
    if value is not True:
        raise ValueError(reason)


def job_for(mode):
    need(type(mode) is str and mode in SELECTIONS, 'exact complete full job')
    row = SELECTIONS[mode]
    return {'optimized': row[5], 'lanes': 'candidate', 'finite_only': False,
            'bootstrap': {'provider': 'integration/probe_binding_v3.py',
                          'driver': 'integration/scientific_driver.py'},
            'full_caller_role': row[4]}


def case_for(mode, stage_sha256):
    row = SELECTIONS[mode]
    return {'stage': row[0], 'job': mode, 'label': NAME + ('N' if mode == 'normal' else 'O'),
            'stage_sha256': stage_sha256}


def command_for(stage, declared, job_name, job, science_root):
    """Only the adopted full Root/provider/image command with a new owned output.

    The sole command/path inverse changes are the new immutable stage mount and
    genuinely owned retained output.  Defaults, lane, anchor, flags and original
    native/source bootstrap remain explicit.  Optimized full is refusal only.
    """
    need(type(stage) is type(STAGE_BASE) and type(science_root) is type(STAGE_BASE),
         'concrete full command paths')
    need(type(job_name) is str and job_name in SELECTIONS and job == job_for(job_name),
         'exact adopted full job with original assertion semantics')
    row = SELECTIONS[job_name]
    need(stage == STAGE_BASE / row[0], 'exact full stage inverse')
    files = declared['files']
    for relative, expected in (('integration/full_driver.py', ROOT_SHA),
                               ('integration/probe_binding_v3.py', PROVIDER_SHA),
                               ('integration/scientific_driver.py', row[3])):
        need(type(files[relative]) is dict and files[relative]['sha256'] == expected and
             files[relative]['mode'] == 0o444, 'adopted original Root/provider/scientific source')
    source = R / 'runtime/completed-source' / NAME
    label = NAME + ('N' if job_name == 'normal' else 'O')
    need(science_root == source / label / 'runner/artifact/science',
         'full science stays in the complete actual attempted source union')
    return ['/usr/bin/python3.12', *(['-O'] if row[5] else []), *FLAGS,
            str(stage / 'integration/full_driver.py'), '--root-sha256', ROOT_SHA,
            '--provider', str(stage / 'integration/probe_binding_v3.py'), PROVIDER_SHA,
            '--driver', str(stage / 'integration/scientific_driver.py'), row[3],
            '--integration', str(stage / 'integration'), '--', '--lanes', 'candidate',
            '--output', str(science_root), '--anchor', str(stage / 'baseline/anchor.json')]


def common_entry_command(case, stage, layout, waiting_sha):
    return ['/usr/bin/python3.12', *FLAGS, *(['-O'] if case['job']=='optimized' else []),
        str(stage/'integration/candidate_entry.py'),'--output',str(layout.science_root),
        '--lanes','candidate','--waiting-config',str(layout.supervision_root/'WAIT.json'),
        '--waiting-sha256',waiting_sha]


def common_entry_binding(kernel,case,layout,declared,receipt):
    """Bind both the original common R command and actual inner native command."""
    wait,wait_pin=kernel.read_json(layout.supervision_root/'WAIT.json',16384,0o444)
    arrival,arrival_pin=kernel.read_json(layout.supervision_root/'ARRIVED.json',16384,0o444)
    seal,seal_pin=kernel.read_json(layout.supervision_root/'RELEASE.json',16384,0o444)
    intent,intent_pin=kernel.read_json(layout.intent_path,16384,0o444,seal['intent_pin'])
    entry,entry_pin=kernel.read_json(layout.runner_root/'ENTRY.json',16384,0o444)
    stage=STAGE_BASE/case['stage']
    kernel.need(wait['case_id']==case['label'] and wait['stage_sha256']==case['stage_sha256']
        and wait['runner_sha256']==receipt['runner_sha256'] and wait['job']==case['job']
        and receipt['command']==common_entry_command(case,stage,layout,wait_pin['sha256']),
        'actual common runner candidate-entry command')
    kernel.need(intent['schema']=='fresh-active-nested-runner-intent-v3'
        and intent['common_rendezvous']=={'entry':arrival['entry'],'runner':arrival['runner'],
            'arrival_sha256':arrival_pin['sha256'],'waiting_sha256':wait_pin['sha256']}
        and seal['schema']=='h25-entry-release-v1' and seal['entry']==arrival['entry']
        and seal['runner']==arrival['runner'] and seal['waiting_sha256']==wait_pin['sha256']
        and seal['arrival_sha256']==arrival_pin['sha256'],'exact retained release/arrival/intent inverse')
    inner=command_for(stage,declared,case['job'],job_for(case['job']),layout.science_root)
    kernel.need(entry['schema']=='h25-common-entry-result-v1' and entry['case_id']==case['label']
        and entry['inner_command']==inner and type(entry['inner_exit']) is int
        and entry['inner_exit']==(1 if case['job']=='optimized' else 0)
        and entry['failure'] is None and entry['waiting_sha256']==wait_pin['sha256']
        and entry['arrival_sha256']==arrival_pin['sha256'] and entry['release_sha256']==seal_pin['sha256']
        and entry['intent_pin']==seal['intent_pin'] and entry['outer_usage_aliases_retired'] is True,
        'actual complete entry disposition and retained one-use binding')
    profile=intent['native_entry_profile'];artifact=layout.artifact_parent.stat()
    usage_path=layout.runner_root/'native-usage.json';usage=usage_path.stat()
    timed=[profile['time_path'],'-f','{"user_seconds":%U,"system_seconds":%S,"kernel_max_rss_kib":%M,"exit":%x}',
           '-o',str(usage_path),'--',*inner]
    native=[profile['entry_path'],'--entry-image',profile['entry_path'],profile['entry_sha256'],str(profile['entry_bytes']),
        '--time-image',profile['time_path'],profile['time_sha256'],str(profile['time_bytes']),
        '--read-root',str(ROOT),'--artifact-parent',str(layout.artifact_parent),str(artifact.st_dev),str(artifact.st_ino),
        '--science-leaf','science','--usage',str(usage_path),str(usage.st_dev),str(usage.st_ino),'--',*timed]
    kernel.need(entry['native_command']==native,'actual inner native/time/source command inverse')
    return entry


def stage_check(kernel, stage_pins):
    """Verify exact full payload inverses; only JOBS and enclosing bindings differ."""
    kernel.exact(stage_pins, ('normal', 'optimized'))
    catalog, catalog_pin = kernel.read_json(ADOPTED / 'SOURCE-SELECTIONS-v1.json', 1048576, 0o444)
    manifest, manifest_pin = kernel.read_json(ADOPTED / 'SELECTED-SOURCE-MANIFEST-v1.json', 1048576, 0o444)
    adoption, adoption_pin = kernel.read_json(ADOPTION_PATH, 1048576, 0o444)
    commands, commands_pin = kernel.read_json(ADOPTED / 'COMMANDS-v1.json', 1048576, 0o444)
    kernel.need(catalog_pin['sha256'] == CATALOG_SHA and manifest_pin['sha256'] == MANIFEST_SHA and
                adoption_pin['sha256'] == ADOPTION_SHA and commands_pin['sha256'] == COMMANDS_SHA and
                adoption['source_adopted'] is True and adoption['S03_08_completed'] is True and
                adoption['selected_manifest']['sha256'] == MANIFEST_SHA,
                'exact actual adopted S03 source authority, no rejected historical catalog')
    kernel.need(catalog['full_callers']['baseline']['overlay']['integration/scientific_driver.py']['sha256'] == BASELINE_SHA,
                'independent adopted full baseline image retained')
    rows, retained = {}, {}
    # S10.02 is a separately owned fresh-baseline route.  Retain its actual
    # accepted source/command boundary; the historical anchor alone never
    # completes the later current baseline-transfer/comparison requirement.
    baseline_command = baseline_source_route(commands)
    for baseline_pin in catalog['full_callers']['baseline']['overlay'].values():
        row, unused = kernel.IO.read(Path(baseline_pin['path']),baseline_pin['bytes'],0o444,baseline_pin)
        rows[row['path']] = row
    for mode, selected in SELECTIONS.items():
        stage = STAGE_BASE / selected[0]
        declared, actual = kernel.read_json(stage / 'STAGE.json', 1048576, 0o444, stage_pins[mode])
        recipe_path = ADOPTED / 'stages' / selected[1] / 'STAGE.json'
        recipe, recipe_pin = kernel.read_json(recipe_path, 1048576, 0o444)
        kernel.need(recipe_pin['sha256'] == selected[2], 'exact accepted full stage recipe')
        original = recipe['files']
        common='integration/candidate_entry.py' in declared['files']
        expected_members=set(original)|({'integration/candidate_entry.py'} if common else set())
        kernel.need(set(declared['files']) == expected_members and
                    all(declared['files'][name] == pin for name, pin in original.items() if name != 'JOBS.json'),
                    'every original full source/control/oracle byte and mode unchanged')
        jobs, jobs_pin = kernel.read_json(stage / 'JOBS.json', 65536, 0o444)
        selected_job=job_for(mode)
        if common:
            selected_job={k:v for k,v in selected_job.items() if k!='bootstrap'}
            selected_job['entry']='integration/candidate_entry.py'
            entry_source=Path(__file__).absolute().parent/'candidate_entry.py'
            entry_source_pin,unused=kernel.IO.read(entry_source,262144,0o444,materialize=False)
            kernel.need(declared['files']['integration/candidate_entry.py']=={'sha256':entry_source_pin['sha256'],'mode':0o444},
                        'actual enrolled waiting-entry source byte inverse')
            rows[str(entry_source)]=entry_source_pin
        kernel.need(jobs == {mode: selected_job} and
                    declared['files']['JOBS.json'] == {'sha256': jobs_pin['sha256'], 'mode': 0o444},
                    'sole JOBS change has an exact complete-command inverse')
        for relative, expected in declared['files'].items():
            kernel.need(type(relative) is str and not Path(relative).is_absolute() and
                        '..' not in Path(relative).parts, 'exact relative full source member')
            path = stage / relative
            pin, unused = kernel.IO.read(path, 67108864, expected['mode'], materialize=False)
            kernel.need(pin['sha256'] == expected['sha256'], 'unchanged full payload member')
            rows[str(path)] = pin
        # Compare the reached command with the original accepted command DATA.
        original_commands = [row for row in commands['commands'] if row['role'] == selected[4]]
        kernel.need(len(original_commands) == 1, 'one adopted original command for full role')
        command = original_commands[0]
        old_stage = ROOT / 'stages' / ('s03-r6-' + selected[1])
        old_output = ROOT / 'runtime/runs' / ('s03-r6-' + selected[1] + ('-O' if selected[5] else '')) / 'science'
        projected = [str(stage) + value[len(str(old_stage)):] if value == str(old_stage) or value.startswith(str(old_stage) + '/')
                     else str(R / 'runtime/completed-source' / NAME / (NAME + ('N' if mode == 'normal' else 'O')) / 'runner/artifact/science')
                     if value == str(old_output) else value for value in command['argv']]
        expected = command_for(stage, declared, mode, job_for(mode),
                    R / 'runtime/completed-source' / NAME / (NAME + ('N' if mode == 'normal' else 'O')) / 'runner/artifact/science')
        kernel.need(projected == expected and command['cwd'] == str(ROOT) and
                    command['optimize'] == int(selected[5]) and command['execution_authorized'] is False,
                    'exact original command/path/mode inverse')
        rows[str(stage / 'STAGE.json')] = actual
        rows[str(recipe_path)] = recipe_pin
        retained[mode] = {'manifest': actual, 'recipe': recipe_pin, 'declared': declared}
    for pin in (catalog_pin, manifest_pin, adoption_pin, commands_pin):
        rows[pin['path']] = pin
    return {'manifest': retained['normal']['manifest'], 'files': rows, 'stages': retained,
            'separate_fresh_baseline_source_route': baseline_command,
            'fresh_baseline_execution_or_comparison_completed': False}


def baseline_source_route(commands):
    """The retained original S10.02 full baseline invocation, never a grant.

    Its actual fresh result and typed transfer belong to the separately guarded
    original baseline/comparison activities.  No prior receipt or anchor is
    accepted as a current baseline by this complete candidate source route.
    """
    rows = [row for row in commands['commands'] if row['role'] == 'full:baseline']
    need(len(rows) == 1 and rows[0]['optimize'] == 0 and
         rows[0]['cwd'] == str(ROOT) and rows[0]['execution_authorized'] is False and
         BASELINE_SHA in rows[0]['argv'] and '--finite-only' not in rows[0]['argv'],
         'actual accepted independent full baseline source command')
    return rows[0]


def _artifact(kernel, path, expected_sha, expected_bytes=None):
    # Full scientific files include a 58MB witness.  OwnedIO streams in 64KiB
    # chunks without materialization; the complete command/validation bill pays
    # for all bytes.  The existing original budget bounds the operation.
    size = path.lstat().st_size
    kernel.need(type(size) is int and size >= 0, 'original scientific file size')
    pin, unused = kernel.IO.read(path, size)
    kernel.need(pin['sha256'] == expected_sha and
                (expected_bytes is None or pin['bytes'] == expected_bytes),
                'exact original full scientific bytes')
    return pin


def _relay(kernel, observation, paths):
    kernel.exact(observation, ('schema','cap_bytes_each','nonblocking_readers_only',
                 'fair_read_quantum_bytes','setup_complete','retired',
                 'all_descriptors_known_closed','eof_complete','overflow',
                 'raw_error_present','streams','writer_lifetime_proof'))
    kernel.need(observation['schema'] == 'joined-bounded-relay-v1' and
                type(observation['cap_bytes_each']) is int and observation['cap_bytes_each'] == 2097152 and
                observation['nonblocking_readers_only'] is True and
                type(observation['fair_read_quantum_bytes']) is int and observation['fair_read_quantum_bytes'] == 65536 and
                observation['setup_complete'] is True and observation['retired'] is True and
                observation['all_descriptors_known_closed'] is True and
                observation['eof_complete'] is True and observation['overflow'] is False and
                observation['raw_error_present'] is False and observation['writer_lifetime_proof'] is False and
                type(observation['streams']) is list and len(observation['streams']) == 2,
                'actual bounded fair relay completed; EOF is not lifetime authority')
    pins = []
    for stream,path in zip(observation['streams'],paths):
        kernel.exact(stream, ('path','bytes','observed_bytes','discarded_bytes','overflow','eof',
                             'final_bytes','write_uncertain','sha256'))
        pin, unused = kernel.IO.read(path, 2097152, 0o600)
        kernel.need(stream['path'] == str(path) and type(stream['bytes']) is int and
                    type(stream['observed_bytes']) is int and type(stream['final_bytes']) is int and
                    pin['bytes'] == stream['bytes'] == stream['observed_bytes'] == stream['final_bytes'] and
                    type(stream['discarded_bytes']) is int and stream['discarded_bytes'] == 0 and
                    stream['overflow'] is False and stream['write_uncertain'] is False and
                    stream['eof'] is True and pin['sha256'] == stream['sha256'],
                    'complete exact-limit/EOF/partial-write raw relay custody')
        pins.append(pin)
    return pins


def validate_terminal(kernel, case, layout, runner_receipt, supervision):
    """Validate only after real process cleanup; retain every raw original error.

    This is observational validation, not financial CLOSE, S10.03 acceptance,
    installed-image qualification, a compatibility flag or an execution grant.
    """
    mode = case['job']
    kernel.need(type(mode) is str and mode in SELECTIONS and
                case == case_for(mode, case['stage_sha256']), 'exact full case inverse')
    selected = SELECTIONS[mode]
    stage = STAGE_BASE / selected[0]
    declared, stage_pin = kernel.read_json(stage / 'STAGE.json', 1048576, 0o444)
    common='integration/candidate_entry.py' in declared['files']
    if common: common_entry_binding(kernel,case,layout,declared,runner_receipt)
    kernel.need(stage_pin['sha256'] == case['stage_sha256'] and
                (common or runner_receipt['command'] == command_for(stage, declared, mode, job_for(mode), layout.science_root)),
                'actual full terminal command/source differs')
    cleanup = supervision['cleanup']
    kernel.need(type(supervision['returncode']) is int and supervision['returncode'] == (1 if common and selected[5] else 0) and
                supervision['failure'] is None and
                cleanup['complete'] is True and cleanup['group_empty_proved'] is True and
                cleanup['remaining'] == [] and cleanup['observed_after_root_exit'] == [] and
                cleanup['reaped_adopted'] == [], 'genuine post-root terminal cleanup required')
    kernel.need(runner_receipt['status'] == ('STOP' if common and selected[5] else 'PASS') and
                type(runner_receipt['exit']) is int and runner_receipt['exit'] == (1 if selected[5] else 0) and
                runner_receipt['termination'] is None and
                runner_receipt['source_bytes_and_modes_unchanged'] is True and
                runner_receipt['retained_log_bytes_stable'] is True,
                'later failure or uncertain native terminal state defeats earlier science receipt')
    closure, closure_pin = kernel.read_json(layout.runner_root / 'WRITER-CLOSURE.json', 65536, 0o444 if common else 0o600)
    kernel.exact(closure, ('schema','launch_entered','launch_returned','wait_known','stdio_aliases_closed',
                          'process_group_empty','usage_inode_retired','local_holders_closed',
                          'domain_reconciliation_required','relay','error_type'))
    kernel.need(closure['schema'] == 'h25-runner-native-writer-closure-v2' and
                closure['launch_entered'] is True and closure['launch_returned'] is True and
                closure['wait_known'] is True and closure['stdio_aliases_closed'] is True and
                closure['process_group_empty'] is (False if common else True) and closure['usage_inode_retired'] is True and
                closure['local_holders_closed'] is True and closure['domain_reconciliation_required'] is True and
                closure['relay']['all_descriptors_known_closed'] is True and
                closure['relay']['eof_complete'] is True and closure['relay']['overflow'] is False and
                closure['relay']['raw_error_present'] is False and
                closure['error_type'] is None, 'genuine all-holder closure after original cleanup')
    _relay(kernel, closure['relay'], [layout.runner_root / 'stdout.txt',layout.runner_root / 'stderr.txt'])
    _relay(kernel, supervision['outer_relay'],
           [layout.supervision_root / 'root.stdout.raw',layout.supervision_root / 'root.stderr.raw'])
    raw_logs = {}
    for stream in ('stdout', 'stderr'):
        pin, raw = kernel.IO.read(layout.runner_root / (stream + '.txt'), 2097152, 0o600,
                                 materialize=selected[5] and stream == 'stderr')
        kernel.need(pin['sha256'] == runner_receipt[stream + '_sha256'] and
                    pin['bytes'] == runner_receipt[stream + '_bytes'] == runner_receipt[stream + '_final_bytes'],
                    'actual retained complete original stream differs')
        raw_logs[stream] = pin
        if selected[5] and stream == 'stderr':
            kernel.need(type(raw) is bytes and raw.startswith(b'Traceback (most recent call last):\n') and
                        raw.endswith(REFUSAL) and b'_epoch_sc4_full_entry' in raw and
                        b'STOP evidence write failed:' not in raw,
                        'original optimized full-entry refusal and raw traceback required')
    if selected[5]:
        kernel.need(not (layout.science_root / 'receipt.json').exists() and
                    not (layout.science_root / 'STOP.json').exists() and raw_logs['stdout']['bytes'] == 0,
                    'optimized full entry remains original refusal, never positive science')
        return {'schema': 'full-caller-terminal-observation-v1', 'role': selected[4],
                'status': 'ORIGINAL_OPTIMIZED_FULL_ENTRY_REFUSAL_OBSERVED',
                'raw_logs': raw_logs, 'writer_closure': closure_pin,
                'whole_outer_complete': False, 'original_retention_and_known_owner_release_still_required': True,
                'execution_permission': False, 'financial_close_issued': False}
    kernel.need(raw_logs['stderr']['bytes'] == 0 and not (layout.science_root / 'STOP.json').exists(),
                'full positive retains every original error and STOP refusal')
    receipt, receipt_pin = kernel.read_json(layout.science_root / 'receipt.json', 4194304)
    anchor, anchor_pin = kernel.read_json(stage / 'baseline/anchor.json', 65536, 0o444)
    kernel.need(receipt['status'] == 'FULL_NETWORK_COMPLETE_PASS' and receipt['mode'] == 'candidate' and
                receipt['lanes'] == 'candidate' and receipt['driver_sha256'] == selected[3] and
                receipt['data_handling']['full_caller_run'] is True and receipt['data_handling']['arm'] == 'candidate' and
                receipt['science'] == anchor['science'] and
                receipt['reference_driver_sha256'] == anchor['driver_sha256'] and
                receipt['source_pin_sha256'] == anchor['source_pin_sha256'],
                'complete original scientific/full-image/anchor disposition required')
    science, files = anchor['science'], {}
    for relative, expected in (
        ('runtime-root/certificates/complex-network.json', science['full_cli_certificate_sha256']),
        ('original-stdout.txt', science['full_cli_stdout_sha256']),
        ('full-return.lossless.json', science['full_return_lossless_sha256'])):
        files[relative] = _artifact(kernel, layout.science_root / relative, expected)
    side = science['side']
    for name, key, count in (('result.json', 'result_sha256', 'result'),
                             ('witness.json', 'exact_witness_sha256', 'witness'),
                             ('rank-trace.json', 'rank_trace_sha256', 'rank_trace')):
        relative = 'side-observations/' + name
        files[relative] = _artifact(kernel, layout.science_root / relative, side[key], side['serialized_bytes'][count])
    complement, complement_pin = kernel.read_json(layout.science_root / 'complement-transcript.json', 65536)
    kernel.need(complement == science['ordered_complements'], 'exact ordered complement observations')
    kernel.need(kernel.IO.read(layout.science_root / 'receipt.json', 4194304)[0] == receipt_pin,
                'full receipt changed across terminal scientific verification')
    return {'schema': 'full-caller-terminal-observation-v1', 'role': selected[4],
            'status': 'ORIGINAL_FULL_CANDIDATE_TERMINAL_OBSERVED', 'receipt': receipt_pin,
            'anchor': anchor_pin, 'scientific_files': files, 'complement': complement_pin,
            'raw_logs': raw_logs, 'writer_closure': closure_pin,
            'original_live_SC4_disposition_required_before_zero_exit': True,
            'whole_outer_complete': False, 'original_retention_and_known_owner_release_still_required': True,
                'execution_permission': False, 'financial_close_issued': False}
