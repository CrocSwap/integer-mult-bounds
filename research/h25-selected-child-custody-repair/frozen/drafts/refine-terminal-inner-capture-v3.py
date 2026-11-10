# Source authoring only. This script parses text; it does not load target source.
from pathlib import Path
import ast, hashlib
r=Path('/workspace/scratch/35c1441288db/h25-selected-child-construction-20261108T203610Z')
p=r/'implementation/supervisor_family_v3.py'
s=p.read_text()
(r/'drafts/supervisor_family_v3-intermediate-v2.py.txt').write_text(s)
s=s.replace("        self.cleanup_errors = [None] * 6", "        self.inner_capture = [dict(name=name, writer=None, reader=None, read_error=None,\n                                   acquire_error=None, close_entry_error=None, observation=None,\n                                   initial=None, path=None, attempted=False, absence_observed=False,\n                                   acquisition_boundary=None)\n                              for name in ('stdout.txt', 'stderr.txt')]\n        self.all_capture = self.capture + self.inner_capture\n        self.round_root = self.label = None\n        self.inner_release_prepared = False\n        self.cleanup_errors = [None] * 8")
s=s.replace("        self.capture = [dict(name=name, writer=None, reader=None, read_error=None,\n                             observation=None, initial=None)", "        self.capture = [dict(name=name, writer=None, reader=None, read_error=None,\n                             close_entry_error=None, observation=None, initial=None,\n                             acquisition_boundary='BEFORE_ROOT_BIRTH')")
# Parent-owned gate binding makes the target log paths concrete and source-owned.
s=s.replace("        evidence.mkdir()\n        domain.install(root)", "        evidence.mkdir()\n        domain.round_root, domain.label = root, case['label']\n        for item in domain.inner_capture:\n            item['path'] = root / 'runtime/runs' / case['label'] / item['name']\n        domain.install(root)")
s=s.replace("            guard['checkpoint'] = 'LIVE_GENERATION_SOURCE_CONTEXT_VALIDATED'", "            # The actual pinned runner created its two inner files before\n            # launching this waiting child. Hold their read descriptors before\n            # authenticating release of the selected component body.\n            domain.prepare_inner_capture(guard, captured)\n            guard['checkpoint'] = 'LIVE_GENERATION_SOURCE_CONTEXT_VALIDATED'")
start=s.index('    def capture_after_retirement(self):')
end=s.index('    def close_capture_writers(self):',start)
replacement='''    def prepare_inner_capture(self, guard, captured):
        self._actual()
        need(guard is self.guard and guard['phase'] == 'WAITING_REQUEST' and
             generation(captured) == self.root and self.birth == 'POPEN_RETURNED' and
             not self.inner_release_prepared and self.round_root is not None,
             'actual source-authenticated original runner before target release')
        for item in self.inner_capture:
            need(not item['attempted'] and item['reader'] is None and
                 item['path'] == self.round_root / 'runtime/runs' / self.label / item['name'],
                 'one actual original label/folder capture acquisition')
            item['attempted'] = True
            item['reader'] = self.open_fd(item['path'], os.O_RDONLY | os.O_NONBLOCK |
                                          os.O_NOFOLLOW | os.O_CLOEXEC)
            info = os.fstat(item['reader']['fd'])
            need(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and
                 info.st_nlink == 1 and not info.st_mode & 0o022 and
                 identity(info) == identity(item['path'].lstat()),
                 'actual exclusive original runner inner capture inode')
            item['initial'] = (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_nlink)
            item['acquisition_boundary'] = 'AUTHENTICATED_BEFORE_TARGET_ACK'
        self.inner_release_prepared = True

    def acquire_retired_inner(self, item):
        # Only a pre-ACK failure can reach this fallback. A working error alone
        # does not prohibit a safe read acquisition after proved retirement.
        self._actual()
        need(self.empty_observed and self.retired and not self.unknown and
             item in self.inner_capture and item['reader'] is None and
             not item['attempted'] and self.round_root is not None and
             item['path'] == self.round_root / 'runtime/runs' / self.label / item['name'],
             'known retirement and exact original label before fallback read')
        try:
            before = item['path'].lstat()
        except FileNotFoundError:
            item['absence_observed'] = True
            item['acquisition_boundary'] = 'NOT_CREATED_BEFORE_KNOWN_RETIREMENT'
            return
        need(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid() and
             before.st_nlink == 1 and not before.st_mode & 0o022,
             'original source-owned retained inner capture')
        item['attempted'] = True
        item['reader'] = self.open_fd(item['path'], os.O_RDONLY | os.O_NONBLOCK |
                                      os.O_NOFOLLOW | os.O_CLOEXEC)
        opened = os.fstat(item['reader']['fd'])
        need(identity(before) == identity(opened) == identity(item['path'].lstat()),
             'complete actual original inner-capture open join')
        item['initial'] = (opened.st_dev, opened.st_ino, opened.st_mode, opened.st_uid, opened.st_nlink)
        item['acquisition_boundary'] = 'AFTER_PROVED_RETIREMENT_WITH_CERTAIN_CUSTODY'

    def capture_after_retirement(self):
        # Four preallocated stream records, with independent read/close attempts.
        # No optional reporting helper is entered between these attempts.
        for item in self.all_capture:
            if (self.empty_observed and self.retired and not self.unknown and
                    item in self.inner_capture and item['reader'] is None and
                    not item['attempted'] and self.round_root is not None):
                try:
                    self.acquire_retired_inner(item)
                except BaseException as error:
                    item['acquire_error'] = error
                    self.last_error = error
                    if self.first_error is None:
                        self.first_error = error
                    if self.guard['primary'][0] is None:
                        self.guard['primary'][0] = error
                    if self.error_count < 1024:
                        self.error_events[self.error_count][0] = 'inner-capture-acquire'
                        self.error_events[self.error_count][1] = error
                        self.error_count = self.error_next[self.error_count]
                    else:
                        self.unknown = True
            if self.empty_observed and item['reader'] is not None and item['reader']['phase'] == 'OWNED':
                try:
                    self.read_capture_known(item)
                except BaseException as error:
                    item['read_error'] = error
                    self.last_error = error
                    if self.first_error is None:
                        self.first_error = error
                    if self.guard['primary'][0] is None:
                        self.guard['primary'][0] = error
                    if self.error_count < 1024:
                        self.error_events[self.error_count][0] = 'capture-full-read'
                        self.error_events[self.error_count][1] = error
                        self.error_count = self.error_next[self.error_count]
                    else:
                        self.unknown = True
            if self.empty_observed and item['reader'] is not None:
                try:
                    self.close_fd(item['reader'])
                except BaseException as error:
                    item['close_entry_error'] = error
                    self.last_error = error
                    if self.first_error is None:
                        self.first_error = error
                    if self.guard['primary'][0] is None:
                        self.guard['primary'][0] = error
                    if self.error_count < 1024:
                        self.error_events[self.error_count][0] = 'capture-reader-close'
                        self.error_events[self.error_count][1] = error
                        self.error_count = self.error_next[self.error_count]
                    else:
                        self.unknown = True

'''
s=s[:start]+replacement+s[end:]
s=s.replace("                                   full_read=True, eof=True, prebirth_reader=True,\n                                   read_chunk_bytes=CHUNK)", "                                   full_read=True, eof=True,\n                                   reader_acquisition_boundary=item['acquisition_boundary'],\n                                   read_chunk_bytes=CHUNK)")
s=s.replace("        logs = {}\n        for item in domain.capture:\n            logs[item['name']]", "        logs, inner_logs = {}, {}\n        for item in domain.all_capture:\n            destination = logs if item in domain.capture else inner_logs\n            destination[item['name']]")
s=s.replace("'path': str(evidence / item['name']), 'sha256': None, 'bytes': None,", "'path': str(item.get('path')), 'sha256': None, 'bytes': None,")
s=s.replace("                'raw_error_retained': item['read_error'] is not None}", "                'raw_error_retained': item['read_error'] is not None or item.get('acquire_error') is not None,\n                'absence_observed': item.get('absence_observed', False),\n                'reader_acquisition_boundary': item.get('acquisition_boundary')}")
s=s.replace("'cleanup': cleanup, 'outer_logs': logs, 'sampled_owned_rss_bytes': peak,", "'cleanup': cleanup, 'outer_logs': logs, 'inner_target_logs': inner_logs,\n                  'sampled_owned_rss_bytes': peak,")
# The successful returned Popen object stays retained even if root registration
# fails before its generation corroboration. A direct matching pid receives the
# recorded key, so consuming it always sets this very object's returncode.
s=s.replace("                for row in direct:\n                    ticket = self.add(row)", "                for row in direct:\n                    if self.process is not None and row['pid'] == self.process.pid and self.root is None:\n                        self.root = generation(row)\n                    ticket = self.add(row)")
s=s.replace("        # Publication's own real close/pending tokens join this same owner.", "        if process is not None and domain.process is None:\n            domain.process = process\n            guard['actual_process'] = process\n            domain.birth = 'POPEN_RETURNED'\n        # Publication's own real close/pending tokens join this same owner.")
ast.parse(s)
p.write_text(s)
print({'bytes':len(s.encode()),'sha256':hashlib.sha256(s.encode()).hexdigest(),'validation':'AST only'})
