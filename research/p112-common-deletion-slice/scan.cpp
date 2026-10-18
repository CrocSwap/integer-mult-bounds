// Exact, bounded C5 slice. Nick Petalas. Apache-2.0.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>
#include <boost/multiprecision/cpp_int.hpp>

// GCC and Clang provide this fixed-width integer on the supported POSIX host.
__extension__ typedef unsigned __int128 Mask;
using Integer = boost::multiprecision::cpp_int;
using Row = std::array<int, 8>;
constexpr std::size_t flat_limit = 788035;
constexpr std::size_t state_limit = 65536;
constexpr Mask live = (Mask{1} << 112) - 1;

void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}

int weight(Mask mask) {
    return __builtin_popcountll(static_cast<std::uint64_t>(mask)) +
           __builtin_popcountll(static_cast<std::uint64_t>(mask >> 64));
}

struct System {
    Mask off = 0;
    std::vector<Row> normals;
};

struct Model {
    std::array<int, 112> labels{};
    std::array<Mask, 512> characters{};
    Mask first = 0;
    std::vector<System> systems;
};

Model read_model() {
    Model model;
    for (int& label : model.labels) {
        require(static_cast<bool>(std::cin >> label), "missing label");
        require(label > 0 && label < 512, "invalid label");
    }
    auto sorted = model.labels;
    std::sort(sorted.begin(), sorted.end());
    require(std::adjacent_find(sorted.begin(), sorted.end()) == sorted.end(),
            "duplicate label");
    std::uint64_t low = 0, high = 0;
    require(static_cast<bool>(std::cin >> low >> high), "missing first mask");
    model.first = Mask{low} | (Mask{high} << 64);
    require((model.first & ~live) == 0 && weight(model.first) == 20,
            "invalid first mask");
    int count = 0;
    require(static_cast<bool>(std::cin >> count) && count == 5680,
            "incomplete system inventory");
    model.systems.reserve(5680);
    for (int i = 0; i < count; ++i) {
        int dimension = 0;
        require(static_cast<bool>(std::cin >> low >> high >> dimension),
                "missing system");
        require(dimension == 1 || dimension == 2, "invalid normal dimension");
        System system;
        system.off = Mask{low} | (Mask{high} << 64);
        require((system.off & ~live) == 0, "system outside live roots");
        for (int j = 0; j < dimension; ++j) {
            Row row{};
            for (int& entry : row) {
                require(static_cast<bool>(std::cin >> entry), "missing normal");
                require(entry >= -64 && entry <= 64, "normal out of range");
            }
            system.normals.push_back(row);
        }
        // Any partner contributes at most 20 live lines. A residual set
        // larger than 36 + 4 cannot be repaired. The independent flat
        // enumeration verifies the 20-line premise before scanning.
        if (weight(system.off & ~model.first) <= 20 + 36 + 4)
            model.systems.push_back(system);
    }
    char extra = 0;
    require(!(std::cin >> extra), "trailing model input");
    for (int c = 0; c < 512; ++c)
        for (int i = 0; i < 112; ++i)
            if (__builtin_parity(static_cast<unsigned>(model.labels[i] & c)))
                model.characters[c] |= Mask{1} << i;
    return model;
}

int binary_rank(Mask mask, const Model& model) {
    assert((mask & ~live) == 0);
    std::array<int, 9> basis{};
    int rank = 0;
    for (int i = 0; i < 112; ++i) {
        if (((mask >> i) & 1) == 0) continue;
        int value = model.labels[i];
        for (int bit = 8; bit >= 0; --bit) {
            if (((value >> bit) & 1) == 0) continue;
            if (basis[bit]) value ^= basis[bit];
            else {
                basis[bit] = value;
                ++rank;
                break;
            }
        }
    }
    return rank;
}

void deduplicate(std::vector<Mask>& masks) {
    std::sort(masks.begin(), masks.end());
    masks.erase(std::unique(masks.begin(), masks.end()), masks.end());
}

std::vector<Mask> cuts(Mask residual, const Model& model) {
    const int rank = binary_rank(residual, model);
    if (rank <= 7) return {0};
    std::vector<Mask> small;
    small.reserve(511);
    for (int c = 1; c < 512; ++c) {
        const Mask cut = residual & model.characters[c];
        if (weight(cut) > 0 && weight(cut) <= 4) small.push_back(cut);
    }
    deduplicate(small);
    if (rank == 8) return small;
    require(rank == 9, "invalid residual rank");
    std::vector<Mask> result;
    result.reserve(511 * 511);
    for (std::size_t i = 0; i < small.size(); ++i)
        for (std::size_t j = 0; j < i; ++j)
            if (weight(small[i] | small[j]) <= 4)
                result.push_back(small[i] | small[j]);
    deduplicate(result);
    return result;
}

