"""Exercise content-portable promotion gates without changing frozen sources.

Prepared with OpenAI Codex assistance; Apache-2.0. Real constructors accept
recompressed inputs and reject altered inputs/recipes. Their shared output
gate accepts alternate compression and rejects altered mathematical payloads.
"""
import argparse
import gzip
import json
import platform
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

from promotion_identity import PINS, SOURCE_CONTENT_SHA256, admitted_output, digest

if not __debug__:
    raise RuntimeError('Assertions required; refusing optimized verification')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert not args.out.exists()
    root = Path(__file__).resolve().parents[1]
    code = root/'code'
    gk = root/'vendor/pr558/vendor/pr552/complex-local/static44/gk'
    payload = gzip.decompress(args.source.read_bytes())
    assert digest(payload) == SOURCE_CONTENT_SHA256
    args.out.parent.mkdir(parents=True, exist_ok=True)
    controls = []
    with tempfile.TemporaryDirectory(prefix='promotion-identity-', dir=args.out.parent) as td:
        scratch = Path(td)
        for kind, constructor, recipe, gk_option in (
            ('eight', code/'promote_eight_portable.py', root/'vendor/pr558/data/PROMOTION.json', '--gk'),
            ('four', code/'build_four_portable.py', root/'data/FROZEN-FOUR-PROMOTION.json', '--gk-dir'),
        ):
            work = scratch/kind
            work.mkdir()
            source = work/'recompressed.json.gz'
            source.write_bytes(gzip.compress(payload, compresslevel=1, mtime=123456789))
            assert digest(source.read_bytes()) != PINS[kind]['source_sha256']
            assert gzip.decompress(source.read_bytes()) == payload

            def run(name, inp, rec, accept, error=None):
                out = work/name
                result = subprocess.run(
                    [sys.executable, '-B', str(code/'run_portable.py'), str(constructor),
                     '--input', str(inp), '--recipe', str(rec), gk_option, str(gk), '--out', str(out)],
                    capture_output=True, text=True, encoding='utf-8')
                if accept:
                    assert result.returncode == 0, result.stdout + result.stderr
                else:
                    assert result.returncode != 0 and error in result.stderr, result.stdout + result.stderr
                    assert not out.exists(), 'rejected input emitted an output directory'
                controls.append(dict(kind=kind, name=name, accepted=accept))
                return out

            out = run('recompressed_input', source, recipe, True)
            encoded = (out/'FULL-WORD.json.gz').read_bytes()
            output_payload = admitted_output(kind, encoded)
            alternate = gzip.compress(output_payload, compresslevel=1, mtime=123456789)
            assert digest(alternate) != digest(encoded)
            assert admitted_output(kind, alternate) == output_payload
            controls.append(dict(kind=kind, name='recompressed_output', accepted=True))

            changed = json.loads(payload)
            changed['B'][0][3] = -changed['B'][0][3]
            mutant = work/'changed-input.json.gz'
            mutant.write_bytes(gzip.compress(json.dumps(changed, sort_keys=True, separators=(',', ':')).encode(), mtime=0))
            run('changed_input_payload', mutant, recipe, False, 'changed promotion input payload')

            changed_recipe = json.loads(recipe.read_bytes())
            changed_recipe['changes'][0]['gates'] += 1
            changed_recipe['source_sha256'] = digest(source.read_bytes())
            mutant_recipe = work/'changed-recipe.json'
            mutant_recipe.write_text(json.dumps(changed_recipe, indent=2)+'\n', encoding='utf-8', newline='\n')
            run('changed_recipe_rebound_source', source, mutant_recipe, False, 'changed frozen promotion recipe')
            mutant_recipe.write_bytes(recipe.read_bytes()+b' ')
            run('changed_recipe_format', source, mutant_recipe, False, 'changed frozen promotion recipe')

            changed_output = json.loads(output_payload)
            changed_output['B'][0][3] = -changed_output['B'][0][3]
            mutant_output = gzip.compress(json.dumps(changed_output, sort_keys=True, separators=(',', ':')).encode(), mtime=0)
            try:
                admitted_output(kind, mutant_output)
            except AssertionError as exc:
                assert 'changed promotion output payload' in str(exc)
            else:
                raise AssertionError('changed output payload admitted')
            controls.append(dict(kind=kind, name='changed_output_payload', accepted=False))

    counts = dict(recompression_accepted=sum(x['accepted'] for x in controls),
                  mutations_rejected=sum(not x['accepted'] for x in controls))
    assert counts == dict(recompression_accepted=4, mutations_rejected=8)
    result = dict(status='PASS_PORTABLE_PROMOTION_CONTENT_AND_RECIPE_CONTROLS',
                  counts=counts, controls=controls, source_content_sha256=SOURCE_CONTENT_SHA256,
                  original_recipe_pins=PINS,
                  runtime=dict(python=sys.version, platform=platform.platform(),
                               zlib_version=zlib.ZLIB_VERSION, zlib_runtime_version=zlib.ZLIB_RUNTIME_VERSION),
                  scope='Tests exactly the input/recipe and output gates used by both real constructors; full scalar, native-frame, phase and global admission remain separate replay stages.')
    args.out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(result['status'], counts)


if __name__ == '__main__':
    main()
