"""Receipt requirements for the exact accepted initial-five amendment.

This validates supplied observations only. It neither reruns nor reorders the
old controls, calls a TCB verifier, or certifies that an api0 call happened.
Placement/call identity is a separate source-admission obligation. A failure
must prevent cold capture/field setup; partial fixture evidence must survive.
"""
from receipt_contract_v1 import need

AMENDMENT_SHA256 = 'e79a7a8de137c20f9c80d6a84794646a617924b8b37a407a786c9bf5ab737e26'
OLD_FIVE = ('TCB-positive-initial-native-closure', 'TCB-wrong-file-digest',
            'TCB-missing-declared-map', 'TCB-root-hash-alias', 'TCB-isolated-reader-file-drift')


def validate_restoration(initial, old_controls, restoration, expected_files, expected_hashlib_origin,
                         expected_root_digest, literal_file_count):
    need(type(expected_files) is tuple and type(literal_file_count) is int and
         len(expected_files) == literal_file_count and literal_file_count > 0,
         'restoration literal expected inventory')
    need(type(old_controls) is dict and old_controls.get('schema') == 'h25-native-tcb-controls-v1' and
         type(old_controls.get('expected_records')) is int and old_controls['expected_records'] == 5,
         'restoration original five census')
    rows = old_controls.get('records')
    need(type(rows) is list and len(rows) == 5 and all(type(row) is dict for row in rows) and
         tuple(row.get('case') for row in rows) == OLD_FIVE, 'restoration original five order')
    need(type(old_controls.get('scientific_calls')) is int and old_controls['scientific_calls'] == 0 and
         type(old_controls.get('probe_native_imports')) is int and old_controls['probe_native_imports'] == 0,
         'restoration original five scope')
    for row, fragment in zip(rows[1:], ('file digest differs', 'mapped file closure differs',
                                       'Bootstrap/provider global changed', 'file changed during hashing')):
        need(type(row.get('rejection')) is str and fragment in row['rejection'], 'restoration original rejection evidence')
    need(rows[3].get('corrupt_function_executed') is False and
         rows[4].get('system_native_files_mutated') is False, 'restoration original control boundary')
    for receipt in (initial, rows[0].get('receipt'), restoration):
        need(type(receipt) is dict and receipt.get('schema') == 'h25-initial-native-tcb-v1' and
             receipt.get('status') == 'MATCHED_DECLARED_INITIAL_NATIVE_FILES', 'restoration positive status')
        need(type(receipt.get('declared_file_count')) is int and receipt['declared_file_count'] == literal_file_count,
             'restoration positive literal file count')
        need(receipt.get('probe_private_abi_access') is False and receipt.get('reusable_pass') is False and
             receipt.get('scientific_admission') is False and receipt.get('executable_mappings_stable') is True,
             'restoration corroboration boundary')
        need(receipt.get('root_source_sha256') == expected_root_digest and
             receipt.get('hashlib_origin') == expected_hashlib_origin and
             receipt.get('hash_function_owned_by_root_module') is True, 'restoration original provider identity')
        files = receipt.get('files')
        need(type(files) is list and len(files) == literal_file_count, 'restoration observed file census')
        for observed, expected in zip(files, expected_files):
            need(type(observed) is dict and type(expected) is tuple and len(expected) == 3 and
                 observed.get('path') == expected[0] and
                 observed.get('expected_sha256') == observed.get('observed_sha256') == expected[1] and
                 type(observed.get('expected_bytes')) is int and type(observed.get('observed_bytes')) is int and
                 observed['expected_bytes'] == observed['observed_bytes'] == expected[2] and
                 type(observed.get('executable_mapping_count')) is int and observed['executable_mapping_count'] > 0,
                 'restoration independently fixed file observation')
        total = sum(row[2] for row in expected_files)
        need(type(receipt.get('expected_total_file_bytes')) is int and
             type(receipt.get('observed_total_file_bytes')) is int and
             receipt['expected_total_file_bytes'] == receipt['observed_total_file_bytes'] == total,
             'restoration fixed byte total')
    # Fresh evidence is not required to have identical map hashes: transient
    # ordinary nonnative mappings can differ. Native file identities must match.
    for key in ('pid', 'hashlib_module_id', 'hash_function_id'):
        need(type(initial.get(key)) is int and initial[key] == restoration.get(key),
             'restoration process/provider continuity')
    need(restoration is not initial and restoration is not rows[0]['receipt'], 'restoration must be separate fresh receipt')
    return restoration


def validate_pre_field_stop(receipt):
    """No universal cleanup claim: failure may leave a partial private file."""
    need(type(receipt) is dict and receipt.get('status') == 'STOP' and
         receipt.get('cold_capture_started') is False and receipt.get('field_setup_started') is False and
         receipt.get('service_load_attempts') == 0 and type(receipt.get('service_load_attempts')) is int,
         'pre-field failure must stop before setup')
    need(type(receipt.get('primary_error')) is dict and
         type(receipt['primary_error'].get('type')) is str and
         type(receipt['primary_error'].get('message')) is str and
         type(receipt.get('cleanup_failures')) is list and
         type(receipt.get('partial_fixture_paths')) is list,
         'pre-field failure retains primary/cleanup/partial fixture evidence')
    return receipt
