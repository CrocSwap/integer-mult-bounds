"""Check the exact chart-737 separating input without using a reverse solver."""
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
CUT,CHART=39826,737
BANK=(1451,1495,1501)
PROBE={3:Q(-1),716:Q(1)}


def timeout(signum,frame):
    print(dumps({'status':'unresolved_timeout','cases_completed':0,'runner_cap_seconds':30}))
    exit(124)


def forward(word,probe):
    public=word['public']
    rows=[probe.get(i,Q(0))for i in range(public)]+[None]*word['owned_fields']
    charts=word['initial']+[None]*word['owned_fields']
    for op,r,*a in word['program'][:CUT]:
        if op=='INIT':
            assert rows[r] is None and charts[r] is None
            rows[r],charts[r]=Q(0),a[0]
        elif op=='CLEAR':
            assert charts[r]==a[0]
            rows[r],charts[r]=None,None
        elif op=='MOVE':
            assert charts[r]==a[0] and a[2]==(r>=public)
            charts[r]=a[1]
        elif op=='SCALE':
            assert charts[r]==a[1]
            rows[r]*=Q(a[0])
        else:
            src,q,chart=a
            assert op in ('ADD','COPY') and charts[r]==charts[src]==chart
            if op=='COPY':assert rows[r]==0
            rows[r]+=Q(q)*rows[src]
    assert tuple(i for i,c in enumerate(charts)if c==CHART)==BANK
    return [rows[r]for r in BANK]


def main():
    assert __debug__
    signal(SIGALRM,timeout);alarm(30)
    packed=(ROOT/'7481-WORD.json.gz').read_bytes()
    assert sha256(packed).hexdigest()==WORD
    raw=decompress(packed)
    assert sha256(raw).hexdigest()==PAYLOAD
    word=loads(raw); tape=word['program']
    assert tape[37945]==['MOVE',1451,595,737,False]
    assert tape[CUT-1:CUT+1]==[['ADD',1451,1495,'-1',737],['MOVE',1495,737,738,False]]
    assert tape[39877:39881]==[['MOVE',1451,737,529,False],['ADD',992,1451,'1',529],
                             ['ADD',1451,146,'2',529],['ADD',1451,228,'1',529]]
    assert [i for i,c in enumerate(word['initial'])if c==595]==[1451,1495]
    assert not set(PROBE).intersection((1451,1495))
    old=forward(word,PROBE)
    control=forward(word,{i:-q for i,q in PROBE.items()})
    zero=forward(word,{})
    assert old==[1,0,0] and control==[-1,0,0] and zero==[0,0,0]
    alarm(0)
    print(dumps({'status':'PASS_FIXED_1451_INPUT_WITNESS','cases_completed':1,'case_cap':1,
                 'runner_cap_seconds':30,'word_sha256':WORD,'payload_sha256':PAYLOAD,
                 'cut':CUT,'chart':CHART,'bank':BANK,'probe':PROBE,'old_bank_values':old,
                 'opposite_control':control,'zero_control':zero,'allowed_initial_roles':[1451,1495]},
                sort_keys=True,indent=2,default=str))


if __name__=='__main__':main()
