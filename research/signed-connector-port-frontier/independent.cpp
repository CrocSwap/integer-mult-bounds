// SPDX-License-Identifier: Apache-2.0
// Contributor: Ross Richardson, with substantial OpenAI Codex assistance.
// Independently implemented without reading or importing the primary census.
// Independent finite census by source-interval endpoint algebra.
//
// Compile: c++ -O3 -std=c++17 independent.cpp -o /tmp/port-census-independent
// Run: /tmp/port-census-independent
//
// This implementation does not replay successive root source coefficients.
// Let S(g) be the signed number of shears before gap g.  For a source whose
// first and second occurrences are at a < b, with first sign e, its w-root
// coefficient is e * [a < g <= b].  Its induced z-root coefficient is
// e * (S(clamp(g,a,b)) - S(a)).  Thus restoration is precisely S(a)=S(b)
// for every source assigned to w.  A source assigned to z instead has only
// coefficient e * [a < g <= b] in z.  z's dirty coefficient is S(g); w's
// dirty coefficient is constant.  Readers are tested on every pair of gaps.
//
// Exact finite domain: 8 source ports * 6! signed source orders * C(10,4)
// transfer positions * C(4,2) balanced transfer sign words = 7,257,600.
// B_j are sources, A_i readers. Bits 0..2 select B ports, bits 3..5 A ports;
// port 0 is z and port 1 is w. Both occurrences of each operator use its
// selected port. An accepted reader difference is either sign of its row.
// No theorem outside this explicitly finite circuit grammar is asserted.

#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>

using Vector = std::array<int, 3>;
using Matrix = std::array<Vector, 3>;
using Count = std::uint64_t;
constexpr Matrix rows{{{1, 1, 1}, {1, 1, -1}, {1, -1, 0}}};

void require(bool condition, const char* message) {
  if (!condition) throw std::runtime_error(message);
}

struct Endpoint {
  int first;
  int second;
  int sign;
};

int active_coefficient(const Endpoint& endpoint, int gap) {
  return endpoint.first < gap && gap <= endpoint.second ? endpoint.sign : 0;
}

int transferred_coefficient(const Endpoint& endpoint,
                            const std::array<int, 11>& shear_prefix, int gap) {
  const int clipped = std::clamp(gap, endpoint.first, endpoint.second);
  return endpoint.sign * (shear_prefix[clipped] - shear_prefix[endpoint.first]);
}

void self_test() {
  // The source interval (1,6] contains shears + at 2, - at 4.
  const std::array<int, 11> prefix{{0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0}};
  const Endpoint source{1, 6, 1};
  const std::array<int, 11> expected_active{{0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0}};
  const std::array<int, 11> expected_transfer{{0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0}};
  for (int gap = 0; gap <= 10; ++gap) {
    require(active_coefficient(source, gap) == expected_active[gap], "active interval self-test");
    require(transferred_coefficient(source, prefix, gap) == expected_transfer[gap], "transfer interval self-test");
    Endpoint negative = source;
    negative.sign = -1;
    require(transferred_coefficient(negative, prefix, gap) == -expected_transfer[gap], "negative source self-test");
  }
  // Moving the second endpoint before the inverse shear leaves residue.
  const Endpoint unrestored{1, 4, 1};
  require(transferred_coefficient(unrestored, prefix, 10) == 1, "nonrestoration residue self-test");
  require(prefix[unrestored.first] != prefix[unrestored.second], "nonrestoration criterion self-test");
}

struct Census {
  std::array<Count, 8> restored_by_source{};
  std::array<Count, 8> feasible_by_source{};
  std::array<Count, 64> count_by_port{};
  Count traces = 0;
  Count restored_traces = 0;
  Count feasible_traces = 0;
};

