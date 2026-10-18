# SPDX-License-Identifier: Apache-2.0
"""Independent phase-table verifier. Does not import the repair implementation."""
from pathlib import Path
from math import isqrt
import argparse,csv,hashlib,io,json

def require(ok,message):
    if not ok:raise ValueError(message)

def table(raw):
    rows=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))));require(bool(rows),'empty table')
    result=[]
    for row in rows:
        require(bool(row),'empty CSV row');values=[]
        for cell in row:
            s=cell.strip();require(bool(s) and s.lstrip('+-').isdecimal() and s not in ('+','-'),'integer code required');values.append(int(s))
        result.append(values)
    return result

def verify(received,completed):
    n=len(received);require(n>=2 and all(n%d!=0 for d in range(2,isqrt(n)+1)),'prime order required')
    require(all(len(row)==n-1 for row in received),'input shape')
    require(len(completed)==n and all(len(row)==n for row in completed),'output shape')
    require(all(type(x)is int for row in received+completed for x in row),'integer matrix')
    require(all(completed[i][:-1]==received[i] for i in range(n)),'received columns changed')
    require(completed[0][-1]==0,'first new phase must be zero')
    # A different implementation: direct arrays, not Counter or missing phases.
    checked=0
    for left in range(n):
        for right in range(left+1,n):
            histogram=[0]*n
            for row in completed:histogram[(row[left]-row[right])%n]+=1
            require(histogram==[1]*n,'full column orthogonality failed');checked+=1
    return dict(status='PASS_INDEPENDENT_EXACT_PHASE_ORTHOGONALITY',order=n,column_pairs=checked,
                preserved_received_columns=True,first_added_phase=0,
                interpretation='For zeta=exp(2*pi*i/p), H_ij=zeta**E_ij has H*H=pI.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--received',type=Path,required=True);p.add_argument('--completed',type=Path,required=True);a=p.parse_args()
    rb=a.received.read_bytes();cb=a.completed.read_bytes();result=verify(table(rb),table(cb))
    require(a.received.read_bytes()==rb and a.completed.read_bytes()==cb,'input drift')
    result.update(received_sha256=hashlib.sha256(rb).hexdigest(),completed_sha256=hashlib.sha256(cb).hexdigest());print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
