/* Method A census for the two-connector transfer alphabet (five sources).
   Enumerates each S5 orbit of labelled incidence-minimal schedules once:
   a source word canonical by first occurrence (945 pairings), a port set J1
   (sources whose two B calls write z1; restoration forces equal ports), and
   a placement of T transfer calls C: z0 += z1 among 10+T event slots.
   Uses the derived prefix formula z0 source part = q0 + S, z1 = q1, with
   readout classes (z0, even phase), (z0, odd phase) and z1.
   Output: one JSON object.  Apache-2.0.  Prepared with Claude Code. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#define NS 5
#define NB (2 * NS)
static int words[945][NB];
static int nw = 0;
static void gen(int *w, int pos, int used, int *cnt) {
  if (pos == NB) { for (int i = 0; i < NB; i++) words[nw][i] = w[i]; nw++; return; }
  for (int l = 0; l <= used && l < NS; l++) {
    if (cnt[l] == 2) continue;
    w[pos] = l; cnt[l]++;
    gen(w, pos + 1, l == used ? used + 1 : used, cnt);
    cnt[l]--;
  }
}
static inline uint32_t translate(uint32_t s, int v) {
  static const uint32_t m[5] = {0x55555555u, 0x33333333u, 0x0f0f0f0fu, 0x00ff00ffu, 0x0000ffffu};
  for (int k = 0; k < 5; k++)
    if (v >> k & 1) { int d = 1 << k; s = ((s & m[k]) << d) | ((s >> d) & m[k]); }
  return s;
}
static inline uint32_t differences(uint32_t s) {
  uint32_t r = 0, t = s;
  while (t) { int v = __builtin_ctz(t); t &= t - 1; r |= translate(s, v); }
  return r;
}
int main(int argc, char **argv) {
  if (argc != 2) { fprintf(stderr, "usage: census_prefix T\n"); return 2; }
  int T = atoi(argv[1]), L = NB + T;
  if (T < 0 || L > 30) return 2;
  int w[NB], cnt[NS] = {0};
  gen(w, 0, 0, cnt);
  if (nw != 945) return 3;
  long long hist[6][33] = {{0}}, restored = 0, unrestored = 0, full[6] = {0};
  int have[6] = {0}; int wit_word[6][NB]; uint32_t wit_j1[6], wit_c[6];
  for (int wi = 0; wi < nw; wi++)
    for (uint32_t J1 = 0; J1 < 32; J1++)
      for (uint32_t pm = 0; pm < (1u << L); pm++) {
        if (__builtin_popcount(pm) != T) continue;
        int q0 = 0, q1 = 0, p = 0, S = 0, bi = 0;
        uint32_t E = 1u, O = 0, Z = 1u;
        for (int t = 0; t < L; t++) {
          if (pm >> t & 1) { S ^= q1; p ^= 1; }
          else { int l = words[wi][bi++]; if (J1 >> l & 1) q1 ^= 1 << l; else q0 ^= 1 << l; }
          int v = q0 ^ S;
          if (p) O |= 1u << v; else E |= 1u << v;
          Z |= 1u << q1;
        }
        if (S || q0 || q1 || p) { unrestored++; continue; }
        restored++;
        int r = __builtin_popcount(J1);
        int c = __builtin_popcount(differences(E) | differences(O) | differences(Z));
        hist[r][c]++;
        if (c == 32) {
          full[r]++;
          if (!have[r]) { have[r] = 1; for (int i = 0; i < NB; i++) wit_word[r][i] = words[wi][i]; wit_j1[r] = J1; wit_c[r] = pm; }
        }
      }
  printf("{\"method\":\"prefix\",\"transfers\":%d,\"orbits\":%lld,\"restored\":%lld,\"histograms\":{", T, restored + unrestored, restored);
  for (int r = 0; r <= 5; r++) {
    printf("%s\"%d\":{", r ? "," : "", r); int first = 1;
    for (int c = 0; c <= 32; c++) if (hist[r][c]) { printf("%s\"%d\":%lld", first ? "" : ",", c, hist[r][c]); first = 0; }
    printf("}");
  }
  printf("},\"universal\":{");
  for (int r = 0; r <= 5; r++) printf("%s\"%d\":%lld", r ? "," : "", r, full[r]);
  printf("},\"first_witness\":{");
  int first = 1;
  for (int r = 0; r <= 5; r++) if (have[r]) {
    printf("%s\"%d\":{\"word\":[", first ? "" : ",", r); first = 0;
    for (int i = 0; i < NB; i++) printf("%s%d", i ? "," : "", wit_word[r][i]);
    printf("],\"z1_sources_mask\":%u,\"transfer_slots_mask\":%u}", wit_j1[r], wit_c[r]);
  }
  printf("}}\n");
  return 0;
}
