/* Method B census, implemented independently of census_prefix.c.
   Literal two-row simulation over the basis {e0,e1,b0..b4}: z0 starts e0,
   z1 starts e1; B_j(p): z_p ^= b_j; C: z0 ^= z1.  For split size r the
   sources 0..r-1 write z1 and r..4 write z0; the z1 word and the z0 word
   are separately canonical by first occurrence and three event streams are
   interleaved recursively, so each S5 orbit occurs once.  Every (row, time)
   value is a readout candidate; a readout pair cancels dirt iff its two
   values agree on e0,e1 (cross-row pairs are not excluded a priori).
   Output: one JSON object.  Apache-2.0.  Prepared with Claude Code. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define E0 1
#define E1 2
static int W0[1000][10], W1[1000][10], tmpw[10], tmpc[10], ntmp, nlen, nbase;
static void rec(int pos, int used, int (*out)[10]) {
  if (pos == nlen) { memcpy(out[ntmp++], tmpw, sizeof tmpw); return; }
  for (int l = 0; l <= used && l < nlen / 2; l++) {
    if (tmpc[l] == 2) continue;
    tmpw[pos] = nbase + l; tmpc[l]++;
    rec(pos + 1, l == used ? used + 1 : used, out);
    tmpc[l]--;
  }
}
static int canonical_words(int len, int base, int (*out)[10]) {
  ntmp = 0; nlen = len; nbase = base; memset(tmpc, 0, sizeof tmpc);
  rec(0, 0, out);
  return ntmp;
}
static int T, R, len0, len1, seq[40];
static long long hist[6][33], restored, unrestored, full[6];
static void evaluate(const int *w0, const int *w1) {
  int z0 = E0, z1 = E1, i0 = 0, i1 = 0, nv = 0, vals[96], L = len0 + len1 + T;
  vals[nv++] = z0; vals[nv++] = z1;
  for (int t = 0; t < L; t++) {
    if (seq[t] == 2) z0 ^= z1;
    else if (seq[t] == 1) z1 ^= 4 << w1[i1++];
    else z0 ^= 4 << w0[i0++];
    vals[nv++] = z0; vals[nv++] = z1;
  }
  if (z0 != E0 || z1 != E1) { unrestored++; return; }
  restored++;
  char got[32] = {0};
  for (int a = 0; a < nv; a++)
    for (int b = a; b < nv; b++) {
      int x = vals[a] ^ vals[b];
      if (!(x & (E0 | E1))) got[x >> 2] = 1;
    }
  int c = 0;
  for (int m = 0; m < 32; m++) c += got[m];
  hist[R][c]++;
  if (c == 32) full[R]++;
}
static void interleave(int t, int a, int b, int c, const int *w0, const int *w1) {
  if (a == len0 && b == len1 && c == T) { evaluate(w0, w1); return; }
  if (a < len0) { seq[t] = 0; interleave(t + 1, a + 1, b, c, w0, w1); }
  if (b < len1) { seq[t] = 1; interleave(t + 1, a, b + 1, c, w0, w1); }
  if (c < T) { seq[t] = 2; interleave(t + 1, a, b, c + 1, w0, w1); }
}
int main(int argc, char **argv) {
  if (argc < 2) { fprintf(stderr, "usage: census_literal T [r]\n"); return 2; }
  T = atoi(argv[1]);
  int only = argc > 2 ? atoi(argv[2]) : -1;
  if (T < 0 || T > 20) return 2;
  for (R = 0; R <= 5; R++) {
    if (only >= 0 && R != only) continue;
    len1 = 2 * R; len0 = 10 - 2 * R;
    int n1 = canonical_words(len1, 0, W1), n0 = canonical_words(len0, R, W0);
    for (int i = 0; i < n0; i++)
      for (int j = 0; j < n1; j++) interleave(0, 0, 0, 0, W0[i], W1[j]);
  }
  printf("{\"method\":\"literal\",\"transfers\":%d,\"only_split\":%d,\"orbits\":%lld,\"restored\":%lld,\"histograms\":{", T, only, restored + unrestored, restored);
  int first = 1;
  for (int r = 0; r <= 5; r++) {
    if (only >= 0 && r != only) continue;
    printf("%s\"%d\":{", first ? "" : ",", r); first = 0; int f2 = 1;
    for (int c = 0; c <= 32; c++) if (hist[r][c]) { printf("%s\"%d\":%lld", f2 ? "" : ",", c, hist[r][c]); f2 = 0; }
    printf("}");
  }
  printf("},\"universal\":{"); first = 1;
  for (int r = 0; r <= 5; r++) { if (only >= 0 && r != only) continue; printf("%s\"%d\":%lld", first ? "" : ",", r, full[r]); first = 0; }
  printf("}}\n");
  return 0;
}
