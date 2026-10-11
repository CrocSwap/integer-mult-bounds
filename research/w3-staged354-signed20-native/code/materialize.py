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
FINAL_WORD = 'f5fca11b5855a5a575a9408b1cde69d152d03432ce3e8e375d6b20b39baf3434'

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
    upstream354=ROOT/'vendor/pr354'
    staged=out/'staged-regeneration'
    launch('regenerate-four-stages',py+[ROOT/'code/staged_export.py',ROOT/'vendor/pr329',staged,upstream354])
    rows={}
    for tag,snapshot in [('parity','00-parity'),('staged','04-sink')]:
        for name in ('249-records.bin','249-states.json','frames.json'):
            old=upstream354/'data'/tag/(name+'.gz');new=staged/snapshot/name
            raw=gzip.decompress(old.read_bytes());assert raw==new.read_bytes(),(tag,name)
            if tag=='parity':assert raw==(work/'round1'/name).read_bytes()
            rows[tag+'/'+name]=dict(pinned_compressed_sha256=sha(old),expanded_sha256=hashlib.sha256(raw).hexdigest(),regenerated_sha256=sha(new))
    rolemap=read(staged/'SOURCE-ROLE-MAP.json')
    assert len(rolemap['removed_original_positions'])==10 and len(rolemap['surviving_original_helper_positions'])==8090
    report=dict(status='PASS_REGENERATED_PR329_FOUR_STAGES_MATCH_PR354_EXACT_BYTES',files=rows,source329_manifest_sha256=sha(ROOT/'vendor/pr329/MANIFEST.json'),source354_manifest_sha256=sha(upstream354/'MANIFEST.sha256'),exporter_sha256=sha(ROOT/'code/staged_export.py'),source_role_map_sha256=sha(staged/'SOURCE-ROLE-MAP.json'),stages=['descent','target','restore','sink'])
    (staged/'REGENERATION.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    w=out/'design';w.mkdir()
    launch('design-T',py+[upstream354/'code/dt.py',staged/'04-sink',w/'T'])
    launch('design-completion',py+[upstream354/'code/comp.py',w/'T'])
    launch('design-twin',py+[upstream354/'code/twin.py',w/'T',w/'TT'])
    final=w/'TT';assert (final/'249-records.bin').read_bytes()==gzip.decompress((upstream354/'data/final/249-records.bin.gz').read_bytes())
    assert sha(final/'249-records.bin')==FINAL_WORD
    launch('check-design-word',py+[ROOT/'code/check354_scalar.py',upstream354/'code',final,out/'DESIGN-SCALAR.json'])
    launch('design-parity-control-T',py+[upstream354/'code/dt.py',staged/'00-parity',w/'T-control'])
    launch('design-parity-control-completion',py+[upstream354/'code/comp.py',w/'T-control'])
    launch('design-parity-control-twin',py+[upstream354/'code/twin.py',w/'T-control',w/'TT-control'])
    assert sha(w/'TT-control/249-records.bin')=='c6a9311acfcf85f4a5775ed0187e31f84531614bb08434ef887ae1e63dda99c4'
    (out/'PARITY-CONTROL.json').write_text(json.dumps(dict(status='PASS_PR354_REIMPLEMENTATION_REPRODUCES_PR346',word_sha256=sha(w/'TT-control/249-records.bin')),sort_keys=True,indent=2)+'\n')
    launch('compact-dormant-helpers',py+[ROOT/'code/compact.py','--output',out/'materialized','--base',work/'round1','--final',final,'--sinks',upstream354/'stages/sink-selection.json'])
    shutil.copy2(out/'materialized/COMPACTION.json',out/'COMPACTION.json')
    c=read(out/'COMPACTION.json')
    assert c['sink_roles_original']==rolemap['removed_original_positions']
    assert sorted(map(int,c['original_to_staged']))==list(range(1920))+rolemap['surviving_original_helper_positions']+[10020]
    assert len(c['deleted_dormant_staged'])==480 and c['inverse_event_relabeling_byte_exact']
    assert c['compacted_word_sha256']=='2aa5b4af88e4295588079cf951a5655bdff861588d39ba8af43c185ee93d14b6'
    print('PASS exact regenerated source, four stages, Design T/twins and dormant compaction',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output');p.add_argument('--cxx',default='c++');p.add_argument('--boost-include');a=p.parse_args();run(a.output,a.cxx,a.boost_include)
