/* Maximum number of points of a fixed 7-dimensional integer set that lie in
   any 6-dimensional linear span of six of the points.

   Membership uses the integer cross product: the seven signed maximal minors
   of six independent points are a normal vector, and a point lies in their
   span exactly when the dot product is zero.  Determinants are fraction-free
   Bareiss determinants.  Every division must be exact, and the normal must be
   orthogonal to each of the six points; either failure aborts.

   Build: cc -O3 -std=c11 -o span_bound span_bound.c
   Usage: span_bound --self-test
          span_bound POINTS
   POINTS is a text file: an integer n, then n lines of seven integers.
   The last stdout line is
     SPAN_BOUND n=.. seen=.. indep=.. best=.. first=.. ortho_failures=0 division_failures=0
*/
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef __int128 i128;

static int div_fail = 0;

static i128 bareiss6(i128 a[6][6]) {
    int sign = 1;
    for (int k = 0; k < 5; k++) {
        if (a[k][k] == 0) {
            int piv = -1;
            for (int i = k + 1; i < 6; i++) {
                if (a[i][k]) {
                    piv = i;
                    break;
                }
            }
            if (piv < 0) return 0;
            for (int j = k; j < 6; j++) {
                i128 t = a[k][j];
                a[k][j] = a[piv][j];
                a[piv][j] = t;
            }
            sign = -sign;
        }
        i128 pk = a[k][k];
        i128 prev = k ? a[k - 1][k - 1] : 1;
        if (prev == 0) {
            div_fail++;
            return 0;
        }
        for (int i = k + 1; i < 6; i++) {
            i128 aik = a[i][k];
            for (int j = k + 1; j < 6; j++) {
                i128 num = pk * a[i][j] - aik * a[k][j];
                if (num % prev) {
                    div_fail++;
                    return 0;
                }
                a[i][j] = num / prev;
            }
        }
    }
    return sign * a[5][5];
}

static i128 igcd(i128 a, i128 b) {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    while (b) {
        i128 t = a % b;
        a = b;
        b = t;
    }
    return a;
}

static int run_points(const int64_t *p, int n, long long *seen_out, long long *indep_out,
                      int *best_out, int *first_out, int *ortho_out) {
    int best = 0;
    int first = -1;
    int ortho = 0;
    long long seen = 0;
    long long indep = 0;
    int sel[6];
    for (int i = 0; i < 6; i++) sel[i] = i;
    while (1) {
        seen++;
        i128 normal[7];
        int nonzero = 0;
        for (int del = 0; del < 7; del++) {
            i128 a[6][6];
            for (int r = 0; r < 6; r++) {
                int c = 0;
                const int64_t *row = p + (size_t)sel[r] * 7;
                for (int j = 0; j < 7; j++) {
                    if (j != del) a[r][c++] = row[j];
                }
            }
            normal[del] = bareiss6(a);
            if (div_fail) return 1;
            if (normal[del]) nonzero = 1;
        }
        if (nonzero) {
            for (int del = 0; del < 7; del++) {
                if (del & 1) normal[del] = -normal[del];
            }
            i128 g = 0;
            for (int j = 0; j < 7; j++) g = igcd(g, normal[j]);
            if (g == 0) return 1;
            for (int j = 0; j < 7; j++) normal[j] /= g;
            for (int r = 0; r < 6; r++) {
                const int64_t *row = p + (size_t)sel[r] * 7;
                i128 s = 0;
                for (int j = 0; j < 7; j++) s += normal[j] * (i128)row[j];
                if (s) {
                    ortho++;
                    break;
                }
            }
            int cnt = 0;
            for (int i = 0; i < n; i++) {
                const int64_t *row = p + (size_t)i * 7;
                i128 s = 0;
                for (int j = 0; j < 7; j++) s += normal[j] * (i128)row[j];
                if (s == 0) cnt++;
            }
            if (first < 0) first = cnt;
            if (cnt > best) best = cnt;
            indep++;
        }
        int k = 5;
        while (k >= 0 && sel[k] == n - 6 + k) k--;
        if (k < 0) break;
        sel[k]++;
        for (int j = k + 1; j < 6; j++) sel[j] = sel[j - 1] + 1;
    }
    *seen_out = seen;
    *indep_out = indep;
    *best_out = best;
    *first_out = first;
    *ortho_out = ortho;
    return 0;
}

static int self_test(void) {
    /* Nine points in Q^7.  The six standard basis vectors e0..e5 together
       with e6, 2 e0 and 2 e6.  The first independent 6-tuple is e0..e5 and
       contains 7 of the points (those six and 2 e0).  The maximum is 8:
       e0,e1,e2,e3,e4,e6,2 e0,2 e6 span a 6-dimensional coordinate subspace. */
    const int64_t pts[9 * 7] = {
        1, 0, 0, 0, 0, 0, 0,
        0, 1, 0, 0, 0, 0, 0,
        0, 0, 1, 0, 0, 0, 0,
        0, 0, 0, 1, 0, 0, 0,
        0, 0, 0, 0, 1, 0, 0,
        0, 0, 0, 0, 0, 1, 0,
        0, 0, 0, 0, 0, 0, 1,
        2, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 2,
    };
    long long seen = 0, indep = 0;
    int best = 0, first = -1, ortho = 0;
    if (run_points(pts, 9, &seen, &indep, &best, &first, &ortho)) return 1;
    if (seen != 84 || indep <= 0 || best != 8 || first != 7 || ortho || div_fail) {
        fprintf(stderr, "self-test mismatch seen=%lld indep=%lld best=%d first=%d ortho=%d div=%d\n",
                seen, indep, best, first, ortho, div_fail);
        return 1;
    }
    printf("SPAN_BOUND n=9 seen=%lld indep=%lld best=%d first=%d ortho_failures=%d division_failures=%d\n",
           seen, indep, best, first, ortho, div_fail);
    return 0;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--self-test") == 0) return self_test();
    if (argc != 2) {
        fprintf(stderr, "usage: span_bound --self-test | span_bound POINTS\n");
        return 2;
    }
    FILE *fp = fopen(argv[1], "r");
    if (!fp) {
        perror(argv[1]);
        return 1;
    }
    int n = 0;
    if (fscanf(fp, "%d", &n) != 1 || n < 6 || n > 64) {
        fprintf(stderr, "bad point count\n");
        return 1;
    }
    int64_t *p = calloc((size_t)n * 7, sizeof(int64_t));
    if (!p) return 1;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < 7; j++) {
            long long v = 0;
            if (fscanf(fp, "%lld", &v) != 1) {
                fprintf(stderr, "short point file\n");
                return 1;
            }
            p[(size_t)i * 7 + j] = v;
        }
    }
    fclose(fp);
    long long seen = 0, indep = 0;
    int best = 0, first = -1, ortho = 0;
    if (run_points(p, n, &seen, &indep, &best, &first, &ortho) || div_fail || ortho) {
        fprintf(stderr, "exact span failure div=%d ortho=%d\n", div_fail, ortho);
        return 1;
    }
    printf("SPAN_BOUND n=%d seen=%lld indep=%lld best=%d first=%d ortho_failures=%d division_failures=%d\n",
           n, seen, indep, best, first, ortho, div_fail);
    free(p);
    return 0;
}
