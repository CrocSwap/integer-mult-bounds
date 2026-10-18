from pathlib import Path
import json,subprocess,hashlib,shutil
P=Path('/tmp/pr-efficient1800');E=P/'split-frame-consumer';R=Path('/tmp/integer-mult-efficient1100-20261015')
# Preserve failed complete replay and its fixture, then make an explicit v2 fixture.
F=P/'split-frame-consumer-v2';assert not F.exists();shutil.copytree(E,F,ignore=shutil.ignore_patterns('.git','__pycache__'))
manifest=json.loads((F/'research/split-skip/SOURCE.json').read_text());entries=[]
for path,name in [('scripts/partial_swap/shared.py','partial_swap_shared.py'),('scripts/audit_sparse_fusion.py','audit_sparse_fusion.py')]:
 old=subprocess.check_output(['git','show','7210de7d0f9ccaeb64c3f60f188419e02be08d95:'+path],cwd=R);expected=manifest['files'][path];assert hashlib.sha256(old).hexdigest()==expected
 live=subprocess.check_output(['git','show','HEAD:'+path],cwd=R);assert live==(F/path).read_bytes()
 (F/'scripts/historical-ci-inputs'/name).write_bytes(old)
 entries.append({'manifest':'research/split-skip/SOURCE.json','field':'files','path':path,'input':name,'sha256':expected,'accepted_live_sha256':[hashlib.sha256(live).hexdigest()]})
f=F/'scripts/replay_historical_check.py';s=f.read_text();needle='\n\n\ndef require(condition, message):';assert s.count(needle)==1;s=s.replace(needle,"\n# These two already-merged helpers also differ from the frozen PR54 inputs.\n# Preserve the original source bytes and attribution, with exact live guards.\nCONFIG['split-skip']['additional_inputs'].extend("+repr(entries)+")\n"+needle);f.write_text(s)
f=F/'tests/test_historical_check.py';s=f.read_text();s=s.replace("'scripts/shared_point_circuit.py', 'scripts/audit_joint_frames.py'})","'scripts/shared_point_circuit.py', 'scripts/audit_joint_frames.py',\n            'scripts/partial_swap/shared.py', 'scripts/audit_sparse_fusion.py'})");f.write_text(s)
subprocess.run(['git','init','-q'],cwd=F,check=True);subprocess.run(['git','add','.'],cwd=F,check=True)
s=(P/'run_split_consumer.py').read_text().replace("D=P/'split-frame-consumer'","D=P/'split-frame-consumer-v2'").replace('check-split-frame-consumer','check-split-frame-consumer-v2').replace('four exact dependency','six exact dependency');(P/'run_split_consumer_v2.py').write_text(s)
(P/'finding-split-existing-pins.json').write_text(json.dumps(dict(status='candidate_repair_not_admitted',first_replay='check-split-frame-consumer.json',failure='Actual witness fails its inherited skip-strips check on partial_swap/shared.py before proposed joint-frame change is consumed. Two additional current-main helpers differ from original split-skip pins.',restorations=entries,historical_commit='7210de7d0f9ccaeb64c3f60f188419e02be08d95',source_binding='Restored bytes checked against unchanged source manifest and actual Git object; live successor bytes match current main exactly.'),indent=2)+'\n')
print('Restored two additional exact historical inputs in new candidate')
