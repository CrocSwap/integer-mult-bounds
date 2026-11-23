"""Exact ordered native restoration lists; no opaque matcher dictionary."""
from fractions import Fraction
from codec import Writer,Reader
from source_loader import need


class RestoreCodec:
    def __init__(self,n,width,owners,ports=18906):
        self.n=n;self.width=width;self.owners=owners;self.ports=ports
        self.h=(n-1).bit_length();need(n>=2 and owners<1<<width,'restore dimensions')
    def put_word(self,out,word):
        need(len(word)<=123*self.n,'matcher length');out.put(len(word),self.width)
        for item in word:
            op,i,*tail=item;need(op in ('swap','add','scale') and 0<=i<self.n,'operation target')
            if op=='scale':need(len(tail)==1,'scale arity');j=0;q=Fraction(tail[0]);need(q!=0,'zero scale');tag=2
            else:
                need(len(tail)==(1 if op=='swap' else 2),'binary operation arity')
                j=tail[0];q=Fraction(0 if op=='swap' else tail[1]);tag=0 if op=='swap' else 1
                need(isinstance(j,int) and 0<=j<self.n,'operation source')
            a,b=q.numerator,q.denominator
            need(-32<=a<32 and 1<=b<32,'restoration coefficient width')
            out.put(tag,2);out.put(i,self.h);out.put(j,self.h);out.put(a%64,6);out.put(b,5)
    def get_word(self,src):
        length=src.get(self.width);need(length<=123*self.n,'matcher length');word=[]
        for _ in range(length):
            tag=src.get(2);i=src.get(self.h);j=src.get(self.h);a=src.get(6);b=src.get(5)
            if a>=32:a-=64
            need(tag<3 and i<self.n and j<self.n and b>0,'invalid operation fields')
            q=Fraction(a,b);need(q.numerator==a and q.denominator==b,'noncanonical fraction')
            if tag==0:need(a==0 and b==1,'swap padding');word.append(('swap',i,j))
            elif tag==1:word.append(('add',i,j,q))
            else:need(j==0 and q!=0,'scale fields');word.append(('scale',i,q))
        return tuple(word)
    def pack(self,restores):
        need(len(restores)<=self.ports,'restore list length');out=Writer();out.put(len(restores),self.width)
        for owner,word in restores:
            need(isinstance(owner,int) and 0<=owner<self.owners,'restore owner');out.put(owner,self.width);self.put_word(out,word)
        return out.finish()
    def unpack(self,image):
        src=Reader(*image);count=src.get(self.width);need(count<=self.ports,'restore list count');result=[]
        for _ in range(count):
            owner=src.get(self.width);need(owner<self.owners,'restore owner');result.append((owner,self.get_word(src)))
        src.finish();return result
    def word_image(self,word):
        out=Writer();self.put_word(out,word);return out.finish()
