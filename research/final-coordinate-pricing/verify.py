"""Reprice legal carriers in PR95's final coordinates; retain all endpoint costs.
Rohan Arun with OpenAI Codex assistance. Apache-2.0.
"""
import sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util,json,gzip,tempfile,subprocess,shlex,os
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pricing_parent95',ROOT/'research/aligned-coordinate-descent/verify.py')
parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
import aligned_composition_graph as graph
from aligned_composition_nodeops import relabel,verify_dense
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare

def required():
 return parent.required()|{'research/aligned-coordinate-descent/SOURCE.json','.github/workflows/final-coordinate-pricing.yml'}|{str(p.relative_to(ROOT))for p in HERE.iterdir()if p.is_file()and p.name not in('SOURCE.json','validation.json')}
def sources():
 parent.sources();d=json.loads((HERE/'SOURCE.json').read_text());assert required()<=set(d['files'])
 for name,digest in d['files'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name

def coordinates(h):
 first=graph.configuration(h)['coordinate_permutation']
 second=json.loads((ROOT/f'research/aligned-coordinate-refinement/permutation-{h}.json').read_text())
 third=json.loads((ROOT/f'research/aligned-coordinate-descent/permutation-{h}.json').read_text())
 final=[third[second[first[i]]]for i in range(h)]
 assert sorted(final)==list(range(h))
 return final

def compile_selected(work):
 """Use the unchanged PR91 engine with a different existing oracle parameter."""
 h=25;source=ROOT/'scripts/experiments/aligned_composition_engine.py'
 previous=sys.path[:]
 try:
  spec=importlib.util.spec_from_file_location('final_pricing_engine',source)
  engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
 finally:sys.path[:]=previous
 config=graph.configuration(h);final=coordinates(h)
 engine.graph=graph.graph;engine.PENDING_COST=True;engine.OUTPUT_MODE=config['output_mode']
 engine.THREE_CYCLE_PASSES=config['three_cycle_passes'];engine.ORACLE_COORDINATES=final
 exe=work/'oracle'
 subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(ROOT/'references/frame-compiler/pr67/research/slot-cost-rank-pair/profile_oracle.cpp'),'-o',str(exe)],check=True)
 engine.ORACLE_EXE=str(exe);engine.ORACLE_INPUT=str(work/'oracle-input.bin');engine.oracles=[]
 try:result,word=engine.compile_(h,matching=True,reclaim=True,dirty=True)
 finally:
  for process in engine.oracles:
   process.stdin.close();assert process.wait(timeout=10)==0
 word=relabel(word,final);raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
 assert raw==gzip.decompress((HERE/'word-25.json.gz').read_bytes()),'Regenerated physical word differs'
 assert result['roles']==word['R']
 scalar=verify_dense(graph.graph(h));assert parent.arithmetic.js(scalar)==json.loads((HERE/'scalar-25.json').read_text())
 return dict(h=h,roles=word['R'],word_sha256=sha256(raw).hexdigest(),engine_sha256=sha256(source.read_bytes()).hexdigest(),final_coordinates=final,scalar=scalar)

def exact(profiles,certificate=None):
 c=certificate or json.loads((HERE/'certificate.json').read_text());bit=parent.combine(profiles);js=parent.arithmetic.js
 assert js(bit)==c['bit']
 saving=Q(c['bit_saving']);grid=Q(1,10**18);rows=bit['child_multiplicities']
 moment=parent.refine.exact_moment(bit['m'],bit['W'],rows,saving);rejected=parent.refine.exact_moment(bit['m'],bit['W'],rows,saving+grid)
 assert moment['upper']<1<rejected['lower'];assert js(moment)==c['exact_moment'] and str(rejected['lower'])==c['next_grid_lower']
 independent=parent.audit.independent_moment(js(bit),saving,js(moment['terms']));negative=parent.audit.independent_moment(js(bit),saving+grid,js(rejected['terms']));assert independent[1]<1<negative[0]
 bridge=parent.finite_bridge(bit['W']);assert js(bridge)==c['finite_bridge']
 assembly=parent.refine.assemble(bridge,saving,Q(1,10**12),10**18);assert js(assembly)==c['assembly'] and str(assembly['kappa'])==c['kappa']
 assert len(assembly['assembly']['constraints'])==47 and all(x>0 for x in assembly['assembly']['constraints'].values())
 assert len(assembly['assembly']['margins'])==7 and all(x>assembly['kappa']for x in assembly['assembly']['margins'].values())
 previous=json.loads((parent.HERE/'certificate.json').read_text());old=previous['bit']
 lower=parent.refine.exact_moment(old['m'],old['W'],{int(t):n for t,n in old['child_multiplicities'].items()},saving)['lower']
 assert lower>1 and str(lower)==c['prior_complete_profile_exclusion_lower'] and assembly['kappa']>Q(previous['kappa'])==Q(c['prior_kappa'])
 print('PASS exact final-coordinate pricing',assembly['kappa'],'47 constraints, seven margins, next-grid rejection and complete PR95 profile exclusion',flush=True)

def verify(regenerate=False):
 sources()
 if regenerate:parent.verify(True)
 profiles=[]
 with tempfile.TemporaryDirectory(prefix='final-coordinate-pricing-')as directory:
  work=Path(directory);receipt=compile_selected(work);print('PASS fresh unchanged-engine producer',json.dumps(receipt),flush=True)
  exe=work/'profiles';subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(ROOT/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(exe)],check=True)
  for h in(23,25):
   folder=parent.HERE if h==23 else HERE;path=folder/f'word-{h}.json.gz';replayed=replay(path)
   assert parent.arithmetic.js(replayed)==json.loads((folder/f'replay-{h}.json').read_text())
   trans=work/f'transitions-{h}.bin';prepare(path,trans);subprocess.run([str(exe),str(trans)],check=True)
   profile=json.loads(Path(str(trans)+'.profiles.json').read_text());assert profile==json.loads((folder/f'profiles-{h}.json').read_text());profiles.append(profile)
   print('PASS full physical replay and CRT profile',h,flush=True)
 exact(profiles)

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--regenerate',action='store_true');a=p.parse_args();verify(a.regenerate)
