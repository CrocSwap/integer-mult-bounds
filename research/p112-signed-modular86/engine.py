"""Exact signed E8-minor determinants, with the caller's rational fallback."""
PRIME=521
if not all(PRIME%d for d in range(2,23)):
    raise ValueError('fixed modulus is not prime')

def eligible(rows):
    n=len(rows)
    return n<=8 and all(len(row)==n and all(type(x) is int for x in row)
                        and sum(x*x for x in row)<=4 for row in rows)

def recover(residue,modulus,bound):
    if modulus<=2*bound or not 0<=residue<modulus:
        raise ValueError('insufficient modulus or invalid residue')
    result=residue if residue<=modulus//2 else residue-modulus
    if abs(result)>bound:
        raise ValueError('balanced determinant exceeds checked Hadamard bound')
    return result

def determinant(rows,fallback):
    if not eligible(rows):
        return fallback(rows)
    n=len(rows);a=[[x%PRIME for x in row] for row in rows];answer=1
    for k in range(n):
        pivot=next((i for i in range(k,n) if a[i][k]),None)
        if pivot is None:
            return 0
        if pivot!=k:
            a[k],a[pivot]=a[pivot],a[k];answer=-answer
        value=a[k][k];answer=answer*value%PRIME;inv=pow(value,-1,PRIME)
        for i in range(k+1,n):
            factor=a[i][k]*inv%PRIME
            if factor:
                for j in range(k+1,n):
                    a[i][j]=(a[i][j]-factor*a[k][j])%PRIME
            a[i][k]=0
    return recover(answer,PRIME,2**n)
