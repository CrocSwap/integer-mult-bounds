// Independent packed-coefficient replay. Hanson Sun / OpenAI Codex, Apache-2.0.
// Group multiplication is composed on the three basis vectors; scalar
// idempotents are enumerated as 2x2 matrices, independently of algebra.py.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <unordered_map>
#include <vector>

using U = std::uint64_t;
struct Poly {
    std::array<U, 3> w{};
    bool operator==(const Poly& b) const { return w == b.w; }
    bool operator<(const Poly& b) const {
        for (int k = 2; k >= 0; --k) if (w[k] != b.w[k]) return w[k] < b.w[k];
        return false;
    }
    bool empty() const { return !(w[0] | w[1] | w[2]); }
    void toggle(int k) { w[k / 64] ^= U(1) << (k % 64); }
    Poly& operator^=(const Poly& b) {
        for (int k = 0; k < 3; ++k) w[k] ^= b.w[k];
        return *this;
    }
};
struct Matrix {
    std::array<Poly, 4> p{};
    bool operator==(const Matrix& b) const { return p == b.p; }
    bool operator<(const Matrix& b) const {
        for (int k = 0; k < 4; ++k) {
            if (p[k] < b.p[k]) return true;
            if (b.p[k] < p[k]) return false;
        }
        return false;
    }
};
struct Hash {
    std::size_t operator()(const Matrix& m) const {
        U h = 0x9e3779b97f4a7c15ULL;
        for (const auto& p : m.p) for (U v : p.w) {
            v ^= v >> 30; v *= 0xbf58476d1ce4e5b9ULL;
            v ^= v >> 27; v *= 0x94d049bb133111ebULL; v ^= v >> 31;
            h ^= v + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2);
        }
        return h;
    }
};
void check(bool ok, const char* message) { if (!ok) throw std::runtime_error(message); }
int parity(int x) { return __builtin_popcount(unsigned(x)) & 1; }
int action(int a, int x) {
    int y = 0;
    for (int r = 0; r < 3; ++r) y |= parity(((a >> (3*r)) & 7) & x) << r;
    return y;
}
int product(int a, int b) {
    int result = 0;
    for (int c = 0; c < 3; ++c) {
        int image = action(a, action(b, 1 << c));
        for (int r = 0; r < 3; ++r) result |= ((image >> r) & 1) << (3*r+c);
    }
    return result;
}
int rank(int a) {
    int rows[3] = {a & 7, (a >> 3) & 7, (a >> 6) & 7}, n = 0;
    for (int c = 0; c < 3; ++c) {
        int k = n;
        while (k < 3 && !(rows[k] & (1 << c))) ++k;
        if (k == 3) continue;
        std::swap(rows[k], rows[n]);
        for (int r = n+1; r < 3; ++r) if (rows[r] & (1 << c)) rows[r] ^= rows[n];
        ++n;
    }
    return n;
}
std::array<std::array<int,168>,168> multiplication;
std::array<int,168> inverse;
Poly translate(const Poly& p, int g) {
    Poly out;
    for (int limb = 0; limb < 3; ++limb) {
        U w = p.w[limb];
        while (w) {
            int j = __builtin_ctzll(w); w &= w-1;
            out.toggle(multiplication[g][64*limb+j]);
        }
    }
    return out;
}
struct Generator { int n, label; };
Matrix step(const Matrix& m, Generator z) {
    Matrix result = m;
    std::array<Poly,4> delta;
    for (int k = 0; k < 4; ++k) { delta[k] = translate(m.p[k], z.label); delta[k] ^= m.p[k]; }
    for (int r = 0; r < 2; ++r) for (int s = 0; s < 2; ++s)
        if (z.n & (1 << (2*r+s)))
            for (int c = 0; c < 2; ++c) result.p[2*r+c] ^= delta[2*s+c];
    return result;
}
struct Row { std::array<Poly,2> p; int coordinate; };
Row canonical(const Poly& a, const Poly& b) {
    const Poly& anchor = a.empty() ? b : a;
    check(!anchor.empty(), "zero row");
    Row best; bool first = true;
    for (int limb = 0; limb < 3; ++limb) {
        U w = anchor.w[limb];
        while (w) {
            int k = 64*limb + __builtin_ctzll(w); w &= w-1;
            Row q{{translate(a,inverse[k]),translate(b,inverse[k])}, k};
            bool smaller = q.p[0] < best.p[0] || (q.p[0] == best.p[0] && q.p[1] < best.p[1]);
            if (first || smaller) { best = q; first = false; }
            else check(!(q.p == best.p), "nontrivial row stabilizer");
        }
    }
    return best;
}
struct Node { Matrix m; int distance; };
struct Entry { int distance, a, b; };

