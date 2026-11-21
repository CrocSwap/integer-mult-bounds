/* Benchmark adapter for the public GMP packed-integer interface. */
#include <gmp.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

int short_product(const uint8_t *a, size_t na, const uint8_t *b, size_t nb,
                  uint8_t *out, size_t capacity)
{
    if (capacity < na || capacity - na < nb)
        return 1;
    mpz_t x, y, z;
    mpz_inits(x, y, z, NULL);
    mpz_import(x, na, -1, 1, 0, 0, a);
    mpz_import(y, nb, -1, 1, 0, 0, b);
    mpz_mul(z, x, y);
    size_t used = 0;
    mpz_export(out, &used, -1, 1, 0, 0, z);
    memset(out + used, 0, capacity - used);
    mpz_clears(x, y, z, NULL);
    return 0;
}
