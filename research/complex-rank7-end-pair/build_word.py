"""Apply the pinned twelve-frame recipe to the retained PR869 U8 word.

Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


BASE_SHA = '090fd574747fbf9628e70cb9beb792732914cfa52e1df147579fe4dbccc68c5a'
WORD_SHA = '096ed4abee4bb02c0d6f03bb8191510e57f6b1fcd34e8644f4fd336254e46411'
RECIPE = Path(__file__).resolve().parent / 'data/END-RECIPE.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def build(source, recipe):
    raw = gzip.decompress(source.read_bytes())
    require(hashlib.sha256(raw).hexdigest() == recipe['input_sha256'] == BASE_SHA,
            'baseline content pin')
    require(recipe['schema'] == 1, 'recipe schema')
    word = json.loads(raw)
    require([q for q, _, _ in recipe['ends']] == [588, 589], 'end sites')
    require([i for i, _, _ in recipe['B_frames']] ==
            [1018, 1019, 1050, 1051, 1130, 1131, 1162, 1163], 'B-frame sites')
    require([i for i, _, _, _ in recipe['early_cleanup']] == [148, 149], 'tail sites')
    for q, old, new in recipe['ends']:
        require(word['helper_final'][str(q)] == old, 'old helper end')
        word['helper_final'][str(q)] = new
    for index, old, new in recipe['B_frames']:
        require(word['B'][index][-1] == old, 'old B frame')
        word['B'][index][-1] = new
    for index, cleanup_index, old, new in recipe['early_cleanup']:
        require(word['early_cleanup'][index] == [cleanup_index, old], 'old tail frame')
        word['early_cleanup'][index][1] = new
    for key in ('local_profile', 'local_rank_mass', 'width_inventory'):
        word['report'][key] = recipe['expected'][key]
    result = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
    require(hashlib.sha256(result).hexdigest() == recipe['expected']['output_sha256'] == WORD_SHA,
            'constructed word content pin')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--recipe', type=Path, default=RECIPE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    recipe = json.loads(args.recipe.read_text(encoding='utf-8'))
    raw = build(args.input, recipe)
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    # Python versions differ in the gzip OS header byte.
    compressed = compressed[:9] + b'\xff' + compressed[10:]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(compressed)
    print(json.dumps(dict(status='PASS_PINNED_TWELVE_FRAME_CONSTRUCTION',
                          content_sha256=WORD_SHA, compressed_sha256=hashlib.sha256(compressed).hexdigest(),
                          changed_annotations=12)), flush=True)


if __name__ == '__main__':
    main()
