"""One exact chart-127 readout via the verified full #7481 endpoint and literal suffix."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from signal import SIGALRM,alarm,signal
from sys import exit

ROOT=Path(__file__).resolve().parent
WORD='acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
PAYLOAD='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
RECEIPT='4f2024c0a84be0389a2f0469a0ea3f27af995b17fa641211c94a34807b8624f9'
CUT,OLD,ROLE,LIVE=58937,45656,1540,1568


def authenticate(name,digest):
    raw=(ROOT/name).read_bytes()
    assert sha256(raw).hexdigest()==digest,name
    return raw


def timeout(signum,frame):
    print(dumps({'status':'unresolved_timeout','cases_completed':0,'runner_cap_seconds':30}))
    exit(124)


def add(row,j,value):
    updated=row.get(j,0)+value
    if updated:
        row[j]=updated
    else:
        row.pop(j,None)


def adjoint(events, seed):
    out=seed.copy()
    for op,r,*a in reversed(events):
        current=out.get(r,0)
        if not current or op=='MOVE':continue
        if op in ('INIT','CLEAR'):
            out.pop(r)
        elif op=='SCALE':
            out[r]=Q(a[0])*current
        else:
            assert op in ('ADD','COPY')
            if op=='COPY':out.pop(r)
            add(out,a[0],Q(a[1])*current)
    return out


def to_output_coordinates(row,word):
    """Convert t on old inputs x to t E^-1 on certified final outputs y=E x."""
    result=row.copy()
    h=word['hosted']
    a_ports=set(h['Dports'])
    for port,x in enumerate(word['live']):
        y=x+112
        a,b=result.get(x,0),result.get(y,0)
        if port in a_ports:
            add(result,x,-b)
        else:
            add(result,x,(a-b)/2-a)
            add(result,y,a+b-b)
    for x,y in zip(h['X2'],h['Y2']):
        add(result,y,result.get(x,0))
    return result


def to_input_coordinates(row,word):
    result=row.copy()
    h=word['hosted']
    a_ports=set(h['Dports'])
    for port,x in enumerate(word['live']):
        y=x+112
        a,b=result.get(x,0),result.get(y,0)
        if port in a_ports:
            add(result,x,b)
        else:
            add(result,x,b/2)
            add(result,y,-a-b/2)
    for x,y in zip(h['X2'],h['Y2']):
        add(result,y,-result.get(x,0))
    return result


def forward(events,values):
    out=values.copy()
    for op,r,*a in events:
        if op=='MOVE':continue
        if op=='INIT':
            assert not out.get(r)
        elif op=='CLEAR':
            out.pop(r,None)
        elif op=='SCALE':
            if r in out:out[r]*=Q(a[0])
        else:
            assert op in ('ADD','COPY')
            if op=='COPY':assert not out.get(r)
            add(out,r,Q(a[1])*out.get(a[0],0))
    return out


def scalar_smooth(n):
    for p in (2,3,5):
        while n%p==0:n//=p
    return n==1


def main():
    assert __debug__
    signal(SIGALRM,timeout);alarm(30)
    payload=decompress(authenticate('7481-WORD.json.gz',WORD))
    assert sha256(payload).hexdigest()==PAYLOAD
    word=loads(payload); tape=word['program']; public=word['public']
    cert=loads(authenticate('NATIVE-RESULT.json',RECEIPT))
    assert cert['status']=='PASS_CHANGED_485_1455_PRODUCER_COMPLETE_NATIVE'
    assert cert['word_canonical_sha256']==PAYLOAD and not cert['native']['bad_inputs']
    assert cert['native']['public']==public==1501 and cert['native']['events']==len(tape)
    h=word['hosted']; assert [h[k]for k in ('alpha','beta','alpha2','beta2')]==['-1','1/2','-1','0']
    active=word['initial']+[None]*word['owned_fields']
    for op,r,*a in tape[:CUT]:
        if op=='INIT':assert active[r] is None;active[r]=a[0]
        elif op=='CLEAR':assert active[r]==a[0];active[r]=None
        elif op=='MOVE':assert active[r]==a[0];active[r]=a[1]
    assert [j for j in range(public,len(active))if active[j] is not None]==[LIVE]
    bank={j for j,chart in enumerate(active)if chart==127 and j!=756}
    assert len(bank)==1046 and max(bank)<public
    assert tape[OLD:OLD+3]==[['MOVE',1540,260,1091,True],['ADD',756,1540,'1',1091],['CLEAR',1540,1091]]
    assert tape[CUT-1:CUT+1]==[['MOVE',756,1091,127,False],['ADD',870,756,'1',127]]
    source_row=adjoint(tape[:OLD],{ROLE:Q(1)})
    live_row=adjoint(tape[:CUT],{LIVE:Q(1)})
    assert len(source_row)==137 and all(j<public for j in source_row.keys()|live_row.keys())
    source_on_y=to_output_coordinates(source_row,word)
    live_on_y=to_output_coordinates(live_row,word)
    assert to_input_coordinates(source_on_y,word)==source_row
    assert to_input_coordinates(live_on_y,word)==live_row
    source_on_extended_cut=adjoint(tape[CUT:],source_on_y)
    live_on_extended_cut=adjoint(tape[CUT:],live_on_y)
    assert all(j<public or j==LIVE for j in source_on_extended_cut.keys()|live_on_extended_cut.keys())
    source_live=source_on_extended_cut.pop(LIVE,Q(0))
    feedback=live_on_extended_cut.pop(LIVE,Q(0))
    denom=1-feedback
    if not denom:
        alarm(0)
        print(dumps({'status':'unresolved_singular_live_owned_feedback','cases_completed':0,'feedback':str(feedback)}))
        return
    # The full old output y determines the original x via the certified E.
    # Hence z=live_on_y*y. Substituting y=A*x_cut+u*z eliminates z.
    result=source_on_extended_cut.copy()
    for j,value in live_on_extended_cut.items():add(result,j,source_live/denom*value)
    outside={j:value for j,value in result.items()if j not in bank}
    def verify_unit_cut(chosen):
        z=live_on_extended_cut.get(chosen,Q(0))/denom
        final=forward(tape[CUT:],{chosen:Q(1),LIVE:z})
        assert all(j<public for j in final)
        inverse=final.copy()
        for port,x in enumerate(word['live']):
            y=x+112;a,b=final.get(x,0),final.get(y,0)
            if port in set(h['Dports']):inverse[y]=b-a
            else:inverse[x]=(a/2+b);inverse[y]=b-a/2
        for x,y in zip(h['X2'],h['Y2']):inverse[x]=final.get(x,0)+final.get(y,0)
        probe={j:Q(v)for j,v in inverse.items()if v}
        cut_state=forward(tape[:CUT],probe)
        assert {j:v for j,v in cut_state.items()if j<public}=={chosen:Q(1)}
        assert cut_state.get(LIVE,0)==z
        value=forward(tape[:OLD],probe).get(ROLE,0)
        assert value==result.get(chosen,0)
        edited_prefix = tape[:OLD] + [['CLEAR', 1540, 260]] + tape[OLD+3:CUT]
        changed=forward(edited_prefix,probe)
        assert changed.get(756,0)==int(chosen==756)-value
        assert all(changed.get(j,0)==cut_state.get(j,0) for j in bank)
        return {'cut_unit':chosen,'original_probe':probe,'old_owned1540':value,
                'live_owned1568_at_cut':z,'old756_at_cut':int(chosen==756),
                'modified756_at_cut':int(chosen==756)-value}
    witness=None
    self_control=None
    if outside:
        chosen=min(outside)
        witness=verify_unit_cut(chosen)
        if chosen!=756 and not result.get(756):
            self_control=verify_unit_cut(756)
            assert witness['old756_at_cut']==0 and witness['modified756_at_cut']
            assert self_control['old756_at_cut']==self_control['modified756_at_cut']==1
    legal=not outside and all(scalar_smooth(v.denominator) and abs(v)+1<2**16 for v in result.values())
    alarm(0)
    print(dumps({'status':'EXACT_OUTSIDE_BANK_SEPARATOR' if outside else 'EXACT_BANK_REPRESENTATION',
        'cases_completed':1,'runner_cap_seconds':30,'cut':CUT,'bank_size':len(bank),'live_owned':LIVE,
        'live_owned_support':len(live_row),'target_support':len(source_row),'source_on_live_owned':source_live,
        'live_owned_feedback':feedback,'elimination_denominator':denom,'cut_coefficient_support':len(result),
        'outside_bank_coefficients':outside,'exact_cut_coefficients':result,'witness':witness,
        'self_scale_control':self_control,'all_direct_coefficients_legal':legal,
        'source_sha256':WORD,'endpoint_receipt_sha256':RECEIPT,'gross_signed_raw':17},
        sort_keys=True,indent=2,default=str))


if __name__=='__main__':main()
