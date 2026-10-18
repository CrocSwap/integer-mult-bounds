#!/usr/bin/env python3
"""Verify a witness package: build everything from WITNESS.json, then compare with EXPECTED.json.

  python3 verify.py --package PKG --work NEW_DIR [--witness W.json] [--expected E.json] [--source NAME=DIR ...] [--jobs N]

The package holds data/WITNESS.json, data/EXPECTED.json, data/PLAN.json, data/OWNERS.json.gz and any recipes the
witness names as `pkg:...`. Pinned source packages default to PKG/../<dir named in the witness>. The run:

1. checks the package MANIFEST (if present), every pinned source manifest/file, PLAN and OWNERS;
2. replays the frozen PR558 baseline;
3. rebuilds every provider word from its base through the typed steps in WITNESS.build (allowlisted below),
   each followed by its paired omission/negative-control audit;
4. localizes each word with the unchanged vendor pipeline (native frames, ledgers, controls, wrappers, phases);
5. runs the global admission in code/ (bind, emit, independent audit, invoice, assembly, controls).

WITNESS.json holds inputs only; everything is computed from it. EXPECTED.json holds expected values only; each is
compared after it has been recomputed, and a mismatch stops the run naming the key. No expected value feeds a
computation.
"""
import argparse, gzip, hashlib, json, os, shutil, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from pathlib import Path
assert __debug__, 'run without -O: the checks are assertions'

TOOL = Path(__file__).resolve().parent
CODE = TOOL / 'code'
STEP_TYPES = ('cold_kernel', 'multicut', 'greedy_kernels', 'promote', 'joint_prefix', 'frozen558_scalar_audits')
LOCAL_FILES = ('INDEPENDENT-LOCAL-REPLAY.json', 'CLIFFORD-REVIEW.json', 'WRAPPER-CHECKS.json')


def read(p):
    data = Path(p).read_bytes()
    return json.loads(gzip.decompress(data) if str(p).endswith('.gz') else data)


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def content(p): return hashlib.sha256(gzip.decompress(Path(p).read_bytes())).hexdigest()


def dump(p, x): Path(p).write_text(json.dumps(x, indent=2) + '\n', newline='\n')


def tree(root, skip):
    return {f.relative_to(root).as_posix(): sha(f) for f in root.rglob('*')
            if f.is_file() and f != root / skip and '__pycache__' not in f.parts}


