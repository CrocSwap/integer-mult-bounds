"""Prospective F4 candidate DATA; no IO, owner restoration, or execution grant.

Adapts the immutable-generation construction in F4 financial_commit_candidate
(CrocSwap/integer-mult-bounds, retained H25 source a0c2ab55...).  This module
implements own MANUAL_ONLY import separately from distinct-target formal close.
The fixed loader must authenticate this source and the actual selected F4 module.
"""
import hashlib
import json
from pathlib import Path
from types import FunctionType, ModuleType


class CandidateError(ValueError):
    pass


def need(condition, message):
    if condition is not True:
        raise CandidateError(message)


def wire_pin(path, wire, mode=0o444):
    need(type(path) in (str, type(Path('/'))) and type(wire) is str and
         type(mode) is int and mode in (0o444, 0o600), 'exact path, wire and mode')
    raw = wire.encode('utf-8')
    return dict(path=str(path), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), mode=mode)


def bind_funding(funding):
    """Bind actual source-owned functions; hashes alone confer no authority.

    The returned builder only creates DATA.  Actual A4/native IO verifies every
    existing original, exact current HEAD and complete census before publishing.
    """
    need(type(funding) is ModuleType, 'actual selected F4 module')
    fg = funding.__dict__
    names = ('financial_plain', 'financial_decode', 'financial_evidence',
             'validate_original_record', '_manifest_successor', '_entry_financial_view',
             '_opening_evidence_f3', 'canonical_financial', 'require_opening_append', 'fp', 'flabel')
    functions = {n: fg.get(n) for n in names}
    need(all(type(f) is FunctionType and f.__globals__ is fg for f in functions.values()),
         'actual selected source-owned F4 functions')
    image = dict(fg)
    owned = {n: (f, f.__code__) for n, f in image.items()
             if type(f) is FunctionType and f.__globals__ is fg}
    records_image = json.dumps(fg['FRAME_RECORDS'], sort_keys=True)
    constants = {n: fg[n] for n in ('FIN_ROOT', 'FIN_ENTRIES', 'FIN_HEAD', 'ADMIN_NS',
                                   'META_CAP', 'FIN_MAX_FILES', 'FIN_MAX_BYTES')}

    def fresh():
        need(set(fg) == set(image) and all(fg[n] is value for n, value in image.items()),
             'unchanged selected F4 namespace')
        need(all(fg[n] is f and f.__code__ is code and f.__globals__ is fg
                 for n, (f, code) in owned.items()), 'unchanged source-owned function code')
        need(json.dumps(fg['FRAME_RECORDS'], sort_keys=True) == records_image, 'unchanged F4 schemas')
        need(all(fg.get(n) is f and f.__globals__ is fg for n, f in functions.items()),
             'unchanged selected F4 functions')
        need(all(fg.get(n) is v for n, v in constants.items()), 'unchanged selected F4 constants')

    def call(name, *args):
        fresh()
        return functions[name](*args)

    def copied(value):
        call('financial_plain', value)
        return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))

    def encode(value):
        return call('canonical_financial', value).decode('utf-8')

    def take(wires):
        def get(pin):
            call('fp', pin, True)
            need(pin['path'] in wires and wire_pin(pin['path'], wires[pin['path']], pin['mode']) == pin,
                 'complete exact original wire')
            return call('financial_decode', wires[pin['path']].encode('utf-8'))
        get.__dict__.update(wires=wires, used=set())
        return get

    def merge(snapshot, additions, allow_body=None):
        result = copied(snapshot)
        call('financial_plain', additions)
        need(type(additions) is dict, 'exact additional wire map')
        for path, wire in additions.items():
            need(type(path) is str and type(wire) is str and Path(path).is_absolute() and
                 '..' not in Path(path).parts and len(wire.encode()) <= constants['META_CAP'], 'bounded original wire')
            previous = result['wires'].get(path)
            need(previous is None or previous == wire or
                 (path == allow_body and previous == '' and wire != ''), 'immutable predecessor wire')
            result['wires'][path] = wire
        need(len(result['wires']) <= constants['FIN_MAX_FILES'] and
             sum(len(w.encode()) for w in result['wires'].values()) <= constants['FIN_MAX_BYTES'],
             'complete bounded wire set')
        return result

    def finish(previous, work, ordered):
        prior = call('financial_evidence', previous)
        get = take(work['wires'])
        legacy = call('_opening_evidence_f3', work['legacy_snapshot'])
        views = [call('_entry_financial_view', p, get(p), get, legacy) for p in ordered]
        need(len({v['entry_id'] for v in views}) == len(views), 'one latest manifest per entry')
        state = get(prior['state_pin'])
        generation = state['generation'] + 1
        need(generation <= 256, 'generation cap')
        body = legacy['parent_body_ns'] + sum(v['body_ns'] for v in views if v['body_ns'] is not None)
        admin = legacy['parent_admin_ns'] + constants['ADMIN_NS'] * len(views)
        state.update(generation=generation, previous_state_sha256=prior['state_pin']['sha256'],
                     ordered_entries=ordered, known_body_ns=body, admin_policy_ns=admin,
                     known_policy_ns=body + admin,
                     unsettled_entries=[v['entry_id'] for v in views if v['phase'] != 'CLOSED_KNOWN'])
        root = constants['FIN_ROOT']
        spath = root / ('STATE-%06d.json' % generation)
        opath = root / ('OPENING-%06d.json' % generation)
        hpath = root / ('HEAD-%06d.json' % generation)
        for path in (spath, opath, hpath):
            need(str(path) not in work['wires'], 'exclusive next generation')
        swire = encode(state); sp = wire_pin(spath, swire)
        opening = dict(prior['descriptor'], suffix_state_pin=sp,
                       previous_opening_sha256=prior['opening_pin']['sha256'],
                       expected_totals=dict(body_ns=body, admin_policy_ns=admin,
                                            known_policy_ns=body + admin, operations=3 + len(views)))
        owire = encode(opening); op = wire_pin(opath, owire)
        head = dict(schema='fresh-financial-head-v1', generation=generation,
                    state_pin=sp, opening_pin=op, previous_head_sha256=prior['head_pin']['sha256'])
        hwire = encode(head)
        work['wires'].update({str(spath): swire, str(opath): owire, str(hpath): hwire,
                              str(constants['FIN_HEAD']): hwire})
        work.update(opening_pin=op, opening_wire=owire, head_wire=hwire,
                    head_pin=wire_pin(constants['FIN_HEAD'], hwire, 0o600))
        # Recompute the COMPLETE census from all retained wires; never filter old debt.
        entries = constants['FIN_ENTRIES']
        work['census'] = {str(root): sorted(['entries'] + [Path(p).name for p in work['wires'] if Path(p).parent == root]),
                          str(entries): sorted(v['entry_id'] for v in views)}
        for view in views:
            folder = entries / view['entry_id']
            work['census'][str(folder)] = sorted(Path(p).name for p in work['wires'] if Path(p).parent == folder)
        call('financial_evidence', work)
        call('require_opening_append', previous, work)
        return work

    class Builder:
        __slots__ = ()

        def build_started(self, predecessor, reserved_manifest_pin, start_pin, extra_wires, pending_path):
            prior = call('financial_evidence', predecessor)
            work = merge(predecessor, extra_wires)
            get = take(work['wires'])
            reserved = call('validate_original_record', 'ENTRY_MANIFEST', get(reserved_manifest_pin))
            name = reserved['attempt_id']; call('flabel', name)
            folder = constants['FIN_ENTRIES'] / name
            need(name not in prior['entries'] and reserved_manifest_pin['path'] == str(folder / 'ENTRY-000000.json') and
                 reserved['phase'] == 'RESERVED' and reserved['settlement_route'] == 'MANUAL_ONLY', 'one fresh manual RESERVED entry')
            need(all(reserved[k] is None for k in ('meter_start_pin', 'meter_body_pin', 'native_chain_pin',
                 'financial_adjudication_pin', 'formal_start_pin', 'formal_receipt_pin')), 'no pre-start evidence adoption')
            start = call('validate_original_record', 'METER_START', get(start_pin))
            need(start_pin['path'] == str(folder / 'METER_START.json') and start['attempt_id'] == name and
                 start['command_pin'] == reserved['command_pin'] and start['reservation_pin'] == reserved['reservation_pin'], 'genuine own START correlation')
            reservation = call('validate_original_record', 'RESERVATION', get(reserved['reservation_pin']))
            need(reservation['before_closed_state_pin'] == prior['state_pin'] and
                 reservation['policy_reserved_before_ns'] == prior['encumbered_policy_ns'], 'reservation names exact predecessor state and all debt')
            command = call('validate_original_record', 'COMMAND', get(reserved['command_pin']))
            need(command['operation_class'] in ('METADATA_INITIALIZER', 'METADATA_CLOSER') and
                 command['settlement_route'] == 'MANUAL_ONLY', 'manual operation only')
            started = dict(reserved, meter_start_pin=start_pin, phase='STARTED')
            call('_manifest_successor', reserved, started)
            mpath = folder / 'ENTRY-000001.json'; mwire = encode(started); mp = wire_pin(mpath, mwire)
            need(str(mpath) not in work['wires'], 'exclusive STARTED manifest')
            need(type(pending_path) is str and Path(pending_path).parent == folder and
                 Path(pending_path).suffix == '.json' and pending_path not in work['wires'], 'fresh own pending path')
            pending = dict(schema='fresh-current-manual-pending-v1',
                           closed_state_sha256=reservation['before_closed_state_pin']['sha256'],
                           operations=[dict(entry_id=name, command_sha256=reserved['command_pin']['sha256'],
                               body_reservation_ns=reservation['body_reservation_ns'],
                               registration_pin=reserved['reservation_pin'], original_start_pin=start_pin)])
            pwire = encode(pending); pp = wire_pin(pending_path, pwire)
            work['wires'].update({str(mpath): mwire, pending_path: pwire})
            need(work['wires'].get(str(folder / 'METER_BODY.json')) == '', 'genuine empty BODY slot remains unfilled')
            old_state = get(prior['state_pin'])
            candidate = finish(predecessor, work, old_state['ordered_entries'] + [mp])
            return dict(candidate=candidate, started_manifest_pin=mp, pending_pin=pp)

        def build_settlement(self, current, own_id, terminal_manifest_pin, extra_wires):
            call('flabel', own_id)
            prior = call('financial_evidence', current)
            need(own_id in prior['entries'], 'own entry is already reserved in current state')
            old = prior['entries'][own_id]
            need(old['settlement_route'] == 'MANUAL_ONLY' and old['phase'] != 'CLOSED_KNOWN', 'once-only own manual import')
            folder = constants['FIN_ENTRIES'] / own_id
            work = merge(current, extra_wires, str(folder / 'METER_BODY.json'))
            get = take(work['wires'])
            terminal = call('validate_original_record', 'ENTRY_MANIFEST', get(terminal_manifest_pin))
            need(terminal['attempt_id'] == own_id and terminal['settlement_route'] == 'MANUAL_ONLY' and
                 terminal['phase'] == 'CLOSED_KNOWN' and Path(terminal_manifest_pin['path']).parent == folder,
                 'independently adjudicated own manual terminal manifest')
            old_manifest = take(current['wires'])(old['manifest_pin'])
            call('_manifest_successor', old_manifest, terminal)
            view = call('_entry_financial_view', terminal_manifest_pin, terminal, get,
                        call('_opening_evidence_f3', current['legacy_snapshot']))
            need(view['terminal_known'] is True and view['known_charge_ns'] is not None and
                 not view['_unknown'], 'genuine terminal, full cleanup and independent known adjudication')
            old_state = get(prior['state_pin'])
            ordered = [terminal_manifest_pin if p == old['manifest_pin'] else p for p in old_state['ordered_entries']]
            result = finish(current, work, ordered)
            after = call('financial_evidence', result)
            need(after['entries'][own_id]['known_charge_ns'] == view['body_ns'] + constants['ADMIN_NS'] and
                 own_id not in after['pending'], 'accepted own charge once without rounding')
            return result

    return Builder()
