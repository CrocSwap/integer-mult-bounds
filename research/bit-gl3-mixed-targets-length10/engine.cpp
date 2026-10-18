// Exact radius-5 join for diag([a],[b]) in M_2(F2[GL_3(F2)]) with the six
// coordinate-CNOT labels and the six binary rank-one idempotents.
// Written independently of research/bit-gl3-mixed-targets-seed18 (session 32,
// Claude Code for JosieElliston). Apache-2.0.
//
// Every word of length <= 10 is A B^-1 with A, B in the radius-5 ball, since
// all 36 paid generators are involutions. A B^-1 = diag([a],[b]) exactly when
// each row of A is a left G-translate of the same row of B. Rows are put in a
// canonical left-translation orbit form; equal canonical keys give the target
// from the two anchor elements. All keys are compared exactly (no digests).
//
// Output (stdout): deterministic receipt lines, then one line per ordered pair
// (a,b) with d(a)+d(b) >= 10 giving the exact radius-5 join minimum (or 11 =
// "no word of length <= 10") and, when a word of length <= 10 exists, a witness.
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
struct Mat {
    Poly e[4];  // (0,0) (0,1) (1,0) (1,1)
};
static inline bool eq(const Mat& a, const Mat& b) { return std::memcmp(&a, &b, sizeof(Mat)) == 0; }
struct MatHash {
    size_t operator()(const Mat& m) const {
        U h = 0x243f6a8885a308d3ULL;
        for (int i = 0; i < 4; ++i)
            for (int k = 0; k < 3; ++k) {
                U v = m.e[i].w[k] + 0x9e3779b97f4a7c15ULL * (3 * i + k + 1);
                v ^= v >> 31; v *= 0x7fb5d329728ea185ULL; v ^= v >> 27;
                v *= 0x81dadef4bc2dd44dULL; v ^= v >> 33;
                h = (h ^ v) * 0x100000001b3ULL;
            }
        return h;
    }
};
struct MatEq {
    bool operator()(const Mat& a, const Mat& b) const { return eq(a, b); }
};

// Paid generator: left multiplication by I + ([g]+[e]) u v^T, u,v in F2^2,
// v^T u = 1.  u bit r selects destination row r; v bit r selects source row r.
struct Gen { int u, v, label; };
static std::vector<Gen> gens;
static void build_gens() {
    for (int u = 1; u < 4; ++u)
        for (int v = 1; v < 4; ++v)
            if (__builtin_popcount(u & v) & 1)
                for (int k = 0; k < 6; ++k) gens.push_back({u, v, k});
    need(gens.size() == 36, "36 generators");
}
static inline Mat step(const Mat& m, const Gen& gn) {
    Poly x{{0, 0, 0}}, y{{0, 0, 0}};
    if (gn.v & 1) { x = px(x, m.e[0]); y = px(y, m.e[1]); }
    if (gn.v & 2) { x = px(x, m.e[2]); y = px(y, m.e[3]); }
    int g = label_index[gn.label];
    x = px(x, translate(x, g));
    y = px(y, translate(y, g));
    Mat r = m;
    if (gn.u & 1) { r.e[0] = px(r.e[0], x); r.e[1] = px(r.e[1], y); }
    if (gn.u & 2) { r.e[2] = px(r.e[2], x); r.e[3] = px(r.e[3], y); }
    return r;
}

// Canonical representative of the left-translation orbit of a row (p,q):
// anchors are the support of p (or of q when p = 0); the representative is
// the lexicographically least ([x^-1]p, [x^-1]q). The minimizer is unique for a
// row of an invertible matrix (trivial stabilizer); a tie aborts.
static inline void canon_row(const Poly& p, const Poly& q, Poly& cp, Poly& cq, int& anchor) {
    const Poly& s = zero(p) ? q : p;
    need(!zero(s), "zero row");
    bool have = false;
    for (int k = 0; k < 3; ++k) {
        U v = s.w[k];
        while (v) {
            int x = __builtin_ctzll(v) + 64 * k;
            v &= v - 1;
            Poly tp = translate(p, inv_[x]), tq = translate(q, inv_[x]);
            int c = have ? cmp(tp, cp) : -1;
            if (c == 0) c = cmp(tq, cq);
            if (!have || c < 0) { cp = tp; cq = tq; anchor = x; have = true; }
            else if (c == 0) need(false, "row stabilizer tie");
        }
    }
}

