// Check four-register subset collisions with exact row reduction over F101.
// This file is derived from the PR468 field engine.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using Row = std::array<unsigned char, 8>;

int prod[101][101], inverse[101], num[101], den[101], outer_table[16][16];
constexpr int ID = 33825;
const int OFF_BITS[6] = {1,2,4,6,8,9};

int minus_product(int a, int t, int b) {
    int q = a - prod[t][b];
    return q < 0 ? q + 101 : q;
}

struct Basis {
    std::array<Row, 3> a{};
    std::array<unsigned char, 3> p{};
    int n = 0;

    bool operator==(const Basis& b) const { return a == b.a; }
};

struct BasisHash {
    size_t operator()(const Basis& b) const {
        size_t h = 0xcbf29ce484222325ULL;
        for (const auto& r : b.a)
            for (int x : r)
                h = (h ^ x) * 0x100000001b3ULL;
        return h;
    }
};

Row subset(int m) {
    Row v{};
    for (int i = 0; i < 8; ++i)
        v[i] = (m >> i) & 1;
    return v;
}

Row residual(Row v, const Basis& b) {
    for (int i = 0; i < b.n; ++i) {
        int t = v[b.p[i]];
        if (t)
            for (int j = b.p[i]; j < 8; ++j)
                v[j] = minus_product(v[j], t, b.a[i][j]);
    }
    return v;
}

Basis insert(Basis b, Row v) {
    v = residual(v, b);
    int p = 0;
    while (p < 8 && !v[p])
        ++p;
    if (p == 8)
        return b;
    if (b.n == 3)
        throw std::logic_error("A state has too many relations");

    int q = inverse[v[p]];
    for (int j = p; j < 8; ++j)
        v[j] = prod[v[j]][q];
    for (int i = 0; i < b.n; ++i) {
        int t = b.a[i][p];
        if (t)
            for (int j = p; j < 8; ++j)
                b.a[i][j] = minus_product(b.a[i][j], t, v[j]);
    }
    int at = b.n;
    while (at && b.p[at - 1] > p) {
        b.a[at] = b.a[at - 1];
        b.p[at] = b.p[at - 1];
        --at;
    }
    b.a[at] = v;
    b.p[at] = p;
    ++b.n;
    return b;
}

int binrank(const std::vector<int>& rows) {
    int b[8]{}, n = 0;
    for (int v : rows) {
        for (int k = 7; k >= 0; --k) {
            if (!((v >> k) & 1))
                continue;
            if (b[k]) {
                v ^= b[k];
            } else {
                b[k] = v;
                ++n;
                break;
            }
        }
    }
    return n;
}

int primitive_parity(const Row& r) {
    int d = 1;
    for (int x : r) {
        if (!den[x])
            throw std::logic_error("Rational reconstruction exceeds the proved bound");
        d = std::lcm(d, den[x]);
    }
    int v[8], g = 0;
    for (int i = 0; i < 8; ++i) {
        v[i] = num[r[i]] * (d / den[r[i]]);
        g = std::gcd(g, std::abs(v[i]));
    }
    int bits = 0;
    for (int i = 0; i < 8; ++i)
        bits |= (std::abs(v[i] / g) & 1) << i;
    return bits;
}

struct GeneralBasis {
    std::array<Row, 6> a{};
    std::array<int, 6> p{};
    int n = 0;

    explicit GeneralBasis(const Basis& b) {
        n = b.n;
        for (int i = 0; i < n; ++i) {
            a[i] = b.a[i];
            p[i] = b.p[i];
        }
    }

    bool add(Row v) {
        for (int i = 0; i < n; ++i) {
            int t = v[p[i]];
            if (t)
                for (int j = p[i]; j < 8; ++j)
                    v[j] = minus_product(v[j], t, a[i][j]);
        }
        int j = 0;
        while (j < 8 && !v[j])
            ++j;
        if (j == 8)
            return false;
        int q = inverse[v[j]];
        for (int k = j; k < 8; ++k)
            v[k] = prod[v[k]][q];
        int at = n;
        while (at && p[at - 1] > j) {
            a[at] = a[at - 1];
            p[at] = p[at - 1];
            --at;
        }
        a[at] = v;
        p[at] = j;
        ++n;
        return true;
    }
};

