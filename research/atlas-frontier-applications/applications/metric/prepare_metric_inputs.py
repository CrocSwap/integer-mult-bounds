# SPDX-License-Identifier: Apache-2.0
"""Create a fresh machine-local input manifest; no inherited file is edited."""
import argparse,hashlib,json,os
from pathlib import Path

def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser()
 for key in ('source','native-root','plan','parent','owners','data-phases','out'):ap.add_argument('--'+key,type=Path,required=True)
 ap.add_argument('--primary-dir',type=Path,default=Path(__file__).resolve().parent/'primary')
 a=ap.parse_args();here=Path(__file__).resolve().parent
 if a.out.exists():raise RuntimeError('Refuse to overwrite input manifest: '+str(a.out))
 receipt=json.loads((a.native_root/'NATIVE-RECEIPT.json').read_bytes())
 paths={'source_manifest':a.source/'MANIFEST.json','native_receipt':a.native_root/'NATIVE-RECEIPT.json','legacy_checker':here/'endpoint_contract.py','stream_checker':here/'exact_stream_metric.py','plan':a.plan,'parent':a.parent,'owners':a.owners,'data_phases':a.data_phases,'primary_pins':a.primary_dir/'PINS.json'}
 for pid,key in [('gauge44','base'),('extra','extra')]:paths[pid+'/canonical']=a.native_root/'native-cache'/receipt['providers'][key]['word_sha256']/'local/CANONICAL-WORD.json.gz'
 d={'scope':'Current-source finite premises for the mixed-fibre sufficient magnitude envelope; not a full payload-256 admission.','inputs':{k:{'path':str(p.resolve()),'sha256':sha(p)}for k,p in paths.items()}}
 lock=a.out.with_name(a.out.name+'.lock');fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
 try:a.out.write_text(json.dumps(d,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
 finally:lock.unlink()
 print('Created fresh input manifest: '+str(a.out))
if __name__=='__main__':main()
