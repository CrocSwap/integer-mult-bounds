#!/usr/bin/env python3
"""Full pinned PR364 replay, deterministic extension, physical checks and price.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from derive import derive
from controls import controls
from banks import verify_banks
from pricing import refine, serial

if not __debug__:
    raise SystemExit('Assertions must be enabled')
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'w3-design-t-staged-p10b-reorder-mc'
PARENT_MANIFEST='aafe5f9324db13d92b11ce9e3ec8e7b54973f921142700de98649ddc46e16354'
EXPECTED='804942957146173674940857/1000000000000000000000000000'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(root):
    expected={}
    for line in (root/'MANIFEST.sha256').read_text().splitlines():
        digest,name=line.split('  ',1)
        assert name not in expected
        expected[name]=digest
    actual={p.relative_to(root).as_posix():sha(p) for p in root.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p.name!='MANIFEST.sha256'}
    assert actual==expected, ('Package changed',str(root))
    return sha(root/'MANIFEST.sha256')


def portable(result):
    """Deterministic finite certificate; no machine paths, clocks or self hash."""
    keys=('source_hashes','engine_hashes','local_histogram','histogram','residual',
          'm','width','coarse','next_coarse','admitted','excluded','fallback_density',
          'fallback_calls','eta','beta','chain','assembly','kappa','gain_over_pr366',
          'gain_over_pr364','derivation','banks','local_operator_and_controls',
          'physical_legality','physical_columns','benchmark_pr366_kappa')
    expected={key:serial(result[key]) for key in keys}
    expected['physical_columns']={key:value for key,value in expected['physical_columns'].items()
                                  if key not in ('seconds','local_scalar_stream','scope')}
    return expected


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--boost-include',type=Path)
    parser.add_argument('--cxx')
    args=parser.parse_args()
    out=args.output.resolve()
    paths=[str(ROOT),str(out),sys.executable,
           str(args.boost_include or os.environ.get('BOOST_INCLUDE','/usr/include')),
           args.cxx or os.environ.get('CXX','c++')]
    if any(any(c.isspace() for c in path) for path in paths):
        raise SystemExit('The pinned upstream shell verifier requires source, output, Python, compiler and Boost paths without whitespace.')
    assert not out.exists(), 'Use a fresh output directory'
    assert not out.is_relative_to(ROOT.parent), 'Output must be outside research packages'
    manifest=check_manifest(ROOT)
    assert check_manifest(PARENT)==PARENT_MANIFEST
    out.mkdir(parents=True)
    env=dict(os.environ,PYTHON=sys.executable,PYTHONDONTWRITEBYTECODE='1')
    if args.boost_include: env['BOOST_INCLUDE']=str(args.boost_include.resolve())
    if args.cxx: env['CXX']=args.cxx
    with (out/'baseline-replay.txt').open('w') as log:
        subprocess.run(['bash',str(PARENT/'verify.sh'),str(out/'baseline')],check=True,
                       env=env,stdout=log,stderr=subprocess.STDOUT)
    word=out/'extension'
    derivation=derive(out/'baseline/F',word)
    with (out/'pr366-price.txt').open('w') as log:
        subprocess.run([sys.executable,'-B',str(PARENT/'code/price.py'),str(out/'pr366')],
                       check=True,env=env,stdout=log,stderr=subprocess.STDOUT)
    benchmark=json.loads((out/'pr366/kappa.json').read_text())
    assert benchmark['kappa']=='160987957846297/200000000000000000'
    negative=controls(word)
    banks=verify_banks(word)
    official=out/'official'
    official.mkdir()
    with (out/'extension-physical.txt').open('w') as log:
        commands=[
            [sys.executable,'-B',str(PARENT/'code/stage_official.py'),str(out/'baseline/parity'),str(word),str(official/'cin'),str(official/'cout')],
            [str(out/'baseline/legality'),str(official/'cin'),str(official/'cout'),str(official/'legality.json')],
            [str(out/'baseline/columns'),str(official/'cout/COHORT249-RECORDS.bin'),str(official/'columns.json')],
            [sys.executable,'-B',str(PARENT/'code/nondeg.py'),str(word),str(out/'baseline/parity')],
        ]
        for command in commands:
            subprocess.run(command,check=True,env=env,stdout=log,stderr=subprocess.STDOUT)
    legality=json.loads((official/'legality.json').read_text())
    columns=json.loads((official/'columns.json').read_text())
    assert legality['status']=='PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE'
    assert columns['status']=='PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL'
    assert columns['formal_columns_checked']==11930
    assert columns['local_odd_scalar_additions']==357762
    assert columns['payload_prefix_bits']==93
    result=refine(word,PARENT)
    assert str(result['kappa'])==EXPECTED and result['gain_over_pr366']>0
    assert result['width']==banks['normalized_stock']==208646
    assert result['residual']==banks['residual_rank_sum']==131846
    result.update(status='PASS_PR364_KERNEL_COMPONENT_EXTENSION_FULL_REPLAY',
                  upstream_pr='https://github.com/CrocSwap/integer-mult-bounds/pull/364',
                  upstream_head='f8c6a47abfec24b87cb1eb0a138dd73dfce2abe4',
                  retiming_pr='https://github.com/CrocSwap/integer-mult-bounds/pull/366',
                  retiming_head='d3d84202e528d6e147a8ea62463ae5c0125997cf',
                  benchmark_pr366_kappa=benchmark['kappa'],
                  parent_manifest_sha256=PARENT_MANIFEST,package_manifest_sha256=manifest,
                  derivation=derivation,local_operator_and_controls=negative,banks=banks,
                  physical_legality=legality,physical_columns=columns,
                  baseline_replay_sha256=sha(out/'baseline-replay.txt'),
                  extension_physical_log_sha256=sha(out/'extension-physical.txt'))
    assert portable(result)==json.loads((ROOT/'EXPECTED.json').read_text()), 'Portable certificate differs'
    assert check_manifest(ROOT)==manifest and check_manifest(PARENT)==PARENT_MANIFEST
    (out/'CERTIFICATE.json').write_text(json.dumps(serial(result),indent=2,sort_keys=True)+'\n')
    print(result['status'],EXPECTED,float(result['kappa']),flush=True)


if __name__=='__main__':
    main()