Census census(const Matrix& target, bool require_same_dirt = true) {
  Census result;

  // A lexicographic 4-of-10 Boolean word locates all transfer events.
  std::array<int, 10> transfer_position{{0, 0, 0, 0, 0, 0, 1, 1, 1, 1}};
  do {
    std::array<int, 4> transfer_sign{{-1, -1, 1, 1}};
    do {
      std::array<int, 11> prefix{};
      std::array<int, 6> source_position{};
      int source_index = 0;
      int transfer_index = 0;
      for (int pos = 0; pos < 10; ++pos) {
        prefix[pos + 1] = prefix[pos];
        if (transfer_position[pos]) prefix[pos + 1] += transfer_sign[transfer_index++];
        else source_position[source_index++] = pos;
      }
      require(prefix[10] == 0, "balanced shear word");
      std::array<int, 6> source_order{{0, 1, 2, 3, 4, 5}};
      do {
        std::array<Endpoint, 3> endpoints{};
        std::array<int, 3> seen{};
        for (int index = 0; index < 6; ++index) {
          const int token = source_order[index];
          const int j = token / 2;
          if (!seen[j]++) endpoints[j] = {source_position[index], -1, token % 2 ? -1 : 1};
          else endpoints[j].second = source_position[index];
        }
        int restorable_sources = 0;
        std::array<Vector, 11> active{};
        std::array<Vector, 11> transferred{};
        for (int j = 0; j < 3; ++j) {
          if (prefix[endpoints[j].first] == prefix[endpoints[j].second]) {
            restorable_sources |= 1 << j;
          }
          for (int gap = 0; gap <= 10; ++gap) {
            active[gap][j] = active_coefficient(endpoints[j], gap);
            transferred[gap][j] = transferred_coefficient(endpoints[j], prefix, gap);
          }
        }
        for (int source_mask = 0; source_mask < 8; ++source_mask) {
          ++result.traces;
          if ((source_mask & restorable_sources) != source_mask) continue;
          ++result.restored_traces;
          ++result.restored_by_source[source_mask];
          std::array<std::array<Vector, 11>, 2> values{};
          for (int gap = 0; gap <= 10; ++gap) {
            for (int j = 0; j < 3; ++j) {
              const bool on_w = (source_mask & (1 << j)) != 0;
              values[0][gap][j] = on_w ? transferred[gap][j] : active[gap][j];
              values[1][gap][j] = on_w ? active[gap][j] : 0;
            }
          }
          std::array<int, 3> allowed_reader_ports{};
          for (int port = 0; port < 2; ++port) {
            for (int earlier = 0; earlier < 10; ++earlier) {
              for (int later = earlier + 1; later <= 10; ++later) {
                if (require_same_dirt && port == 0 && prefix[earlier] != prefix[later]) continue;
                const Vector difference{{values[port][later][0] - values[port][earlier][0],
                                         values[port][later][1] - values[port][earlier][1],
                                         values[port][later][2] - values[port][earlier][2]}};
                for (int row = 0; row < 3; ++row) {
                  bool positive = true;
                  bool negative = true;
                  for (int j = 0; j < 3; ++j) {
                    positive &= difference[j] == target[row][j];
                    negative &= difference[j] == -target[row][j];
                  }
                  if (positive || negative) allowed_reader_ports[row] |= 1 << port;
                }
              }
            }
          }
          if (!allowed_reader_ports[0] || !allowed_reader_ports[1] || !allowed_reader_ports[2]) continue;
          ++result.feasible_traces;
          ++result.feasible_by_source[source_mask];
          for (int reader_mask = 0; reader_mask < 8; ++reader_mask) {
            bool allowed = true;
            for (int row = 0; row < 3; ++row) {
              const int selected_port = (reader_mask >> row) & 1;
              allowed &= (allowed_reader_ports[row] & (1 << selected_port)) != 0;
            }
            if (allowed) ++result.count_by_port[source_mask | (reader_mask << 3)];
          }
        }
      } while (std::next_permutation(source_order.begin(), source_order.end()));
    } while (std::next_permutation(transfer_sign.begin(), transfer_sign.end()));
  } while (std::next_permutation(transfer_position.begin(), transfer_position.end()));
  require(result.traces == 7257600, "complete enumeration size");
  require(std::accumulate(result.restored_by_source.begin(), result.restored_by_source.end(), Count{0}) == result.restored_traces,
          "restoration count reconciliation");
  require(std::accumulate(result.feasible_by_source.begin(), result.feasible_by_source.end(), Count{0}) == result.feasible_traces,
          "feasibility count reconciliation");
  return result;
}

