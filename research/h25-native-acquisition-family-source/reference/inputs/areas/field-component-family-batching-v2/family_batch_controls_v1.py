"""Concrete control bodies; every case unexecuted and requires an actual owner.

Positive bodies use actual independently admitted sources, genuine child stages,
original source predicates and complete expected scenario expansion. This file
contains no manufactured212-family fixtures and runs nothing on import.
"""
import epoch_schema_v5 as schema
import family_batching_v1 as batching

CONTROL_CONFIGURATION = None
_USED = []
_ERRORS = []


def _consume(case):
    schema.exact(CONTROL_CONFIGURATION, ('schema', 'review_sha256', 'cases'))
    schema.text(CONTROL_CONFIGURATION['schema'], 64)
    schema.need(CONTROL_CONFIGURATION['schema'] == 'h25-family-batch-control-config-v1', 'unconfigured controls')
    schema.digest(CONTROL_CONFIGURATION['review_sha256'])
    schema.label(case)
    schema.need(case not in _USED, 'control consumed')
    _USED.append(case)


def _check_expected_error(case, error, state=None):
    expected = CONTROL_CONFIGURATION['cases'][case]
    schema.exact(expected, ('error_type', 'error_args', 'checkpoint', 'completed_cases', 'require_native_pending'))
    classes = {'EpochStop': schema.EpochStop, 'RuntimeError': RuntimeError, 'ValueError': ValueError,
               'TypeError': TypeError, 'KeyError': KeyError}
    schema.need(type(expected['error_type']) is str and expected['error_type'] in classes and
        type(error) is classes[expected['error_type']], 'negative observed an earlier/different rejection class')
    arguments = BaseException.__dict__['args'].__get__(error, BaseException)
    schema.need(batching._equal(arguments, batching._expected_literal(expected['error_args'],[0])),
                'negative observed an earlier/different rejection predicate')
    if state is not None:
        schema.need(state['checkpoint'] == expected['checkpoint'] and
            len(state['captured']) == expected['completed_cases'], 'negative did not reach its required paid boundary')
        if expected['require_native_pending'] is True:
            schema.need(state['pending'][0] is not None and 'native' in state['pending'][0],
                        'negative lacks actual owned raw-before-oracle evidence')
    return None


def positive_original_case(owner):
    _consume('positive-original-case')
    observation = batching.run_next_envelope(owner)
    schema.need(observation['family_completion'] is False and observation['complete_finite_union'] is False,
                'unit envelope invented completion')
    return observation


def positive_complete_family(owner, identity):
    _consume('positive-complete-family')
    token = batching.seal_family(owner, identity)
    state = batching._entry(owner)
    schema.need(state['families'][identity][0] is token, 'actual live family token identity differs')
    return {'family': identity, 'actual_current_complete_case_count': len(state['catalog']['families'][identity]['required_cases']),
            'full_finite_union': False, 'restorable': False}


def positive_complete_mode(owner):
    _consume('positive-complete-mode')
    token = batching.finish_mode(owner)
    schema.need(token is batching._entry(owner)['mode_token'], 'actual full212 live component capability absent')
    return {'actual_families': 212, 'full_six_area_finite': False, 'restorable': False}


def expected_rejection(case, owner, identity=None):
    """Each negative requires an independently reviewed wrong-input plan/context.

    No live source/owner mutation occurs in the control. Other predicates and
    positive context must be valid so an earlier gate cannot fake the rejection.
    """
    schema.need(type(case) is str and case in ('missing-scenario', 'duplicate-case', 'replayed-generation', 'wrong-role',
        'wrong-mode', 'wrong-source', 'wrong-process-generation', 'early-reject-for-later-fault',
        'missing-full-raw', 'child-oracle-bit-only', 'incomplete-cleanup', 'opaque-identity-unavailable',
        'native-delivery-not-proven', 'bodyless-family', 'partial-unit-family', 'batch-over180',
        'batch-over1GiB', 'same-science-lock', 'case-tail-omitted', 'wrong-global-order'), 'unknown negative')
    _consume(case)
    try:
        if case in ('missing-scenario', 'bodyless-family', 'partial-unit-family'):
            batching.seal_family(owner, identity)
        else:
            batching.run_next_envelope(owner)
    except BaseException as error:
        _ERRORS.append(error)
        state = batching._entry(owner)
        _check_expected_error(case, error, state)
        schema.need(state['primary'][0] is error and state['original']['unknown_owner']['primary'][0] is error and
            state['original']['unknown_owner']['quarantine'][0] is True and state['phase'] == 'STOP',
            'actual first primary/quarantine not preserved')
        return {'case': case, 'actual_stop': True, 'error_retained': True, 'family_completion': False}
    raise schema.EpochStop('incorrect batch/family input was admitted')


def wrong_constructor(case, original_parent, replay_owner, orchestrator):
    schema.need(type(case) is str and case in ('more-than256-envelopes', 'more-than2-children', 'unknown-body-in-catalog',
        'duplicate-context', 'wrong-current-template', 'unreviewed-fit', 'fit-tail-over-parent',
        'optimized-before-normal', 'case-program-from-child-oracle'), 'unknown constructor control')
    _consume(case)
    try:
        batching.make_family_owner(original_parent, replay_owner, orchestrator)
    except BaseException as error:
        _ERRORS.append(error)
        _check_expected_error(case, error)
        schema.need(batching.parent._UNKNOWN_OWNER['primary'][0] is error and
            batching.parent._UNKNOWN_OWNER['quarantine'][0] is True, 'constructor lost first actual primary')
        return {'case': case, 'actual_constructor_stop': True, 'family_completion': False}
    raise schema.EpochStop('incorrect constructor was admitted')


def reject_saved_token(owner, saved_record):
    _consume('saved-record-is-not-capability')
    try:
        batching.consume_component_union(owner, saved_record)
    except BaseException as error:
        _ERRORS.append(error)
        _check_expected_error('saved-record-is-not-capability', error, batching._entry(owner))
        schema.need(batching._entry(owner)['primary'][0] is error, 'restored-token primary lost')
        return {'actual_saved_record_rejected': True, 'restorable': False}
    raise schema.EpochStop('saved record restored authority')
