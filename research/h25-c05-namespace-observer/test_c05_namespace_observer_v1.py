"""Future Codex fixture controls only; not executed in the consultation.

Use only this new module and newly owned /tmp fixtures. No subprocesses,
original imports, device creation, audit hooks or replaced native primitives.
"""
import os
import tempfile
import unittest

from c05_namespace_observer_v1 import NamespaceObservation, ObservationStop


FIXTURE_EVIDENCE = []


def make_file(path, raw):
    # Retain failed fixture construction; never run cleanup after uncertainty.
    state = [True, None, None, None]  # pending, FD, primary, close error
    FIXTURE_EVIDENCE.append((path, state))
    try:
        state[1] = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                           os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        state[0] = False
        offset = calls = 0
        while offset < len(raw):
            if calls == 8:
                raise RuntimeError('fixture write call bound')
            count = os.write(state[1], raw[offset:])
            if count <= 0:
                raise RuntimeError('fixture write made no progress')
            offset += count
            calls += 1
    except BaseException as error:
        state[2] = error
        raise
    finally:
        descriptor = state[1]
        state[1] = None
        if descriptor is not None:
            try:
                os.close(descriptor)
            except BaseException as error:
                state[3] = error
                if state[2] is None:
                    state[2] = error
                    raise


class NamespaceFixtures(unittest.TestCase):
    def test_owned_fixtures(self):
        root = tempfile.mkdtemp(prefix='c05-ns-', dir='/tmp')
        FIXTURE_EVIDENCE.append(('root', root))
        # Retain this bounded fixture on success and failure; no finalizer.
        make_file(root + '/header.h', b'/* independent fixture */\n')
        make_file(root + '/empty.h', b'')
        os.mkdir(root + '/directory')
        os.mkdir(root + '/pch.h.gch')
        make_file(root + '/present.h.gch', b'present, not a claimed valid PCH')
        os.symlink('header.h', root + '/link.h')
        os.symlink('missing-target', root + '/dangling.h.gch')
        os.symlink('directory', root + '/directory-link')
        os.link(root + '/header.h', root + '/hardlink.h')
        os.mkfifo(root + '/fifo.h')

        # Expected identities come from fixture input observations, not capture().
        fixed = {}
        for name in ('header.h', 'hardlink.h', 'empty.h'):
            info = os.stat(root + '/' + name, follow_symlinks=False)
            fixed[name] = (info.st_dev, info.st_ino, info.st_mode, info.st_size)
        self.assertEqual(fixed['header.h'], fixed['hardlink.h'])
        self.assertNotEqual(fixed['header.h'][:2], fixed['empty.h'][:2])
        FIXTURE_EVIDENCE.append(('fixed', fixed))

        def capture(relative):
            owner = NamespaceObservation(root + '/' + relative)
            FIXTURE_EVIDENCE.append(('owner', owner))
            owner.observe()
            record = owner.project()
            self.assertEqual(record['phase'], 'DONE')
            self.assertFalse(record['pending_open'])
            self.assertFalse(record['quarantined'])
            self.assertFalse(record['regular_content_read'])
            self.assertFalse(record['durable_capture_established'])
            self.assertFalse(record['full_c05'])
            self.assertFalse(record['runtime_qualified'])
            for row in record['rows']:
                if row['pinned'] is not None:
                    self.assertTrue(row['close_attempted'])
                    self.assertTrue(row['close_confirmed'])
            return owner, record

        cases = (
            ('header.h', 'REGULAR_CONTENT_UNREAD'),
            ('empty.h', 'REGULAR_CONTENT_UNREAD'),
            ('absent.h', 'ABSENT_AT_PINNED_PARENT'),
            ('missing-directory/child.h', 'ABSENT_AT_PINNED_PARENT'),
            ('header.h/child.h', 'NON_DIRECTORY_PREFIX'),
            ('directory', 'DIRECTORY_CONTENTS_UNENUMERATED'),
            ('pch.h.gch', 'DIRECTORY_CONTENTS_UNENUMERATED'),
            ('present.h.gch', 'REGULAR_CONTENT_UNREAD'),
            ('link.h', 'SYMLINK_UNRESOLVED'),
            ('dangling.h.gch', 'SYMLINK_UNRESOLVED'),
            ('directory-link/child.h', 'SYMLINK_UNRESOLVED'),
            ('fifo.h', 'SPECIAL_FILE_UNSUPPORTED'),
        )
        for relative, expected in cases:
            owner, record = capture(relative)
            self.assertEqual(record['outcome'], expected)
            if relative.endswith('/child.h'):
                terminal = record['terminal_index']
                self.assertEqual(record['rows'][terminal]['name'],
                                 relative.split('/')[0])
                self.assertTrue(all(row['lookup'] is None and row['pinned'] is None
                                    for row in record['rows'][terminal + 1:]))
            with self.assertRaises(ObservationStop):
                owner.observe()

        for name, expected in fixed.items():
            _, record = capture(name)
            info = record['rows'][record['terminal_index']]['pinned']
            self.assertEqual((info[0], info[1], info[2], info[6]), expected)

        _, first = capture('header.h')
        _, alias = capture('hardlink.h')
        left = first['rows'][first['terminal_index']]['pinned']
        right = alias['rows'][alias['terminal_index']]['pinned']
        self.assertEqual(left[:2], right[:2])
        self.assertNotEqual(first['requested_path'], alias['requested_path'])

        _, before = capture('later.h.gch')
        make_file(root + '/later.h.gch', b'new presence after earlier observation')
        _, during = capture('later.h.gch')
        os.unlink(root + '/later.h.gch')
        _, after = capture('later.h.gch')
        self.assertEqual(before['outcome'], 'ABSENT_AT_PINNED_PARENT')
        self.assertEqual(during['outcome'], 'REGULAR_CONTENT_UNREAD')
        self.assertEqual(after['outcome'], 'ABSENT_AT_PINNED_PARENT')
        # Outcome endpoints agree; complete metadata equality is NOT claimed.
        self.assertFalse(after['interval_stability_established'])

    def test_pure_input_refusals(self):
        for path in ('relative', '/a//b', '/a/./b', '/a/../b', '/a/',
                     '/a\x00b', '/\N{GREEK SMALL LETTER PI}',
                     '/' + 'a/' * 64 + 'a', '/' + 'a' * 4096,
                     b'/bytes', True, None):
            with self.subTest(path=path):
                with self.assertRaises(ObservationStop):
                    NamespaceObservation(path)


if __name__ == '__main__':
    unittest.main(failfast=True)