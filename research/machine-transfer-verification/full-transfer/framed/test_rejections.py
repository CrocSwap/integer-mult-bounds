#!/usr/bin/env python3
"""Reject malformed inverse/ambient schedules using exact checker copies in memory."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--word-dir',required=True,type=Path)
    p.add_argument('--profile-inputs',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args(); records=[]
    cases=[
      ('reverse_local.py','incorrect_gate_transpose','        zv[a] ^= zv[b]\n','        zv[b] ^= zv[a]\n','Complete dirty-basis inverse-renamed action','reverse'),
      ('reverse_local.py','missing_reverse_original_center_transport','        move(slot,f)  # original 0 -> U^perp, rank one\n','','clone source frame','reverse'),
      ('reverse_local.py','unpaid_reverse_center_copy','        paid[0,f]+=1; phases[phase][\'paid_copy_transports\']+=1\n','        phases[phase][\'paid_copy_transports\']+=1\n','Auxiliary mass','reverse'),
      ('full_ambient.py','missing_final_paid_correction','    Y ^= copy\n','','Paid endpoint correction not interchange','ambient'),
      ('full_ambient.py','wrong_endpoint_copy_residual','    copy=transform(X,1)                   # one FRESH copy, rank-one transport\n','    copy=transform(X,0)\n','Paid endpoint correction not interchange','ambient'),
      ('full_ambient.py','missing_stage2_auxiliary_exterior',"'auxiliary_stage2':(12,3)","'auxiliary_stage2':(12,15)",'Noncomplementary original-role endpoint','ambient'),
      ('full_ambient.py','wrong_data_front_residual',"('front_X',5,13,8)","('front_X',5,13,4)",'Boundary residual: front_X','ambient'),
    ]
    for filename,name,old,new,expected,mode in cases:
        file=HERE/filename;source=file.read_text()
        if source.count(old)!=1:raise RuntimeError('Nonunique mutation anchor: '+name)
        ns={'__name__':'mutated','__file__':str(file)}
        exec(compile(source.replace(old,new),str(file)+':'+name,'exec'),ns)
        try:
            if mode=='ambient':ns['algebra']()
            else:ns['audit'](a.word_dir/'pair-ranked-word-25.json.gz',a.word_dir/'source-word-manifest.json',a.word_dir/'pair-ranked-25-receipt.json',a.profile_inputs/'ranked-25.bin')
        except ValueError as e:
            if expected not in str(e):raise RuntimeError('Wrong rejection: '+name+': '+str(e)) from e
            records.append(dict(name=name,status='REJECTED',reason=str(e),checker_sha256=sha256(file.read_bytes()).hexdigest(),mutation_sha256=sha256((old+'\0'+new).encode()).hexdigest()))
        else:raise RuntimeError('Malformed schedule accepted: '+name)
        print('PASS rejected',name,flush=True)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(dict(status='PASS',controls=records,scope='Only in-memory checker copies mutated; original source words and files unchanged.'),indent=2)+'\n')

if __name__=='__main__':main()
