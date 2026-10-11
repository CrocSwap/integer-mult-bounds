#!/usr/bin/env python3
"""Rebuild the exact PR325 source twice, then PR346 Design T and twins.
OpenAI Codex-assisted integration; upstream authors and licenses are retained.
"""
import sys
if not __debug__:raise SystemExit('Assertions must remain enabled; refusing optimization')
sys.dont_write_bytecode = True
import argparse, gzip, hashlib, json, os, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text())
BASE_WORD = 'f1933dbf6f82303bb0cc6e42d4e292a652d99fb44286648452db374178e60c6f'
FINAL_WORD = 'c6a9311acfcf85f4a5775ed0187e31f84531614bb08434ef887ae1e63dda99c4'

def check_bytes(pinned, generated, receipt):
    assert set(receipt) == {'249-records.bin', '249-states.json', 'frames.json'}
    names = {'249-records.bin': 'BASE-RECORDS.bin.gz', '249-states.json': 'BASE-states.json.gz', 'frames.json': 'BASE-frames.json.gz'}
    for name, row in receipt.items():
        old = pinned/names[name]
        new = generated/name
        assert sha(old) == row['pinned_compressed_sha256']
        assert sha(new) == row['regenerated_sha256']
        expanded = gzip.decompress(old.read_bytes())
        assert expanded == new.read_bytes()
        assert hashlib.sha256(expanded).hexdigest() == row['expanded_sha256']

def run(out, cxx, boost):
    out = Path(out).resolve()
    assert out.exists() and not (out/'source-regeneration').exists()
    work = out/'source-regeneration'; work.mkdir()
    upstream = ROOT/'vendor/pr346'; code = upstream/'code'; data = upstream/'data/bit'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    py = [sys.executable, '-B']
    def launch(label, argv):
        with (out/'logs'/(label+'.log')).open('w') as log:
            subprocess.run(list(map(str, argv)), check=True, cwd=out, env=env, stdout=log, stderr=subprocess.STDOUT)
    reports = []
    for round in range(2):
        generated = work/f'round{round}'
        launch(f'base-export-{round}', py+[code/'export_p10.py', ROOT/'vendor/predecessor', generated])
        rows = {}
        for old, new in [('BASE-RECORDS.bin.gz','249-records.bin'), ('BASE-states.json.gz','249-states.json'), ('BASE-frames.json.gz','frames.json')]:
            expanded = gzip.decompress((data/old).read_bytes())
            rows[new] = dict(pinned_compressed_sha256=sha(data/old), regenerated_sha256=sha(generated/new), expanded_sha256=hashlib.sha256(expanded).hexdigest())
        check_bytes(data, generated, rows)
        reports.append(rows)
    assert reports[0] == reports[1] and sha(work/'round1/249-records.bin') == BASE_WORD
    assert gzip.decompress((out/'predecessor/records.bin.gz').read_bytes()) == (work/'round1/249-records.bin').read_bytes()
    controls = []
    def reject(label, rows):
        try: check_bytes(data, work/'round1', rows)
        except AssertionError: controls.append(label)
        else: raise AssertionError('bad binding accepted: '+label)
    for name in reports[1]:
        for key in reports[1][name]:
            rows = json.loads(json.dumps(reports[1])); rows[name][key]='0'*64
            reject(name+':'+key, rows)
    rows = dict(reports[1]); rows.pop('frames.json'); reject('missing source file', rows)
    rows = dict(reports[1]); rows['extra']={}; reject('extra source file', rows)
    report = dict(status='PASS_TWO_BYTE_EXACT_PR325_BASE_REGENERATIONS', rounds=2, files=reports[1], source_manifest_sha256=sha(ROOT/'vendor/predecessor/MANIFEST.json'), exporter_sha256=sha(code/'export_p10.py'), negative_controls=controls, source_word_sha256=BASE_WORD)
    (work/'REGENERATION.json').write_text(json.dumps(report, sort_keys=True, indent=2)+'\n')
    w = out/'design'; (w/'eval').mkdir(parents=True); (w/'agentA/T').mkdir(parents=True); shutil.copytree(work/'round1', w/'snap')
    shutil.copyfile(code/'pricing/cost.py', w/'eval/cost.py')
    shutil.copyfile(code/'builders/decomp.py', w/'agentA/decomp.py')
    env.update(W3WORK=str(w), W3LABELS=str(data/'labels.json'), PR315=str(code/'pricing'))
    (w/'T').mkdir(); (w/'TT').mkdir()
    compile_args = [cxx,'-O2','-std=c++17','-DHDIM=20','-I',ROOT/'code/portable-include','-I',code/'checkers']
    if boost: compile_args += ['-I',Path(boost).resolve()]
    launch('compile-design-check', compile_args+[code/'checkers/verifyT.cpp','-o',out/'bin/verify-design'])
    for script, args in [('interface',[]),('gather',[]),('build_v5',[w/'T']),('addcomp',[w/'T']),('twin',[w/'T',w/'TT'])]:
        if script=='addcomp':launch('derive-design-compensation', [out/'bin/verify-design',w/'T',w/'T/resid.txt'])
        launch('design-'+script, py+[code/'builders'/(script+'.py')]+args)
    final = w/'TT'
    assert sha(final/'249-records.bin') == FINAL_WORD
    assert (final/'249-records.bin').read_bytes() == gzip.decompress((data/'FINAL-RECORDS.bin.gz').read_bytes())
    launch('check-design-word', [out/'bin/verify-design',final])
    launch('compact-dormant-helpers', py+[ROOT/'code/compact.py','--output',out,'--base',work/'round1','--final',final,'--expected-word',FINAL_WORD])
    c = read(out/'COMPACTION.json')
    assert c['deleted_count']==480 and c['inverse_event_relabeling_byte_exact']
    assert c['compacted_word_sha256']=='05df0a39669bb077a9a2fa527904023a5a9da18cf644e06429d44f2a7ea92603'
    print('PASS exact regenerated source, Design T/twins and dormant compaction', flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output');p.add_argument('--cxx',default='c++');p.add_argument('--boost-include');a=p.parse_args();run(a.output,a.cxx,a.boost_include)
