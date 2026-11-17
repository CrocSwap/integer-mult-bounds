"""In-memory macOS + Python 3.9 compatibility shim for #7605 clean launcher subprocesses.

Preserves all on-disk files and SHA-256 pin checks untouched; applies only:
  1. `source.py` Windows path separator fix (`str(arc.relative_to(HERE))` -> `arc.relative_to(HERE).as_posix()`),
  2. Python 3.9 `int.bit_count()` -> `bin(...).count("1")` at `builtins.compile` time,
  3. Propagates itself across child `subprocess.run` / `subprocess.check_output` Python invocations,
logging every in-memory adaptation to `py39-shim-adaptations.jsonl` inside this folder.
"""
from __future__ import annotations

import builtins
import hashlib
import importlib.machinery
import itertools
import json
from pathlib import Path
import runpy
import subprocess
import sys

SELF = Path(__file__).resolve()
LOG = SELF.parent / "py39-shim-adaptations.jsonl"
KNOWN_SOURCE_PY = "35a3a38c6fe57cfb703a57a0382ef6f6b738131753b5fb5b97a68185b82994e1"

_ORIG_COMPILE = builtins.compile
_ORIG_GET_CODE = importlib.machinery.SourceFileLoader.get_code
_ORIG_RUN = subprocess.run
_ORIG_CHECK_OUTPUT = subprocess.check_output
_ORIG_ZIP = builtins.zip
_ZIP_SENTINEL = object()


def _py310_zip(*iterables, strict=False):
    if not strict:
        return _ORIG_ZIP(*iterables)
    if not iterables:
        return iter(())
    iters = [iter(it) for it in iterables]

    def _strict_gen():
        while True:
            row = [next(it, _ZIP_SENTINEL) for it in iters]
            n_end = sum(1 for x in row if x is _ZIP_SENTINEL)
            if n_end == 0:
                yield tuple(row)
            elif n_end == len(iters):
                return
            else:
                raise ValueError("zip() argument lengths differ (strict=True)")

    return _strict_gen()


builtins.zip = _py310_zip

if not hasattr(itertools, "pairwise"):
    def _pairwise(iterable):
        a, b = itertools.tee(iterable)
        next(b, None)
        return _ORIG_ZIP(a, b)

    itertools.pairwise = _pairwise


def _rewrite_bit_count(src: str) -> str:
    needle = ".bit_count()"
    if needle not in src:
        return src
    cur = src
    while True:
        pos = cur.find(needle)
        if pos == -1:
            break
        i = pos - 1
        while i >= 0:
            ch = cur[i]
            if ch in ")]":
                close_ch = ch
                open_ch = "(" if ch == ")" else "["
                depth = 1
                i -= 1
                while i >= 0 and depth > 0:
                    if cur[i] == close_ch:
                        depth += 1
                    elif cur[i] == open_ch:
                        depth -= 1
                    i -= 1
            elif ch.isalnum() or ch in "_.":
                i -= 1
            else:
                break
        start = i + 1
        expr = cur[start:pos]
        if not expr:
            break
        cur = cur[:start] + f'bin({expr}).count("1")' + cur[pos + len(needle):]
    return cur


def _log_adapt(kind: str, filename: str, before_sha: str, after_sha: str) -> None:
    try:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "kind": kind,
                "filename": filename,
                "before_sha256": before_sha,
                "after_sha256": after_sha,
            }) + "\n")
    except Exception:
        pass


def _hooked_compile(source, filename, mode, flags=0, dont_inherit=False, optimize=-1, **kw):
    if isinstance(source, (str, bytes)):
        is_bytes = isinstance(source, bytes)
        text = source.decode("utf-8") if is_bytes else source
        if ".bit_count()" in text:
            adapted = _rewrite_bit_count(text)
            if adapted != text:
                _log_adapt(
                    "bit_count_py39",
                    str(filename),
                    hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    hashlib.sha256(adapted.encode("utf-8")).hexdigest(),
                )
                source = adapted.encode("utf-8") if is_bytes else adapted
    return _ORIG_COMPILE(source, filename, mode, flags=flags, dont_inherit=dont_inherit, optimize=optimize, **kw)


builtins.compile = _hooked_compile


def _hooked_get_code(self, fullname):
    path = Path(self.path)
    if path.name == "source.py":
        raw = path.read_bytes()
        h = hashlib.sha256(raw).hexdigest()
        if h == KNOWN_SOURCE_PY:
            src = raw.decode("utf-8")
            before = "str(arc.relative_to(HERE))"
            after = "arc.relative_to(HERE).as_posix()"
            assert src.count(before) == 1
            adapted = _rewrite_bit_count(src.replace(before, after))
            _log_adapt("source_py_posix", str(path), h, hashlib.sha256(adapted.encode("utf-8")).hexdigest())
            return _ORIG_COMPILE(adapted, str(path), "exec")
    raw_p = Path(self.path)
    if raw_p.is_file() and raw_p.suffix == ".py":
        raw_b = raw_p.read_bytes()
        try:
            txt = raw_b.decode("utf-8")
        except UnicodeDecodeError:
            return _ORIG_GET_CODE(self, fullname)
        if ".bit_count()" in txt:
            adapted = _rewrite_bit_count(txt)
            _log_adapt(
                "loader_bit_count_py39",
                str(raw_p),
                hashlib.sha256(raw_b).hexdigest(),
                hashlib.sha256(adapted.encode("utf-8")).hexdigest(),
            )
            return _ORIG_COMPILE(adapted, str(raw_p), "exec")
    return _ORIG_GET_CODE(self, fullname)


importlib.machinery.SourceFileLoader.get_code = _hooked_get_code


def _inject_shim(args):
    if isinstance(args, (list, tuple)) and len(args) >= 2 and str(args[0]) == sys.executable:
        out = list(args)
        for i, x in enumerate(out[1:], 1):
            sx = str(x)
            if sx.endswith(".py"):
                if Path(sx).resolve() != SELF:
                    out.insert(i, str(SELF))
                break
        return out
    return args


def _hooked_run(args, *a, **kw):
    return _ORIG_RUN(_inject_shim(args), *a, **kw)


def _hooked_check_output(args, *a, **kw):
    return _ORIG_CHECK_OUTPUT(_inject_shim(args), *a, **kw)


subprocess.run = _hooked_run
subprocess.check_output = _hooked_check_output


if __name__ == "__main__":
    target = Path(sys.argv[1]).resolve()
    sys.argv = sys.argv[1:]
    sys.path.insert(0, str(target.parent))
    src_txt = target.read_text(encoding="utf-8")
    if ".bit_count()" in src_txt:
        adapted_main = _rewrite_bit_count(src_txt)
        _log_adapt(
            "main_bit_count_py39",
            str(target),
            hashlib.sha256(src_txt.encode("utf-8")).hexdigest(),
            hashlib.sha256(adapted_main.encode("utf-8")).hexdigest(),
        )
        globs = {"__name__": "__main__", "__file__": str(target), "__builtins__": builtins}
        exec(_ORIG_COMPILE(adapted_main, str(target), "exec"), globs)
    else:
        runpy.run_path(str(target), run_name="__main__")
