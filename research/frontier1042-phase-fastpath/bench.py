#!/usr/bin/env python3
"""Time phase-recipe engines on the three archived frontier1042 canonical words (descriptive only).

Usage: bench.py OUT_DIR ENGINES, with OUT_DIR fresh and ENGINES a comma list of
sparse, dense, reference (selected-replay-fastpath/run.py), pinned (the pinned phases_full.py via the
pinned run_portable.py, as the replay runs it) and par-reference / par-dense662
(phase-recipes-parallel/phases_parallel.py --jobs N). Every run must reproduce the pinned bytes.
"""
import hashlib, json, os, platform, resource, shutil, subprocess, sys, tarfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / 'research/community-frontier1042-audit/selected-replay.tar.gz'
PINS = dict(cells='research/gauge44-leaver8/construction/leaver/LEAVER-PINS-k8.json',
            chain='research/gauge44-leaver8/construction/leaver/CHAIN-PINS-k8.json',
            slots='research/gauge44-slots/construction/slots/SLOT-PINS-k8.json')
SRC = ROOT / 'research/complex-k492-owner-repair/vendor/multicold'
P = SRC / 'vendor/pr558'
CLIF = P / 'vendor/pr552/complex-global/vendor531/vendor/clifford'


def main():
    out, engines = Path(sys.argv[1]).resolve(), sys.argv[2].split(',')
    jobs = sys.argv[3] if len(sys.argv) > 3 else str(os.cpu_count() or 1)
    assert not out.exists() and not sys.flags.optimize
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(SRC), GAIN_PR564_SOURCE=str(SRC))
    with tarfile.open(ARCHIVE) as tar:
        words = {}
        for st in PINS:
            words[st] = out / 'words' / st / 'CANONICAL-WORD.json.gz'
            words[st].parent.mkdir(parents=True)
            words[st].write_bytes(tar.extractfile(st + '/local/CANONICAL-WORD.json.gz').read())
    res = []
    for eng in engines:
        for st, word in words.items():
            pin = json.loads((ROOT / PINS[st]).read_text())['clifford_recipes_sha256']
            d = out / 'runs' / eng / st
            if eng in ('sparse', 'dense', 'reference'):
                cmd = [sys.executable, '-B', str(ROOT / 'research/selected-replay-fastpath/run.py'),
                       '--word', str(word), '--out', str(d), '--engine', eng]
            else:
                d.mkdir(parents=True)
                shutil.copy(word, d / 'CANONICAL-WORD.json.gz')
                if eng == 'pinned':
                    cmd = [sys.executable, '-B', str(SRC / 'code/run_portable.py'), str(P / 'code/phases_full.py'),
                           str(d), str(CLIF)]
                else:
                    cmd = [sys.executable, '-B', str(ROOT / 'research/phase-recipes-parallel/phases_parallel.py'),
                           str(d), str(CLIF), '--jobs', jobs, '--engine', eng.split('-', 1)[1]]
            ru = resource.getrusage(resource.RUSAGE_CHILDREN)
            t = time.monotonic()
            p = subprocess.run(cmd, env=env, capture_output=True, text=True)
            dt = time.monotonic() - t
            ru2 = resource.getrusage(resource.RUSAGE_CHILDREN)
            cpu = ru2.ru_utime - ru.ru_utime + ru2.ru_stime - ru.ru_stime
            rp = d / 'CLIFFORD-RECIPES.json'
            got = hashlib.sha256(rp.read_bytes()).hexdigest() if rp.exists() else None
            r = dict(engine=eng, stage=st, exit_code=p.returncode, wall_seconds=round(dt, 2), cpu_seconds=round(cpu, 2),
                     recipe_sha256=got, equals_pin=got == pin)
            print(json.dumps(r), flush=True)
            res.append(r)
            assert p.returncode == 0 and got == pin, (eng, st, p.stderr[-500:])
    (out / 'BENCHMARK.json').write_text(json.dumps(dict(
        python=sys.version.split()[0], platform=platform.platform(), machine=platform.machine(),
        cpu_count=os.cpu_count(), jobs=int(jobs), archive=str(ARCHIVE.relative_to(ROOT)),
        note='Shared host, not isolated; descriptive timings only.', results=res), indent=1) + '\n')


if __name__ == '__main__':
    main()
