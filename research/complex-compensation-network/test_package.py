#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Optimized standalone relocation and real corrupted-file controls.
conorholds, with substantial OpenAI Codex assistance.
"""
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def run(path):
    env = os.environ.copy(); env['PYTHONOPTIMIZE'] = '2'
    return subprocess.run([sys.executable, '-I', '-O', '-O', '-B', str(path / 'verify.py'), '--panel-only'],
                          cwd=path.parent, env=env, capture_output=True, text=True, timeout=60)


def change_json(path, mutate):
    obj = json.loads(path.read_text()); mutate(obj)
    path.write_text(json.dumps(obj)+'\n')


def main():
    with tempfile.TemporaryDirectory(prefix='complex-network-package-') as temporary:
        root = Path(temporary); original = root / 'relocated'
        shutil.copytree(HERE, original)
        result = run(original)
        check(result.returncode == 0 and 'PASS_COMPLEX_COMPENSATION_NETWORK' in result.stdout,
              'optimized standalone relocation: ' + result.stdout + result.stderr)
        mutations = []
        def add(name, mutate, error):
            mutations.append((name, mutate, error))
        add('omitted_literal_preparation', lambda p: change_json(p/'COMPENSATION.json', lambda x: x.pop(0)), 'literal compensation witness')
        add('aliased_recipe_gate', lambda p: change_json(p/'RECIPE.json', lambda x: x['operations'][0].__setitem__(2, x['operations'][0][1])), 'shear operand')
        add('undercharged_recipe', lambda p: change_json(p/'RECIPE.json', lambda x: x['claimed'].__setitem__('after_real', x['claimed']['after_real']-16)), 'paid recipe counts')
        add('corrupt_recorded_cost', lambda p: change_json(p/'CERTIFICATE.json', lambda x: x['counts'].__setitem__('after_real', x['counts']['after_real']-2)), 'panel certificate mismatch')
        add('corrupt_native_executable', lambda p: (p/'reference/native_emitter.py').write_bytes((p/'reference/native_emitter.py').read_bytes()+b'\n# altered\n'), 'reference hash')
        def corrupt_word(p):
            path = p/'reference/CANONICAL-WORD.json.gz'
            word = json.loads(gzip.decompress(path.read_bytes())); word['ports'][0] ^= 1
            path.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
        add('corrupt_source_word', corrupt_word, 'reference hash')
        add('wrong_native_provenance', lambda p: change_json(p/'SOURCES.json', lambda x: next(r for r in x['files'] if r['path'].endswith('/hpe_emit_local.py')).__setitem__('sha256', '0'*64)), 'executable provenance')
        add('duplicate_recipe_field', lambda p: (p/'RECIPE.json').write_text((p/'RECIPE.json').read_text().rstrip()[:-1]+',"grid_denominator":256}\n'), 'duplicate JSON key')
        add('omitted_literal_cleanup', lambda p: change_json(p/'CLEANUP.json', lambda x: x.pop(0)), 'literal cleanup witness')
        add('invalid_cleanup_pivot', lambda p: change_json(p/'CLEANUP-RECIPE.json', lambda x: x['blocks'][0]['pivots'][0].__setitem__(0, 704)), 'out-of-range pivot')
        add('unpaid_cleanup', lambda p: change_json(p/'CLEANUP-RECIPE.json', lambda x: x['claimed'].__setitem__('after_real', x['claimed']['after_real']-2)), 'cleanup complete paid counts')
        add('wrong_cleanup_source', lambda p: change_json(p/'CLEANUP-RECIPE.json', lambda x: x.__setitem__('original_cleanup_sha256', '0'*64)), 'cleanup input binding')
        add('changed_comparison_schedule', lambda p: (p/'comparators/pr1979/MENU.json').write_bytes((p/'comparators/pr1979/MENU.json').read_bytes()+b' '), 'comparison source hash: MENU.json')
        add('changed_comparison_stream', lambda p: (p/'comparators/pr1979/PROGRAMS.json.gz').write_bytes((p/'comparators/pr1979/PROGRAMS.json.gz').read_bytes()+b' '), 'comparison literal stream hash')
        add('corrupt_comparison_receipt', lambda p: change_json(p/'CERTIFICATE.json', lambda x: x['merged_gauge_comparison']['orientations']['forward'].__setitem__('published_real', 134068)), 'panel certificate mismatch')
        add('omitted_literal_forest', lambda p: change_json(p/'FOREST-COMPENSATION.json', lambda x: x.pop(0)), 'literal forest witness')
        add('changed_published_cleanup', lambda p: change_json(p/'PR1119-CLEANUP.json', lambda x: x.pop(0)), 'PR1119 cleanup payload binding')
        add('corrupt_matched_method_receipt', lambda p: change_json(p/'CERTIFICATE.json', lambda x: x['matched_method_comparison']['programs']['forest_current_cleanup']['forward'].__setitem__('copy_unit_real', 65376)), 'panel certificate mismatch')
        for name, mutate, error in mutations:
            directory = root/name; shutil.copytree(HERE, directory); mutate(directory)
            result = run(directory)
            check(result.returncode != 0 and error in result.stderr,
                  'corruption failed to reach intended guard: '+name+'\n'+result.stdout+result.stderr)
        bad_upstream = root/'untrusted-published-source'
        manifest = json.loads((original/'METHOD-BASELINES.json').read_text())
        source = bad_upstream/manifest['files'][0]['path']; source.parent.mkdir(parents=True)
        source.write_text('# untrusted comparison source\n')
        result = subprocess.run([sys.executable, '-I', '-O', '-B', str(original/'reproduce_baseline.py'),
                                 '--upstream', str(bad_upstream)], capture_output=True, text=True, timeout=60)
        check(result.returncode != 0 and 'published comparison source pin' in result.stderr,
              'untrusted published code did not reach source pin guard: '+result.stdout+result.stderr)
        print('PASS_COMPLEX_NETWORK_PACKAGE relocation=1 corrupt_files='+str(len(mutations))+
              ' external_source_pin=PASS optimized=2')


if __name__ == '__main__':
    main()
