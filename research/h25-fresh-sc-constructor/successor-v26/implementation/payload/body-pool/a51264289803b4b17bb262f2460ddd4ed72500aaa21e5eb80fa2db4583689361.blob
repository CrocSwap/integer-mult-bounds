"""Owned Linux child domains for one trusted, single-threaded parent process.

Source proposal only.  No target was imported or run during authoring.  The
external launcher must authenticate the OS, interpreter, system modules and
original subreaper installer before importing this module.  This is the original
closed child-domain premise, not a sandbox against hostile forking or a hostile
host.  Acquisition/unwind ambiguity quarantines the parent; it never authorizes
another launch or a completion.  The enclosing guard must observe parent exit.
"""
import os
import signal
import subprocess
import time
import epoch_schema_v5 as schema

_TYPE, _LEN = type, len
_OPEN, _READ, _CLOSE = os.open, os.read, os.close
_STAT = os.stat
_SCANDIR, _GETPID, _GETPGRP, _GETSID = os.scandir, os.getpid, os.getpgrp, os.getsid
_PIDFD_OPEN, _PIDFD_SIGNAL = os.pidfd_open, signal.pidfd_send_signal
_WAITPID, _CLOCK, _SLEEP = os.waitpid, time.monotonic, time.sleep
_POPEN, _POLL = subprocess.Popen, subprocess.Popen.poll
_PAGE_BYTES = os.sysconf('SC_PAGE_SIZE')
_DOMAINS = []
MAX_GENERATIONS = 128
MAX_PROC_ENTRIES = 131072
MAX_PROC_BYTES = 8192
CLEANUP_SECONDS = 2.0


def _state(capability):
    schema.need(_TYPE(capability) is object, 'exact owned domain capability required')
    for token, state in _DOMAINS:
        if token is capability:
            return state
    raise schema.EpochStop('unregistered owned domain')


def refresh_unknown_owner(owner):
    # These are exact V5 ErrorOwner state references captured by the original
    # parent before use. Read only the pinned private shape; no projection,
    # callback, native I/O or interpretation of historical release slot9.
    for native in owner['native_errors']:
        if native is None:
            continue
        io = native[7]
        if (io[0] or io[1] or io[2] or io[4] or io[6] or io[10] or io[11] or
                io[5] is not None or native[5][1] or io[7][4] == 1):
            owner['quarantine'][0] = True
            if io[5] is not None:
                owner['iterator_uncertain'][0] = True


def _fresh_acquisition(state):
    # This shares the original parent's preallocated unknown-resource owner.
    # Pending acquisition and delivered census failure are independent of a
    # later Python close return.  Neither flag is cleared by cleanup.
    owner = state['unknown_owner']
    refresh_unknown_owner(owner)
    schema.need(state['quarantine'] is False and state['acquisition_in_flight'] is False and
                state['io_uncertain'] is False and owner['quarantine'][0] is False and
                owner['pending'][0] is False and owner['iterator_uncertain'][0] is False,
                'uncertain ownership prohibits a fresh native acquisition')


def _opaque(state, error, slot):
    # Preallocated slots retain the actual delivered object, without formatting.
    # A secondary never replaces the first primary.  Slots are finite and an
    # overflow means quarantine, not a successful evidence projection.
    state['quarantine'] = True
    if state['primary'][0] is None:
        state['primary'][0] = error
    elif state['secondary'][slot] is None:
        state['secondary'][slot] = error
    else:
        state['overflow'][0] = error


