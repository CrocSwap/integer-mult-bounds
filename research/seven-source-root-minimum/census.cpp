// Exact matching/colour census, independent of census.py's word and set generators.
// Mason Hale, with OpenAI Codex assistance. Apache-2.0.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <map>
#include <string>
#include <vector>

using Bits = __uint128_t;  // GCC and Clang; all shifts are in [0,127].
int popcount(Bits x) {
    return __builtin_popcountll(static_cast<uint64_t>(x)) +
           __builtin_popcountll(static_cast<uint64_t>(x >> 64));
}
struct Group {
    uint64_t partitions = 0;
    std::map<int, uint64_t> histogram;
};
struct Partition { Bits required; std::string key; };
std::vector<Partition> partitions;
std::map<std::string, Group> groups;
std::array<int, 7> colour;
std::array<int, 14> word;
std::map<int, uint64_t> differences;
uint64_t words = 0;

void colours(int t, int used) {
    if (t == 7) {
        if (used < 3) return;
        std::vector<int> sizes(used, 0);
        for (int c : colour) ++sizes[c];
        std::sort(sizes.rbegin(), sizes.rend());
        std::string key;
        for (int s : sizes) key += (key.empty() ? "" : "+") + std::to_string(s);
        Bits required = 0;
        for (int mask = 1; mask < 128; ++mask) {
            unsigned hit = 0;
            for (int j = 0; j < 7; ++j)
                if ((mask >> j) & 1) hit |= 1u << colour[j];
            if (__builtin_popcount(hit) >= 3) required |= Bits(1) << mask;
        }
        partitions.push_back({required, key});
        ++groups[key].partitions;
        return;
    }
    for (int c = 0; c <= used && c < 4; ++c) {
        colour[t] = c;
        colours(t + 1, used + (c == used));
    }
}

void inspect() {
    ++words;
    std::array<int, 15> prefixes{};
    for (int i = 0; i < 14; ++i) prefixes[i + 1] = prefixes[i] ^ (1 << word[i]);
    Bits covered = 1;
    for (int i = 0; i < 15; ++i)
        for (int j = 0; j < i; ++j) covered |= Bits(1) << (prefixes[i] ^ prefixes[j]);
    ++differences[popcount(covered)];
    for (const auto &p : partitions)
        ++groups[p.key].histogram[popcount(p.required & ~covered)];
}

void match(int label) {
    int first = 0;
    while (first < 14 && word[first] >= 0) ++first;
    if (first == 14) { inspect(); return; }
    word[first] = label;
    for (int second = first + 1; second < 14; ++second) {
        if (word[second] >= 0) continue;
        word[second] = label;
        match(label + 1);
        word[second] = -1;
    }
    word[first] = -1;
}

void print_histogram(const std::map<int, uint64_t> &h) {
    std::cout << "{";
    bool first = true;
    for (auto [key, count] : h) {
        if (!first) std::cout << ",";
        first = false;
        std::cout << '"' << key << "\":" << count;
    }
    std::cout << "}";
}

int main() {
    colours(0, 0);
    word.fill(-1);
    match(0);
    std::cout << "{\"sources\":7,\"words\":" << words
              << ",\"partitions\":" << partitions.size()
              << ",\"cases\":" << words * partitions.size()
              << ",\"difference_histogram\":";
    print_histogram(differences);
    std::cout << ",\"groups\":{";
    bool first = true;
    for (auto &[key, group] : groups) {
        if (!first) std::cout << ",";
        first = false;
        std::cout << '"' << key << "\":{\"partitions\":" << group.partitions
                  << ",\"missing_histogram\":";
        print_histogram(group.histogram);
        std::cout << "}";
    }
    std::cout << "}}\n";
}
