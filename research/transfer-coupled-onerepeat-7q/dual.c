/* Dual even-parity cost Sigma_m min_a (e0[a] + e1[a xor m]).
 * Returns -1 if some mask is uncovered. Wentao Li + AI. Apache-2.0.
 */
#define INF 99

long dual_sum(const int *e0, const int *e1) {
    long total = 0;
    for (int m = 1; m < 32; m++) {
        int best = INF;
        for (int a = 0; a < 32; a++) {
            int c0 = e0[a];
            if (c0 >= INF) {
                continue;
            }
            int c1 = e1[a ^ m];
            if (c1 < INF) {
                int s = c0 + c1;
                if (s < best) {
                    best = s;
                }
            }
        }
        if (best >= INF) {
            return -1;
        }
        total += best;
    }
    return total;
}
