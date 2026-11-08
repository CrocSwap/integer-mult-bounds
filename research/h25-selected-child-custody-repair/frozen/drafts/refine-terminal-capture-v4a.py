# AST/text source refinement only, no execution of supplied or authored targets.
from pathlib import Path
import ast, hashlib
r=Path('/workspace/scratch/35c1441288db/h25-selected-child-construction-20261108T203610Z')
p=r/'implementation/supervisor_family_v3.py'
s=p.read_text()
(r/'drafts/supervisor_family_v3-intermediate-v3.py.txt').write_text(s)
s=s.replace("self.capture = [dict(name=name, writer=None", "self.capture = [dict(kind='outer', name=name, writer=None")
s=s.replace("self.inner_capture = [dict(name=name, writer=None", "self.inner_capture = [dict(kind='inner', name=name, writer=None")
s=s.replace("        self.all_capture = self.capture + self.inner_capture\n", "        self.all_capture = self.capture + self.inner_capture\n        for item in self.all_capture:\n            item['read_entered'], item['read_bytes'], item['raw_complete'] = False, 0, False\n            item['read_digest'], item['raw_eof'] = None, False\n")
s=s.replace("item in self.inner_capture and", "item['kind'] == 'inner' and")
s=s.replace("logs if item in domain.capture else inner_logs", "logs if item['kind'] == 'outer' else inner_logs")
s=s.replace("        self.stop_signal = signum\n", "        if self.stop_signal is None:\n            self.stop_signal = signum\n")
s=s.replace("        alarm_handler_entered = True\n", "        need(time.monotonic() < deadline, 'No original root execution time remains after preparation')\n        alarm_handler_entered = True\n")
a=s.index('    def read_capture_known(self, item):'); b=s.index('    def prepare_inner_capture(',a)
replacement='''    def read_capture_known(self, item):
        """Read available held bytes before name/initial-seal corroboration."""
        reader = item['reader']
        need(reader is not None and reader['phase'] == 'OWNED', 'actual retained capture reader')
        fd, path = reader['fd'], item['path']
        item['read_entered'] = True
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_size <= LOG_CAP,
             'actual bounded regular capture descriptor')
        need(os.lseek(fd, 0, os.SEEK_SET) == 0, 'retained capture reader starts at zero')
        digest, total = hashlib.sha256(), 0
        item['read_digest'] = digest
        while total < before.st_size:
            data = os.read(fd, min(CHUNK, before.st_size - total))
            need(bool(data), 'complete available bounded capture')
            total += len(data)
            item['read_bytes'] = total
            digest.update(data)
        eof = os.read(fd, 1)
        item['raw_eof'] = eof == b''
        item['raw_complete'] = total == before.st_size and eof == b''
        after = os.fstat(fd)
        # An earlier failed identity-seal operation does not suppress reading
        # an available known descriptor. It still prevents accepted evidence.
        need(item['initial'] is not None and
             (before.st_dev, before.st_ino, before.st_mode, before.st_uid, before.st_nlink) ==
             item['initial'] and eof == b'' and
             identity(before) == identity(after) == identity(path.lstat()),
             'stable complete capture EOF and original named inode after domain emptiness')
        item['observation'] = dict(path=str(path), sha256=digest.hexdigest(), bytes=total,
                                   identity=list(identity(after)), stable=True,
                                   full_read=True, eof=True,
                                   reader_acquisition_boundary=item['acquisition_boundary'],
                                   read_chunk_bytes=CHUNK)
        return item['observation']

'''
s=s[:a]+replacement+s[b:]
s=s.replace("'raw_error_retained': item['read_error'] is not None or item.get('acquire_error') is not None,", "'raw_error_retained': item['read_error'] is not None or item.get('acquire_error') is not None,\n                'read_entered': item['read_entered'], 'actually_read_bytes': item['read_bytes'],\n                'available_fd_eof_observed': item['raw_eof'],\n                'available_fd_full_read_observed': item['raw_complete'],")
ast.parse(s)
p.write_text(s)
print({'bytes':len(s.encode()),'sha256':hashlib.sha256(s.encode()).hexdigest(),'validation':'AST only'})
