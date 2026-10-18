// Common-cut P112 census. Nick Petalas. Apache-2.0.
// Flat/orbit and dual-code methods descend from PR3161/3162.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
#include <boost/multiprecision/cpp_int.hpp>

using U = std::uint64_t;
using Integer = boost::multiprecision::cpp_int;
constexpr std::size_t direction_count = 1144;
constexpr std::size_t flat_limit = 788035;
constexpr std::size_t cut_limit = 65536;
constexpr std::size_t state_limit = 262144;
constexpr int budget = 14;
struct Mask {
    U lo = 0, hi = 0;
    bool operator==(const Mask& b) const { return lo == b.lo && hi == b.hi; }
    bool operator<(const Mask& b) const {
        return lo < b.lo || (lo == b.lo && hi < b.hi);
    }
};
constexpr Mask live{~U{0}, (U{1} << 48) - 1};
Mask operator|(Mask a, Mask b) { return {a.lo | b.lo, a.hi | b.hi}; }
Mask operator&(Mask a, Mask b) { return {a.lo & b.lo, a.hi & b.hi}; }
Mask operator^(Mask a, Mask b) { return {a.lo ^ b.lo, a.hi ^ b.hi}; }
Mask minus(Mask a, Mask b) { return {a.lo & ~b.lo, a.hi & ~b.hi}; }
int weight(Mask a) {
    return __builtin_popcountll(a.lo) + __builtin_popcountll(a.hi);
}
bool has(Mask a, int i) {
    assert(i >= 0 && i < 112);
    return i < 64 ? ((a.lo >> i) & 1U) : ((a.hi >> (i - 64)) & 1U);
}
void set_bit(Mask& a, int i) {
    assert(i >= 0 && i < 112);
    if (i < 64) a.lo |= U{1} << i;
    else a.hi |= U{1} << (i - 64);
}
void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}
struct Model {
    std::array<int, 112> labels{};
    std::array<std::array<int, 8>, direction_count> normals{};
    std::array<Mask, direction_count> off{};
    std::array<std::array<int, 112>, 12> generators{};
    std::array<Mask, 512> characters{};
};

Model read_model(const char* path) {
    std::ifstream input(path);
    require(static_cast<bool>(input), "cannot open fixture");
    Model model;
    std::array<bool, 512> seen{};
    for (int& x : model.labels) {
        require(static_cast<bool>(input >> x) && x > 0 && x < 512 && !seen[x],
                "invalid label");
        seen[x] = true;
    }
    for (auto& row : model.normals) {
        bool nonzero = false;
        for (int& x : row) {
            require(static_cast<bool>(input >> x) && x >= -4 && x <= 4,
                    "invalid normal coordinate");
            nonzero = nonzero || x != 0;
        }
        require(nonzero, "zero projective normal");
    }
    for (Mask& m : model.off) {
        require(static_cast<bool>(input >> m.lo >> m.hi) && (m.hi >> 48) == 0,
                "invalid support mask");
        const int n = weight(m);
        require(n == 53 || n == 56 || n == 70 || n == 73, "invalid support size");
    }
    for (auto& permutation : model.generators) {
        std::array<bool, 112> used{};
        for (int& x : permutation) {
            require(static_cast<bool>(input >> x) && x >= 0 && x < 112 && !used[x],
                    "invalid generator");
            used[x] = true;
        }
    }
    std::string trailing;
    require(!(input >> trailing), "trailing fixture input");
    for (int c = 0; c < 512; ++c)
        for (int i = 0; i < 112; ++i)
            if (__builtin_parity(static_cast<unsigned>(c & model.labels[i])))
                set_bit(model.characters[c], i);
    return model;
}

int binary_rank(const Model& model, Mask mask) {
    std::array<int, 9> basis{};
    int rank = 0;
    for (int i = 0; i < 112; ++i) {
        if (!has(mask, i)) continue;
        int x = model.labels[i];
        for (int bit = 8; bit >= 0; --bit) {
            if (((x >> bit) & 1) == 0) continue;
            if (basis[bit]) x ^= basis[bit];
            else { basis[bit] = x; ++rank; break; }
        }
    }
    return rank;
}

