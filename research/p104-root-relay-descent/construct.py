"""Regenerate WORD.json.gz from PR6030's pinned word and the explicit edit list in EDIT.json.gz.  Apache-2.0.

Standard library only; no solver and no dependence on any other tooling.  The edit list is data:
  initial / final : {register: [old, new]} changes to the public boundary charts,
  program         : the new event list as segments; [a, b] copies PR6030's program[a:b] unchanged and any
                    other entry is a literal event.
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
Predecessor credit (PR6030, PR5827 aliromman and its lineage): see README.md.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip, json, sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def payload(value):
    """The complete serialized word, independent of its gzip container."""
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def matches_shipped(value, compressed):
    """Compare every payload byte; gzip metadata and compression may vary.

    Immutable source archives keep their separate exact-byte authentication in
    sources.py. This predicate is only for a regenerated output artifact.
    """
    return gzip.decompress(compressed) == payload(value)


def dump(value):
    return gzip.compress(payload(value), mtime=0)


def construct(base, edit):
    """Return the edited word.  `base` is PR6030's WORD.json.gz payload, `edit` is EDIT.json.gz."""
    need(digest(base) == edit['base_word_sha256'], 'Edit applies to the pinned PR6030 word')
    word = deepcopy(base)
    for key in ('initial', 'final'):
        for register, (old, new) in edit[key].items():
            need(base[key][int(register)] == old, 'Declared old boundary value: ' + key + ' ' + register)
            word[key][int(register)] = new
    program, source = [], base['program']
    for step in edit['program']:
        if isinstance(step[0], int):
            a, b = step
            need(0 <= a < b <= len(source), 'Copy segment inside the base program')
            program.extend(deepcopy(source[a:b]))
        else:
            program.append(list(step))
    word['program'] = program
    need(word.keys() == base.keys(), 'Same word fields')
    for key in base:
        if key not in ('program', 'initial', 'final'):
            need(word[key] == base[key], 'Unchanged word field: ' + key)
    removed = Counter(e[0] for e in source) - Counter(e[0] for e in program)
    added = Counter(e[0] for e in program) - Counter(e[0] for e in source)
    need({'added': dict(added), 'removed': dict(removed)} == edit['operation_delta'], 'Declared operation delta')
    return word


def pinned_base():
    """PR6030's word, authenticated against SOURCES.json (digest-checked again in construct)."""
    sys.path.insert(0, str(HERE))
    from sources import base_word
    return base_word()


if __name__ == '__main__':
    word = construct(pinned_base(), read(HERE / 'EDIT.json.gz'))
    if '--write' in sys.argv:
        (HERE / 'WORD.json.gz').write_bytes(dump(word))
    print('constructed', len(word['program']), 'events,', word['public'], 'public',
          '(matches shipped WORD payload)' if matches_shipped(word, (HERE / 'WORD.json.gz').read_bytes()) else '(differs from shipped payload)')
