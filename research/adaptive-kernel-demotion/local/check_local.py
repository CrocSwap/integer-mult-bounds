"""Portable fresh changed-local replay, Windows-native/stdlib, bounded child jobs.
No WSL, GPU, C++ executable, background service or network. Apache-2.0.
Inherited unchanged PR1117 phase edges and adapters remain explicit assumptions.
"""
import argparse,gzip,json,hashlib,subprocess,sys,time
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent

def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(b,s):
 if not b:raise RuntimeError(s)
def construct(out,k):
 w=read(P/'data/PR1117-WORD.json.gz');patch=read(P/'data/PATCHES.json');need(hashlib.sha256(enc(w)).hexdigest()==patch['parent_sha256']=='f64e0942edc5eb2d45b0a3b068ba942436f35ba9a077ff53d7e4424d1617b2cd','actual PR1117 word');seen=set()
 for group in patch['groups'][:k]:
  for q in group['helpers']:
   key=('start_extra',q);need(key not in seen,'overlapping entrance patches');seen.add(key);need(w['start_extra'][str(q)]==group['before'],'old entrance');w['start_extra'][str(q)]=group['after']
  for sec,i,old,new in group['frames']:
   key=(sec,i);need(key not in seen,'overlapping gate patches');seen.add(key);need(w[sec][i][-1]==old,'old frame');w[sec][i][-1]=new
 provider=read(P/'data/PROVIDERS.json')[k-1];need(provider['selector']==k,'provider selector');w['report'].update(local_profile=provider['local_profile'],local_rank_mass=provider['local_rank_mass'],width_inventory=provider['width_inventory'])
 raw=enc(w);need(hashlib.sha256(raw).hexdigest()==provider['content_sha256'],'constructed new word');out.write_bytes(gzip.compress(raw,mtime=0));return out

def main():
 need(__debug__,'assertion-based vendor engines require normal Python, not -O')
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--selector',type=int,choices=range(1,6),required=True);a=ap.parse_args();need(not a.out.exists(),'fresh output directory required')
 for name,digest in read(P/'SOURCE-PINS.json').items():need(sha(P/name)==digest,'input source pin '+name)
 a.out.mkdir(parents=True);t=time.monotonic();raw=construct(a.out/'CHANGED-WORD.json.gz',a.selector);steps=[]
 def run(label,script,args):
  start=time.monotonic();flags=0x4000 if sys.platform=='win32' else 0
  r=subprocess.run([sys.executable,'-I','-B',str(script),*map(str,args)],capture_output=True,text=True,timeout=20,creationflags=flags)
  (a.out/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf-8');need(r.returncode==0,label+' failed '+r.stderr[-1200:]);steps.append(dict(step=label,seconds=time.monotonic()-start));print('PASS',label,flush=True)
 native=a.out/'native';run('raw-independent',P/'vendor/audit_local.py',['--word',raw,'--output',a.out/'RAW-CHECK.json']);run('native',P/'vendor/hpe_audit_and_transport.py',['--raw',raw,'--routing',P/'data/PARENT-ROUTING.json.gz','--out',native]);run('emit',P/'vendor/hpe_emit_local.py',[native]);run('emitted-independent',P/'vendor/hpe_audit_local.py',[native]);need(read(native/'CANONICAL-WORD.json.gz')==read(P/'data'/f'EXPECTED-{a.selector}-CANONICAL-WORD.json.gz'),'fresh canonical exact equality')
 replay=read(native/'INDEPENDENT-LOCAL-REPLAY.json');expected=read(P/'data'/f'EXPECTED-{a.selector}-LOCAL-REPLAY.json');need(replay['canonical_word_sha256']==sha(native/'CANONICAL-WORD.json.gz') and replay['local_programs_sha256']==sha(native/'LOCAL-PROGRAMS.json.gz'),'fresh emitted byte bindings'); need({k:v for k,v in replay.items() if k not in ('canonical_word_sha256','local_programs_sha256')}=={k:v for k,v in expected.items() if k not in ('canonical_word_sha256','local_programs_sha256')},'fresh emitted receipt mathematical equality')
 run('changed-phases',P/'check_changed_phases.py',['--old',P/'data/OLD-CANONICAL-WORD.json.gz','--new',native/'CANONICAL-WORD.json.gz','--out',a.out/'CHANGED-PHASES.json']);ph=read(a.out/'CHANGED-PHASES.json');oldph=read(P/'data'/f'EXPECTED-{a.selector}-CHANGED-PHASES.json')
 for k in ('new_frames','changed_edges','changed_wrappers','controls','records','engine_sha256'):need(ph[k]==oldph[k],'fresh phase result '+k)
 result=dict(status='PASS_FRESH_COMBINED_LOCAL_SUPPLIER',actual_columns=704,orientations=2,selector=a.selector,changed_edges=ph['changed_edges'],changed_wrappers=ph['changed_wrappers'],emitted_controls=25,phase_controls=len(ph['controls']),local_profile=read(native/'CANONICAL-WORD.json.gz')['local_profile'],total_seconds=time.monotonic()-t,steps=steps,scope='Every changed local scalar endpoint/frame/low-end cone, emitted event program and changed phase/adapter. Unchanged PR1117 phase edges, endpoint adapters and global/compiler/analytic contracts inherited; global owner/precision/outer assembly checked separately.')
 (a.out/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('PASS_FRESH_COMBINED_LOCAL_SUPPLIER',result['total_seconds'],'seconds')
if __name__=='__main__':main()

