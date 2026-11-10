"""Source-derived original receipt predicates; no controls are executed here.

The exact original _check_controls body is retained, with only an explicit
child optimization integer and literal native status expansion.  This
replays the existing result predicates, not the underlying native tests.
"""
from epoch_schema_v5 import need

EXPECTED_CACHE_TRANSCRIPT_RECORDS = 155

EXPECTED_V7_CONSUMER_CASES = ('source-before-native', 'source-before-trace', 'builtin-before-native', 'builtin-shadow-and-key-cleanup', 'row-calling-environment-full-and-light', 'row-key-first-error-and-cleanup', 'actual-row-native-observation', 'cold-_code_named-code', 'cold-_code_named-defaults', 'cold-_code_named-globals', 'cold-_check_factory_environment-code', 'cold-_check_factory_environment-defaults', 'cold-_check_factory_environment-globals', 'final-class-__init__-code', 'final-class-__init__-defaults', 'final-class-__init__-closure', 'final-class-check-code', 'final-class-check-defaults', 'final-class-check-closure', 'final-class-check_backend-code', 'final-class-check_backend-defaults', 'final-class-check_backend-closure', 'unregistered-final-subclass', 'restored-final-class-binds')

EXPECTED_V8_CALLER_CASES = ('cold-dispatcher-code', 'cold-dispatcher-defaults', 'cold-dispatcher-kwdefaults', 'cold-dispatcher-closure', 'runtime-dispatcher-code', 'runtime-dispatcher-defaults', 'runtime-dispatcher-kwdefaults', 'runtime-dispatcher-closure', 'runtime-collector-code', 'runtime-collector-defaults', 'runtime-collector-kwdefaults', 'runtime-collector-closure')

EXPECTED_AUTHORITY_CONTROL_CASES = ('A1-authority-entry-and-helper-fields', 'A2-caller-dispatcher-fields', 'A3-every-owned-module-helper', 'A4-registered-product-methods-and-closure-helpers', 'A5-foreign-key-failure-disposal', 'A6-runtime-child-dispatcher-and-helper-fields')