std::vector<Mask> all_flats(const Model& model) {
    std::vector<Mask> flats;
    flats.reserve(flat_limit);
    std::size_t matrices = 0;
    for (int a = 0; a < 7; ++a)
        for (int b = a + 1; b < 8; ++b)
            for (int c = b + 1; c < 9; ++c) {
                const std::array<int, 3> pivots{a, b, c};
                std::vector<std::pair<int, int>> free;
                for (int i = 0; i < 3; ++i)
                    for (int j = 0; j < pivots[i]; ++j)
                        if (j != a && j != b && j != c) free.emplace_back(i, j);
                require(free.size() <= 18, "RREF capacity");
                for (unsigned pattern = 0; pattern < (1U << free.size()); ++pattern) {
                    std::array<int, 3> ann{1 << a, 1 << b, 1 << c};
                    for (std::size_t k = 0; k < free.size(); ++k)
                        if ((pattern >> k) & 1U)
                            ann[free[k].first] |= 1 << free[k].second;
                    const Mask excluded = model.characters[ann[0]] |
                        model.characters[ann[1]] | model.characters[ann[2]];
                    const Mask m = minus(live, excluded);
                    ++matrices;
                    require(weight(m) <= 20, "six-flat capacity changed");
                    flats.push_back(m);
                }
            }
    require(matrices == flat_limit, "incomplete flat enumeration");
    std::sort(flats.begin(), flats.end());
    flats.erase(std::unique(flats.begin(), flats.end()), flats.end());
    require(flats.size() == 776806, "distinct flat count changed");
    return flats;
}

void independently_check_flats(const Model& model, const std::vector<Mask>& expected) {
    // Least successive coset representatives, not RREF pivot/free entries.
    // Adapted from Nick Petalas's PR3163 independent enumerator.
    std::vector<Mask> masks;
    masks.reserve(flat_limit);
    for (int a = 1; a < 512; ++a)
        for (int b = a + 1; b < 512; ++b) {
            if (b >= (a ^ b)) continue;
            for (int c = b + 1; c < 512; ++c) {
                if (c >= (c ^ a) || c >= (c ^ b) || c >= (c ^ a ^ b)) continue;
                const Mask excluded = model.characters[a] | model.characters[b] |
                    model.characters[c];
                require(masks.size() < flat_limit, "independent flat capacity");
                masks.push_back(minus(live, excluded));
            }
        }
    require(masks.size() == flat_limit, "incomplete independent flat enumeration");
    std::sort(masks.begin(), masks.end());
    masks.erase(std::unique(masks.begin(), masks.end()), masks.end());
    require(masks == expected, "independent flat inventory differs");
}
void check_two_flat_supplement(const Model& model, const std::vector<Mask>& flats) {
    // Recheck PR3185's exact root-cover premise, needed for the quotient basis.
    int roots = 0;
    for (Mask off : model.off) {
        const int size = weight(off);
        if (size != 53 && size != 56) continue;
        ++roots;
        std::set<Mask> high;
        for (Mask flat : flats) {
            const Mask intersection = flat & off;
            if (weight(intersection) >= 18) high.insert(intersection);
            require(high.size() <= 4096, "root-cover intersection capacity");
        }
        require(high.size() == (size == 53 ? 320U : 336U), "root-cover inventory");
        const std::vector<Mask> masks(high.begin(), high.end());
        int maximum = 0;
        for (std::size_t a = 0; a < masks.size(); ++a)
            for (std::size_t b = a; b < masks.size(); ++b)
                maximum = std::max(maximum, weight(masks[a] | masks[b]));
        require(maximum == 38, "two-flat root-cover bound changed");
    }
    require(roots == 120, "incomplete root-cover control");
}
using Tables = std::array<std::array<std::array<Mask, 256>, 14>, 12>;
Tables permutation_tables(const Model& model) {
    Tables result{};
    for (int g = 0; g < 12; ++g)
        for (int byte = 0; byte < 14; ++byte)
            for (int value = 0; value < 256; ++value)
                for (int bit = 0; bit < 8; ++bit)
                    if ((value >> bit) & 1)
                        set_bit(result[g][byte][value],
                                model.generators[g][8 * byte + bit]);
    return result;
}
Mask image(Mask m, int g, const Tables& tables) {
    Mask result{};
    for (int byte = 0; byte < 14; ++byte) {
        const U part = byte < 8 ? m.lo >> (8 * byte) : m.hi >> (8 * (byte - 8));
        result = result | tables[g][byte][part & 255];
    }
    return result;
}
std::size_t find_root(std::vector<std::size_t>& parents, std::size_t i) {
    for (std::size_t step = 0; step < parents.size(); ++step) {
        if (parents[i] == i) return i;
        parents[i] = parents[parents[i]];
        i = parents[i];
    }
    throw std::runtime_error("union-find cycle");
}
std::vector<std::size_t> representatives(const std::vector<Mask>& flats,
                                       const Tables& tables) {
    std::vector<std::size_t> parents(flats.size());
    std::iota(parents.begin(), parents.end(), std::size_t{0});
    for (std::size_t i = 0; i < flats.size(); ++i)
        for (int g = 0; g < 12; ++g) {
            const Mask transformed = image(flats[i], g, tables);
            const auto at = std::lower_bound(flats.begin(), flats.end(), transformed);
            require(at != flats.end() && *at == transformed, "flat orbit not closed");
            const auto j = static_cast<std::size_t>(at - flats.begin());
            const auto a = find_root(parents, i), b = find_root(parents, j);
            if (a != b) parents[a] = b;
        }
    std::vector<std::size_t> result;
    for (std::size_t i = 0; i < flats.size(); ++i)
        if (find_root(parents, i) == i) result.push_back(i);
    require(result.size() == 160, "first-flat orbit count changed");
    return result;
}

