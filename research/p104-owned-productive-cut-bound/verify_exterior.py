"""Independent dense exact probe for the fixed-cut owned-helper gate."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import alarm

ROOT=Path(__file__).resolve().parent


def main():
    assert __debug__
    alarm(20)
    blob=(ROOT/'7481-WORD.json.gz').read_bytes()
    assert sha256(blob).hexdigest()=='acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
    raw=decompress(blob)
    assert sha256(raw).hexdigest()=='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
    word=loads(raw)
    tape=word['program']
    source, start, stop = 1533, 38139, 42503
    assert tape[start]==['INIT',source,597] and tape[stop]==['CLEAR',source,591]
    n=word['public']+word['owned_fields']
    values=[Fraction(0)]*n
    charts=word['initial']+[None]*word['owned_fields']
    writes={}
    for t,(op,r,*a) in enumerate(tape[:stop]):
        if op=='INIT':
            assert charts[r] is None and not values[r]
            charts[r]=a[0]
            if t==start:
                values[r]=Fraction(1)
        elif op=='CLEAR':
            assert charts[r]==a[0]
            charts[r]=None
            values[r]=Fraction(0)
        elif op=='MOVE':
            assert charts[r]==a[0]
            charts[r]=a[1]
        elif op=='SCALE':
            assert charts[r]==a[-1]
            values[r]*=Fraction(a[0])
        else:
            assert op in ('ADD','COPY') and charts[r]==charts[a[0]]==a[-1]
            if op=='COPY':
                assert not values[r]
            new=values[r]+Fraction(a[1])*values[a[0]]
            if new!=values[r]:
                writes[r]=t
            values[r]=new
    assert charts[source]==591
    assert all(charts[j] is not None for j,v in enumerate(values) if v)
    outside=[[j,charts[j],str(v),writes.get(j)] for j,v in enumerate(values) if v and charts[j]!=591]
    alarm(0)
    print(dumps({'start':start,'cut':stop,'source':source,
                 'coframe':[j for j,c in enumerate(charts) if c==591],
                 'exterior':outside},indent=2,sort_keys=True))


if __name__=='__main__':
    main()
