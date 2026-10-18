#!/usr/bin/env python3
"""Fresh unchanged PR543 C++ legality and 5/9/11-stage replays.

Requires C++17 and Boost; set CXX and BOOST_INCLUDE if needed.
Scott Woolsey Biggart with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile

import verify as v


def run(command):
    result = subprocess.run([str(x) for x in command], capture_output=True, text=True)
    v.need(result.returncode == 0, 'command failed: ' + ' '.join(map(str, command)) + '\n' + result.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', type=Path)
    args = parser.parse_args()
    v.need(not v.sys.flags.optimize, 'run without -O')
    local = v.certificate()
    v.need(local == json.loads((v.HERE / 'CERTIFICATE.json').read_text()), 'local certificate differs')
    original = v.read_sources()
    changed = v.build(original, v.nominate(original))
    bit = v.ROOT / 'research/e8-bit-carrier-skeleton/code/bit'
    cpp = bit / 'checkers'
    include = ['-I' + str(cpp), '-I' + str(v.ROOT / 'research/e8-bit-carrier-skeleton/portable-include')]
    if os.environ.get('BOOST_INCLUDE'):
        include.append('-I' + os.environ['BOOST_INCLUDE'])
    compiler = [os.environ.get('CXX', 'c++'), '-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9'] + include
    result = {'status': 'PASS_R420_TARGET_BASIS_NATIVE', 'source_pins': v.sha((v.HERE / 'SOURCES.json').read_bytes()),
              'words': {}}
    with tempfile.TemporaryDirectory(prefix='r420-target-native-') as tmp:
        work = Path(tmp)
        legality = work / 'legality'
        run(compiler + [cpp / 'legality_h.cpp', '-o', legality])
        binaries = {}
        for pairs in (2, 4, 5):
            binaries[pairs] = work / ('columns-' + str(pairs))
            run(compiler + ['-DVPORTS=120', '-DRHELP=420', '-DKPAIRS=' + str(pairs),
                            cpp / 'columns_k.cpp', '-o', binaries[pairs]])
        for name, word in [('before', original), ('after', changed)]:
            folder = work / name; folder.mkdir()
            word_path = folder / 'word.json'; word_path.write_bytes(v.canonical(word))
            export = folder / 'export'
            run([v.sys.executable, '-I', '-B', v.ROOT / v.EXPORT, word_path, export])
            cin, cout = folder / 'cin', folder / 'cout'
            run([v.sys.executable, '-I', '-B', bit / 'regression/stage_cohort.py', export, export, cin, cout])
            output = folder / 'legality.json'
            run([legality, cin, cout, output])
            admitted = json.loads(output.read_text())
            v.need(admitted['common_frame_ADDs'] == local[name]['ADDs'] and admitted['rank_mass'] == 5112 and
                   admitted['copies'] == admitted['erasures'] == 9 and admitted['all_final_frames_pass'],
                   'C++ legality invoice')
            raw = cout / 'COHORT249-RECORDS.bin'
            v.need(v.sha(raw.read_bytes()) == local[name]['record_sha256'], 'staged stream changed')
            evidence = {'legality': 'PASS', 'stages': []}
            stream = list(struct.iter_unpack('<6i', raw.read_bytes()))
            # Delete a final D ADD. On the changed word this is target restoration.
            index = max(i for i, r in enumerate(stream) if r[0] == 1 and r[5] == 1)
            mutant = folder / 'missing-D-end.bin'
            mutant.write_bytes(b''.join(struct.pack('<6i', *r) for i, r in enumerate(stream) if i != index))
            for pairs, binary in binaries.items():
                output = folder / ('columns-' + str(pairs) + '.json')
                run([binary, raw, output])
                checked = json.loads(output.read_text())
                v.need(checked['formal_columns_checked'] == 240 * pairs + 420 and
                       checked['local_scalar_additions'] == local[name]['ADDs'] and
                       checked['payload_prefix_upper'] == local[name]['payload_prefix_upper'] and
                       checked['payload_prefix_bits'] == local[name]['payload_bits'] and
                       dict(checked['local_raw_H']) == {int(k): n for k, n in local[name]['histogram'].items()},
                       'C++ columns/prefix/profile mismatch')
                controls = checked['negative_controls']
                v.need(len(controls) == 6 * (pairs - 1) and all(c['rejected'] for c in controls), 'bridge controls')
                rejected = subprocess.run([str(binary), str(mutant), str(folder / 'invalid.json')],
                                          capture_output=True, text=True)
                v.need(rejected.returncode != 0 and 'local defining-decoder full formal column' in rejected.stderr,
                       'C++ missing D end must fail on its endpoint')
                evidence['stages'].append({'stages': 2 * pairs + 1,
                                           'formal_columns': checked['formal_columns_checked'],
                                           'bridge_controls': len(controls), 'missing_D_end_rejected': True})
            result['words'][name] = evidence
    if args.write_certificate:
        with args.write_certificate.open('x') as out:
            out.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        v.need(result == json.loads((v.HERE / 'NATIVE-CERTIFICATE.json').read_text()), 'native certificate differs')
    print('PASS_R420_TARGET_BASIS_NATIVE words=2 stages=5,9,11 columns=900,1380,1620 bridge_controls=96 missing_D_controls=6')


if __name__ == '__main__':
    main()
