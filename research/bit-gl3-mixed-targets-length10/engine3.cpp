// Bounded third-register probe: diag([a],[b],[c]) in M_3(F2[GL_3(F2)]) with one
// extra dirty scalar register (restored: c = e, or ending at any monomial [c]),
// 28 binary rank-one idempotents x 6 coordinate-CNOT labels = 168 paid
// involutions, free GL_3(F2) scalar mixing normalized by augmentation.
// Radius-3 ball by exact BFS; every word of length <= 7 is A B^-1 with A at
// distance <= 4 and B at distance <= 3, so the ball-3 x ball-3 key join plus
// the streamed distance-4 images (generator images of distance-3 states not in
// the ball) joined against ball-3 keys cover all lengths <= 7. Row-orbit keys
// as in engine.cpp, compared exactly. Session 32 (Claude Code for
// JosieElliston). Apache-2.0.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <thread>
#include <tuple>
#include <unordered_map>
#include <vector>

using U = std::uint64_t;
static void need(bool ok, const char* why) {
    if (!ok) { std::fprintf(stderr, "FAIL: %s\n", why); std::exit(2); }
}

// ---- address group GL_3(F2): bit (3*row+col), row-combination product ----
static int mul3(int a, int b) {
    int out = 0;
    for (int r = 0; r < 3; ++r) {
        int v = 0;
        for (int c = 0; c < 3; ++c)
            if (a >> (3 * r + c) & 1) v ^= (b >> (3 * c)) & 7;
        out |= v << (3 * r);
    }
    return out;
}
static const int ID3 = 1 | (1 << 4) | (1 << 8);
static int G = 0;
static std::vector<int> elem;              // index -> 9-bit matrix (sorted)
static int idx_of[512];
static int prod[168][168], inv_[168], dist_[168], identity_index;
static int label_matrix[6], label_index[6];
static const int LI[6] = {0, 0, 1, 1, 2, 2}, LJ[6] = {1, 2, 0, 2, 0, 1};

static void build_group() {
    for (int k = 0; k < 6; ++k) label_matrix[k] = ID3 ^ (1 << (3 * LI[k] + LJ[k]));
    std::vector<int> seen(512, -1), queue{ID3};
    seen[ID3] = 0;
    for (size_t h = 0; h < queue.size(); ++h)
        for (int k = 0; k < 6; ++k) {
            int t = mul3(label_matrix[k], queue[h]);
            if (seen[t] < 0) { seen[t] = seen[queue[h]] + 1; queue.push_back(t); }
        }
    need(queue.size() == 168, "GL3(F2) order");
    elem = queue;
    std::sort(elem.begin(), elem.end());
    G = 168;
    std::fill(idx_of, idx_of + 512, -1);
    for (int i = 0; i < G; ++i) idx_of[elem[i]] = i;
    for (int i = 0; i < G; ++i) {
        dist_[i] = seen[elem[i]];
        for (int j = 0; j < G; ++j) prod[i][j] = idx_of[mul3(elem[i], elem[j])];
    }
    identity_index = idx_of[ID3];
    for (int i = 0; i < G; ++i)
        for (int j = 0; j < G; ++j)
            if (prod[i][j] == identity_index) inv_[i] = j;
    for (int k = 0; k < 6; ++k) label_index[k] = idx_of[label_matrix[k]];
}

