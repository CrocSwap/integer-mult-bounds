"""Compare complete stable mathematical outputs and retain typed claim boundaries."""
import hashlib,json
from fractions import Fraction
def need(ok,s):
    if not ok:raise ValueError(s)
def read(root,path):return json.loads((root/path).read_bytes())
def stable(value,drop):
    need(set(drop)<= {'seconds','elapsed_seconds','peak_rss_kib'},'Unapproved mathematical receipt exclusion')
    result=dict(value)
    for name in drop:result.pop(name,None)
    return result
def validate(package,workspace,commands):
    summaries={}
    for command in commands:
        rows=[]
        for output in command['outputs']:
            actual=read(workspace,output['path']);expected=read(package,output['expected'])
            need(stable(actual,output['drop'])==stable(expected,output['drop']),'Changed mathematical output: '+command['name']+'/'+output['path'])
            rows.append({'path':output['path'],'all_stable_fields_equal':True,'ignored_only':output['drop'],'fresh_sha256':hashlib.sha256((workspace/output['path']).read_bytes()).hexdigest()})
        summaries[command['name']]=rows
    claims=read(package,'CLAIMS.json')
    need(Fraction(claims['candidate_kappa'])-Fraction(claims['comparison_kappa'])==Fraction(1,200000000000),'Incorrect kappa difference')
    need(claims['raw_signed_profile_changed'] is False and claims['raw_ceiling_changed'] is False,'False economic gain')
    need(claims['selected_record_changed'] is False and claims['new_unconditional_or_formal_kernel_theorem'] is False,'Unsupported selected/formal claim')
    need(claims['global_extra_paid_H8']==claims['global_extra_productive_H8']==144,'Missing neutral paid or target jobs')
    need(claims['scientific_status']=='PASS_CONDITIONAL_COMPLETE_CONJUNCTION','No completed conditional conjunction')
    names={c['name'] for c in commands}
    need({'source-loading','helper-aliases','local','global','invoice-funding','precision','conjunction'}<=names,'Incomplete scientific replay schedule')
    return summaries
