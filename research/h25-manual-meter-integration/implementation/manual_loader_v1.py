"""Fixed manual startup source transport; SOURCE ONLY, no command grant.

Adapted from fresh-round-bootstrap-loader-v3/bootstrap_loader.py, exact donor
e681aa3ee4c48d2a3273899a1bb11af76929d440d05f47320e7fea26df9f9f3e.
Predecessor transport/IO/error rules below are retained. This successor selects
the materialized manual C2 profile and exact F4/A4; no payload adapter is changed.

The external exact fresh-interpreter launcher/OS/source-custody selection is
this component's trust root. This is the original explicitly selected operating
TCB, NOT a universal loaded-image proof. Immutable bootstrap source reads take
place before the future global EX and must be admitted as startup work. Registry,
head, opening-corpus and historical marker reads belong to the later real owner.
No caller may supply a module object, callable, file path or source image.
Literal V3 selection loads complete composed C2 source into its own actual private
module/global namespace; only its original IO/native-kernel transport is used here.
C2 source acceptance is not a selected runtime profile or full-controller caller
admission. Actual profile/adoption/runtime remain open.
"""
import builtins
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import sys
from types import ModuleType

W = Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
R = W / 'outputs/h25-data-handling-20261028'
ENV = {'PATH':'/usr/bin:/bin','PYTHONHASHSEED':'0','LANG':'C.UTF-8',
       'LC_ALL':'C.UTF-8','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1'}
INITIAL_PATH = ('/usr/lib/python312.zip','/usr/lib/python3.12','/usr/lib/python3.12/lib-dynload')
FIRST, SECONDARY, IO_UNKNOWN = [None], [None] * 32, [False]
SLOTS = [[None, 'FREE', None, False] for unused in range(32)]
RETAINED = []
USED = [False]
PACKAGE = R / 'areas/manual-integration-v29'
REFERENCE = W / 'outputs/f4-a4-manual-integration-20261104T0343Z/reference/areas'
CONTROLLER = PACKAGE / 'manual_controller_v1.py'
FUNDING = REFERENCE / 'fresh-round-reusable-record-implementation-v3/funding_current.py'
ACTIVE = REFERENCE / 'fresh-round-financial-version-bindings-v1/active_current.py'
# Exact frozen source selection; source acceptance and operational admission
# remain separate, and this component creates no command permission.
SELECTED = {'funding': {'bytes':151228,'sha256':'a0c2ab55aaf47350bb51fa98e07bc7b520c388742f2da06820d2d10f7d8f506d'},
            'active': {'bytes':91614,'sha256':'f651f9acd3328db337f334a31d1cccec38098eecf9e72e9c62deaf06bd79bd45'}}
# Filled with literal reviewed file hashes at source freeze, never runtime DATA.
NEW_PINS = {
    'controller':{'bytes':81638,'sha256':'208e9cdc763f92858cacd089bdd56c55a467fb53d532f5f315e8f6a834d6fa02'},
    'candidate':{'bytes':12935,'sha256':'34de91b231780be9ceb20f4340e13b2cd6215d11ed4b64ded8f063fb011d0b58'},
    'writer':{'bytes':39367,'sha256':'3aba6ee55c6b2264d20dc69b9e55ea154ac4c9e012815d3e75d9a5c92ed97bce'},
    'settlement':{'bytes':19346,'sha256':'236a6823c0ca9722e00fd9f6b4196cd576a290778ad642f0c2da91a6aba325a6'}}


class AdapterStop(RuntimeError):
    pass


def remember(error):
    if FIRST[0] is None:
        FIRST[0] = error
    elif error is not FIRST[0]:
        for index in range(32):
            if SECONDARY[index] is error:
                break
            if SECONDARY[index] is None:
                SECONDARY[index] = error
                break
        else:
            IO_UNKNOWN[0] = True
    return FIRST[0]


def need(value, message):
    if not value:
        raise AdapterStop(message)


def identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_uid, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def acquire(path, flags=0, directory=False):
    need(not IO_UNKNOWN[0], 'unknown IO blocks new acquisition')
    slot = next(s for s in SLOTS if s[1] in ('FREE','CLOSED'))
    slot[:] = [None, 'PENDING', str(path), directory]
    try:
        slot[0] = os.scandir(path) if directory else os.open(path, flags | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        slot[1] = 'OWNED'
        return slot
    except BaseException as error:
        IO_UNKNOWN[0] = True
        remember(error)
        raise


def close(slot):
    need(slot[1] == 'OWNED', 'known owned close only; no retry')
    slot[1] = 'CLOSING'
    try:
        slot[0].close() if slot[3] else os.close(slot[0])
    except BaseException as error:
        slot[1] = 'CLOSE_UNKNOWN'
        IO_UNKNOWN[0] = True
        remember(error)
        raise
    slot[1] = 'CLOSED'


def names(path, cap):
    slot, values = acquire(path, directory=True), []
    try:
        for item in slot[0]:
            need(len(values) < cap, 'directory member cap')
            values.append(item.name)
    except BaseException as error:
        remember(error)
        raise
    finally:
        try:
            close(slot)
        except BaseException as secondary:
            remember(secondary)
    need(not IO_UNKNOWN[0], 'directory close unknown')
    return values


def read_fd(slot, cap, proc=False):
    before = os.fstat(slot[0])
    if not proc:
        need(stat.S_ISREG(before.st_mode) and before.st_uid in (0,os.getuid()) and
             before.st_nlink == 1 and before.st_size <= cap, 'stable regular owner/link/size')
        need(identity(Path(slot[2]).lstat()) == identity(before), 'descriptor/path differs')
        os.lseek(slot[0], 0, os.SEEK_SET)
    chunks, count = [], 0
    while True:
        block = os.read(slot[0], min(65536,cap + 1 - count))
        if not block:
            break
        chunks.append(block)
        count += len(block)
        need(count <= cap, 'read cap')
    raw = b''.join(chunks)
    if not proc:
        need(count == before.st_size and identity(os.fstat(slot[0])) == identity(before) ==
             identity(Path(slot[2]).lstat()), 'stable descriptor/path changed')
    return raw


def stable_source(path, expected):
    need(path.is_absolute() and path.resolve(strict=True) == path, 'canonical source path')
    before = path.lstat()
    need(stat.S_IMODE(before.st_mode) == 0o444, 'frozen source mode')
    slot = acquire(path, os.O_RDONLY | os.O_NONBLOCK)
    try:
        need(identity(before) == identity(os.fstat(slot[0])), 'source opened identity')
        raw = read_fd(slot, expected['bytes'])
        need(len(raw) == expected['bytes'] and hashlib.sha256(raw).hexdigest() == expected['sha256'], 'source pin')
    except BaseException as error:
        remember(error)
        raise
    finally:
        try:
            close(slot)
        except BaseException as secondary:
            remember(secondary)
    need(not IO_UNKNOWN[0], 'source close unknown')
    return raw


def metadata(path, cap=8192):
    slot = acquire(path, os.O_RDONLY | os.O_NONBLOCK)
    try:
        raw = read_fd(slot, cap, proc=True)
    except BaseException as error:
        remember(error)
        raise
    finally:
        try:
            close(slot)
        except BaseException as secondary:
            remember(secondary)
    need(not IO_UNKNOWN[0], 'metadata close unknown')
    return raw


def process(pid):
    raw = metadata('/proc/' + str(pid) + '/stat')
    end = raw.rfind(b') ')
    need(end >= 0 and raw.split(b' ',1)[0] == str(pid).encode('ascii'), 'process stat syntax/pid')
    fields = raw[end + 2:].split()
    return {'pid':pid,'ppid':int(fields[1]),'pgid':int(fields[2]),'sid':int(fields[3]),
            'start_ticks':int(fields[19]),'rss_bytes':int(fields[21])*os.sysconf('SC_PAGE_SIZE')}


def clean_launch(profile):
    need(type(profile) is str and profile in ('normal','optimized'), 'exact manual profile')
    need(sys.executable == '/usr/bin/python3.12' and sys.implementation.name == 'cpython' and
         sys.version_info[:2] == (3,12) and sys.base_prefix == '/usr', 'selected interpreter')
    need(sys.flags.optimize == (1 if profile == 'optimized' else 0) and sys.flags.no_site == sys.flags.no_user_site ==
         sys.flags.dont_write_bytecode == 1 and sys.flags.safe_path and
         sys.flags.ignore_environment == sys.flags.isolated == sys.flags.hash_randomization == 0 and
         tuple(sys.path) == INITIAL_PATH and dict(os.environ) == ENV and os.getcwd() == str(W), 'clean launch')
    need(len(names('/proc/self/task',2)) == 1 and signal.getitimer(signal.ITIMER_REAL) == (0.0,0.0) and
         signal.getsignal(signal.SIGALRM) == signal.SIG_DFL and
         signal.getsignal(signal.SIGCHLD) == signal.SIG_DFL, 'single thread/default signal owners')
    status = dict(line.split(':',1) for line in metadata('/proc/self/status',65536).decode('ascii').splitlines() if ':' in line)
    need(int(status['Umask'].strip(),8) == 0o077, 'umask0077')
    for fd in (1,2):
        st = os.fstat(fd)
        need(stat.S_ISREG(st.st_mode) and stat.S_IMODE(st.st_mode) == 0o600 and
             st.st_uid == os.getuid() and st.st_nlink == 1, 'captured0600 current-owner streams')


# Private handles are admitted by this exact source transport and retained here.
# Attribute lookalikes or caller ModuleType objects never enter this registry.
class _Loaded:
    __slots__ = ('C','F','A','candidate','writer','settlement','profile')

_HANDLES = {}
_PARTIAL_C = [None]
_MANUAL_METHODS = ('adopt_financial_candidate','enter_enclosing_manual',
    'prepare_metadata_close','publish_metadata_close','write_original_record',
    'initialize','refresh_opening','current_binding','begin',
    'native_lease_for_controller','check','release_for_exec','adopt_handoff',
    'publish_reviewed_close','release')


def _source(path, pin, subject, name):
    need(name not in sys.modules, 'private module name already used')
    raw = stable_source(path,pin)
    module = ModuleType(name)
    module.__dict__.update(__file__=str(subject),__name__=name,__package__=None,
                           __spec__=None,__builtins__=builtins)
    sys.modules[name] = module
    RETAINED.append((module,raw))  # Retain even a failed top-level load.
    exec(compile(raw,str(subject),'exec',dont_inherit=True),module.__dict__)
    return module


def load_fixed_sources(profile):
    """Load exact source only; do not acquire EX or bind an owner here.

    Both this launch check and the materialized C2 clean_launch(profile) precede
    any manual meter alarm. Parent and native meter use separate fresh processes.
    F4/A4 use original subject filenames with retained exact source bytes; this
    preserves the writer's explicitly selected original-source function checks.
    """
    need(USED[0] is False,'one source loading attempt including failure')
    USED[0] = True
    clean_launch(profile)
    need(set(NEW_PINS)=={'controller','candidate','writer','settlement'},
         'all exact joined source pins required')
    C = _source(CONTROLLER,NEW_PINS['controller'],CONTROLLER,
                'h25_manual_v1_private_controller')
    _PARTIAL_C[0] = C  # Retain partial native transport even if later source load fails.
    need(C.FIRST[0] is None and C.IO_UNKNOWN[0] is False and
         C.SOFT_DEADLINE[0] is None and C.ACTIVE_CASE[0] is None and
         not C.RETAINED_MODULES and all(s[1] in ('FREE','CLOSED') for s in C.IO.slots),
         'pristine actual manual C2 native kernel')
    F = _source(FUNDING,SELECTED['funding'],
        R/'areas/fresh-round-reusable-record-implementation-v3/funding_current.py',
        'h25_manual_v1_private_funding')
    A = _source(ACTIVE,SELECTED['active'],
        R/'areas/fresh-round-financial-version-bindings-v1/active_current.py',
        'h25_manual_v1_private_active')
    peers = []
    for key,filename in (('candidate','financial_candidate_v1.py'),
                         ('writer','original_records_v29.py'),
                         ('settlement','manual_settlement_v1.py')):
        peers.append(_source(PACKAGE/filename,NEW_PINS[key],PACKAGE/filename,
                              'h25_manual_v1_private_'+key))
    launch = C.clean_launch(profile)
    need(FIRST[0] is None and IO_UNKNOWN[0] is False and
         C.FIRST[0] is None and C.IO_UNKNOWN[0] is False and
         all(s[1] in ('FREE','CLOSED') for s in SLOTS+C.IO.slots),
         'both transports known closed before owner binding')
    loaded = _Loaded()
    loaded.C,loaded.F,loaded.A = C,F,A
    loaded.candidate,loaded.writer,loaded.settlement = peers
    loaded.profile = profile
    modules = (C,F,A,*peers)
    images = tuple((m,m.__dict__,tuple((n,v,v.__code__) for n,v in m.__dict__.items()
                    if type(v).__name__=='function' and v.__globals__ is m.__dict__)) for m in modules)
    classes = tuple((cls,dict(cls.__dict__),tuple((fn,fn.__code__) for fn in cls.__dict__.values()
                    if type(fn).__name__=='function')) for cls in (C.OwnedIO,C.GlobalLease))
    _HANDLES[loaded] = {'modules':modules,'images':images,'classes':classes,'launch':launch,
                       'owner':'NOT_BOUND','ctx':None,'ports':None}
    RETAINED.append(loaded)
    return loaded


def _actual(loaded):
    need(type(loaded) is _Loaded and loaded in _HANDLES,'actual private loader handle')
    state = _HANDLES[loaded]
    need((loaded.C,loaded.F,loaded.A,loaded.candidate,loaded.writer,loaded.settlement)==state['modules'],
         'same selected retained modules')
    for module,namespace,images in state['images']:
        need(module.__dict__ is namespace,'same actual module namespace')
        for name,fn,code in images:
            need(namespace.get(name) is fn and fn.__code__ is code and fn.__globals__ is namespace,
                 'same actual selected source function')
    for cls,image,methods in state['classes']:
        need(dict(cls.__dict__)==image,'unchanged actual C2 native class image')
        need(all(fn.__code__ is code for fn,code in methods),'unchanged actual C2 native method code')
    return state


def open_manual_owner(loaded, role, *, approved_opening, expected_head_pin,
                      approved_manual_entry):
    """Fixed source caller supplies literal PUBLISHER or CLOSER, never a port.

    All DATA remains untrusted evidence. Native acquisition is performed only by
    actual A4.bind_api -> its one-use factory -> original GlobalLease.acquire.
    """
    state = _actual(loaded)
    need(type(role) is str and role in ('PUBLISHER','CLOSER'),'manual-only literal role')
    need(state['owner']=='NOT_BOUND','one manual owner attempt')
    state['owner'] = 'BIND_PENDING'
    try:
        factory = loaded.A.bind_api(loaded.C,loaded.F,role=role,
            expected_head_pin=expected_head_pin,approved_opening=approved_opening,
            approved_manual_entry=approved_manual_entry)
        RETAINED.append(factory)
        state['owner'] = 'FACTORY_PENDING'
        ctx = factory()
        state['ctx'] = ctx  # Retain before class-image validation can fail.
        RETAINED.append(ctx)
        namespace = loaded.A.__dict__
        image,functions = loaded.A.class_image(type(ctx),_MANUAL_METHODS,namespace,slotted=True)
        state['ports'] = (type(ctx),image,functions)
        state['owner'] = 'HELD'
        return ctx
    except BaseException as error:
        if FIRST[0] is None:
            FIRST[0] = error  # Delivered first error before further bookkeeping.
        remember(error)
        # A4 internally owns unreturned-context cleanup; never guessed-close it.
        state['owner'] = 'FACTORY_UNKNOWN' if state['ctx'] is None else 'HELD_FAILED'
        raise


def manual_call(loaded, ctx, method, *args):
    state = _actual(loaded)
    need(ctx is state['ctx'] and state['owner'] in ('HELD','HELD_FAILED'),'actual retained manual context')
    need(method in ('adopt_financial_candidate','initialize','refresh_opening',
                    'publish_metadata_close','check'),'fixed manual dispatch ports only')
    cls,image,functions = state['ports']
    loaded.A.unchanged_class(cls,image,functions,loaded.A.__dict__)
    return image[method](ctx,*args)


def release_manual_once(loaded):
    state = _actual(loaded)
    ctx = state['ctx']
    if ctx is None:
        return  # Actual factory already owns its own failed construction cleanup.
    need(state['owner'] in ('HELD','HELD_FAILED'),'one returned-context release entry')
    state['owner'] = 'RELEASE_ENTERED'
    try:
        # No payload adapter and no recovered numeric descriptor authority.
        cls,image,functions = state['ports']
        loaded.A.unchanged_class(cls,image,functions,loaded.A.__dict__)
        image['release'](ctx)
        state['owner'] = 'RELEASE_RETURNED'
    except BaseException as error:
        if FIRST[0] is None:
            FIRST[0] = error
        state['owner'] = 'CLOSE_UNKNOWN'
        remember(error)
        raise


def cleanup_transports_once(loaded=None):
    """Release known descriptor slots once; preserve pending/close uncertainty."""
    C = _actual(loaded)['modules'][0] if loaded is not None else _PARTIAL_C[0]
    if C is not None:
        for slot in C.IO.slots:
            if slot[1]=='OWNED':
                try:
                    C.OwnedIO.close(C.IO,slot)
                except BaseException as error:
                    if FIRST[0] is None:
                        FIRST[0] = error
                    remember(error)
    for slot in SLOTS:
        if slot[1]=='OWNED':
            try:
                close(slot)
            except BaseException as error:
                if FIRST[0] is None:
                    FIRST[0] = error
                remember(error)


def cleanup_disposition(loaded=None):
    state = _actual(loaded) if loaded is not None else None
    C = state['modules'][0] if state is not None else _PARTIAL_C[0]
    owner = state['owner'] if state is not None else 'NO_OWNER_ATTEMPT'
    known = (not IO_UNKNOWN[0] and all(s[1] in ('FREE','CLOSED') for s in SLOTS)
             and (C is None or (not C.IO_UNKNOWN[0] and
                  all(s[1] in ('FREE','CLOSED') for s in C.IO.slots)))
             and owner in ('NOT_BOUND','NO_OWNER_ATTEMPT','RELEASE_RETURNED'))
    return {'known_closed':known,'owner':owner,'loader_io_unknown':IO_UNKNOWN[0],
            'controller_io_unknown':C.IO_UNKNOWN[0] if C is not None else False,
            'first':FIRST[0],'controller_first':C.FIRST[0] if C is not None else None}
