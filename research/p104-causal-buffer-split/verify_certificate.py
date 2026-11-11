"""Reconstruct the exact source, timed certificate and emitted candidate.
Prepared for dillona with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
import argparse, gzip, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import HERE, sources, read, canonical, need
from certificate import observe, check, controls
from construct import construct

def run():
    need(__debug__, 'Assertions are proof obligations')
    with sources() as (_, _, _, _, _, word):
        hit, paths = read(HERE/'WITNESS.json'), read(HERE/'PATHS.json')
        cache = observe(word, hit)
        result = check(hit, cache)
        candidate = construct(word, hit, paths)
        need(canonical(candidate) == gzip.decompress((HERE/'WORD.json.gz').read_bytes()), 'Every reconstructed candidate byte')
        result.update(source_sha256=sha256(canonical(word)).hexdigest(),
                      candidate_sha256=sha256(canonical(candidate)).hexdigest(),
                      controls=controls(word, hit, paths, cache),
                      neutral_paths=len(paths), paid_paths=1)
        return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = run()
    if args.out:
        with args.out.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        need(result == read(HERE/'CERTIFICATE.json'), 'Every frozen temporal certificate field')
    print(result['status'], flush=True)
