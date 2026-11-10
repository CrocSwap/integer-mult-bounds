"""Join the two disjoint source circuits without moving a protected event.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The two row synthesizers retain CubeJerry and Nick Petalas's credit.
"""
from copy import deepcopy
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
SOURCE = 'research/p104-helper470-twin-rung-removal/WORD.json.gz'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            require(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source hash '+row['path'])


def source_word():
    authenticate()
    return json.loads(gzip.decompress((ROOT/SOURCE).read_bytes()))


def join(word, blocks):
    result = deepcopy(word)
    previous = len(word['program'])
    for block in reversed(blocks):
        start, stop = block['start'], block['stop']
        require(0 <= start < stop <= previous, 'ordered disjoint source intervals')
        require(sha256(canonical(word['program'][start:stop])).hexdigest() == block['source_sha256'], 'source block binding')
        result['program'][start:stop] = block['replacement']
        previous = start
    return result


def build():
    word = source_word()
    blocks = []
    for name in ['p104-prefix-row-synthesis', 'p104-chart127-suffix']:
        module = load(name, ROOT/'research'/name/'synthesize.py')
        source = word['program'][module.START:module.STOP]
        replacement, discovery = module.synthesize(source)
        blocks.append(dict(source_package=name, start=module.START, stop=module.STOP,
            frame=module.FRAME, source_sha256=sha256(canonical(source)).hexdigest(),
            replacement=replacement, discovery=discovery))
    return blocks, join(word, blocks)


if __name__ == '__main__':
    require(sys.argv[1:] in ([], ['--write']), 'supported arguments')
    blocks, word = build()
    if sys.argv[1:] == ['--write']:
        (P/'BLOCKS.json').write_bytes(canonical(blocks)+b'\n')
        (P/'WORD.json.gz').write_bytes(gzip.compress(canonical(word), mtime=0))
    else:
        require(blocks == json.loads((P/'BLOCKS.json').read_text()), 'complete regenerated blocks')
        require(canonical(word) == gzip.decompress((P/'WORD.json.gz').read_bytes()), 'complete regenerated word')
    print('PASS_P104_COMPOSED_SCALAR_CONSTRUCTION', len(word['program']))
