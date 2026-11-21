import sys,re; sys.set_int_max_str_digits(0)
src=open('<research-tree>/lean/decoder-duality/Nov15/BlockComplete.lean').read()
bm=int(re.search(r'def listedBM : Nat := (\d+)',src).group(1))
allbm=0
n=0
for k in range(512*512):
    if (bm>>k)&1:
        a,b=k%512,k//512; z=a^b
        for (x,y) in ((a,b),(b,a),(a,z),(z,a),(b,z),(z,b)):
            allbm|=1<<(x+512*y)
print(bin(allbm).count('1'))
mask=(1<<16384)-1
pieces=[(allbm>>(16384*i))&mask for i in range(16)]
open('bmdata.lean','w').write("/-- all 6 ordered pairs of every certified line, split into 16 pieces of 16384 bits -/\ndef bmL : List Nat := [\n  "+",\n  ".join(map(str,pieces))+"]\n")