// ---- group algebra F2[G] as 168-bit sets ----
struct Poly {
    U w[3];
};
static inline bool zero(const Poly& p) { return !(p.w[0] | p.w[1] | p.w[2]); }
static inline Poly px(const Poly& a, const Poly& b) {
    return Poly{{a.w[0] ^ b.w[0], a.w[1] ^ b.w[1], a.w[2] ^ b.w[2]}};
}
static inline Poly translate(const Poly& p, int g) {  // [g] * p
    Poly out{{0, 0, 0}};
    for (int k = 0; k < 3; ++k) {
        U v = p.w[k];
        while (v) {
            int b = __builtin_ctzll(v) + 64 * k;
            v &= v - 1;
            int t = prod[g][b];
            out.w[t >> 6] ^= U(1) << (t & 63);
        }
    }
    return out;
}
static inline int cmp(const Poly& a, const Poly& b) {
    for (int k = 2; k >= 0; --k)
        if (a.w[k] != b.w[k]) return a.w[k] < b.w[k] ? -1 : 1;
    return 0;
}
// ---- three registers: 3x3 matrices over F2[G], 28 idempotents x 6 labels ----
struct Mat { Poly e[9]; };
static inline bool eq(const Mat& a, const Mat& b) { return std::memcmp(&a, &b, sizeof(Mat)) == 0; }
struct MatHash {
    size_t operator()(const Mat& m) const {
        U h = 0x243f6a8885a308d3ULL;
        for (int i = 0; i < 9; ++i)
            for (int k = 0; k < 3; ++k) {
                U v = m.e[i].w[k] + 0x9e3779b97f4a7c15ULL * (3 * i + k + 1);
                v ^= v >> 31; v *= 0x7fb5d329728ea185ULL; v ^= v >> 27;
                v *= 0x81dadef4bc2dd44dULL; v ^= v >> 33;
                h = (h ^ v) * 0x100000001b3ULL;
            }
        return h;
    }
};
struct MatEq { bool operator()(const Mat& a, const Mat& b) const { return eq(a, b); } };
struct Gen { int u, v, label; };
static std::vector<Gen> gens;
static inline Mat step(const Mat& m, const Gen& gn) {
    Poly x[3] = {{{0,0,0}},{{0,0,0}},{{0,0,0}}};
    for (int r = 0; r < 3; ++r) if (gn.v >> r & 1) for (int c = 0; c < 3; ++c) x[c] = px(x[c], m.e[3*r+c]);
    int g = label_index[gn.label];
    for (int c = 0; c < 3; ++c) x[c] = px(x[c], translate(x[c], g));
    Mat out = m;
    for (int r = 0; r < 3; ++r) if (gn.u >> r & 1) for (int c = 0; c < 3; ++c) out.e[3*r+c] = px(out.e[3*r+c], x[c]);
    return out;
}
static inline int cmp3(const Poly* a, const Poly* b) {
    for (int i = 0; i < 3; ++i) { int c = cmp(a[i], b[i]); if (c) return c; }
    return 0;
}
static inline void canon_row(const Poly* row, Poly* out, int& anchor) {
    const Poly* s = nullptr;
    for (int i = 0; i < 3; ++i) if (!zero(row[i])) { s = &row[i]; break; }
    need(s != nullptr, "zero row");
    bool have = false;
    for (int k = 0; k < 3; ++k) {
        U v = s->w[k];
        while (v) {
            int x = __builtin_ctzll(v) + 64 * k;
            v &= v - 1;
            Poly t[3];
            for (int i = 0; i < 3; ++i) t[i] = translate(row[i], inv_[x]);
            int c = have ? cmp3(t, out) : -1;
            if (!have || c < 0) { for (int i = 0; i < 3; ++i) out[i] = t[i]; anchor = x; have = true; }
            else if (c == 0) need(false, "row stabilizer tie");
        }
    }
}
struct Key { Poly k[9]; };
struct KeyHash { size_t operator()(const Key& m) const { return MatHash()(*reinterpret_cast<const Mat*>(&m)); } };
struct KeyEq { bool operator()(const Key& a, const Key& b) const { return std::memcmp(&a, &b, sizeof(Key)) == 0; } };
static inline void make_key(const Mat& m, Key& key, int* anc) {
    for (int r = 0; r < 3; ++r) canon_row(&m.e[3*r], &key.k[3*r], anc[r]);
}

