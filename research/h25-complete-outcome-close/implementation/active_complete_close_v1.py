"""SOURCE ONLY: private ACTIVE ownership and durable registry publication.

Trusted caller must authenticate the exact loaded controller/funding modules
before bind_api. Module names, hash strings, dictionaries and instance fields
are NOT that authentication. This code performs real GlobalLease acquisition
and verification; never restore an owner from DATA or pass it to a child.
Ordinary OS/CPython/fsync/rename/link and registered-writer exclusion are selected
operating premises, not universal hostile-admin or crash-storage theorems.
"""
import hashlib
import json
import os
import stat
import time
from pathlib import Path
from types import ModuleType, FunctionType, GetSetDescriptorType

# Kernel-body predecessor provenance ONLY; actual selected C/profile authenticated externally.
CONTROLLER_SHA = 'be36f1427694c786efc1cf04958a6fb002776f586641828ce569f36e2f289895'
FUNDING_SHA = '164468176d2094fbd496eecfd0d0adf3b6ceaf89b2573456509157cc26256677'
W = Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
R = W / 'outputs/h25-data-handling-20261028'
CONTROL = R / 'control/fresh-metered-round-v1'
DOMAIN = R / 'runtime/fresh-metered-round-v1/attempts'
STAGE = CONTROL / '_active-staging'
HEADS = CONTROL / '_registry-heads'
HANDOFFS = CONTROL / '_handoff-intents'
CLAIMS = CONTROL / '_handoff-claims'
HEAD = CONTROL / 'ACTIVE-HEAD.json'
LOCK = W / 'outputs/h25-bookkeeping-swarm-20261028/runtime/science.lock'


class ActiveError(RuntimeError):
    pass


def need(ok, text):
    if ok is not True:
        raise ActiveError(text)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')




# Finite ordinary-Python kernel substitution boundary. These checks perform no
# filesystem/process/clock operation and never establish loaded-image identity.
def module_namespace(module):
    need(type(module) is ModuleType, 'exact selected module type')
    namespace = ModuleType.__getattribute__(module, '__dict__')
    need(type(namespace) is dict, 'native module namespace')
    keys = tuple(dict.__iter__(namespace))
    need(all(type(k) is str for k in keys), 'module keys before hashing/lookup')
    need('__getattr__' not in keys, 'no selected module attribute fallback')
    return namespace


def function_image(fn, namespace):
    need(type(fn) is FunctionType and fn.__globals__ is namespace, 'actual source-owned function')
    return (fn, fn.__code__, fn.__defaults__, fn.__kwdefaults__, fn.__closure__)


def unchanged_function(image, namespace):
    fn, code, defaults, kwdefaults, closure = image
    need(type(fn) is FunctionType and fn.__globals__ is namespace and
         fn.__code__ is code and fn.__defaults__ is defaults and
         fn.__kwdefaults__ is kwdefaults and fn.__closure__ is closure,
         'captured original function metadata')


def class_image(cls, methods, namespace, *, slotted=False):
    need(type(cls) is type, 'ordinary exact class before native type inspection')
    mro = type.__getattribute__(cls, '__mro__')
    need(type(mro) is tuple and len(mro) == 2 and mro[0] is cls and mro[1] is object, 'direct object class')
    native = type.__getattribute__(cls, '__dict__')
    keys = tuple(native)
    need(all(type(k) is str for k in keys), 'class keys before hashing/lookup')
    image = {k: native[k] for k in keys}
    allowed = {'__module__', '__doc__'} | set(methods)
    if slotted:
        allowed |= {'__slots__', '__new__'}
        need(type(image.get('__slots__')) is tuple and len(image['__slots__']) == 0 and
             type(image.get('__new__')) is staticmethod, 'private empty-slotted class')
        function_image(staticmethod.__getattribute__(image['__new__'], '__func__'), namespace)
    else:
        allowed |= {'__dict__', '__weakref__'}
        for name in ('__dict__', '__weakref__'):
            descriptor = image.get(name)
            need(type(descriptor) is GetSetDescriptorType and descriptor.__objclass__ is cls and
                 type(descriptor.__name__) is str and descriptor.__name__ == name, 'native actual-class dictionary descriptor')
    need(set(image) == allowed and type(image['__module__']) is str and
         (image['__doc__'] is None or type(image['__doc__']) is str), 'fixed class layout; no special hooks')
    function_images = {name: function_image(image[name], namespace) for name in methods}
    if slotted:
        function_images['__new__'] = function_image(staticmethod.__getattribute__(image['__new__'], '__func__'), namespace)
    return image, function_images


def unchanged_class(cls, image, function_images, namespace):
    need(type(cls) is type, 'unchanged ordinary metaclass')
    native = type.__getattribute__(cls, '__dict__'); keys = tuple(native)
    need(all(type(k) is str for k in keys) and set(keys) == set(image) and
         all(native[k] is image[k] for k in keys), 'no class namespace/descriptor substitution')
    mro = type.__getattribute__(cls, '__mro__')
    need(type(mro) is tuple and len(mro) == 2 and mro[0] is cls and mro[1] is object, 'unchanged direct class ancestry')
    for value in function_images.values():
        unchanged_function(value, namespace)


def instance_state(value, cls, image, function_images, namespace, fields):
    need(type(value) is cls, 'exact actual instance before descriptor access')
    unchanged_class(cls, image, function_images, namespace)
    # Direct native getset dispatch bypasses value.__getattribute__ entirely.
    values = GetSetDescriptorType.__get__(image['__dict__'], value, cls)
    need(type(values) is dict, 'exact native instance dictionary')
    keys = tuple(dict.__iter__(values))
    need(all(type(k) is str for k in keys) and set(keys) == set(fields), 'no instance method/descriptor/special-hook shadow')
    return values


def bounded_kernel_data(value, nodes=None, depth=0):
    if nodes is None:
        nodes = [0]
    nodes[0] += 1
    need(nodes[0] <= 256 and depth <= 8, 'bounded kernel metadata state')
    t = type(value)
    if t is dict:
        keys = tuple(dict.__iter__(value))
        need(len(keys) <= 64 and all(type(k) is str for k in keys), 'kernel dictionary keys before lookup')
        for key in keys:
            bounded_kernel_data(value[key], nodes, depth + 1)
    elif t is list or t is tuple:
        need(len(value) <= 64, 'kernel metadata sequence bound')
        for item in value:
            bounded_kernel_data(item, nodes, depth + 1)
    elif t is str:
        need(len(value) <= 16384, 'kernel metadata string bound')
    else:
        need(value is None or t is int or t is bool, 'exact scalar kernel metadata')


def exception_instance(value):
    cls = type(value)
    if type(cls) is not type:
        return False
    mro = type.__getattribute__(cls, '__mro__')
    return type(mro) is tuple and any(base is BaseException for base in mro)

