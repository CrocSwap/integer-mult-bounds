/* Exact convolution for the finite range of the general multiplier. */
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define PRIME_A UINT32_C(2013265921)
#define PRIME_B UINT32_C(1811939329)
#define MAX_TRANSFORM (UINT32_C(1) << 26)

static uint32_t multiply_mod(uint32_t a, uint32_t b, uint32_t p)
{
    return (uint32_t)((uint64_t)a * b % p);
}

static uint32_t power_mod(uint32_t base, uint32_t exponent, uint32_t p)
{
    uint32_t out = 1;
    while (exponent) {
        if (exponent & 1u)
            out = multiply_mod(out, base, p);
        base = multiply_mod(base, base, p);
        exponent >>= 1;
    }
    return out;
}

/* Each block uses two forward scratch streams. No bit-reversal table is needed. */
static void transform(uint32_t *data, size_t n, uint32_t *left, uint32_t *right,
                      uint32_t p, uint32_t generator, int inverse)
{
    for (size_t h = inverse ? 1 : n / 2; h && h < n;
         h = inverse ? 2 * h : h / 2) {
        uint32_t e = (p - 1) / (uint32_t)(2 * h);
        uint32_t root = power_mod(generator, inverse ? p - 1 - e : e, p);
        for (size_t block = 0; block < n; block += 2 * h) {
            memcpy(left, data + block, h * sizeof(*left));
            memcpy(right, data + block + h, h * sizeof(*right));
            uint32_t phase = 1;
            for (size_t j = 0; j < h; ++j) {
                uint32_t a = left[j];
                uint32_t b = inverse ? multiply_mod(right[j], phase, p) : right[j];
                uint32_t sum = a + b;
                uint32_t diff = a >= b ? a - b : a + p - b;
                data[block + j] = sum >= p ? sum - p : sum;
                left[j] = inverse ? diff : multiply_mod(diff, phase, p);
                phase = multiply_mod(phase, root, p);
            }
            memcpy(data + block + h, left, h * sizeof(*left));
        }
    }
    if (inverse) {
        uint32_t scale = power_mod((uint32_t)n, p - 2, p);
        for (size_t j = 0; j < n; ++j)
            data[j] = multiply_mod(data[j], scale, p);
    }
}

static void load_words(const uint8_t *src, size_t bytes, uint32_t *dst, size_t n)
{
    size_t i = 0;
    for (; i + 1 < bytes; i += 2)
        dst[i / 2] = (uint32_t)src[i] | ((uint32_t)src[i + 1] << 8);
    if (i < bytes)
        dst[i++ / 2] = src[bytes - 1];
    memset(dst + (i + 1) / 2, 0, (n - (i + 1) / 2) * sizeof(*dst));
}

/* Return 0 on success, 1 for a bad extent, and 2 for an allocation failure.
   All supplied extents are in bytes. The inputs are unsigned and little-endian. */
int short_product(const uint8_t *a, size_t na, const uint8_t *b, size_t nb,
                  uint8_t *out, size_t capacity)
{
    if (na > 2u * MAX_TRANSFORM || nb > 2u * MAX_TRANSFORM ||
        capacity < na + nb || (na && !a) || (nb && !b) || (capacity && !out))
        return 1;
    if (!na || !nb) {
        if (capacity)
            memset(out, 0, capacity);
        return 0;
    }
    size_t wa = (na + 1) / 2, wb = (nb + 1) / 2, nc = wa + wb - 1;
    if (nc > MAX_TRANSFORM)
        return 1;
    size_t n = 1;
    while (n < nc)
        n *= 2;
    /* Three length-n fields and two half-length scratch streams. */
    uint32_t *arena = calloc(4 * n, sizeof(*arena));
    if (!arena)
        return 2;
    uint32_t *x = arena, *y = x + n, *first = y + n;
    uint32_t *left = first + n, *right = left + n / 2;
    uint32_t moduli[2] = {PRIME_A, PRIME_B}, roots[2] = {31, 13};
    for (size_t j = 0; j < 2; ++j) {
        load_words(a, na, x, n);
        load_words(b, nb, y, n);
        transform(x, n, left, right, moduli[j], roots[j], 0);
        transform(y, n, left, right, moduli[j], roots[j], 0);
        for (size_t i = 0; i < n; ++i)
            x[i] = multiply_mod(x[i], y[i], moduli[j]);
        transform(x, n, left, right, moduli[j], roots[j], 1);
        if (j == 0)
            memcpy(first, x, nc * sizeof(*first));
    }
    uint32_t inv = power_mod(PRIME_A % PRIME_B, PRIME_B - 2, PRIME_B);
    uint64_t carry = 0;
    size_t at = 0;
    for (size_t i = 0; i < nc; ++i) {
        uint32_t t = (x[i] + PRIME_B - first[i] % PRIME_B) % PRIME_B;
        carry += first[i] + (uint64_t)PRIME_A * multiply_mod(t, inv, PRIME_B);
        for (unsigned half = 0; half < 2 && at < na + nb; ++half) {
            out[at++] = (uint8_t)carry;
            carry >>= 8;
        }
    }
    while (at < na + nb) {
        out[at++] = (uint8_t)carry;
        carry >>= 8;
    }
    if (capacity > at)
        memset(out + at, 0, capacity - at);
    /* Charge retirement of the entire high-water interval. */
    volatile uint32_t *clear = arena;
    for (size_t i = 0; i < 4 * n; ++i)
        clear[i] = 0;
    free(arena);
    return carry != 0;
}
