# Authoring-only text/AST changes; no target import or execution.
from pathlib import Path
import ast, hashlib, re
r=Path('/workspace/scratch/35c1441288db/h25-selected-child-construction-20261108T203610Z')
p=r/'implementation/supervisor_family_v3.py'
s=p.read_text()
(r/'drafts/supervisor_family_v3-intermediate-v1.py.txt').write_text(s)
s=s.replace("RUNNER_SHA = 'bd882e3dadb1b6aeaa63ee824f1a1c58f8ef2546b6840a2bffa46885a184d3eb'", "RUNNER_SHA = '7e8c678cfd7773780a2eb6f0e70f53ae251dc121d05df9d13879dd70d9d79292'")
s=s.replace("        self.error_events = [None] * 1024\n        self.error_count = 0", "        self.error_events = [[None, None] for unused in range(1024)]\n        self.error_next = list(range(1, 1025))\n        self.error_count = 0")
start=s.index('    def _remember(self, error, operation):')
end=s.index('    def _actual(self):',start)
s=s[:start]+s[end:]
# Inlining avoids failure to enter a reporting helper after a caught error and
# avoids tuple allocation/counter addition before the next mandatory attempt.
lines=[]
for line in s.splitlines(True):
    match=re.fullmatch(r"(\s*)(self|owner|domain)\._remember\(error, ('[^']+')\)\n",line)
    if not match:
        lines.append(line);continue
    pad,obj,operation=match.groups()
    lines.extend([
        f"{pad}{obj}.last_error = error\n",
        f"{pad}if {obj}.first_error is None:\n",
        f"{pad}    {obj}.first_error = error\n",
        f"{pad}if {obj}.guard['primary'][0] is None:\n",
        f"{pad}    {obj}.guard['primary'][0] = error\n",
        f"{pad}if {obj}.error_count < 1024:\n",
        f"{pad}    {obj}.error_events[{obj}.error_count][0] = {operation}\n",
        f"{pad}    {obj}.error_events[{obj}.error_count][1] = error\n",
        f"{pad}    {obj}.error_count = {obj}.error_next[{obj}.error_count]\n",
        f"{pad}else:\n",
        f"{pad}    {obj}.unknown = True\n",
    ])
s=''.join(lines)
s=s.replace("            signal.signal(signum, self.stop_handler)\n            self.stop_handler_changed[index] = True", "            self.stop_handler_changed[index] = True\n            signal.signal(signum, self.stop_handler)")
s=s.replace("        domain.restore_stop_handlers()\n    # All children", "    # All children")
s=s.replace("    _SUPERVISION_CURRENT[0] = None\n    if guard['primary'][0] is not None:\n", "    try:\n        domain.restore_stop_handlers()\n    except BaseException as error:\n        root_errors[8] = error\n        if guard['primary'][0] is None:\n            guard['primary'][0] = error\n    _SUPERVISION_CURRENT[0] = None\n    if guard['primary'][0] is not None:\n")
# Preserve first local guard error before entering any guard reporting helper.
s=s.replace("        _guard_fail(guard, error)\n        raise", "        if guard['primary'][0] is None:\n            guard['primary'][0] = error\n        _guard_fail(guard, error)\n        raise")
# Record failed cleanup helper entry locally before continuing the other stream.
s=s.replace("                    self.cleanup_errors[2 if item['name'] == 'root.stdout.raw' else 3] = error", "                    self.cleanup_errors[2 if item['name'] == 'root.stdout.raw' else 3] = error\n                    if self.first_error is None:\n                        self.first_error = error\n                    if self.guard['primary'][0] is None:\n                        self.guard['primary'][0] = error")
s=s.replace("                    self.cleanup_errors[4 if item['name'] == 'root.stdout.raw' else 5] = error", "                    self.cleanup_errors[4 if item['name'] == 'root.stdout.raw' else 5] = error\n                    if self.first_error is None:\n                        self.first_error = error\n                    if self.guard['primary'][0] is None:\n                        self.guard['primary'][0] = error")
ast.parse(s)
p.write_text(s)
print({'bytes':len(s.encode()),'sha256':hashlib.sha256(s.encode()).hexdigest(), 'parse':'AST only'})
