# SPDX-License-Identifier: Apache-2.0
"""Exact completion of prime-order phase-coded orthogonal pilot columns."""
from pathlib import Path
from collections import Counter
from math import isqrt
import argparse,csv,hashlib,io,json

def need(ok, message):
    if not ok: raise ValueError(message)

def prime(n):
    return n>=2 and all(n%d for d in range(2,isqrt(n)+1))

def parse(raw):
    text=raw.decode('utf-8-sig')
    rows=list(csv.reader(io.StringIO(text)))
    need(bool(rows) and all(row and all(x.strip() for x in row) for row in rows),'nonempty CSV rows')
    out=[]
    for row in rows:
        values=[]
        for x in row:
            x=x.strip();need(x.lstrip('+-').isdigit() and x not in ('+','-'),'integer phase code')
            values.append(int(x))
        out.append(values)
    return out

def complete(received):
    p=len(received);need(prime(p),'prime row count required')
    need(all(len(row)==p-1 for row in received),'received shape must be p by p-1')
    need(all(type(x)is int for row in received for x in row),'integer phase code')
    # For prime p, a sum of p pth roots vanishes iff every phase occurs once.
    for a in range(p-1):
        for b in range(a+1,p-1):
            counts=Counter((row[a]-row[b])%p for row in received)
            need(counts==Counter(range(p)),'incoming columns are not orthogonal')
    missing=[0]
    for i in range(1,p):
        counts=Counter((received[i][j]-received[0][j])%p for j in range(p-1))
        absent=[a for a in range(p) if not counts[a]]
        need(len(absent)==1 and all(n==1 for n in counts.values()),'row missing-phase certificate failed')
        missing.append(absent[0])
    output=[row[:]+[missing[i]] for i,row in enumerate(received)]
    return output,dict(order=p,missing_phases=missing,received_column_pairs=(p-1)*(p-2)//2,
                       algorithm='B097 missing-phase completion; first added phase is zero',
                       scope='Exact root-of-unity orthogonality and literal input preservation; no channel-performance claim.')

def encode(rows):
    out=io.StringIO(newline='');csv.writer(out,lineterminator='\n').writerows(rows)
    return out.getvalue().encode('utf-8')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--certificate',type=Path,required=True);a=ap.parse_args()
    paths=[a.output.resolve(),a.certificate.resolve()];need(len(set(paths))==2 and a.input.resolve() not in paths,'distinct input and output paths required')
    raw=a.input.read_bytes();digest=hashlib.sha256(raw).hexdigest();rows=parse(raw);output,cert=complete(rows);encoded=encode(output)
    cert.update(input_sha256=digest,output_sha256=hashlib.sha256(encoded).hexdigest(),preserved_received_columns=True)
    targets={paths[0]:encoded,paths[1]:(json.dumps(cert,sort_keys=True,indent=2)+'\n').encode('utf-8')}
    locks=[]
    try:
        for p in sorted(paths):
            need(p.parent.is_dir() and not p.exists(),'fresh output in existing directory required')
            lock=p.with_name(p.name+'.lock');handle=lock.open('x');handle.write('Exclusive phase-completion output\n');handle.flush();locks.append((lock,handle))
        need(hashlib.sha256(a.input.read_bytes()).hexdigest()==digest,'input changed before output')
        for p,data in targets.items():
            with p.open('xb') as out:out.write(data)
        need(hashlib.sha256(a.input.read_bytes()).hexdigest()==digest,'input changed during output')
    finally:
        for lock,handle in reversed(locks):handle.close();lock.unlink()
    print(json.dumps(dict(status='PASS_EXACT_PRIME_PHASE_COMPLETION',order=len(rows),input_sha256=digest,output_sha256=cert['output_sha256'])))
if __name__=='__main__':main()
