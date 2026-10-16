# SPDX-License-Identifier: Apache-2.0
"""Bind PR2839's block-boundary premise checker to actual PR2833 native words.

Retained native/frame/phase routines and mathematical energy lemma keep their
original credit. This source-bound application and fault checks were prepared
by dataisfire with substantial OpenAI Codex assistance. No full theorem claim.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import blocknorm_certificate as BN

SOURCE_HEAD = 'e9307b48d7d1b690939935ecef0f8e524e6d92f4'
SOURCE_MANIFEST = 'c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f'
HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    need(not sys.flags.optimize, 'assertions enabled for inherited native checkers')
    native = args.native.resolve()
    receipt = BN.read(native/'NATIVE-RECEIPT.json')
    need(receipt['status'] == 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE', 'complete native protocol')
    need(receipt['source_commit'] == SOURCE_HEAD and receipt['manifest_sha256'] == SOURCE_MANIFEST, 'exact PR2833 source')
    cache = native/'native-cache'
    observed = {p.relative_to(cache).as_posix(): BN.digest(p) for p in cache.rglob('*') if p.is_file()}
    need(observed == receipt['cache_files'], 'complete authenticated native/cache inventory')
    registry, directories, artifacts = {}, {}, {}
    for tag, pid in (('base','gauge44'),('extra','extra')):
        binding = receipt['providers'][tag]
        base = cache/binding['word_sha256']
        stages = BN.read(base/'STEPS.json')
        need([s['step'] for s in stages] == ['native','ledgers','local-replay','wrappers','phases']
             and all(s['exit_code'] == 0 for s in stages), 'five native stages')
        local = base/'local'
        canonical = BN.read(local/'CANONICAL-WORD.json.gz')
        phase = BN.read(local/'CLIFFORD-REVIEW.json')
        need(phase['status'] == 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES'
             and phase['canonical_word_sha256'] == BN.digest(local/'CANONICAL-WORD.json.gz')
             and phase['warp_recipes_rank_zero'] and phase['warp_recipes_equal_exact_512_column_product']
             and phase['all_child_equalities_include_global_phase'], 'actual native phase and warp proof')
        need(BN.read(local/'WRAPPER-CHECKS.json')['status'] == 'PASS_RESIDUAL_WRAPPERS_ARE_EXACT', 'actual residual wrappers')
        programs = BN.read(local/'LOCAL-PROGRAMS.json.gz')
        registry[pid] = {
            'v': canonical['v'], 'h': canonical['h'], 'R': canonical['R'],
            'canonical_word_sha256': BN.digest(local/'CANONICAL-WORD.json.gz'),
            'local_programs_sha256': BN.digest(local/'LOCAL-PROGRAMS.json.gz'),
            'local_programs': programs,
            'local_program_checks': BN.read(local/'LOCAL-CHECKS.json'),
            'exact_local_clifford_recipe_sha256': BN.digest(local/'CLIFFORD-RECIPES.json'),
            'residual_adapter_sha256': BN.digest(local/'RESIDUAL-ADAPTERS.json'),
        }
        directories[pid] = local
        artifacts[pid] = {name: BN.digest(local/name) for name in (
            'CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json',
            'INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-REVIEW.json','WRAPPER-CHECKS.json')}
    endpoints, localbits = BN.certify_providers(registry, directories)
    need(localbits == 70, 'exact actual local maximum')
    # Semantic faults exercise the actual new provider, independently of its
    # digest checks. These do not replace the full admission mutation suite.
    events = registry['gauge44']['local_programs']['forward']
    controls = []

    def reject(name, altered):
        try:
            BN.replay_endpoint(altered,112,408,False)
        except (AssertionError, ValueError, KeyError):
            controls.append(name)
        else:
            raise ValueError('accepted semantic fault: ' + name)

    terminal_clear = max(i for i,e in enumerate(events)
                         if e[0] == 'scalar' and e[1][0] == 'clear' and e[1][1][0] == 'C')
    reject('omitted_terminal_centre_clear', events[:terminal_clear]+events[terminal_clear+1:])
    release = max(i for i,e in enumerate(events) if e[0] == 'zero_buffer' and e[1] == 'free')
    reject('omitted_private_buffer_release', events[:release]+events[release+1:])
    reject('helper_to_data_leak', events+[['scalar',['add',['L',112],['L',224],1,1]]])
    changed = copy.deepcopy(events)
    target_add = max(i for i,e in enumerate(changed)
                     if e[0] == 'scalar' and e[1][0] == 'add' and e[1][1][0] == 'L'
                     and 112 <= e[1][1][1] < 224)
    changed[target_add][1][3] *= -1
    reject('wrong_final_target_coefficient', changed)
    result = {
        'status': 'PASS_PR2833_ACTUAL_BLOCK_NORM_PROVIDER_PREMISES',
        'source_head': SOURCE_HEAD, 'source_manifest_sha256': SOURCE_MANIFEST,
        'blocknorm_checker_sha256': BN.digest(HERE/'blocknorm_certificate.py'),
        'actual_local_prefix_bits': localbits, 'endpoint_replay': endpoints,
        'native_artifacts_sha256': artifacts, 'semantic_faults_rejected': controls,
        'scope': 'Actual provider prerequisites only. Full owners, within-replica depth, precision invoice and outer release remain separately required.',
    }
    need(not args.out.exists(), 'fresh output')
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(result['status'], 'providers=2 orientations=4 columns=632 controls='+str(len(controls)))


if __name__ == '__main__':
    main()
