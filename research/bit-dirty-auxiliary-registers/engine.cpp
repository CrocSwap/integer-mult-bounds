// Exhaustive exact check: abelian bit words with dirty auxiliary registers.
//
// Usage: engine N W S OUT [rank2-control]
//   N  scalar registers (2..4), the first W are data registers, the rest are
//      dirty auxiliaries whose endpoint may be any diagonal monomial;
//   S  number of paid calls (1..6);
//   OUT file receiving one line per diagonal terminal.
//
// Every ordered word of S binary rank-one idempotents is expanded as
//   P(t) = prod_j ((I+N_j) + t_j N_j) = sum_a M_a t^a,  a in {0,1}^S.
// The physical relation lattice of the rational frames is assumed to have
// rank at most one (the frame span is at least S-1); see README section 4.
// Option R=0 covers every relation lattice without subset collisions;
// otherwise subset monomials a,b collide exactly when a-b = +-r for a
// cube vector r in {-1,0,1}^S.  For each option the formal coefficients are
// grouped, a diagonal monomial endpoint is required, and every data target is
// tested for the rank-at-most-two obstruction c in Qr + span(e_i,e_j).
// A terminal that survives this test would be reported as a candidate.
// All arithmetic is over F2 bit masks and small integers.
//
// The optional fifth argument "rank2-control" adds the rank-two scalar
// idempotent E00+E11, which lies outside the model.  It is a failure control:
// one such call multiplies both data registers by one frame.

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

using Mat = uint32_t;  // row i occupies bits [i*n, i*n+n)

static int n, W, S;

static inline int bit(Mat m, int i, int j) { return (m >> (i * n + j)) & 1u; }

static Mat mul(Mat a, Mat b) {
  Mat c = 0;
  const Mat rowmask = (1u << n) - 1u;
  for (int i = 0; i < n; ++i) {
    Mat row = 0;
    for (int k = 0; k < n; ++k)
      if (bit(a, i, k)) row ^= (b >> (k * n)) & rowmask;
    c |= row << (i * n);
  }
  return c;
}

static Mat identity() {
  Mat m = 0;
  for (int i = 0; i < n; ++i) m |= 1u << (i * n + i);
  return m;
}

static Mat offdiag_mask() {
  Mat m = 0;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      if (i != j) m |= 1u << (i * n + j);
  return m;
}

// Rank over F2 of an n x n bit matrix.
static int rank2(Mat m) {
  int rows[4];
  const Mat rowmask = (1u << n) - 1u;
  for (int i = 0; i < n; ++i) rows[i] = (m >> (i * n)) & rowmask;
  int r = 0;
  for (int c = 0; c < n; ++c) {
    int p = -1;
    for (int i = r; i < n; ++i)
      if ((rows[i] >> c) & 1) { p = i; break; }
    if (p < 0) continue;
    std::swap(rows[r], rows[p]);
    for (int i = 0; i < n; ++i)
      if (i != r && ((rows[i] >> c) & 1)) rows[i] ^= rows[r];
    ++r;
  }
  return r;
}

struct Relation {
  std::vector<int> r;         // entries in {-1,0,1}; empty means R = 0
  uint64_t paired = 0;        // subsets a that have a partner a+r or a-r
  std::vector<int> partner;   // partner[a] or -1
};

static std::vector<Mat> projectors;
static std::vector<Relation> relations;
static Mat OFF, ID;
static FILE* out;
static unsigned long long words = 0, terminals = 0, candidates = 0;
static unsigned long long terminals_by_option_kind[3] = {0, 0, 0};  // none, support<S, support=S
static unsigned long long aux_touching_terminals = 0;
static int word[8];
static std::vector<Mat> layer[8];

// c + lambda r has support of size <= 2 for some rational lambda.
// Only lambda in {-1,0,1} can lower the support below that of lambda = 0.
static bool rank_at_most_two(int c, const std::vector<int>& r) {
  for (int lam = -1; lam <= 1; ++lam) {
    if (r.empty() && lam != 0) continue;
    int support = 0;
    for (int j = 0; j < S; ++j) {
      int v = ((c >> j) & 1) + (r.empty() ? 0 : lam * r[j]);
      if (v != 0) ++support;
    }
    if (support <= 2) return true;
  }
  return false;
}

