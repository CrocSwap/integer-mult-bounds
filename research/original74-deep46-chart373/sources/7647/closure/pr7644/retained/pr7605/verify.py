#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate the source closure and the exact application adaptation.

Ali Romman, with substantial OpenAI Codex assistance.
"""
import gzip
import hashlib
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
BUILD = runpy.run_path(str(HERE / 'build.py'))
require = BUILD['require']


def main():
    BUILD['authenticate']()
    changes = json.loads((HERE / 'APPLICATION-CHANGES.json').read_bytes())
    raw = (HERE / changes['source']).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == changes['source_sha256'], 'application source pin')
    text = raw.decode()
    for edit in changes['edits']:
        require(text.count(edit['before']) == edit['occurrences'], 'exact application adaptation count')
        text = text.replace(edit['before'], edit['after'])
    require(text.encode() == (HERE / 'application.py').read_bytes(), 'complete declared application changes')
    require(hashlib.sha256(text.encode()).hexdigest() == changes['adapted_sha256'], 'application result hash')
    word = BUILD['build_word']()
    require(json.loads(gzip.decompress((HERE / 'data/word.json.gz').read_bytes())) == word,
            'constructed word payload')
    require(json.loads((HERE / 'data/invoice-new.json').read_bytes()) == BUILD['invoice'](),
            'constructed full invoice')
    alternate = gzip.compress(json.dumps(word).encode(), compresslevel=1, mtime=123)
    require(alternate != (HERE / 'data/word.json.gz').read_bytes(), 'alternate gzip container')
    require(json.loads(gzip.decompress(alternate)) == word, 'gzip payload equality')
    print(json.dumps(dict(status='PASS_HELPER757_SOURCE_CLOSURE', retained_files=109,
                         application_edits=len(changes['edits']), gzip_payload_control=True)))


if __name__ == '__main__':
    main()