bool target_small(int mask, const Basis& b) {
    if (__builtin_popcount(static_cast<unsigned>(mask)) <= 2)
        return true;
    for (int i = 0; i < 8; ++i) {
        for (int j = i + 1; j < 8; ++j) {
            GeneralBasis g(b);
            g.add(subset(1 << i));
            g.add(subset(1 << j));
            if (!g.add(subset(mask)))
                return true;
        }
    }
    return false;
}

struct Group {
    uint64_t key;
    int mask, coefficient;
};

struct Search {
    std::array<int, 8> word;
    int ancillas = 15;
    uint64_t index = 0;
    std::array<int, 4> diagonal{};
    std::vector<std::pair<int, int>> terms;
    std::vector<int> off;
    std::unordered_set<Basis, BasisHash> visited;
    uint64_t states[4]{}, parity = 0, zero = 0, terminals = 0;
    uint64_t robust = 0, not_monomial = 0;

    void start() {
        int coefficients[256]{};
        coefficients[0] = ID;
        for (int j = 0; j < 8; ++j) {
            int x = 0, y = 0;
            for (int i = 0; i < 4; ++i) {
                int row = (word[j] >> (4*i)) & 15;
                if (row) {
                    if (y && y != row) throw std::logic_error("A projector has rank greater than one");
                    y = row; x |= 1 << i;
                }
            }
            if (!x || !y || !(__builtin_parity(unsigned(x&y))))
                throw std::logic_error("A projector is not a nonzero rank-one idempotent");
            for (int m = 0; m < (1 << j); ++m) {
                int c = coefficients[m], u = 0;
                for (int i = 0; i < 4; ++i)
                    u |= __builtin_parity(unsigned(((c >> (4*i)) & 15) & x)) << i;
                int right = outer_table[u][y];
                coefficients[m] = c ^ right;
                coefficients[m | (1 << j)] = right;
            }
        }
        for (int m = 0; m < 256; ++m)
            if (coefficients[m])
                terms.emplace_back(m, coefficients[m]);
        for (int bit : OFF_BITS) {
            int v = 0;
            for (int j = 0; j < 8; ++j)
                v |= ((word[j] >> bit) & 1) << j;
            off.push_back(v);
        }
        for (int w = 0; w < 4; ++w)
            for (int j = 0; j < 8; ++j)
                diagonal[w] |= ((word[j] >> (5*w)) & 1) << j;
        go(Basis{});
    }

    int allowed(const Basis& b) const {
        auto ps = off;
        for (int i = 0; i < b.n; ++i) ps.push_back(primitive_parity(b.a[i]));
        return binrank(ps) <= 3;
    }

    bool nonzero_frames(const Basis& b) const {
        for (int i = 0; i < b.n; ++i) {
            int count = 0;
            for (int v : b.a[i]) count += v != 0;
            if (count == 1) return false;
        }
        return true;
    }

