#!/usr/bin/env python3
"""Whole-head replay of PR #1175's four packages on one checked k8 chain, with one source-bound receipt.

The four packages stack on research/gauge44-slots (#1018) and are verified one on top of the other; this driver
runs them all from a single reconstruction of the seven-slot k8 word's chain and writes one receipt (stage scripts,
their SHA256, log SHA256, timings; every JSON/gz/log artifact's digest; the native provider identities each PLAN
binds; the physical owner inventories; the exact kappa of each package) so that a reviewer binds the exact native
providers, the physical owner allocation and the admission evidence of the whole head from one run.

  chain       research/gauge44-leaver8's reproduction of the k8 mutable-leaver chain (the 'base', 'cells' and 'chain'
              stages of scripts/verify_frontier1042.py, same arguments), or a completed scripts/verify_frontier1042.py
              work directory passed with --baseline1042 (its receipt is checked), or a chain directory (--chain).
  arcflow     research/gauge44-slots-arcflow/construction/slots/verify_slots.py: slot layer and its 34 controls, native
              locals of the slot word, independent audit_local, strict replay of the arc-flow owner map (T = 8).
  unpromo     research/gauge44-slots-unpromo-arcflow/construction/unpromo/verify_unpromo.py on the arcflow run: sixteen
              restored entrances, three rejected mutants, native locals, independent audit, strict replay.
  deepen      this package's construction/deepen/verify_deepen.py on the unpromo run: ten deepened ends, three rejected
              mutants, native locals, independent audit, strict replay.
  t16         research/gauge44-slots-t16-arcflow/verify_t16.py on the arcflow run's locals (T = 16).
  recounts    the standard-library owner recounts of the three T = 8 maps; the regenerated independent price receipts
              of all four packages must equal the committed ones byte for byte (the T16 package's receipt prices the T8
              profile it carries; its T16 profile is priced code-disjointly in the next stage).
  independent wholehead/check_independent.py: Josie Elliston's owner/event-window audit (research/t16-owner-audit-seed67,
              rules R1-R7, X1, X2, eleven controls) and Sagar Thakrar's code-disjoint pricing
              (research/pending-claims-independent-pricing) applied unchanged to every package.

Usage: python3 -B research/gauge44-slots-deepen-arcflow/verify_chain.py --main . --work /tmp/wholehead1175
         [--chain DIR | --baseline1042 DIR] [--pr635 research/complex-sw4-frame8/vendor/pr635]
Prepared by G. V. Chudnovsky with Anthropic Claude assistance. Apache-2.0.
"""
import argparse, gzip, hashlib, json, os, subprocess, sys, time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGES = {'arcflow': 'research/gauge44-slots-arcflow', 'unpromo': 'research/gauge44-slots-unpromo-arcflow',
            'deepen': 'research/gauge44-slots-deepen-arcflow', 't16': 'research/gauge44-slots-t16-arcflow'}
KAPPA = {'arcflow': '0.001674083482880778', 'unpromo': '0.001674576537247681',
         'deepen': '0.001675338871723469', 't16': '0.001674087289164567'}
FILES = ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json', 'INDEPENDENT-LOCAL-REPLAY.json',
         'CLIFFORD-RECIPES.json', 'CLIFFORD-REVIEW.json', 'RESIDUAL-ADAPTERS.json')
CHAIN_STAGES = ['leaver-manifest', 'base', 'cells', 'chain']


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(p): return hashlib.sha256(gzip.decompress(Path(p).read_bytes())).hexdigest()
def read(p):
    b = Path(p).read_bytes(); return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def require(ok, msg):
    if not ok: raise SystemExit('FAIL ' + msg)


