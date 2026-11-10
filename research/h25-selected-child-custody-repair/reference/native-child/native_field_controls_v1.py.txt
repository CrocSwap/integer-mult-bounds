"""Independent original-getter/id controls; SOURCE ONLY, UNEXECUTED.

Entry receives Root's previously caller-authenticated same-image new_fixture.
No imports or calls of a replacement collector, no production-token access,
no image loading, no class mutation, no expected-reference private corruption.
Each installed audit hook is permanently disabled and drops foreign cells.
"""
import builtins
import gc
import sys
from types import FunctionType
from receipt_contract_v1 import need, record, finish

FIELDS = ('__code__', '__globals__', '__builtins__', '__defaults__',
          '__kwdefaults__', '__closure__', '__dict__')
# These expectations are literal CPython observable events, not native outputs.
EVENTS = (('get:__code__', 'id'), ('id',), ('id',),
          ('get:__defaults__', 'id'), ('get:__kwdefaults__', 'id'),
          ('id',), ('id',))
CASE_IDS = (
    'match-code', 'match-globals', 'match-builtins', 'match-defaults',
    'match-kwdefaults', 'match-closure', 'match-dict',
    'none-defaults', 'none-kwdefaults', 'none-closure', 'lazy-dict',
    'getter-error-code', 'getter-error-defaults', 'getter-error-kwdefaults',
    'id-error-code', 'id-error-globals', 'id-error-builtins', 'id-error-defaults',
    'id-error-kwdefaults', 'id-error-closure', 'id-error-dict',
    'dispose-defaults', 'dispose-kwdefaults', 'dispose-dict',
    'error-dispose-defaults', 'error-dispose-kwdefaults', 'error-dispose-dict',
    'close-get-code', 'close-get-defaults', 'close-get-kwdefaults',
    'close-id-code', 'close-id-defaults', 'close-id-kwdefaults', 'close-id-dict',
    'argument-bool', 'argument-negative', 'argument-seven', 'argument-large',
    'argument-int-subclass', 'argument-function-wrong', 'argument-arity',
    'unbound', 'bind-duplicate', 'bind-tuple-subclass', 'bind-id-wrapper',
    'bind-getter-wrapper', 'bind-function-type', 'bind-token-subclass',
    'close-wrong-token', 'close-before-events', 'gc-tracked', 'gc-foreign-cycle')
NORMAL_CASE_COUNT = 52
OPTIMIZED_CASE_COUNT = 52


class ControlFault(Exception):
    pass


class TupleField(tuple):
    def __new__(cls, log):
        result = tuple.__new__(cls, (17,))
        result.log = log
        return result
    def __del__(self):
        self.log.append('dispose')


class DictField(dict):
    def __init__(self, log):
        dict.__init__(self)
        self.log = log
    def __del__(self):
        self.log.append('dispose')


def sample():
    cell = object()
    def target(value=17, *, keyword=23):
        return cell, value, keyword
    return target


def empty_sample():
    def target():
        return None
    return target


def _hook():
    # Only exact source-owned controls mutate this cell. Hook stays installed,
    # permanently inert after close; no foreign function/exception survives.
    state = [False, None, None, None, None]
    def audit(event, args):
        if not state[0]:
            return
        label = None
        if event == 'object.__getattr__' and args[0] is state[1]:
            label = 'get:' + args[1]
        elif event == 'builtins.id':
            label = 'id'
        if label is not None:
            state[2].append(label)
            action = state[3]
            if action is not None:
                action(label)
    sys.addaudithook(audit)
    def arm(target, log, action=None):
        need(not state[0], 'audit already armed')
        state[1:5] = [target, log, action, None]
        state[0] = True
    def disarm():
        state[0] = False
        state[1:5] = [None, None, None, None]
    return arm, disarm


def _observation(events, result='exact-int-match', error=None, active=0, phase=1):
    return {'events': list(events), 'result': result, 'error': error,
            'active': active, 'phase': phase}