_CONTROL_CONTRACT = {'cache_counts': {'binding_rejections': 12,
                  'cases': 29,
                  'requests': 71,
                  'source_admission_rejections': 2,
                  'tamper_rejections': 1,
                  'unsupported_rejections': 2},
 'construction_normal_names': ['complete-constructor-h8',
                               'complete-constructor-h9',
                               'exact-add-0',
                               'exact-add-1',
                               'exact-add-2',
                               'exact-add-3',
                               'exact-add-4',
                               'exact-add-5',
                               'exact-add-6',
                               'exact-add-7',
                               'exact-add-8',
                               'exact-add-9',
                               'exact-add-10',
                               'overlap-assertion-matching-mode',
                               'negative-index',
                               'index-outside',
                               'none-index',
                               'float-index',
                               'bool-index',
                               'unhashable-kind',
                               'mask-callback',
                               'index-callback',
                               'kind-callback',
                               'support-callback',
                               'lookup-callback',
                               'unarmed-construction-remains-incremental',
                               'retired-complete-index-and-private-snapshot',
                               'resumed-run-loses-frozen-tail-qualification',
                               'resumed-duplicate-restores-same-dictionary',
                               'reinitialized-run-loses-qualification-h8',
                               'retired-object-literal-reinitialization-h8',
                               'reinitialized-run-loses-qualification-h9',
                               'retired-object-literal-reinitialization-h9',
                               'reinitialized-run-loses-qualification-h7',
                               'retired-object-literal-reinitialization-h7',
                               'resumption-restores-original-index-after-graph-edits',
                               'lookup-entry-mutation',
                               'lookup-replacement',
                               'snapshot-binding',
                               'double-finalize',
                               'wrong-finalizer',
                               'factory-rejects-changed-original-add',
                               'factory-rejects-source-builtin-shadow',
                               'seal-rejects-late-add-replacement',
                               'scope-cannot-be-rearmed',
                               'hook-bearing-constructor-trace',
                               'hook-bearing-constructor-profile',
                               'hook-bearing-constructor-gc',
                               'hook-bearing-constructor-thread',
                               'hook-bearing-constructor-signal',
                               'hook-bearing-constructor-monitoring',
                               'invalid-dimension-original-assertion',
                               'malformed-complete-index-before-clear',
                               'generic-subclass-add-fallback',
                               'factory-rejects-original-defaults',
                               'factory-rejects-original-code',
                               'factory-rejects-original-helper',
                               'factory-rejects-original-descriptor',
                               'owner-rejects-changed-wrapper-defaults',
                               'public-total-helper-restores-before-add',
                               'p1-original-authentication-and-final-wrapper-composition'],
 'construction_optimized_names': ['complete-constructor-h8',
                                  'complete-constructor-h9',
                                  'exact-add-0',
                                  'exact-add-1',
                                  'exact-add-2',
                                  'exact-add-3',
                                  'exact-add-4',
                                  'exact-add-5',
                                  'exact-add-6',
                                  'exact-add-7',
                                  'exact-add-8',
                                  'exact-add-9',
                                  'exact-add-10',
                                  'overlap-assertion-matching-mode',
                                  'negative-index',
                                  'index-outside',
                                  'none-index',
                                  'float-index',
                                  'bool-index',
                                  'unhashable-kind',
                                  'mask-callback',
                                  'index-callback',
                                  'kind-callback',
                                  'support-callback',
                                  'lookup-callback',
                                  'unarmed-construction-remains-incremental',
                                  'retired-complete-index-and-private-snapshot',
                                  'resumed-run-loses-frozen-tail-qualification',
                                  'resumed-duplicate-restores-same-dictionary',
                                  'reinitialized-run-loses-qualification-h8',
                                  'retired-object-literal-reinitialization-h8',
                                  'reinitialized-run-loses-qualification-h9',
                                  'retired-object-literal-reinitialization-h9',
                                  'reinitialized-run-loses-qualification-h7',
                                  'retired-object-literal-reinitialization-h7',
                                  'resumption-restores-original-index-after-graph-edits',
                                  'lookup-entry-mutation',
                                  'lookup-replacement',
                                  'snapshot-binding',
                                  'double-finalize',
                                  'wrong-finalizer',
                                  'factory-rejects-changed-original-add',
                                  'factory-rejects-source-builtin-shadow',
                                  'seal-rejects-late-add-replacement',
                                  'scope-cannot-be-rearmed',
                                  'hook-bearing-constructor-trace',
                                  'hook-bearing-constructor-profile',
                                  'hook-bearing-constructor-gc',
                                  'hook-bearing-constructor-thread',
                                  'hook-bearing-constructor-signal',
                                  'hook-bearing-constructor-monitoring',
                                  'malformed-complete-index-before-clear',
                                  'generic-subclass-add-fallback',
                                  'factory-rejects-original-defaults',
                                  'factory-rejects-original-code',
                                  'factory-rejects-original-helper',
                                  'factory-rejects-original-descriptor',
                                  'owner-rejects-changed-wrapper-defaults',
                                  'public-total-helper-restores-before-add',
                                  'p1-original-authentication-and-final-wrapper-composition'],
 'inventory_cases': [['valid', 'value'],
                     ['list-pins', 'value'],
                     ['wrong-digest', 'error'],
                     ['missing', 'error'],
                     ['extra', 'error'],
                     ['extra-nonexact', 'value'],
                     ['symlink', 'error'],
                     ['root-symlink', 'error'],
                     ['changed-mode', 'value'],
                     ['fresh-call-after-mutation', 'error'],
                     ['restored', 'value']],
 'rank_guard_mutation_names': ['__code__',
                               '__defaults__',
                               '__kwdefaults__',
                               '_LEN',
                               '_GET',
                               '_MAX_ENTRIES',
                               'make_row_interner',
                               'make_runtime_guard',
                               'builtin/len',
                               'builtin/int',
                               'cell/exact_int',
                               'cell/exact_tuple',
                               'cell/exact_type',
                               'cell/get',
                               'cell/length',
                               'cell/max_entries',
                               'cell/max_rows',
                               'cell/max_value',
                               'cell/missing',
                               'cell/table',
                               'empty-cell'],
 'serialization_names': ['ordinary',
                         'empty',
                         'rows-1',
                         'rows-1023',
                         'rows-1024',
                         'rows-1025',
                         'rows-2048',
                         'byte-bound-169',
                         'byte-bound-170',
                         'byte-bound-171',
                         'scalars-unicode-wide',
                         'wide-unlimited',
                         'wide-digit-error',
                         'interned-rank-rows',
                         'depth-30',
                         'depth-33',
                         'circular',
                         'callback-list',
                         'callback-dict',
                         'callback-error',
                         'int-subclass',
                         'unsupported-object',
                         'malformed-result',
                         'malformed-witness',
                         'malformed-rank',
                         'nonstring-supported-keys',
                         'expected-result_sha256',
                         'expected-exact_witness_sha256',
                         'expected-rank_trace_sha256',
                         'expected-rank_call_count',
                         'expected-rank_distinct_matrix_count',
                         'failure-stage_create',
                         'failure-stage_open',
                         'failure-stage_write',
                         'failure-stage_flush',
                         'failure-stage_after_close',
                         'failure-stage_hash',
                         'failure-final_open-result.json',
                         'failure-final_write-result.json',
                         'failure-final_flush-result.json',
                         'failure-final_after_close-result.json',
                         'failure-final_open-witness.json',
                         'failure-final_write-witness.json',
                         'failure-final_flush-witness.json',
                         'failure-final_after_close-witness.json',
                         'failure-final_open-rank-trace.json',
                         'failure-final_write-rank-trace.json',
                         'failure-final_flush-rank-trace.json',
                         'failure-final_after_close-rank-trace.json',
                         'short-final-0',
                         'short-final-1',
                         'copy-corrupt-content',
                         'stage-mutated-size',
                         'copy-read-error',
                         'copy-hash-error',
                         'cleanup-unlink-error',
                         'cleanup-rmdir-error',
                         'primary-plus-close-error',
                         'primary-plus-manifest-error',
                         'drift-reference_global',
                         'drift-json_default',
                         'drift-expected_value',
                         'drift-effective_builtin',
                         'drift-json_global_shadow',
                         'drift-keyword_default',
                         'exit-json-drift',
                         'fallback-exit-json-drift',
                         'existing-finals',
                         'state-mutation-between-writes',
                         'path-subclass-fallback']}

