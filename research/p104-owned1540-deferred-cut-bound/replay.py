"""Authenticate and replay the exact deferred owned1540 bank exclusion."""
from hashlib import sha256
from json import loads
from os import killpg
from pathlib import Path
from signal import SIGKILL
from subprocess import PIPE, Popen, TimeoutExpired
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
FILES = {'7481-WORD.json.gz','NATIVE-RESULT.json','suffix_readout.py','PROVENANCE.json','receipts/RESULT.json'}


def unique(pairs):
    result=dict(pairs)
    assert len(result)==len(pairs),'duplicate JSON key'
    return result


def parse(raw):
    return loads(raw,object_pairs_hook=unique)


def authenticate(raw,digest):
    assert sha256(raw).hexdigest()==digest,'changed bytes'


def compare(receipt):
    assert receipt['status']=='EXACT_OUTSIDE_BANK_SEPARATOR' and receipt['cases_completed']==1
    assert receipt['cut']==58937 and receipt['bank_size']==1046 and receipt['target_support']==137
    assert receipt['live_owned']==1568 and receipt['elimination_denominator']=='1'
    assert receipt['source_on_live_owned']==receipt['live_owned_feedback']=='0'
    assert receipt['cut_coefficient_support']==232 and len(receipt['outside_bank_coefficients'])==55
    assert '756' not in receipt['exact_cut_coefficients']
    assert receipt['outside_bank_coefficients']['882']=='-1/2'
    witness=receipt['witness']; control=receipt['self_scale_control']
    assert witness['original_probe']=={'772':'1','882':'1'}
    assert (witness['old756_at_cut'],witness['modified756_at_cut'],witness['old_owned1540'])==(0,'1/2','-1/2')
    assert (control['old756_at_cut'],control['modified756_at_cut'],control['old_owned1540'])==(1,1,0)
    assert witness['live_owned1568_at_cut']==control['live_owned1568_at_cut']=='0'
    assert receipt['gross_signed_raw']==17


def expect_rejection(action):
    try: action()
    except AssertionError: return
    raise AssertionError('mutated input or receipt passed')


def main():
    assert __debug__ and implementation.name=='cpython' and version_info[:2]==(3,12)
    pins=parse((ROOT/'PINS.json').read_bytes())
    assert set(pins)==FILES
    files={name:(ROOT/name).read_bytes()for name in sorted(FILES)}
    for name,raw in files.items():authenticate(raw,pins[name])
    process=Popen([executable,'-I','-B',str(ROOT/'suffix_readout.py')],cwd=ROOT,
                  stdout=PIPE,stderr=PIPE,start_new_session=True)
    try: output,errors=process.communicate(timeout=30)
    except TimeoutExpired:
        killpg(process.pid,SIGKILL);process.communicate();raise AssertionError('unresolved process cap') from None
    assert process.returncode==0 and not errors,errors.decode(errors='replace')
    receipt=parse(output)
    assert receipt==parse(files['receipts/RESULT.json'])
    compare(receipt)
    raw=files['7481-WORD.json.gz']
    expect_rejection(lambda:authenticate(bytes([raw[0]^1])+raw[1:],pins['7481-WORD.json.gz']))
    expect_rejection(lambda:parse('{"word":1,"word":2}'))
    false_control=dict(receipt['self_scale_control'],old_owned1540='-1/2')
    expect_rejection(lambda:compare(dict(receipt,self_scale_control=false_control)))
    print('PASS_DEFERRED_OWNED1540: exact outside-bank witness and incompatible self-scale control')


if __name__=='__main__': main()