    void go(const Basis& b) {
        if (!visited.insert(b).second)
            return;
        ++states[b.n];
        int possible = allowed(b);
        if (!possible) { ++parity; return; }
        if (!nonzero_frames(b)) { ++zero; return; }

        std::unordered_map<uint64_t, int> positions;
        std::vector<Group> groups;
        positions.reserve(terms.size());
        groups.reserve(terms.size());
        for (auto [mask, c] : terms) {
            auto v = residual(subset(mask), b);
            uint64_t key = 0;
            for (int j = 0; j < 8; ++j)
                key |= uint64_t(v[j]) << (7 * j);
            auto [it, fresh] = positions.emplace(key, int(groups.size()));
            if (fresh)
                groups.push_back({key, mask, c});
            else
                groups[it->second].coefficient ^= c;
        }

        std::vector<Group> active;
        int counts[16]{};
        for (auto g : groups) {
            if (g.coefficient) {
                active.push_back(g);
                for (int bit : OFF_BITS)
                    counts[bit] += (g.coefficient >> bit) & 1;
            }
        }
        int chosen = -1;
        for (int bit : OFF_BITS)
            if (counts[bit] && (chosen < 0 || counts[bit] < counts[chosen]))
                chosen = bit;

        if (chosen < 0) {
            int target[3] = {-1,-1,-1};
            std::vector<Group> need;
            for (int w=0; w<3; ++w) {
                std::vector<Group> diagonal_terms;
                for (auto g:active) if ((g.coefficient >> (5*w)) & 1) diagonal_terms.push_back(g);
                if (diagonal_terms.empty()) throw std::logic_error("An active diagonal has zero augmentation");
                if (diagonal_terms.size()==1) target[w]=diagonal_terms[0].mask;
                else if (need.empty() || diagonal_terms.size()<need.size()) need=diagonal_terms;
            }
            if (!need.empty()) {
                if (b.n==3) return;
                // At most one of the first two terms can survive in a monomial.
                for (int i=0; i<2; ++i) for (int j=i+1; j<int(need.size()); ++j) {
                    Row v{};
                    for (int k=0;k<8;++k) {
                        int t=((need[i].mask>>k)&1)-((need[j].mask>>k)&1);
                        v[k]=t<0?100:t;
                    }
                    auto c=insert(b,v);
                    if (c.n!=b.n+1) throw std::logic_error("A diagonal partner is in the same group");
                    go(c);
                }
                return;
            }
            ++terminals;
            for (int w=0;w<3;++w) if (target_small(target[w],b)) return;
            ++robust;
            std::cerr << "ROBUST " << index << " word";
            for (int n:word) std::cerr << ' ' << n;
            std::cerr << " targets";
            for(int t:target)std::cerr << ' ' << t;
            std::cerr << " relations";
            for(int i=0;i<b.n;++i) {
                std::cerr << " [";
                for(int k=0;k<8;++k)std::cerr << num[b.a[i][k]] << '/' << den[b.a[i][k]] << ',';
                std::cerr << ']';
            }
            std::cerr << '\n';
            return;
        }

        if (b.n == 3)
            return;
        int first = 0;
        while (!((active[first].coefficient >> chosen) & 1))
            ++first;
        for (int j = first + 1; j < int(active.size()); ++j) {
            if ((active[j].coefficient >> chosen) & 1) {
                Row v{};
                for (int k = 0; k < 8; ++k) {
                    int t = ((active[first].mask >> k) & 1) -
                            ((active[j].mask >> k) & 1);
                    v[k] = t < 0 ? 100 : t;
                }
                auto c = insert(b, v);
                if (c.n != b.n + 1)
                    throw std::logic_error("A partner is already in the same group");
                go(c);
            }
        }
    }
};

void setup() {
    for (int a = 0; a < 101; ++a)
        for (int b = 0; b < 101; ++b)
            prod[a][b] = (a * b) % 101;
    for (int a = 1; a < 101; ++a)
        for (int b = 1; b < 101; ++b)
            if (prod[a][b] == 1)
                inverse[a] = b;
    for (int d = 1; d <= 5; ++d) {
        for (int n = -5; n <= 5; ++n) {
            if (std::gcd(std::abs(n), d) == 1) {
                int x = prod[(n + 101) % 101][inverse[d]];
                if (den[x] && (num[x] != n || den[x] != d))
                    throw std::logic_error("Rational reconstruction is not unique");
                num[x] = n;
                den[x] = d;
            }
        }
    }
    for (int x = 0; x < 16; ++x)
        for (int y = 0; y < 16; ++y)
            for (int i = 0; i < 4; ++i)
                if ((x >> i) & 1) outer_table[x][y] |= y << (4*i);
}

