"""Exercise the actual generated-payload admission against compression and data faults."""
import argparse,copy,gzip,hashlib,importlib.util,io,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def need(ok,label):
    if not ok:raise ValueError(label)
def main():
    p=argparse.ArgumentParser();p.add_argument('--physical',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    need(not a.out.resolve().is_relative_to(HERE.parent),'external receipt only')
    sp=importlib.util.spec_from_file_location('actual_payload_admission',HERE/'physical_replay.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    expected=json.loads((HERE/'PHYSICAL-EXPECTED.json').read_bytes());receipt=json.loads((a.physical/'RESULT.json').read_bytes());data=gzip.decompress((a.physical/'ACTUAL-FAMILY-FACTORS.json.gz').read_bytes());pin=expected['actual_factors_payload_sha256']
    variants=[gzip.compress(data,compresslevel=n,mtime=0)for n in (0,1,6,9)]
    buffer=io.BytesIO()
    with gzip.GzipFile(filename='representation-only',mode='wb',compresslevel=6,fileobj=buffer,mtime=123456)as z:z.write(data)
    variants.append(buffer.getvalue());header=bytearray(variants[2]);header[9]^=1;variants.append(bytes(header))
    for archive in variants:
        r=dict(receipt);r['actual_factors_sha256']=hashlib.sha256(archive).hexdigest()
        need(m.normalize_result(r,archive,pin)==expected,'compression representation changed mathematical receipt')
    controls=[]
    def reject(name,r,archive,payload_pin=pin):
        try:
            actual=m.normalize_result(r,archive,payload_pin)
            need(actual==expected,'mathematical receipt mismatch')
        except(ValueError,KeyError,OSError,EOFError):controls.append(name)
        else:raise ValueError('accepted fault: '+name)
    original=variants[2];honest=dict(receipt);honest['actual_factors_sha256']=hashlib.sha256(original).hexdigest()
    for label,bad_data in [('changed_payload',data.replace(b'"width":',b'"width_changed":',1)),('json_whitespace',data+b' ')]:
        bad=gzip.compress(bad_data,mtime=0);r=dict(honest);r['actual_factors_sha256']=hashlib.sha256(bad).hexdigest();reject(label,r,bad)
    bad=dict(honest);bad['actual_factors_sha256']='0'*64;reject('wrong_archive_hash',bad,original)
    bad=dict(honest);bad.pop('actual_factors_sha256');reject('missing_archive_hash',bad,original)
    for label,key in [('wrong_mass','rank_mass'),('wrong_count','parent_factor_count')]:
        bad=dict(honest);bad[key]+=1;reject(label,bad,original)
    bad=copy.deepcopy(honest);bad['source_sha256']['owners']='0'*64;reject('wrong_owner_source',bad,original)
    bad=copy.deepcopy(honest);bad['mutations_rejected']=[];reject('missing_controls',bad,original)
    bad=dict(honest);bad.pop('calls');reject('missing_math_key',bad,original)
    for label,archive in [('truncated_gzip',original[:-9]),('corrupt_crc',original[:-8]+bytes([original[-8]^1])+original[-7:])]:
        bad=dict(honest);bad['actual_factors_sha256']=hashlib.sha256(archive).hexdigest();reject(label,bad,archive)
    report=dict(status='PASS_PORTABLE_GENERATED_PAYLOAD_CONTROLS',representations=len(variants),rejected_controls=controls,payload_sha256=pin,scope='Same installedPython/zlib tested across compression levels and headers; not a claim of executing multiplezlibbuilds. Fixed checked-in gzip source bytes remain immutable manifest inputs.')
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(variants),'representations',len(controls),'rejections')
if __name__=='__main__':main()
