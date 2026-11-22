#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compare all four actual F-address streams to independent literal lowering.

Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
The all-call owner geometry and full finite invoice are separate obligations.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    runtime = HERE/'runtime-overlay/code/buffer_runtime.py'
    spec = importlib.util.spec_from_file_location('reviewed_buffer_runtime', runtime)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    binding_path = HERE/'GLOBAL-BUFFER-BINDING.json.gz'
    binding = read(binding_path)
    records = []
    for provider in ('gauge44','extra'):
        tag = 'base' if provider == 'gauge44' else 'extra'
        native_path = args.native/tag/'LOCAL-PROGRAMS.json.gz'
        need(sha(native_path) == binding['source_sha256']['native'][provider]['LOCAL-PROGRAMS.json.gz'], 'native source binding')
        original = read(native_path)
        for orientation in ('forward','backward'):
            selected = next(x for x in binding['calls'] if x['provider'] == provider and x['orientation'] == orientation)
            call = {k:selected[k] for k in ('time','owners','orientation')}
            call['provider_id'] = provider
            slots = {int(k):v for k,v in binding['providers'][provider][orientation]['slots'].items()}
            def ref(value):
                kind, register = value
                if kind == 'L':
                    return ['F',selected['owners'][register][0]]
                if kind == 'C':
                    return ['F',66304+register]
                need(kind == 'Z', 'unknown native operand')
                return ['F',slots[register]]
            wanted = []
            for event in copy.deepcopy(original[orientation]):
                kind = event[0]
                if kind == 'zero_buffer':
                    _,action,register = event
                    family = slots[register]
                    if action == 'alloc':
                        wanted += [['private_zero','alloc',family],['scalar',['clear',['F',family]],1]]
                    else:
                        need(action == 'free', 'unknown zero-buffer event')
                        wanted += [['scalar',['clear',['F',family]],1],['private_zero','free',family]]
                    continue
                if kind == 'scalar':
                    event[1][1] = ref(event[1][1])
                    if event[1][0] in ('add','copy'):
                        event[1][2] = ref(event[1][2])
                elif kind == 'warp':
                    event[1] = ref(event[1])
                elif kind == 'center':
                    event[1] = ['F',66304+event[1]]
                elif kind in ('adapter','residual_adapter','climb'):
                    event[2] = ['F',selected['owners'][event[2]][0]]
                else:
                    need(kind == 'phase', 'unknown native event')
                wanted.append(event)
            actual = list(module.iter_call_events({'buffer_binding':binding},call))
            need(actual == wanted, 'actual physical stream differs from independent lowering')
            records.append(dict(provider=provider,orientation=orientation,time=selected['time'],
                                native_events=len(original[orientation]),physical_events=len(actual),
                                native_program_sha256=sha(native_path),
                                actual_physical_stream_sha256=hashlib.sha256(json.dumps(actual,separators=(',',':')).encode()).hexdigest()))
    receipt = dict(status='PASS_INDEPENDENT_ACTUAL_FOUR_PHYSICAL_LOWERING_STREAMS',records=records,
                   buffer_runtime_sha256=sha(runtime),buffer_binding_sha256=sha(binding_path),
                   scope='One invocation for every provider/orientation. Every actual F operand and inserted CLEAR event compared to an independently constructed reference; all666 owner maps separately validated by the exact binding audit. No global arithmetic scalar replay or finite invoice claimed here.')
    if args.out:
        args.out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'])


if __name__ == '__main__':
    main()