def complete_close_data(F, closure, receipt_raw, review_raw, documents, own_request,
                        own_provenance, original_own_start, current, raw_head, raw_reg):
    """Consistency of externally accepted evidence; never native authentication.

    The authenticated source-private parent has already accepted the full raw
    inventory, fixed the result contract at original admission, and authenticated
    the clock lineage. This bounded DATA check neither reconstructs those facts
    nor verifies large raw files. Every selected metadata body is actually read.
    """
    def exact(value, fields):
        F.plain(value); F.exact(value, fields)
    def digest(raw):
        return hashlib.sha256(raw).hexdigest()
    def document(name, fields, schema):
        value = F.decode(documents[name]); exact(value, fields)
        need(value['schema'] == schema, 'complete-close document schema')
        return value
    binding = closure['evidence_binding']
    exact(binding, ('schema', 'admission_pin', 'source_manifest_pin', 'profile_pin',
                    'result_contract_pin', 'evidence_manifest_pin', 'clock_pin',
                    'expected_head_pin', 'closer_start_clock_path'))
    need(binding['schema'] == 'complete-close-evidence-binding-v1', 'complete binding version')
    for key in ('admission_pin', 'source_manifest_pin', 'profile_pin', 'result_contract_pin',
                'evidence_manifest_pin', 'clock_pin', 'expected_head_pin'):
        F.pin(binding[key])
    request = closure['request']; start = closure['start']
    need(request['schema'] == 'fresh-round-request-v1' and start['schema'] == 'fresh-round-start-v1',
         'original request and START schemas')
    for key in ('round_id', 'label', 'command_sha256', 'body_reservation_ns', 'policy_sha256'):
        need(type(request[key]) is type(start[key]) and request[key] == start[key],
             'request agrees with actual registered START')
    need(request['round_id'] == F.ROUND_ID, 'same original round')
    F.validate_pre_entry_provenance(start['pre_entry_provenance'], request['label'],
                                   request['command_sha256'], request['body_reservation_ns'])
    need(own_request['label'] != request['label'] and
         own_request['command_sha256'] != request['command_sha256'], 'distinct own/target operations')
    need(binding['expected_head_pin']['sha256'] == digest(raw_head), 'accepted current head')
    admission = document('admission_pin', ('schema', 'request', 'start_pin', 'baseline_registry_pin',
        'source_manifest_pin', 'profile_pin', 'result_contract_pin', 'registration_pin'),
        'complete-close-original-admission-v1')
    for key in ('request', 'start_pin', 'baseline_registry_pin'):
        need(admission[key] == closure[key], 'original admission target binding')
    for key in ('source_manifest_pin', 'profile_pin', 'result_contract_pin'):
        need(admission[key] == binding[key], 'original admitted source/profile/oracle')
    need(admission['registration_pin'] == start['pre_entry_provenance']['registration_pin'],
         'same original registration; pre-outcome selection is external accepted premise')
    contract = document('result_contract_pin', ('schema', 'kind', 'command_sha256',
        'source_manifest_pin', 'profile_pin'), 'complete-close-result-contract-v1')
    need(contract['kind'] in ('FULL_POSITIVE', 'EXPECTED_REFUSAL', 'KNOWN_STOP') and
         contract['command_sha256'] == request['command_sha256'] and
         contract['source_manifest_pin'] == binding['source_manifest_pin'] and
         contract['profile_pin'] == binding['profile_pin'], 'original result contract binding')
    evidence = document('evidence_manifest_pin', ('schema', 'round_id', 'label', 'command_sha256',
        'start_sha256', 'admission_sha256', 'source_manifest_sha256', 'profile_sha256',
        'result_contract_sha256', 'interval_scope', 'rss_scope', 'body_begin_ns', 'body_end_ns',
        'body_elapsed_ns', 'peak_sampled_rss_bytes', 'body_fully_observed', 'cleanup_known',
        'custody_complete', 'nested_entries_complete', 'outcome', 'result_kind', 'uncertainty',
        'tail_state', 'raw_inputs'), 'complete-close-accepted-evidence-v1')
    need(evidence['round_id'] == F.ROUND_ID and evidence['label'] == request['label'] and
         evidence['command_sha256'] == request['command_sha256'] and
         evidence['start_sha256'] == closure['start_pin']['sha256'], 'whole evidence target')
    for name in ('admission', 'source_manifest', 'profile', 'result_contract'):
        need(evidence[name + '_sha256'] == binding[name + '_pin']['sha256'], 'exact accepted evidence inputs')
    need(evidence['interval_scope'] == 'COMPLETE_OUTER_COMMAND' and
         evidence['rss_scope'] == 'AGGREGATE_SAMPLED_ROOT' and
         evidence['result_kind'] == contract['kind'], 'whole invocation and original outcome oracle')
    receipt = F.decode(receipt_raw)
    exact(receipt, ('schema', 'round_id', 'label', 'start_sha256', 'outcome', 'body_elapsed_ns',
        'administrative_debit_ns', 'body_begin_ns', 'body_end_ns', 'body_fully_observed',
        'cleanup_known', 'custody_complete', 'nested_entries_complete', 'uncertainty',
        'peak_sampled_rss_bytes', 'tail_state', 'independent_outcome_review_sha256'))
    need(receipt['schema'] == 'fresh-round-receipt-v1' and receipt['round_id'] == F.ROUND_ID and
         receipt['label'] == request['label'] and receipt['start_sha256'] == closure['start_pin']['sha256'],
         'unchanged formal receipt identity')
    for key in ('outcome', 'body_elapsed_ns', 'body_begin_ns', 'body_end_ns', 'body_fully_observed',
                'cleanup_known', 'custody_complete', 'nested_entries_complete', 'uncertainty',
                'peak_sampled_rss_bytes', 'tail_state'):
        need(type(receipt[key]) is type(evidence[key]) and receipt[key] == evidence[key], 'receipt/evidence correlation')
    for key in ('body_fully_observed', 'cleanup_known', 'custody_complete', 'nested_entries_complete'):
        need(receipt[key] is True, 'complete accepted terminal/custody facts')
    begin = F.uint(receipt['body_begin_ns']); end = F.uint(receipt['body_end_ns'])
    elapsed = F.uint(receipt['body_elapsed_ns']); F.uint(receipt['peak_sampled_rss_bytes'])
    need(end >= begin and end - begin == elapsed, 'exact whole outer interval')
    need(receipt['uncertainty'] == [] and receipt['tail_state'] in ('COMPLETE', 'ADMIN_ONLY_OPEN'),
         'no unknown nonadministrative tails')
    need(receipt['outcome'] in ('PASS', 'STOP') and
         (contract['kind'] != 'KNOWN_STOP' or receipt['outcome'] == 'STOP'), 'truthful original outcome')
    need(type(evidence['raw_inputs']) is list and 1 <= len(evidence['raw_inputs']) <= F.MAX_ENTRIES,
         'complete bounded raw inventory accepted externally')
    seen = set()
    for item in evidence['raw_inputs']:
        exact(item, ('path', 'bytes', 'sha256', 'mode'))
        need(type(item['path']) is str and Path(item['path']).is_absolute() and
             item['path'] not in seen, 'distinct original raw evidence')
        seen.add(item['path']); F.uint(item['bytes']); F.digest(item['sha256'])
        need(type(item['mode']) is int and item['mode'] in (0o444, 0o600), 'raw evidence custody mode')
    clock = document('clock_pin', ('schema', 'clock_domain_sha256', 'target_start_sha256',
        'closer_start_sha256', 'target_end_ns', 'closer_begin_ns'), 'complete-close-clock-lineage-v1')
    F.digest(clock['clock_domain_sha256']); F.uint(clock['closer_begin_ns'])
    path = binding['closer_start_clock_path']
    need(type(path) is list and 1 <= len(path) <= 8 and all(type(x) is str for x in path), 'own original clock selector')
    own_begin = F.select(original_own_start, path); F.uint(own_begin)
    need(clock['target_start_sha256'] == closure['start_pin']['sha256'] and
         clock['closer_start_sha256'] == own_provenance['original_start_pin']['sha256'] and
         type(clock['target_end_ns']) is int and clock['target_end_ns'] == end and
         clock['closer_begin_ns'] == own_begin and end <= own_begin, 'original terminal before own closer')
    review = F.decode(review_raw)
    exact(review, ('schema', 'decision', 'receipt_projection_sha256', 'evidence_binding_sha256'))
    projection = dict(receipt); del projection['independent_outcome_review_sha256']
    need(review['schema'] == 'complete-close-independent-review-v1' and
         review['decision'] == 'ACCEPT_COMPLETE_OUTCOME' and
         review['receipt_projection_sha256'] == digest(canonical(projection)) and
         review['evidence_binding_sha256'] == digest(canonical(binding)) and
         receipt['independent_outcome_review_sha256'] == digest(review_raw), 'acyclic exact accepted review binding')
    policy = documents['policy']
    need(receipt['administrative_debit_ns'] == F.uint(policy['administrative_debit_ns']) and
         type(receipt['administrative_debit_ns']) is int, 'exact target policy fee')
    # Actual overrun numbers remain untouched. Funding decides future eligibility.
    # No fit boolean is issued here. Even an original PASS over reservation/RSS
    # remains recordable verbatim; original assess_round retains its blockers.
    need(type(current['sequence']) is int and current['sequence'] < 2 * F.MAX_ENTRIES, 'prospective generation cap')
    rp = {'path': str(DOMAIN / request['label'] / 'receipt.json'), 'bytes': len(receipt_raw),
          'sha256': digest(receipt_raw), 'mode': 0o600}; F.pin(rp)
    new = F.decode(raw_reg); new['predecessor_sha256'] = digest(raw_reg)
    new['events'].append({'kind': 'CLOSE', 'label': request['label'], 'pin': rp})
    new_raw = canonical(new); F.registry(new_raw); F.require_append_only(raw_reg, new_raw)
    sequence = current['sequence'] + 1
    reg_pin = {'path': str(CONTROL / ('REGISTRY-%06d.json' % sequence)), 'bytes': len(new_raw),
               'sha256': digest(new_raw), 'mode': 0o444}; F.pin(reg_pin)
    next_head = {'schema': 'fresh-active-head-v1', 'sequence': sequence,
                 'registry_pin': reg_pin, 'previous_head_sha256': digest(raw_head)}
    next_raw = canonical(next_head)
    need(0 < len(receipt_raw) <= F.META_CAP and 0 < len(new_raw) <= F.META_CAP and
         0 < len(next_raw) <= F.META_CAP, 'all prospective images bounded before publication')
    return receipt, rp, new, new_raw, next_raw


