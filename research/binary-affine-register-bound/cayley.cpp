// Complete affine Cayley BFS, independent of the Python rank/factorization code.
// Gareth Davidson, with substantial OpenAI Codex assistance. Apache-2.0.
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

int main(int argc, char** argv) {
  try {
    if (argc != 3) throw std::runtime_error("usage: cayley DIM OUTPUT");
    unsigned d = std::stoul(argv[1]);
    if (d < 1 || d > 4) throw std::runtime_error("dimension must be 1..4");
    const unsigned width = d + 1, addresses = 1u << d;
    const unsigned size = 1u << (d * width), rowmask = (1u << width) - 1;
    std::vector<std::pair<unsigned, unsigned>> gates;
    for (unsigned u = 1; u < addresses; ++u)
      for (unsigned f = 1; f <= rowmask; ++f)
        if (__builtin_parity(u & f) == 0) gates.emplace_back(u, f);
    // A left affine transvection XORs the form f(current(x)) into rows in u.
    unsigned changes[16][32] = {};
    for (unsigned u = 1; u < addresses; ++u)
      for (unsigned q = 0; q <= rowmask; ++q)
        for (unsigned i = 0; i < d; ++i)
          if ((u >> i) & 1) changes[u][q] ^= q << (width * i);
    unsigned identity = 0;
    for (unsigned i = 0; i < d; ++i) identity |= (1u << i) << (width * i);
    std::vector<uint8_t> distance(size, 255);
    std::vector<unsigned> queue;
    queue.reserve(size);
    distance[identity] = 0;
    queue.push_back(identity);
    uint64_t edges = 0;
    for (size_t at = 0; at < queue.size(); ++at) {
      unsigned state = queue[at], rows[5], forms[32] = {};
      for (unsigned i = 0; i < d; ++i) rows[i] = (state >> (width * i)) & rowmask;
      rows[d] = addresses;
      for (unsigned f = 1; f <= rowmask; ++f) {
        unsigned bit = f & -f;
        forms[f] = forms[f ^ bit] ^ rows[__builtin_ctz(bit)];
      }
      for (auto [u, f] : gates) {
        unsigned next = state ^ changes[u][forms[f]];
        if (distance[next] == 255) {
          if (distance[state] >= 253) throw std::runtime_error("distance overflow");
          distance[next] = distance[state] + 1;
          queue.push_back(next);
        }
        ++edges;
      }
    }
    unsigned histogram[255] = {};
    for (unsigned state : queue) ++histogram[distance[state]];
    std::ofstream output(argv[2], std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("cannot open output");
    output.write(reinterpret_cast<const char*>(distance.data()), distance.size());
    if (!output) throw std::runtime_error("failed output write");
    std::cout << "{\"dimension\":" << d << ",\"generators\":" << gates.size()
              << ",\"states\":" << queue.size() << ",\"edges\":" << edges
              << ",\"histogram\":[";
    for (unsigned i = 0; i <= d; ++i) std::cout << (i ? "," : "") << histogram[i];
    std::cout << "]}\n";
    return 0;
  } catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