Integer gcd_integer(Integer a, Integer b) {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    // Euclidean division halves the larger argument within two steps.
    for (int iteration = 0; iteration < 4096; ++iteration) {
        if (b == 0) return a;
        Integer remainder = a % b;
        a = b;
        b = remainder;
    }
    throw std::runtime_error("integer gcd capacity exhausted");
}

std::vector<Row> real_basis(const std::vector<Row>& rows) {
    require(rows.size() <= 256, "normal-row capacity exhausted");
    std::array<std::array<Integer, 8>, 8> basis{};
    std::vector<Row> independent;
    for (const Row& original : rows) {
        std::array<Integer, 8> row{};
        std::copy(original.begin(), original.end(), row.begin());
        for (int pivot = 0; pivot < 8; ++pivot) {
            if (row[pivot] == 0) continue;
            if (basis[pivot][pivot] == 0) {
                basis[pivot] = row;
                independent.push_back(original);
                break;
            }
            const Integer a = basis[pivot][pivot], b = row[pivot];
            Integer divisor = 0;
            for (int k = pivot; k < 8; ++k) {
                row[k] = a * row[k] - b * basis[pivot][k];
                divisor = gcd_integer(divisor, row[k]);
            }
            if (divisor != 0)
                for (int k = pivot; k < 8; ++k) row[k] /= divisor;
        }
        if (independent.size() == 8) break;
    }
    return independent;
}

struct Flat {
    Mask mask;
    std::array<int, 3> annihilator;
};

std::vector<Flat> all_flats(const Model& model, std::map<int, int>& histogram) {
    std::vector<Flat> flats;
    flats.reserve(flat_limit);
    for (int a = 0; a < 9; ++a)
        for (int b = a + 1; b < 9; ++b)
            for (int c = b + 1; c < 9; ++c) {
                std::vector<std::pair<int, int>> free;
                const std::array<int, 3> pivots{a, b, c};
                for (int i = 0; i < 3; ++i)
                    for (int j = pivots[i] + 1; j < 9; ++j)
                        if (j != a && j != b && j != c) free.emplace_back(i, j);
                require(free.size() <= 18, "RREF free-entry capacity exhausted");
                const unsigned limit = 1U << free.size();
                for (unsigned pattern = 0; pattern < limit; ++pattern) {
                    std::array<int, 3> ann{1 << a, 1 << b, 1 << c};
                    for (std::size_t k = 0; k < free.size(); ++k)
                        if ((pattern >> k) & 1U)
                            ann[free[k].first] |= 1 << free[k].second;
                    const Mask mask = live & ~(model.characters[ann[0]] |
                        model.characters[ann[1]] | model.characters[ann[2]]);
                    require(flats.size() < flat_limit, "flat capacity exhausted");
                    flats.push_back({mask, ann});
                    ++histogram[weight(mask)];
                }
            }
    require(flats.size() == flat_limit, "incomplete six-flat enumeration");
    require(histogram.rbegin()->first == 20, "six-flat cap changed");
    std::sort(flats.begin(), flats.end(), [](const Flat& a, const Flat& b) {
        if (a.mask != b.mask) return a.mask < b.mask;
        return a.annihilator < b.annihilator;
    });
    flats.erase(std::unique(flats.begin(), flats.end(),
        [](const Flat& a, const Flat& b) { return a.mask == b.mask; }), flats.end());
    return flats;
}

void independently_check_flats(const Model& model, const std::vector<Flat>& flats,
                               const std::map<int, int>& expected_histogram) {
    // Different enumeration: choose the successive least coset representatives
    // of each 3-space, not pivot columns and free RREF entries.
    std::vector<Mask> masks;
    masks.reserve(flat_limit);
    std::map<int, int> histogram;
    for (int a = 1; a < 512; ++a)
        for (int b = a + 1; b < 512; ++b) {
            if (b >= (a ^ b)) continue;
            for (int c = b + 1; c < 512; ++c) {
                if (c >= (c ^ a) || c >= (c ^ b) || c >= (c ^ a ^ b)) continue;
                const Mask mask = live & ~(model.characters[a] |
                    model.characters[b] | model.characters[c]);
                require(masks.size() < flat_limit, "independent flat capacity exhausted");
                masks.push_back(mask);
                ++histogram[weight(mask)];
            }
        }
    require(masks.size() == flat_limit, "incomplete independent flat enumeration");
    require(histogram == expected_histogram, "independent flat histogram differs");
    deduplicate(masks);
    require(masks.size() == flats.size(), "independent mask count differs");
    for (std::size_t i = 0; i < masks.size(); ++i)
        require(masks[i] == flats[i].mask, "independent partner mask differs");
}