def _proc(pid, state):
    schema.integer(pid, 1, (1 << 31) - 1)
    descriptor = None
    primary = None
    _fresh_acquisition(state)
    # The uncertain acquisition flag is set before the native entry.  If open
    # raises after an undisclosed descriptor acquisition, parent exit is needed.
    try:
        try:
            _STAT('/proc/' + str(pid) + '/stat', dir_fd=None, follow_symlinks=False)
        except (FileNotFoundError, ProcessLookupError):
            # Only the pinned metadata-only primitive establishes absence.
            # An exception from a later acquisition never proves no FD existed.
            return None
        state['acquisition_in_flight'] = True
        state['unknown_owner']['pending'][0] = True
        descriptor = _OPEN('/proc/' + str(pid) + '/stat',
            os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK)
        state['acquisition_in_flight'] = False
        state['unknown_owner']['pending'][0] = False
        raw = _READ(descriptor, MAX_PROC_BYTES + 1)
        schema.need(_TYPE(raw) is bytes and _LEN(raw) <= MAX_PROC_BYTES,
                    'bounded proc stat read differs')
        end = raw.rfind(b') ')
        schema.need(end >= 0, 'malformed proc stat')
        fields = raw[end + 2:].split()
        schema.need(_LEN(fields) >= 22 and raw[:raw.find(b' ')] == str(pid).encode('ascii'),
                    'proc stat identity or shape differs')
        row = (pid, int(fields[1]), int(fields[2]), int(fields[3]),
               int(fields[19]), fields[0].decode('ascii'), int(fields[21]) * _PAGE_BYTES)
        schema.need(row[4] > 0 and row[6] >= 0, 'proc generation or RSS differs')
        return row
    except BaseException as error:
        primary = error
        if state['unknown_owner']['primary'][0] is None:
            state['unknown_owner']['primary'][0] = error
        state['quarantine'] = True
        state['unknown_owner']['quarantine'][0] = True
        _opaque(state, error, 0)
        raise
    finally:
        if descriptor is not None:
            # Burn before entry; a failed native close is not retried.
            owned = descriptor
            descriptor = None
            try:
                _CLOSE(owned)
            except BaseException as close_error:
                if state['unknown_owner']['primary'][0] is None:
                    state['unknown_owner']['primary'][0] = close_error
                state['quarantine'] = True
                state['unknown_owner']['quarantine'][0] = True
                state['io_uncertain'] = True
                _opaque(state, close_error, 1)
                if primary is None:
                    raise


def _census(state):
    iterator = None
    primary = None
    rows = {}
    _fresh_acquisition(state)
    state['acquisition_in_flight'] = True
    state['unknown_owner']['pending'][0] = True
    try:
        iterator = _SCANDIR('/proc')
        state['acquisition_in_flight'] = False
        state['unknown_owner']['pending'][0] = False
        count = 0
        for entry in iterator:
            count += 1
            schema.need(count <= MAX_PROC_ENTRIES, 'proc census entry bound exceeded')
            name = entry.name
            if name.isdecimal():
                row = _proc(int(name), state)
                if row is not None:
                    rows[row[0]] = row
        return rows
    except BaseException as error:
        primary = error
        # All delivered iteration/body failures latch before optional helper
        # entry. A no-op/successful close cannot establish release afterward.
        if state['unknown_owner']['primary'][0] is None:
            state['unknown_owner']['primary'][0] = error
        state['quarantine'] = True
        state['io_uncertain'] = True
        state['unknown_owner']['quarantine'][0] = True
        state['unknown_owner']['iterator_uncertain'][0] = True
        _opaque(state, error, 2)
        raise
    finally:
        if iterator is not None:
            owned = iterator
            iterator = None
            try:
                owned.close()
            except BaseException as close_error:
                if state['unknown_owner']['primary'][0] is None:
                    state['unknown_owner']['primary'][0] = close_error
                state['quarantine'] = True
                state['unknown_owner']['quarantine'][0] = True
                state['unknown_owner']['iterator_uncertain'][0] = True
                state['io_uncertain'] = True
                _opaque(state, close_error, 3)
                if primary is None:
                    raise


