"""Direct bounded-word complex convolution; Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
"""
from pathlib import Path


def need(ok,why):
    if not ok:raise ValueError(why)


def source_module(name):
    p=Path(__file__).with_name(name)
    scope={'__name__':'native_component','__file__':str(p)}
    exec(compile(p.read_bytes(),str(p),'exec'),scope)
    return scope


class Convolver:
    def __init__(self,size,p,width):
        need(size>=2 and size&(size-1)==0 and p>=1,'transform shape')
        self.N=size;self.p=p;self.S=1<<p;self.width=width
        self.limit=1<<width;self.operations=0;self.maximum_bits=0
        root=source_module('root_seed.py')['root_seed'](size,p,width)
        self.operations=root['charged_word_operations'];self.maximum_bits=root['largest_intermediate_bits']
        self.roots=[(self.S,0)]
        for _ in range(1,size//2):
            self.roots.append(self.cmul(self.roots[-1],(root['real'],root['imag'])))
        self.setup_operations=self.operations

    def val(self,x):
        need(abs(x)<self.limit,'word overflow')
        self.operations+=1;self.maximum_bits=max(self.maximum_bits,abs(x).bit_length());return x

    def cmul(self,a,b):
        ac=self.val(a[0]*b[0]);bd=self.val(a[1]*b[1])
        ad=self.val(a[0]*b[1]);bc=self.val(a[1]*b[0])
        return self.val(self.val(ac-bd)//self.S),self.val(self.val(ad+bc)//self.S)

    def fft(self,data,inverse=False):
        need(len(data)==self.N,'transform array length')
        data=list(data)
        for z in data:self.val(z[0]);self.val(z[1])
        j=0
        for i in range(1,self.N):
            mask=self.N>>1
            while j&mask:j^=mask;mask>>=1;self.operations+=4
            j^=mask
            if i<j:data[i],data[j]=data[j],data[i]
            self.operations+=9
        step=2
        while step<=self.N:
            half=step>>1;stride=self.N//step
            for start in range(0,self.N,step):
                for k in range(half):
                    tw=self.roots[k*stride]
                    if not inverse:tw=(tw[0],-tw[1])
                    u=data[start+k];v=self.cmul(data[start+k+half],tw)
                    data[start+k]=(self.val(u[0]+v[0]),self.val(u[1]+v[1]))
                    data[start+k+half]=(self.val(u[0]-v[0]),self.val(u[1]-v[1]))
                    self.operations+=18
            step<<=1
        if inverse:data=[(self.val(a//self.N),self.val(b//self.N)) for a,b in data]
        return data

    def prepare(self,kernel):
        need(1<=len(kernel)<=self.N,'kernel size')
        return self.fft(list(kernel)+[(0,0)]*(self.N-len(kernel)))

    def apply(self,data,prepared,output_length):
        need(1<=len(data)<=self.N and 1<=output_length<=self.N,'convolution size')
        d=self.fft(list(data)+[(0,0)]*(self.N-len(data)))
        result=self.fft([self.cmul(x,y) for x,y in zip(d,prepared)],True)
        return result[:output_length]
