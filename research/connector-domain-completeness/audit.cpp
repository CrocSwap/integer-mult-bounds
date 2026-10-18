// @krzysztofwojt with substantial OpenAI Codex assistance. Apache-2.0.
#include <iostream>
#include <vector>

void audit_gap(const std::vector<int>& gaps) {
  for (int gap : gaps) std::cout.put(static_cast<char>(gap));
}
#define main retained_main
#include "subject.cpp"  // authenticated private snapshot supplied by verify.py
#undef main

template <class Container> void emit(const Container& values) {
  for (auto value : values) std::cout << ' ' << value;
  std::cout << '\n';
}

int main(int argc, char** argv) {
  try {
    Tables tables;
    if (argc == 2) {
      const bool b = std::string(argv[1]) == "B";
      if (!b && std::string(argv[1]) != "A") throw std::runtime_error("expected A/B");
      Engine engine(tables, universal_templates(b).front(), b ? Counts{4,4,4} : Counts{6,4,4},
                    Clock::now() + std::chrono::seconds(120));
      // Only used with the explicitly instrumented gap body: no word search.
      if (!engine.enumerate() || engine.found || engine.timed_out)
        throw std::runtime_error("gap enumeration incomplete");
      return 0;
    }
    for (bool b : {false, true}) {
      const auto templates = universal_templates(b);
      for (const auto& word : templates) {
        Engine instance(tables, word, b ? Counts{4,4,4} : Counts{6,4,4},
                        Clock::now() + std::chrono::seconds(120));
        if (instance.blocks != (b ? 10 : 8)) throw std::runtime_error("wrong block count");
        std::cout << "T " << b; emit(word);
      }
      Engine engine(tables, templates.front(), b ? Counts{4,4,4} : Counts{6,4,4},
                    Clock::now() + std::chrono::seconds(120));
      for (int first = 0; first <= 7; ++first) for (int second = 0; second <= 7; ++second) {
        LowWord gaps(engine.blocks, 0); gaps[0] = first; gaps[1] = second;
        const auto domains = engine.domains_for(gaps);
        for (int slot : {0, 1}) {
          std::vector<int> ids;
          domains[slot].each([&](int id) { ids.push_back(id); });
          std::cout << "D " << b << ' ' << first << ' ' << second << ' ' << slot; emit(ids);
        }
      }
    }
    for (const auto& path : tables.paths) {
      std::cout << "P " << path.mask << ' ' << path.end;
      for (int count : path.counts) std::cout << ' ' << count;
      emit(path.word);
    }
    for (const auto& c : tables.candidates) {
      std::cout << "C";
      emit(std::vector<int>{c.normal, c.start, c.end, c.mask, c.length,
                            c.counts[0], c.counts[1], c.counts[2]});
    }
  } catch (const std::exception& error) {
    std::cerr << "AUDIT_ERROR " << error.what() << '\n'; return 1;
  }
}
