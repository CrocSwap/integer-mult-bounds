#!/usr/bin/env python3
"""Fresh public-source PR211 butterfly bit, PR193 complex and retained packing reproduction."""
import sys
if sys.flags.optimize:
    raise SystemExit('Assertions required')
if sys.version_info < (3, 11):
    raise SystemExit('Python 3.11+ required')
sys.dont_write_bytecode = True
sys.set_int_max_str_digits(0)
import argparse, copy, importlib.metadata, os, platform, subprocess, time, gzip, hashlib
from common import *
import bootstrap, effective_packing, verify_math


def admit(r):
    assert r['status']=='PASS source-bound V7 complete changed graph physical columns terminal and primes'
    expected=read(HERE/'expected-bit.json')
    assert r['metadata']['emitted_sha256']==expected['emitted_sha256']
    assert r['profile']==expected['profile']
    baseline=r['baseline_formal']
    assert len(baseline)==2 and {x['ring'] for x in baseline}=={'2','0'}
    assert all(x['formal_variables']==20668 and x['defining_decoder'] and x['all_dirty_and_source_columns_restored'] for x in baseline)
    assert all(x['identity']==(x['ring']=='2') and x['target_contract']==('F2 identity' if x['ring']=='2' else 'integer defining decoder') for x in baseline)
    assert {x['mutation'] for x in r['package_controls']}=={'broken_mix','outside_cap','below_level','dropped_star','non_nested'} and len(r['package_controls'])==5
    assert {x['mutation'] for x in r['word_controls']}=={'omit_compensation','missing_partner','stale','zero_operation_frame'} and len(r['word_controls'])==4
    assert all(type(x['rejection']) is str and x['rejection'] for x in r['package_controls']+r['word_controls'])
    assert all(r['package'][k]==v for k,v in {'W':22428,'roles':18908,'m':72,'deficit':1936}.items())
    t=r['terminal'];f=t['formal']
    assert len(f)==3 and {(x['mode'],x['direction']) for x in f}=={('F2',1),('Z',1),('Z',-1)}
    assert all(x['formal_columns']==20634 and x['source_columns']==1760 and x['target_columns']==1760 and x['dirty_columns']==17114 and x['all_outputs'] and x['all_sources_and_dirty_restored'] and x['retained_cleanup_literal_reverse'] and x['partner_mix_unmix_at_original_anchors'] for x in f)
    assert t['literal_sandwich_inverse'] and t['original_partner_delivery_anchors_retained'] and t['all_original_adjoint_responses_retained']
    assert set(t['controls'])=={'omit-write','omit-pre-target','omit-ancestor-response'} and set(t['controls'].values())=={'REJECTED'}
    p=r['prime_summary']
    assert p['status']=='PASS exact prime witnesses for every used physical frame'
    assert p['total_used_frames']==25723 and p['unique_used_bases']==24611
    assert r['prime_canonical_sha256']==expected['prime_canonical_sha256']
    names=set(expected['stage_names'])
    assert len(r['stages'])==len(names) and {x['stage'] for x in r['stages']}==names and all(x['status']=='PASS' for x in r['stages'])
    assert r['missing_prime_record_control_rejected'] and r['truncated_terminal_control_rejected'] and r['source_files_unchanged']

