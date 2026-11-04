"""Once-only own MANUAL_ONLY financial import using the actual selected C2 IO/EX.

Publication sequence adapts A4 publish/publish_financial_candidate (H25 retained
f651f9ac...). It is deliberately separate from A4's distinct-target close.
Source selection, independent adjudicator admission and native operating TCB
remain external premises. No execution permission is created by this source.
"""
import os
import stat
from pathlib import Path
from types import FunctionType, ModuleType


class SettlementError(RuntimeError):
    pass


def need(condition, message):
    if condition is not True:
        raise SettlementError(message)


class FailureState:
    """Pure error/custody state; a status image is never a native capability."""
    def __init__(self):
        self.first = None
        self.secondary = []
        self.unknown = False
        self.phase = 'HELD'
        self.reservation_retained = True

    def remember(self, error, uncertain=False):
        if self.first is None:
            self.first = error
        elif error is not self.first and all(error is not e for e in self.secondary):
            if len(self.secondary) < 32:
                self.secondary.append(error)
            else:
                self.unknown = True
        self.unknown = self.unknown or uncertain
        return self.first

    def publication_entered(self):
        need(self.phase == 'HELD', 'once-only import attempt')
        self.phase = 'PUBLICATION_PENDING'

    def verified(self):
        need(self.phase == 'PUBLICATION_PENDING' and self.first is None and not self.unknown,
             'complete readback before reservation release')
        self.phase = 'COMMITTED_READBACK'
        self.reservation_retained = False


