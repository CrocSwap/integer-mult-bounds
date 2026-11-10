"""Negative controls for the two source-holder fusions, judged by the unchanged #645 audit_local.py.

For each site the word is mutated five ways: drop the FULL-cleanup restore, drop the donation, flip the donation sign,
keep the fused target read, and drop both donation and restore. Every mutant must be rejected and the honest word must
pass. Sites (gate positions and contents) are pinned in CONTROL-SITES.json.
usage: python -B controls.py --word FULL-WORD.json.gz --out FUSION-CONTROLS.json"""
import argparse, copy, gzip, hashlib, json, subprocess, sys, tempfile
from pathlib import Path
P = Path(__file__).resolve().parent; ROOT = P.parents[1]; AUD = ROOT / 'research/gauge44-slots/independent/audit_local.py'
def audit(w, d):
    p = Path(d) / 'W.json.gz'; p.write_bytes(gzip.compress(json.dumps(w, separators=(',', ':')).encode(), mtime=0))
    r = subprocess.run([sys.executable, '-B', str(AUD), '--word', str(p), '--output', str(Path(d) / 'A.json')], capture_output=True, text=True)
    lines = (r.stdout + r.stderr).strip().splitlines(); return r.returncode == 0, (lines[-1] if lines else '')[-160:]
def drop_cleanup(w, ci):
    w['cleanup'] = w['cleanup'][:ci] + w['cleanup'][ci + 1:]; w['early_cleanup'] = [[i - 1 if i > ci else i, U] for i, U in w['early_cleanup']]
def main():
    global AUD
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--word', type=Path, required=True); ap.add_argument('--out', type=Path, required=True); ap.add_argument('--main', type=Path, required=True); ap.add_argument('--sites', type=Path, required=True); a = ap.parse_args(); AUD = a.main/'research/gauge44-slots/independent/audit_local.py'
    raw = gzip.decompress(a.word.read_bytes()); spec = json.loads(a.sites.read_text())
    assert hashlib.sha256(raw).hexdigest() == spec['word_content_sha256'], 'word pin'
    w0 = json.loads(raw); d = tempfile.mkdtemp(prefix='fusion-controls-'); ok, msg = audit(w0, d); assert ok, ('honest word rejected', msg)
    rejected, accepted = [], []
    for s in spec['sites']:
        di, ci = s['donation_B_index'], s['restore_cleanup_index']
        assert w0['B'][di][:5] == s['donation'] and w0['cleanup'][ci][:5] == s['restore'], ('site pin', s['t'])
        muts = {}
        w = copy.deepcopy(w0); drop_cleanup(w, ci); muts['drop_restore'] = w
        w = copy.deepcopy(w0); del w['B'][di]; muts['drop_donation'] = w
        w = copy.deepcopy(w0); g = w['B'][di]; w['B'][di] = g[:3] + [-g[3]] + g[4:]; muts['flip_donation_sign'] = w
        w = copy.deepcopy(w0); w['B'].insert(s['fused_read_B_position'], list(s['fused_read'])); muts['keep_fused_read'] = w
        w = copy.deepcopy(w0); drop_cleanup(w, ci); del w['B'][di]; muts['drop_donation_and_restore'] = w
        for name, w in muts.items():
            ok, msg = audit(w, d); (accepted if ok else rejected).append(dict(control=f"{name}@{s['t']}", reason=msg)); print(('ACCEPTED ' if ok else 'rejected ') + f"{name}@{s['t']}", msg[-90:], flush=True)
    a.out.write_text(json.dumps(dict(status='PASS_FUSION_NEGATIVE_CONTROLS' if not accepted else 'FAIL', honest='PASS', rejected=rejected, accepted=accepted), indent=2) + '\n')
    assert not accepted and len(rejected) == 10, 'every mutant must be rejected'
    print('PASS controls: honest word accepted,', len(rejected), 'mutants rejected')
if __name__ == '__main__':
    main()