class Verifier:
    def __init__(self, a):
        self.pkg = a.package.resolve()
        self.discover = a.discover
        self.witness_file = (a.witness or self.pkg / 'data/WITNESS.json').resolve()
        self.witness = read(self.witness_file)
        self.build = self.witness['build']
        if self.discover:
            self.expected_file, self.expected = None, dict(build={})
        else:
            self.expected_file = (a.expected or self.pkg / 'data/EXPECTED.json').resolve()
            self.expected = read(self.expected_file)
        given = dict(x.split('=', 1) for x in a.source)
        self.src = {n: Path(given.get(n, self.pkg.parent / s['dir'])).resolve() for n, s in self.build['sources'].items()}
        # The PR568 package carries the run wrapper, the frozen PR558 replay and the vendored local pipeline.
        S = self.src['multicold']
        self.S, self.B = S, S / 'vendor/pr558'
        self.F = self.B / 'vendor/pr552'
        self.V = self.F / 'complex-global/vendor531'
        self.GK = self.F / 'complex-local/static44/gk'
        self.lock = threading.Lock()
        self.stages = []

    # ---- pins -------------------------------------------------------------------------------------------------
    def pinned(self, where, key, got, label):
        """Compare a recomputed build value with EXPECTED.build; discovery records it instead (spec.py writes it out)."""
        if self.discover:
            where[key] = got
        else:
            assert key in where, 'BUILD PIN MISSING %s.%s' % (label, key)
            assert got == where[key], 'BUILD PIN MISMATCH %s.%s: expected %s got %s' % (label, key, where[key], got)
        return got

    def input_file(self, s, key, tag):
        """A recipe named by the witness, checked against its witness hash pin before use."""
        path = self.ref(s[key])
        assert sha(path) == s[key + '_sha256'], 'INPUT PIN MISMATCH %s.%s' % (tag, key)
        return path

    def ref(self, r):
        """'pkg:rel' is a file of this package; 'NAME:rel' is a pinned file of source NAME."""
        kind, rel = r.split(':', 1)
        if kind == 'pkg':
            return self.pkg / rel
        assert rel in self.build['sources'][kind]['files'], 'unpinned source file ' + r
        return self.src[kind] / rel

    def check_pins(self):
        if (self.pkg / 'MANIFEST.json').exists():
            assert tree(self.pkg, 'MANIFEST.json') == read(self.pkg / 'MANIFEST.json'), 'package MANIFEST'
        for name, s in self.build['sources'].items():
            root = self.src[name]
            assert sha(root / 'MANIFEST.json') == s['manifest_sha256'], name + ' manifest pin'
            manifest = read(root / 'MANIFEST.json')
            if s.get('full_tree'):
                assert tree(root, 'MANIFEST.json') == manifest, name + ' tree'
            files = manifest.get('files', manifest)
            for rel, value in s['files'].items():
                assert sha(root / rel) == value == files[rel], (name, rel)
        assert sha(self.pkg / 'data/PLAN.json') == self.witness['data']['plan_sha256'], 'data/PLAN.json pin'
        assert sha(self.pkg / 'data/OWNERS.json.gz') == self.witness['data']['owners_sha256'], 'data/OWNERS.json.gz pin'
        for pid, d in self.build['providers'].items():
            for i, s in enumerate(d['steps']):
                assert s['type'] in STEP_TYPES, 'step type not allowlisted: ' + s['type']
                for k in ('recipe', 'kernel_recipes'):
                    if k in s:
                        self.input_file(s, k, '%s-step%d' % (pid, i))
        if not self.discover:
            assert self.expected['witness_sha256'] == sha(self.witness_file), 'EXPECTED.json was generated for a different WITNESS.json'

    # ---- running pinned scripts -------------------------------------------------------------------------------
    def env(self):
        e = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
                 MULTICOLD_SOURCE=str(self.S), GAIN_PR564_SOURCE=str(self.S), WITNESS_FILE=str(self.witness_file))
        for k in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_EXPECTED'):
            e.pop(k, None)
        if self.discover:
            e['WITNESS_DISCOVER'] = '1'
        else:
            e['WITNESS_EXPECTED'] = str(self.expected_file)
        return e

    def run(self, name, script, *args):
        log = self.O / (name + '.log')
        t = time.monotonic()
        print('RUN', name, flush=True)
        with log.open('w') as f:
            code = subprocess.call([sys.executable, '-B', str(self.S / 'code/run_portable.py'), str(script), *map(str, args)],
                                   stdout=f, stderr=subprocess.STDOUT, env=self.env())
        with self.lock:
            self.stages.append(dict(name=name, exit_code=code, seconds=round(time.monotonic() - t, 3), log_sha256=sha(log)))
            dump(self.O / 'STAGES.json', self.stages)
        if code:
            raise RuntimeError(name + ' failed\n' + log.read_text()[-6000:])
        print('PASS', name, flush=True)

    # ---- typed provider build steps ---------------------------------------------------------------------------
    def omissions(self, path, e, tag):
        self.pinned(e, 'omission_controls', len(read(path)['controls']), tag)

    def cold_kernel(self, word, s, e, out, tag):
        """PR568 single-cold kernel constructor and its kernel omission audit."""
        recipe = self.input_file(s, 'recipe', tag)
        self.run(tag + '-construction', self.S / 'code/build_cold_kernel.py', '--input', word, '--recipe', recipe, '--gk-dir', self.GK, '--out', out)
        self.run(tag + '-omissions', self.S / 'code/audit_kernel_controls.py', '--word', out / 'FULL-WORD.json.gz', '--recipe', recipe,
                 '--out', out / 'KERNEL-OMISSION-CONTROLS.json')
        self.omissions(out / 'KERNEL-OMISSION-CONTROLS.json', e, tag)

    def multicut(self, word, s, e, out, tag):
        """PR568 multi-cut kernel constructor and its omission audit (also used for `greedy_kernels`)."""
        recipe = self.input_file(s, 'recipe', tag)
        self.run(tag + '-construction', self.S / 'code/build_multicut_kernels.py', '--input', word, '--recipe', recipe, '--gk-dir', self.GK, '--out', out)
        self.run(tag + '-omissions', self.S / 'code/audit_multicold_controls.py', '--word', out / 'FULL-WORD.json.gz', '--recipe', recipe,
                 '--out', out / 'MULTICOLD-OMISSION-CONTROLS.json')
        self.omissions(out / 'MULTICOLD-OMISSION-CONTROLS.json', e, tag)

    def promote(self, word, s, e, out, tag):
        """PR569 entrance-promotion constructor plus an independent frame-only transfer check with its controls."""
        recipe = self.input_file(s, 'recipe', tag)
        for f in ('providers/coupled_frames_base.py', 'providers/search_suffix_kernels.py'):
            self.ref('larger_gain:' + f)
        self.run(tag + '-construction', self.ref('larger_gain:providers/build_entrance_promotions.py'), '--word', word, '--recipes', recipe,
                 '--gk-dir', self.GK, '--out', out)
        source, built, recipes = read(word), read(out / 'FULL-WORD.json.gz'), read(recipe)
        frame_only(source, built, recipes)
        mutations = (
            ('reverted_promotion', lambda w: w['start_extra'].__setitem__(str(recipes[0]['pivot']), list(recipes[0]['old_frame']))),
            ('scalar_operation_changed', lambda w: w['B'][0].insert(0, 'mutated')),
            ('extra_entrance_changed', lambda w: w['start_extra'].__setitem__(
                next(k for k in w['start_extra'] if k not in {str(x['pivot']) for x in recipes}), [])),
            ('fixed_field_changed', lambda w: w.__setitem__('cut', w['cut'][:-1])))
        rejected = []
        for name, mutate in mutations:
            w = json.loads(json.dumps(built)); mutate(w)
            try:
                frame_only(source, w, recipes)
            except (AssertionError, KeyError, IndexError, TypeError):
                rejected.append(name)
            else:
                raise AssertionError('frame-only control accepted: ' + name)
        dump(out / 'FRAME-ONLY-CONTROLS.json', dict(status='PASS_FRAME_ONLY_PROMOTION_TRANSFER', promotions=len(recipes), controls=rejected))
        self.omissions(out / 'FRAME-ONLY-CONTROLS.json', e, tag)

    def joint_prefix(self, word, s, e, out, tag):
        """PR575 joint-prefix constructor with all-kernel omissions, rank-five omissions and the literal-prefix/coverage audit."""
        recipe, kern = self.input_file(s, 'recipe', tag), self.input_file(s, 'kernel_recipes', tag)
        assert s['variant'] in ('eightcold', 'width7')
        self.run(tag + '-construction', self.ref('joint_prefix:code/build_joint_prefix.py'), '--input', word, '--recipe', recipe,
                 '--variant', s['variant'], '--gk-dir', self.GK, '--out', out)
        shutil.copyfile(self.raw.parent / 'PROMOTION.json', out / 'PROMOTION.json')
        self.run(tag + '-all-kernel-omissions', self.ref('joint_prefix:code/audit_multicold_controls.py'), '--word', out / 'FULL-WORD.json.gz',
                 '--recipe', kern, '--out', out / 'ALL-KERNEL-CONTROLS.json')
        self.run(tag + '-rank5-omissions', self.B / 'code/audit_promoted_scalar.py', out / 'FULL-WORD.json.gz', self.sel, out / 'RANK5-CONTROLS.json')
        self.run(tag + '-independent-joint-prefix-and-coverage', self.ref('joint_prefix:code/audit_joint_prefix.py'), '--source', word,
                 '--word', out / 'FULL-WORD.json.gz', '--recipe', recipe, '--variant', s['variant'], '--kernel-recipes', kern,
                 '--controls', out / 'ALL-KERNEL-CONTROLS.json', '--rank5-controls', out / 'RANK5-CONTROLS.json',
                 '--promotion', out / 'PROMOTION.json', '--selection', self.sel, '--out', out / 'JOINT-PREFIX-AUDIT.json')
        j = read(out / 'JOINT-PREFIX-AUDIT.json')
        assert j['status'] == 'PASS_INDEPENDENT_LITERAL_PREFIX_AND_FINAL_KERNEL_COVERAGE'
        assert all(x['forward_rejected'] and x['reflected_rejected'] for x in read(out / 'ALL-KERNEL-CONTROLS.json')['controls'])
        self.omissions(out / 'ALL-KERNEL-CONTROLS.json', e, tag)
        self.pinned(e, 'rank5_controls', len(read(out / 'RANK5-CONTROLS.json')['controls']), tag)
        self.pinned(e, 'joint_negative_controls', len(j['negative_controls_rejected']), tag)

    def frozen558_scalar_audits(self, word, s, e, out, tag):
        """Inherited static44 and rank-five omission audits on a frozen558-descended word (the word is unchanged)."""
        out.mkdir()
        self.run(tag + '-static44', self.F / 'complex-local/static44/audit_scalar.py', word, self.sel, out / 'STATIC44-SCALAR-AUDIT.json')
        shutil.copyfile(self.raw.parent / 'PROMOTION.json', word.parent / 'PROMOTION.json')
        self.run(tag + '-rank5', self.B / 'code/audit_promoted_scalar.py', word, self.sel, out / 'PROMOTED-SCALAR-AUDIT.json')

    def build_word(self, pid, d):
        base = d['base']
        assert base['kind'] in ('frozen558_promoted', 'source_file'), base['kind']
        word = self.raw if base['kind'] == 'frozen558_promoted' else self.ref(base['file'])
        if self.discover:
            self.expected['build'][pid] = dict(steps=[{} for _ in d['steps']])
        e = self.expected['build'][pid]
        assert len(e['steps']) == len(d['steps']), pid + ': EXPECTED.build step count'
        self.pinned(e, 'base_content_sha256', content(word), pid)
        steps = {'cold_kernel': self.cold_kernel, 'multicut': self.multicut, 'greedy_kernels': self.multicut, 'promote': self.promote,
                 'joint_prefix': self.joint_prefix, 'frozen558_scalar_audits': self.frozen558_scalar_audits}
        for i, s in enumerate(d['steps']):
            assert s['type'] in steps, 'step type not allowlisted: ' + s['type']
            tag = '%s-step%d-%s' % (pid, i, s['type'])
            es = e['steps'][i]
            if s['type'] == 'frozen558_scalar_audits':
                steps[s['type']](word, s, es, self.O / tag, tag)
                continue
            self.pinned(es, 'input_content_sha256', content(word), tag)
            steps[s['type']](word, s, es, self.O / tag, tag)
            word = self.O / tag / 'FULL-WORD.json.gz'
            self.pinned(es, 'output_content_sha256', content(word), tag)
        self.pinned(e, 'word_content_sha256', content(word), pid)
        return word

    def localize(self, pid, word):
        """The unchanged vendor local pipeline: native frames, both reflected ledgers, local controls, wrappers, phases."""
        local, V = self.O / (pid + '-local'), self.V
        self.run(pid + '-all-columns-native-frames', V / 'code/audit_and_transport.py', '--raw', word,
                 '--routing', self.F / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz', '--out', local)
        self.run(pid + '-both-reflected-ledgers', V / 'code/emit_local.py', local)
        self.run(pid + '-independent-local-controls', V / 'code/audit_local.py', local)
        self.run(pid + '-normalized-wrappers', V / 'code/adapters_local.py', local / 'CANONICAL-WORD.json.gz', local / 'RESIDUAL-ADAPTERS.json',
                 local / 'WRAPPER-CHECKS.json')
        self.run(pid + '-all-phase-edges', self.B / 'code/phases_full.py', local, V / 'vendor/clifford')
        return local

    # ---- the whole run ----------------------------------------------------------------------------------------
    def verify(self, work, jobs, reuse_baseline=None, reuse_local=()):
        self.check_pins()
        O = self.O = work.resolve()
        assert not O.exists() and not any(O.is_relative_to(x) for x in (self.pkg, TOOL, *self.src.values())), 'work dir must be new and outside inputs'
        O.mkdir(parents=True)
        start = time.monotonic()
        if reuse_baseline:
            baseline = reuse_baseline.resolve()
        else:
            baseline = O / 'baseline558'
            self.run('frozen558-full-replay', self.B / 'verify.py', '--work', baseline)
        self.sel = baseline / 'reconstruction/static44/SELECTION.json'
        self.raw = baseline / 'reconstruction/promoted/FULL-WORD.json.gz'
        reuse = dict(x.split('=', 1) for x in reuse_local)

        def provider(pid):
            word = self.build_word(pid, self.build['providers'][pid])
            return Path(reuse[pid]).resolve() if pid in reuse else self.localize(pid, word)
        with ThreadPoolExecutor(max(1, min(jobs, len(self.build['providers'])))) as pool:
            futures = {pid: pool.submit(provider, pid) for pid in sorted(self.build['providers'])}
            locals_ = {pid: f.result() for pid, f in futures.items()}
        if self.discover:
            dump(O / 'EXPECTED-BUILD.json', self.expected['build'])  # every recomputed build value

        G, P = O / 'mixed-global', self.pkg
        S, V = self.S, self.V
        self.run('bind-providers', CODE / 'bind_providers_portable.py', '--baseline', baseline,
                 *[x for pid, l in sorted(locals_.items()) for x in ('--provider', '%s=%s' % (pid, l))], '--plan', P / 'data/PLAN.json', '--out', G)
        self.run('emit-controller', CODE / 'emit_allcold.py', '--base', G / 'base', '--owners', P / 'data/OWNERS.json.gz', '--plan', G / 'PLAN.json', '--out', G / 'hosted')
        (G / 'audit').mkdir()
        self.run('independent-controller-and-controls', CODE / 'audit_allcold.py', G / 'base', G / 'hosted', G / 'audit/ASYNC-AUDIT.json', '--mutation-controls')
        self.run('fresh-invoice', CODE / 'invoice_allcold.py', '--base', G / 'base', '--hosted', G / 'hosted', '--audit', G / 'audit', '--out', G / 'audit',
                 '--retained-invoice', V / 'evidence/audit/PREFIX-AND-INVOICE.json')
        self.run('conservative-and-native-exact-assembly', CODE / 'assemble.py', S, G, O / 'ASSEMBLY.json')
        self.run('admission-controls', CODE / 'assembly_controls.py', '--source-package', S, '--owner', G / 'audit/OWNERS-AND-PROFILE.json',
                 '--invoice', G / 'audit/PREFIX-AND-INVOICE.json', '--out', O / 'ASSEMBLY-CONTROLS.json')
        if self.discover:  # the phase-timing controls compare against the pinned semantic phase hash
            print('DISCOVERY DONE', O)
            return None
        self.run('phase-timing-portability-controls', CODE / 'phase_timing_controls.py', S, G / 'base', G / 'audit', O / 'PHASE-TIMING-CONTROLS.json')

        X, PR = self.expected['global'], self.expected['providers']
        assert set(PR) == {p for _, _, p in self.witness['dispatch']} == set(locals_), 'EXPECTED.providers differ from dispatched providers'
        for pid, local in locals_.items():
            r, ph = read(local / 'INDEPENDENT-LOCAL-REPLAY.json'), read(local / 'CLIFFORD-REVIEW.json')
            assert len(r['negative_controls_rejected']) == PR[pid]['native_negative_controls'] and r['paid_profiles']['forward'] == r['paid_profiles']['backward']
            assert ph['status'] == 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES' and ph['all_child_equalities_include_global_phase'] is True
            assert ph['directed_edges'] == PR[pid]['phase_edges'] and ph['endpoint_adapters'] == 2 * self.witness['geometry']['v']
        assert len(read(G / 'audit/ASYNC-AUDIT.json')['mutations_rejected']) == X['mutations_rejected']
        assert len(read(O / 'ASSEMBLY-CONTROLS.json')['rejected_controls']) == X['assembly_controls_rejected']
        z = read(O / 'ASSEMBLY.json')
        assert Fraction(z['kappa_decimal']) == Fraction(X['kappa_decimal']), 'SPEC MISMATCH expected.kappa_decimal'
        assert Fraction(z['conservative_kappa_decimal']) == Fraction(X['conservative_kappa_decimal']), 'SPEC MISMATCH expected.conservative_kappa_decimal'
        assert {str(k): v for k, v in z['complex_profile'].items()} == X['global_profile'] and z['provider_counts'] == X['provider_counts']
        result = dict(status=self.build['status'], name=self.witness['name'], **{k: z[k] for k in (
            'kappa', 'kappa_decimal', 'complex_lower', 'bit_lower', 'conservative_kappa_decimal', 'conservative_complex_lower',
            'provider_counts', 'surcharge_model', 'scope')}, global_profile=z['complex_profile'], seconds=time.monotonic() - start,
            reused=dict(baseline=bool(reuse_baseline), locals=sorted(reuse)))
        dump(O / 'RESULT.json', result)
        paths = ['RESULT.json', 'ASSEMBLY.json', 'ASSEMBLY-CONTROLS.json', 'PHASE-TIMING-CONTROLS.json', 'mixed-global/BINDING.json',
                 'mixed-global/audit/ASYNC-AUDIT.json', 'mixed-global/audit/OWNERS-AND-PROFILE.json', 'mixed-global/audit/PREFIX-AND-INVOICE.json',
                 'mixed-global/audit/IDLE-REMAINDER-FRAMES.json']
        paths += sorted(f.relative_to(O).as_posix() for f in O.glob('*-step*/*.json'))
        paths += [pid + '-local/' + fn for pid in sorted(set(locals_) - set(reuse)) for fn in LOCAL_FILES]
        dump(O / 'RECEIPT.json', dict(status=result['status'], steps=self.stages, artifacts={p: sha(O / p) for p in paths},
                                      witness_sha256=sha(self.witness_file), expected_sha256=sha(self.expected_file), source_manifest_sha256={n: sha(self.src[n] / 'MANIFEST.json') for n in self.src}))
        print(json.dumps(result, indent=2))
        return result


def frame_only(source, word, recipes):
    """A promotion may change only entrance frames: identical scalar operations, start_extra changed exactly at the
    recipe pivots (old -> new frame), and report changes limited to entrance bookkeeping."""
    assert source.keys() == word.keys()
    for section in source:
        if section in ('A', 'cut', 'B', 'cleanup', 'precondition'):
            assert len(source[section]) == len(word[section])
            assert all(x[:-1] == y[:-1] for x, y in zip(source[section], word[section])), 'scalar operation changed'
        elif section not in ('start_extra', 'report'):
            assert source[section] == word[section], 'fixed field changed: ' + section
    entrances = dict(source['start_extra'])
    for r in recipes:
        k = str(r['pivot'])
        assert sorted(entrances[k]) == sorted(r['old_frame']) and len(r['new_frame']) == len(r['old_frame']) + 1, 'wrong old entrance ' + k
        entrances[k] = word['start_extra'][k]
        assert sorted(entrances[k]) == sorted(r['new_frame']), 'wrong new entrance ' + k
    assert word['start_extra'] == entrances, 'entrance changed outside the recipe'
    allowed = {'local_profile', 'local_rank_mass', 'entrance_rank', 'entering_helpers', 'width_inventory'}
    assert source['report'].keys() == word['report'].keys()
    assert all(source['report'][k] == word['report'][k] for k in source['report'] if k not in allowed)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--package', type=Path, required=True, help='witness package directory')
    ap.add_argument('--work', type=Path, help='new output directory (not needed with --check-pins)')
    ap.add_argument('--witness', type=Path, help='inputs (default PACKAGE/data/WITNESS.json)')
    ap.add_argument('--expected', type=Path, help='expected values (default PACKAGE/data/EXPECTED.json)')
    ap.add_argument('--source', action='append', default=[], metavar='NAME=DIR', help='pinned source package directory')
    ap.add_argument('--jobs', type=int, default=3, help='provider chains built in parallel')
    ap.add_argument('--check-pins', action='store_true', help='check package, source, data and recipe pins, then stop')
    ap.add_argument('--discover', action='store_true', help='record values instead of comparing them (used by spec.py generate)')
    ap.add_argument('--reuse-baseline', type=Path, help='development only: reuse a frozen558 replay directory')
    ap.add_argument('--reuse-local', action='append', default=[], metavar='PID=DIR', help='development only: reuse a localized provider')
    a = ap.parse_args(argv)
    v = Verifier(a)
    if a.check_pins:
        v.check_pins()
        print('PINS OK', v.witness['name'], sha(v.witness_file))
        return
    if a.work is None:
        ap.error('--work is required')
    v.verify(a.work, a.jobs, a.reuse_baseline, a.reuse_local)


if __name__ == '__main__':
    main()
