// Exact GL(2,F2) meet-in-the-middle discovery on an explicit balanced graph.
// Every output, including all auxiliary outputs, must be a distinct input.
// Prepared for huxint with OpenAI Codex assistance. Apache-2.0.
#include <algorithm>
#include <array>
#include <cstdint>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using Rows = std::array<uint16_t, 10>;
struct Key {
    uint64_t low = 0, high = 0;
    bool operator==(const Key& o) const { return low == o.low && high == o.high; }
};
struct KeyHash {
    size_t operator()(const Key& k) const {
        uint64_t x = k.low ^ (k.high + 0x9e3779b97f4a7c15ULL + (k.low << 6) + (k.low >> 2));
        x ^= x >> 30; x *= 0xbf58476d1ce4e5b9ULL;
        x ^= x >> 27; x *= 0x94d049bb133111ebULL;
        return x ^ (x >> 31);
    }
};
constexpr int GL[6][2] = {{1,2},{2,1},{1,3},{3,2},{2,3},{3,1}};
constexpr int INVERSE[6] = {0,1,2,3,5,4};

Rows columns(const Rows& rows, int width) {
    Rows result{};
    for (int i = 0; i < width; ++i)
        for (int j = 0; j < width; ++j)
            result[j] |= ((rows[i] >> j) & 1) << i;
    return result;
}

Key key(const Rows& rows, int width, const std::vector<int>& fixed) {
    const auto cols = columns(rows, width);
    std::array<bool,10> used{};
    Rows ordered{};
    int n = 0;
    for (int j : fixed) { ordered[n++] = cols[j]; used[j] = true; }
    for (int j = 0; j < width; ++j) if (!used[j]) ordered[n++] = cols[j];
    std::sort(ordered.begin() + fixed.size(), ordered.begin() + width);
    Key k;
    for (int j = 0; j < width; ++j) {
        k.high = (k.high << width) | (k.low >> (64 - width));
        k.low = (k.low << width) | ordered[j];
    }
    return k;
}

Rows apply(Rows rows, int a, int b, int choice) {
    const uint16_t values[4] = {0, rows[a], rows[b], uint16_t(rows[a] ^ rows[b])};
    rows[a] = values[GL[choice][0]];
    rows[b] = values[GL[choice][1]];
    return rows;
}

uint64_t packed_permutation(const Rows& values, int width) {
    uint64_t code = 0;
    for (int i = 0; i < width; ++i) code |= uint64_t(values[i]) << (4*i);
    return code;
}