template <typename T, std::size_t Size>
void array_output(const std::array<T, Size>& array) {
  std::cout << '[';
  for (std::size_t i = 0; i < array.size(); ++i) {
    if (i) std::cout << ',';
    std::cout << array[i];
  }
  std::cout << ']';
}

void compact_output(const Census& result) {
  std::cout << "{\"feasible_source_trace_count\":" << result.feasible_traces
            << ",\"nonzero_port_mask_counts\":{";
  bool first = true;
  for (int mask = 0; mask < 64; ++mask) {
    if (!result.count_by_port[mask]) continue;
    if (!first) std::cout << ',';
    first = false;
    std::cout << '\"' << mask << "\":" << result.count_by_port[mask];
  }
  std::cout << "}}";
}

int swap_mask_bits(int mask, int i, int j) {
  if (((mask >> i) & 1) != ((mask >> j) & 1)) mask ^= (1 << i) | (1 << j);
  return mask;
}

int main() {
  self_test();
  const Census result = census(rows);
  Matrix row_swap = rows;
  std::swap(row_swap[0], row_swap[2]);
  const Census swapped_rows = census(row_swap);
  Matrix column_swap = rows;
  for (auto& row : column_swap) std::swap(row[0], row[2]);
  const Census swapped_columns = census(column_swap);
  Matrix column_sign_flip = rows;
  for (auto& row : column_sign_flip) row[2] = -row[2];
  const Census flipped_column = census(column_sign_flip);
  const Census omitted_dirt = census(rows, false);
  const Matrix all_ones{{{1, 1, 1}, {1, 1, 1}, {1, 1, 1}}};
  const Census ones = census(all_ones);
  Matrix zero_replaced = rows;
  zero_replaced[2][2] = 1;
  const Census replaced_zero = census(zero_replaced);

  for (int mask = 0; mask < 64; ++mask) {
    require(swapped_rows.count_by_port[swap_mask_bits(mask, 3, 5)] == result.count_by_port[mask], "row permutation equivariance");
    require(swapped_columns.count_by_port[swap_mask_bits(mask, 0, 2)] == result.count_by_port[mask], "column permutation equivariance");
    require(flipped_column.count_by_port[mask] == result.count_by_port[mask], "column sign invariance");
    require(omitted_dirt.count_by_port[mask] >= result.count_by_port[mask], "dirt removal monotonicity");
  }
  require(omitted_dirt.count_by_port != result.count_by_port, "dirt removal strict sensitivity");
  require(ones.count_by_port != result.count_by_port, "target matrix sensitivity");

  std::cout << "{\n  \"method\": \"independent source-interval endpoint algebra\",\n"
            << "  \"matrix_rows\": [[1,1,1],[1,1,-1],[1,-1,0]],\n"
            << "  \"mask_convention\": \"bits0..2=B0..B2 source; bits3..5=A0..A2 reader; 0=z,1=w\",\n"
            << "  \"trace_count\": " << result.traces << ",\n"
            << "  \"restored_trace_count\": " << result.restored_traces << ",\n"
            << "  \"feasible_source_trace_count\": " << result.feasible_traces << ",\n";
  std::cout << "  \"restored_by_source_mask\": "; array_output(result.restored_by_source); std::cout << ",\n";
  std::cout << "  \"feasible_by_source_mask\": "; array_output(result.feasible_by_source); std::cout << ",\n";
  std::cout << "  \"feasible_trace_count_by_six_bit_port_mask\": "; array_output(result.count_by_port); std::cout << ",\n";
  std::cout << "  \"controls\": {\n";
  std::cout << "    \"swap_rows_0_2\": "; compact_output(swapped_rows); std::cout << ",\n";
  std::cout << "    \"swap_columns_0_2\": "; compact_output(swapped_columns); std::cout << ",\n";
  std::cout << "    \"negate_column_2\": "; compact_output(flipped_column); std::cout << ",\n";
  std::cout << "    \"omit_same_dirt_requirement_invalid\": "; compact_output(omitted_dirt); std::cout << ",\n";
  std::cout << "    \"all_ones_target\": "; compact_output(ones); std::cout << ",\n";
  std::cout << "    \"replace_entry_2_2_zero_with_one\": "; compact_output(replaced_zero); std::cout << "\n";
  std::cout << "  }\n}\n";
}
