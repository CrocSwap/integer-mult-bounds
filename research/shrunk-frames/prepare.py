#!/usr/bin/env python3
"""Capture, audit, and compose the pinned PR #125 finite parent word.

This authoring/checking entry point runs the existing compiler once in memory,
checks its frozen parent profile and reflection receipt, then builds the
terminal-elided candidate. ``--write`` is an explicit artifact regeneration
operation; the default mode is read-only.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

import reflection_audit
from terminal_elision import build, canonical_word_bytes, parent_word_from_capture, write_outputs


def normalized_json(value):
    return json.loads(json.dumps(value, sort_keys=True))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true',
                        help='Regenerate the frozen candidate profile, receipt, and selection')
    parser.add_argument('--parent-word', type=Path,
                        help='Write the transient canonical parent word for the independent audit')
    args = parser.parse_args()

    source = HERE / 'complex_deferred.py'
    state = reflection_audit.capture(source)
    parent = state['out']
    frozen_parent = json.loads((HERE / 'controls/pr125-complex-profile.json').read_text())
    require(normalized_json(parent) == frozen_parent,
            'captured parent profile differs from the pinned PR #125 control')

    parent_receipt = reflection_audit.audit(state)
    parent_receipt['source_sha256'] = sha256(source.read_bytes()).hexdigest()
    parent_receipt['audit_sha256'] = sha256((HERE / 'reflection_audit.py').read_bytes()).hexdigest()
    frozen_audit = json.loads((HERE / 'reflection-audit.json').read_text())
    require(normalized_json(parent_receipt) == frozen_audit,
            'independent parent reflection receipt changed')

    word = parent_word_from_capture(state)
    word_bytes = canonical_word_bytes(word)
    word_sha256 = sha256(word_bytes).hexdigest()
    if args.parent_word:
        args.parent_word.parent.mkdir(parents=True, exist_ok=True)
        args.parent_word.write_bytes(word_bytes)

    profile, receipt, selection = build(word, parent, word_sha256)
    if args.write:
        write_outputs(HERE, profile, receipt, selection)
    else:
        expected_profile = json.loads((HERE / 'complex-profile.json').read_text())
        require(normalized_json(profile) == expected_profile,
                'generated terminal-elided profile differs from frozen output')
        expected_receipt = json.loads(gzip.decompress((HERE / 'terminal-elision.json.gz').read_bytes()))
        require(normalized_json(receipt) == expected_receipt,
                'generated terminal-elision word differs from frozen receipt')
        expected_selection = json.loads((HERE / 'terminal-selection.json').read_text())
        require(normalized_json(selection) == expected_selection,
                'generated simultaneous target schedule differs from frozen receipt')
    print('PASS captured PR #125 parent; 381 terminal roles, %d direct updates; %s mode' %
          (profile['terminal_direct_updates'], 'wrote' if args.write else 'matched frozen'))


if __name__ == '__main__':
    main()