def bind_api(controller, funding, *, role, expected_head_pin=None,
             approved_handoff_pin=None, approved_closure=None, approved_opening=None, approved_manual_entry=None, guardian=None, approved_complete_closure=None):
    """Called ONLY by the separately authenticated source-private parent role.

    Exact module/source/loaded-instance authentication is an external bootstrap
    premise. Merely constructing ModuleType/FunctionType is not authentication.
    approved_* are pinned permission/evidence DATA chosen by that trusted role;
    they never create ownership. Every returned context first acquires its own
    actual EX. No factory/caller/native command is authorized by this file.
    """
    need(type(controller) is ModuleType and type(funding) is ModuleType, 'actual selected module objects')
    need(type(role) is str and role in ('PUBLISHER', 'CONTROLLER', 'CLOSER'), 'fixed caller role')
    C, F = controller, funding
    cg, fg = module_namespace(C), module_namespace(F)
    IOType, LeaseType, io = cg['OwnedIO'], cg['GlobalLease'], cg['IO']
    io_image, io_functions = class_image(IOType, ('__init__', 'acquire', 'close', 'read', 'names', 'write'), cg)
    lease_image, lease_functions = class_image(LeaseType, ('__init__', 'acquire', 'verify', 'close'), cg)
    instance_state(io, IOType, io_image, io_functions, cg, {'slots'})
    lock_reference, domain_reference, control_reference = cg['HISTORICAL_LOCK'], fg['DOMAIN'], fg['CONTROL']
    need(type(lock_reference) is type(LOCK) and lock_reference == LOCK and
         type(domain_reference) is type(DOMAIN) and domain_reference == DOMAIN and
         type(control_reference) is type(CONTROL) and control_reference == CONTROL,
         'actual original canonical lock/domain values')
    first_state, secondary_state, unknown_state = cg['FIRST'], cg['SECONDARY'], cg['IO_UNKNOWN']
    need(type(first_state) is list and len(first_state) == 1 and type(secondary_state) is list and
         len(secondary_state) == 256 and type(unknown_state) is list and len(unknown_state) == 1 and
         type(unknown_state[0]) is bool, 'actual original error/uncertainty containers')
    remember_image = function_image(cg['remember'], cg)
    remember_original = remember_image[0]
    continuation_image = function_image(cg['joined_continuation_check'], cg)
    funding_names = ('snapshot_round', 'assess_round', 'registry', 'require_append_only',
                     'read_opening', 'opening_evidence', 'validate_opening_binding', 'require_opening_append',
                     'validate_opening_partition', 'validate_pre_entry_provenance', 'metadata_decode', 'select',
                     'read_pinned', 'plain', 'decode', 'pin', 'uint', 'exact', 'digest')
    funding_images = {name: function_image(fg[name], fg) for name in funding_names}
    active_globals = globals()  # Actual source-private A module; bootstrap authentication remains external.
    # Fixed authenticated loader supplies actual source-private G, never DATA.
    guardian_module, guardian_channel, guardian_namespace, guardian_image = None, None, None, None
    if guardian is not None:
        need(type(guardian) is tuple and len(guardian) == 2, 'actual fixed G association pair')
        guardian_module, guardian_channel = guardian
        guardian_namespace = module_namespace(guardian_module)
        guardian_image = function_image(guardian_namespace['verify_association'], guardian_namespace)
    guardian_globals = dict(guardian_namespace) if guardian_namespace is not None else None
    guardian_class = guardian_namespace['GuardianChannel'] if guardian_namespace is not None else None
    guardian_class_image = dict(type.__getattribute__(guardian_class, '__dict__')) if guardian_class is not None else None
    guardian_function_images = [function_image(fn, guardian_namespace) for fn in guardian_class_image.values()
                                if type(fn) is FunctionType] if guardian_class_image is not None else []
    if guardian_class_image is not None:
        for member in guardian_class_image.values():
            if type(member) is property:
                guardian_function_images.extend(function_image(fn, guardian_namespace)
                    for fn in (member.fget,member.fset,member.fdel) if fn is not None)
    need(guardian_image is not None or role == 'CLOSER', 'production owner requires actual G channel')

    def guard(record, phase):
        if role == 'CLOSER':
            return None  # Separately funded metadata-only STOP/UNKNOWN; no G clearing.
        need(guardian_image is not None, 'no source-private G association')
        unchanged_function(guardian_image, guardian_namespace)
        need(set(guardian_namespace) == set(guardian_globals) and
             all(guardian_namespace[k] is guardian_globals[k] for k in guardian_globals),
             'actual G source globals unchanged')
        native_class = type.__getattribute__(guardian_class, '__dict__')
        need(set(native_class) == set(guardian_class_image) and
             all(native_class[k] is guardian_class_image[k] for k in guardian_class_image),
             'actual G class/method/descriptor identities unchanged')
        for image in guardian_function_images:
            unchanged_function(image, guardian_namespace)
        selected_request = record.get('request') or (manual['request'] if manual is not None else None)
        selected_start = (record.get('manual_provenance') or
                          (manual['provenance'] if manual is not None else None))
        need(selected_request is not None and selected_start is not None,
             'immutable original manual request and GSTART before protected work')
        return guardian_image[0](guardian_channel, role, selected_request,
                                 selected_start['original_start_pin'], phase)

    def failure_state_valid():
        keys = tuple(dict.__iter__(cg))
        if not all(type(k) is str for k in keys):
            return False
        if not (cg.get('FIRST') is first_state and cg.get('SECONDARY') is secondary_state and
                cg.get('IO_UNKNOWN') is unknown_state and cg.get('remember') is remember_original):
            return False
        if not (type(first_state) is list and len(first_state) == 1 and
                type(secondary_state) is list and len(secondary_state) == 256 and
                type(unknown_state) is list and len(unknown_state) == 1 and type(unknown_state[0]) is bool):
            return False
        return (first_state[0] is None or exception_instance(first_state[0])) and all(
            e is None or exception_instance(e) for e in secondary_state)

    def io_state(allow_uncertain=False):
        values = instance_state(io, IOType, io_image, io_functions, cg, {'slots'})
        slots = values['slots']
        need(type(slots) is list and len(slots) == 16, 'fixed original IO slots')
        for item in slots:
            need(type(item) is list and len(item) == 3 and type(item[1]) is str,
                 'exact IO slot structure before field use')
            need(item[1] in ('FREE', 'CLOSED', 'OWNED', 'PENDING', 'CLOSING'), 'original IO slot phase')
            need(item[2] is None or type(item[2]) is bool, 'original IO directory flag')
            if item[1] == 'FREE':
                need(item[0] is None and item[2] is None, 'original free slot')
            elif item[1] == 'OWNED' and not allow_uncertain:
                # Owned scandir iterators exist only INSIDE the unchanged original
                # names call. At these nonreentrant source-private entry points,
                # only known ordinary OS descriptor slots may persist.
                need(item[2] is False and type(item[0]) is int and item[0] >= 0, 'known owned OS descriptor')
            elif item[1] in ('PENDING', 'CLOSING'):
                need(allow_uncertain, 'uncertain IO blocks fresh dispatch')
        return values

    def lease_state(held, fields=None):
        wanted = {'fd', 'phase', 'birth', 'lock_info'} if fields is None else fields
        values = instance_state(held, LeaseType, lease_image, lease_functions, cg, wanted)
        if not wanted:
            return values
        need(type(values['phase']) is str and values['phase'] in
             ('NEW', 'OPEN_PENDING', 'OPEN_RETURNED', 'EX_HELD', 'CLOSE_ENTERED', 'CLOSE_RETURNED', 'CLOSE_UNKNOWN'),
             'exact original lease phase before equality/dispatch')
        need(values['fd'] is None or (type(values['fd']) is int and values['fd'] >= 0), 'exact owned descriptor field')
        birth = values['birth']
        if birth is not None:
            need(type(birth) is dict, 'actual process metadata dictionary')
            keys = tuple(dict.__iter__(birth))
            need(all(type(k) is str for k in keys) and set(keys) ==
                 {'pid', 'ppid', 'pgid', 'sid', 'start_ticks', 'rss_bytes'}, 'actual process metadata keys')
            need(all(type(birth[k]) is int and birth[k] >= 0 for k in keys), 'actual process metadata exact ints')
        bounded_kernel_data(values['lock_info'])
        return values

    def kernel_integrity(held=None, *, allow_uncertain=False):
        need(module_namespace(C) is cg and module_namespace(F) is fg and
             cg.get('IO') is io and cg.get('OwnedIO') is IOType and cg.get('GlobalLease') is LeaseType and
             cg.get('HISTORICAL_LOCK') is lock_reference and fg.get('DOMAIN') is domain_reference and
             fg.get('CONTROL') is control_reference, 'same actual selected kernel objects')
        unchanged_class(IOType, io_image, io_functions, cg)
        unchanged_class(LeaseType, lease_image, lease_functions, cg)
        unchanged_function(remember_image, cg)
        need(failure_state_valid(), 'original error/uncertainty memory integrity')
        for name, image in funding_images.items():
            need(fg.get(name) is image[0], 'same selected funding function')
            unchanged_function(image, fg)
        values = io_state(allow_uncertain)
        if held is not None:
            lease_state(held)
        return values

    complete_validator = complete_close_data
    complete_validator_image = function_image(complete_validator, active_globals)

    # No kernel instance/native method has been invoked before these snapshots.
    kernel_integrity()
    for value in (expected_head_pin, approved_handoff_pin, approved_closure, approved_opening, approved_manual_entry):
        F.plain(value)
    if approved_complete_closure is not None:
        need(role == 'CLOSER' and approved_closure is None, 'one selected closer branch')
        F.plain(approved_complete_closure)
        F.exact(approved_complete_closure, ('request', 'start', 'start_pin', 'baseline_registry_pin',
                                          'receipt_pin', 'review_pin', 'evidence_binding'))
        F.exact(approved_complete_closure['evidence_binding'], ('schema', 'admission_pin',
            'source_manifest_pin', 'profile_pin', 'result_contract_pin', 'evidence_manifest_pin',
            'clock_pin', 'expected_head_pin', 'closer_start_clock_path'))
        need(approved_complete_closure['evidence_binding']['schema'] == 'complete-close-evidence-binding-v1',
             'complete closure selected version before native acquisition')
        for key in ('start_pin', 'baseline_registry_pin', 'receipt_pin', 'review_pin'):
            F.pin(approved_complete_closure[key])
        binding = approved_complete_closure['evidence_binding']
        for key in ('admission_pin', 'source_manifest_pin', 'profile_pin', 'result_contract_pin',
                    'evidence_manifest_pin', 'clock_pin', 'expected_head_pin'):
            F.pin(binding[key])
        F.exact(approved_complete_closure['request'], ('schema', 'round_id', 'label',
            'command_sha256', 'body_reservation_ns', 'policy_sha256', 'phase_release_sha256'))
        F.exact(approved_complete_closure['start'], ('schema', 'round_id', 'label',
            'command_sha256', 'body_reservation_ns', 'policy_sha256', 'pre_entry_provenance'))
    complete_closure = F.decode(canonical(approved_complete_closure)) if approved_complete_closure is not None else None
    # Copy only strict DATA. No caller retains a mutable permission dictionary.
    expected = F.decode(canonical(expected_head_pin)) if expected_head_pin is not None else None
    handoff = F.decode(canonical(approved_handoff_pin)) if approved_handoff_pin is not None else None
    closure = F.decode(canonical(approved_closure)) if approved_closure is not None else None
    opening = F.decode(canonical(approved_opening)) if approved_opening is not None else None
    manual = F.decode(canonical(approved_manual_entry)) if approved_manual_entry is not None else None
    contexts, opened = {}, [False]
    sentinel = object()

    def fail(record, error):
        valid = failure_state_valid()
        if record['first'] is None:
            record['first'] = first_state[0] if valid and first_state[0] is not None else error
        if error is not record['first'] and all(error is not e for e in record['secondary']):
            if len(record['secondary']) < 32:
                record['secondary'].append(error)
            else:
                record['secondary_saturated'] = True
        record['phase'] = 'FAILED_UNCERTAIN_NO_RETRY'
        # Never invoke replaced global state while reporting its integrity failure.
        # The private first/secondary debt survives even when kernel memory is unsafe.
        if valid:
            try:
                unchanged_function(remember_image, cg)
                remember_original(error)
            except BaseException as secondary:
                if secondary is not record['first'] and len(record['secondary']) < 32:
                    record['secondary'].append(secondary)
                else:
                    record['secondary_saturated'] = True
        else:
            record['kernel_memory_uncertain'] = True
        return record['first']

    def rec(ctx):
        need(type(ctx) is Context, 'actual private context type before hashing')
        unchanged_class(Context, context_image, context_functions, active_globals)
        need(ctx in contexts, 'actual private context only')
        return contexts[ctx]

    def verify(record, *, allow_original_failure=False):
        need(record['phase'] not in ('FAILED_UNCERTAIN_NO_RETRY', 'RELEASED', 'CLOSE_UNKNOWN'), 'live private owner phase')
        kernel_integrity(record['lease'])
        need(unknown_state[0] is False and (first_state[0] is None or allow_original_failure is True),
             'no uncertain IO; prior original error only through source-owned cleanup/retention transition')
        need(record['pid'] == os.getpid(), 'same actual process/context; no fork or DATA restoration')
        values = lease_state(record['lease'])
        need(values['fd'] is record['owned_fd'], 'same captured actual native descriptor field')
        observation = lease_image['verify'](record['lease'])  # Original real native verification.
        kernel_integrity(record['lease'])
        need(observation['parent']['start_ticks'] == record['birth']['start_ticks'] and
             observation['parent']['pid'] == record['birth']['pid'], 'native generation unchanged')
        return observation

    def close_actual(record):
        need(record['lease_close_entered'] is False, 'one actual lease close; never replay a numeric FD')
        record['lease_close_entered'] = True
        if record['lease'] is None or record['lease_acquire_entered'] is False:
            return  # Original pure initializer never acquired any native descriptor.
        kernel_integrity(record['lease'], allow_uncertain=True)
        values = lease_state(record['lease'])
        need(values['phase'] not in ('CLOSE_ENTERED', 'CLOSE_RETURNED', 'CLOSE_UNKNOWN'),
             'original source lease was already closed/uncertain; no repeated FD close')
        if record['owned_fd'] is not None:
            need(values['fd'] is record['owned_fd'], 'no replaced native descriptor on cleanup')
        lease_image['close'](record['lease'])

    def guarded_io(name, *args, **kwargs):
        cleanup = name == 'close'
        kernel_integrity(allow_uncertain=cleanup)
        for record in contexts.values():
            if record['lease'] is not None and record['lease_initialized']:
                lease_state(record['lease'])
        if cleanup:
            slot = args[0]
            slots = io_state(True)['slots']
            need(any(slot is item for item in slots) and type(slot) is list and len(slot) == 3 and
                 type(slot[1]) is str and slot[1] == 'OWNED' and slot[2] is False and
                 type(slot[0]) is int and slot[0] >= 0, 'actual ordinary owned IO slot before close')
        return io_image[name](io, *args, **kwargs)

    def funding_io(name, *args):
        kernel_integrity()
        for record in contexts.values():
            if record['lease'] is not None and record['lease_initialized']:
                lease_state(record['lease'])
        # SAME real IO object, not a proxy or callback. Original internal self calls
        # are covered by selected single-thread/nonreentrant private stability.
        return funding_images[name][0](io, *args)

    def directory(path, *, private=True):
        need(path.is_absolute() and path.resolve(strict=True) == path, 'canonical selected directory')
        st = path.lstat()
        need(stat.S_ISDIR(st.st_mode) and st.st_uid == os.getuid() and
             ((stat.S_IMODE(st.st_mode) == 0o700) if private else not stat.S_IMODE(st.st_mode) & 0o022),
             'owned selected directory mode')
        return (st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_mtime_ns, st.st_ctime_ns)

    def sync_dir(record, path):
        directory(path, private=path not in (CONTROL, DOMAIN.parent.parent))
        slot = guarded_io('acquire', path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        primary = None
        try:
            os.fsync(slot[0])
        except BaseException as e:
            primary = fail(record, e)
        finally:
            if slot[1] == 'OWNED':
                try:
                    guarded_io('close', slot)
                except BaseException as e:
                    primary = fail(record, e)
        if primary is not None:
            raise primary

    def pinned(path, raw, mode):
        return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'mode': mode}

    def read(record, p):
        verify(record)
        return funding_io('read_pinned', p, os.getuid())[1]

    def stage_empty():
        directory(STAGE)
        need(guarded_io('names', STAGE, 2) == [], 'no pending/orphan staging file; no cleanup by guessed name')

    def publish(record, path, raw, mode, *, replace_head=False):
        verify(record); stage_empty()
        need(type(raw) is bytes and 0 < len(raw) <= F.META_CAP and mode in (0o444, 0o600), 'bounded publication')
        directory(path.parent, private=path.parent != CONTROL)
        record['publication'] = {'path': path, 'slot': None, 'temporary': None, 'phase': 'BEFORE_CREATE'}
        tmp = STAGE / ('pending-' + record['role'] + '-' + path.name)
        record['publication']['temporary'] = tmp  # Private identity exists BEFORE fallible open.
        record['publication']['phase'] = 'OPEN_PENDING'
        slot = guarded_io('acquire', tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC)
        record['publication']['slot'] = slot
        primary = None
        try:
            record['publication']['phase'] = 'WRITING'
            offset = 0
            while offset < len(raw):
                n = os.write(slot[0], raw[offset:offset + 65536])
                need(type(n) is int and 0 < n <= min(65536, len(raw) - offset), 'progressing exact write')
                offset += n
            os.fchmod(slot[0], mode)
            os.fsync(slot[0])
        except BaseException as e:
            primary = fail(record, e)
        finally:
            if slot[1] == 'OWNED':
                try:
                    guarded_io('close', slot)
                except BaseException as e:
                    primary = fail(record, e)
        if primary is not None:
            raise primary
        # Keep all partial/failed artifacts; there is no automatic unlink/retry catch.
        need(read(record, pinned(tmp, raw, mode)) == raw, 'complete staged readback')
        sync_dir(record, STAGE)
        record['publication']['phase'] = 'COMMIT_PENDING'
        if replace_head:
            need(path == HEAD, 'only exact HEAD is replaceable')
            os.replace(tmp, path)
        else:
            os.link(tmp, path, follow_symlinks=False)  # Atomic no-overwrite publication.
            sync_dir(record, path.parent)
            os.unlink(tmp)  # Only the actual known-created, closed staged file.
        sync_dir(record, STAGE)
        sync_dir(record, path.parent)
        result = pinned(path, raw, mode)
        need(read(record, result) == raw, 'final publication/custody readback')
        stage_empty()
        record['publication']['phase'] = 'COMMITTED'
        return result

    def head(record, pin_expected):
        verify(record); stage_empty(); directory(HEADS); F.pin(pin_expected)
        need(pin_expected['path'] == str(HEAD) and pin_expected['mode'] == 0o600, 'exact current HEAD pin')
        raw = read(record, pin_expected); obj = F.decode(raw)
        F.exact(obj, ('schema', 'sequence', 'registry_pin', 'previous_head_sha256'))
        need(obj['schema'] == 'fresh-active-head-v1' and type(obj['sequence']) is int and
             0 <= obj['sequence'] <= 2 * F.MAX_ENTRIES, 'bounded head generation')
        seq = obj['sequence']; F.pin(obj['registry_pin'])
        need(obj['registry_pin']['path'] == str(CONTROL / ('REGISTRY-%06d.json' % seq)), 'head registry generation')
        expected_heads = {'HEAD-%06d.json' % n for n in range(seq + 1)}
        need(set(guarded_io('names', HEADS, 2 * F.MAX_ENTRIES + 2)) == expected_heads, 'exact head history census')
        need(read(record, pinned(HEADS / ('HEAD-%06d.json' % seq), raw, 0o600)) == raw, 'current immutable head history')
        names = guarded_io('names', CONTROL, 1024)
        need({n for n in names if n.startswith('REGISTRY-')} ==
             {'REGISTRY-%06d.json' % n for n in range(seq + 1)}, 'no unadopted registry generation')
        reg_raw = read(record, obj['registry_pin']); F.registry(reg_raw)
        return obj, raw, reg_raw

    def advance(record, current, current_raw, old_registry_raw, new_registry, opening_transition=None):
        verify(record); stage_empty()
        F.plain(new_registry); new_raw = canonical(new_registry)
        F.require_append_only(old_registry_raw, new_raw, opening_transition)
        seq = current['sequence'] + 1
        need(seq <= 2 * F.MAX_ENTRIES, 'registry generation cap')
        registry_pin = publish(record, CONTROL / ('REGISTRY-%06d.json' % seq), new_raw, 0o444)
        next_head = {'schema': 'fresh-active-head-v1', 'sequence': seq,
                     'registry_pin': registry_pin, 'previous_head_sha256': hashlib.sha256(current_raw).hexdigest()}
        raw = canonical(next_head)
        publish(record, HEADS / ('HEAD-%06d.json' % seq), raw, 0o600)
        need(read(record, record['head_pin']) == current_raw, 'no stale head adoption')
        record['head_pin'] = publish(record, HEAD, raw, 0o600, replace_head=True)
        adopted, adopted_raw, adopted_registry = head(record, record['head_pin'])
        need(adopted_raw == raw and adopted_registry == new_raw, 'durable exact head adopted')
        return adopted, adopted_raw, adopted_registry

    def current_registry_pin(record):
        current, _, _ = head(record, record['head_pin'])
        return current['registry_pin']

    def active_view(record):
        verify(record)
        guard(record, 'ACTIVE')
        need(record['phase'] == 'ACTIVE' and record['request'] is not None, 'actual ACTIVE reservation')
        current, current_raw, reg_raw = head(record, record['head_pin'])
        snap = funding_io('snapshot_round', current['registry_pin'], os.getuid())
        old_raw = read(record, record['baseline_registry_pin'])
        old, _, old_starts, old_closes = F.registry(old_raw)
        reg, _, starts, closes = F.registry(reg_raw)
        name = record['request']['label']
        F.require_append_only(old_raw, reg_raw)
        need(reg['events'] == old['events'] + [{'kind': 'REGISTER', 'label': name, 'pin': record['start_pin']}] and
             reg['policies'] == old['policies'] and reg['phase'] == old['phase'] and
             set(old_starts) == set(old_closes) and set(starts) - set(closes) == {name},
             'exact own pending reservation only; every other entry closed')
        need(snap['records'][name]['receipt'] is None and
             snap['records'][name]['start'] == record['start'], 'actual current START/source reservation')
        # A separately checked accounting prefix, NOT a filtered current ledger.
        # Own reservation remains in request and the current registry stays pending.
        prefix = dict(snap, registry=old, registry_pin=record['baseline_registry_pin'],
                      records={k: snap['records'][k] for k in old_starts})
        result = F.assess_round(prefix, record['request'])
        need(result['funding_data_eligible_only'] is True, 'prior debt/uncertainty or own reservation blocks')
        return result

    def read_manual(record, expected_state_sha256=None):
        verify(record)
        guard(record, 'MANUAL')
        need(manual is not None, 'same enclosing native operation original manual pre-entry binding is unconfigured')
        F.exact(manual, ('schema', 'request', 'provenance', 'closed_state_pin', 'registration_checks', 'start_checks'))
        need(manual['schema'] == 'fresh-active-manual-entry-binding-v1', 'selected original manual entry binding')
        request, provenance = manual['request'], manual['provenance']
        F.validate_pre_entry_provenance(provenance, request['label'], request['command_sha256'], request['body_reservation_ns'])
        state_raw = read(record, manual['closed_state_pin'])
        F.metadata_decode(state_raw)  # Current manually retained accepted-state DATA, not an owner.
        if expected_state_sha256 is not None:
            need(manual['closed_state_pin']['sha256'] == expected_state_sha256, 'all closed manual costs imported before new formal entry')
        registration = F.metadata_decode(read(record, provenance['registration_pin']))
        original_start = F.metadata_decode(read(record, provenance['original_start_pin']))
        pending = F.metadata_decode(read(record, provenance['pending_manifest_pin']))
        F.exact(pending, ('schema', 'closed_state_sha256', 'operations'))
        wanted = {'entry_id': request['label'], 'command_sha256': request['command_sha256'],
                  'body_reservation_ns': request['body_reservation_ns'],
                  'registration_pin': provenance['registration_pin'], 'original_start_pin': provenance['original_start_pin']}
        need(pending['schema'] == 'fresh-current-manual-pending-v1' and
             pending['closed_state_sha256'] == manual['closed_state_pin']['sha256'] and
             pending['operations'] == [wanted], 'exact strongly-bound current enclosing pending operation only')
        need(registration['attempt_id'] == request['label'], 'original one-use ID, never a new alias')
        for document, checks in ((registration, manual['registration_checks']), (original_start, manual['start_checks'])):
            need(type(checks) is list and 1 <= len(checks) <= 16, 'explicit original pre-entry field correlations')
            for check in checks:
                F.exact(check, ('path', 'expected'))
                actual = F.select(document, check['path'])
                need(type(actual) is type(check['expected']) and actual == check['expected'], 'original pre-entry provenance differs')
        record['manual_request'] = F.decode(canonical(request))
        record['manual_provenance'] = F.decode(canonical(provenance))
        return record['manual_provenance']

    def complete_failure(record, error):
        # Protect raw identity before the inherited optional reporting path.
        slots = record['complete_errors']
        if slots[0] is None:
            slots[0] = record['first'] if record['first'] is not None else error
        # First protect the caught error, then preserve any established actual
        # kernel primary. Malformed kernel memory never becomes new authority.
        try:
            if (record['first'] is None and dict.get(cg, 'FIRST') is first_state and
                    type(first_state) is list and len(first_state) == 1 and
                    first_state[0] is not None and exception_instance(first_state[0])):
                slots[0] = first_state[0]
        except BaseException as inspection_error:
            slots[record['complete_error_count']] = inspection_error
            record['complete_error_count'] += 1
        record['first'] = slots[0]
        record['phase'] = 'FAILED_UNCERTAIN_NO_RETRY'
        if error is not slots[0] and all(error is not x for x in slots):
            index = record['complete_error_count']
            if index < len(slots):
                slots[index] = error; record['complete_error_count'] = index + 1
            else:
                record['secondary_saturated'] = True
        try:
            fail(record, error)
        except BaseException as reporting_error:
            index = record['complete_error_count']
            if reporting_error is not slots[0] and all(reporting_error is not x for x in slots) and index < len(slots):
                slots[index] = reporting_error; record['complete_error_count'] = index + 1
        return slots[0]

    def publish_complete(record):
        try:
            verify(record)
            need(role == 'CLOSER' and record['phase'] == 'HELD' and
                 record['complete_used'] is False, 'one actual complete-close selection')
            record['complete_used'] = True  # Consumed before first fallible evidence read.
            unchanged_function(complete_validator_image, active_globals)
            need(active_globals.get('complete_close_data') is complete_validator, 'fixed selected validator')
            read_manual(record)
            own_request = F.decode(canonical(record['manual_request']))
            own_provenance = F.decode(canonical(record['manual_provenance']))
            record['complete_own_request'] = own_request
            record['complete_own_provenance'] = own_provenance
            own_start = F.metadata_decode(read(record, own_provenance['original_start_pin']))
            for key in ('request', 'start', 'start_pin', 'baseline_registry_pin'):
                record[key] = complete_closure[key]
            record['phase'] = 'ACTIVE'; active_view(record)
            binding = complete_closure['evidence_binding']
            F.pin(complete_closure['receipt_pin']); F.pin(complete_closure['review_pin'])
            need(Path(complete_closure['receipt_pin']['path']).parent == CONTROL and
                 Path(complete_closure['review_pin']['path']).is_relative_to(R / 'review') and
                 complete_closure['receipt_pin']['mode'] == complete_closure['review_pin']['mode'] == 0o444,
                 'complete selected frozen receipt/review namespace')
            need(binding['expected_head_pin'] == record['head_pin'], 'exact selected current HEAD')
            review_raw = read(record, complete_closure['review_pin'])
            receipt_raw = read(record, complete_closure['receipt_pin'])
            documents = {}
            for name in ('admission_pin', 'source_manifest_pin', 'profile_pin', 'result_contract_pin',
                         'evidence_manifest_pin', 'clock_pin'):
                F.pin(binding[name]); need(binding[name]['mode'] == 0o444, 'frozen accepted metadata')
                documents[name] = read(record, binding[name])
            snapshot = funding_io('snapshot_round', current_registry_pin(record), os.getuid())
            documents['policy'] = snapshot['policies'][record['request']['policy_sha256']]
            current, raw_head, raw_reg = head(record, record['head_pin'])
            receipt, rp, new, new_raw, next_raw = complete_validator(F, complete_closure,
                receipt_raw, review_raw, documents, own_request, own_provenance, own_start,
                current, raw_head, raw_reg)
            now = time.monotonic_ns()
            need(type(now) is int and now >= record['protocol_anchor_ns'] and
                 now - record['protocol_anchor_ns'] <= own_request['body_reservation_ns'],
                 'own closer local window, never target reservation; complete meter remains external')
            # Recheck real currentness before the first publication. Existing EX
            # and registered-writer exclusion cover the following publication.
            checked, checked_head, checked_reg = head(record, record['head_pin'])
            need(checked == current and checked_head == raw_head and checked_reg == raw_reg,
                 'unchanged prevalidated publication generation')
            record['phase'] = 'RECEIPT_PUBLICATION_PENDING'
            actual = publish(record, DOMAIN / record['request']['label'] / 'receipt.json', receipt_raw, 0o600)
            need(actual == rp, 'unchanged original receipt bytes and destination')
            adopted, adopted_head, adopted_reg = advance(record, current, raw_head, raw_reg, new)
            need(adopted_head == next_raw and adopted_reg == new_raw, 'exact prevalidated durable CLOSE readback')
            record['phase'] = 'RECORDED_NOT_PHYSICALLY_SETTLED'
            return {'receipt_pin': actual, 'head_pin': record['head_pin'], 'all_costs_settled': False,
                    'native_capability': False, 'execution_permission': False}
        except BaseException as error:
            raise complete_failure(record, error)

    class Context:
        __slots__ = ()
        def __new__(cls, key):
            need(key is sentinel, 'source-private construction only')
            return object.__new__(cls)

        def initialize(self, initial_registry_raw):
            r = rec(self)
            try:
                verify(r); guard(r, 'INITIALIZE'); need(r['phase'] == 'HELD' and expected is None and role == 'PUBLISHER', 'one initial publisher')
                need(opening is not None and opening['funding_source_sha256'] == FUNDING_SHA, 'current selected funding/opening binding')
                selected = funding_io('validate_opening_binding', opening, os.getuid())
                read_manual(r, F.opening_evidence(selected)['state_sha256'])
                reg, _, starts, closes = F.registry(initial_registry_raw)
                need(not starts and not closes and reg['predecessor_sha256'] is None and
                     reg['opening_pin'] == selected['opening_pin'], 'empty new registry with complete selected current opening')
                for p in (DOMAIN.parent, DOMAIN, STAGE, HEADS, HANDOFFS, CLAIMS):
                    if not p.exists():
                        os.mkdir(p, 0o700)
                    directory(p)
                    sync_dir(r, p.parent)
                need(guarded_io('names', DOMAIN, 2) == [] and guarded_io('names', HEADS, 2) == [] and
                     not HEAD.exists(), 'no prior/orphan initialization')
                stage_empty()
                rp = publish(r, CONTROL / 'REGISTRY-000000.json', initial_registry_raw, 0o444)
                raw = canonical({'schema': 'fresh-active-head-v1', 'sequence': 0,
                                 'registry_pin': rp, 'previous_head_sha256': None})
                publish(r, HEADS / 'HEAD-000000.json', raw, 0o600)
                r['head_pin'] = publish(r, HEAD, raw, 0o600)
                head(r, r['head_pin'])
                return F.decode(canonical(r['head_pin']))
            except BaseException as e:
                raise fail(r, e)

        def refresh_opening(self):
            r = rec(self)
            try:
                verify(r)
                guard(r, 'REFRESH')
                need(r['phase'] == 'HELD' and role in ('PUBLISHER', 'CONTROLLER') and opening is not None and
                     opening['funding_source_sha256'] == FUNDING_SHA, 'new actual owner and fixed approved current opening')
                current, raw_head, raw_reg = head(r, r['head_pin'])
                old_snapshot = funding_io('snapshot_round', current['registry_pin'], os.getuid())
                _, _, starts, closes = F.registry(raw_reg)
                need(set(starts) == set(closes), 'every prior formal entry CLOSED before refresh')
                selected = funding_io('validate_opening_binding', opening, os.getuid())
                read_manual(r, F.opening_evidence(selected)['state_sha256'])
                need(old_snapshot['opening_snapshot']['opening_pin'] != selected['opening_pin'], 'new immutable closed-cost prefix required')
                F.require_opening_append(old_snapshot['opening_snapshot'], selected)
                transition = {'previous': old_snapshot['opening_snapshot'], 'current': selected,
                              'records': old_snapshot['records']}
                new = F.decode(raw_reg); new['predecessor_sha256'] = hashlib.sha256(raw_reg).hexdigest()
                new['opening_pin'] = selected['opening_pin']
                advance(r, current, raw_head, raw_reg, new, transition)
                refreshed = funding_io('snapshot_round', current_registry_pin(r), os.getuid())
                need(refreshed['opening_snapshot'] == selected and refreshed['records'] == old_snapshot['records'],
                     'opening-only refresh readback preserves every prior record/price')
                # The prelude is part of this actual enclosing body under its ORIGINAL
                # manual pre-entry START. No formal START or cost is backdated.
                return {'schema': 'fresh-current-opening-refresh-observation-v1', 'head_pin': r['head_pin'],
                        'opening_pin': selected['opening_pin'], 'formal_start_backdated': False,
                        'native_capability': False, 'execution_permission': False}
            except BaseException as e:
                raise fail(r, e)

        def current_binding(self):
            r = rec(self)
            try:
                active_view(r)
                return F.decode(canonical({'schema': 'fresh-active-current-binding-v1',
                    'request': r['request'], 'start': r['start'], 'start_pin': r['start_pin'],
                    'head_pin': r['head_pin'], 'baseline_registry_pin': r['baseline_registry_pin'],
                    'native_capability': False, 'execution_permission': False}))
            except BaseException as e:
                raise fail(r, e)

        def begin(self, request):
            r = rec(self)
            try:
                verify(r); guard(r, 'HELD'); need(r['phase'] == 'HELD' and role in ('PUBLISHER', 'CONTROLLER'), 'begin once')
                F.plain(request)
                current, raw_head, raw_reg = head(r, r['head_pin'])
                snapshot = funding_io('snapshot_round', current['registry_pin'], os.getuid())
                read_manual(r, F.opening_evidence(snapshot['opening_snapshot'])['state_sha256'])
                need(request == r['manual_request'], 'formal entry is the SAME original manually reserved enclosing operation')
                assessment = F.assess_round(snapshot, request)
                need(assessment['funding_data_eligible_only'] is True, 'NEW admission blocked')
                r['request'] = F.decode(canonical(request)); r['baseline_registry_pin'] = current['registry_pin']
                r['phase'] = 'START_PUBLICATION_PENDING'  # Private role/request precedes any mkdir/open.
                name = r['request']['label']; folder = DOMAIN / name
                r['start'] = {'schema': 'fresh-round-start-v1', 'round_id': F.ROUND_ID,
                              'label': name, 'command_sha256': request['command_sha256'],
                              'body_reservation_ns': request['body_reservation_ns'], 'policy_sha256': request['policy_sha256'],
                              'pre_entry_provenance': r['manual_provenance']}
                os.mkdir(folder, 0o700); sync_dir(r, DOMAIN)
                r['start_pin'] = publish(r, folder / 'START.json', canonical(r['start']), 0o600)
                new = F.decode(raw_reg); new['predecessor_sha256'] = hashlib.sha256(raw_reg).hexdigest()
                new['events'].append({'kind': 'REGISTER', 'label': name, 'pin': r['start_pin']})
                advance(r, current, raw_head, raw_reg, new)
                r['phase'] = 'ACTIVE'
                active_view(r)
                return {'schema': 'active-registration-observation-v1', 'start_pin': r['start_pin'],
                        'head_pin': r['head_pin'], 'native_capability': False, 'execution_permission': False}
            except BaseException as e:
                raise fail(r, e)

        def native_lease_for_controller(self, caller_module, actual_registry=None, purpose='PRODUCTION'):
            r = rec(self)
            try:
                need(role == 'CONTROLLER' and caller_module is C and r['phase'] == 'ACTIVE',
                     'same authenticated controller module and ACTIVE actual owner')
                if actual_registry is None:
                    need(purpose == 'PRODUCTION', 'no registry-free cleanup/retention exemption')
                    verify(r)
                    guard(r, 'ACTIVE')
                else:
                    need(purpose in ('CLEANUP','RETENTION'), 'fixed source-owned continuation purpose')
                    kernel_integrity(r['lease'])
                    need(cg.get('joined_continuation_check') is continuation_image[0],
                         'actual fixed C2 continuation verifier')
                    unchanged_function(continuation_image, cg)
                    # Actual source function, same private registry/ctx, no DATA
                    # Boolean grants. It proves the known lifecycle before this
                    # one narrow original-error continuation can exist.
                    need(continuation_image[0](self, actual_registry, purpose) is True,
                         'actual known cleanup/sealed retention continuation absent')
                    old = r.get('continuation')
                    need(old is None or (old['registry'] is actual_registry and
                         (old['first'] is None or old['first'] is first_state[0])), 'same registry and retained actual original failure')
                    r['continuation'] = {'registry':actual_registry,'purpose':purpose,'first':first_state[0]}
                    verify(r, allow_original_failure=True)
                    guard(r, 'RETENTION' if purpose == 'RETENTION' else 'ACTIVE')
                return r['lease']  # Same actual original C2 EX/OFD; never serialized to B.
            except BaseException as e:
                raise fail(r, e)

        def check(self, nested_ns, cleanup_ns):
            r = rec(self)
            try:
                F.uint(nested_ns); F.uint(cleanup_ns)
                assessment = active_view(r)
                now = time.monotonic_ns()
                need(type(now) is int and now >= r['protocol_anchor_ns'], 'actual local monotonic sample')
                elapsed = now - r['protocol_anchor_ns']
                need(elapsed + nested_ns + cleanup_ns <= r['request']['body_reservation_ns'], 'retained body reservation locally exhausted')
                return {'schema': 'active-local-reservation-observation-v1', 'elapsed_since_protocol_anchor_ns': elapsed,
                        'local_reservation_check_passed': True, 'whole_outer_body_fit_proved': False,
                        'clock_scope': 'private_protocol_anchor_to_local_sample_imports_and_final_exit_excluded',
                        'unallocated_policy_ns': assessment['remaining_policy_ns'] - assessment['requested_reservation_ns'],
                        'own_reservation_encumbered_ns': assessment['requested_reservation_ns'], 'execution_permission': False}
            except BaseException as e:
                raise fail(r, e)

        def release_for_exec(self):
            r = rec(self)
            try:
                active_view(r); need(role == 'PUBLISHER', 'separate publisher owner only')
                intent = {'schema': 'fresh-active-handoff-intent-v1', 'source_role': role, 'destination_role': 'CONTROLLER',
                          'request': r['request'], 'start': r['start'], 'start_pin': r['start_pin'],
                          'head_pin': r['head_pin'], 'baseline_registry_pin': r['baseline_registry_pin'],
                          'protocol_anchor_ns': r['protocol_anchor_ns'], 'native_capability_transferred': False}
                r['phase'] = 'HANDOFF_PUBLICATION_PENDING'
                p = publish(r, HANDOFFS / (r['request']['label'] + '.json'), canonical(intent), 0o444)
                verify(r); r['phase'] = 'CLOSE_ENTERED'; close_actual(r); r['phase'] = 'RELEASED'
                return p  # Permission/timing DATA only. No FD/owner survives this API.
            except BaseException as e:
                raise fail(r, e)

        def adopt_handoff(self):
            r = rec(self)
            try:
                verify(r); guard(r, 'ADOPT'); need(role == 'CONTROLLER' and r['phase'] == 'HELD' and handoff is not None, 'fresh actual controller owner plus approved intent')
                intent = F.decode(read(r, handoff))
                F.exact(intent, ('schema', 'source_role', 'destination_role', 'request', 'start', 'start_pin',
                                 'head_pin', 'baseline_registry_pin', 'protocol_anchor_ns', 'native_capability_transferred'))
                need(intent['schema'] == 'fresh-active-handoff-intent-v1' and intent['source_role'] == 'PUBLISHER' and
                     intent['destination_role'] == role and intent['native_capability_transferred'] is False and
                     intent['head_pin'] == r['head_pin'], 'exact data intent/current head')
                for k in ('request', 'start', 'start_pin', 'baseline_registry_pin'):
                    r[k] = intent[k]
                F.uint(intent['protocol_anchor_ns'])
                # Cross-process clock-domain applicability is an external role-profile premise.
                r['protocol_anchor_ns'] = intent['protocol_anchor_ns']
                r['phase'] = 'ACTIVE'
                selected_head = current_registry_pin(r)
                selected_snapshot = funding_io('snapshot_round', selected_head, os.getuid())
                read_manual(r, F.opening_evidence(selected_snapshot['opening_snapshot'])['state_sha256'])
                need(r['request'] == r['manual_request'] and r['start']['pre_entry_provenance'] == r['manual_provenance'],
                     'handoff is same original enclosing operation')
                active_view(r)
                claim = {'schema': 'fresh-active-handoff-claim-v1', 'handoff_sha256': handoff['sha256'],
                         'start_sha256': r['start_pin']['sha256'], 'native_owner_is_not_this_record': True}
                publish(r, CLAIMS / (r['request']['label'] + '.json'), canonical(claim), 0o444)
                return {'handoff_claimed': True, 'new_real_lease_acquired': True, 'native_capability': False, 'execution_permission': False}
            except BaseException as e:
                raise fail(r, e)

        def publish_reviewed_close(self):
            r = rec(self)
            if complete_closure is not None:
                return publish_complete(r)
            try:
                verify(r); need(role == 'CLOSER' and r['phase'] == 'HELD' and closure is not None,
                                'new actual closer plus independently accepted frozen evidence')
                read_manual(r)  # The CLOSER has its OWN separately funded native body, never admin-filled.
                F.exact(closure, ('request', 'start', 'start_pin', 'baseline_registry_pin', 'receipt_pin', 'review_pin'))
                for k in ('request', 'start', 'start_pin', 'baseline_registry_pin'):
                    r[k] = closure[k]
                r['phase'] = 'ACTIVE'; active_view(r)
                F.pin(closure['receipt_pin']); F.pin(closure['review_pin'])
                need(Path(closure['receipt_pin']['path']).parent == CONTROL and
                     Path(closure['review_pin']['path']).is_relative_to(R / 'review') and
                     closure['receipt_pin']['mode'] == closure['review_pin']['mode'] == 0o444,
                     'selected frozen close candidate/review namespace')
                review_raw = read(r, closure['review_pin'])  # Opaque independently accepted evidence, never native authority.
                raw = read(r, closure['receipt_pin']); receipt = F.decode(raw)
                need(receipt['schema'] == 'fresh-round-receipt-v1' and receipt['round_id'] == F.ROUND_ID and
                     receipt['label'] == r['request']['label'] and receipt['start_sha256'] == r['start_pin']['sha256'] and
                     receipt['independent_outcome_review_sha256'] == hashlib.sha256(review_raw).hexdigest(), 'exact reviewed body/uncertainty record')
                F.exact(receipt, ('schema', 'round_id', 'label', 'start_sha256', 'outcome', 'body_elapsed_ns',
                                  'administrative_debit_ns', 'body_begin_ns', 'body_end_ns', 'body_fully_observed',
                                  'cleanup_known', 'custody_complete', 'nested_entries_complete', 'uncertainty',
                                  'peak_sampled_rss_bytes', 'tail_state', 'independent_outcome_review_sha256'))
                need(receipt['outcome'] == 'STOP' and receipt['cleanup_known'] is False and
                     receipt['tail_state'] == 'UNKNOWN' and receipt['uncertainty'] is not None,
                     'metadata-only CLOSER records STOP/UNKNOWN; native success needs separate source adoption')
                need(receipt['outcome'] in ('PASS', 'STOP') and
                     receipt['tail_state'] in ('COMPLETE', 'ADMIN_ONLY_OPEN', 'UNKNOWN'), 'retained outcome/unknown scope')
                for key in ('body_fully_observed', 'cleanup_known', 'custody_complete', 'nested_entries_complete'):
                    need(type(receipt[key]) is bool, 'exact qualification flag')
                if receipt['body_elapsed_ns'] is not None:
                    F.uint(receipt['body_elapsed_ns']); F.uint(receipt['body_begin_ns']); F.uint(receipt['body_end_ns'])
                    need(receipt['body_end_ns'] >= receipt['body_begin_ns'] and
                         receipt['body_end_ns'] - receipt['body_begin_ns'] == receipt['body_elapsed_ns'], 'exact reviewed body interval')
                F.uint(receipt['administrative_debit_ns'])
                policy_snapshot = funding_io('snapshot_round', current_registry_pin(r), os.getuid())
                policy = policy_snapshot['policies'][r['request']['policy_sha256']]
                need(receipt['administrative_debit_ns'] == policy['administrative_debit_ns'], 'separate exact admin policy')
                # No field is invented from local check(), PID/FD observations, or caller booleans.
                # Genuine whole-body/cleanup/review acceptance is the trusted closer-source premise.
                current, raw_head, raw_reg = head(r, r['head_pin'])
                r['phase'] = 'RECEIPT_PUBLICATION_PENDING'
                rp = publish(r, DOMAIN / r['request']['label'] / 'receipt.json', raw, 0o600)
                new = F.decode(raw_reg); new['predecessor_sha256'] = hashlib.sha256(raw_reg).hexdigest()
                new['events'].append({'kind': 'CLOSE', 'label': r['request']['label'], 'pin': rp})
                advance(r, current, raw_head, raw_reg, new)
                r['phase'] = 'RECORDED_NOT_PHYSICALLY_SETTLED'
                return {'receipt_pin': rp, 'head_pin': r['head_pin'], 'all_costs_settled': False, 'execution_permission': False}
            except BaseException as e:
                raise fail(r, e)

        def release(self):
            r = rec(self)
            need(r['phase'] not in ('RELEASED', 'CLOSE_UNKNOWN'), 'one actual close attempt')
            try:
                r['phase'] = 'CLOSE_ENTERED'
                close_actual(r)
                r['phase'] = 'RELEASED'
            except BaseException as e:
                r['phase'] = 'CLOSE_UNKNOWN'
                if complete_closure is not None:
                    primary = complete_failure(r, e)
                    r['phase'] = 'CLOSE_UNKNOWN'
                    raise primary
                if r['first'] is None:
                    r['first'] = e
                raise r['first']

    context_image, context_functions = class_image(Context,
        ('initialize', 'refresh_opening', 'current_binding', 'begin', 'native_lease_for_controller',
         'check', 'release_for_exec', 'adopt_handoff', 'publish_reviewed_close', 'release'),
        active_globals, slotted=True)

    def open_owner():
        need(opened[0] is False, 'one context per exact bound source-role invocation')
        opened[0] = True
        unchanged_class(Context, context_image, context_functions, active_globals)
        ctx = Context(sentinel)
        r = {'role': role, 'pid': os.getpid(), 'lease': None, 'birth': None,
             'phase': 'PRIVATE_BEFORE_ACQUIRE', 'first': None, 'secondary': [], 'secondary_saturated': False,
             'request': None, 'head_pin': expected, 'publication': None,
             'protocol_anchor_ns': None, 'lease_close_entered': False,
             'lease_initialized': False, 'lease_acquire_entered': False, 'owned_fd': None,
             'kernel_memory_uncertain': False, 'complete_used': False,
             'complete_errors': [None] * 34, 'complete_error_count': 1,
             'complete_own_request': None, 'complete_own_provenance': None}
        contexts[ctx] = r  # Private ownership/role identity BEFORE fallible initialization/acquire.
        try:
            guard(r, 'BOOTSTRAP')
            values = kernel_integrity()
            need(all(slot[1] in ('FREE', 'CLOSED') for slot in values['slots']),
                 'fresh role begins with no borrowed/pending IO slot')
            r['protocol_anchor_ns'] = time.monotonic_ns()  # Partial local window only.
            need(type(r['protocol_anchor_ns']) is int and r['protocol_anchor_ns'] >= 0, 'genuine finite local protocol anchor')
            unchanged_class(LeaseType, lease_image, lease_functions, cg)
            r['lease'] = object.__new__(LeaseType)  # No metaclass/class __call__/foreign __new__ dispatch.
            lease_state(r['lease'], fields=set())
            lease_image['__init__'](r['lease'])
            r['lease_initialized'] = True
            kernel_integrity(r['lease'])
            r['phase'] = 'ACQUIRE_PENDING'; r['lease_acquire_entered'] = True
            lease_image['acquire'](r['lease'])
            kernel_integrity(r['lease'])
            acquired = lease_state(r['lease'])
            r['owned_fd'] = acquired['fd']; r['birth'] = dict(acquired['birth'])
            r['phase'] = 'HELD'; verify(r)
            return ctx
        except BaseException as e:
            fail(r, e)
            # Exactly one actual cleanup entry; unsafe metadata remains unknown debt,
            # never guessed/replayed descriptor cleanup or a reconstructed owner.
            try:
                close_actual(r)
            except BaseException as close_error:
                fail(r, close_error)
            raise r['first']

    return open_owner