std::vector<Mask> small_characters(const Model& model, Mask residual) {
    std::vector<Mask> words;
    words.reserve(511);
    for (int c = 1; c < 512; ++c) {
        const Mask word = residual & model.characters[c];
        if (weight(word) > 0 && weight(word) <= budget) words.push_back(word);
    }
    std::sort(words.begin(), words.end());
    words.erase(std::unique(words.begin(), words.end()), words.end());
    return words;
}

bool deletable(const Model& model, Mask residual) {
    const int need = binary_rank(model, residual) - 6;
    if (need <= 0) return true;
    const auto words = small_characters(model, residual);
    if (need == 1) return !words.empty();
    for (std::size_t a = 0; a < words.size(); ++a)
        for (std::size_t b = a + 1; b < words.size(); ++b) {
            const Mask joined = words[a] | words[b];
            if (weight(joined) > budget) continue;
            if (need == 2) return true;
            for (std::size_t c = b + 1; c < words.size(); ++c)
                if (!(words[c] == (words[a] ^ words[b])) &&
                    weight(joined | words[c]) <= budget) return true;
        }
    return false;
}

std::vector<Mask> minimal_cuts(const Model& model, Mask residual) {
    const int need = binary_rank(model, residual) - 6;
    if (need <= 0) return {Mask{}};
    const auto words = small_characters(model, residual);
    std::set<Mask> cuts;
    if (need == 1) cuts.insert(words.begin(), words.end());
    else for (std::size_t a = 0; a < words.size(); ++a)
        for (std::size_t b = a + 1; b < words.size(); ++b) {
            const Mask joined = words[a] | words[b];
            if (weight(joined) > budget) continue;
            if (need == 2) cuts.insert(joined);
            else for (std::size_t c = b + 1; c < words.size(); ++c)
                if (!(words[c] == (words[a] ^ words[b])) &&
                    weight(joined | words[c]) <= budget) cuts.insert(joined | words[c]);
            require(cuts.size() <= cut_limit, "cut capacity exhausted");
        }
    std::vector<Mask> ordered(cuts.begin(), cuts.end());
    std::sort(ordered.begin(), ordered.end(), [](Mask a, Mask b) {
        return weight(a) < weight(b);
    });
    std::vector<Mask> minimal;
    for (Mask cut : ordered) {
        bool dominated = false;
        for (Mask old : minimal)
            if (minus(old, cut) == Mask{}) { dominated = true; break; }
        if (!dominated) minimal.push_back(cut);
    }
    return minimal;
}