DATA_CONTROL_STATUS = {
    'construction': 'PASS',
    'serialization': 'SERIALIZATION_FINITE_PASS',
    'cache_validity': 'PASS',
    'cold_authority': 'PASS',
    'rank_metadata': 'AREA6_METADATA_HELPER_CONTROLS_PASS',
    'rank_native': 'NATIVE_OBSERVATION_DIFFERENTIAL_CONTROLS_PASS',
    'inventory': 'INVENTORY_DIFFERENTIAL_CONTROLS_PASS',
    'combined_composition': 'BOUNDED_COMBINED_COMPOSITION_PASS',
    'cache_reference_v3': 'PASS',
    'native_initial_tcb': 'NATIVE_INITIAL_TCB_CONTROLS_PASS',
    **{'native_probe': 'NATIVE_METADATA_CONTROLS_PASS', 'bootstrap_preload': 'BOOTSTRAP_PRELOAD_CONTROLS_PASS', 'bootstrap_late': 'BOOTSTRAP_LATE_CONTROL_PASS', 'native_metadata': 'PASS', 'native_fields': 'SOURCE_CONTROL_OBSERVATIONS_COMPLETE_RUNTIME_GATE_OPEN'},
}

def check_original_control_union(state, optimize, *, include_late=False):
    controls = state['controls']
    expected_status = {name: status for name, status in DATA_CONTROL_STATUS.items()
                       if include_late or name != 'bootstrap_late'}
    need(set(controls) == set(expected_status), 'Complete data control union missing')
    for name, expected in expected_status.items():
        need(type(controls[name]) is dict and controls[name].get('status') == expected,
             'Data control did not pass: ' + name)
    expected_names = _CONTROL_CONTRACT['construction_optimized_names' if optimize else 'construction_normal_names']
    construction = controls['construction']
    need(construction.get('schema') == 'h25-construction-controls-v2' and
         construction.get('cases') == len(expected_names) and
         construction.get('optimized') is bool(optimize) and
         [row['name'] for row in construction.get('controls', [])] == expected_names and
         all(row['status'] == 'PASS' for row in construction['controls']),
         'Exact construction control census changed')
    serialization = controls['serialization']
    need(serialization.get('case_count') == 70 and serialization.get('optimization') == optimize and
         [row['case'] for row in serialization.get('cases', [])] == _CONTROL_CONTRACT['serialization_names'],
         'Exact serialization control census changed')
    cache_counts = dict(_CONTROL_CONTRACT['cache_counts'], cases=30, requests=74)
    cache = controls['cache_validity']
    need(cache.get('counts') == cache_counts and
         type(EXPECTED_CACHE_TRANSCRIPT_RECORDS) is int and
         cache.get('transcript_record_count') == EXPECTED_CACHE_TRANSCRIPT_RECORDS and
         cache.get('native_consumer_case_count') == 10 and
         cache.get('native_consumer_cases') == [
             'empty-first-result-authority', 'offhash-foreign-key', 'offhash-value-resize',
             'eligible-native-exit-unsupported', 'provider-function-binding',
             'binding-inspect-code', 'binding-inspect-defaults', 'isolated-module-close',
             'teardown-validation-rejection', 'teardown-attempted-native-accounting-rejection'],
         'Exact retained native-consumer control census changed')
    need(cache.get('v6_consumer_case_count') == 18 and
         len(cache.get('v6_consumer_cases', [])) == 18, 'Exact additive v6 control count changed')
    need(type(EXPECTED_V7_CONSUMER_CASES) is tuple and
         cache.get('v7_consumer_case_count') == len(EXPECTED_V7_CONSUMER_CASES) and
         cache.get('v7_consumer_cases') == list(EXPECTED_V7_CONSUMER_CASES),
         'Exact additive V7 control census is unconfigured or changed')
    need(type(EXPECTED_V8_CALLER_CASES) is tuple and
         cache.get('v8_caller_case_count') == len(EXPECTED_V8_CALLER_CASES) and
         cache.get('v8_caller_cases') == list(EXPECTED_V8_CALLER_CASES),
         'Exact additive V8 caller control census is unconfigured or changed')
    authority_controls = controls['cold_authority']
    authority_rows = authority_controls.get('records', [])
    need(authority_controls.get('schema') == 'h25-cold-authority-controls-v7' and
         type(EXPECTED_AUTHORITY_CONTROL_CASES) is tuple and
         authority_controls.get('expected_records') == authority_controls.get('observed_record_count') == len(authority_rows) == 6 and
         [row['case'] for row in authority_rows] == list(EXPECTED_AUTHORITY_CONTROL_CASES) and
         all(type(row['expected_cases']) is int and type(row['observed_cases']) is int and
             row['expected_cases'] == row['observed_cases'] for row in authority_rows) and
         authority_controls.get('expected_subcases') == authority_controls.get('observed_subcases') ==
         sum(row['observed_cases'] for row in authority_rows) and
         authority_controls.get('scientific_calls') == authority_controls.get('native_private_calls') == 0,
         'Exact cold authority grouped and derived subcase census changed')
    metadata_native = controls['native_metadata']
    need(metadata_native.get('schema') == 'h25-native-metadata-controls-v3' and
         metadata_native.get('observed_record_count') == len(metadata_native.get('records', [])) == 16 and
         metadata_native.get('native_lifecycle_before') == metadata_native.get('native_lifecycle_after'),
         'Exact additive native metadata control census changed')
    need(controls['cache_reference_v3'].get('counts') == cache_counts,
         'Separate bounded v3 reference control census changed')
    initial_tcb = controls['native_initial_tcb']
    need(initial_tcb.get('schema') == 'h25-native-tcb-controls-v1' and
         len(initial_tcb.get('records', [])) == 5 and initial_tcb.get('expected_records') == 5 and
         initial_tcb.get('scientific_calls') == 0 and initial_tcb.get('probe_native_imports') == 0,
         'Initial native TCB control census changed')
    native_controls = controls['native_probe']
    need(native_controls.get('records') == 62 and
         native_controls['direct'].get('inspection_calls') == 58 and
         len(native_controls['direct'].get('records', [])) == 60 and
         len(native_controls.get('disarmed', [])) == 1 and len(native_controls.get('bounds', [])) == 1,
         'Native metadata direct/fixture census changed')
    need(len(controls['bootstrap_preload'].get('records', [])) == 21 and
         controls['bootstrap_preload'].get('scientific_calls') == 0, 'Bootstrap preload census changed')
    if include_late:
        need(state['native_packet']['late_completed'] is True and
             len(controls['bootstrap_late'].get('records', [])) == 1, 'Bootstrap late-last census changed')
    metadata = controls['rank_metadata']
    rows, guard, digests = metadata['rows'], metadata['guard'], metadata['digests']
    need(rows['status'] == 'ROW_METADATA_CONTROLS_PASS' and rows['event_fixture_count'] == 8 and
         rows['unsupported_cases'] == 9 and rows['table_cap_tested'] == 4096 and rows['callback_events'] == [],
         'Exact immutable-row control census changed')
    need(guard['status'] == 'OBSERVATION_GUARD_CONTROLS_PASS' and guard['base_check_calls'] == 43 and
         len(guard['mutations']) == 21 and
         {row[0] for row in guard['mutations']} == set(_CONTROL_CONTRACT['rank_guard_mutation_names']),
         'Exact observation-guard control census changed')
    need(digests['status'] == 'DIGEST_SNAPSHOT_CONTROLS_PASS' and
         digests['declared_fixture_bytes'] == 2097172 and digests['same_snapshot_sha_calls'] == 3 and
         digests['stream_request_bytes'] == [1048576] * 4 and
         digests['read_once_same_snapshot'] is True and digests['fresh_after_mutation'] is True,
         'Exact same-call digest control census changed')
    native = controls['rank_native']
    need(native['rank_events'] == 17 and len(native['outcomes']) == 18 and
         native['callbacks'] == ['basis.values', 'basis.values'] and
         native['counters'] == {'complement_native': 0, 'complement_fallback': 0,
                                'gram_native': 14, 'gram_fallback': 4},
         'Exact native observation control census changed')
    need([list(row) for row in controls['inventory']['cases']] == _CONTROL_CONTRACT['inventory_cases'],
         'Exact inventory control census changed')
    composition = controls['combined_composition']
    need(composition['height'] == 8 and composition['optimized'] == optimize and
         composition['arms'] == ['baseline', 'candidate'] and
         set(composition['files']) == {'result.json', 'witness.json', 'rank-trace.json', 'complements.json'} and
         composition['production_writer_expected_unchanged'] is True and
         composition['production_writer_executed'] is False and composition['full_h25_gate_passed'] is False,
         'Exact bounded composition scope changed')
