# Adapted from PR569 audit_frame_promotions.py; bind PR568 multicold source and omission receipts. Apache-2.0.
#!/usr/bin/env python3
"""Independently bind frame-only changes to fresh scalar omission controls.

Prepared with OpenAI Codex assistance. Apache-2.0. This imports neither the
constructor nor its graph. Native frame and phase checks remain separate.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(source, word, recipes):
    require(source.keys() == word.keys(), 'Changed word schema')
    require(len(recipes) == 32 and len({r['pivot'] for r in recipes}) == 32, 'Wrong promotion set')
    changed = 0
    for section in source:
        if section in ('A', 'cut', 'B', 'cleanup', 'precondition'):
            require(len(source[section]) == len(word[section]), 'Changed scalar length')
            for before, after in zip(source[section], word[section]):
                require(before[:-1] == after[:-1], 'Changed scalar operation/coefficient/order')
                changed += before[-1] != after[-1]
        elif section not in ('start_extra', 'report'):
            require(source[section] == word[section], 'Changed fixed word field: ' + section)
    entrances = copy.deepcopy(source['start_extra'])
    for recipe in recipes:
        key = str(recipe['pivot'])
        require(entrances[key] == recipe['old_frame'], 'Wrong old entrance')
        require(len(recipe['old_frame']) == 1 and len(recipe['new_frame']) == 2,
                'Wrong entrance rank change')
        entrances[key] = recipe['new_frame']
    require(word['start_extra'] == entrances, 'Changed entrance outside recipe')
    allowed = {'local_profile', 'local_rank_mass', 'entrance_rank', 'entering_helpers', 'width_inventory'}
    require(set(word['report']) - set(source['report']) <= allowed and set(source['report']) <= set(word['report']), 'Changed report schema')
    require(all(source['report'][key] == word['report'][key]
                for key in source['report'] if key not in allowed), 'Changed fixed report field')
    require(changed == 96, 'Wrong changed frame count')
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--recipes', type=Path, required=True)
    parser.add_argument('--controls', type=Path, required=True)
    parser.add_argument('--promotions', type=int, choices=(0, 4, 8), required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source, word, recipes = read(args.source), read(args.word), read(args.recipes)
    changed = check(source, word, recipes)
    control_paths = [args.controls / 'STATIC44-SCALAR-AUDIT.json', args.controls / 'MULTICOLD-OMISSION-CONTROLS.json']
    static, multi = map(read, control_paths)
    require(static['word_sha256'] == sha(args.source) and len(static['controls']) == 44 and
            all(v == 'REJECTED_OMITTED_KERNEL_CORRECTION' for v in static['controls'].values()),
            'Static44 controls do not bind source word')
    require(multi['word_sha256'] == sha(args.source) and len(multi['controls']) == 32 and
            all(c['forward_rejected'] and c['reflected_rejected'] for c in multi['controls']),
            'Multicold controls do not bind source word')
    promoted = args.controls / 'PROMOTED-SCALAR-AUDIT.json'
    c = read(promoted)
    require(c['word_sha256'] == sha(args.source) and len(c['controls']) == 8 and
            all(v == 'REJECTED_OMITTED_PROMOTED_POSTCENTER_KERNEL_CORRECTION' for v in c['controls'].values()),
            'Rank-five controls do not bind source word')
    control_paths.append(promoted)
    # The source has passed the complete PR568 replay; bind its raw content to
    # the immutable constructor recipe before transferring frame-only evidence.
    pinned_content = '055c0fb41d8b0d506674f62d0227833a74eabd19a022a1dfeb72c3952b7a030f'
    require(hashlib.sha256(gzip.decompress(args.source.read_bytes())).hexdigest() == pinned_content,
            'Wrong immutable PR568 eight-cold source')
    rejected = []
    for name in ('scalar_coefficient', 'entrance_outside_recipe', 'cleanup_order'):
        mutant = copy.deepcopy(word)
        if name == 'scalar_coefficient':
            event = next(e for e in mutant['B'] if e[0] == 'add')
            event[3] += 1
        elif name == 'entrance_outside_recipe':
            mutant['start_extra']['224'] = [1]
        else:
            mutant['cleanup'].reverse()
        try:
            check(source, mutant, recipes)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('Accepted mutation: ' + name)
    result = dict(status='PASS_INDEPENDENT_FRAME_ONLY_PROMOTIONS',
                  source_sha256=sha(args.source), word_sha256=sha(args.word),
                  recipes_sha256=sha(args.recipes), auditor_sha256=sha(Path(__file__)),
                  changed_frames=changed, promotions=32, all_scalar_operations_identical=True,
                  omission_receipts={p.name: sha(p) for p in control_paths},
                  negative_controls_rejected=rejected,
                  scope='Scalar omission proofs transfer because every scalar operation, coefficient '
                        'and order is identical. Native frame legality, actual profiles, normalized '
                        'wrappers, full phases and global admission require separate fresh replay.')
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
