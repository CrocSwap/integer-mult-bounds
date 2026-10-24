"""Compare all stable mathematical result fields, with exact frozen evidence bindings."""
import hashlib,json
from pathlib import Path
def require(ok,message):
    if not ok:raise ValueError(message)
def read(root,path):return json.loads((root/path).read_bytes())
def stable(value,drop):
    result=dict(value)
    for name in drop:result.pop(name,None)
    return result
def validate(root,scratch,commands):
    summaries={}
    for command in commands:
        actual=read(scratch,command['result']);expected=read(root,command['expected'])
        require(stable(actual,command['drop'])==stable(expected,command['drop']),'Changed mathematical receipt: '+command['name'])
        summaries[command['name']]={'all_stable_fields_equal':True,'ignored_only':command['drop'],'fresh_sha256':hashlib.sha256((scratch/command['result']).read_bytes()).hexdigest()}
    a=read(scratch,'agents/algebra/FRESH.json')
    require(a['status']=='PASS_INDEPENDENT_COUPLED_PROVIDER_COMPONENT' and a['coupled_helpers_without_target_credit']==8 and a['owned_outputs_zero']==9,'Wrong provider scope')
    b=read(scratch,'agents/budget/FRESH.json')
    require(b['coupled']['autonomous_credit']==0,'Unearned coupled helper credit')
    require(b['full_profile']['hypothetical_added_target_profile']=={'8':144},'Wrong conditional profile')
    require(b['full_profile']['eight_paid_H8_per_provider']['signed_profile_equals_reference'] is True,'Rankwise cancellation failed')
    require(b['conditional_screen']['new_kappa'] is None,'Unexpected kappa claim')
    require(b['executed_checker_sha256']==hashlib.sha256((root/'capsule/agents/budget/screen_v3.py').read_bytes()).hexdigest(),'Wrong freshly executed final budget source')
    require(b['boundary_scalar_units']==42 and b['scalar_tariff_units_including_swaps']==175022,'Wrong literal boundary tariff')
    e=read(scratch,'agents/budget/FRESH-ENVELOPE.json')
    require(e['total_max_field_l2_exponent']==18996 and e['total_joint_field_l2_exponent']==19012 and e['copy_count']==16,'Wrong local norm bounds')
    require(e['executed_checker_sha256']==hashlib.sha256((root/'capsule/agents/budget/independent_local_envelope.py').read_bytes()).hexdigest(),'Wrong freshly executed envelope source')
    return summaries
