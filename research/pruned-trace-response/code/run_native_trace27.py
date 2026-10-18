"""Replay upstream native checkers on the changed bit word; no checker patches.
Usage: run_native_portable.py INPUT_PACKAGE493 WORD OUT --cxx CXX --boost-include INCLUDE
Requires Python with numpy/sympy, a C++17 compiler and genuine Boost headers.
"""
from pathlib import Path
import argparse,subprocess,os,json,time,concurrent.futures,sys,hashlib,threading

def main():
 if not __debug__:raise SystemExit('Assertions must be enabled')
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input_package',type=Path);ap.add_argument('word',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--cxx',default=os.environ.get('CXX','c++'));ap.add_argument('--boost-include',type=Path,required=True);ap.add_argument('--jobs',type=int,default=3);args=ap.parse_args()
 B,WORD,D,boost=(x.resolve()for x in [args.input_package,args.word,args.out,args.boost_include]);assert not D.exists();assert (boost/'boost/multiprecision/cpp_int.hpp').is_file(),'genuine Boost include missing';D.mkdir(parents=True);(D/'bin').mkdir();CODE=B/'code/bit';CHECK=CODE/'checkers';env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1');stages=[];lock=threading.Lock()
 def dump(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n')
 def run(name,cmd):
  began=time.monotonic();r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,encoding='utf-8',errors='replace',env=env);(D/(name+'.log')).write_text(r.stdout+r.stderr,encoding='utf-8',newline='\n')
  with lock:stages.append(dict(name=name,exit=r.returncode,seconds=time.monotonic()-began));dump(D/'STAGES.json',stages)
  if r.returncode:raise RuntimeError(name+' failed; see '+str(D/(name+'.log'))+'\n'+r.stdout[-1200:]+r.stderr[-1200:])
  print('PASS '+name,flush=True)
 inc=['-I'+str(B/'portable-include'),'-I'+str(CHECK),'-I'+str(boost)];suffix='.exe'if os.name=='nt'else'';exe=lambda name:D/'bin'/(name+suffix)
 common=[args.cxx,'-O2','-std=c++17','-DHDIM=8']+inc
 jobs=[('legality','legality_h.cpp',['-DNCOPY=9']),('legality_default','legality_h.cpp',[]),('columns_h','columns_h.cpp',['-DNCOPY=9','-DVPORTS=120','-DRHELP=480']),('columns_k4','columns_k.cpp',['-DNCOPY=9','-DVPORTS=120','-DRHELP=480','-DKPAIRS=4'])]
 with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(args.jobs,3)))as pool:
  fs=[pool.submit(run,'compile-'+name,common+extra+[CHECK/source,'-o',exe(name)])for name,source,extra in jobs]
  for f in fs:f.result()
 py=[sys.executable,'-B']
 run('export',py+[CODE/'export_records.py',WORD,D/'records'])
 run('stage',py+[CODE/'regression/stage_cohort.py',D/'records',D/'records',D/'cin',D/'cout'])
 run('legality',[exe('legality'),D/'cin',D/'cout',D/'cout/legality.json'])
 run('columns_h',[exe('columns_h'),D/'cout/COHORT249-RECORDS.bin',D/'cout/columns.json'])
 run('columns_k4',[exe('columns_k4'),D/'cout/COHORT249-RECORDS.bin',D/'cout/columns_k4.json'])
 run('interface',py+[CODE/'independent/interface.py',WORD,'--json',D/'interface.json'])
 run('gram_frames',py+[CHECK/'gram_frames.py',D/'records','--gram','e8ham','--h','8','--positive'])
 run('structural_controls',py+[CODE/'mutate_records.py',D/'records',D/'cin',D/'cout',exe('legality'),exe('columns_k4'),exe('legality_default')])
 run('mutable_source_controls',py+[CODE/'mutate_records_mut.py',WORD,D/'records',D/'cin',D/'cout',exe('legality'),exe('columns_h'),exe('columns_k4')])
 read=lambda p:json.loads(p.read_text());h=read(D/'cout/columns.json');k=read(D/'cout/columns_k4.json');lg=read(D/'cout/legality.json');assert h['formal_columns_checked']==960 and k['formal_columns_checked']==1440;assert len(k['stages'])==9 and len(k['negative_controls'])==18 and all(x['rejected']for x in k['negative_controls']);assert k['local_raw_H']==h['local_raw_H']==[[1,1257],[2,1330],[3,43],[4,163],[6,137],[8,9]];assert k['payload_prefix_bits']==h['payload_prefix_bits'] and 0<k['payload_prefix_bits']<=102
 expected_counts={'structural_controls':'PASS all 6 record-level negative controls rejected','mutable_source_controls':'PASS all 3 record-level mutable-source mutants rejected'}
 for name,marker in expected_counts.items():assert marker in(D/(name+'.log')).read_text()
 hashes={name:hashlib.sha256((CHECK/name).read_bytes()).hexdigest()for name in ['legality_h.cpp','columns_h.cpp','columns_k.cpp','gram_frames.py']}
 receipt=dict(status='PASS_NATIVE_PRUNED_TRACE27_LOCAL_FRAME_COLUMNS_PREFIX_AND_CONTROLS',word_sha256=hashlib.sha256(WORD.read_bytes()).hexdigest(),checker_source_sha256=hashes,local_paid_profile=dict(k['local_raw_H']),formal_columns_nine_stage=1440,formal_columns_five_stage=960,nine_stage_bridge_controls=18,structural_record_controls=6,mutable_source_controls=3,payload_prefix_bits=k['payload_prefix_bits'],gram_frames_audit_passed=True,actual_checker_configuration='HDIM8 NCOPY9 VPORTS120 RHELP480 KPAIRS4',scope='Changed native scalar/frame/interface/Gram/prefix evidence. Global routing, full finite invoice and exact outer assembly are separate. Compiler source is unmodified.')
 dump(D/'NATIVE-REVIEW.json',receipt);print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()