struct Qualified {
    std::size_t index;
    std::vector<Mask> cuts;
};

std::vector<Qualified> qualify(const Model& model, Mask cover) {
    std::vector<Qualified> result;
    result.reserve(128);
    for (std::size_t i = 0; i < model.systems.size(); ++i) {
        const Mask residual = model.systems[i].off & ~cover;
        // The independently checked seven-flat cap is 36, and |P| <= 4.
        if (weight(residual) > 40) continue;
        auto options = cuts(residual, model);
        if (options.empty()) continue;
        require(result.size() < 128, "qualified-system capacity exhausted");
        result.push_back({i, std::move(options)});
    }
    return result;
}

std::vector<Mask> common_states(const std::vector<Qualified>& qualified) {
    std::vector<Mask> states{0};
    states.reserve(state_limit);
    for (const auto& item : qualified) {
        const std::size_t old_size = states.size();
        std::vector<Mask> additions;
        additions.reserve(state_limit);
        for (std::size_t i = 0; i < old_size; ++i)
            for (Mask cut : item.cuts) {
                const Mask next = states[i] | cut;
                if (weight(next) > 4) continue;
                if (additions.size() == state_limit) deduplicate(additions);
                require(additions.size() < state_limit, "union capacity exhausted");
                additions.push_back(next);
            }
        states.insert(states.end(), additions.begin(), additions.end());
        deduplicate(states);
        require(states.size() <= state_limit, "state capacity exhausted");
    }
    return states;
}

std::vector<Row> admitted_rows(const Model& model,
                              const std::vector<Qualified>& qualified, Mask state) {
    std::vector<Row> rows;
    rows.reserve(256);
    for (const auto& item : qualified) {
        const bool admitted = std::any_of(item.cuts.begin(), item.cuts.end(),
            [state](Mask cut) { return (cut & ~state) == 0; });
        if (admitted) {
            const auto& normals = model.systems[item.index].normals;
            rows.insert(rows.end(), normals.begin(), normals.end());
        }
    }
    require(rows.size() <= 256, "admitted-row capacity exhausted");
    return rows;
}

struct RankCheck {
    std::array<int, 3> annihilator;
    Mask deletion;
    std::vector<Row> rows;
    int rank;
};

struct Result {
    std::vector<RankCheck> checks;
    int maximum = 0;
    std::uint64_t states = 0, ranks = 0, planes = 0;
    std::size_t maximum_qualified = 0, maximum_states = 0;
    Flat witness{};
    Mask deletion = 0;
    std::vector<Row> witness_rows;
};

Result scan(const Model& model, const std::vector<Flat>& flats) {
    Result result;
    for (const Flat& flat : flats) {
        const auto qualified = qualify(model, model.first | flat.mask);
        const auto states = common_states(qualified);
        result.maximum_qualified = std::max(result.maximum_qualified, qualified.size());
        result.maximum_states = std::max(result.maximum_states, states.size());
        for (const auto& item : qualified)
            if (model.systems[item.index].normals.size() == 2) ++result.planes;
        result.states += states.size();
        for (Mask state : states) {
            const auto rows = admitted_rows(model, qualified, state);
            // A list of at most M vectors cannot exceed the current maximum M.
            if (rows.size() <= static_cast<std::size_t>(result.maximum)) continue;
            ++result.ranks;
            const auto basis = real_basis(rows);
            require(result.checks.size() < 4096, "rank-check capacity exhausted");
            result.checks.push_back({flat.annihilator, state, rows,
                                     static_cast<int>(basis.size())});
            if (basis.size() > static_cast<std::size_t>(result.maximum)) {
                result.maximum = static_cast<int>(basis.size());
                result.witness = flat;
                result.deletion = state;
                result.witness_rows = basis;
            }
        }
    }
    return result;
}