int main(int argc, char** argv) {
    try {
        check(argc == 3, "usage: independent STATES.bin TABLE.bin");
        std::vector<int> group; std::array<int,512> index; index.fill(-1);
        for (int m = 0; m < 512; ++m) if (rank(m) == 3) { index[m] = int(group.size()); group.push_back(m); }
        check(group.size() == 168, "group size");
        int identity = index[273];
        for (int a = 0; a < 168; ++a) for (int b = 0; b < 168; ++b)
            multiplication[a][b] = index[product(group[a],group[b])];
        for (int a = 0; a < 168; ++a) {
            inverse[a] = -1;
            for (int b = 0; b < 168; ++b) if (multiplication[a][b] == identity) inverse[a] = b;
            check(inverse[a] >= 0, "missing inverse");
        }
        std::vector<int> labels;
        for (int r = 0; r < 3; ++r) for (int c = 0; c < 3; ++c)
            if (r != c) labels.push_back(index[273 ^ (1 << (3*r+c))]);
        std::vector<Generator> generators;
        for (int n = 0; n < 16; ++n) {
            int squared = 0;
            for (int r = 0; r < 2; ++r) for (int c = 0; c < 2; ++c) {
                int v = 0;
                for (int k = 0; k < 2; ++k) v ^= ((n >> (2*r+k)) & 1) & ((n >> (2*k+c)) & 1);
                squared |= v << (2*r+c);
            }
            if (squared == n && n != 0 && n != 9)
                for (int label : labels) generators.push_back({n,label});
        }
        check(generators.size() == 36, "generator alphabet");
        Matrix unit; unit.p[0].toggle(identity); unit.p[3].toggle(identity);
        std::vector<Node> nodes{{unit,0}};
        std::unordered_map<Matrix,int,Hash> seen; seen.reserve(700000); seen.emplace(unit,0);
        std::array<std::size_t,5> layers{1,0,0,0,0}; U transitions = 0;
        for (std::size_t cursor = 0; cursor < nodes.size(); ++cursor) {
            Node node = nodes[cursor];
            if (node.distance == 4) continue;
            for (auto z : generators) {
                ++transitions;
                Matrix target = step(node.m,z);
                if (seen.emplace(target,int(nodes.size())).second) {
                    nodes.push_back({target,node.distance+1}); ++layers[node.distance+1];
                }
            }
        }
        seen.clear(); seen.rehash(0);
        std::vector<std::size_t> order(nodes.size()); std::iota(order.begin(),order.end(),0);
        std::sort(order.begin(),order.end(),[&](auto a, auto b) {return nodes[a].m < nodes[b].m;});
        std::ofstream states(argv[1],std::ios::binary); check(bool(states), "state output");
        for (auto i : order) {
            for (const Poly& p : nodes[i].m.p) for (int k = 0; k < 21; ++k)
                states.put(char((p.w[k/8] >> (8*(k%8))) & 255));
            states.put(char(nodes[i].distance));
        }
        states.close(); check(bool(states), "state write failure");
        std::unordered_map<Matrix,std::vector<Entry>,Hash> buckets; buckets.reserve(150000);
        for (const Node& node : nodes) {
            Row top = canonical(node.m.p[0],node.m.p[1]), bottom = canonical(node.m.p[2],node.m.p[3]);
            Matrix key{{top.p[0],top.p[1],bottom.p[0],bottom.p[1]}};
            buckets[key].push_back({node.distance,top.coordinate,bottom.coordinate});
        }
        std::array<unsigned char,168*168> minimum; minimum.fill(9);
        U pairs = 0; std::size_t largest = 0;
        for (const auto& bucket : buckets) {
            const auto& entries = bucket.second;
            largest = std::max(largest,entries.size()); pairs += U(entries.size())*entries.size();
            for (auto a : entries) for (auto b : entries) {
                int x = multiplication[a.a][inverse[b.a]], y = multiplication[a.b][inverse[b.b]];
                auto& cell = minimum[168*x+y]; cell = std::min(int(cell),a.distance+b.distance);
            }
        }
        std::ofstream table(argv[2],std::ios::binary);
        table.write(reinterpret_cast<const char*>(minimum.data()), minimum.size());
        table.close(); check(bool(table), "table write failure");
        std::cout << "{\"layers\":[";
        for (int k = 0; k < 5; ++k) std::cout << (k ? "," : "") << layers[k];
        std::cout << "],\"states\":" << nodes.size() << ",\"transitions\":" << transitions
                  << ",\"cosets\":" << buckets.size() << ",\"largest_coset\":" << largest
                  << ",\"ordered_join_pairs\":" << pairs << "}\n";
    } catch (const std::exception& e) { std::cerr << e.what() << "\n"; return 1; }
}
