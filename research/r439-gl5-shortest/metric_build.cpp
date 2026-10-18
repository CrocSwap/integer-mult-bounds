// Complete labelled GL(n,2) transvection BFS, n <= 5. Apache-2.0.
// Gareth Davidson, with substantial OpenAI Codex assistance.
// Standard Cayley-graph synthesis, not a new optimal-CNOT algorithm.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

int main(int argc, char **argv) {
  try {
    if (argc != 3) throw std::runtime_error("usage: metric_build n output-prefix");
    const int n = std::stoi(argv[1]);
    if (n < 2 || n > 5) throw std::runtime_error("n outside 2..5");
    const uint32_t size = 1u << (n*n), mask = (1u << n)-1;
    std::vector<uint8_t> distance(size, 255), last(size, 255);
    std::vector<int> order;
    uint64_t group = 1;
    uint32_t identity = 0;
    for (int d=0; d<n; ++d) {
      identity |= 1u << (n*d+d);
      group *= (1u << n) - (1u << d);
      for (int s=0; s<n; ++s) if (s != d) order.push_back(n*d+s);
    }
    std::sort(order.begin(), order.end(), [](int a,int b) {return (a^13)<(b^13);});
    std::vector<uint32_t> queue;
    queue.reserve(group);
    queue.push_back(identity); distance[identity] = 0;
    for (size_t i=0; i<queue.size(); ++i) {
      const uint32_t x=queue[i];
      for (int g:order) {
        const int d=g/n, s=g%n;
        const uint32_t y=x ^ (((x >> (n*s)) & mask) << (n*d));
        if (distance[y] != 255) continue;
        distance[y] = distance[x]+1; last[y]=g; queue.push_back(y);
      }
    }
    if (queue.size() != group) throw std::runtime_error("group cardinality");
    std::vector<uint64_t> histogram(32,0);
    for (auto x:queue) ++histogram.at(distance[x]);
    auto save = [&](const std::string &suffix, const std::vector<uint8_t> &data) {
      std::ofstream out(std::string(argv[2])+suffix, std::ios::binary);
      if (!out.write(reinterpret_cast<const char*>(data.data()),size))
        throw std::runtime_error("output failed");
    };
    save(".dist",distance); save(".last",last);
    std::cout << "{\"n\":" << n << ",\"vertices\":" << queue.size()
              << ",\"histogram\":[";
    while (histogram.back()==0) histogram.pop_back();
    for (size_t i=0; i<histogram.size(); ++i) std::cout << (i?",":"") << histogram[i];
    std::cout << "]}\n";
  } catch (const std::exception &e) {std::cerr<<e.what()<<'\n'; return 1;}
}
