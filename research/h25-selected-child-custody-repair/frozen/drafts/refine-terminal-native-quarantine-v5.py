# Passive source/AST authoring; no target imports or calls.
from pathlib import Path
import ast,hashlib
r=Path('/workspace/scratch/35c1441288db/h25-selected-child-construction-20261108T203610Z')
p=r/'implementation/supervisor_family_v3.py';s=p.read_text()
(r/'drafts/supervisor_family_v3-intermediate-v4a.py.txt').write_text(s)
s=s.replace("        self.error_count = 0\n", "        self.error_count = 0\n        self.error_overflow = None\n",1)
s=s.replace("        self.pause_errors = [None] * 16\n", "        self.pause_errors = [None] * 16\n        self.pause_next = list(range(1, 17))\n        self.pause_count = 0\n        self.pause_overflow = None\n        self.pause_error_history_complete = True\n")
s=s.replace("self.io = [dict(phase='FREE', fd=None, path=None, working=None,", "self.io = [dict(phase='FREE', fd=None, attempted_close_fd=None, path=None, working=None,")
s=s.replace("self.tickets = [dict(phase='FREE', fd=None, key=None, pid=None,", "self.tickets = [dict(phase='FREE', fd=None, attempted_close_fd=None, key=None, pid=None,")
s=s.replace("self.capture = [dict(kind='outer', name=name, writer=None", "self.capture = [dict(kind='outer', path=None, name=name, writer=None")
s=s.replace("    def open_fd(self, path, flags, mode=0o600, absent_ok=False):", "    def open_fd(self, path, flags, mode=0o600):")
s=s.replace("            if absent_ok and type(error) is FileNotFoundError:\n                slot['phase'] = 'CLOSED'\n                raise\n", "")
a=s.index('            # The original first-delivered native contract')
b=s.index("            self.last_error = error",a)
s=s[:a]+"            # REQUIRED-NATIVE-PREMISES condition6: an exception class is\n            # never evidence that an acquiring operation acquired nothing.\n            slot['phase'], self.unknown = 'OPEN_UNKNOWN', True\n"+s[b:]
s=s.replace("        self._check()\n        slot = None\n        primary = None\n        parts, total = [], 0\n", "        self._check()\n        if absent_ok:\n            # os.stat is metadata-only in the original pinned primitive. An\n            # actual absent observation may skip a non-direct process, but a\n            # raced failure of the following open remains quarantined.\n            try:\n                os.stat(path, follow_symlinks=False)\n            except FileNotFoundError:\n                return None\n        slot = None\n        primary = None\n        parts, total = [], 0\n")
s=s.replace("slot = self.open_fd(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC, absent_ok=absent_ok)", "slot = self.open_fd(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC)")
a=s.index('        except FileNotFoundError as error:',s.index('    def read_metadata'))
b=s.index('        except BaseException as error:',a)
s=s[:a]+s[b:]
a=s.index('        except ProcessLookupError as error:',s.index('    def add(self, row):'))
b=s.index('        except BaseException as error:',a)
s=s[:a]+s[b:]
s=s.replace("                self.pause_errors[0] = error", "                if self.pause_count < 16:\n                    self.pause_errors[self.pause_count] = error\n                    self.pause_count = self.pause_next[self.pause_count]\n                elif self.pause_overflow is None:\n                    self.pause_overflow = error\n                else:\n                    self.pause_error_history_complete = False")
# No acquiring-native exception is silently mapped to successful absence.
ast.parse(s)
p.write_text(s)
print({'bytes':len(s.encode()),'sha256':hashlib.sha256(s.encode()).hexdigest(),'validation':'AST only'})
