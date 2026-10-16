"""Exact integer Gram determinants for the immutable PR300 selected bases.

This checks nondegeneracy, not PR300 source-span or chronological admission.
"""
import source_data as sd
import json

def det(a):
    a=[r[:]for r in a];n=len(a);prior=1;sign=1
    for k in range(n-1):
        p=next((r for r in range(k,n)if a[r][k]),None)
        if p is None:return 0
        if p!=k:a[k],a[p]=a[p],a[k];sign=-sign
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                numerator=a[i][j]*pivot-a[i][k]*a[k][j]
                assert numerator%prior==0;a[i][j]=numerator//prior
            a[i][k]=0
        prior=pivot
    return sign*a[-1][-1]

def basis_receipt(selection):
    bases={}
    for row in selection['entries']:
        B=row['new_basis'];n=row['new_dimension'];assert len(B)==n
        assert all(len(r)==24 and all(type(x)is int for x in r)for r in B)
        key=tuple(tuple(r)for r in B)
        if key not in bases:
            gram=[[9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)for b in B]for a in B]
            determinant=det(gram);assert determinant
            remaining=abs(determinant);factors={}
            for prime in (2,3,5):
                exponent=0
                while remaining%prime==0:remaining//=prime;exponent+=1
                if exponent:factors[prime]=exponent
            assert remaining==1
            bases[key]=dict(dimension=n,gram_determinant=determinant,absolute_determinant_bits=abs(determinant).bit_length(),prime_factorization=factors)
    return dict(unique_selected_bases=len(bases),nondegenerate_over_Q=True,
        maximum_gram_determinant_bits=max(x['absolute_determinant_bits']for x in bases.values()),
        all_gram_prime_factors=[2,3,5],nondegenerate_over_every_field_of_characteristic_above5=True,
        bases=list(bases.values()),scope='Exact nondegeneracy and row independence only; actual chronological frame replacement requires a separate check.')


def run():
    return basis_receipt(sd.read_json('pr300/descent2-selection.json'))

if __name__=='__main__':
    if not __debug__: raise RuntimeError('Assertions required')
    print(json.dumps(run(),indent=2))
