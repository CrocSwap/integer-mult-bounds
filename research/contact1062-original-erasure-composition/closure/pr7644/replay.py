# SPDX-License-Identifier: Apache-2.0
"""Rebuild the word and perform a fresh serial native and signed application in isolated scratch."""
import argparse
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
B = runpy.run_path(str(HERE/'build.py'))


def execute(args):
    subprocess.run([sys.executable, '-I', '-B', *map(str,args)], check=True)


def independent():
    with TemporaryDirectory(prefix='chart1062-independent-') as tmp:
        result = Path(tmp)/'verification.json'
        source = B['BASE']
        execute([HERE/'independent.py', '--candidate', B['DATA']/'word.json.gz',
                 '--original-word', source/'data/word.json.gz', '--original-invoice', source/'data/invoice-new.json',
                 '--original-final', source/'data/FINAL.json', '--signed-caller', B['DATA']/'caller.json',
                 '--original-source', source, '--out', result])
        actual = json.loads(result.read_bytes())
        expected = json.loads((HERE/'receipts/independent.json').read_bytes())
        observed = {key:actual[key] for key in expected}
        B['require'](observed == expected, 'Independent scientific fields equal frozen verification receipt')
        print('PASS_CHART1062_INDEPENDENT', actual['status'])


def compare_receipt(live_file, reference):
    actual = json.loads(live_file.read_bytes())
    expected = json.loads((HERE/'receipts'/reference).read_bytes())
    B['require']({key:actual[key] for key in expected} == expected, reference)


def scientific():
    B['build']()
    with TemporaryDirectory(prefix='chart1062-application-') as tmp:
        scratch = Path(tmp)
        for name in ('run.py','word_checks.py'):
            shutil.copyfile(HERE/'application'/name, scratch/name)
        adapter = scratch/'run.py'
        work = scratch/'work'
        execute([adapter, 'prepare', '--work', work, '--package', B['BASE'],
                 '--word', B['DATA']/'word.json.gz', '--sha', B['CANONICAL'],
                 '--edits', B['DATA']/'edits.json', '--invoice', B['DATA']/'invoice.json',
                 '--claim', B['CLAIM']])
        execute([adapter, 'native', '--work', work, '--package', B['BASE']])
        compare_receipt(work/'producer54/validation_native/NATIVE-RESULT.json', 'native-science.json')
        execute([adapter, 'signed', '--work', work, '--package', B['BASE']])
        compare_receipt(work/'producer54/validation_signed/RESULT.json', 'signed-science.json')
        final = json.loads((work/'FINAL.json').read_bytes())
        expected = json.loads((HERE/'receipts/FINAL.json').read_bytes())
        B['require'](final == expected, 'Fresh application equals frozen final certificate')
        B['require'](json.loads((work/'DIRECTED-PRICE.json').read_bytes()) ==
                     json.loads((HERE/'receipts/DIRECTED-PRICE.json').read_bytes()),
                     'Second directed complete pricing computation equals frozen certificate')
        print('PASS_CHART1062_FRESH_COMPLETE_APPLICATION',B['CLAIM'], flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('build','independent','application'))
    args=parser.parse_args()
    B['require'](__debug__ and sys.version_info[:2] == (3,12),'Use CPython 3.12 -I -B')
    if args.stage=='build':
        B['build']()
        print('PASS_CHART1062_FROZEN_WORD', B['CANONICAL'])
    elif args.stage=='independent':
        independent()
    else:
        scientific()