def admit_artifacts(output,fresh):
    expected=read(HERE/'expected-bit.json')
    for name,want in expected['emitted_sha256'].items():
        path=output/'effective-bit'/(name+'.gz')
        assert not path.is_symlink()
        assert hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()==want,'Persisted effective artifact drift: '+name
    path=output/'effective-bit/all-used-prime-witnesses.json.gz'
    assert not path.is_symlink()
    raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==fresh['prime_witness_sha256'],'Persisted prime archive drift'
    assert hashlib.sha256(gzip.decompress(raw)).hexdigest()==fresh['prime_canonical_sha256']==expected['prime_canonical_sha256'],'Persisted canonical prime drift'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--complex-root', type=Path, required=True)
    p.add_argument('--bit-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--check-inputs-only', action='store_true')
    a = p.parse_args()
    c0, b0 = a.complex_root.resolve(), a.bit_root.resolve()
    out = fresh_output(a.output, (HERE, c0, b0))
    manifest = check_package()
    sources = check_sources(c0, b0)
    if a.check_inputs_only:
        out.mkdir(parents=True)
        write(out / 'preflight.json', dict(status='PASS exact public source closure',
              proof_executed=False, manifest_sha256=manifest,
              source_file_counts={k: len(v) for k, v in sources.items()}))
        print('PASS public-source preflight; no supplier proof executed')
        return
    dependencies = {name: importlib.metadata.version(name) for name in ('numpy', 'scipy')}
    assert dependencies == {'numpy': '2.3.5', 'scipy': '1.17.0'}, 'Install the pinned requirements.txt'
    started = time.monotonic()
    out.mkdir(parents=True)
    c, b = bootstrap.prepare(c0, b0, out)
    commands = []

    def run(label, arguments):
        start = time.monotonic()
        log = out / (label + '.log')
        with log.open('x') as stream:
            proc = subprocess.run([sys.executable, '-B', *map(str, arguments)],
                   cwd=out, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
                   stdout=stream, stderr=subprocess.STDOUT)
        commands.append(dict(label=label, exit_code=proc.returncode,
                        seconds=time.monotonic()-start, log=log.name, log_sha256=sha(log)))
        (out / 'commands.json').write_text(json.dumps(commands, indent=2)+'\n')
        assert proc.returncode == 0, 'Stage failed; preserve ' + str(log)

    run('complex193', [HERE/'run_complex.py', '--repo', c, '--output', out])
    accepted = read(out/'complex-acceptance.json')
    assert accepted['status'] == 'PASS freshly executed six-stage PR193 proof'
    assert accepted['stages_executed'] == 6 and accepted['source_pins'] == sources['complex']
    run('complex_adapter_controls', [HERE/'adapter193/test_patch.py', '--repo193', c,
        '--actual', c/'research/source-assisted-v4/.work/canonical-result.json',
        '--output', out/'complex-adapter-controls.json'])
    controls = read(out/'complex-adapter-controls.json')
    assert controls['status'] == 'PASS two-root portability controls'
    assert len(controls['accepted']) == 4 and len(controls['rejected']) == 22
    run('bit211_butterflies', [HERE/'run_bit.py', '--bit-root', b, '--output', out])
    fresh = read(out/'effective-bit/receipt.json')
    admit(fresh)
    admit_artifacts(out,fresh)
    bad = copy.deepcopy(fresh); bad['terminal']['formal'] = []
    try:
        admit(bad)
    except AssertionError:
        pass
    else:
        raise AssertionError('Truncated receipt accepted')
    packed = effective_packing.run(b, fresh)
    write(out/'packing-scalar.json', packed)
    mathematical = js(verify_math.run(c, b, fresh, packed))
    assert mathematical == read(HERE/'certificate.json'), 'Deterministic mathematical certificate changed'
    write(out/'certificate.json', mathematical)
    assert check_sources(c0, b0) == sources
    check_sources(c, b)
    assert check_package() == manifest
    write(out/'receipt.json', dict(status='PASS clean public-source full reproduction',
        manifest_sha256=manifest, certificate_sha256=sha(out/'certificate.json'),
        bit_receipt_sha256=sha(out/'effective-bit/receipt.json'),
        complex_acceptance_sha256=sha(out/'complex-acceptance.json'),
        python=platform.python_version(), system=platform.system(), dependencies=dependencies,
        commands=commands, elapsed_seconds=time.monotonic()-started,
        fresh_complex_stages=6, fresh_changed_bit_physical_columns_and_primes=True,
        fresh_actual_chart_and_incidence=True, complete_nine_invocation_bill=True,
        complex_moment_and_finite_bill_rechecked=True, truncated_receipt_rejected=True,
        protected_source_pins_unchanged=True, private_evidence_inputs=False,
        kappa=mathematical['kappa']))
    print('PASS clean public-source PR211 butterfly candidate; conditional kappa=' + mathematical['kappa'])


if __name__ == '__main__':
    main()