void all_permutations(int id, int width, const std::vector<std::pair<int,int>>& pairs) {
    const int gates = pairs.size(), split = gates / 2;
    Rows tokens{};
    for (int i = 0; i < width; ++i) tokens[i] = i;
    std::unordered_set<uint64_t> routes{packed_permutation(tokens,width)};
    for (auto [a,b] : pairs) {
        auto next = routes;
        for (auto code : routes) {
            const auto x = (code >> (4*a)) & 15, y = (code >> (4*b)) & 15;
            next.insert(code ^ ((x ^ y) << (4*a)) ^ ((x ^ y) << (4*b)));
        }
        routes.swap(next);
    }
    int factorial = 1; for (int i = 2; i <= width; ++i) factorial *= i;
    if (routes.size() == size_t(factorial)) {
        std::cout << "{\"id\":" << id << ",\"W\":" << width
                  << ",\"routing_permutations\":" << routes.size()
                  << ",\"all_permutations_routable\":true,\"nonroutable_scalar_permutation\":false}" << std::endl;
        return;
    }
    struct Prefix { Rows cols; uint32_t word; };
    std::unordered_map<Key,std::vector<Prefix>,KeyHash> prefixes;
    prefixes.reserve(300000);
    Rows identity{};
    for (int i = 0; i < width; ++i) identity[i] = 1 << i;
    uint64_t prefix_count = 0, suffix_count = 0, matches = 0;
    std::function<void(int,Rows,uint32_t)> forward = [&](int depth, Rows rows, uint32_t word) {
        if (depth == split) {
            prefixes[key(rows,width,{})].push_back({columns(rows,width),word});
            ++prefix_count; return;
        }
        auto [a,b] = pairs[depth];
        for (int k = 0; k < 6; ++k)
            forward(depth+1,apply(rows,a,b,k),word | (uint32_t(k) << (3*depth)));
    };
    forward(0,identity,0);
    bool found = false;
    uint32_t chosen_prefix = 0, chosen_suffix = 0;
    Rows chosen_rho{};
    std::unordered_set<uint64_t> scalar_permutations;
    std::function<void(int,Rows,uint32_t)> backward = [&](int depth, Rows rows, uint32_t word) {
        if (found) return;
        if (depth == gates-split) {
            ++suffix_count;
            auto it = prefixes.find(key(rows,width,{}));
            if (it == prefixes.end()) return;
            auto cols = columns(rows,width);
            for (const auto& prefix : it->second) {
                ++matches;
                Rows output_tokens{}, rho{};
                for (int in = 0; in < width; ++in) {
                    int out = 0;
                    while (out < width && cols[out] != prefix.cols[in]) ++out;
                    if (out == width) throw std::runtime_error("Bad column-key match");
                    output_tokens[out] = in; rho[in] = out;
                }
                auto code = packed_permutation(output_tokens,width);
                scalar_permutations.insert(code);
                if (!routes.count(code)) {
                    found = true; chosen_prefix = prefix.word; chosen_suffix = word;
                    chosen_rho = rho; return;
                }
            }
            return;
        }
        auto [a,b] = pairs[gates-1-depth];
        for (int k = 0; k < 6 && !found; ++k)
            backward(depth+1,apply(rows,a,b,k),word | (uint32_t(k) << (3*depth)));
    };
    backward(0,identity,0);
    std::cout << "{\"id\":" << id << ",\"W\":" << width
              << ",\"routing_permutations\":" << routes.size()
              << ",\"prefix_assignments\":" << prefix_count
              << ",\"prefix_keys\":" << prefixes.size()
              << ",\"suffix_assignments\":" << suffix_count
              << ",\"matching_full_words\":" << matches
              << ",\"scalar_permutations\":" << scalar_permutations.size()
              << ",\"nonroutable_scalar_permutation\":" << (found ? "true" : "false");
    if (found) {
        std::cout << ",\"choices\":[";
        std::vector<int> choices;
        for (int i = 0; i < split; ++i) choices.push_back((chosen_prefix >> (3*i)) & 7);
        for (int i = gates-split-1; i >= 0; --i) choices.push_back(INVERSE[(chosen_suffix >> (3*i)) & 7]);
        Rows transfer = identity;
        for (int i = 0; i < gates; ++i) {
            if (i) std::cout << ',';
            std::cout << choices[i];
            transfer = apply(transfer,pairs[i].first,pairs[i].second,choices[i]);
        }
        std::cout << "],\"rho\":[";
        for (int i = 0; i < width; ++i) {
            if (transfer[chosen_rho[i]] != (1 << i)) throw std::runtime_error("Wrong recovered permutation");
            if (i) std::cout << ',';
            std::cout << chosen_rho[i];
        }
        std::cout << ']';
    }
    std::cout << "}" << std::endl;
}

