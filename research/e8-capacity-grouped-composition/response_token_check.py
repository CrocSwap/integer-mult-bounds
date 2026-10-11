"""Whole emitted response/main/cleanup endpoint check from independent helper tokens.

Run: python -B response_token_check.py CANDIDATE LOCAL-PROGRAMS.JSON.GZ OUTPUT.JSON
This strengthens the upstream overlay check without editing upstream sources.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import gzip,json,sys
if not __debug__:
    raise RuntimeError('Response token verification requires assertions enabled')
sys.dont_write_bytecode=True

def check(candidate_path,program_path,output_path):
    candidate_path,program_path,output_path=map(Path,(candidate_path,program_path,output_path))
    assert not output_path.exists(),'token receipt requires a fresh output path'
    data=candidate_path.read_bytes();c=json.loads(data)
    raw=gzip.decompress(program_path.read_bytes());local=json.loads(raw)
    candidate_sha=sha256(data).hexdigest();assert local['candidate_sha256']==candidate_sha
    n,v=2*c['v']+c['R'],c['v'];ext=dict(c['ext'])
    assert (n,v,c['R'],len(ext))==(1021,120,781,215)
    assert len(ext)==len(c['ext']) and all(240<=r<n and c['start'][r]==f for r,f in ext.items())
    def initial():
        return {('L',i):{(i,'T_inverse_'+str(i) if i in ext else 'I'):Q(1)}for i in range(n)}
    def run(events):
        state=initial()
        for event in events:
            if event[0]!='scalar':continue
            _,phase,e,frame=event
            assert phase in ['old_response','main','cleanup']
            op=e[0];target=tuple(e[1])
            if op=='clear':state[target]={}
            elif op=='copy':state[target]=dict(state.get(tuple(e[2]),{}))
            else:
                assert op=='add'
                source=dict(state.get(tuple(e[2]),{}));weight=Q(e[3],e[4]);row=state.setdefault(target,{})
                for key,value in source.items():
                    new=row.get(key,Q(0))+weight*value
                    if new:row[key]=new
                    else:row.pop(key,None)
        return state
    results={};controls=[]
    for orientation,events in local['local_programs'].items():
        assert orientation in ['forward','backward']
        phases=[e[1]for e in events if e[0]=='phase']
        assert phases==['old_response','ad0','A','centers','B','final','adF','cleanup','done']
        first=events.index(['phase','ad0'])
        prefix=events[:first]
        assert all(e[1]=='old_response'for e in prefix if e[0]=='scalar')
        pre=run(prefix);start=initial()
        assert all(pre['L',i]==start['L',i]for i in ext)
        assert all(not any(key[0]in ext for key in row)for register,row in pre.items()if register not in [('L',i)for i in ext])
        actual=run(events);expected=initial()
        for i in range(v):
            target,source,q=(v+i,i,Q(1))if orientation=='forward'else(i,v+i,Q(-1))
            expected['L',target][source,'I']=q
        assert all(actual[key]==row for key,row in expected.items())
        assert all(not row for key,row in actual.items()if key[0]!='L')
        assert all(actual['L',i]==start['L',i]for i in range(240,n))
        # Omit the first actual entrance add in each fully serialized orientation.
        changed=list(events);position=next(i for i,e in enumerate(changed)if e[0]=='scalar'and e[1]=='main')
        omitted=changed.pop(position);assert omitted[2][0]=='add'
        mutant=run(changed);different=[i for i in range(n)if mutant['L',i]!=expected['L',i]]
        assert different,'omitted entrance add unexpectedly accepted'
        controls.append(dict(orientation=orientation,name='omit_first_actual_entrance_add',rejected=True,omitted_event=omitted,nonmatching_live_rows=len(different)))
        refs=[]
        for e in prefix:
            if e[0]!='scalar':continue
            op=e[2]
            refs.extend(op[1:3] if op[0]in ['copy','add']else op[1:2])
        gauge_refs=sum(tuple(reg)==('L',r)for reg in refs for r in ext)
        results[orientation]=dict(independent_live_columns=n,independent_helper_operator_tokens=len(ext),helper_diagonal_entries=781,
            offdiagonal_helper_entries=0,helper_data_couplings=0,private_work_nonzero=0,
            old_response_literal_gauged_references=gauge_refs,old_response_gauged_offdiagonal_endpoint_entries=0,
            scalar_events=sum(e[0]=='scalar'for e in events))
    assert set(results)=={'forward','backward'}
    receipt=dict(status='PASS_WHOLE_EMITTED_RESPONSE_MAIN_CLEANUP_INDEPENDENT_HELPER_TOKENS',
        candidate_sha256=candidate_sha,local_programs_uncompressed_sha256=sha256(raw).hexdigest(),results=results,controls_rejected=controls,
        algorithm='Execute the actual serialized scalar projection of the entire response/main/cleanup once from215 independently labelled helper input operators. No overlay and no internal chart commutation assumption.',
        scope='Finite scalar endpoint premise under the separately verified frame/child model. Exact Gaussian boundary normalization, source-bound phases, banks and global invoices are separate checks. Inherited all-size/compiler/correlated-bank/chart/precision/restored-row and analytic obligations remain conditional.')
    output_path.parent.mkdir(parents=True,exist_ok=True)
    output_path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt

if __name__=='__main__':
    assert len(sys.argv)==4
    r=check(*sys.argv[1:]);print(r['status'])
