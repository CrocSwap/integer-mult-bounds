"""Optional cross-check of the frame model against the pinned independent auditor.

Draws random legal frame reassignments of the X4 word from the model's domains (keeping
the start-of-B centre equality exact), writes each into a copy of the word together with
the paid profile the model predicts, and runs research/gauge44-frames-x/independent/
audit_local.py unchanged on it. The auditor replays the exact scalar map in both
orientations and recomputes every frame chain, centre/target level and low-end cone, so
each accepted sample confirms both legality and the model's cost accounting. Not part of
the proof; standard library only.
"""
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import random
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model as M    # noqa: E402
import verify as V   # noqa: E402

AUDIT = 'research/gauge44-frames-x/independent/audit_local.py'
AUDIT_SHA256 = '03afcfc9da428b3f6edac81c1fee7f277ab81b64998efae78380b63498dec6cd'


def audit_module(repo):
    path = repo / AUDIT
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = json.loads((repo / 'research/gauge44-frames-x/MANIFEST.json').read_text())
    V.require(digest == AUDIT_SHA256 and AUDIT_SHA256 in V.values_of(manifest, 'independent/audit_local.py'),
              'pinned auditor')
    spec = importlib.util.spec_from_file_location('x4fb_audit_local', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, digest


def legal(model, X):
    """Monotone everywhere, with no climb into a start-of-B pin (the contract's equality)."""
    try:
        model.profile(X)
    except ValueError:
        return False
    for q, ch in model.chains.items():
        for k, node in enumerate(ch):
            if node[0] == 'P' and model.frame_of(ch[k - 1], X) != model.fixed_frames[node]:
                return False
    return True


def sample(model, rng, moves, nodes):
    X = model.baseline()
    changed = 0
    for _ in range(moves * 20):
        node = rng.choice(nodes)
        old = X[node]
        X[node] = rng.choice(model.domain[node])
        if X[node] != old and legal(model, X):
            changed += 1
            if changed == moves:
                break
        else:
            X[node] = old
    return X, changed


def write_word_unchecked(word, model, X, path, profile):
    w = json.loads(json.dumps(word))
    nA, nB = model.nA, model.nB
    for (kind, i), Fr in X.items():
        if i < nA:
            w['A'][i][-1] = list(Fr)
        elif i < nA + nB:
            w['B'][i - nA][-1] = list(Fr)
        else:
            w['early_cleanup'][i - nA - nB][1] = list(Fr)
    w['report']['local_profile'] = {str(d): c for d, c in profile.items()}
    path.write_bytes(gzip.compress(json.dumps(w).encode(), mtime=0))
    return w['report']['local_profile']


def write_word(word, model, X, path):
    return write_word_unchecked(word, model, X, path, model.profile(X))


def refused(audit, path, out):
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            audit.run(path, out)
    except RuntimeError:
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--samples', type=int, default=6)
    parser.add_argument('--moves', type=int, default=25)
    parser.add_argument('--seed', type=int, default=28)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    word, source = V.load_selected_word(V.REPO)
    model = M.Model(word)
    audit, digest = audit_module(V.REPO)
    b = V.excluded_exponent(V.REPO)
    bounds = [V.charges(engine, b) for engine in V.load_engines(V.REPO).values()]
    base = model.profile(model.baseline())
    rng = random.Random(args.seed)
    comps = model.components()
    pools = [sorted(model.domain), sorted(max(comps, key=len))]
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for k in range(args.samples):
            X, changed = sample(model, rng, args.moves, pools[k % 2])
            path = Path(tmp) / f'sample{k}.json.gz'
            predicted = write_word(word, model, X, path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                audit.run(path, Path(tmp) / f'receipt{k}.json')
            receipt = json.loads((Path(tmp) / f'receipt{k}.json').read_text())
            ok = receipt['status'].startswith('PASS') and receipt['local_profile'] == predicted
            V.require(ok, 'auditor disagrees with the model on sample %d' % k)
            diff = {d: int(predicted.get(str(d), 0)) - base.get(d, 0) for d in V.RANKS}
            worse = any(diff.values()) and all(V.lower_value(diff, bd) > 0 for bd in bounds)
            V.require(worse or not any(diff.values()), 'sample is not costlier than the baseline at b_next')
            rows.append(dict(sample=k, pool='all free gates' if k % 2 == 0 else 'largest component',
                             frames_changed=changed, predicted_profile=predicted,
                             auditor_status=receipt['status'],
                             strictly_costlier_at_b_next=worse))
            print(rows[-1], flush=True)
        # Controls: the auditor must refuse a frame below its forward join and a wrong profile.
        controls = {}
        X = model.baseline()
        node = next(nd for nd in sorted(model.domain) if len(model.lo[nd]) > 0)
        X[node] = model.lo[node][1:]
        path = Path(tmp) / 'control-below-join.json.gz'
        write_word_unchecked(word, model, X, path, model.profile(model.baseline()))
        controls['frame_below_forward_join'] = refused(audit, path, Path(tmp) / 'c1.json')
        X, _ = sample(model, rng, args.moves, pools[0])
        while model.profile(X) == model.profile(model.baseline()):
            X, _ = sample(model, rng, args.moves, pools[0])
        path = Path(tmp) / 'control-wrong-profile.json.gz'
        write_word_unchecked(word, model, X, path, model.profile(model.baseline()))
        controls['baseline_profile_on_changed_frames'] = refused(audit, path, Path(tmp) / 'c2.json')
        V.require(all(controls.values()), 'auditor accepted a control')
    result = dict(status='PASS_AUDIT_LOCAL_CROSSCHECK', auditor=AUDIT, auditor_sha256=digest,
                  seed=args.seed, moves_per_sample=args.moves, samples=rows,
                  controls_refused_by_auditor=controls, word=source)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n', newline='\n')
    print(result['status'], len(rows))


if __name__ == '__main__':
    main()