def bind_manual_settlement(controller, funding, candidate_module):
    """Return one fresh native owner factory; do not accept caller lease/IO ports."""
    need(all(type(m) is ModuleType for m in (controller, funding, candidate_module)),
         'actual authenticated selected modules')
    cg, fg, bg = controller.__dict__, funding.__dict__, candidate_module.__dict__
    io, IOType, LeaseType = cg['IO'], cg['OwnedIO'], cg['GlobalLease']
    need(type(io) is IOType and type(IOType) is type and type(LeaseType) is type,
         'exact original C2 IO and lease classes')
    io_names = ('__init__', 'acquire', 'close', 'read', 'names', 'write')
    lease_names = ('__init__', 'acquire', 'verify', 'close')
    io_methods = {n: IOType.__dict__.get(n) for n in io_names}
    lease_methods = {n: LeaseType.__dict__.get(n) for n in lease_names}
    need(all(type(f) is FunctionType and f.__globals__ is cg
             for f in list(io_methods.values()) + list(lease_methods.values())), 'actual C2 native methods')
    fnames = ('financial_plain', 'financial_evidence', 'verify_financial_candidate',
              'read_financial_opening', '_read_frame_pin', 'financial_decode')
    fns = {n: fg.get(n) for n in fnames}
    need(all(type(f) is FunctionType and f.__globals__ is fg for f in fns.values()), 'source-owned F4 functions')
    bind = bg.get('bind_funding')
    need(type(bind) is FunctionType and bind.__globals__ is bg, 'source-owned candidate binder')
    builder = bind(funding)
    stage = fg['CONTROL'] / '_manual-settlement-staging-v1'
    images = [(cg, dict(cg)), (fg, dict(fg)), (bg, dict(bg))]
    codes = [(f, f.__code__, namespace) for namespace, image in images for f in image.values()
             if type(f) is FunctionType and f.__globals__ is namespace]
    codes += [(f, f.__code__, cg) for f in list(io_methods.values()) + list(lease_methods.values())]
    io_image, lease_image = dict(IOType.__dict__), dict(LeaseType.__dict__)
    remember, checkpoint = cg['remember'], cg['checkpoint']
    need(all(type(f) is FunctionType and f.__globals__ is cg for f in (remember, checkpoint)), 'original error/checkpoint functions')
    need(fg['CONTROL'] == cg['ROOT'] / 'control/fresh-metered-round-v1', 'same canonical formal/financial domain')
    contexts = {}; issued = [False]

    def sources():
        need(all(f.__code__ is code and f.__globals__ is namespace for f, code, namespace in codes),
             'unchanged selected source function code')
        for namespace, image in images:
            need(set(namespace) == set(image) and all(namespace[n] is v for n, v in image.items()),
                 'unchanged selected module namespace')
        for cls, image in ((IOType, io_image), (LeaseType, lease_image)):
            now = type.__getattribute__(cls, '__dict__')
            need(set(now) == set(image) and all(now[n] is v for n, v in image.items()), 'unchanged actual kernel class')
        need(cg['IO'] is io and type(io) is IOType, 'same original IO instance')

    def fail(r, error, uncertain=False):
        primary = r['failure'].remember(error, uncertain)
        remember(error)
        if uncertain:
            cg['IO_UNKNOWN'][0] = True
        return primary

    def private_record(ctx):
        need(type(ctx) is Context and ctx in contexts, 'actual private settlement context')
        r = contexts[ctx]
        need(r['pid'] == os.getpid(), 'same actual settlement process')
        return r

    def record(ctx):
        r = private_record(ctx)
        sources()
        return r

    def slot_state():
        values = object.__getattribute__(io, '__dict__')
        need(type(values) is dict and all(type(k) is str for k in values) and set(values) == {'slots'},
             'exact original IO instance fields')
        slots = values['slots']
        need(type(slots) is list and len(slots) == 16, 'exact original slot vector')
        for row in slots:
            need(type(row) is list and len(row) == 3 and type(row[1]) is str and
                 row[1] in ('FREE', 'CLOSED', 'PENDING', 'OWNED', 'CLOSING') and
                 (row[2] is None or type(row[2]) is bool), 'exact original slot record')
            if row[1] == 'FREE':
                need(row[0] is None and row[2] is None, 'original unused slot')
            elif row[1] == 'PENDING':
                need(row[0] is None and type(row[2]) is bool, 'original pending acquisition')
            else:
                need(type(row[2]) is bool, 'known acquired slot kind')
                if row[2] is False:
                    need(type(row[0]) is int and row[0] >= 0, 'exact original descriptor slot')
                else:
                    # C.names closes its actual scandir iterator in finally and
                    # retains it in a CLOSED slot. Never dispatch a foreign
                    # .close hook or replay an uncertain directory acquisition.
                    need(row[1] == 'CLOSED', 'opaque directory handle must already be closed')
        return slots

    def lease_state(r):
        need(type(r['lease']) is LeaseType, 'exact original lease instance')
        values = object.__getattribute__(r['lease'], '__dict__')
        need(type(values) is dict and all(type(k) is str for k in values) and
             set(values) == {'fd', 'phase', 'birth', 'lock_info'}, 'exact original lease fields')
        need(values['fd'] is None or (type(values['fd']) is int and values['fd'] >= 0), 'exact original native descriptor')
        need(type(values['phase']) is str and values['phase'] in
             ('NEW', 'OPEN_PENDING', 'OPEN_RETURNED', 'EX_HELD', 'CLOSE_ENTERED', 'CLOSE_RETURNED', 'CLOSE_UNKNOWN'),
             'original lease phase')
        birth = values['birth']
        if birth is not None:
            need(type(birth) is dict and all(type(k) is str for k in birth) and
                 set(birth) == {'pid', 'ppid', 'pgid', 'sid', 'start_ticks', 'rss_bytes'} and
                 all(type(v) is int and v >= 0 for v in birth.values()), 'original native process observation')
        need(values['lock_info'] is None or type(values['lock_info']) is dict, 'original lock observation')
        return values

    def cleanup_kernel(r):
        # Funding/candidate integrity failure must not bypass original native
        # cleanup. Recheck the narrower ORIGINAL kernel and private lease state;
        # if that state itself is unsafe, preserve UNKNOWN rather than guess FD.
        need(set(cg) == set(images[0][1]) and
             all(cg[n] is value for n, value in images[0][1].items()), 'original cleanup kernel namespace')
        need(all(f.__code__ is code for f, code, namespace in codes if namespace is cg),
             'original cleanup kernel function code')
        for cls, image in ((IOType, io_image), (LeaseType, lease_image)):
            current = type.__getattribute__(cls, '__dict__')
            need(set(current) == set(image) and all(current[n] is v for n, v in image.items()),
                 'original cleanup kernel class')
        need(type(io) is IOType, 'original cleanup IO instance')
        slot_state()
        if r['lease_initialized']:
            state = lease_state(r)
            need(state['phase'] not in ('CLOSE_ENTERED', 'CLOSE_RETURNED', 'CLOSE_UNKNOWN'), 'one original lease cleanup')
            if r['fd'] is not None:
                need(state['fd'] is r['fd'], 'same acquired descriptor on cleanup')

    def verify(r):
        sources()
        need(not r['close_entered'] and type(r['lease']) is LeaseType and
             not cg['IO_UNKNOWN'][0] and r['failure'].first is None, 'known live native settlement owner')
        slot_state(); lease_state(r)
        observation = lease_methods['verify'](r['lease'])
        need(r['lease'].fd is r['fd'] and observation['parent']['start_ticks'] == r['birth']['start_ticks'] and
             observation['parent']['pid'] == r['pid'], 'same acquired native FD and process birth')
        return observation

    def iocall(r, name, *args):
        verify(r)
        return io_methods[name](io, *args)

    def directory(path):
        need(type(path) is type(fg['FIN_ROOT']) and path.is_absolute() and path.resolve(strict=True) == path,
             'canonical settlement directory')
        st = path.lstat()
        need(stat.S_ISDIR(st.st_mode) and st.st_uid == os.getuid() and stat.S_IMODE(st.st_mode) == 0o700,
             'private original directory')
        return cg['identity'](st)

    def sync(r, path):
        before = directory(path); slot = None; primary = None
        try:
            slot = iocall(r, 'acquire', path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
            need(cg['identity'](os.fstat(slot[0])) == before, 'same directory descriptor')
            os.fsync(slot[0])
            need(directory(path) == before, 'unchanged directory during sync')
        except BaseException as error:
            primary = fail(r, error, True)
        finally:
            if slot is not None and slot[1] == 'OWNED':
                try:
                    io_methods['close'](io, slot)
                except BaseException as error:
                    primary = fail(r, error, True)
        if primary is not None:
            raise primary

    def read(r, pin):
        verify(r)
        row, raw = fns['_read_frame_pin'](io, pin, os.getuid())
        verify(r)
        return raw

    def publish(r, path, raw, mode, replace=False):
        verify(r); directory(path.parent); directory(stage)
        need(iocall(r, 'names', stage, 2) == [], 'empty source-fixed publication stage')
        need(type(raw) is bytes and 0 < len(raw) <= fg['META_CAP'] and mode in (0o444, 0o600), 'bounded exact publication')
        temp = stage / ('manual-settlement-' + path.name)
        r['publication'] = dict(path=str(path), temporary=str(temp), phase='OPEN_PENDING')
        slot = None; primary = None
        try:
            slot = iocall(r, 'acquire', temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC)
            r['publication']['phase'] = 'WRITING'; offset = 0
            while offset < len(raw):
                checkpoint(); n = os.write(slot[0], raw[offset:offset + 65536])
                need(type(n) is int and 0 < n <= min(65536, len(raw) - offset), 'progressing complete write')
                offset += n
            os.fchmod(slot[0], mode); os.fsync(slot[0])
        except BaseException as error:
            primary = fail(r, error, True)
        finally:
            if slot is not None and slot[1] == 'OWNED':
                try:
                    io_methods['close'](io, slot)
                except BaseException as error:
                    primary = fail(r, error, True)
        if primary is not None:
            raise primary
        pin = bg['wire_pin'](temp, raw.decode('utf-8'), mode)
        need(read(r, pin) == raw, 'complete staged readback')
        sync(r, stage); verify(r); r['publication']['phase'] = 'COMMIT_PENDING'
        if replace:
            need(path == fg['FIN_HEAD'], 'only current financial HEAD may replace')
            os.replace(temp, path)
        else:
            os.link(temp, path, follow_symlinks=False)
            sync(r, path.parent)
            os.unlink(temp)  # Only this known-created, closed staged inode.
        sync(r, stage); sync(r, path.parent)
        need(read(r, bg['wire_pin'](path, raw.decode('utf-8'), mode)) == raw, 'published exact readback')
        need(iocall(r, 'names', stage, 2) == [], 'known empty publication stage')
        r['publication']['phase'] = 'COMMITTED'

    class Context:
        __slots__ = ()

        def settle(self, current_snapshot, own_id, terminal_manifest_pin, extra_wires):
            r = record(self); verify(r)
            need(not r['attempted'], 'once-only own import; failed/partial publication cannot retry')
            r['attempted'] = True
            try:
                fns['financial_plain'](current_snapshot)
                before = fns['financial_evidence'](current_snapshot)
                candidate = builder.build_settlement(current_snapshot, own_id, terminal_manifest_pin, extra_wires)
                # Do not read old HEAD as a complete snapshot after newer ENTRY
                # originals exist: verify the COMPLETE proposed census against the
                # actual old HEAD, all originals and original legacy reader instead.
                verify(r)
                after = fns['verify_financial_candidate'](io, candidate, os.getuid(), before['head_pin'])
                verify(r)
                for name, old in before['entries'].items():
                    new = after['entries'][name]
                    if name != own_id:
                        need(old == new, 'no other entry settlement, repricing or target close')
                r['candidate_pending'] = candidate
                r['failure'].publication_entered()
                # This exact source-owned stage lives outside the financial
                # census. Never use/clear the payload controller's artifact stage.
                directory(fg['CONTROL'])
                if not stage.exists():
                    os.mkdir(stage, 0o700)
                    sync(r, fg['CONTROL'])
                directory(stage)
                head = fns['financial_decode'](candidate['head_wire'].encode()); generation = head['generation']
                for prefix, mode in (('STATE-', 0o444), ('OPENING-', 0o444), ('HEAD-', 0o600)):
                    path = fg['FIN_ROOT'] / (prefix + '%06d.json' % generation)
                    publish(r, path, candidate['wires'][str(path)].encode('utf-8'), mode)
                publish(r, fg['FIN_HEAD'], candidate['head_wire'].encode('utf-8'), 0o600, True)
                verify(r)
                actual = fns['read_financial_opening'](io, candidate['opening_pin'], os.getuid())
                need(actual == candidate, 'whole financial publication and complete census readback')
                verify(r)
                r['failure'].verified()
                r['candidate_pending'] = None
                r['committed'] = actual
                return actual
            except BaseException as error:
                uncertain = r['failure'].phase == 'PUBLICATION_PENDING'
                raise fail(r, error, uncertain)

        def release(self):
            r = private_record(self)
            need(not r['close_entered'], 'one actual lease close')
            r['close_entered'] = True
            try:
                sources()
            except BaseException as error:
                fail(r, error, True)
            try:
                cleanup_kernel(r)
            except BaseException as error:
                raise fail(r, error, True)
            # All slots were known closed before this private factory acquired EX.
            for slot in slot_state():
                if slot[1] == 'OWNED':
                    try:
                        io_methods['close'](io, slot)
                    except BaseException as error:
                        fail(r, error, True)
                elif slot[1] not in ('FREE', 'CLOSED'):
                    r['failure'].unknown = True; cg['IO_UNKNOWN'][0] = True
            try:
                lease_methods['close'](r['lease'])
                r['closed_known'] = not r['failure'].unknown and not cg['IO_UNKNOWN'][0]
            except BaseException as error:
                fail(r, error, True)
            if r['failure'].first is not None:
                raise r['failure'].first

        def disposition(self):
            r = private_record(self); f = r['failure']
            return dict(phase=f.phase, reservation_retained=f.reservation_retained,
                        publication=r['publication'], import_readback_complete=r['committed'] is not None,
                        cleanup_known=r['closed_known'], unknown=f.unknown or cg['IO_UNKNOWN'][0],
                        first=None if f.first is None else type(f.first).__name__,
                        secondary=[type(e).__name__ for e in f.secondary], physical_boundary='OPEN_NOT_ZERO')

    def open_settlement():
        sources()
        need(not issued[0], 'one settlement factory invocation')
        issued[0] = True
        need(cg['FIRST'][0] is None and cg['IO_UNKNOWN'][0] is False and
             all(s[1] in ('FREE', 'CLOSED') for s in slot_state()), 'pristine source-owned kernel before fresh EX')
        ctx = Context()
        r = dict(pid=os.getpid(), lease=None, lease_initialized=False, lease_acquire_entered=False,
                 fd=None, birth=None, close_entered=False,
                 closed_known=False, attempted=False, failure=FailureState(), candidate_pending=None,
                 committed=None, publication=None)
        contexts[ctx] = r
        try:
            lease = object.__new__(LeaseType)
            r['lease'] = lease
            lease_methods['__init__'](lease)
            r['lease_initialized'] = True
            r['lease_acquire_entered'] = True
            lease_methods['acquire'](lease)
            r['fd'], r['birth'] = lease.fd, dict(lease.birth)
            verify(r)
        except BaseException as error:
            fail(r, error, True)
            r['close_entered'] = True
            if r['lease_initialized'] and r['lease_acquire_entered']:
                try:
                    cleanup_kernel(r)
                    lease_methods['close'](r['lease'])
                except BaseException as cleanup:
                    fail(r, cleanup, True)
            raise r['failure'].first
        return ctx

    return open_settlement