void print_case(const Model& model, const std::array<int, 3>& annihilator,
                Mask deletion, const std::vector<Row>& rows, int rank) {
    std::cout << "{\"V2_annihilator\":[";
    for (int j = 0; j < 3; ++j) {
        if (j) std::cout << ',';
        std::cout << annihilator[j];
    }
    std::cout << "],\"deleted_labels\":[";
    bool first = true;
    for (int i = 0; i < 112; ++i) {
        if (((deletion >> i) & 1) == 0) continue;
        if (!first) std::cout << ',';
        first = false;
        std::cout << model.labels[i];
    }
    std::cout << "],\"directions\":[";
    for (std::size_t i = 0; i < rows.size(); ++i) {
        if (i) std::cout << ',';
        std::cout << '[';
        for (int j = 0; j < 8; ++j) {
            if (j) std::cout << ',';
            std::cout << rows[i][j];
        }
        std::cout << ']';
    }
    std::cout << "],\"rank\":" << rank << '}';
}

void print_result(const Model& model, const std::vector<Flat>& flats,
                  const std::map<int, int>& histogram, const Result& result) {
    std::cout << "{\"all_flats\":" << flat_limit
              << ",\"distinct_live_masks\":" << flats.size()
              << ",\"maximum_common_span\":" << result.maximum
              << ",\"states_checked\":" << result.states
              << ",\"exact_rank_checks\":" << result.ranks
              << ",\"qualified_plane_occurrences\":" << result.planes
              << ",\"maximum_qualified_systems\":" << result.maximum_qualified
              << ",\"maximum_states_per_pair\":" << result.maximum_states
              << ",\"six_flat_size_histogram\":{";
    bool first = true;
    for (const auto& [size, count] : histogram) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << '\"' << size << "\":" << count;
    }
    std::cout << "},\"witness\":";
    print_case(model, result.witness.annihilator, result.deletion,
               result.witness_rows, result.maximum);
    std::cout << ",\"rank_checks\":[";
    for (std::size_t i = 0; i < result.checks.size(); ++i) {
        if (i) std::cout << ',';
        const auto& check = result.checks[i];
        print_case(model, check.annihilator, check.deletion, check.rows, check.rank);
    }
    std::cout << "]}\n";
    require(static_cast<bool>(std::cout), "output failure");
}

void self_test() {
    Model model;
    for (int i = 0; i < 112; ++i) model.labels[i] = 1 << (i % 9);
    for (int c = 0; c < 512; ++c)
        for (int i = 0; i < 112; ++i)
            if (__builtin_parity(static_cast<unsigned>(model.labels[i] & c)))
                model.characters[c] |= Mask{1} << i;
    require(binary_rank(511, model) == 9, "rank-nine control failed");
    const auto options = cuts(511, model);
    require(!options.empty(), "rank-nine deletion control failed");
    for (Mask cut : options)
        require(weight(cut) >= 2 && binary_rank(Mask{511} & ~cut, model) <= 7,
                "unsound deletion control");
    require(std::find(options.begin(), options.end(), Mask{3}) != options.end(),
            "missing two-character cut");
    const auto one = cuts(255, model);
    require(std::find(one.begin(), one.end(), Mask{1}) != one.end(),
            "missing one-character cut");
    require(cuts(127, model) == std::vector<Mask>{0}, "rank-seven control failed");
    require(real_basis({Row{1, 2, 3, 4, 0, 0, 0, 0},
                        Row{2, 4, 6, 8, 0, 0, 0, 0}}).size() == 1,
            "dependent rational-rank control failed");
    require(real_basis({Row{1, 2, 0, 0, 0, 0, 0, 0},
                        Row{2, 1, 0, 0, 0, 0, 0, 0}}).size() == 2,
            "independent rational-rank control failed");
    const std::vector<Qualified> q{{0, {Mask{3}}}, {1, {Mask{12}}}, {2, {Mask{48}}}};
    const auto states = common_states(q);
    require(std::find(states.begin(), states.end(), Mask{15}) != states.end(),
            "shared four-cut missing");
    require(std::find(states.begin(), states.end(), Mask{63}) == states.end(),
            "separate cuts mistaken for shared cut");
    std::cout << "PASS_SCAN_CONTROLS\n";
}

int main(int argc, char** argv) {
    try {
        require(__builtin_cpu_supports("popcnt"), "CPU POPCNT support is required");
        if (argc == 2 && std::string(argv[1]) == "--self-test") {
            self_test();
            return 0;
        }
        require(argc == 1, "unexpected scanner argument");
        const Model model = read_model();
        std::map<int, int> histogram;
        const auto flats = all_flats(model, histogram);
        independently_check_flats(model, flats, histogram);
        const Result result = scan(model, flats);
        print_result(model, flats, histogram, result);
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FAIL: " << error.what() << '\n';
        return 2;
    }
}