static void check_word(const std::vector<Mat>& M) {
  ++words;
  const int A = 1 << S;
  uint64_t bad = 0;
  for (int a = 0; a < A; ++a)
    if (M[a] & OFF) bad |= 1ull << a;
  for (size_t ri = 0; ri < relations.size(); ++ri) {
    const Relation& rel = relations[ri];
    if ((bad & ~rel.paired) != 0) continue;
    // grouped coefficients; class representative is the smaller subset mask
    bool ok = true;
    for (int a = 0; a < A && ok; ++a) {
      int b = rel.partner.empty() ? -1 : rel.partner[a];
      if (b >= 0 && b < a) continue;
      Mat g = M[a] ^ (b >= 0 ? M[b] : 0u);
      if (g & OFF) ok = false;
    }
    if (!ok) continue;
    int rep[4];
    for (int i = 0; i < n && ok; ++i) {
      int count = 0;
      for (int a = 0; a < A; ++a) {
        int b = rel.partner.empty() ? -1 : rel.partner[a];
        if (b >= 0 && b < a) continue;
        int g = bit(M[a], i, i) ^ (b >= 0 ? bit(M[b], i, i) : 0);
        if (g) { ++count; rep[i] = a; }
      }
      if (count != 1) ok = false;  // the endpoint entry must be one monomial
    }
    if (!ok) continue;
    ++terminals;
    int kind = rel.r.empty() ? 0 : 1;
    if (kind) {
      int sup = 0;
      for (int v : rel.r) sup += v != 0;
      if (sup == S) kind = 2;
    }
    ++terminals_by_option_kind[kind];
    bool aux = false;
    for (int j = 0; j < S; ++j) {
      Mat N = projectors[word[j]];
      for (int i = 0; i < n; ++i)
        for (int k = 0; k < n; ++k)
          if ((i >= W || k >= W) && bit(N, i, k)) aux = true;
    }
    if (aux) ++aux_touching_terminals;
    bool survivor = true;
    for (int w = 0; w < W; ++w)
      if (rank_at_most_two(rep[w], rel.r)) survivor = false;
    if (survivor) ++candidates;
    std::fprintf(out, "%d", survivor ? 1 : 0);
    for (int j = 0; j < S; ++j) std::fprintf(out, " %d", word[j]);
    std::fprintf(out, " |");
    if (rel.r.empty()) std::fprintf(out, " 0");
    else for (int v : rel.r) std::fprintf(out, " %d", v);
    std::fprintf(out, " |");
    for (int i = 0; i < n; ++i) std::fprintf(out, " %d", rep[i]);
    std::fprintf(out, "\n");
  }
}

static void dfs(int depth) {
  if (depth == S) { check_word(layer[S]); return; }
  const std::vector<Mat>& prev = layer[depth];
  std::vector<Mat>& next = layer[depth + 1];
  for (size_t p = 0; p < projectors.size(); ++p) {
    word[depth] = (int)p;
    Mat N = projectors[p], IN = ID ^ N;
    const int A = 1 << depth;
    for (int a = 0; a < A; ++a) {
      next[a] = mul(prev[a], IN);
      next[a | (1 << depth)] = mul(prev[a], N);
    }
    dfs(depth + 1);
  }
}

int main(int argc, char** argv) {
  if (argc != 5 && argc != 6) {
    std::fprintf(stderr, "usage: engine N W S OUT [rank2-control]\n");
    return 2;
  }
  bool rank2_control = argc == 6;
  if (rank2_control && std::strcmp(argv[5], "rank2-control") != 0) return 2;
  n = std::atoi(argv[1]); W = std::atoi(argv[2]); S = std::atoi(argv[3]);
  if (n < 2 || n > 4 || W < 1 || W > n || S < 1 || S > 6) return 2;
  out = std::fopen(argv[4], "w");
  if (!out) return 2;
  ID = identity(); OFF = offdiag_mask();
  for (Mat m = 1; m < (1u << (n * n)); ++m)
    if (mul(m, m) == m && rank2(m) == 1) projectors.push_back(m);
  if (rank2_control) projectors.push_back((1u << 0) | (1u << (n + 1)));
  // relation options: R = 0, then cube vectors up to sign with support >= 2
  relations.push_back(Relation());
  int total = 1;
  for (int j = 0; j < S; ++j) total *= 3;
  for (int code = 0; code < total; ++code) {
    std::vector<int> r(S);
    int c = code, sup = 0, first = 0;
    for (int j = 0; j < S; ++j) { r[j] = c % 3 - 1; c /= 3; }
    for (int j = 0; j < S; ++j) if (r[j]) { ++sup; if (!first) first = r[j]; }
    if (sup < 2 || first < 0) continue;  // A_j = 0 excluded; sign normalized
    Relation rel; rel.r = r; rel.partner.assign(1 << S, -1);
    for (int a = 0; a < (1 << S); ++a) {
      int b = 0; bool valid = true;
      for (int j = 0; j < S; ++j) {
        int v = ((a >> j) & 1) + r[j];
        if (v < 0 || v > 1) { valid = false; break; }
        b |= v << j;
      }
      if (valid) { rel.partner[a] = b; rel.partner[b] = a; }
    }
    for (int a = 0; a < (1 << S); ++a)
      if (rel.partner[a] >= 0) rel.paired |= 1ull << a;
    relations.push_back(rel);
  }
  for (int d = 0; d <= S; ++d) layer[d].assign(1 << d, 0);
  layer[0][0] = ID;
  dfs(0);
  std::fclose(out);
  std::printf("{\"rank2_control\": %s, \"registers\": %d, \"data_registers\": %d, "
              "\"calls\": %d, \"projectors\": %zu, \"relation_options\": %zu, "
              "\"words\": %llu, \"diagonal_terminals\": %llu, "
              "\"terminals_no_collision\": %llu, \"terminals_partial_cube\": %llu, "
              "\"terminals_full_cube\": %llu, \"aux_touching_terminals\": %llu, "
              "\"candidates\": %llu}\n",
              rank2_control ? "true" : "false", n, W, S, projectors.size(),
              relations.size(), words, terminals, terminals_by_option_kind[0],
              terminals_by_option_kind[1], terminals_by_option_kind[2],
              aux_touching_terminals, candidates);
  return 0;
}
