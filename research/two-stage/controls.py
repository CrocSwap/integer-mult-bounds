"""Exact bit-array endpoint/copy checks, including arbitrary dirty scratch.
Zhihao Chen (jacklightChen), with Codex assistance. Apache-2.0.
"""
def xor(x,y):return [a^b for a,b in zip(x,y)]
def perm(x,mask):return [x[i^mask] for i in range(len(x))]
def shear(x,y,z):
    # Identity producer L on a one-role witness: chronological J,V,J,V.
    y=xor(y,z);z=xor(z,x);y=xor(y,z);z=xor(z,x)
    return x,y,z
def run():
    count=0
    # Complete linear basis of two four-cell data streams and two dirty banks.
    for column in range(16):
        streams=[[int(4*j+i==column) for i in range(4)] for j in range(4)]
        x,y,z1,z2=streams
        # U swaps one address coordinate, its complement the other.
        # Auxiliary2 has nonzero source D0=E and complementary sink P.
        X,Y,Z1,Z2=perm(x,1),y[:],z1[:],perm(z2,2)
        X,Y,Z1=shear(X,Y,Z1)
        Y,X,Z2=shear(Y,X,Z2)
        A,B=perm(X,3),perm(Y,2)
        out1,out2=perm(Z1,3),perm(Z2,1)
        assert A==perm(y,3)
        assert B==xor(perm(x,3),perm(y,2))
        corrected=xor(B,perm(A,1))
        assert corrected==perm(x,3) and out1==perm(z1,3) and out2==perm(z2,3)
        count+=1
    x=[0]*4;y=[1,0,0,0]
    B=perm(y,2)
    assert B!=x  # Omitting the correction does not implement interchange.
    return dict(complete_input_basis_columns=count,dirty_banks=2,copy_correction_rank=1,
                omitted_correction_rejected=True,scope='Exact endpoint composition control; full producers independently verified')
