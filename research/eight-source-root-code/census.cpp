// Independent fixed-domain census: RREF codes and contiguous interval parities.
// Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <map>
#include <stdexcept>
#include <utility>
#include <vector>

using Bits = std::array<std::uint64_t, 4>;
using Code = std::array<int, 16>;

void put(Bits& values, int mask) {
    values[mask / 64] |= std::uint64_t(1) << (mask % 64);
}
void remove(Bits& values, int mask) {
    values[mask / 64] &= ~(std::uint64_t(1) << (mask % 64));
}
int size(const Bits& values) {
    int result = 0;
    for (auto value : values) result += __builtin_popcountll(value);
    return result;
}

std::vector<Code> inventory() {
    std::vector<Code> codes;
    // Every dimension-three subspace of seven coordinates has one RREF basis.
    for (int a = 0; a < 7; ++a) for (int b = a + 1; b < 7; ++b)
        for (int c = b + 1; c < 7; ++c) {
            const std::array<int, 3> pivots{a, b, c};
            std::vector<std::pair<int, int>> free;
            for (int row = 0; row < 3; ++row)
                for (int col = pivots[row] + 1; col < 7; ++col)
                    if (col != a && col != b && col != c) free.emplace_back(row, col);
            for (unsigned assignment = 0; assignment < (1u << free.size()); ++assignment) {
                std::array<int, 3> rows{1 << a, 1 << b, 1 << c};
                for (unsigned i = 0; i < free.size(); ++i)
                    if ((assignment >> i) & 1u) rows[free[i].first] |= 1 << free[i].second;
                Code code{};
                for (int combination = 0; combination < 16; ++combination) {
                    int word = (combination & 1) ? 255 : 0;
                    for (int row = 0; row < 3; ++row)
                        if ((combination >> (row + 1)) & 1) word ^= rows[row] << 1;
                    code[combination] = word;
                }
                std::sort(code.begin(), code.end());
                codes.push_back(code);
            }
        }
    std::sort(codes.begin(), codes.end());
    if (codes.size() != 11811 || std::adjacent_find(codes.begin(), codes.end()) != codes.end())
        throw std::runtime_error("wrong code inventory");
    return codes;
}

Bits mandatory(const Code& code) {
    Bits required{~std::uint64_t(0), ~std::uint64_t(0), ~std::uint64_t(0), ~std::uint64_t(0)};
    for (int h : code) if (h != 255) {
        int subset = h;
        while (true) {
            remove(required, subset);
            if (subset == 0) break;
            subset = (subset - 1) & h;
        }
    }
    return required;
}

template<class T> void json_histogram(const std::map<int, T>& values) {
    std::cout << '{';
    bool first = true;
    for (auto [key, value] : values) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << '"' << key << "\":" << value;
    }
    std::cout << '}';
}

int main() {
    const auto codes = inventory();
    std::vector<Bits> required;
    std::map<int, std::uint64_t> mandatory_histogram, difference_histogram;
    for (const auto& code : codes) {
        required.push_back(mandatory(code));
        ++mandatory_histogram[size(required.back())];
    }
    std::array<int, 8> order{0, 1, 2, 3, 4, 5, 6, 7};
    std::uint64_t words = 0, survivors = 0;
    do {
        std::array<int, 16> word{};
        for (int i = 0; i < 8; ++i) { word[i] = i; word[i + 8] = order[i]; }
        Bits differences{};
        put(differences, 0);
        for (int left = 0; left < 16; ++left) {
            int parity = 0;
            for (int right = left; right < 16; ++right) {
                parity ^= 1 << word[right];
                put(differences, parity);
            }
        }
        ++difference_histogram[size(differences)];
        for (const auto& masks : required) {
            bool passes = true;
            for (int block = 0; block < 4; ++block)
                if ((masks[block] & differences[block]) != masks[block]) { passes = false; break; }
            survivors += passes;
        }
        ++words;
    } while (std::next_permutation(order.begin(), order.end()));
    if (words != 40320) throw std::runtime_error("wrong permutation inventory");
    std::cout << "{\"summary\":{\"n\":8,\"roots\":4,\"source_orders\":" << words
              << ",\"codes\":" << codes.size() << ",\"cases\":" << words * codes.size()
              << ",\"mandatory_survivors\":" << survivors
              << ",\"max_difference_size\":" << difference_histogram.rbegin()->first
              << ",\"difference_histogram\":";
    json_histogram(difference_histogram);
    std::cout << ",\"mandatory_size_histogram\":";
    json_histogram(mandatory_histogram);
    std::cout << "},\"code_inventory\":[";
    bool first = true;
    for (const auto& code : codes) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << '[';
        for (int i = 0; i < 16; ++i) { if (i) std::cout << ','; std::cout << code[i]; }
        std::cout << ']';
    }
    std::cout << "]}\n";
    return survivors == 0 ? 0 : 1;
}
