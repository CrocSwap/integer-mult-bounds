"""Fast coherent hash/source check for the stopped duplicate-search audit."""
from pathlib import Path
from hashlib import sha1,sha256
import argparse,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def need(ok,message):
    if not ok:raise ValueError(message)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-manifest',action='store_true');args=ap.parse_args()
    pins=read(HERE/'SOURCES.json')
    for row in pins['files']:need(digest(HERE/'sources'/row['copy'])==row['sha256'],'Copied source '+row['copy'])
    upstream=read(HERE/'UPSTREAM.json');folder=HERE/'upstream/phase-rank-debt'
    need(upstream['commit']=='def829364e8e53a74eac7997b49b5366afd5bc29','Exact PR4696 head')
    for row in upstream['files']:
        raw=(HERE/row['copy']).read_bytes()
        need(sha256(raw).hexdigest()==row['sha256'],'Upstream SHA '+row['name'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['blob'],'Upstream Git blob '+row['name'])
    need((HERE/'sources/native-word.json.gz').read_bytes()==(folder/'inputs/round3-native.json.gz').read_bytes(),'Same actual source word')
    oldpins=read(folder/'SOURCES.json');pin=next(r for r in oldpins['files'] if r['path'].endswith('round3-native.json.gz'))
    need(digest(folder/'inputs/round3-native.json.gz')==pin['sha256'],'Exact upstream native pin')
    gate=read(HERE/'FULL-FORM-GATE.json')
    need(gate['script_sha256']==digest(HERE/'full_form_gate.py') and gate['sources_sha256']==digest(HERE/'SOURCES.json'),'Full-form source binding')
    need(gate['actual_components']==1067 and gate['original_residences']==4186,'Actual graph census')
    need([r['form_coordinates'] for r in gate['results']]==[10941,11229],'Full-form dimensions')
    for row in gate['results']:
        need(not row['useful_helper_roles'] and not row['witnesses'] and row['remaining_equations']==0,'No unpriced free helper gain')
        need(row['helper_queries']==80,'Every helper coefficient query')
    audit=read(HERE/'RANK-DEBT-AUDIT.json')
    need(audit['script_sha256']==digest(HERE/'rank_debt_audit.py'),'Independent audit source')
    need(audit['graph_gate_script_sha256']==digest(HERE/'full_form_gate.py'),'Actual graph source')
    need(audit['sources_sha256']==digest(HERE/'SOURCES.json') and audit['upstream_pins_sha256']==digest(HERE/'UPSTREAM.json'),'Audit input pins')
    need(audit['upstream_replay_stdout_sha256']==digest(HERE/'RANK-DEBT-REPLAY.log'),'Fresh upstream replay log')
    need(audit['upstream_verifier_exit_code']==0 and audit['upstream_sources_unchanged'],'Unchanged exact upstream replay')
    need(len(audit['orientations'])==2,'Both source words')
    for row in audit['orientations']:
        need(row['persistent_rank_telescopes']==632 and row['pointwise_fixed_helper_entrances']==408,'All physical paths')
        need(row['helper_rank_mass']==3471 and row['helper_jobs']==2208,'Actual helper invoice')
        need(row['helper_blocks_without_adapter_cuts']=={'0':19817,'1':2208},'No marker cuts needed')
        need(row['helper_adapter_markers']==0 and row['adapter_markers']==448,'Adapter owners')
        need(row['block_hypotheses_survive_no_inert_marker_freezes'],'Debt scope assessment')
    controls=read(HERE/'CONTROLS.json')
    need(controls['script_sha256']==digest(HERE/'controls.py') and controls['gate_script_sha256']==digest(HERE/'full_form_gate.py') and
        controls['audit_script_sha256']==digest(HERE/'rank_debt_audit.py'),'Independent control sources')
    need(len(controls['controls'])==3,'Three actual corruption controls')
    result=dict(status='PASS_FROZEN_ACTUAL_PHASE_AND_RANK_DEBT_AUDIT',script_sha256=digest(__file__),
        full_form_modes=2,actual_components=1067,useful_unpaid_helper_directions=0,
        audited_orientations=2,helper_paths_per_orientation=408,independent_controls=3,
        duplicate_511_scan_run=False,new_kappa=False,
        receipt_sha256={n:digest(HERE/n) for n in ['SOURCES.json','UPSTREAM.json','FULL-FORM-GATE.json',
            'RANK-DEBT-AUDIT.json','RANK-DEBT-REPLAY.log','CONTROLS.json']},
        scope='No-inert-marker forward full-form relaxation gates plus independent actual-path debt audit and exact PR4696 replay. No new native supplier, Lean theorem, compiler or kappa.')
    target=HERE/'BUNDLE-CHECK.json';encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if target.exists() and not args.write_manifest:need(target.read_text(encoding='utf-8')==encoded,'Frozen receipt drift')
    else:target.write_text(encoded,encoding='utf-8',newline='\n')
    files={str(p.relative_to(HERE)).replace('\\','/'):digest(p) for p in HERE.rglob('*') if p.is_file() and
        p.name!='ARTIFACT-MANIFEST.json' and not any(x in ['.scratch','__pycache__'] for x in p.relative_to(HERE).parts)}
    manifest=dict(status='FROZEN_ACTUAL_PHASE_RANK_DEBT_AUDIT_FILES',files_sha256=files)
    if args.write_manifest:(HERE/'ARTIFACT-MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    else:need(read(HERE/'ARTIFACT-MANIFEST.json')==manifest,'Frozen file hashes')
    print(result['status'],'modes=2 actualComponents=1067 independentPaths=816 duplicate511=false')
if __name__=='__main__':main()
