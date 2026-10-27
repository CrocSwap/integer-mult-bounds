"""Controlled byte-format and source-binding checks; no native/scalar replay."""
import argparse,hashlib,json,shutil,tempfile
from pathlib import Path
import portable_parent as adapter

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);args=ap.parse_args()
    require(not args.work.exists(),'test work must be absent');args.work.mkdir()
    package=Path(__file__).resolve().parent;parent=package/'parent';controls={}
    lf=b'{\n  "integer": 12345,\n  "rational": "1/3",\n  "digest": "ab12"\n}\n'
    crlf=lf.replace(b'\n',b'\r\n')
    require(adapter.same_artifact_bytes(lf,crlf),'LF/CRLF equivalent full bytes')
    require(adapter.same_artifact_bytes(crlf,lf),'CRLF/LF symmetry')
    mutants={'changed_digit':lf.replace(b'12345',b'12346'),
        'changed_rational':lf.replace(b'1/3',b'1/4'),
        'integer_to_float':lf.replace(b'12345',b'12345.0'),
        'integer_to_string':lf.replace(b'12345',b'"12345"'),
        'changed_hash':lf.replace(b'ab12',b'ab13'),
        'changed_whitespace':lf.replace(b'  "integer"',b' "integer"'),
        'changed_key_order':lf.replace(b'  "integer": 12345,\n  "rational": "1/3",',b'  "rational": "1/3",\n  "integer": 12345,')}
    for name,mutant in mutants.items():
        require(not adapter.same_artifact_bytes(crlf,mutant),'mutant accepted: '+name);controls[name]=True
    try:adapter.same_artifact_bytes(lf,lf.replace(b'\n',b'\r',1))
    except ValueError:controls['lone_CR']=True
    else:raise ValueError('lone CR accepted')
    receipts={};old_linesep=adapter.os.linesep
    try:
        for name,newline in [('LF','\n'),('CRLF','\r\n')]:
            adapter.os.linesep=newline
            executed,receipt=adapter.prepare_parent(parent,args.work/('execution-'+name))
            require(adapter.verify_parent(parent,executed,receipt),'execution source binding')
            require(set(receipt['changed_artifacts'])<=set(adapter.ARTIFACTS),'only allowed artifact changes')
            require(all((executed/n).read_bytes()==adapter.native_newlines((parent/n).read_bytes(),newline.encode()) for n in adapter.ARTIFACTS),'exact host-native execution artifacts')
            receipts[name]={'derived':executed!=parent,'changed_artifacts':receipt['changed_artifacts'],'manifest_sha256':receipt['execution_manifest_sha256']}
            if executed!=parent:
                target=executed/'outer/LEDGER.json';raw=target.read_bytes();changed=raw.replace(b'1',b'2',1);require(changed!=raw,'mutation fixture')
                target.write_bytes(changed)
                try:adapter.verify_parent(parent,executed,receipt)
                except ValueError:controls['derived_changed_digit_hash_rejected']=True
                else:raise ValueError('derived mathematical byte mutation accepted')
                target.write_bytes(raw)
                manifest=executed/'MANIFEST.json';raw_manifest=manifest.read_bytes();manifest.write_bytes(raw_manifest+b' ')
                try:adapter.verify_parent(parent,executed,receipt)
                except ValueError:controls['derived_manifest_byte_change_rejected']=True
                else:raise ValueError('derived manifest alteration accepted')
                manifest.write_bytes(raw_manifest);adapter.verify_parent(parent,executed,receipt)
    finally:adapter.os.linesep=old_linesep
    mutant_parent=args.work/'mutated-original';shutil.copytree(parent,mutant_parent)
    target=mutant_parent/'verify.py';target.write_bytes(target.read_bytes()+b'\n# controlled code mutation\n')
    try:adapter.prepare_parent(mutant_parent,args.work/'must-not-exist')
    except ValueError:controls['original_native_code_hash_rejected']=True
    else:raise ValueError('frozen native code mutation accepted')
    require(not (args.work/'must-not-exist').exists(),'invalid original created an execution copy')
    result={'status':'PASS_PORTABLE_PARENT_CONTROLLED_FORMAT_AND_HASH_CHECKS','controls':controls,'fixtures':receipts,
        'scope':'Byte-format and exact source binding only; no scientific supplier/native replay.',
        'adapter_sha256':hashlib.sha256(Path(adapter.__file__).read_bytes()).hexdigest(),
        'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
