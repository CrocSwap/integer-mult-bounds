// Independent bit-packed F3 BFS; Ross Richardson / OpenAI Codex, Apache-2.0.
// Each coefficient occupies two bits. No Python tables or search data are read.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using Key = std::uint64_t;

int coefficient(Key key, int n, int row, int column) {
    return (key >> (2 * (row * n + column))) & 3;
}

Key change(Key key, int n, int target, int source, int sign) {
    Key result = key;
    for (int column = 0; column < n; ++column) {
        int a = coefficient(key, n, target, column);
        int b = coefficient(key, n, source, column);
        int value = target == source ? (3 - a) % 3 : (a + sign * b + 3) % 3;
        int shift = 2 * (target * n + column);
        result = (result & ~(Key(3) << shift)) | (Key(value) << shift);
    }
    return result;
}

int main(int argc, char **argv) {
    try {
        if (argc != 3) throw std::runtime_error("usage: independent DIMENSION OUTPUT");
        int n = std::stoi(argv[1]);
        if (n != 2 && n != 3 && n != 5) throw std::runtime_error("dimension");
        Key identity = 0;
        for (int i = 0; i < n; ++i) identity |= Key(1) << (2 * (i * n + i));
        std::unordered_map<Key, unsigned char> distance;
        distance.reserve(600000);
        distance.emplace(identity, 0);
        std::vector<Key> queue{identity};
        for (std::size_t cursor = 0; cursor < queue.size(); ++cursor) {
            Key state = queue[cursor];
            int depth = distance.at(state);
            if (depth == 4) continue;
            // Deliberately use a different generator order from the Python BFS.
            for (int s = n - 1; s >= 0; --s) {
                for (int t = n - 1; t >= 0; --t) {
                    for (int sign : {1, -1}) {
                        if (s == t && sign == 1) continue;
                        Key next = change(state, n, t, s, sign);
                        if (distance.emplace(next, depth + 1).second) queue.push_back(next);
                    }
                }
            }
        }
        std::vector<std::pair<Key, unsigned char>> ordered;
        ordered.reserve(distance.size());
        for (const auto &entry : distance) {
            Key ternary = 0, place = 1;
            for (int r = 0; r < n; ++r) for (int c = 0; c < n; ++c) {
                ternary += place * coefficient(entry.first, n, r, c);
                place *= 3;
            }
            ordered.emplace_back(ternary, entry.second);
        }
        std::sort(ordered.begin(), ordered.end());
        std::ofstream output(argv[2], std::ios::binary);
        if (!output) throw std::runtime_error("output open");
        for (const auto &entry : ordered) {
            for (int i = 0; i < 8; ++i) output.put(char((entry.first >> (8 * i)) & 255));
            output.put(char(entry.second));
        }
        output.close();
        if (!output) throw std::runtime_error("output write");
        std::cout << "PASS_INDEPENDENT_BALL n=" << n << " states=" << ordered.size() << '\n';
        return 0;
    } catch (const std::exception &error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
