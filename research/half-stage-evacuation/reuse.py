"""Source-bound reuse of this session's completed unchanged native/parent checks.

Apache-2.0. OpenAI Codex assistance. Reuse does not cover changed owners,
chronology, global invoice or outer arithmetic; those are replayed freshly.
"""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import time

HERE = Path(__file__).resolve().parent
OLD = HERE.parent/'source-partner-residual-exchanges'


def read(p):
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def need(ok, message):
    if not ok:
        raise ValueError(message)


def reuse_fixed(cache, work, package, stages, native_dirs=None):
    frozen = OLD/'evidence/FULL-RESULT.json'
    need(sha(cache/'RESULT.json') == sha(frozen), 'exact completed cache receipt')
    result = read(frozen)
    need(result['status'] == 'PASS_RESIDUAL_EXCHANGE_COMPLETE_FINITE_ADMISSION_AND_OUTER', 'cache complete status')
    previous_stages = {s['name']: s for s in result['stages']}
    old_package = cache/'build/derivative'
    need(sha(package/'vendor/pr1297/MANIFEST.json') == sha(old_package/'vendor/pr1297/MANIFEST.json'), 'retained parent source manifest')
    need(sha(package/'vendor/pr1297/verify.py') == previous_stages['retained-parent']['script_sha256'], 'retained parent checker source')
    parent = cache/'parent'
    parent_result = read(parent/'RESULT.json')
    need(parent_result['status'] == 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION', 'parent cache status')
    need(parent_result['kappa'] == read(package/'vendor/pr1297/CLAIM.json')['kappa'], 'parent cache exact claim')
    need(all(s['exit_code'] == 0 for s in parent_result['stages']), 'parent cache complete stages')
    for tag, name in [('base', 'gauge44-word.json.gz'), ('extra', 'extra-word.json.gz')]:
        need(read(parent/f'native-{tag}/local/FULL-WORD.json.gz') == read(package/'vendor/pr1297'/name), 'retained parent input '+tag)
    out_parent = work/'parent'
    out_parent.mkdir()
    def ignore(path, names):
        return ['source_partners'] if Path(path).resolve() == (parent/'layout').resolve() else []
    shutil.copytree(parent/'layout', out_parent/'layout', ignore=ignore)
    for name in ['RESULT.json', 'STAGES.json']:
        shutil.copy2(parent/name, out_parent/name)
    stages.append(dict(name='retained-parent', exit_code=0, reused=str(parent),
                       source_manifest_sha256=sha(package/'vendor/pr1297/MANIFEST.json'),
                       result_sha256=sha(parent/'RESULT.json'), frozen_full_receipt_sha256=sha(frozen)))
    for tag in ['base', 'extra']:
        if native_dirs:
            src = Path(native_dirs[tag])
            deadline = time.monotonic()+1800
            while True:
                st = read(src/'STEPS.json') if (src/'STEPS.json').exists() else []
                need(all(s['exit_code'] == 0 for s in st), 'fresh changed-word native failure '+tag)
                if len(st) == 5: break
                need(time.monotonic() < deadline, 'fresh changed-word native timeout '+tag)
                time.sleep(5)
            need([s['step'] for s in st] == ['native','ledgers','local-replay','wrappers','phases'], 'fresh changed-word native stages '+tag)
            need(sha(package/'new/run_native_borrow.py') == previous_stages['native-'+tag]['script_sha256'], 'unchanged native checker code '+tag)
            need(read(src/'local/FULL-WORD.json.gz') == read(package/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz'), 'fresh native changed-word binding '+tag)
            review = read(src/'local/CLIFFORD-REVIEW.json')
            need(review['status'] == 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES', 'fresh phase status '+tag)
            need(review['canonical_word_sha256'] == sha(src/'local/CANONICAL-WORD.json.gz'), 'fresh phase canonical input '+tag)
            need(review['recipe_sha256'] == sha(src/'local/CLIFFORD-RECIPES.json'), 'fresh exact phase recipes '+tag)
            need(review['all_child_equalities_include_global_phase'] and review['warp_recipes_rank_zero'] and review['warp_recipes_equal_exact_512_column_product'], 'fresh exact warp/phase equalities '+tag)
            shutil.copytree(src, work/('native-'+tag))
            stages.append(dict(name='native-'+tag,exit_code=0,fresh_precomputed_from=str(src),
                word_source_head='8cd9dc88e24f062e2ca2fa7f4844a3d3319381fb',
                word_semantic_equality=True,canonical_sha256=sha(src/'local/CANONICAL-WORD.json.gz'),
                phase_receipt_sha256=sha(src/'local/CLIFFORD-REVIEW.json'),steps=st))
            print('PASS native-'+tag+' (fresh changed-word chain, receipt/hash-bound)',flush=True)
            continue
        src = cache/('native-'+tag)
        need(sha(package/'new/run_native_borrow.py') == previous_stages['native-'+tag]['script_sha256'], 'native checker source '+tag)
        need(read(src/'local/FULL-WORD.json.gz') == read(package/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz'), 'unchanged native word '+tag)
        steps = read(src/'STEPS.json')
        need([s['step'] for s in steps] == ['native','ledgers','local-replay','wrappers','phases'] and all(s['exit_code'] == 0 for s in steps), 'five cached native stages '+tag)
        review = read(src/'local/CLIFFORD-REVIEW.json')
        need(review == read(OLD/f'evidence/{tag.upper()}-CLIFFORD-REVIEW.json'), 'frozen phase receipt '+tag)
        need(review['canonical_word_sha256'] == sha(src/'local/CANONICAL-WORD.json.gz'), 'canonical phase input '+tag)
        need(review['recipe_sha256'] == sha(src/'local/CLIFFORD-RECIPES.json'), 'exact phase recipes '+tag)
        pins = result['supplier']['independent']['input_sha256']
        expected = [h for name, h in pins.items() if ('native-'+tag) in name and name.endswith('CANONICAL-WORD.json.gz')]
        need(expected == [sha(src/'local/CANONICAL-WORD.json.gz')], 'cached native bound to completed global receipt '+tag)
        shutil.copytree(src, work/('native-'+tag))
        stages.append(dict(name='native-'+tag, exit_code=0, reused=str(src),
                           word_semantic_equality=True, canonical_sha256=expected[0],
                           frozen_full_receipt_sha256=sha(frozen)))
        print('PASS native-'+tag+' (unchanged, source/receipt/hash-bound reuse)', flush=True)
    print('PASS retained-parent (unchanged, source/receipt-bound reuse)', flush=True)
