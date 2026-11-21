"""Multiply private or external signed scalar words with difference-form Karatsuba."""

def word_product(x, y):
    bits = max(x.bit_length(), y.bit_length())
    if bits <= 192:
        return x*y
    if x < 0 or y < 0:
        value = word_product(abs(x), abs(y))
        return -value if (x < 0) != (y < 0) else value
    if not x or not y:
        return 0
    k = (bits+1)//2
    mask = (1 << k)-1
    a, b = x >> k, x & mask
    c, d = y >> k, y & mask
    high = word_product(a,c)
    low = word_product(b,d)
    middle = high+low-word_product(a-b,c-d)
    return (high << (2*k))+(middle << k)+low