int main(int argc, char** argv) {
    const bool scan_all = argc == 2 && std::string(argv[1]) == "--all-permutations";
    if (argc != 1 && !scan_all) throw std::runtime_error("Unknown discovery mode");
    int id, width, gates, prescribed;
    while (std::cin >> id >> width >> gates >> prescribed) {
        if (width < 2 || width > 10 || gates < 0 || gates > 16 || prescribed > width)
            throw std::runtime_error("Input outside explicit discovery budget");
        std::vector<std::pair<int,int>> pairs(gates);
        for (auto& p : pairs) {
            std::cin >> p.first >> p.second;
            if (p.first < 0 || p.second < 0 || p.first >= width || p.second >= width || p.first == p.second)
                throw std::runtime_error("Invalid gate pair");
        }
        std::vector<int> input_fixed, output_fixed;
        for (int i = 0, a, b; i < prescribed; ++i) {
            std::cin >> a >> b; input_fixed.push_back(a); output_fixed.push_back(b);
        }
        if (scan_all) { all_permutations(id,width,pairs); continue; }
        const int split = gates / 2;
        Rows identity{};
        for (int j = 0; j < width; ++j) identity[j] = 1 << j;
        std::unordered_map<Key,uint32_t,KeyHash> prefixes;
        prefixes.reserve(300000);
        uint64_t prefix_count = 0, suffix_count = 0;
        std::function<void(int,Rows,uint32_t)> forward = [&](int depth, Rows rows, uint32_t word) {
            if (depth == split) {
                prefixes.emplace(key(rows, width, input_fixed), word); ++prefix_count; return;
            }
            auto [a,b] = pairs[depth];
            for (int k = 0; k < 6; ++k)
                forward(depth + 1, apply(rows,a,b,k), word | (uint32_t(k) << (3*depth)));
        };
        forward(0,identity,0);
        bool found = false;
        uint32_t chosen_prefix = 0, chosen_inverse_suffix = 0;
        Rows matched_inverse{};
        std::function<void(int,Rows,uint32_t)> backward = [&](int depth, Rows rows, uint32_t word) {
            if (found) return;
            if (depth == gates - split) {
                ++suffix_count;
                auto it = prefixes.find(key(rows, width, output_fixed));
                if (it != prefixes.end()) {
                    found = true; chosen_prefix = it->second;
                    chosen_inverse_suffix = word; matched_inverse = rows;
                }
                return;
            }
            auto [a,b] = pairs[gates - 1 - depth];
            for (int k = 0; k < 6 && !found; ++k)
                backward(depth + 1, apply(rows,a,b,k), word | (uint32_t(k) << (3*depth)));
        };
        backward(0,identity,0);
        std::cout << "{\"id\":" << id << ",\"W\":" << width
                  << ",\"prefix_assignments\":" << prefix_count
                  << ",\"prefix_keys\":" << prefixes.size()
                  << ",\"suffix_assignments\":" << suffix_count
                  << ",\"exists\":" << (found ? "true" : "false");
        if (found) {
            std::vector<int> choices;
            for (int i = 0; i < split; ++i) choices.push_back((chosen_prefix >> (3*i)) & 7);
            for (int i = gates-split-1; i >= 0; --i)
                choices.push_back(INVERSE[(chosen_inverse_suffix >> (3*i)) & 7]);
            Rows transfer = identity;
            for (int i = 0; i < gates; ++i)
                transfer = apply(transfer,pairs[i].first,pairs[i].second,choices[i]);
            std::array<int,10> rho{};
            std::array<bool,10> occupied{};
            for (int out = 0; out < width; ++out) {
                const int row = transfer[out];
                if (!row || (row & (row-1))) throw std::runtime_error("Nonpermutation recovery");
                int in = 0; while ((1 << in) != row) ++in;
                if (occupied[in]) throw std::runtime_error("Repeated permutation input");
                occupied[in] = true; rho[in] = out;
            }
            for (int i = 0; i < prescribed; ++i)
                if (rho[input_fixed[i]] != output_fixed[i]) throw std::runtime_error("Wrong fixed terminal");
            std::cout << ",\"choices\":[";
            for (int i = 0; i < gates; ++i) { if (i) std::cout << ','; std::cout << choices[i]; }
            std::cout << "],\"rho\":[";
            for (int i = 0; i < width; ++i) { if (i) std::cout << ','; std::cout << rho[i]; }
            std::cout << ']';
        }
        std::cout << "}" << std::endl;
    }
}
