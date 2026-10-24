"""Packed binary IO for bounded-word tabulated TM simulation.
Apache-2.0. Dugongue with substantial OpenAI Codex assistance.
This is a finite operational model, not emitted RamStd code or a Lean proof.
"""
import itertools
import json
import random


def need(p,why):
    if not p: raise ValueError(why)

class Codec:
    def __init__(self,r,c=2,w=64):
        need(r>=1 and r&(r-1)==0 and c>=2 and c&(c-1)==0,'power-of-two shape')
        need(2*c*r+8<w,'bounded-word table/address envelope')
        self.r,self.c,self.w=r,c,w
        self.rlog=r.bit_length()-1; self.clog=c.bit_length()-1
        self.bmask=(1<<r)-1;self.smask=(1<<c)-1;self.cmask=(1<<(c*r))-1
        self.setup_ops=0;self.ops=0
        # Explicit enumeration: no multiplication oracle or supplied lookup table.
        self.encode=[];self.encode_reverse=[]
        for x in range(1<<r):
            y=z=0
            for j in range(r):
                y |= (1+((x>>j)&1)) << (j<<self.clog)
                z |= (1+((x>>(r-1-j))&1)) << (j<<self.clog)
                self.setup_ops+=30
            self.encode.append(y);self.encode_reverse.append(z);self.setup_ops+=8
        self.decode=[]
        for packed in range(1<<(c*r)):
            length=value=0;valid=True
            for j in range(r):
                symbol=(packed>>(j<<self.clog))&self.smask;self.setup_ops+=12
                if symbol==0: break
                if symbol not in (1,2):valid=False;break
                value=(value<<1)|(symbol-1);length+=1;self.setup_ops+=12
            self.decode.append((length,value,valid));self.setup_ops+=12
        need(self.setup_ops<=100*r*(1<<(c*r)),'setup instruction envelope')

    def pack_bits(self,bits):
        # Test/caller convenience, not used inside the charged codec.
        return [sum(b<<j for j,b in enumerate(bits[i:i+self.r])) for i in range(0,len(bits),self.r)]

    def _append(self,out,buffer,used,value,length,field_bits):
        # Reservoir contains fewer than r fields before the call; add <=r more.
        # field_bits is fixed power of two, so all field scaling is a shift.
        flog=field_bits.bit_length()-1
        buffer |= value << (used<<flog);used+=length;self.ops+=10
        need(buffer<(1<<self.w),'reservoir overflow')
        if used>=self.r:
            out.append(buffer & ((1<<(self.r<<flog))-1))
            buffer >>= self.r<<flog;used-=self.r;self.ops+=12
        return buffer,used

    def input_to_tm(self,digits,n,order='msb'):
        """n logical bits in little-endian r-bit digits -> packed c-bit TM cells.
        order selects TM's bit order; no uncharged bit-by-bit input is read.
        """
        need(order in ('msb','lsb') and n>=0 and n+self.r<(1<<self.w),'input protocol')
        count=(n+self.r-1)>>self.rlog
        need(len(digits)==count,'packed input length')
        out=[];buffer=used=0
        for index in (range(count-1,-1,-1) if order=='msb' else range(count)):
            length=min(self.r,n-(index<<self.rlog))
            x=digits[index];need(0<=x<(1<<length),'unused input digit bits nonzero')
            self.ops+=12
            if order=='msb':
                value=self.encode_reverse[x] >> ((self.r-length)<<self.clog)
            else:value=self.encode[x]&((1<<(length<<self.clog))-1)
            self.ops+=10
            buffer,used=self._append(out,buffer,used,value,length,self.c)
        if used:out.append(buffer);self.ops+=2
        return out

    def tm_to_output(self,chunks,cap):
        """Read MSB-first coded prefix until blank, capped at cap symbols.
        Return exactly ceil(cap/r) little-endian binary digits, high bits zero.
        Chunks beyond the first terminator are not read or required.
        """
        need(cap>=0 and cap+self.r<(1<<self.w),'output cap')
        if cap==0:return []
        remaining=cap;seen=[]
        for raw in chunks:
            if remaining==0:break
            length=min(remaining,self.r)
            need(0<=raw<=self.cmask,'coded chunk word bound')
            code=raw&((1<<(length<<self.clog))-1);self.ops+=10
            got,value,valid=self.decode[code];self.ops+=8
            need(valid,'invalid output symbol before terminator')
            seen.append((got,value));self.ops+=4
            remaining-=got;self.ops+=4
            if got<length or remaining==0:break
        else:
            need(remaining==0 or (seen and seen[-1][0]<self.r) or cap==0,'truncated output without terminator')
        out=[];buffer=used=0
        for length,value in reversed(seen):
            self.ops+=4
            buffer,used=self._append(out,buffer,used,value,length,1)
        if used:out.append(buffer);self.ops+=2
        total=(cap+self.r-1)>>self.rlog;self.ops+=6
        while len(out)<total:out.append(0);self.ops+=4
        need(len(out)==total,'output width')
        if out and cap&(self.r-1):out[-1]&=(1<<(cap&(self.r-1)))-1;self.ops+=6
        return out


