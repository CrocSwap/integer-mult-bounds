"""Run the complete pinned local audit, optionally with integer rows.

Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse,contextlib,hashlib,importlib.util,io,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
CHECKER='research/emitted-local-integer-replay-seed90/baseline.py'
spec=importlib.util.spec_from_file_location('local_integer_rows',HERE/'fast.py');fast=importlib.util.module_from_spec(spec);spec.loader.exec_module(fast)

def require(ok,message):
 if not ok:raise ValueError(message)
def sha(data):return hashlib.sha256(data).hexdigest()
def source():
 text=(ROOT/CHECKER).read_bytes().replace(b'\r\n',b'\n')
 pins=json.loads((HERE/'SOURCES.json').read_bytes())
 require(sha(text)==pins[CHECKER],'checker source hash mismatch')
 return text.decode()

def execute(directory,engine='integer',row_class=None,outcomes=None):
 text=source();text=fast.transform(text) if engine=='integer' else text
 require(engine in ('reference','integer'),'unknown engine')
 argv=sys.argv;sys.argv=[str(ROOT/CHECKER),str(directory)];stream=io.StringIO()
 env={'Row':row_class or fast.Row}
 if outcomes is not None:
  marker='profiles={};checks={}'
  require(text.count(marker)==1,'outcome hook boundary')
  text=text.replace(marker,'local=_record_local(local)\n'+marker)
  def record_local(fn):
   def wrapped(events,back):
    try:answer=fn(events,back)
    except Exception as error:
     outcomes.append({'backward':back,'exception':type(error).__module__+'.'+type(error).__qualname__,'args':repr(error.args)});raise
    outcomes.append({'backward':back,'pass':True});return answer
   return wrapped
  env['_record_local']=record_local
 try:
  with contextlib.redirect_stdout(stream):exec(compile(text,str(ROOT/CHECKER),'exec',optimize=0),env)
 finally:sys.argv=argv
 return (Path(directory)/'INDEPENDENT-LOCAL-REPLAY.json').read_bytes(),stream.getvalue()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);ap.add_argument('--engine',choices=['reference','integer'],default='integer');ap.add_argument('--timing',type=Path)
 args=ap.parse_args();wall=time.perf_counter();cpu=time.process_time();receipt,log=execute(args.directory,args.engine)
 timing={'engine':args.engine,'wall_seconds':time.perf_counter()-wall,'cpu_seconds':time.process_time()-cpu,'receipt_LF_sha256':sha(receipt.replace(b'\r\n',b'\n')),'stdout_sha256':sha(log.encode())}
 if args.timing:args.timing.write_text(json.dumps(timing,indent=2)+'\n')
 print(log,end='')

if __name__=='__main__':main()
