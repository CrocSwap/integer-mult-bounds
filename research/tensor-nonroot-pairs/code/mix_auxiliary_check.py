"""Exact auxiliary-line extension of the retained upstream e8core/mix checker.
Only two algebraic representation changes: full-frame mask uses line count,
and half-dot-products stay rational rather than floor division. Upstream
Apache-2.0 attribution is preserved in the loaded sources and package vendor.
Usage: python mix_auxiliary_check.py RUNTIME_DIR WORD RECORDS OUT_JSON
"""
import hashlib, importlib.util, json, sys, types
from pathlib import Path
runtime, word, records, output = map(Path, sys.argv[1:5])
src = runtime / 'e8core.py'
text = src.read_text(encoding='utf-8')
changes = [
 ('FULL = (1 << v) - 1', "FULL = (1 << len(c['lines'])) - 1"),
 ('sum(a * b for a, b in zip(x, y)) // 2', 'Q(sum(a * b for a, b in zip(x, y)), 2)')
]
for old, new in changes:
    assert text.count(old) == 1, (old, text.count(old))
    text = text.replace(old, new)
m = types.ModuleType('e8core'); m.__file__ = str(src)
exec(compile(text, str(src) + ' [auxiliary-line extension]', 'exec'), m.__dict__)
sys.modules['e8core'] = m
mixsrc = runtime / 'mix_check.py'
spec = importlib.util.spec_from_file_location('auxiliary_mix_check', mixsrc)
mix = importlib.util.module_from_spec(spec); spec.loader.exec_module(mix)
w = json.loads(word.read_text())
frames = json.loads((records / 'frames.json').read_text())['frames']
r = mix.check(w, frames)
r.update(source_sha256=hashlib.sha256(word.read_bytes()).hexdigest(),
         original_engine_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
         original_mix_sha256=hashlib.sha256(mixsrc.read_bytes()).hexdigest(),
         representation_changes=[{'from': a, 'to': b} for a,b in changes],
         ports=w['v'], auxiliary_line_count=len(w['lines'])-w['v'])
output.write_text(json.dumps(r, indent=2)+'\n', encoding='utf-8')
print(json.dumps(r))
