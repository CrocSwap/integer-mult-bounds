"""Independent bounded controls; new owned fixtures and this observer only.

No subprocess, original source import, native replacement, audit hook or reset.
Fixtures are retained on success and failure. These are partial-component tests,
not original Root, compiler, custody, currentness or C05 qualification.
"""
import errno
import json
import os
import stat
import sys
import tempfile

from c05_namespace_observer_v1 import NamespaceObservation, ObservationStop


OWNERS = []
FIXTURES = []
COUNTS = {'observations': 0, 'fixture_scenarios': 0, 'input_refusals': 0,
          'closed_fd_probes': 0, 'native_error_controls': 0,
          'temporal_counterexamples': 0, 'checks': 0}


def need(value, message):
    COUNTS['checks'] += 1
    if not value:
        raise RuntimeError(message)


def write_fixture(path, raw, mode):
    state = {'path': path, 'pending': True, 'fd': None,
             'primary': None, 'close_error': None}
    FIXTURES.append(state)
    try:
        state['fd'] = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                              os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        state['pending'] = False
        offset = 0
        while offset < len(raw):
            size = os.write(state['fd'], raw[offset:])
            need(size > 0, 'fixture write made no progress')
            offset += size
        os.fchmod(state['fd'], mode)
    except BaseException as error:
        state['primary'] = error
        raise
    finally:
        descriptor = state['fd']
        state['fd'] = None
        if descriptor is not None:
            try:
                os.close(descriptor)
            except BaseException as error:
                state['close_error'] = error
                if state['primary'] is None:
                    state['primary'] = error
                    raise