struct Rec {
    Poly key[4];        // canonical top row, canonical bottom row
    std::uint32_t parent;  // index into ball (for d=5: a d=4 state)
    std::uint8_t d, xa, ya, gen;
};
static inline int keycmp(const Rec& a, const Rec& b) {
    for (int i = 0; i < 4; ++i) {
        int c = cmp(a.key[i], b.key[i]);
        if (c) return c;
    }
    return 0;
}
static inline void make_rec(const Mat& m, Rec& r) {
    int a, b;
    canon_row(m.e[0], m.e[1], r.key[0], r.key[1], a);
    canon_row(m.e[2], m.e[3], r.key[2], r.key[3], b);
    r.xa = std::uint8_t(a); r.ya = std::uint8_t(b);
}

int main(int argc, char** argv) {
    int threads = argc > 1 ? std::atoi(argv[1]) : 8;
    build_group();
    build_gens();
    // group sanity: associativity, inverses, label involutions
    for (int a = 0; a < G; a += 7)
        for (int b = 0; b < G; b += 5)
            for (int c = 0; c < G; ++c)
                need(prod[prod[a][b]][c] == prod[a][prod[b][c]], "associativity");
    for (int k = 0; k < 6; ++k)
        need(prod[label_index[k]][label_index[k]] == identity_index, "CNOT involution");
    std::array<int, 8> glayers{};
    for (int i = 0; i < G; ++i) glayers[dist_[i]]++;
    std::printf("address_layers");
    for (int k = 0; k < 7; ++k) std::printf(" %d", glayers[k]);
    std::printf("\n");

    // ---- radius-4 ball, exact dedupe ----
    Mat I{};
    I.e[0].w[identity_index >> 6] |= U(1) << (identity_index & 63);
    I.e[3] = I.e[0];
    std::vector<Mat> ball{I};
    std::vector<std::uint8_t> bd{0};
    std::vector<std::uint32_t> bparent{0};
    std::vector<std::uint8_t> bgen{255};
    std::unordered_map<Mat, std::uint32_t, MatHash, MatEq> where;
    where.reserve(1 << 21);
    where.emplace(I, 0);
    std::vector<size_t> layer_start{0, 1};
    for (int depth = 1; depth <= 4; ++depth) {
        size_t lo = layer_start[depth - 1], hi = layer_start[depth];
        for (size_t s = lo; s < hi; ++s)
            for (int g = 0; g < 36; ++g) {
                Mat t = step(ball[s], gens[g]);
                if (where.find(t) == where.end()) {
                    where.emplace(t, std::uint32_t(ball.size()));
                    ball.push_back(t); bd.push_back(std::uint8_t(depth));
                    bparent.push_back(std::uint32_t(s)); bgen.push_back(std::uint8_t(g));
                }
            }
        layer_start.push_back(ball.size());
    }
    std::printf("ball4_layers");
    for (int k = 0; k < 5; ++k) std::printf(" %zu", layer_start[k + 1] - layer_start[k]);
    std::printf("\nball4_states %zu\n", ball.size());

    // ---- records: ball-4 plus every generator image of a d=4 state outside ball-4 ----
    size_t l4lo = layer_start[4], l4hi = layer_start[5];
    size_t n4 = ball.size(), nraw5 = (l4hi - l4lo) * 36;
    std::vector<Rec> recs(n4 + nraw5);
    std::vector<std::uint8_t> keep(n4 + nraw5, 1);
    auto work = [&](int t) {
        for (size_t i = t; i < n4; i += threads) {
            make_rec(ball[i], recs[i]);
            recs[i].d = bd[i]; recs[i].parent = std::uint32_t(i); recs[i].gen = 255;
        }
        for (size_t j = t; j < nraw5; j += threads) {
            size_t s = l4lo + j / 36;
            int g = int(j % 36);
            Mat a = step(ball[s], gens[g]);
            Rec& r = recs[n4 + j];
            if (where.find(a) != where.end()) { keep[n4 + j] = 0; r.d = 99; continue; }
            make_rec(a, r);
            r.d = 5; r.parent = std::uint32_t(s); r.gen = std::uint8_t(g);
        }
    };
    {
        std::vector<std::thread> pool;
        for (int t = 0; t < threads; ++t) pool.emplace_back(work, t);
        for (auto& th : pool) th.join();
    }
    size_t w = 0;
    for (size_t i = 0; i < recs.size(); ++i) if (keep[i]) recs[w++] = recs[i];
    recs.resize(w);
    std::vector<std::uint8_t>().swap(keep);
    std::printf("raw_layer5_images %zu\nrecords_before_dedupe %zu\n", nraw5, recs.size());

    // sort by (key, xa, ya, d); a state is determined by its key and anchors
    std::vector<std::uint32_t> order(recs.size());
    for (size_t i = 0; i < order.size(); ++i) order[i] = std::uint32_t(i);
    std::sort(order.begin(), order.end(), [&](std::uint32_t x, std::uint32_t y) {
        const Rec &a = recs[x], &b = recs[y];
        int c = keycmp(a, b);
        if (c) return c < 0;
        if (a.xa != b.xa) return a.xa < b.xa;
        if (a.ya != b.ya) return a.ya < b.ya;
        if (a.d != b.d) return a.d < b.d;
        return x < y;
    });
    // dedupe states, then walk key buckets
    std::vector<std::uint32_t> uniq;
    uniq.reserve(order.size());
    for (size_t i = 0; i < order.size(); ++i) {
        if (!uniq.empty()) {
            const Rec &a = recs[uniq.back()], &b = recs[order[i]];
            if (keycmp(a, b) == 0 && a.xa == b.xa && a.ya == b.ya) continue;
        }
        uniq.push_back(order[i]);
    }
    std::vector<std::uint32_t>().swap(order);
    size_t layer5 = 0;
    for (auto u : uniq) layer5 += recs[u].d == 5;
    std::printf("layer5_distinct %zu\nball5_states %zu\n", layer5, uniq.size());

    // join
    static int best4[168][168], best[168][168];
    static std::uint32_t wa[168][168], wb[168][168];
    for (int a = 0; a < G; ++a)
        for (int b = 0; b < G; ++b) { best4[a][b] = 9; best[a][b] = 11; }
    size_t buckets = 0, buckets4 = 0, largest = 0, pairs = 0;
    for (size_t lo = 0; lo < uniq.size();) {
        size_t hi = lo + 1;
        while (hi < uniq.size() && keycmp(recs[uniq[lo]], recs[uniq[hi]]) == 0) ++hi;
        ++buckets;
        bool any4 = false;
        for (size_t i = lo; i < hi; ++i) any4 |= recs[uniq[i]].d <= 4;
        buckets4 += any4;
        largest = std::max(largest, hi - lo);
        for (size_t i = lo; i < hi; ++i) {
            const Rec& A = recs[uniq[i]];
            for (size_t j = lo; j < hi; ++j) {
                const Rec& B = recs[uniq[j]];
                ++pairs;
                int c = A.d + B.d;
                int ta = prod[A.xa][inv_[B.xa]], tb = prod[A.ya][inv_[B.ya]];
                if (A.d <= 4 && B.d <= 4 && c < best4[ta][tb]) best4[ta][tb] = c;
                if (c < best[ta][tb]) { best[ta][tb] = c; wa[ta][tb] = uniq[i]; wb[ta][tb] = uniq[j]; }
            }
        }
        lo = hi;
    }
    std::printf("key_buckets %zu\nkey_buckets_meeting_ball4 %zu\nlargest_bucket %zu\nordered_pairs %zu\n",
                buckets, buckets4, largest, pairs);

    // seed18 control: radius-4 join equals min(9, d(a)+d(b)) everywhere
    size_t mismatch4 = 0, exact_le9 = 0, open = 0;
    for (int a = 0; a < G; ++a)
        for (int b = 0; b < G; ++b) {
            int direct = dist_[a] + dist_[b];
            if (best4[a][b] != std::min(9, direct)) ++mismatch4;
            if (direct <= 9) ++exact_le9; else ++open;
            // direct words of length <= 10 split as 5+5, so the join must find
            // them; seed18's exact minimum for direct <= 9 is the direct cost.
            if (direct <= 9) need(best[a][b] == direct, "radius-5 join disagrees with exact direct minimum");
            else need(best[a][b] >= 9, "radius-5 join beats seed18's lower bound 9");
        }
    std::printf("radius4_table_mismatches %zu\npairs_direct_le9 %zu\npairs_direct_ge10 %zu\n",
                mismatch4, exact_le9, open);
    need(mismatch4 == 0, "radius-4 table differs from min(9,d(a)+d(b))");

    // report open pairs
    int hist[16][16] = {};
    auto word_of = [&](std::uint32_t ri, std::vector<int>& seq) {
        // applied left-multiplication sequence (first applied first) producing the state
        const Rec& r = recs[ri];
        std::uint32_t s = r.parent;
        std::vector<int> back;
        if (r.d == 5) back.push_back(r.gen);
        while (s != 0) { back.push_back(bgen[s]); s = bparent[s]; }
        seq.assign(back.rbegin(), back.rend());
    };
    std::vector<std::array<int, 4>> lines;
    for (int a = 0; a < G; ++a)
        for (int b = 0; b < G; ++b) {
            int direct = dist_[a] + dist_[b];
            if (direct < 10) continue;
            hist[direct][best[a][b]]++;
            std::printf("pair %d %d direct %d min_le10 %d", elem[a], elem[b], direct, best[a][b]);
            if (best[a][b] <= 10) {
                std::vector<int> sa, sb;
                word_of(wa[a][b], sa);
                word_of(wb[a][b], sb);
                // A B^-1: apply B's sequence reversed, then A's sequence
                std::printf(" word");
                for (auto it = sb.rbegin(); it != sb.rend(); ++it)
                    std::printf(" %d%d%d%d", gens[*it].u, gens[*it].v, LI[gens[*it].label], LJ[gens[*it].label]);
                for (int g : sa)
                    std::printf(" %d%d%d%d", gens[g].u, gens[g].v, LI[gens[g].label], LJ[gens[g].label]);
            }
            std::printf("\n");
        }
    for (int d = 10; d <= 12; ++d)
        for (int m = 0; m <= 11; ++m)
            if (hist[d][m]) std::printf("histogram direct %d min_le10 %d count %d\n", d, m, hist[d][m]);

    // ---- length 11 for the pairs still undecided (direct 12, no word <= 10) ----
    // A word of length 11 is (h C) B^-1 with C at distance 5, h a generator and
    // B in the radius-5 ball. h C has the same canonical key as B, and its anchors
    // determine the target. Stream every h C and look up the matching B exactly.
    if (!(argc > 2 && std::strcmp(argv[2], "--l11") == 0)) { std::printf("DONE\n"); return 0; }
    std::vector<std::array<int, 2>> targets;
    for (int a = 0; a < G; ++a)
        for (int b = 0; b < G; ++b)
            if ((dist_[a] + dist_[b] >= 12 && best[a][b] > 10) || dist_[a] + dist_[b] == 11)
                targets.push_back({a, b});  // undecided pairs, plus all direct-11 pairs as positive controls
    std::printf("l11_targets %zu\n", targets.size());
    std::vector<std::uint32_t> l5;
    for (auto u : uniq) if (recs[u].d == 5) l5.push_back(u);
    auto find_bucket = [&](const Rec& probe) -> std::pair<size_t, size_t> {
        size_t lo = 0, hi = uniq.size();
        while (lo < hi) { size_t m = (lo + hi) / 2; if (keycmp(recs[uniq[m]], probe) < 0) lo = m + 1; else hi = m; }
        size_t e = lo;
        while (e < uniq.size() && keycmp(recs[uniq[e]], probe) == 0) ++e;
        return {lo, e};
    };
    struct Hit { std::uint32_t c, b; int h, t; };
    std::vector<std::vector<Hit>> hits(threads);
    std::vector<size_t> images(threads, 0), matched(threads, 0);
    auto work11 = [&](int t) {
        for (size_t i = t; i < l5.size(); i += threads) {
            const Rec& C = recs[l5[i]];
            Mat m;
            m.e[0] = translate(C.key[0], C.xa); m.e[1] = translate(C.key[1], C.xa);
            m.e[2] = translate(C.key[2], C.ya); m.e[3] = translate(C.key[3], C.ya);
            for (int h = 0; h < 36; ++h) {
                Mat a = step(m, gens[h]);
                Rec r;
                make_rec(a, r);
                ++images[t];
                auto [lo, e] = find_bucket(r);
                if (lo == e) continue;
                ++matched[t];
                for (size_t k = 0; k < targets.size(); ++k) {
                    int xb = prod[inv_[targets[k][0]]][r.xa], yb = prod[inv_[targets[k][1]]][r.ya];
                    // a bucket is sorted by (xa, ya): binary search the exact anchors
                    size_t p = lo, q = e;
                    while (p < q) {
                        size_t m = (p + q) / 2;
                        const Rec& M = recs[uniq[m]];
                        if (M.xa < xb || (M.xa == xb && M.ya < yb)) p = m + 1; else q = m;
                    }
                    if (p < e && recs[uniq[p]].xa == xb && recs[uniq[p]].ya == yb)
                        hits[t].push_back({l5[i], uniq[p], h, int(k)});
                }
            }
        }
    };
    {
        std::vector<std::thread> pool;
        for (int t = 0; t < threads; ++t) pool.emplace_back(work11, t);
        for (auto& th : pool) th.join();
    }
    size_t nimg = 0, nmatch = 0, nhit = 0;
    for (int t = 0; t < threads; ++t) { nimg += images[t]; nmatch += matched[t]; nhit += hits[t].size(); }
    std::printf("l11_images %zu\nl11_images_meeting_ball5_keys %zu\nl11_hits %zu\n", nimg, nmatch, nhit);
    std::vector<int> best11(targets.size(), 12);
    std::vector<Hit> wit(targets.size());
    for (int t = 0; t < threads; ++t)
        for (const Hit& x : hits[t]) {
            int c = 6 + recs[x.b].d;
            // deterministic witness, independent of the thread count
            bool better = c < best11[x.t] ||
                (c == best11[x.t] && std::make_tuple(x.c, x.h, x.b) <
                                      std::make_tuple(wit[x.t].c, wit[x.t].h, wit[x.t].b));
            if (better) { best11[x.t] = c; wit[x.t] = x; }
        }
    for (size_t k = 0; k < targets.size(); ++k) {
        int a = targets[k][0], b = targets[k][1];
        std::printf("l11 pair %d %d direct %d min_le11 %d", elem[a], elem[b], dist_[a] + dist_[b], best11[k]);
        if (best11[k] <= 11) {
            std::vector<int> sa, sb;
            word_of(wit[k].c, sa);
            sa.push_back(wit[k].h);
            word_of(wit[k].b, sb);
            std::printf(" word");
            for (auto it = sb.rbegin(); it != sb.rend(); ++it)
                std::printf(" %d%d%d%d", gens[*it].u, gens[*it].v, LI[gens[*it].label], LJ[gens[*it].label]);
            for (int g : sa)
                std::printf(" %d%d%d%d", gens[g].u, gens[g].v, LI[gens[g].label], LJ[gens[g].label]);
        }
        std::printf("\n");
    }
    std::printf("DONE\n");
    return 0;
}