int main(int argc, char** argv) {
    int threads = argc > 1 ? std::atoi(argv[1]) : 8;
    build_group();
    for (int u = 1; u < 8; ++u) for (int v = 1; v < 8; ++v)
        if (__builtin_popcount(u & v) & 1) for (int k = 0; k < 6; ++k) gens.push_back({u, v, k});
    need(gens.size() == 168, "168 generators");
    Mat I{};
    for (int r = 0; r < 3; ++r) I.e[4*r].w[identity_index >> 6] |= U(1) << (identity_index & 63);
    std::vector<Mat> ball{I};
    std::vector<std::uint8_t> bd{0};
    std::unordered_map<Mat, std::uint32_t, MatHash, MatEq> where;
    where.reserve(1 << 23);
    where.emplace(I, 0);
    std::vector<size_t> ls{0, 1};
    for (int depth = 1; depth <= 3; ++depth) {
        for (size_t s = ls[depth-1]; s < ls[depth]; ++s)
            for (const Gen& g : gens) {
                Mat t = step(ball[s], g);
                if (where.find(t) == where.end()) { where.emplace(t, ball.size()); ball.push_back(t); bd.push_back(depth); }
            }
        ls.push_back(ball.size());
    }
    std::printf("ball3_layers");
    for (int k = 0; k < 4; ++k) std::printf(" %zu", ls[k+1] - ls[k]);
    std::printf("\n");
    // key buckets of ball-3
    std::unordered_map<Key, std::vector<std::array<std::uint32_t,2>>, KeyHash, KeyEq> buckets; // (state, anchors packed)
    buckets.reserve(ball.size());
    for (size_t i = 0; i < ball.size(); ++i) {
        Key k; int a[3]; make_key(ball[i], k, a);
        buckets[k].push_back({std::uint32_t(i), std::uint32_t(a[0] | a[1] << 8 | a[2] << 16)});
    }
    std::printf("ball3_states %zu\nball3_buckets %zu\n", ball.size(), buckets.size());
    // best[a][b][restored?]: cost of diag(a,b,c); index c==e separately
    static int bestR[168][168], bestAny[168][168];
    for (int a = 0; a < 168; ++a) for (int b = 0; b < 168; ++b) bestR[a][b] = bestAny[a][b] = 99;
    auto relax = [&](int (*R)[168], int (*A)[168], int da, unsigned pa, int db, unsigned pb) {
        int ta = prod[pa & 255][inv_[pb & 255]], tb = prod[(pa >> 8) & 255][inv_[(pb >> 8) & 255]];
        int tc = prod[(pa >> 16) & 255][inv_[(pb >> 16) & 255]];
        int c = da + db;
        if (c < A[ta][tb]) A[ta][tb] = c;
        if (tc == identity_index && c < R[ta][tb]) R[ta][tb] = c;
    };
    for (auto& kv : buckets)
        for (auto& x : kv.second) for (auto& y : kv.second)
            relax(bestR, bestAny, bd[x[0]], x[1], bd[y[0]], y[1]);
    // stream layer-4 images against ball-3 keys (lengths <= 7)
    std::vector<std::vector<std::array<int,168>>> tR(threads, std::vector<std::array<int,168>>(168)), tA = tR;
    for (auto& v : tR) for (auto& r : v) r.fill(99);
    for (auto& v : tA) for (auto& r : v) r.fill(99);
    std::vector<size_t> imgs(threads, 0);
    auto work = [&](int t) {
        int (*R)[168] = reinterpret_cast<int(*)[168]>(tR[t].data());
        int (*A)[168] = reinterpret_cast<int(*)[168]>(tA[t].data());
        for (size_t s = ls[3] + t; s < ls[4]; s += threads)
            for (const Gen& g : gens) {
                Mat m = step(ball[s], g);
                ++imgs[t];
                if (where.find(m) != where.end()) continue;
                Key k; int a[3]; make_key(m, k, a);
                auto it = buckets.find(k);
                if (it == buckets.end()) continue;
                unsigned pa = a[0] | a[1] << 8 | a[2] << 16;
                for (auto& y : it->second) relax(R, A, 4, pa, bd[y[0]], y[1]);
            }
    };
    { std::vector<std::thread> pool; for (int t = 0; t < threads; ++t) pool.emplace_back(work, t); for (auto& th : pool) th.join(); }
    size_t ni = 0; for (auto x : imgs) ni += x;
    for (int t = 0; t < threads; ++t) for (int a = 0; a < 168; ++a) for (int b = 0; b < 168; ++b) {
        bestR[a][b] = std::min(bestR[a][b], tR[t][a][b]); bestAny[a][b] = std::min(bestAny[a][b], tA[t][a][b]); }
    std::printf("layer4_images %zu\n", ni);
    // compare with direct cost
    int histR[16][100] = {}, histA[16][100] = {};
    size_t saveR = 0, saveA = 0, mism = 0;
    for (int a = 0; a < 168; ++a) for (int b = 0; b < 168; ++b) {
        int d = dist_[a] + dist_[b];
        histR[d][bestR[a][b]]++; histA[d][bestAny[a][b]]++;
        if (bestR[a][b] < d) ++saveR;
        if (bestAny[a][b] < d) ++saveA;
        if (d <= 7 && bestR[a][b] != d) ++mism;   // direct words of length <= 7 must be found
    }
    std::printf("saving_restored %zu\nsaving_any_third %zu\ndirect_le7_not_found %zu\n", saveR, saveA, mism);
    for (int d = 0; d <= 12; ++d) for (int m = 0; m < 100; ++m) {
        if (histR[d][m]) std::printf("hist_restored direct %d min_le7 %d count %d\n", d, m, histR[d][m]);
        if (histA[d][m]) std::printf("hist_any_third direct %d min_le7 %d count %d\n", d, m, histA[d][m]);
    }
    std::printf("DONE\n");
}
