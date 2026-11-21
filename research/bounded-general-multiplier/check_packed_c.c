/* Run the packed ABI under address and undefined-behavior sanitizers. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

int short_product(const uint8_t *, size_t, const uint8_t *, size_t, uint8_t *, size_t);

int main(void)
{
    uint8_t a[258], b[258], out[518], want[518];
    uint32_t random = 772101;
    size_t checks = 0;
    for (size_t n = 0; n <= 257; n += 7) {
        for (size_t m = 0; m <= 257; m += 9) {
            for (size_t i = 0; i < sizeof(a); ++i) {
                random = 1664525u * random + 1013904223u;
                a[i] = n % 2 ? 255u : (uint8_t)(random >> 24);
                b[i] = m % 2 ? 255u : (uint8_t)(random >> 8);
            }
            memset(want, 0, sizeof(want));
            memset(out, 0x7f, sizeof(out));
            for (size_t i = 0; i < n; ++i) {
                unsigned carry = 0;
                for (size_t j = 0; j < m; ++j) {
                    carry += (unsigned)a[i] * b[j] + want[i+j];
                    want[i+j] = (uint8_t)carry;
                    carry >>= 8;
                }
                want[i+m] = (uint8_t)carry;
            }
            if (short_product(a,n,b,m,out,sizeof(out)) ||
                memcmp(out,want,sizeof(out)) != 0)
                return 1;
            ++checks;
        }
    }
    if (short_product(a,2,b,4,out,5) != 1 || short_product(NULL,4,b,4,out,8) != 1 ||
        short_product(a,(size_t)1 << 29,b,1,out,sizeof(out)) != 1)
        return 1;
    printf("PASS_SANITIZED_PACKED %zu products and 3 extent guards\n", checks);
    return 0;
}