def check():
    cases=0;ops=0;setup=0;mutations=0
    rng=random.Random(20261022)
    for r,c in [(1,2),(2,2),(4,2),(8,2),(1,4),(2,4),(4,4)]:
        codec=Codec(r,c);setup+=codec.setup_ops
        fixtures=[]
        for n in range(9):fixtures.extend((n,list(b)) for b in itertools.product((0,1),repeat=n))
        for _ in range(100):
            n=rng.randrange(1,513);fixtures.append((n,[rng.randrange(2) for _ in range(n)]))
        for n,bits in fixtures:
            digits=codec.pack_bits(bits)
            for order in ('lsb','msb'):
                before=codec.ops;coded=codec.input_to_tm(digits,n,order)
                logical=bits if order=='lsb' else list(reversed(bits))
                want=[sum((1+b)<<(j<<codec.clog) for j,b in enumerate(logical[i:i+r])) for i in range(0,n,r)]
                need(coded==want,'packed input codec mismatch')
                need(codec.ops-before<=100*((n+r-1)//r+1),'input operation envelope')
            # The output bit string is the usual MSB word, possibly with leading zeros.
            cap=n+rng.randrange(9)
            symbols=[1+b for b in bits]
            if cap>n:symbols += [0]+[rng.randrange(1<<c) for _ in range(r+2)]
            raw=[sum(s<<(j<<codec.clog) for j,s in enumerate(symbols[i:i+r])) for i in range(0,len(symbols),r)]
            before=codec.ops;actual=codec.tm_to_output(raw,cap)
            value=int(''.join(map(str,bits)) or '0',2)
            expected=[(value>>(i*r))&codec.bmask for i in range((cap+r-1)//r)]
            need(actual==expected,'packed MSB output codec mismatch')
            need(codec.ops-before<=160*((cap+r-1)//r+1),'output operation envelope')
            cases+=1
        # Real corrupted decoder entry must break a fixed integer-value example.
        raw=codec.input_to_tm(codec.pack_bits([1]),1,'msb')[0]
        old=codec.decode[raw];codec.decode[raw]=(1,0,True)
        need(codec.tm_to_output([raw],1)!=[1],'decoder fault escaped');codec.decode[raw]=old;mutations+=1
        # Invalid symbol before terminator rejects; dirty data after blank does not.
        try:codec.tm_to_output([3],1)
        except ValueError:pass
        else:raise ValueError('invalid symbol accepted')
        need(codec.tm_to_output([0],1)==[0],'empty-zero output')
        ops+=codec.ops
    return dict(status='PASS',packed_io_cases=cases,charged_codec_operations=ops,charged_setup_operations=setup,
                corrupted_decoder_controls=mutations,invalid_output_symbols_rejected=True,
                leading_zeros=True,dirty_post_terminator=True,partial_chunks=True,
                word_multiplication_or_division=False,emitted_RamStd_program=False,Lean_proof=False)

if __name__=='__main__':print(json.dumps(check(),indent=2))