def metadata(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_uid, info.st_gid, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def closed(descriptor):
    try:
        os.fstat(descriptor)
    except OSError as error:
        need(error.errno == errno.EBADF, 'unexpected closed-FD probe error')
        COUNTS['closed_fd_probes'] += 1
    else:
        raise RuntimeError('observer left a delivered descriptor open')


def check_closure(owner):
    delivered = [fd for fd in owner.fd_numbers if fd is not None]
    need(all(fd is None for fd in owner._fds), 'ownership slot survived return')
    need(len(delivered) == len(set(delivered)), 'simultaneously held FDs alias')
    for index, descriptor in enumerate(owner.fd_numbers):
        if descriptor is not None:
            need(owner.close_attempted[index] and owner.close_confirmed[index],
                 'delivered descriptor lacks successful close return')
            closed(descriptor)
        else:
            need(not owner.close_attempted[index], 'unacquired slot was closed')


def capture(path, expected, terminal_name=None):
    owner = NamespaceObservation(path)
    OWNERS.append(owner)
    need(owner.observe() is None, 'observe must return no fabricated certificate')
    COUNTS['observations'] += 1
    record = owner.project()
    need(record['outcome'] == expected, 'wrong fixture disposition: ' + path)
    need(record['phase'] == 'DONE' and not record['pending_open'] and
         not record['quarantined'] and owner.primary is None,
         'successful owner has unresolved operation state')
    for flag in ('regular_content_read', 'directory_members_enumerated',
                 'absolute_namespace_snapshot', 'interval_stability_established',
                 'durable_capture_established', 'full_c05', 'runtime_qualified'):
        need(record[flag] is False, 'unearned acceptance flag: ' + flag)
    check_closure(owner)
    terminal = record['terminal_index']
    if terminal_name is not None:
        need(record['rows'][terminal]['name'] == terminal_name,
             'wrong stopping component')
        for row in record['rows'][terminal + 1:]:
            need(row['lookup'] is row['pinned'] is row['late'] is None,
                 'unresolved suffix gained observations')
    try:
        owner.observe()
    except ObservationStop:
        pass
    else:
        raise RuntimeError('completed owner acquired again')
    COUNTS['fixture_scenarios'] += 1
    return owner, record


def main():
    root = tempfile.mkdtemp(prefix='c05-independent-', dir='/tmp')
    FIXTURES.append({'retained_root': root})
    print('RETAINED_C05_FIXTURE ' + root, flush=True)
    write_fixture(root + '/alpha.h', b'\x00independent original fixture\xff\n', 0o640)
    write_fixture(root + '/empty.h', b'', 0o444)
    write_fixture(root + '/unread.h', b'classification is not content access', 0)
    os.mkdir(root + '/directory')
    os.mkdir(root + '/tree.gch')
    write_fixture(root + '/present.gch', b'not a claimed usable PCH', 0o600)
    os.symlink('alpha.h', root + '/link')
    os.symlink('no-target', root + '/dangling')
    os.symlink('directory', root + '/directory-link')
    os.link(root + '/alpha.h', root + '/hard.h')
    os.mkfifo(root + '/fifo')
    # Independently capture the fixture oracle before invoking the candidate.
    expected = {name: metadata(os.lstat(root + '/' + name))
                for name in ('alpha.h', 'empty.h', 'unread.h', 'hard.h',
                             'link', 'dangling', 'directory-link', 'fifo')}
    need(expected['alpha.h'][:2] == expected['hard.h'][:2], 'fixture hardlink differs')
    need(expected['alpha.h'][:2] != expected['empty.h'][:2], 'independent objects alias')
    scenarios = (
        ('alpha.h', 'REGULAR_CONTENT_UNREAD', None),
        ('empty.h', 'REGULAR_CONTENT_UNREAD', None),
        ('unread.h', 'REGULAR_CONTENT_UNREAD', None),
        ('hard.h', 'REGULAR_CONTENT_UNREAD', None),
        ('directory', 'DIRECTORY_CONTENTS_UNENUMERATED', None),
        ('tree.gch', 'DIRECTORY_CONTENTS_UNENUMERATED', None),
        ('present.gch', 'REGULAR_CONTENT_UNREAD', None),
        ('link', 'SYMLINK_UNRESOLVED', None),
        ('dangling', 'SYMLINK_UNRESOLVED', None),
        ('directory-link/not-read', 'SYMLINK_UNRESOLVED', 'directory-link'),
        ('alpha.h/not-read', 'NON_DIRECTORY_PREFIX', 'alpha.h'),
        ('fifo', 'SPECIAL_FILE_UNSUPPORTED', None),
        ('absent', 'ABSENT_AT_PINNED_PARENT', 'absent'),
        ('missing-prefix/not-read', 'ABSENT_AT_PINNED_PARENT', 'missing-prefix'),
    )
    for name, outcome, terminal in scenarios:
        _, record = capture(root + '/' + name, outcome, terminal)
        if name in expected:
            row = record['rows'][record['terminal_index']]
            need(row['pinned'] == expected[name] and row['lookup'] == expected[name],
                 'candidate differs from independent pre-observation fixture metadata')
    # Exact component-bound positive, independent of the candidate constants.
    deep = root
    for _ in range(61):
        deep += '/d'
        os.mkdir(deep)
    target = deep + '/end'
    write_fixture(target, b'x', 0o600)
    need(len(target.split('/')[1:]) == 64, 'fixture does not hit 64-component boundary')
    owner, _ = capture(target, 'REGULAR_CONTENT_UNREAD')
    need(sum(fd is not None for fd in owner.fd_numbers) == 65,
         '64-component positive did not retain 65 descriptors')
    # Genuine outcome ABA: endpoints agree but an intervening PCH object exists.
    _, before = capture(root + '/later.gch', 'ABSENT_AT_PINNED_PARENT', 'later.gch')
    write_fixture(root + '/later.gch', b'actual intervening presence', 0o600)
    _, during = capture(root + '/later.gch', 'REGULAR_CONTENT_UNREAD')
    os.unlink(root + '/later.gch')
    _, after = capture(root + '/later.gch', 'ABSENT_AT_PINNED_PARENT', 'later.gch')
    need(before['outcome'] == after['outcome'] != during['outcome'], 'ABA discriminator failed')
    COUNTS['temporal_counterexamples'] += 1
    # Independent real-OS counterexample: a held directory is not its old spelling.
    os.mkdir(root + '/ancestor')
    write_fixture(root + '/ancestor/old.h', b'old held directory', 0o600)
    fd = os.open(root + '/ancestor', os.O_PATH | os.O_DIRECTORY |
                 os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        held = os.stat('old.h', dir_fd=fd, follow_symlinks=False)
        os.rename(root + '/ancestor', root + '/parked')
        os.mkdir(root + '/ancestor')
        through_fd = os.stat('old.h', dir_fd=fd, follow_symlinks=False)
        need(metadata(held) == metadata(through_fd), 'held directory object changed')
        try:
            os.lstat(root + '/ancestor/old.h')
        except FileNotFoundError as error:
            need(error.errno == errno.ENOENT, 'wrong absolute lookup error')
        else:
            raise RuntimeError('old absolute spelling still names held child')
    finally:
        os.close(fd)
    closed(fd)
    COUNTS['temporal_counterexamples'] += 1
    for path in ('relative', '/', '/a//b', '/a/./b', '/a/../b', '/a/',
                 '/a\x00b', '/\N{GREEK SMALL LETTER PI}', '/a\nb',
                 '/' + 'd/' * 64 + 'end', '/' + 'a' * 4096,
                 b'/bytes', True, None):
        try:
            NamespaceObservation(path)
        except ObservationStop:
            COUNTS['input_refusals'] += 1
        else:
            raise RuntimeError('malformed/out-of-local-domain input accepted')
    # LAST: real native failure must poison later acquisition in this interpreter.
    failing = NamespaceObservation(root + '/' + 'n' * 3000)
    OWNERS.append(failing)
    try:
        failing.observe()
    except OSError as primary:
        need(primary.errno == errno.ENAMETOOLONG, 'unexpected actual error route')
        need(failing.primary is primary and failing.quarantined and
             failing.phase == 'FAILED' and failing.outcome is None,
             'actual error was reclassified or lost')
        check_closure(failing)
        later = NamespaceObservation(root + '/alpha.h')
        OWNERS.append(later)
        for action in (failing.project, later.observe, owner.project):
            try:
                action()
            except BaseException as retained:
                need(retained is primary, 'quarantine lost original exception identity')
            else:
                raise RuntimeError('post-failure operation escaped quarantine')
        need(all(fd is None for fd in later.fd_numbers), 'post-failure owner acquired')
        COUNTS['native_error_controls'] += 1
    else:
        raise RuntimeError('owned-temp native error control did not fail')
    summary = {'schema': 'h25-c05-independent-observer-controls-v1',
               'python_profile': 'optimized' if sys.flags.optimize else 'normal',
               'counts': COUNTS, 'retained_fixture': root,
               'full_c05': False, 'full_v03': False, 'runtime_qualified': False,
               'adverse_close_delivery_executed': False,
               'costs': 'OPEN_NOT_ZERO'}
    print('PASS_C05_INDEPENDENT_NAMESPACE ' + json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
