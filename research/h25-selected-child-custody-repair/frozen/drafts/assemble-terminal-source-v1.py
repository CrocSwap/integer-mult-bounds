# Authoring-only text/AST assembly. Never imports or executes a target module.
from pathlib import Path
import ast
import hashlib
root = Path('/workspace/scratch/35c1441288db/h25-selected-child-construction-20261108T203610Z')
old = (root/'inputs/files/20_supervisor_family_v3.py').read_text()
io = (root/'drafts/terminal-io-fragment-v1.txt').read_text()
proc = (root/'drafts/terminal-proc-fragment-v1.txt').read_text()
owner = (root/'drafts/terminal-owner-fragment-v1.txt').read_text()
capture = (root/'drafts/terminal-capture-fragment-v1.txt').read_text()
run = (root/'drafts/terminal-run-root-fragment-v1.txt').read_text()
# Apply explicit source repairs to the retained first draft without overwriting it.
owner = owner.replace("def open_fd(self, path, flags, mode=0o600):", "def open_fd(self, path, flags, mode=0o600, absent_ok=False):")
owner = owner.replace("            slot['working'] = error\n            self.last_error = error", "            slot['working'] = error\n            if absent_ok and type(error) is FileNotFoundError:\n                slot['phase'] = 'CLOSED'\n                raise\n            self.last_error = error", 1)
owner = owner.replace("slot = self.open_fd(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC)", "slot = self.open_fd(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC, absent_ok=absent_ok)")
owner = owner.replace("fd = ticket['fd']\n            ticket['fd'], ticket['phase']", "self._check()\n            fd = ticket['fd']\n            ticket['attempted_close_fd'] = fd\n            ticket['fd'], ticket['phase']")
owner = owner.replace("fd = slot['fd']\n        slot['fd'], slot['phase']", "fd = slot['fd']\n        slot['attempted_close_fd'] = fd\n        slot['fd'], slot['phase']")
owner = owner.replace("        self.guard = guard\n", "        need(any(prior is guard for prior in _GUARD_ATTEMPTS), 'genuine reserved original guard')\n        self.guard = guard\n")
owner = owner.replace("        self.native_types, self.native_addressof, self.ctypes = None, None, None\n", "        self.native_types, self.native_addressof, self.ctypes = None, None, None\n        self.native_handle, self.native_flags, self.native_call = None, None, None\n")
owner = owner.replace("        self.native_evidence, self.native = evidence, native\n", "        self.native_evidence, self.native = evidence, native\n        self.native_call = native[1]\n        self.native_handle, self.native_flags = native[0]._handle, native[1]._flags_\n")
owner = owner.replace("        call = self.native[1]\n        need(call.argtypes", "        call = self.native[1]\n        need(call is self.native_call and self.native[0].prctl is call and\n             self.native[0]._name == LIBC and self.native[0]._handle == self.native_handle and\n             call._flags_ == self.native_flags and call.errcheck is None,\n             'actual retained libc/prctl association without an added callback')\n        need(call.argtypes")
# The real capture methods belong to the actual same class.
owner += '\n' + capture
s = old[:old.index('def stable_file(')] + io + '\n\n' + old[old.index('def proc('):]
s = s[:s.index('def proc(')] + proc + '\n\n' + s[s.index('def install_subreaper('):]
s = s[:s.index('class OwnedDomain:')] + owner + '\n\n' + s[s.index('def reconcile_missing_receipt('):]
# The original binding body is reached with the preallocated genuine guard.
a = s.index('def _guard_begin(case, deadline):')
b = s.index('    try:\n        binding = case', a)
s = s[:a] + "def _guard_begin(case, deadline, guard=None):\n    if guard is None:\n        guard = _guard_reserve(deadline)\n    need(any(prior is guard for prior in _GUARD_ATTEMPTS), 'actual source-reserved guard')\n" + s[b:]
a = s.index('def run_root('); b = s.index('def stop_supplement(', a)
s = s[:a] + run + '\n\n' + s[b:]
ast.parse(s)
out = root/'implementation/supervisor_family_v3.py'
out.write_text(s)
print({'path':str(out),'bytes':len(s.encode()),'sha256':hashlib.sha256(s.encode()).hexdigest(), 'validation':'AST parse only; no target import or execution'})
