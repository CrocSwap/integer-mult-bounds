#!/usr/bin/env python3
"""Freeze the PR569 global verifier adapter for the composed provider."""
import argparse,hashlib,json,re
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ('source-code','local','plan','out'):ap.add_argument('--'+n,type=Path,required=True)
    ap.add_argument('--invoice',type=Path)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    read=lambda p:json.loads(p.read_text())
    for p in a.source_code.glob('*.py'):
        s=p.read_text()
        if p.name=='bind_providers_portable.py':
            s=s.replace('(3005 if p else 2929)','(3004 if p else 2929)')
            s=s.replace('expected={1:2320+p,2:432+5*p,3:456-4*p,4:192,5:56,6:56,8:8}',"expected=({1:2352,2:580,3:336,4:192,5:56,6:56,8:8} if p else {1:2320,2:432,3:456,4:192,5:56,6:56,8:8})")
        elif p.name=='assembly_controls.py':
            extra = "    for helper in (271, 283, 295, 307):\n        def move_new_cold(o, i, helper=helper):\n            widths = i['providers']['width7_eight']['widths']\n            other = widths.index(9)\n            widths[helper], widths[other] = widths[other], widths[helper]\n        controls.append(('new_target_kernel_width_swap_' + str(helper), move_new_cold))\n"
            s=s.replace('    rejected = []',extra+'    rejected = []').replace('assert len(rejected) == 89','assert len(rejected) == 93')
        elif p.name=='assemble.py':
            if not a.invoice:
                continue
            invoice=read(a.invoice);plan=read(a.plan)
            # Retain all previous provider pins except the exact newly rebuilt
            # provider. Per-provider native charges remain literal constants.
            oldline=next(line for line in s.splitlines()if line.startswith('PROVIDERS='))
            import ast
            providers=ast.literal_eval(oldline.split('=',1)[1]);pid='width7_eight';d=plan['provider_registry'][pid]
            phase=read(a.local/'CLIFFORD-REVIEW.json')
            providers[pid]=dict(semantic_phase_sha256=hashlib.sha256(json.dumps({k:v for k,v in phase.items()if k!='seconds'},sort_keys=True,separators=(',',':')).encode()).hexdigest(),promoted=32,width_digest=hashlib.sha256(json.dumps(d['widths'],separators=(',',':')).encode()).hexdigest(),program_hashes=d['orientation_program_sha256'],artifacts={n:sha(a.local/n)for n in d['artifact_sha256']if n!='CLIFFORD-REVIEW.json'})
            for name,desc in providers.items():
                provider_invoice=invoice['providers'][name]
                desc['expected_profile']=provider_invoice['paid_profile']
                desc['expected_local']={ori:{k:v for k,v in local.items()if k in ('events','macros','real_component_primitives','coefficient_work_primitive_count','prefix_l1')}for ori,local in provider_invoice['local'].items()}
            s=s.replace(oldline,'PROVIDERS='+repr(providers))
            s=s.replace("{'1':2320+promoted,'2':432+5*promoted,'3':456-4*promoted,'4':192,'5':56,'6':56,'8':8}","PROVIDERS[pid]['expected_profile']")
            s=s.replace("for name,primitives,coefficient_work in [('forward',161308,79874),('backward',161356,79906)]:","for name in ('forward','backward'):\n   pinned=PROVIDERS[pid]['expected_local'][name];primitives=pinned['real_component_primitives'];coefficient_work=pinned['coefficient_work_primitive_count']")
            s=s.replace("z['events']==21495+2*promoted and z['macros']==16294","z['events']==pinned['events'] and z['macros']==pinned['macros']")
            s=s.replace("Q(88876257700 if name=='forward' else 1044730572396)","Q(pinned['prefix_l1'])")
            s=s.replace('==72*16294',"==sum(PROVIDERS[c['provider_id']]['expected_local'][c['orientation']]['macros'] for c in calls)")
            s=s.replace('0.001602631813774414678548','0.001603248695587935849402').replace('0.001602631810982070093186','0.001603248692797211432214')
            s=s.replace('0.001600067494703216','0.001600682403612293').replace('0.001600067491919801','0.001600682400830496')
            s=s.replace('expected={1:169056,2:41184,3:25968,4:13824,5:4032,6:4032,7:48,8:576,48:1808}','expected={1:169056,2:40428,3:26472,4:13824,5:4032,6:4032,7:48,8:576,48:1808}')
            s=s.replace("gain_over_pinned564_percent=dec(100*(k/Q('0.001593134158181640')-1))","gain_over_pinned569_percent=dec(100*(k/Q('0.001600067494703216')-1))")
            s=s.replace('Two fixed plain/width-seven per-invocation providers','Two fixed plain/composed-prefix-multicold per-invocation providers')
        (a.out/p.name).write_text(s)

if __name__=='__main__':main()