def create_domain(unknown_owner):
    """Called only after the original same-process subreaper was installed."""
    schema.need(_LEN(_DOMAINS) < 4, 'two modes by two producers domain bound exceeded')
    schema.exact(unknown_owner, ('quarantine', 'pending', 'iterator_uncertain', 'primary', 'native_errors'))
    for key in ('quarantine', 'pending', 'iterator_uncertain', 'primary'):
        schema.need(_TYPE(unknown_owner[key]) is list and _LEN(unknown_owner[key]) == 1,
                    'original parent unknown-resource slot differs')
    schema.need(_TYPE(unknown_owner['native_errors']) is list and _LEN(unknown_owner['native_errors']) == 4,
                'exact two-mode V5 error-owner registry required')
    for native in unknown_owner['native_errors']:
        schema.need(native is None or (_TYPE(native) is list and _LEN(native) == 9 and
                    _TYPE(native[7]) is list and _LEN(native[7]) == 13),
                    'original captured V5 error-owner shape differs')
    refresh_unknown_owner(unknown_owner)
    schema.need(all(unknown_owner[key][0] is False for key in
                ('quarantine', 'pending', 'iterator_uncertain')) and unknown_owner['primary'][0] is None,
                'unknown-resource parent already requires teardown')
    token = object()
    state = {'rows': [None] * MAX_GENERATIONS, 'fds': [None] * MAX_GENERATIONS,
             'fd_attempted': [False] * MAX_GENERATIONS,
             'fd_closed': [False] * MAX_GENERATIONS, 'count': 0,
             'groups': set(), 'reaped': [], 'after_root': set(),
             'process': None, 'root': None, 'returncode': None,
             'parent_pid': _GETPID(), 'parent_group': _GETPGRP(), 'parent_session': _GETSID(0),
             'phase': 'CONSTRUCTING', 'quarantine': False,
             'acquisition_in_flight': False, 'io_uncertain': False, 'primary': [None],
             'unknown_owner': unknown_owner,
             'secondary': [None] * 16, 'overflow': [None],
             'final_rows': None, 'closure_confirmed': False}
    _DOMAINS.append((token, state))
    try:
        rows = _census(state)
        schema.need(not any(row[1] == state['parent_pid'] for row in rows.values()),
                    'parent has preexisting child processes')
        state['phase'] = 'RESERVED'
        return token
    except BaseException as error:
        if unknown_owner['primary'][0] is None:
            unknown_owner['primary'][0] = error
        unknown_owner['quarantine'][0] = True
        state['quarantine'] = True
        _opaque(state, error, 4)
        state['phase'] = 'STOP'
        raise


def _add(state, row):
    _fresh_acquisition(state)
    key = row[0], row[4]
    schema.need(row[0] != state['parent_pid'], 'parent cannot enter own child domain')
    for index in range(state['count']):
        prior = state['rows'][index]
        if prior is not None and (prior[0], prior[4]) == key:
            if row[2] != state['parent_group']:
                state['groups'].add((row[2], row[3]))
            return True
    index = state['count']
    schema.need(index < MAX_GENERATIONS, 'owned process generation bound exceeded')
    # Reserve the slot before native acquisition.  No role/generation slot is
    # recycled after a failed or disappeared acquisition.
    state['count'] = index + 1
    state['rows'][index] = row
    state['acquisition_in_flight'] = True
    state['unknown_owner']['pending'][0] = True
    try:
        state['fds'][index] = _PIDFD_OPEN(row[0], 0)
        state['acquisition_in_flight'] = False
        state['unknown_owner']['pending'][0] = False
        current = _proc(row[0], state)
        if current is None or (current[0], current[4]) != key:
            return False  # The actual FD stays owned for one terminal close.
        if current[2] != state['parent_group']:
            state['groups'].add((current[2], current[3]))
        return True
    except BaseException as error:
        if state['unknown_owner']['primary'][0] is None:
            state['unknown_owner']['primary'][0] = error
        state['quarantine'] = True
        state['unknown_owner']['quarantine'][0] = True
        _opaque(state, error, 5)
        raise


def observe(capability):
    state = _state(capability)
    all_rows = _census(state)
    known = set()
    for index in range(state['count']):
        prior = state['rows'][index]
        current = None if prior is None else all_rows.get(prior[0])
        if current is not None and current[4] == prior[4]:
            known.add(current[0])
            _add(state, current)
    for unused in range(MAX_GENERATIONS + 1):
        changed = False
        for pid, row in all_rows.items():
            if pid not in known and (row[1] == state['parent_pid'] or row[1] in known):
                if _add(state, row):
                    known.add(pid)
                    changed = True
        if not changed:
            break
    else:
        raise schema.EpochStop('child-domain closure iteration bound exceeded')
    return all_rows, tuple(all_rows[pid] for pid in sorted(known))


def adopt_popen(capability, process):
    state = _state(capability)
    schema.need(state['phase'] == 'RESERVED' and state['process'] is None and
                _TYPE(process) is _POPEN, 'Popen ownership or one-attempt state differs')
    state['process'] = process  # Exact original return, never a supplied proxy.
    row = _proc(process.pid, state)
    schema.need(row is not None and row[1] == state['parent_pid'] and
                row[2] == row[3] == process.pid,
                'new child PID/session/generation missing before first poll')
    state['root'] = row
    schema.need(_add(state, row) is True, 'original child pidfd generation not owned')
    state['phase'] = 'RUNNING'
    return row