Integer gcd_integer(Integer a, Integer b) {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    for (int step = 0; step < 4096; ++step) {
        if (b == 0) return a;
        Integer remainder = a % b;
        a = b; b = remainder;
    }
    throw std::runtime_error("gcd capacity exhausted");
}
int rational_rank(const Model& model, const std::vector<int>& directions) {
    require(directions.size() <= direction_count, "rank input capacity");
    std::array<std::array<Integer, 8>, 8> basis{};
    int rank = 0;
    for (int d : directions) {
        std::array<Integer, 8> row{};
        std::copy(model.normals[d].begin(), model.normals[d].end(), row.begin());
        for (int j = 0; j < 8; ++j) {
            if (row[j] == 0) continue;
            if (basis[j][j] == 0) { basis[j] = row; ++rank; break; }
            const Integer a = basis[j][j], b = row[j];
            Integer divisor = 0;
            for (int k = j; k < 8; ++k) {
                row[k] = a * row[k] - b * basis[j][k];
                divisor = gcd_integer(divisor, row[k]);
            }
            if (divisor != 0)
                for (int k = j; k < 8; ++k) row[k] /= divisor;
            for (const Integer& value : row) {
                const Integer magnitude = value < 0 ? -value : value;
                require(magnitude == 0 || boost::multiprecision::msb(magnitude) < 1024,
                        "rational-rank integer capacity exhausted");
            }
        }
        if (rank >= 6) return rank;
    }
    return rank;
}

