"""Literal invoice + semantic mutations, independent of source summary statuses."""
from copy import deepcopy
from . import invoice,source

def run():
    word=source.js('research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz')
    ctrl=source.js('research/joint-helper-lattice/CONTROLLER.json')
    result=invoice.assemble(word,ctrl);controls=[]
    def reject(name,w,c):
        try:invoice.assemble(w,c)
        except ValueError as e:controls.append({'name':name,'semantic_rejected':str(e)})
        else:raise ValueError('mutant accepted '+name)
    for typ in ['center','climb']:
        bad=deepcopy(word);p=bad['programs']['forward'];p.pop(next(j for j,e in enumerate(p) if e[0]==typ));reject('omitted_'+typ,bad,ctrl)
    for typ in ['QUERY_SHEAR','IDLE','LOCAL']:
        bad=deepcopy(ctrl);p=bad['physical_events'];p.pop(next(j for j,e in enumerate(p) if e[0]==typ));reject('omitted_'+typ,word,bad)
    bad=deepcopy(ctrl);bad['boundaries']['left_program'].pop(0);reject('omitted_scalar_normalizer',word,bad)
    bad=deepcopy(word);next(e for e in bad['programs']['forward'] if e[0]=='climb')[5]+=1;reject('wrong_paid_rank',bad,ctrl)
    assert result['paid_calls']==64404 and result['productive_fields']==10928 and result['rank_mass_surplus']==752
    result['status']='PASS_COMPLETE_LITERAL_P16_INVOICE';result['semantic_controls']=controls
    return result
