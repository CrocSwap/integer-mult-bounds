"""Authenticated exact finite checks; Dugongue with OpenAI assistance; Apache-2.0."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)

def main():
    pins=json.loads((ROOT/'CONTENT-HASHES.json').read_text(encoding='utf-8'))
    files={f.relative_to(ROOT).as_posix() for f in ROOT.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
    need(files==set(pins)|{'CONTENT-HASHES.json'},'Package inventory drift')
    for name,digest in pins.items():need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'Source drift: '+name)
    reports={}
    for name in ['tabulated_tm.py','packed_codec.py','tabulated_multiply.py','end_to_end.py']:
        run=subprocess.run([sys.executable,'-I','-O','-B',str(ROOT/name)],capture_output=True,text=True,encoding='utf-8',timeout=120)
        need(run.returncode==0,name+' failed: '+run.stderr[-2000:]);reports[name]=json.loads(run.stdout)
        need(reports[name]['status']=='PASS',name+' did not pass')
    m=reports['tabulated_tm.py'];c=reports['packed_codec.py'];e=reports['end_to_end.py']
    need(m['machine_cases']==224 and m['nonhalting_macros']==30 and m['mutated_table_detected'] and m['undersized_word_rejected'],'TM coverage/control missing')
    need(c['packed_io_cases']==4277 and c['corrupted_decoder_controls']==7,'Codec coverage/control missing')
    need(e['input_pairs']==16 and e['real_TM_halting'] and e['packed_contiguous_window_IO'] and not e['all_length_multiplier'],'Finite composed fixture scope mismatch')
    print(json.dumps({'status':'PASS','scope':'Authenticated finite operational models and bounded composed fixture; informal universal proofs; no new TM kappa or Lean audit','reports':reports},indent=2))

if __name__=='__main__':main()