struct Qualified { int direction; std::vector<Mask> cuts; };
std::vector<Mask> common_states(const std::vector<Qualified>& qualified) {
    std::set<Mask> states{Mask{}};
    for (const auto& item : qualified) {
        std::set<Mask> additions;
        for (Mask state : states)
            for (Mask cut : item.cuts) {
                const Mask next = state | cut;
                if (weight(next) <= budget) additions.insert(next);
                require(additions.size() <= state_limit, "union capacity exhausted");
            }
        states.insert(additions.begin(), additions.end());
        require(states.size() <= state_limit, "state capacity exhausted");
    }
    return {states.begin(), states.end()};
}
using Permutation = std::array<int, 112>;
using Table = std::array<std::array<Mask, 256>, 14>;
Permutation compose(const Permutation& a, const Permutation& b) {
    Permutation result{};
    for (int i = 0; i < 112; ++i) result[i] = a[b[i]];
    return result;
}
Permutation inverse(const Permutation& a) {
    Permutation result{};
    for (int i = 0; i < 112; ++i) result[a[i]] = i;
    return result;
}
std::vector<Permutation> fixing_maps(const Model& model, Mask first,
                                    const Tables& tables) {
    Permutation identity{};
    std::iota(identity.begin(), identity.end(), 0);
    std::vector<Mask> masks{first};
    std::vector<Permutation> walks{identity}, fixed;
    std::map<Mask, std::size_t> seen{{first, 0}};
    // Any subset of Schreier loops is safe. These are performance limits,
    // not claims that the full stabilizer or its orbit was enumerated.
    for (std::size_t cursor = 0; cursor < 512 && cursor < walks.size(); ++cursor) {
        for (int g = 0; g < 12; ++g) {
            const Mask target = image(masks[cursor], g, tables);
            const auto at = seen.find(target);
            const auto path = compose(model.generators[g], walks[cursor]);
            if (at == seen.end()) {
                if (walks.size() < 4096) {
                    const auto inserted = seen.emplace(target, walks.size());
                    require(inserted.second, "duplicate walk insertion");
                    masks.push_back(target);
                    walks.push_back(path);
                }
                continue;
            }
            const auto loop = compose(inverse(walks[at->second]), path);
            if (loop == identity || std::find(fixed.begin(), fixed.end(), loop) != fixed.end())
                continue;
            fixed.push_back(loop);
            if (fixed.size() == 32) return fixed;
        }
    }
    return fixed;
}
std::vector<Table> fixing_tables(const std::vector<Permutation>& fixed, Mask first) {
    require(fixed.size() <= 32, "fixing-map capacity");
    std::vector<Table> tables(fixed.size());
    for (std::size_t g = 0; g < fixed.size(); ++g) {
        Mask transformed{};
        for (int i = 0; i < 112; ++i)
            if (has(first, i)) set_bit(transformed, fixed[g][i]);
        require(transformed == first, "Schreier loop does not fix first mask");
        for (int byte = 0; byte < 14; ++byte)
            for (int value = 0; value < 256; ++value)
                for (int bit = 0; bit < 8; ++bit)
                    if ((value >> bit) & 1)
                        set_bit(tables[g][byte][value], fixed[g][8 * byte + bit]);
    }
    return tables;
}
bool omit_second(Mask second, const std::vector<Table>& fixed) {
    for (const Table& table : fixed) {
        Mask transformed{};
        for (int byte = 0; byte < 14; ++byte) {
            const U part = byte < 8 ? second.lo >> (8 * byte) : second.hi >> (8 * (byte - 8));
            transformed = transformed | table[byte][part & 255];
        }
        if (transformed < second) return true;
    }
    return false;
}
struct Counts {
    U pairs = 0, oracles = 0, candidates = 0, states = 0;
    std::size_t max_states = 0, max_cuts = 0;
};
void check_pair(const Model& model, Mask cover, const std::vector<int>& directions,
                Counts& counts) {
    std::vector<Qualified> qualified;
    std::size_t total_cuts = 0;
    for (int d : directions) {
        auto cuts = minimal_cuts(model, minus(model.off[d], cover));
        require(!cuts.empty(), "lost positive direction");
        total_cuts += cuts.size();
        require(total_cuts <= cut_limit, "pair cut capacity exhausted");
        qualified.push_back({d, std::move(cuts)});
    }
    const auto states = common_states(qualified);
    ++counts.candidates;
    counts.states += states.size();
    counts.max_states = std::max(counts.max_states, states.size());
    counts.max_cuts = std::max(counts.max_cuts, total_cuts);
    for (Mask state : states) {
        std::vector<int> admitted;
        for (const auto& item : qualified)
            for (Mask cut : item.cuts)
                if (minus(cut, state) == Mask{}) {
                    admitted.push_back(item.direction); break;
                }
        if (admitted.size() < 6) continue;
        require(rational_rank(model, admitted) <= 5, "common span exceeds five");
    }
}

void scan(const Model& model, const std::vector<Mask>& flats,
          const std::vector<std::size_t>& reps, const Tables& tables,
          std::size_t start, std::size_t length) {
    for (std::size_t ri = start; ri < start + length; ++ri) {
        const Mask first = flats[reps[ri]];
        const auto fixing = fixing_tables(fixing_maps(model, first, tables), first);
        std::vector<int> active;
        std::array<Mask, direction_count> residual{};
        for (std::size_t d = 0; d < direction_count; ++d) {
            residual[d] = minus(model.off[d], first);
            if (weight(residual[d]) <= 54) active.push_back(static_cast<int>(d));
        }
        Counts counts;
        for (Mask second : flats) {
            if (weight(first) + weight(second) < 19) continue;
            if (omit_second(second, fixing)) continue;
            ++counts.pairs;
            std::vector<int> directions;
            for (int d : active) {
                const Mask rest = minus(residual[d], second);
                if (weight(rest) > 34) continue;
                ++counts.oracles;
                if (deletable(model, rest)) directions.push_back(d);
            }
            if (directions.size() < 6 || rational_rank(model, directions) <= 5) continue;
            check_pair(model, first | second, directions, counts);
        }
        std::cout << "ROW " << ri << ' ' << reps[ri] << ' ' << weight(first)
                  << ' ' << fixing.size() << ' ' << counts.pairs << ' '
                  << counts.oracles << ' ' << counts.candidates << ' '
                  << counts.states << ' ' << counts.max_states << ' '
                  << counts.max_cuts << '\n';
        std::cout.flush();
        require(static_cast<bool>(std::cout), "output failed");
    }
    std::cout << "PASS_COMMON_FOURTEEN " << start << ' ' << length << '\n';
    require(static_cast<bool>(std::cout), "completion output failed");
}

