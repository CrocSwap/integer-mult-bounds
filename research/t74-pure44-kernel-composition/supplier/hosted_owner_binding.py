"""Bind the emitted hosted role map to the exact OWNERS input used by admission.

Read-only successor guard for the metadata boundary identified in PR1959 and
executed by PR2301. The retained emitter/auditors are not modified.
Apache-2.0; prepared with OpenAI Codex assistance.
"""
from pathlib import Path
import argparse,gzip,hashlib,json


def need(ok,message):
    if not ok:raise ValueError(message)


def load(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw)if path.suffix=='.gz'else raw)


def check_link(template,owners,owner_archive_sha256):
    need(isinstance(template,dict)and isinstance(template.get('hosting'),dict),'missing hosted owner map')
    hosting=template['hosting']
    need(isinstance(owners,list)and isinstance(hosting.get('pooled_slots'),list),'invalid complete owner map')
    need(hosting['pooled_slots']==owners,'hosted pooled_slots differ from exact OWNERS input')
    need(hosting.get('owner_map_sha256')==owner_archive_sha256,'hosted owner_map_sha256 differs from exact OWNERS archive')


def run(template_path,owners_path,assembly_path):
    template=load(template_path);owners=load(owners_path);assembly=load(assembly_path)
    owner_sha=hashlib.sha256(owners_path.read_bytes()).hexdigest()
    payload=gzip.decompress(template_path.read_bytes())
    template_sha=hashlib.sha256(payload).hexdigest()
    need(assembly['status']=='PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY','wrong assembly status')
    need(assembly['template_sha256']==template_sha,'guard template differs from admitted assembly template')
    check_link(template,owners,owner_sha)
    need(owners and all(type(r.get('time'))is int for r in owners),'invalid owner invocation times')
    i=0;j=next((j for j,r in enumerate(owners)if r['time']!=owners[i]['time']and r['width']==owners[i]['width']),None)
    need(j is not None,'retiming control requires distinct equal-width invocations')
    controls=[]
    def reject(name,bad,expected):
        try:check_link(bad,owners,owner_sha)
        except ValueError as exc:
            need(str(exc)==expected,'control rejected for wrong predicate: '+name)
            controls.append({'name':name,'reason':str(exc)})
        else:raise ValueError('accepted corrupted hosted metadata: '+name)
    # Shallow clone the container and only the two changed roles: retained inputs
    # and every untouched template field remain identical, without a huge deepcopy.
    slots=list(template['hosting']['pooled_slots']);slots[i]=dict(slots[i],time=owners[j]['time']);slots[j]=dict(slots[j],time=owners[i]['time'])
    bad=dict(template,hosting=dict(template['hosting'],pooled_slots=slots))
    reject('equal_width_role_times_exchanged',bad,'hosted pooled_slots differ from exact OWNERS input')
    wrong='0'*64 if owner_sha!='0'*64 else'1'*64
    bad=dict(template,hosting=dict(template['hosting'],owner_map_sha256=wrong))
    reject('wrong_owner_map_archive_sha256',bad,'hosted owner_map_sha256 differs from exact OWNERS archive')
    return dict(status='PASS_HOSTED_OWNERS_CROSS_STAGE_BINDING',roles=len(owners),all_role_fields_equal=True,role_times_included=True,owner_archive_sha256=owner_sha,admitted_template_payload_sha256=template_sha,mutations_rejected=controls,scope='Exact emitted hosted metadata equals the complete OWNERS input; separate admission verifies role feasibility, native operators, invoice and outer constraints.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for flag in ['hosted','owners','assembly','out']:ap.add_argument('--'+flag,type=Path,required=True)
    a=ap.parse_args();need(not a.out.exists(),'fresh receipt path required')
    need(a.out.resolve()not in{p.resolve()for p in[a.hosted,a.owners,a.assembly]},'receipt must not replace an input')
    receipt=run(a.hosted,a.owners,a.assembly)
    a.out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()