def main():
    require(not sys.flags.optimize, 'assertions are required')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--main', type=Path, required=True, help='repository checkout')
    ap.add_argument('--work', type=Path, required=True, help='new output directory')
    ap.add_argument('--chain', type=Path, help='completed k8 chain directory (reproduce_leaver_chain.py --out)')
    ap.add_argument('--baseline1042', type=Path, help='completed scripts/verify_frontier1042.py work directory')
    ap.add_argument('--pr635', type=Path, help='PR635 supplier checkout (default: the vendored copy on main)')
    a = ap.parse_args()
    root = a.main.resolve(); work = a.work.resolve()
    require(not work.exists(), 'use a fresh output directory'); work.mkdir(parents=True)
    pr635 = (a.pr635 or root / 'research/complex-sw4-frame8/vendor/pr635').resolve()
    require((pr635 / 'research/complex-571-cold14-st2/code/hpe_audit_and_transport.py').is_file(), 'PR635 supplier')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    for k in ('PYTHONOPTIMIZE', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD'): env.pop(k, None)
    stages = []

    def run(name, script, *args, isolated=False):
        script = Path(script); log = work / (name + '.log'); t = time.monotonic()
        cmd = [sys.executable, '-I', '-B'] if isolated else [sys.executable, '-B']
        with log.open('w') as f:
            rc = subprocess.call(cmd + [str(script), *map(str, args)], cwd=root, env=env, stdout=f, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, exit_code=rc, seconds=round(time.monotonic() - t, 3),
                           script=script.relative_to(root).as_posix(), script_sha256=sha(script), log_sha256=sha(log)))
        (work / 'STAGES.json').write_text(json.dumps(stages, indent=2) + '\n')
        require(rc == 0, name + ' failed; see ' + str(log))
        print('PASS', name, stages[-1]['seconds'], flush=True)
        return log.read_text()

    pk = {k: root / v for k, v in PACKAGES.items()}
    for k in PACKAGES: run(k + '-manifest', pk[k] / 'verify_manifest.py')

    # 1. the k8 chain: cold, or an explicitly checked completed reconstruction
    leaver = root / 'research/gauge44-leaver8'
    if a.baseline1042:
        bl = a.baseline1042.resolve(); rec = read(bl / 'RESULT.json')
        require(rec['status'] == 'PASS_COMPLETE_PR1042_COMPOSITION', 'baseline1042 receipt')
        for s in rec['stages']:
            require(s['exit_code'] == 0 and sha(root / s['script']) == s['script_sha256'] and
                    sha(bl / (s['name'] + '.log')) == s['log_sha256'], 'baseline1042 stage ' + s['name'])
        chain = bl / 'chain'; chain_mode = 'reused scripts/verify_frontier1042.py replay ' + str(bl)
    elif a.chain:
        chain = a.chain.resolve(); chain_mode = 'supplied chain directory ' + str(chain)
    else:
        common = ['--main', root, '--pr635', pr635]
        run('leaver-manifest', leaver / 'verify_manifest.py')
        run('base', leaver / 'construction/reproduce.py', *common, '--out', work / 'base', '--until', 'word')
        run('cells', leaver / 'construction/leaver/reproduce_leaver.py', *common, '--word-dir', work / 'base', '--id', 'k8', '--out', work / 'cells')
        run('chain', leaver / 'construction/leaver/reproduce_leaver_chain.py', *common, '--leaver-dir', work / 'cells',
            '--hamming', work / 'base/hamming', '--id', 'k8', '--out', work / 'chain')
        chain = work / 'chain'; chain_mode = 'cold reconstruction'
    cp = read(leaver / 'construction/leaver/CHAIN-PINS-k8.json')
    require(csha(chain / 'local/CANONICAL-WORD.json.gz') == cp['canonical_sha256'], 'chain canonical word')

    # 2. the four packages, each on the previous one's completed run
    run('arcflow', pk['arcflow'] / 'construction/slots/verify_slots.py', '--main', root, '--pr635', pr635,
        '--baseline', chain, '--work', work / 'arcflow')
    run('unpromo', pk['unpromo'] / 'construction/unpromo/verify_unpromo.py', '--main', root, '--pr635', pr635,
        '--baseline', work / 'arcflow', '--work', work / 'unpromo')
    run('deepen', pk['deepen'] / 'construction/deepen/verify_deepen.py', '--main', root, '--pr635', pr635,
        '--baseline', work / 'unpromo', '--work', work / 'deepen')
    run('t16', pk['t16'] / 'verify_t16.py', '--main', root, '--local', work / 'arcflow/local', '--work', work / 't16')

    # 3. recounts and the independent price receipts (byte-identical to the committed ones)
    for k in ('arcflow', 'unpromo', 'deepen'):
        run(k + '-recount', pk[k] / 'construction/owners/recount_owners.py', isolated=True)
    for k in PACKAGES:
        out = work / ('price-%s.json' % k)
        # the T16 package's ported price_profile.py prices the T8 profile it carries (data/T8/PLAN.json, its README);
        # the T16 profile's code-disjoint price is stage 'independent' below
        extra = ['--profile', pk[k] / 'data/T8/PLAN.json'] if k == 't16' else []
        run(k + '-price', pk[k] / 'independent/price_profile.py', '--main', root, '--output', out, *extra)
        require(sha(out) == sha(pk[k] / 'independent/GAUGE44-INDEPENDENT-PRICE.json'), k + ' price receipt differs')

    # 4. independent owner audit and code-disjoint pricing of every package (unchanged auditors)
    words = dict(arcflow=work / 'arcflow/slots/FULL-WORD.json.gz', unpromo=work / 'unpromo/word/FULL-WORD.json.gz',
                 deepen=work / 'deepen/word/FULL-WORD.json.gz', t16=work / 'arcflow/slots/FULL-WORD.json.gz')
    strict = dict(arcflow=work / 'arcflow/global/ASSEMBLY.json', unpromo=work / 'unpromo/global/ASSEMBLY.json',
                  deepen=work / 'deepen/global/ASSEMBLY.json', t16=work / 't16/ASSEMBLY.json')
    run('independent', HERE / 'wholehead/check_independent.py', '--main', root, '--output', work / 'INDEPENDENT.json',
        *[x for k in PACKAGES for x in ('--word', '%s=%s' % (k, words[k]), '--assembly', '%s=%s' % (k, strict[k]))])
    ind = read(work / 'INDEPENDENT.json'); require(ind['status'] == 'PASS_INDEPENDENT_OWNERS_AND_PRICE_FOUR_PACKAGES', 'independent')

    # 5. one receipt: kappas, bit supplier, provider identities, inventories, artifacts
    sys.path.insert(0, str(pk['deepen'] / 'code'))
    from generated_identity import artifact_identities
    locals_ = dict(arcflow=work / 'arcflow/local', unpromo=work / 'unpromo/local', deepen=work / 'deepen/local', t16=work / 'arcflow/local')
    packages = {}; bits = set()
    for k in PACKAGES:
        asm = read(strict[k]); committed = read(pk[k] / 'RESULT.json'); plan = read(pk[k] / 'data/PLAN.json')
        replay = read(work / ('%s/global/REPLAY.json' % k)) if k != 't16' else read(work / 't16/REPLAY.json')
        layer = read(work / ('%s/RESULT.json' % k))['status'] if k != 't16' else replay['status']
        require(asm['kappa_decimal'] == KAPPA[k] == committed['kappa_decimal'] == replay['kappa_decimal'], k + ' kappa')
        require(replay['status'] in ('PASS_GAUGE44_STRICT_GLOBAL_REPLAY', 'PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY'), k + ' strict status')
        require(Fraction(asm['kappa']) == Fraction(committed['kappa']), k + ' exact kappa')
        require(len(asm['outer']) == 47 and all(Fraction(v) > 0 for v in asm['outer'].values()), k + ' strict outer assembly')
        bits.add(json.dumps(asm['bit_supplier'], sort_keys=True))
        reg = plan['provider_registry']['gauge44']; ids = artifact_identities(str(locals_[k]))
        require(ids == reg['artifact_semantic_sha256'], k + ' native provider identities')
        rebuilt = {f: sha(locals_[k] / f) for f in FILES}
        # as the bind stage: byte-pinned reference artifacts; the others carry timings and are pinned semantically
        require(all(rebuilt[f] == reg['artifact_sha256'][f] for f in ('LOCAL-CHECKS.json', 'CLIFFORD-RECIPES.json', 'RESIDUAL-ADAPTERS.json')), k + ' native provider reference artifacts')
        owners = read(pk[k] / 'data/OWNERS.json.gz')
        packages[k] = dict(package=PACKAGES[k], kappa=asm['kappa'], kappa_decimal=asm['kappa_decimal'],
                           complex_lower=asm['complex_lower'], bit_lower=asm['bit_lower'],
                           native_word_content_sha256=csha(words[k]), canonical_word_content_sha256=csha(locals_[k] / 'CANONICAL-WORD.json.gz'),
                           provider_artifact_sha256=reg['artifact_sha256'], rebuilt_artifact_sha256=rebuilt,
                           provider_artifact_semantic_sha256=reg['artifact_semantic_sha256'],
                           orientation_program_sha256=reg['orientation_program_sha256'], local_profile=reg['actual_paid_profile'],
                           width_inventory=ind['packages'][k]['owner']['width_inventory'],
                           plan_sha256=sha(pk[k] / 'data/PLAN.json'), owners_sha256=sha(pk[k] / 'data/OWNERS.json.gz'),
                           spec_sha256=sha(pk[k] / 'data/SPEC.json'), roles=len(owners), calls=len(plan['order']),
                           global_profile=plan['profile'], idle_remainder_profile=ind['packages'][k]['owner']['idle'],
                           layer_status=layer, strict_status=replay['status'], package_result_sha256=sha(pk[k] / 'RESULT.json'))
    require(len(bits) == 1, 'the four packages cite one bit supplier')
    require(json.loads(bits.pop()) == read(root / 'research/gauge44-slots/RESULT.json')['bit_supplier'], 'bit supplier equals research/gauge44-slots')
    artifacts = {p.relative_to(work).as_posix(): sha(p) for p in sorted(work.rglob('*'))
                 if p.is_file() and p.suffix in ('.json', '.gz', '.log') and p != work / 'RESULT.json'}
    result = dict(status='PASS_WHOLE_HEAD_GAUGE44_SLOTS_ARCFLOW_CHAIN', head_package=PACKAGES['deepen'],
                  kappa=packages['deepen']['kappa'], kappa_decimal=packages['deepen']['kappa_decimal'],
                  chain=chain_mode, chain_canonical_sha256=cp['canonical_sha256'], pr635_supplier=str(pr635),
                  packages=packages, bit_supplier=read(root / 'research/gauge44-slots/RESULT.json')['bit_supplier'],
                  independent=dict(status=ind['status'], controls_per_package={k: len(v['controls']) for k, v in ind['packages'].items()}),
                  stages=stages, artifacts=artifacts,
                  scope='Finite conditional witnesses on the #1005/#1018 chain, each replayed on the previous one with its native '
                        'locals rebuilt by the PR635 supplier; all-size compiler, common-label/mutable-source realization, '
                        'whole-call hosting, precision/tape, exact recovery, analytic transfer and bit H1-H5 remain assumptions.')
    (work / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], {k: v['kappa_decimal'] for k, v in packages.items()}, flush=True)


if __name__ == '__main__':
    main()