int parse_integer(const char* text) {
    std::size_t used = 0;
    const std::string value(text);
    const int result = std::stoi(value, &used);
    require(used == value.size(), "invalid integer argument");
    return result;
}
void rank_controls(const Model& model) {
    std::uint32_t seed = 20261017;
    for (int i = 0; i < 96; ++i) {
        std::vector<int> directions;
        const int length = i % 10;
        std::cout << "RANK " << i << ' ' << length;
        for (int j = 0; j < length; ++j) {
            seed = seed * 1664525U + 1013904223U;
            const int d = static_cast<int>(seed % direction_count);
            directions.push_back(i % 3 == 0 && !directions.empty() ? directions[0] : d);
            std::cout << ' ' << directions.back();
        }
        std::cout << ' ' << rational_rank(model, directions) << '\n';
    }
    require(static_cast<bool>(std::cout), "rank-control output failed");
}
void self_test() {
    Model model;
    for (int i = 0; i < 112; ++i) model.labels[i] = 1 << (i % 9);
    for (int c = 0; c < 512; ++c)
        for (int i = 0; i < 112; ++i)
            if (__builtin_parity(static_cast<unsigned>(c & model.labels[i])))
                set_bit(model.characters[c], i);
    for (int n = 7; n <= 9; ++n) {
        const Mask residual{(U{1} << n) - 1, 0};
        const auto cuts = minimal_cuts(model, residual);
        const std::size_t expected = n == 7 ? 7 : (n == 8 ? 28 : 84);
        require(cuts.size() == expected, "missing minimal dual-code cuts");
        for (Mask cut : cuts)
            require(weight(cut) == n - 6 &&
                    binary_rank(model, minus(residual, cut)) == 6,
                    "unsound dual-code cut");
    }
    require(!deletable(model, live), "accepted over-budget repeated basis");
    require(minimal_cuts(model, live).empty(), "false repeated-basis cut");
    const std::vector<Qualified> separate{{0, {Mask{255, 0}}},
                                        {1, {Mask{65280, 0}}}};
    const auto states = common_states(separate);
    require(states.size() == 3 &&
            std::find(states.begin(), states.end(), Mask{65535, 0}) == states.end(),
            "separate cuts mistaken for common cut");
    for (int d = 0; d < 8; ++d) model.normals[d][d] = 1;
    require(rational_rank(model, {0, 1, 2, 3, 4, 5}) == 6,
            "independent rational-rank control");
    model.normals[5] = model.normals[4];
    require(rational_rank(model, {0, 1, 2, 3, 4, 5}) == 5,
            "dependent rational-rank control");
    std::cout << "PASS_COMMON_CUT_CONTROLS\n";
    require(static_cast<bool>(std::cout), "control output failed");
}
int main(int argc, char** argv) {
    try {
        require(__builtin_cpu_supports("popcnt"), "CPU POPCNT support required");
        if (argc == 2 && std::string(argv[1]) == "--self-test") {
            self_test();
            return 0;
        }
        if (argc == 3 && std::string(argv[1]) == "--rank-controls") {
            rank_controls(read_model(argv[2]));
            return 0;
        }
        require(argc == 4, "usage: census FIXTURE START COUNT");
        const int start = parse_integer(argv[2]), length = parse_integer(argv[3]);
        require(start >= 0 && start < 160 && length >= 1 && length <= 160 - start,
                "invalid orbit range");
        const Model model = read_model(argv[1]);
        const auto flats = all_flats(model);
        independently_check_flats(model, flats);
        check_two_flat_supplement(model, flats);
        const auto tables = permutation_tables(model);
        const auto reps = representatives(flats, tables);
        scan(model, flats, reps, tables, static_cast<std::size_t>(start),
             static_cast<std::size_t>(length));
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FAIL: " << error.what() << '\n';
        return 2;
    }
}
