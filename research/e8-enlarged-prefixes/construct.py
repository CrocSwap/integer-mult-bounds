from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
assert __debug__
ROOT=Path(__file__).resolve().parent
source,out=map(Path,sys.argv[1:3]);assert not out.exists();out.mkdir(parents=True)
subprocess.run([sys.executable,'-B',str(ROOT/'gauge_construct.py'),str(source),str(out/'enlarged')],check=True)
subprocess.run([sys.executable,'-B',str(ROOT/'prefix_construct.py'),str(out/'enlarged/candidate.json'),str(out/'prefix')],check=True)
p=out/'prefix/candidate.json';c=json.loads(p.read_text())
s=importlib.util.spec_from_file_location('frames',ROOT.parent/'e8-shared-donor-chains/frames/reconstruct.py');F=importlib.util.module_from_spec(s);s.loader.exec_module(F)
oldblocks=c['blocks'];F.rehist_and_audit(c);assert c['blocks']==oldblocks
expected=json.loads((ROOT/'EXPECTED.json').read_text());assert hashlib.sha256(p.read_bytes()).hexdigest()==expected['candidate_sha256']
(out/'candidate.json').write_bytes(p.read_bytes())
result=dict(status='PASS_EIGHTH_ENLARGEMENT_AND_PROTECTED_PREFIX_COMPOSITION',candidate_sha256=expected['candidate_sha256'],gauge=json.loads((out/'enlarged/RESULT.json').read_text()),prefix=json.loads((out/'prefix/RECEIPT.json').read_text()))
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
