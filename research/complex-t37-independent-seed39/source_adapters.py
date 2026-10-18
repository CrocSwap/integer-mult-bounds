# SPDX-License-Identifier: Apache-2.0
"""Adapt PR870 replication counts and the charged complex prefix reserve.

The literal edit table records each before/after string and expected count.
T37 uses 333 calls and an 8+8+8+8+5 dedicated-bank envelope. Its complex
prefix reserve is 1024 bits, charged twice in the physical row coefficient.
The historical invoice remains pinned to 512 bits and is dominated by the
new allowance; its full per-vertex reserve and the fresh recount are retained.
Bit-side 512-bit coefficients and bootstrap cutoffs, local 192-bit bounds,
144 factors per wrapper, and the scalar adapter multiplier 16 are unchanged.
Source notices are preserved; vendored code is never modified.
"""
import argparse
import hashlib
import shutil
from common import HERE, read, require, sha, dump


def expected_runtime():
    source = HERE/'vendor/pr870'
    pins = read(HERE/'VENDOR-PINS.json')['pr870']['files']
    edits = read(HERE/'data/ADAPTER-EDITS.json')
    paths = {path.name: path for path in (source/'code').glob('*.py')}
    require({'code/'+name for name in paths} ==
            {relative for relative in pins if relative.startswith('code/')},
            'Pinned source code inventory')
    require(set(edits) <= set(paths), 'Adapter edit file inventory')
    contents, receipt = {}, {}
    for name, path in sorted(paths.items()):
        relative = 'code/'+name
        require(sha(path) == pins[relative], 'Vendored source pin: '+relative)
        text = path.read_text(encoding='utf-8')
        for before, after, count in edits.get(name, []):
            require(text.count(before) == count, 'Exact edit multiplicity: '+name+' '+before)
            text = text.replace(before, after)
        contents[name] = text.encode('utf-8')
        receipt[name] = dict(source_sha256=pins[relative],
                             output_sha256=hashlib.sha256(contents[name]).hexdigest(),
                             edits=edits.get(name, []))
    return contents, receipt


def inventory(directory):
    require(directory.is_dir(), 'Missing runtime directory: '+str(directory))
    return {path.relative_to(directory).as_posix(): path for path in directory.rglob('*')
            if path.is_file() and '__pycache__' not in path.parts}


def check_runtime(out):
    """Reconstruct every generated source byte and check the copied inputs."""
    contents, receipt = expected_runtime()
    code = inventory(out/'code')
    require(set(code) == set(contents), 'Runtime code file inventory')
    for name, expected in contents.items():
        require(code[name].read_bytes() == expected and sha(code[name]) == receipt[name]['output_sha256'],
                'Runtime code content mismatch: '+name)
    pins = read(HERE/'VENDOR-PINS.json')['pr870']['files']
    source_inputs, copied_inputs = inventory(HERE/'vendor/pr870/inputs'), inventory(out/'inputs')
    require({'inputs/'+name for name in source_inputs} ==
            {relative for relative in pins if relative.startswith('inputs/')},
            'Pinned source input inventory')
    require(set(copied_inputs) == set(source_inputs), 'Runtime input file inventory')
    for name, source in source_inputs.items():
        require(sha(source) == pins['inputs/'+name], 'Vendored input pin: '+name)
        require(copied_inputs[name].read_bytes() == source.read_bytes(), 'Runtime input mismatch: '+name)
    require(read(out/'ADAPTERS.json') == receipt, 'Runtime adapter receipt mismatch')
    return receipt


def materialize(out):
    require(not out.exists(), 'Runtime output must be new')
    contents, receipt = expected_runtime()
    (out/'code').mkdir(parents=True)
    for name, content in contents.items():
        (out/'code'/name).write_bytes(content)
    shutil.copytree(HERE/'vendor/pr870/inputs', out/'inputs')
    dump(out/'ADAPTERS.json', receipt)
    require(check_runtime(out) == receipt, 'Fresh runtime materialization')
    return receipt


if __name__ == '__main__':
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out', type=Path)
    materialize(parser.parse_args().out)