int main(int argc,char**argv) {
    try {
        if(argc!=4)throw std::runtime_error("Usage: two_bases ALPHABETS INDEX OUTPUT_JSON");
        setup();
        std::ifstream alphabet_file(argv[1]);
        int index=std::stoi(argv[2]);
        std::vector<std::pair<int,int>> alphabet;
        for(int line=0;line<=index;++line) {
            alphabet.clear();
            for(int j=0;j<8;++j) {
                int x,y;
                if(!(alphabet_file>>x>>y))throw std::runtime_error("Cannot read alphabet");
                alphabet.emplace_back(x,y);
            }
        }
        std::sort(alphabet.begin(),alphabet.end());
        alphabet.erase(std::unique(alphabet.begin(),alphabet.end()),alphabet.end());
        int count=int(alphabet.size());
        int matrices[8],hit[8][14],labels[8]{},distance[14]{};
        bool commutes[8][8];
        for(int j=0;j<count;++j) {
            auto[x,y]=alphabet[j];
            matrices[j]=outer_table[x][y];
            for(int r=1;r<8;++r) {
                hit[j][r-1]=__builtin_parity(unsigned(x&r));
                hit[j][r+6]=__builtin_parity(unsigned(y&r));
            }
        }
        for(int i=0;i<count;++i)for(int j=0;j<count;++j) {
            auto[x,y]=alphabet[i];auto[u,v]=alphabet[j];
            int a=__builtin_parity(unsigned(y&u))?outer_table[x][v]:0;
            int b=__builtin_parity(unsigned(v&x))?outer_table[u][y]:0;
            commutes[i][j]=a==b;
        }
        uint64_t prefixes=0,leaves=0,words=0,terminals=0,robust=0,parity=0,zero=0,states[4]{};
        bool stopped=false;
        auto begun=std::chrono::steady_clock::now();
        auto walk=[&](auto&&self,int depth)->void {
            if(stopped)return;
            ++prefixes;
            for(int r=0;r<14;++r)if(distance[r]+8-depth<3)return;
            if(depth==8) {
                ++leaves;
                Search search;search.index=words;
                for(int j=0;j<8;++j)search.word[j]=matrices[labels[j]];
                search.start();++words;
                for(int k=0;k<4;++k)states[k]+=search.states[k];
                terminals+=search.terminals;robust+=search.robust;parity+=search.parity;zero+=search.zero;
                if(search.robust)stopped=true;
                return;
            }
            for(int j=0;j<count;++j) {
                bool normal=true;
                for(int k=depth-1;k>=0;--k) {
                    if(!commutes[labels[k]][j])break;
                    if(labels[k]>j){normal=false;break;}
                }
                if(!normal)continue;
                labels[depth]=j;
                for(int r=0;r<14;++r)distance[r]+=hit[j][r];
                self(self,depth+1);
                for(int r=0;r<14;++r)distance[r]-=hit[j][r];
            }
        };
        walk(walk,0);
        double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-begun).count();
        std::ofstream out(argv[3]);if(!out)throw std::runtime_error("Cannot open output");
        out << "{\"basis\":"<<index<<",\"alphabet_size\":"<<count<<",\"complete\":" << (stopped?"false":"true") << ",\"prefixes\":" << prefixes
            << ",\"distance_trace_words\":" << leaves << ",\"searched_words\":" << words << ",\"states\":[" << states[0] << ',' << states[1] << ',' << states[2] << ',' << states[3]
            << "],\"terminals\":" << terminals << ",\"robust\":" << robust << ",\"parity_prunes\":" << parity << ",\"zero_frame_prunes\":" << zero << ",\"seconds\":" << seconds << "}\n";
        if(!out)throw std::runtime_error("Cannot write output");
        return 0;
    } catch(const std::exception& e) {std::cerr << e.what() << '\n';return 1;}
}
