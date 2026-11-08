"""Additive FB01-FB03 controls, all UNEXECUTED; no mutation or toy fixtures.

The actual caller must supply separately admitted positive and negative source
contexts. Expected exact errors/checkpoints prevent an earlier gate from being
counted as the intended rejection. Original33 bodies remain byte-identical.
"""
import sys
import types
import epoch_schema_v5 as schema
import family_batching_v1 as batching
import source_bindings_v3 as bindings
import h25_parent_supervisor as supervisor

CONTROL_CONFIGURATION = None
_USED = []
_ERRORS = []


def _consume(case):
    schema.exact(CONTROL_CONFIGURATION, ('schema','review_sha256','cases'))
    schema.need(CONTROL_CONFIGURATION['schema'] == 'h25-family-batch-additive-controls-v2', 'new controls unconfigured')
    schema.digest(CONTROL_CONFIGURATION['review_sha256'])
    schema.need(type(case) is str and case in CONTROL_CONFIGURATION['cases'] and case not in _USED,
                'new control missing/already consumed')
    _USED.append(case)
    return CONTROL_CONFIGURATION['cases'][case]


def positive_global_raw_judgment(owner):
    _consume('positive-authenticated-globals-through-independent-raw')
    state = batching._entry(owner); before = len(state['captured'])
    observed = batching.run_next_envelope(owner)
    schema.need(len(state['captured']) > before and state['checkpoint'] == 'DURABLE_JUDGMENT' and
        all(row['observed']['raw_pins'] and row['observed']['family_completion'] is False
            for row in state['captured'].values()) and observed['family_completion'] is False,
        'positive did not pass borrowed validator and reach independent RAW judgment')
    guard = supervisor._GUARD_ATTEMPTS[-1]
    schema.need(guard['phase'] == 'CONSUMED_RELEASE' and guard['checkpoint'] == 'CHILD_CONSUMED_RELEASE' and
        guard['live'] is not None and guard['request_pin'] is not None and guard['ack_pin'] is not None and
        guard['consume_pin'] is not None, 'positive lacks actual before-target parent release')
    return observed


def inspect_actual_imports(case, original_parent):
    expected = _consume(case)
    schema.need(case in ('positive-original-wrapper-dotted-import','positive-package-submodule-alias-symbol',
        'negative-substituted-package','negative-substituted-submodule','negative-substituted-alias',
        'negative-substituted-from-symbol'), 'unknown actual import control')
    original = batching.parent._state(original_parent); batching.parent._guard(original)
    schema.exact(expected, ('module','source','expect_stop','error_args'))
    module = sys.modules[expected['module']]
    raw = batching.copying.read_verified_complete_v3(expected['source'],8388608,error_owner=original['errors'])
    modules = {k:v for k,v in tuple(sys.modules.items()) if type(k) is str and type(v) is types.ModuleType}
    # A fake-map negative must be supplied by an independently reviewed actual
    # caller/job; this body never fabricates the source-module inventory itself.
    try:
        tree,functions,classes,imports = bindings._source_objects(module,expected['source'],raw,modules)
        bindings._imports_unchanged(imports)
    except BaseException as error:
        _ERRORS.append(error)
        schema.need(expected['expect_stop'] is True and type(error) is bindings.BindingStop and
            batching._equal(BaseException.__dict__['args'].__get__(error,BaseException),
                batching._expected_literal(expected['error_args'],[0])), 'earlier/wrong import rejection')
        return {'case':case,'actual_rejection':True,'runtime_admission':False}
    schema.need(expected['expect_stop'] is False and bool(imports), 'substituted import context admitted')
    return {'case':case,'actual_real_namespace_imports':len(imports),'runtime_admission':False}


def expected_guard_or_global_rejection(case, owner):
    expected = _consume(case)
    schema.need(case in ('negative-launch-flags-missing','negative-launch-flags-substituted',
        'negative-borrowed-global-substituted','negative-borrowed-literal-mutated',
        'negative-request-generation-not-live','negative-request-wrong-context','negative-request-wrong-source',
        'negative-request-wrong-case-mode-action','negative-request-reused-nonce',
        'negative-ack-missing','negative-ack-stale','negative-ack-wrong-parent','negative-ack-wrong-request',
        'negative-ack-duplicate','negative-ack-timedout','negative-ack-reused-generation',
        'negative-ack-after-child-exit','negative-postexit-observation-without-ack'), 'unknown guard/global control')
    schema.exact(expected, ('error_type','error_args','checkpoint','guard_checkpoint','ack_published'))
    try:
        batching.run_next_envelope(owner)
    except BaseException as error:
        _ERRORS.append(error); state=batching._entry(owner)
        classes={'EpochStop':schema.EpochStop,'RuntimeError':RuntimeError,'BindingStop':bindings.BindingStop}
        schema.need(type(expected['error_type']) is str and type(error) is classes[expected['error_type']] and
            batching._equal(BaseException.__dict__['args'].__get__(error,BaseException),
                batching._expected_literal(expected['error_args'],[0])) and state['checkpoint']==expected['checkpoint'],
            'earlier/wrong global/guard failure')
        if expected['guard_checkpoint'] is not None:
            guard=supervisor._GUARD_ATTEMPTS[-1]
            schema.need(guard['phase']=='STOP' and guard['checkpoint']==expected['guard_checkpoint'] and
                guard['primary'][0] is error and type(expected['ack_published']) is bool and
                (guard['ack_pin'] is not None) is expected['ack_published'],
                'negative lacks actual exact before-target guard checkpoint/error custody')
        schema.need(state['primary'][0] is error and state['original']['unknown_owner']['primary'][0] is error and
            state['original']['unknown_owner']['quarantine'][0] is True and state['phase']=='STOP',
            'negative lost actual primary/quarantine')
        return {'case':case,'actual_stop':True,'target_release_not_assumed':True,'full_family':False}
    raise schema.EpochStop('incorrect guard/global input admitted')


def reject_nonreal_module_inventory(original_parent, supplied_modules):
    expected = _consume('negative-fake-module-map')
    original=batching.parent._state(original_parent); batching.parent._guard(original)
    schema.exact(expected, ('module','source','error_args'))
    module=sys.modules[expected['module']]
    raw=batching.copying.read_verified_complete_v3(expected['source'],8388608,error_owner=original['errors'])
    try:
        bindings._source_objects(module,expected['source'],raw,supplied_modules)
    except BaseException as error:
        _ERRORS.append(error)
        schema.need(type(error) is bindings.BindingStop and
            batching._equal(BaseException.__dict__['args'].__get__(error,BaseException),
                batching._expected_literal(expected['error_args'],[0])), 'wrong fake-inventory rejection')
        return {'actual_fake_inventory_rejected':True,'production_map_never_fabricated':True}
    raise schema.EpochStop('nonreal module inventory was admitted')