def expectations():
    out = {}
    for case_id, events in zip(CASE_IDS[:7], EVENTS):
        out[case_id] = _observation(events)
    for case_id, index in (('none-defaults', 3), ('none-kwdefaults', 4), ('none-closure', 5)):
        out[case_id] = _observation(EVENTS[index])
    out['lazy-dict'] = _observation(('id',))
    for suffix, index in (('code', 0), ('defaults', 3), ('kwdefaults', 4)):
        out['getter-error-' + suffix] = _observation(EVENTS[index][:1], 'raised', ['ControlFault', 'getter-stop'])
    for suffix, events in zip(('code', 'globals', 'builtins', 'defaults', 'kwdefaults', 'closure', 'dict'), EVENTS):
        out['id-error-' + suffix] = _observation(events, 'raised', ['ControlFault', 'id-stop'])
    for suffix, index in (('defaults', 3), ('kwdefaults', 4), ('dict', 6)):
        out['dispose-' + suffix] = _observation(EVENTS[index] + ('dispose', 'compare'))
        out['error-dispose-' + suffix] = _observation(EVENTS[index] + ('dispose',), 'raised', ['ControlFault', 'retained-id-stop'])
    for prefix, pairs in (('close-get-', (('code', 0), ('defaults', 3), ('kwdefaults', 4))),
                          ('close-id-', (('code', 0), ('defaults', 3), ('kwdefaults', 4), ('dict', 6)))):
        for suffix, index in pairs:
            # callback status itself emits no getter/id event
            out[prefix + suffix] = _observation(EVENTS[index] + ('active:1', 'closed:2'), phase=3)
            # close action order occurs immediately after triggering event.
            if prefix == 'close-get-':
                out[prefix + suffix]['events'] = [EVENTS[index][0], 'active:1', 'closed:2', 'id']
    arg_type = ['TypeError', 'field_id requires exact function and integer index']
    for name in ('argument-bool', 'argument-int-subclass', 'argument-function-wrong', 'argument-arity'):
        out[name] = _observation((), 'raised', arg_type)
    for name in ('argument-negative', 'argument-seven'):
        out[name] = _observation((), 'raised', ['IndexError', 'field_id index must be in 0..6'])
    out['argument-large'] = _observation((), 'raised', ['OverflowError', 'Python int too large to convert to C long'])
    out['unbound'] = _observation((), 'raised', ['RuntimeError', 'Field service is not bound and active'], phase=0)
    out['bind-duplicate'] = _observation((), 'raised', ['RuntimeError', 'Field primitive binding is single-use'])
    for name in ('bind-tuple-subclass', 'bind-id-wrapper', 'bind-function-type', 'bind-token-subclass'):
        out[name] = _observation((), 'raised', ['TypeError', 'Field binding requires exact original primitive packet'], phase=4)
    out['bind-getter-wrapper'] = _observation((), 'raised', ['TypeError', 'Field getter must be an original bound method-wrapper'], phase=4)
    out['close-wrong-token'] = _observation((), 'raised', ['RuntimeError', 'Field close lacks the original owner token'])
    out['close-before-events'] = _observation((), 'none', phase=3)
    out['gc-tracked'] = {'tracked': True, 'foreign_referents': 0, 'active': 0,
                         'root_count': 10, 'all_original_roots_visited': True}
    out['gc-foreign-cycle'] = {'finalizers': ['cycle-dispose'], 'active_after_error': 0,
                               'closed_root_count': 1, 'closed_root_is_token': True}
    need(len(out) == 52 and set(out) == set(CASE_IDS), 'native literal case inventory')
    return out


