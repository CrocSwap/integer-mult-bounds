#!/usr/bin/env python3
"""Read-only reproduction of the fixed PR168 frame refinement and exact audit."""
import gzip,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
sys.dont_write_bytecode=True
assert not sys.flags.optimize,'Run without -O'
manifest=json.loads((P/'SOURCE.json').read_text())
for name,digest in manifest['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'research/terminal-sinks'))
import paired_cube_producer as producer
import paired_cube_physical as physical
from sinks_gate import sinks_record
from paired_cube_network import certificate as baseline_certificate
# Complete unchanged current PR168 bit, complex, sink and paid-assembly gates.
baseline_certificate()
with tempfile.TemporaryDirectory(prefix='frame-refinement-') as tmp:
 t=Path(tmp);row=json.loads((ROOT/'certificates/paired-cube-complex-input.json').read_text())
 producer.regenerate(row,t)
 def load(name):return json.loads(gzip.decompress((P/'selected'/(name+'.json.gz')).read_bytes()))
 g,w,word=load('graph'),load('frames'),load('word')
 for name,data in [('graph',g),('frames',w),('selection',word)]:assert data==json.loads((t/(name+'.json')).read_text()),name
 assert row==load('profile-before')
 frames,pairs=load('physical-frames'),load('physical-pairs')
 assert pairs==json.loads((ROOT/'references/paired-cube/physical/pairs.json').read_text())['pairs']
 actual=physical.physical(g,w,word,row,frames,pairs)
 assert json.loads(json.dumps(actual))==load('profile')
 sinks=json.loads((ROOT/'research/terminal-sinks/sinks.json').read_text())['sinks']
 result=sinks_record(g,w,word,row,frames,pairs,sinks,actual)
 expected=json.loads((P/'selected/sinks-profile.json').read_text())
 assert json.loads(json.dumps(result))==expected
 subprocess.run([sys.executable,'-B',str(P/'arithmetic.py')],check=True)
 subprocess.run([sys.executable,'-B',str(P/'audit/check_sinks.py'),'--candidate',str(P/'selected'),'--output',str(t/'sinks.json')],check=True)
 independent=json.loads((t/'sinks.json').read_text())
 assert independent['eligible_count']==expected['sinks']
 for a,b in [('child_histogram','child_histogram'),('local_histogram','local_histogram'),('target_data_histogram','target_histogram')]:
  clean=lambda d:{int(k):v for k,v in d.items() if int(k) and v}
  assert clean(expected[a])==clean(independent[b]),a
 subprocess.run([sys.executable,'-B',str(P/'audit/formal_sinks.py'),'--candidate',str(P/'selected'),'--selection',str(t/'sinks.json'),'--formal-helper',str(P/'audit/physical.py'),'--output',str(t/'formal.json')],check=True)
 formal=json.loads((t/'formal.json').read_text())
 assert all(x['columns']==expected['W_per_vertex'] and x['dirty']==expected['physical_R'] and x['restored'] for x in formal['columns'])
 assert len(formal['controls'])==3 and set(formal['controls'].values())=={'REJECTED'}
print('PASS source pins, regenerated DAG, unchanged bit supplier, both signed words, 10 inherited physical/sink/formal controls, 47 inequalities and 7 margins')