def poll_owned(capability):
    state = _state(capability)
    schema.need(state['phase'] == 'RUNNING' and _TYPE(state['process']) is _POPEN,
                'original running Popen required')
    result = _POLL(state['process'])
    if result is not None:
        schema.integer(result, -128, 255)
        state['returncode'] = result
    return result


def _kill(state):
    for index in range(state['count']):
        fd, prior = state['fds'][index], state['rows'][index]
        if fd is None or state['fd_attempted'][index]:
            continue
        current = _proc(prior[0], state)
        if current is not None and current[4] == prior[4] and current[5] != 'Z':
            try:
                _PIDFD_SIGNAL(fd, signal.SIGKILL, None, 0)
            except ProcessLookupError:
                pass


def finish_domain(capability):
    """Always attempted, including Popen exceptions; no caller closure claims."""
    state = _state(capability)
    schema.need(state['phase'] in ('RESERVED', 'RUNNING'), 'domain cleanup replay')
    state['phase'] = 'CLEANUP_CONSUMED'
    started = _CLOCK()
    primary = None
    try:
        _fresh_acquisition(state)
        while True:
            all_rows, current = observe(capability)
            process = state['process']
            if process is not None and process.returncode is not None:
                for row in current:
                    if row[0] != process.pid:
                        state['after_root'].add((row[0], row[4]))
            _kill(state)
            if process is not None:
                result = _POLL(process)
                if result is not None:
                    state['returncode'] = result
            for index in range(state['count']):
                prior = state['rows'][index]
                row = _proc(prior[0], state)
                if (row is None or row[4] != prior[4] or row[1] != state['parent_pid'] or
                        (process is not None and row[0] == process.pid)):
                    continue
                try:
                    pid, status = _WAITPID(row[0], os.WNOHANG)
                except ChildProcessError:
                    continue
                if pid:
                    state['reaped'].append((pid, prior[4], status))
            all_rows, current = observe(capability)
            remaining = tuple(row for row in all_rows.values()
                if row[1] == state['parent_pid'] or (row[2], row[3]) in state['groups'] or
                any(prior is not None and (row[0], row[4]) == (prior[0], prior[4])
                    for prior in state['rows'][:state['count']]))
            state['final_rows'] = remaining
            if not current and not remaining:
                state['closure_confirmed'] = True
                break
            if _CLOCK() - started >= CLEANUP_SECONDS:
                break
            _SLEEP(0.01)
    except BaseException as error:
        primary = error
        if state['unknown_owner']['primary'][0] is None:
            state['unknown_owner']['primary'][0] = error
        state['quarantine'] = True
        state['unknown_owner']['quarantine'][0] = True
        _opaque(state, error, 6)
        raise
    finally:
        # Every known FD gets one attempt even if a prior close failed.  Native
        # return/boxing, Python call-entry and final unwind still have no total
        # recovery theorem; any such failure forbids minting and parent reuse.
        first_close = None
        for index in range(state['count']):
            descriptor = state['fds'][index]
            if descriptor is None or state['fd_attempted'][index]:
                continue
            state['fd_attempted'][index] = True
            try:
                _CLOSE(descriptor)
                state['fd_closed'][index] = True
            except BaseException as error:
                if state['unknown_owner']['primary'][0] is None:
                    state['unknown_owner']['primary'][0] = error
                state['quarantine'] = True
                state['unknown_owner']['quarantine'][0] = True
                state['io_uncertain'] = True
                _opaque(state, error, 7)
                if first_close is None:
                    first_close = error
        state['phase'] = 'CLOSED' if primary is None and first_close is None else 'STOP'
        if primary is None and first_close is not None:
            raise first_close


def terminal_facts(capability):
    state = _state(capability)
    _fresh_acquisition(state)
    schema.need(state['phase'] == 'CLOSED' and state['quarantine'] is False and
                state['acquisition_in_flight'] is False and state['io_uncertain'] is False and state['root'] is not None and
                state['returncode'] == 0 and state['closure_confirmed'] is True and
                state['final_rows'] == () and not state['after_root'] and not state['reaped'] and
                all(fd is None or (state['fd_attempted'][index] and state['fd_closed'][index])
                    for index, fd in enumerate(state['fds'])),
                'owned terminal domain is incomplete, failed, orphaned or quarantined')
    # Fresh census after FD cleanup.  This is independent of receipt booleans.
    rows = _census(state)
    schema.need(not any(row[1] == state['parent_pid'] or
                        (row[2], row[3]) in state['groups'] for row in rows.values()),
                'postcleanup owned child/group still present')
    return {'root': list(state['root']), 'returncode': state['returncode'],
            'owned_generations': [list(row) for row in state['rows'][:state['count']]],
            'groups': [list(pair) for pair in sorted(state['groups'])],
            'remaining': [], 'adopted_reaps': [], 'observed_after_root_exit': [],
            'pidfd_close_attempted': list(state['fd_attempted'][:state['count']]),
            'pidfd_close_confirmed': list(state['fd_closed'][:state['count']]),
            'source': 'original in-process Popen and owned generation registry',
            'hostile_fork_or_privileged_host_resistance_claimed': False}


