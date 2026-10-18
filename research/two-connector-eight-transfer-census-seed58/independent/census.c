/* Two-connector free-source-port census (PR1498 model), T paid transfers C: z0 += z1.
   Five sources, each B_j twice (ten B calls), one port per source (forced by restoration,
   PR1498 step 1), every placement of T C calls.
   Dirt markers: z0 starts e0, z1 starts e1. Readout pair valid iff equal dirt coefficient.
   Coverage = set of source-part differences over dirt-equal pairs of connector states (all cuts).
   Usage: census T slice nslices  -> prints histogram lines and witnesses. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

static int words[1000][10]; static int nwords = 0;
static void gen(int *pre, int len, int *cnt, int nl) {
  if (len == 10) { memcpy(words[nwords++], pre, sizeof(int)*10); return; }
  for (int j = 0; j < 5 && j <= nl; j++) {
    if (j == nl) { cnt[j] = 1; pre[len] = j; gen(pre, len+1, cnt, nl+1); cnt[j] = 0; }
    else if (cnt[j] == 1) { cnt[j] = 2; pre[len] = j; gen(pre, len+1, cnt, nl); cnt[j] = 1; }
  }
}
static inline uint32_t xt(uint32_t s, int a) { /* {v^a : v in s} as 32-bit set */
  if (a & 1)  s = ((s & 0x55555555u) << 1) | ((s >> 1) & 0x55555555u);
  if (a & 2)  s = ((s & 0x33333333u) << 2) | ((s >> 2) & 0x33333333u);
  if (a & 4)  s = ((s & 0x0F0F0F0Fu) << 4) | ((s >> 4) & 0x0F0F0F0Fu);
  if (a & 8)  s = ((s & 0x00FF00FFu) << 8) | ((s >> 8) & 0x00FF00FFu);
  if (a & 16) s = (s << 16) | (s >> 16);
  return s;
}
static inline uint32_t diffset(uint32_t s) {
  uint32_t d = 0, t = s;
  while (t) { int a = __builtin_ctz(t); t &= t - 1; d |= xt(s, a); }
  return d;
}
int main(int argc, char **argv) {
  int T = atoi(argv[1]); int slice = atoi(argv[2]); int ns = atoi(argv[3]);
  int maxw = argc > 4 ? atoi(argv[4]) : 5;
  int pre[10], cnt[5] = {0};
  gen(pre, 0, cnt, 0);
  int L = 10 + T;
  long long hist[6][33]; memset(hist, 0, sizeof hist);
  long long cand = 0, rest = 0, full = 0; int printed = 0;
  /* enumerate C position subsets as bitmasks of L bits with popcount T */
  for (int w = slice; w < nwords; w += ns) {
    for (int ports = 0; ports < 32; ports++) {
      int r = __builtin_popcount(ports);
      for (uint32_t pos = (1u << T) - 1; pos < (1u << L); ) {
        cand++;
        int q0 = 0, q1 = 0, drift = 0, par = 0, b = 0;
        uint32_t V1 = 1u, V0e = 1u, V0o = 0u; /* initial: q1=0; z0 source 0 at parity 0 */
        for (int i = 0; i < L; i++) {
          if (pos & (1u << i)) { drift ^= q1; par ^= 1; }
          else { int j = words[w][b++]; if (ports & (1 << j)) q1 ^= 1 << j; else q0 ^= 1 << j; }
          V1 |= 1u << q1;
          if (par) V0o |= 1u << (q0 ^ drift); else V0e |= 1u << (q0 ^ drift);
        }
        if (drift == 0 && q0 == 0 && q1 == 0 && par == 0) {
          rest++;
          uint32_t cov = diffset(V1) | diffset(V0e) | diffset(V0o);
          int c = __builtin_popcount(cov);
          hist[r][c]++;
          if (cov == 0xFFFFFFFFu) {
            full++;
            if (printed < maxw) {
              printed++;
              printf("WITNESS word=");
              for (int k = 0; k < 10; k++) printf("%d", words[w][k]);
              printf(" ports=%d Cpos=", ports);
              for (int i = 0; i < L; i++) if (pos & (1u << i)) printf("%d,", i);
              printf("\n");
            }
          }
        }
        /* next combination with same popcount (Gosper) */
        if (pos == 0) break;
        uint32_t c0 = pos & -pos, rr = pos + c0; pos = (((rr ^ pos) >> 2) / c0) | rr;
      }
    }
  }
  printf("SUMMARY T=%d slice=%d/%d words=%d cand=%lld restored=%lld full=%lld\n", T, slice, ns, nwords, cand, rest, full);
  for (int r = 0; r <= 5; r++) { printf("HIST r=%d", r); for (int c = 0; c <= 32; c++) if (hist[r][c]) printf(" %d:%lld", c, hist[r][c]); printf("\n"); }
  return 0;
}