def run_native_field_controls(new_fixture, mode):
    expected = expectations()
    rows = []
    id0 = builtins.id
    getters = tuple(FunctionType.__dict__[name].__get__ for name in FIELDS)
    arm, disarm = _hook()
    created = 0
    def context(bind=True):
        nonlocal created
        created += 1
        need(created <= 24, 'fixture context budget exceeded')
        owner, entries = new_fixture()
        need(type(entries) is tuple and len(entries) == 5, 'native fixture entry shape')
        call, bind0, close, status, abi = entries
        need(all(getattr(e, '__self__', None) is owner for e in entries), 'native fixture owner')
        need(abi() == (1, 7, 0x030C03F0, 8, 2), 'native fixture ABI')
        token = object()
        if bind:
            bind0(getters, id0, FunctionType, token)
        return owner, call, bind0, close, status, token
    base = context()
    owner, call, bind0, close, status, token = base
    def observe(fn, index, *, action=None, entry=call, status0=status,
                expected_id=None, compare=False):
        log = []
        fault = None
        outcome = 'raised'
        try:
            arm(fn, log, None if action is None else lambda label: action(label, log))
            value = entry(fn, index)
            if compare:
                log.append('compare')
            outcome = 'none' if value is None else 'exact-int-match' if type(value) is int and value == expected_id else 'wrong-result'
        except BaseException as exc:
            fault = [type(exc).__name__, str(exc)]
        finally:
            disarm()
        state = status0()
        need(type(state) is tuple and len(state) == 5 and state[0] == 1 and state[3] in (0, 1) and state[4] == 0,
             'native status exact shape')
        return _observation(log, outcome, fault, state[2], state[1])
    def emit(case_id, observation):
        rows.append(record(case_id, observation, expected[case_id]))
    try:
        for index, case_id in enumerate(CASE_IDS[:7]):
            fn = sample()
            original = id0(getters[index](fn, FunctionType))
            # Original expression is the independent oracle; no native oracle.
            oracle_log = []
            arm(fn, oracle_log)
            try:
                oracle_value = id0(getters[index](fn, FunctionType))
            finally:
                disarm()
            need(type(oracle_value) is int and oracle_value == original and tuple(oracle_log) == EVENTS[index], 'literal Python oracle differs')
            emit(case_id, observe(fn, index, expected_id=original))
        for case_id, index in (('none-defaults', 3), ('none-kwdefaults', 4), ('none-closure', 5)):
            fn = empty_sample()
            need(getters[index](fn, FunctionType) is None, 'None fixture construction')
            emit(case_id, observe(fn, index, expected_id=id0(None)))
        fn = empty_sample()
        # No prior __dict__ read: first native read materializes the lazy dict.
        log = []
        arm(fn, log)
        try:
            value = call(fn, 6)
        finally:
            disarm()
        dictionary = getters[6](fn, FunctionType)
        emit('lazy-dict', _observation(log, 'exact-int-match' if type(dictionary) is dict and not dictionary and type(value) is int and value == id0(dictionary) else 'wrong-result'))
        dictionary = None
        for suffix, index in (('code', 0), ('defaults', 3), ('kwdefaults', 4)):
            def fail_get(label, log):
                if label.startswith('get:'):
                    raise ControlFault('getter-stop')
            emit('getter-error-' + suffix, observe(sample(), index, action=fail_get))
        for suffix, index in zip(('code', 'globals', 'builtins', 'defaults', 'kwdefaults', 'closure', 'dict'), range(7)):
            def fail_id(label, log):
                if label == 'id':
                    raise ControlFault('id-stop')
            emit('id-error-' + suffix, observe(sample(), index, action=fail_id))
        for error_mode in (False, True):
            for suffix, index in (('defaults', 3), ('kwdefaults', 4), ('dict', 6)):
                fn = sample()
                disposal_log = []
                value = TupleField(disposal_log) if index == 3 else DictField(disposal_log)
                original = id0(value)
                setattr(fn, FIELDS[index], value)
                value = None
                # The hook detaches the current field while C owns its temporary.
                # The error survives return; no foreign ref may survive in C.
                retained = ControlFault('retained-id-stop')
                def detach(label, log):
                    if label == 'id':
                        # Finalizer logs directly into the actual event list.
                        foreign = getters[index](fn, FunctionType)
                        foreign.log = log
                        foreign = None
                        setattr(fn, FIELDS[index], None if index in (3, 4) else {})
                        if error_mode:
                            raise retained
                # Avoid the action's getter introducing a second audit: give
                # the same log to the object before arming instead.
                event_log = []
                foreign = getters[index](fn, FunctionType)
                foreign.log = event_log
                foreign = None
                fault = None
                outcome = 'raised'
                def detach_literal(label):
                    if label == 'id':
                        setattr(fn, FIELDS[index], None if index in (3, 4) else {})
                        if error_mode:
                            raise retained
                try:
                    arm(fn, event_log, detach_literal)
                    result = call(fn, index)
                    event_log.append('compare')
                    outcome = 'exact-int-match' if type(result) is int and result == original else 'wrong-result'
                except BaseException as exc:
                    need(exc is retained, 'original audit exception identity')
                    fault = [type(exc).__name__, str(exc)]
                    # Traceback references the source hook, not C's temporary.
                    exc.__traceback__ = None
                finally:
                    disarm()
                st = status()
                emit(('error-dispose-' if error_mode else 'dispose-') + suffix,
                     _observation(event_log, outcome, fault, st[2], st[1]))
                retained = detach_literal = detach = fn = foreign = None
        for prefix, pairs in (('close-get-', (('code', 0), ('defaults', 3), ('kwdefaults', 4))),
                              ('close-id-', (('code', 0), ('defaults', 3), ('kwdefaults', 4), ('dict', 6)))):
            fixture = context()
            owner1, call1, bind1, close1, status1, token1 = fixture
            for suffix, index in pairs:
                # One context per destructive close; no rebind/reset.
                if status1()[1] != 1:
                    fixture = context()
                    owner1, call1, bind1, close1, status1, token1 = fixture
                fn = sample()
                original = id0(getters[index](fn, FunctionType))
                def close_action(label, log):
                    if (prefix == 'close-get-' and label.startswith('get:')) or (prefix == 'close-id-' and label == 'id'):
                        log.append('active:' + str(status1()[2]))
                        close1(token1)
                        log.append('closed:' + str(status1()[1]))
                emit(prefix + suffix, observe(fn, index, action=close_action, entry=call1, status0=status1, expected_id=original))
        class IntSubclass(int):
            pass
        fn = sample()
        for name, index in (('argument-bool', True), ('argument-negative', -1), ('argument-seven', 7), ('argument-large', 1 << 100), ('argument-int-subclass', IntSubclass(0))):
            emit(name, observe(fn, index))
        emit('argument-function-wrong', observe(object(), 0))
        def wrong_arity(fn, index):
            return call(fn)
        emit('argument-arity', observe(fn, 0, entry=wrong_arity))
        unbound = context(False)
        emit('unbound', observe(fn, 0, entry=unbound[1], status0=unbound[4]))
        def operation_observation(operation, status0):
            error = None
            try:
                operation()
            except BaseException as exc:
                error = [type(exc).__name__, str(exc)]
            st = status0()
            return _observation((), 'raised' if error else 'unexpected-success', error, st[2], st[1])
        emit('bind-duplicate', operation_observation(lambda: bind0(getters, id0, FunctionType, token), status))
        class TupleSubclass(tuple):
            pass
        class TokenSubclass:
            pass
        for name in ('bind-tuple-subclass', 'bind-id-wrapper', 'bind-getter-wrapper', 'bind-function-type', 'bind-token-subclass'):
            fixture = context(False)
            packet = [getters, id0, FunctionType, object()]
            if name == 'bind-tuple-subclass': packet[0] = TupleSubclass(getters)
            elif name == 'bind-id-wrapper': packet[1] = lambda value: id0(value)
            elif name == 'bind-getter-wrapper': packet[0] = (lambda *args: None,) + getters[1:]
            elif name == 'bind-function-type': packet[2] = type
            else: packet[3] = TokenSubclass()
            emit(name, operation_observation(lambda: fixture[2](*packet), fixture[4]))
            # A failed first bind is terminal, even with the correct packet.
            retry = operation_observation(lambda: fixture[2](getters, id0, FunctionType, object()), fixture[4])
            need(retry['error'] == ['RuntimeError', 'Field primitive binding is single-use'] and retry['phase'] == 4, 'partial bind terminality')
            packet = None
        emit('close-wrong-token', operation_observation(lambda: close(object()), status))
        closed = context()
        closed[3](closed[5])
        closed[3](closed[5])
        emit('close-before-events', observe(fn, 0, entry=closed[1], status0=closed[4]))
        referents = gc.get_referents(owner)
        emit('gc-tracked', {'tracked': gc.is_tracked(owner), 'foreign_referents': sum(isinstance(r, (TupleField, DictField)) for r in referents), 'active': status()[2],
            'root_count': len(referents), 'all_original_roots_visited': all(any(r is expected_root for r in referents) for expected_root in getters + (id0, FunctionType, token))})
        referents = None
        cycle_log = []
        class Cyclic(dict):
            def __del__(self):
                cycle_log.append('cycle-dispose')
        fn = sample()
        cycle = Cyclic()
        cycle['self'] = cycle
        cycle['native_entry_and_context'] = (call, owner)
        fn.__dict__ = cycle
        cycle = None
        def cycle_fail(label, log):
            if label == 'id':
                fn.__dict__ = {}
                raise ControlFault('cycle-stop')
        observed = observe(fn, 6, action=cycle_fail)
        need(observed['error'] == ['ControlFault', 'cycle-stop'], 'cycle error identity')
        gc.collect()
        active_after_error = status()[2]
        close(token)
        cleared = gc.get_referents(owner)
        emit('gc-foreign-cycle', {'finalizers': cycle_log, 'active_after_error': active_after_error,
            'closed_root_count': len(cleared), 'closed_root_is_token': len(cleared) == 1 and cleared[0] is token})
        cleared = None
    finally:
        disarm()
        close(token)
        base = owner = call = bind0 = close = status = token = fn = None
    count = NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT
    return finish(rows, CASE_IDS, count, expected, mode)