def stop_slots(capability):
    state = _state(capability)
    return state['primary'], state['secondary'], state['overflow'], {
        'phase': state['phase'], 'quarantine': state['quarantine'],
        'acquisition_in_flight': state['acquisition_in_flight'],
        'io_uncertain': state['io_uncertain'],
        'shared_pending': state['unknown_owner']['pending'][0],
        'shared_iterator_uncertain': state['unknown_owner']['iterator_uncertain'][0],
        'shared_quarantine': state['unknown_owner']['quarantine'][0],
        'closure_confirmed': state['closure_confirmed'],
        'pidfd_close_attempted': list(state['fd_attempted'][:state['count']]),
        'pidfd_close_confirmed': list(state['fd_closed'][:state['count']])}


def prefix_exit1_terminal_facts(capability):
    """Return cleanup/exit DATA for an actual owned prefix child exiting 1.

    Separate from production terminal_facts. Never creates an epoch ticket,
    ParentCompletion, source admission, or control-family acceptance.
    """
    state = _state(capability)
    owner = state['unknown_owner']
    try:
        schema.need(_GETPID() == state['parent_pid'],
                    'prefix terminal observer is not the owning parent')
        _fresh_acquisition(state)
        schema.need(owner['primary'][0] is None and
                    state['primary'][0] is None,
                    'earlier error forbids prefix terminal observation')
        schema.need(
            state['phase'] == 'CLOSED' and
            state['quarantine'] is False and
            state['acquisition_in_flight'] is False and
            state['io_uncertain'] is False and
            state['root'] is not None and
            _TYPE(state['returncode']) is int and
            state['returncode'] == 1 and
            state['closure_confirmed'] is True and
            state['final_rows'] == () and
            not state['after_root'] and
            not state['reaped'] and
            all(fd is None or
                (state['fd_attempted'][index] and state['fd_closed'][index])
                for index, fd in enumerate(state['fds'])),
            'owned exit1 prefix domain is incomplete or quarantined',
        )
        rows = _census(state)
        schema.need(
            not any(row[1] == state['parent_pid'] or
                    (row[2], row[3]) in state['groups']
                    for row in rows.values()),
            'postcleanup owned prefix child/group still present',
        )
        return {
            'schema': 'h25-prefix-exit1-terminal-facts-v1',
            'root': list(state['root']),
            'returncode': state['returncode'],
            'owned_generations': [
                list(row) for row in state['rows'][:state['count']]
            ],
            'groups': [list(pair) for pair in sorted(state['groups'])],
            'remaining': [],
            'adopted_reaps': [],
            'observed_after_root_exit': [],
            'pidfd_close_attempted': list(
                state['fd_attempted'][:state['count']]
            ),
            'pidfd_close_confirmed': list(
                state['fd_closed'][:state['count']]
            ),
            'source': 'original in-process Popen and owned generation registry',
            'production_completion': False,
            'refusal_semantics_authenticated_by_this_function': False,
            'hostile_fork_or_privileged_host_resistance_claimed': False,
        }
    except BaseException as error:
        if owner['primary'][0] is None:
            prior = state['primary'][0]
            owner['primary'][0] = error if prior is None else prior
        primary = owner['primary'][0]
        if state['primary'][0] is None:
            state['primary'][0] = primary
        if error is not primary:
            if state['secondary'][8] is None:
                state['secondary'][8] = error
            elif state['overflow'][0] is None:
                state['overflow'][0] = error
        state['quarantine'] = True
        owner['quarantine'][0] = True
        # Do not change phase: an invalid early call must not prevent
        # finish_domain from reaching its known-FD cleanup.
        if primary is error:
            raise
        raise primary
