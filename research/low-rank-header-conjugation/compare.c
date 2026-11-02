/* Appended to the authenticated retained engine and new kernel.
 * Produced by Nick Petalas. Apache-2.0.
 */
static void canonical_request(Mat r, int request) {
    if (request < 4) {
        unit_proj(r, request);
        minus_from_id(r);
    } else if (request == 4) {
        memset(r, 0, sizeof(Mat));
        r[0][0] = r[0][1] = 1;
        minus_from_id(r);
    } else if (request < 7) {
        unit_proj(r, request - 5);
    } else {
        memset(r, 0, sizeof(Mat));
        r[0][0] = r[1][1] = 1;
    }
}

int main(void) {
    const int cases[8][2] = {
        {2, 2}, {2, 3}, {2, 4}, {3, 2}, {3, 3}, {4, 2}, {4, 3}, {5, 2}
    };
    long long headers = 0, requests = 0, entries = 0;
    for (int test = 0; test < 8; test++) {
        q = cases[test][0];
        m = cases[test][1];
        field();
        long long total = 1;
        for (int i = 0; i < m * m; i++) total *= q;
        for (long long code = 0; code < total; code++) {
            Mat g, gi;
            long long digits = code;
            for (int i = 0; i < m; i++) for (int j = 0; j < m; j++) {
                g[i][j] = (int)(digits % q);
                digits /= q;
            }
            if (!inverse(g, gi)) continue;
            headers++;
            for (int request = 0; request < 8; request++) {
                if (request < 4 && request >= m) continue;
                Mat r, temp, dense, fast;
                canonical_request(r, request);
                mul(g, r, temp);
                mul(temp, gi, dense);
                conjugated_request(g, gi, request, fast);
                requests++;
                for (int i = 0; i < m; i++) for (int j = 0; j < m; j++) {
                    entries++;
                    if (dense[i][j] != fast[i][j]) return 1;
                }
            }
        }
    }
    printf("PASS_CONJUGATION_EQUIVALENCE headers=%lld requests=%lld entries=%lld\n",
           headers, requests, entries);
    return 0;
}
