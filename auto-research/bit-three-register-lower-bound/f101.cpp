// Check subset collisions with exact row reduction over F101.
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

int prod[101][101], inverse[101], num[101], den[101], mm[512][512];

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
    std::vector<std::pair<int, int>> terms;
    std::vector<int> off;
    std::unordered_set<Basis, BasisHash> visited;
    uint64_t states[4]{}, parity = 0, zero = 0, terminals = 0;
    uint64_t robust = 0, not_monomial = 0;

    void start() {
        int coefficients[256]{};
        coefficients[0] = 273;
        for (int j = 0; j < 8; ++j) {
            for (int m = 0; m < (1 << j); ++m) {
                int c = coefficients[m];
                coefficients[m] = mm[c][273 ^ word[j]];
                coefficients[m | (1 << j)] = mm[c][word[j]];
            }
        }
        for (int m = 0; m < 256; ++m)
            if (coefficients[m])
                terms.emplace_back(m, coefficients[m]);
        for (int bit : {1, 2, 3, 5, 6, 7}) {
            int v = 0;
            for (int j = 0; j < 8; ++j)
                v |= ((word[j] >> bit) & 1) << j;
            off.push_back(v);
        }
        go(Basis{});
    }

    void go(const Basis& b) {
        if (!visited.insert(b).second)
            return;
        ++states[b.n];
        auto ps = off;
        for (int i = 0; i < b.n; ++i)
            ps.push_back(primitive_parity(b.a[i]));
        if (binrank(ps) > 3) {
            ++parity;
            return;
        }
        for (int i = 0; i < b.n; ++i) {
            int entries = 0;
            for (int v : b.a[i])
                entries += v != 0;
            if (entries == 1) {
                ++zero;
                return;
            }
        }

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
        int counts[9]{};
        for (auto g : groups) {
            if (g.coefficient) {
                active.push_back(g);
                for (int bit : {1, 2, 3, 5, 6, 7})
                    counts[bit] += (g.coefficient >> bit) & 1;
            }
        }
        int chosen = -1;
        for (int bit : {1, 2, 3, 5, 6, 7})
            if (counts[bit] && (chosen < 0 || counts[bit] < counts[chosen]))
                chosen = bit;

        if (chosen < 0) {
            int target[3] = {-1, -1, -1};
            for (auto g : active) {
                for (int w = 0; w < 3; ++w) {
                    if ((g.coefficient >> (4 * w)) & 1) {
                        if (target[w] >= 0) {
                            ++not_monomial;
                            return;
                        }
                        target[w] = g.mask;
                    }
                }
            }
            for (int m : target) {
                if (m < 0) {
                    ++not_monomial;
                    return;
                }
            }
            ++terminals;
            for (int m : target)
                if (target_small(m, b))
                    return;
            ++robust;
            std::cerr << "ROBUST";
            for (int n : word)
                std::cerr << ' ' << n;
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
    for (int a = 0; a < 512; ++a) {
        for (int b = 0; b < 512; ++b) {
            int c = 0;
            for (int i = 0; i < 3; ++i) {
                for (int j = 0; j < 3; ++j) {
                    int t = 0;
                    for (int k = 0; k < 3; ++k)
                        t ^= ((a >> (3 * i + k)) & 1) & ((b >> (3 * k + j)) & 1);
                    c |= t << (3 * i + j);
                }
            }
            mm[a][b] = c;
        }
    }
}

struct InputCase {
    int id;
    std::array<int, 8> word;
};

int main(int argc, char** argv) {
    try {
        if (argc != 3)
            throw std::runtime_error("Usage: f101 INPUT RESULTS");
        setup();
        std::ifstream input(argv[1]);
        if (!input)
            throw std::runtime_error("Cannot open input: " + std::string(argv[1]));
        int count;
        if (!(input >> count) || count <= 0)
            throw std::runtime_error("The case count must be a positive integer");

        std::vector<InputCase> cases;
        std::unordered_set<int> ids;
        for (int c = 0; c < count; ++c) {
            InputCase entry;
            if (!(input >> entry.id))
                throw std::runtime_error("Incomplete input: missing case ID");
            if (!ids.insert(entry.id).second)
                throw std::runtime_error("Duplicate case ID: " + std::to_string(entry.id));
            for (int& n : entry.word) {
                if (!(input >> n))
                    throw std::runtime_error("Incomplete input: missing projector");
                // Controls can use rank-two idempotents. Their acceptance is
                // not a physical construction. The catalogue checks rank one.
                if (n <= 0 || n >= 512 || mm[n][n] != n)
                    throw std::runtime_error("Each projector must be a nonzero 3-by-3 binary idempotent");
            }
            cases.push_back(entry);
        }
        input >> std::ws;
        auto trailing = input.peek();
        if (input.bad())
            throw std::runtime_error("Cannot read input: " + std::string(argv[1]));
        if (trailing != std::ifstream::traits_type::eof())
            throw std::runtime_error("Input has extra data after the last case");

        std::ofstream output(argv[2]);
        if (!output)
            throw std::runtime_error("Cannot open output: " + std::string(argv[2]));
        uint64_t allwords = 0, allrob = 0;
        auto begun = std::chrono::steady_clock::now();
        for (int c = 0; c < count; ++c) {
            auto ns = cases[c].word;
            std::sort(ns.begin(), ns.end());
            uint64_t totals[4]{}, terminal = 0, rob = 0, parity = 0;
            uint64_t zero = 0, words = 0, invalid = 0;
            do {
                Search s;
                s.word = ns;
                s.start();
                for (int k = 0; k < 4; ++k)
                    totals[k] += s.states[k];
                terminal += s.terminals;
                rob += s.robust;
                parity += s.parity;
                zero += s.zero;
                invalid += s.not_monomial;
                ++words;
            } while (std::next_permutation(ns.begin(), ns.end()));
            output << "{\"case\":" << cases[c].id << ",\"words\":" << words
                   << ",\"states\":[" << totals[0] << ',' << totals[1] << ','
                   << totals[2] << ',' << totals[3] << "],\"terminals\":" << terminal
                   << ",\"robust\":" << rob << ",\"parity_prunes\":" << parity
                   << ",\"zero_frame_prunes\":" << zero
                   << ",\"nonmonomial_diagonal\":" << invalid << "}\n";
            output.flush();
            if (!output)
                throw std::runtime_error("Cannot write output: " + std::string(argv[2]));
            allwords += words;
            allrob += rob;
            if ((c + 1) % 10 == 0 || c + 1 == count) {
                double seconds = std::chrono::duration<double>(
                    std::chrono::steady_clock::now() - begun).count();
                std::cerr << c + 1 << " / " << count << " families, " << allwords
                          << " words, " << allrob << " robust, " << seconds << " seconds\n";
            }
        }
        output.close();
        if (!output)
            throw std::runtime_error("Cannot close output: " + std::string(argv[2]));
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
