#!/usr/bin/env python3
"""Fresh PR91 h23 and deferred-span h25 producers, followed by credited label swaps.

PR91: Chafik Boukhalfa with OpenAI Codex assistance. PR93 coordinate choices:
Rohan Arun with OpenAI Codex assistance. PR94 additional h25 swap: Maxime
Fleury with Codebuff assistance. Deferred storage and this composition:
Thomas DiFiore with OpenAI Codex assistance. Apache-2.0; inherited notices apply.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
import argparse
from concurrent.futures import ProcessPoolExecutor
import gzip
from hashlib import sha256
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PR91 = ROOT / 'references/frame-compiler/pr91'
SWAPS = {23: [(5, 6)], 25: [(22, 23), (5, 6)]}

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def packed(raw):
    stream = io.BytesIO()
    with gzip.GzipFile(filename='', mode='wb', fileobj=stream, mtime=0) as archive:
        archive.write(raw)
    return stream.getvalue()

def deferred_parent(work):
    """Redirect only generated outputs; inherited source checks retain their paths."""
    parent = ROOT / 'research/deferred-span-frames'
    sys.path.insert(0, str(parent))
    module = load('merged_private_deferred', parent / 'producer.py')
    original_here, original_check = module.HERE, module.check_sources
    def checked_original_sources():
        module.HERE = original_here
        try:
            original_check()
        finally:
            module.HERE = work
    (work / 'selection.json').write_bytes((parent / 'selection.json').read_bytes())
    module.check_sources = checked_original_sources
    module.HERE = work
    module.compile_axis(25)
    word = gzip.decompress((work / 'word-25.json.gz').read_bytes())
    assert word == gzip.decompress((parent / 'word-25.json.gz').read_bytes())
    result = json.loads((work / 'axis-25.json').read_text())['compiled']
    return result, word

def compile_axis(job):
    h, output = job
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f'merged-span-parent-{h}-') as directory:
        work = Path(directory)
        if h == 23:
            environment = dict(os.environ)
            environment.pop('SDKROOT', None)
            subprocess.run([sys.executable, str(PR91 / 'scripts/experiments/aligned_composition_compiler.py'),
                            '--h', '23', '--output', str(work / 'compiled.json'), '--word', str(work / 'word.json.gz')],
                           env=environment, check=True)
            compiled = json.loads((work / 'compiled.json').read_text())
            parent = gzip.decompress((work / 'word.json.gz').read_bytes())
            expected = json.loads((PR91 / 'research/aligned-composition/discovery-selection.json').read_text())['axes']['23']['word_sha256']
            assert sha256(parent).hexdigest() == expected
        else:
            compiled, parent = deferred_parent(work)
        nodeops = load('merged_private_nodeops', PR91 / 'scripts/experiments/aligned_composition_nodeops.py')
        permutation = list(range(h))
        for a, b in SWAPS[h]:
            permutation[a], permutation[b] = permutation[b], permutation[a]
        word = nodeops.relabel(json.loads(parent), permutation)
        raw = (json.dumps(word, separators=(',', ':')) + '\n').encode()
        archive = packed(raw)
        (output / f'word-{h}.json.gz').write_bytes(archive)
        result = dict(h=h, parent='PR91 264f202' if h == 23 else 'frozen deferred-span h25',
                      parent_word_sha256=sha256(parent).hexdigest(),
                      word_sha256=sha256(raw).hexdigest(), gzip_sha256=sha256(archive).hexdigest(),
                      swaps=SWAPS[h], permutation=permutation, compiled=compiled)
        (output / f'axis-{h}.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        print(f'PASS fresh merged-span parent and exact coordinate action h={h}, roles={word["R"]}', flush=True)
        return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--h', type=int, choices=(23, 25))
    args = parser.parse_args()
    if args.h:
        compile_axis((args.h, args.output))
    else:
        with ProcessPoolExecutor(max_workers=2) as pool:
            list(pool.map(compile_axis, [(h, args.output) for h in (23, 25)]))
