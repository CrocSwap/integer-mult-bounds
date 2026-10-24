"""Opt-in fixed-context quotient; enlarged finite control is part of its cost.

Brian (JoyboyBrian), substantial OpenAI Codex assistance. Apache-2.0.
Based on David Arias's PR2753 fresh_rows quotient and ToikY's shared radix idea.
"""

def compile_quotient(q,dimension):
    from cardinal_counts import Count,positive
    from cardinality import radix_power
    from words import need
    need(type(q) is int and q>=2 and type(dimension) is int and dimension>0,'compiled radix/dimension')
    # Explicit square-and-multiply construction; all operands are fixed context.
    power=dimension*dimension; factor=q; high_factor=1; products=[]
    def product(a,b):
        products.append((a.bit_length(),b.bit_length()))
        return a*b
    while power:
        if power&1:high_factor=product(high_factor,factor)
        power//=2
        if power:factor=product(factor,factor)
    construction=dict(multiplications=len(products),operand_bit_pairs=products,
                      schoolbook_bit_products=sum(a*b for a,b in products),
                      stored_divisor_bits=high_factor.bit_length())
    def quotient(fresh,context,families):
        need((context.q,context.dimension)==(q,dimension),'matching compiled high divisor')
        positive(fresh)
        unused=Count(fresh)
        try:
            need(unused.divide_small(families)==0,'complete fresh family factor')
            need(unused.divide_small(context.codes.size)==0,'complete fresh GL low factor')
            first=True
            for _ in radix_power(context.ring,q):
                if first:first=False
                else:need(unused.divide_small(high_factor)==0,'complete fresh high factor')
            need(not unused.zero(),'nonempty unused row quotient')
            return unused
        except ValueError:
            unused.close()
            raise
    quotient.construction=construction
    return quotient,high_factor
