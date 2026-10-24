"""Actual entry-point and independent path/block corruption controls."""
from pathlib import Path
from copy import deepcopy
import contextlib,gzip,io,json,shutil,sys,tempfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
import full_form_gate as F
import rank_debt_audit as D

def main():
    payload=json.loads(gzip.decompress((HERE/'sources/native-word.json.gz').read_bytes()));out=[]
    bad=deepcopy(payload)
    next(e for e in bad['programs']['forward'] if e[0]=='climb')[5]+=1
    try:D.actual_paths(bad,'forward')
    except ValueError as e:
        D.need(str(e)=='Actual increasing paid edge','Exact independent width rejection');out.append('wrong_actual_paid_width')
    else:raise ValueError('Wrong width accepted')
    # Split an actual helper paid edge into two positive rises with the same
    # endpoints and no intervening scalar. The block condition must reject it.
    bad=deepcopy(payload);frames=bad['canonical']['frames'];word=bad['programs']['forward']
    for at,e in enumerate(word):
        if e[0]=='climb' and e[2]>=224 and e[5]>=2:
            A,B=frames[e[3]],frames[e[4]];basis=D.pivots(A)
            vector=next(v for v in B if not D.contains(basis,v))
            middle=len(frames);frames.append(A+[vector])
            first=list(e);first[4]=middle;first[5]=1
            second=list(e);second[3]=middle;second[5]-=1
            word[at:at+1]=[first,second];break
    else:raise ValueError('Missing helper block fixture')
    try:D.actual_paths(bad,'forward')
    except ValueError as e:
        D.need(str(e)=='Actual no-marker helper block has at most one paid call','Exact block rejection');out.append('two_original_paid_jobs_in_one_helper_block')
    else:raise ValueError('Split block accepted')
    scratch=HERE/'.scratch';scratch.mkdir(exist_ok=True);saved=F.HERE
    with tempfile.TemporaryDirectory(prefix='pin-control-',dir=scratch) as folder:
        target=Path(folder).resolve();D.need(target.is_relative_to(scratch.resolve()),'Scratch containment')
        shutil.copytree(HERE/'sources',target/'sources');shutil.copyfile(HERE/'SOURCES.json',target/'SOURCES.json')
        p=target/'sources/mixed_gauge.py';p.write_bytes(p.read_bytes()+b'\n# deliberate source mutation\n');F.HERE=target
        try:
            with contextlib.redirect_stdout(io.StringIO()):F.main()
        except ValueError as e:
            D.need(str(e)=='Pinned source mixed_gauge.py','Exact actual gate source rejection');out.append('geometry_source_byte_mutation')
        else:raise ValueError('Changed geometry source accepted')
        finally:F.HERE=saved
    output=dict(status='PASS_ACTUAL_GRAPH_PHASE_DEBT_CONTROLS',controls=out,
        script_sha256=D.digest(__file__),gate_script_sha256=D.digest(HERE/'full_form_gate.py'),
        audit_script_sha256=D.digest(HERE/'rank_debt_audit.py'),sources_sha256=D.digest(HERE/'SOURCES.json'),
        scope='Actual source authentication and independent width/block predicates; unchanged original files. No native or analytic theorem proof.')
    (HERE/'CONTROLS.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(output['status'],len(out))
if __name__=='__main__':main()
