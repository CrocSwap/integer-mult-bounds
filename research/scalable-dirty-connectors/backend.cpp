#include <algorithm>
#include <bit>
#include <charconv>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

using Word = std::uint64_t;
using Clock = std::chrono::steady_clock;
static volatile Word timing_guard = 0;

template <class T> static T argument(const char *text) {
  const std::string_view value(text);
  T result{};
  const auto [end, error] =
      std::from_chars(value.data(), value.data() + value.size(), result);
  if (error != std::errc{} || end != value.data() + value.size())
    throw std::runtime_error("invalid numeric argument");
  return result;
}

enum class Kind : std::uint8_t { X, B, A };
struct Op {
  Kind kind;
  std::uint16_t a;
  std::uint16_t b;
};

struct LoadedProgram {
  std::vector<Op> operations;
  std::uint64_t file_bytes = 0;
};

struct Programs {
  std::vector<Op> star;
  std::vector<Op> baseline;
  std::uint64_t star_file_bytes = 0;
  std::uint64_t baseline_file_bytes = 0;
};

struct Stats {
  std::uint64_t dense_leaves = 0;
  std::uint64_t matrix_word_reads = 0;
  std::uint64_t source_word_reads = 0;
  std::uint64_t and_words = 0;
  std::uint64_t popcounts = 0;
  std::uint64_t parity_xors = 0;
  std::uint64_t dense_target_word_reads = 0;
  std::uint64_t dense_target_word_writes = 0;
  std::uint64_t echo_internal_nodes = 0;
  std::uint64_t source_calls = 0;
  std::uint64_t sparse_calls = 0;
  std::uint64_t sparse_support_index_reads = 0;
  std::uint64_t sparse_source_word_reads = 0;
  std::uint64_t sparse_target_word_reads = 0;
  std::uint64_t sparse_target_word_writes = 0;
  std::uint64_t sparse_xors = 0;
  std::uint64_t shears = 0;
  std::uint64_t shear_word_reads = 0;
  std::uint64_t shear_word_writes = 0;
  std::uint64_t shear_xors = 0;
};

struct Matrix {
  int n = 0;
  int words = 0;
  std::vector<Word> cells;
};

struct Support {
  std::vector<std::uint16_t> left;
  std::vector<std::uint16_t> right;
};

struct Fixture {
  int n = 0;
  int masks = 0;
  int roots = 0;
  int words = 0;
  int scratch_count = 3;
  int root_base = 0;
  int scratch_base = 0;
  std::vector<std::vector<Matrix>> b_factors;
  std::vector<Support> a_support;
  const Fixture *maps_from = nullptr;
  std::vector<Word> rows;
  std::vector<Word> initial_rows;
};

static const std::vector<std::vector<Matrix>> &b_maps(const Fixture &f) {
  return f.maps_from ? b_maps(*f.maps_from) : f.b_factors;
}

static const std::vector<Support> &a_maps(const Fixture &f) {
  return f.maps_from ? a_maps(*f.maps_from) : f.a_support;
}

static LoadedProgram read_program(const std::string &path) {
  std::ifstream input(path);
  if (!input)
    throw std::runtime_error("cannot read " + path);
  LoadedProgram result;
  std::string line;
  std::size_t line_number = 0;
  while (std::getline(input, line)) {
    ++line_number;
    result.file_bytes += line.size() + 1;
    std::istringstream row(line);
    std::string tag;
    std::string extra;
    long long a = -1;
    long long b = -1;
    if (!(row >> tag >> a >> b) || (row >> extra)) {
      throw std::runtime_error(path + ": malformed operation at line " +
                               std::to_string(line_number));
    }
    if (a < 0 || a > 65535 || b < 0 || b > 65535) {
      throw std::runtime_error(
          path + ": operation argument out of uint16 range at line " +
          std::to_string(line_number));
    }
    Kind kind;
    if (tag == "X")
      kind = Kind::X;
    else if (tag == "B")
      kind = Kind::B;
    else if (tag == "A")
      kind = Kind::A;
    else
      throw std::runtime_error(path + ": unknown operation tag at line " +
                               std::to_string(line_number));
    result.operations.push_back(
        Op{kind, static_cast<std::uint16_t>(a), static_cast<std::uint16_t>(b)});
  }
  if (!input.eof())
    throw std::runtime_error("I/O error while reading " + path);
  result.file_bytes = std::filesystem::file_size(path);
  return result;
}

static void count_program(const std::vector<Op> &p, std::uint64_t &xs,
                          std::uint64_t &bs, std::uint64_t &as) {
  xs = bs = as = 0;
  for (const Op &op : p) {
    if (op.kind == Kind::X)
      ++xs;
    else if (op.kind == Kind::B)
      ++bs;
    else
      ++as;
  }
}

static Word *row_ptr(Fixture &f, int row) {
  return f.rows.data() + static_cast<std::size_t>(row) * f.words;
}
static const Word *row_ptr(const Fixture &f, int row) {
  return f.rows.data() + static_cast<std::size_t>(row) * f.words;
}

static void dense_add(const Matrix &matrix, const Word *src, Word *dst,
                      Stats *stats) {
  const int L = matrix.n;
  const int W = matrix.words;
  const Word *mrow = matrix.cells.data();
  if (stats)
    ++stats->dense_leaves;
  for (int base = 0; base < L; base += 64) {
    Word result_word = 0;
    for (int bit = 0; bit < 64; ++bit) {
      const int i = base + bit;
      unsigned parity = 0;
      for (int w = 0; w < W; ++w) {
        const Word coefficient_word = mrow[static_cast<std::size_t>(i) * W + w];
        const Word source_word = src[w];
        parity ^= static_cast<unsigned>(
            std::popcount(coefficient_word & source_word) & 1u);
        if (stats) {
          ++stats->matrix_word_reads;
          ++stats->source_word_reads;
          ++stats->and_words;
          ++stats->popcounts;
          ++stats->parity_xors;
        }
      }
      result_word |= static_cast<Word>(parity) << bit;
    }
    const int target_word = base / 64;
    dst[target_word] ^= result_word;
    if (stats) {
      ++stats->dense_target_word_reads;
      ++stats->dense_target_word_writes;
    }
  }
}

static void echo(Fixture &f, int source_row, int target_row, int source, int lo,
                 int hi, int depth, Stats *stats) {
  if (hi - lo == 1) {
    dense_add(b_maps(f)[source][lo], row_ptr(f, source_row),
              row_ptr(f, target_row), stats);
    return;
  }
  if (stats)
    ++stats->echo_internal_nodes;
  const int mid = lo + (hi - lo) / 2;
  const int scratch_row = f.scratch_base + depth;
  // The left factor interval is applied first; the right interval follows it.
  echo(f, source_row, scratch_row, source, lo, mid, depth + 1, stats);
  echo(f, scratch_row, target_row, source, mid, hi, depth + 1, stats);
  echo(f, source_row, scratch_row, source, lo, mid, depth + 1, stats);
  echo(f, scratch_row, target_row, source, mid, hi, depth + 1, stats);
}

static bool bit_at(const Word *row, int bit) {
  return ((row[bit / 64] >> (bit % 64)) & 1u) != 0;
}

static void sparse_add(const Support &support, const Word *src, Word *dst,
                       int L, Stats *stats) {
  if (stats)
    ++stats->sparse_calls;
  for (int base = 0; base < L; base += 64) {
    Word contribution = 0;
    for (int bit = 0; bit < 64; ++bit) {
      const int i = base + bit;
      const int p = support.left[i];
      const int q = support.right[i];
      const bool value = bit_at(src, p) ^ bit_at(src, q);
      contribution |= static_cast<Word>(value) << bit;
      if (stats) {
        stats->sparse_support_index_reads += 2;
        stats->sparse_source_word_reads += 2;
        ++stats->sparse_xors;
      }
    }
    const int target_word = base / 64;
    dst[target_word] ^= contribution;
    if (stats) {
      ++stats->sparse_target_word_reads;
      ++stats->sparse_target_word_writes;
      ++stats->sparse_xors;
    }
  }
}

static void row_xor(Word *dst, const Word *src, int W, Stats *stats) {
  if (stats)
    ++stats->shears;
  for (int w = 0; w < W; ++w) {
    dst[w] ^= src[w];
    if (stats) {
      stats->shear_word_reads += 2;
      ++stats->shear_word_writes;
      ++stats->shear_xors;
    }
  }
}

static void run_program(Fixture &f, const std::vector<Op> &program,
                        Stats *stats) {
  for (const Op &op : program) {
    if (op.kind == Kind::X) {
      if (op.a >= f.roots || op.b >= f.roots)
        throw std::runtime_error("bad shear root index");
      row_xor(row_ptr(f, f.root_base + op.a), row_ptr(f, f.root_base + op.b),
              f.words, stats);
    } else if (op.kind == Kind::B) {
      if (op.a >= f.n || op.b >= f.roots)
        throw std::runtime_error("bad B source/root index");
      if (stats)
        ++stats->source_calls;
      echo(f, op.a, f.root_base + op.b, op.a, 0, 5, 0, stats);
    } else {
      if (op.a == 0 || op.a > f.masks || op.b >= f.roots)
        throw std::runtime_error("bad A mask/root index");
      sparse_add(a_maps(f)[op.a], row_ptr(f, f.root_base + op.b),
                 row_ptr(f, f.n + (op.a - 1)), f.words * 64, stats);
    }
  }
}

static Matrix random_matrix(int L, std::mt19937_64 &rng) {
  Matrix m;
  m.n = L;
  m.words = L / 64;
  m.cells.resize(static_cast<std::size_t>(L) * m.words);
  for (Word &w : m.cells)
    w = rng();
  return m;
}

static void randomize_row(Word *row, int W, std::mt19937_64 &rng) {
  for (int i = 0; i < W; ++i)
    row[i] = rng();
}

static std::vector<Word> direct_matvec(const Matrix &m,
                                       const std::vector<Word> &src) {
  std::vector<Word> dst(m.words, 0);
  for (int i = 0; i < m.n; ++i) {
    unsigned parity = 0;
    for (int w = 0; w < m.words; ++w) {
      parity ^= static_cast<unsigned>(
          std::popcount(m.cells[static_cast<std::size_t>(i) * m.words + w] &
                        src[w]) &
          1u);
    }
    dst[i / 64] ^= static_cast<Word>(parity) << (i % 64);
  }
  return dst;
}

static std::vector<Word> direct_b(const Fixture &f, int source,
                                  const std::vector<Word> &input) {
  std::vector<Word> current = input;
  for (const Matrix &factor : b_maps(f)[source])
    current = direct_matvec(factor, current);
  return current;
}

static std::vector<Word> direct_a(const Fixture &f, int mask,
                                  const std::vector<Word> &input) {
  std::vector<Word> result(f.words, 0);
  const Support &support = a_maps(f)[mask];
  for (int i = 0; i < f.words * 64; ++i) {
    const bool value = bit_at(input.data(), support.left[i]) ^
                       bit_at(input.data(), support.right[i]);
    result[i / 64] ^= static_cast<Word>(value) << (i % 64);
  }
  return result;
}

static void xor_into(std::vector<Word> &dst, const std::vector<Word> &src) {
  for (std::size_t i = 0; i < dst.size(); ++i)
    dst[i] ^= src[i];
}

static std::vector<Word> copy_row(const Fixture &f, int row) {
  const Word *ptr = row_ptr(f, row);
  return std::vector<Word>(ptr, ptr + f.words);
}

static bool equal_row(const Fixture &f, int row,
                      const std::vector<Word> &expected) {
  const Word *ptr = row_ptr(f, row);
  return std::equal(ptr, ptr + f.words, expected.begin(), expected.end());
}

static void check_b_call(Fixture &f, int source, int root,
                         std::uint64_t &checked) {
  std::vector<std::vector<Word>> roots_before;
  for (int r = 0; r < f.roots; ++r)
    roots_before.push_back(copy_row(f, f.root_base + r));
  std::vector<std::vector<Word>> scratch_before;
  for (int r = 0; r < f.scratch_count; ++r)
    scratch_before.push_back(copy_row(f, f.scratch_base + r));
  const std::vector<Word> source_before = copy_row(f, source);
  const std::vector<Word> contribution = direct_b(f, source, source_before);
  std::vector<Word> target_expected = roots_before[root];
  xor_into(target_expected, contribution);
  echo(f, source, f.root_base + root, source, 0, 5, 0, nullptr);
  if (!equal_row(f, f.root_base + root, target_expected))
    throw std::runtime_error("B echo output mismatch");
  for (int r = 0; r < f.roots; ++r) {
    if (r != root && !equal_row(f, f.root_base + r, roots_before[r]))
      throw std::runtime_error("B echo changed another root");
  }
  if (!equal_row(f, source, source_before))
    throw std::runtime_error("B echo changed source");
  for (int r = 0; r < f.scratch_count; ++r) {
    if (!equal_row(f, f.scratch_base + r, scratch_before[r]))
      throw std::runtime_error("B echo failed private scratch restoration");
  }
  ++checked;
}

static void check_a_call(Fixture &f, int mask, int root,
                         std::uint64_t &checked) {
  const std::vector<Word> input = copy_row(f, f.root_base + root);
  const std::vector<Word> output_before = copy_row(f, f.n + mask - 1);
  std::vector<Word> expected = output_before;
  xor_into(expected, direct_a(f, mask, input));
  std::vector<std::vector<Word>> roots_before;
  for (int r = 0; r < f.roots; ++r)
    roots_before.push_back(copy_row(f, f.root_base + r));
  sparse_add(a_maps(f)[mask], row_ptr(f, f.root_base + root),
             row_ptr(f, f.n + mask - 1), f.words * 64, nullptr);
  if (!equal_row(f, f.n + mask - 1, expected))
    throw std::runtime_error("A sparse output mismatch");
  for (int r = 0; r < f.roots; ++r) {
    if (!equal_row(f, f.root_base + r, roots_before[r]))
      throw std::runtime_error("A changed connector roots");
  }
  ++checked;
}

static void validate_program(Fixture &f, const std::vector<Op> &program,
                             std::uint64_t &checked_calls) {
  f.rows = f.initial_rows;
  for (const Op &op : program) {
    if (op.kind == Kind::X) {
      row_xor(row_ptr(f, f.root_base + op.a), row_ptr(f, f.root_base + op.b),
              f.words, nullptr);
    } else if (op.kind == Kind::B) {
      check_b_call(f, op.a, op.b, checked_calls);
    } else {
      check_a_call(f, op.a, op.b, checked_calls);
    }
  }
  for (int r = 0; r < f.n; ++r) {
    if (!std::equal(row_ptr(f, r), row_ptr(f, r) + f.words,
                    f.initial_rows.begin() +
                        static_cast<std::size_t>(r) * f.words)) {
      throw std::runtime_error("program changed source row");
    }
  }
  for (int r = 0; r < f.roots; ++r) {
    if (!std::equal(row_ptr(f, f.root_base + r),
                    row_ptr(f, f.root_base + r) + f.words,
                    f.initial_rows.begin() +
                        static_cast<std::size_t>(f.root_base + r) * f.words)) {
      throw std::runtime_error("program failed dirty-root restoration");
    }
  }
  for (int r = 0; r < f.scratch_count; ++r) {
    if (!std::equal(row_ptr(f, f.scratch_base + r),
                    row_ptr(f, f.scratch_base + r) + f.words,
                    f.initial_rows.begin() +
                        static_cast<std::size_t>(f.scratch_base + r) *
                            f.words)) {
      throw std::runtime_error(
          "program failed dirty-private-scratch restoration");
    }
  }

  std::vector<std::vector<Word>> expected(f.masks + 1,
                                          std::vector<Word>(f.words, 0));
  for (int mask = 1; mask <= f.masks; ++mask) {
    std::vector<Word> sum(f.words, 0);
    for (int j = 0; j < f.n; ++j) {
      if ((mask >> j) & 1) {
        const Word *source_ptr =
            f.initial_rows.data() + static_cast<std::size_t>(j) * f.words;
        std::vector<Word> source(source_ptr, source_ptr + f.words);
        xor_into(sum, direct_b(f, j, source));
      }
    }
    expected[mask] = direct_a(f, mask, sum);
    xor_into(expected[mask],
             std::vector<Word>(
                 f.initial_rows.begin() +
                     static_cast<std::size_t>(f.n + mask - 1) * f.words,
                 f.initial_rows.begin() +
                     static_cast<std::size_t>(f.n + mask) * f.words));
  }
  for (int mask = 1; mask <= f.masks; ++mask) {
    if (!equal_row(f, f.n + mask - 1, expected[mask])) {
      throw std::runtime_error("complete program target mismatch at mask " +
                               std::to_string(mask));
    }
  }
}

static void validate_formal(const std::vector<Op> &program, int n, int roots,
                            const std::string &name,
                            bool exactly_twice_per_source,
                            bool paired_readouts = true) {
  const int formal_bits = roots + n;
  std::vector<std::uint32_t> root_rows(roots);
  for (int r = 0; r < roots; ++r)
    root_rows[r] = 1u << r;
  std::vector<std::vector<std::pair<std::uint32_t, unsigned>>> observations(
      (1 << n));
  std::vector<std::vector<int>> source_ports(n);
  std::uint64_t xs = 0, bs = 0, as = 0;
  for (const Op &op : program) {
    if (op.kind == Kind::X) {
      if (op.a >= roots || op.b >= roots)
        throw std::runtime_error(name + ": invalid X root");
      root_rows[op.a] ^= root_rows[op.b];
      ++xs;
    } else if (op.kind == Kind::B) {
      if (op.a >= n || op.b >= roots)
        throw std::runtime_error(name + ": invalid B source/port");
      root_rows[op.b] ^= 1u << (roots + op.a);
      source_ports[op.a].push_back(op.b);
      ++bs;
    } else {
      if (op.a == 0 || op.a >= (1u << n) || op.b >= roots)
        throw std::runtime_error(name + ": invalid A mask/port");
      observations[op.a].push_back(
          {root_rows[op.b], static_cast<unsigned>(op.b)});
      ++as;
    }
  }
  for (int r = 0; r < roots; ++r) {
    if (root_rows[r] != (1u << r))
      throw std::runtime_error(name + ": formal dirty roots did not restore");
  }
  for (int j = 0; j < n; ++j) {
    if (source_ports[j].size() < 2 ||
        (exactly_twice_per_source && source_ports[j].size() != 2) ||
        !std::all_of(source_ports[j].begin(), source_ports[j].end(),
                     [&](int port) { return port == source_ports[j][0]; })) {
      throw std::runtime_error(
          name + ": source port schedule did not cancel the dirty root");
    }
  }
  for (int mask = 1; mask < (1 << n); ++mask) {
    const auto &reads = observations[mask];
    if (reads.size() < 2 || reads.size() % 2 != 0 ||
        (paired_readouts && reads.size() != 2))
      throw std::runtime_error(name + ": invalid readout incidence");
    std::uint32_t contribution = 0;
    for (const auto &[row, port] : reads) {
      (void)port;
      contribution ^= row;
    }
    if (contribution != (static_cast<std::uint32_t>(mask) << roots))
      throw std::runtime_error(name +
                               ": dirty/readout source polynomial mismatch");
  }
  if (formal_bits > 31)
    throw std::runtime_error(name + ": formal basis too wide");
  std::cout << "FORMAL " << name << " PASS X=" << xs << " B=" << bs
            << " A=" << as << '\n';
}

static Fixture make_fixture(int n, int L, std::uint64_t seed,
                            bool make_maps = true) {
  if (L <= 0 || L % 64 != 0)
    throw std::runtime_error("L must be a positive multiple of 64");
  Fixture f;
  f.n = n;
  f.masks = (1 << n) - 1;
  f.roots = n - 3;
  f.words = L / 64;
  f.root_base = n + f.masks;
  f.scratch_base = f.root_base + f.roots;
  const int row_count = f.scratch_base + f.scratch_count;
  f.rows.resize(static_cast<std::size_t>(row_count) * f.words);
  f.initial_rows.resize(f.rows.size());
  std::mt19937_64 rng(seed);
  if (make_maps) {
    for (int j = 0; j < n; ++j) {
      std::vector<Matrix> factors;
      for (int d = 0; d < 5; ++d)
        factors.push_back(random_matrix(L, rng));
      f.b_factors.push_back(std::move(factors));
    }
    f.a_support.resize(f.masks + 1);
    for (int mask = 1; mask <= f.masks; ++mask) {
      Support s;
      s.left.resize(L);
      s.right.resize(L);
      for (int i = 0; i < L; ++i) {
        s.left[i] = static_cast<std::uint16_t>((i + mask) % L);
        s.right[i] = static_cast<std::uint16_t>((i + 7 * mask + 1) % L);
        if (s.left[i] == s.right[i])
          throw std::runtime_error("sparse A support collision");
      }
      f.a_support[mask] = std::move(s);
    }
  }
  for (int r = 0; r < row_count; ++r)
    randomize_row(row_ptr(f, r), f.words, rng);
  f.initial_rows = f.rows;
  return f;
}

static std::uint64_t row_words_for(int rows, int L) {
  return static_cast<std::uint64_t>(rows) * (L / 64);
}

static void print_stats(const std::string &name, const Stats &s) {
  std::cout << "COUNTS " << name << " dense_leaves=" << s.dense_leaves
            << " matrix_word_reads=" << s.matrix_word_reads
            << " source_word_reads=" << s.source_word_reads
            << " and_words=" << s.and_words << " popcounts=" << s.popcounts
            << " parity_xors=" << s.parity_xors
            << " target_word_reads=" << s.dense_target_word_reads
            << " target_word_writes=" << s.dense_target_word_writes
            << " echo_internal_nodes=" << s.echo_internal_nodes
            << " B_calls=" << s.source_calls << " A_calls=" << s.sparse_calls
            << " A_support_index_reads=" << s.sparse_support_index_reads
            << " A_source_word_reads=" << s.sparse_source_word_reads
            << " A_target_word_reads=" << s.sparse_target_word_reads
            << " A_target_word_writes=" << s.sparse_target_word_writes
            << " A_source_plus_target_xors=" << s.sparse_xors
            << " shears=" << s.shears
            << " shear_word_reads=" << s.shear_word_reads
            << " shear_word_writes=" << s.shear_word_writes
            << " shear_xors=" << s.shear_xors << '\n';
}

static double time_program(Fixture &f, const std::vector<Op> &program,
                           int repetitions) {
  const auto start = Clock::now();
  for (int i = 0; i < repetitions; ++i)
    run_program(f, program, nullptr);
  const auto end = Clock::now();
  // Consume the timed mutations through an observable write. This diagnostic
  // scan is outside the timed interval and needs one scalar CPU work word.
  Word checksum = 0;
  for (Word value : f.rows)
    checksum ^= value;
  timing_guard = checksum;
  return std::chrono::duration<double, std::micro>(end - start).count() /
         repetitions;
}

static int choose_repetitions(Fixture &f, const std::vector<Op> &p) {
  const auto start = Clock::now();
  for (int i = 0; i < 3; ++i)
    run_program(f, p, nullptr);
  const auto end = Clock::now();
  const double elapsed = std::chrono::duration<double>(end - start).count();
  if (elapsed <= 0.0)
    return 100;
  const int reps = static_cast<int>(0.25 / (elapsed / 3.0));
  return std::clamp(reps, 10, 10000);
}

static void print_trials(const char *name, const std::vector<double> &times) {
  std::cout << name << "=[";
  for (std::size_t i = 0; i < times.size(); ++i) {
    if (i)
      std::cout << ',';
    std::cout << times[i];
  }
  std::cout << ']';
}

int main(int argc, char **argv) {
  try {
    if (argc != 6 && argc != 7) {
      std::cerr
          << "usage: star_backend N L path/to/star.ops path/to/baseline.ops "
             "<extra|gray> [seed]\n";
      return 2;
    }
    const int n = argument<int>(argv[1]);
    const int L = argument<int>(argv[2]);
    const std::string star_path = argv[3];
    const std::string baseline_path = argv[4];
    const std::string baseline_kind = argv[5];
    if (baseline_kind != "extra" && baseline_kind != "gray")
      throw std::runtime_error("baseline must be extra or gray");
    const std::uint64_t seed = argc == 7 ? argument<std::uint64_t>(argv[6])
                                         : 0x535441520000ULL + n * 1009ULL + L;
    if (n != 6 && n != 8)
      throw std::runtime_error("benchmark supports n=6 and n=8 only");
    if (L > 65536)
      throw std::runtime_error("sparse support uses uint16 indices");

    const auto prep_start = Clock::now();
    Fixture candidate = make_fixture(n, L, seed);
    const double fixture_ms =
        std::chrono::duration<double, std::milli>(Clock::now() - prep_start)
            .count();
    const auto program_start = Clock::now();
    Programs programs;
    LoadedProgram star_file = read_program(star_path);
    LoadedProgram baseline_file = read_program(baseline_path);
    programs.star = std::move(star_file.operations);
    programs.baseline = std::move(baseline_file.operations);
    programs.star_file_bytes = star_file.file_bytes;
    programs.baseline_file_bytes = baseline_file.file_bytes;
    const double program_ms =
        std::chrono::duration<double, std::milli>(Clock::now() - program_start)
            .count();

    std::uint64_t xstar, bstar, astar, xbaseline, bbaseline, abaseline;
    count_program(programs.star, xstar, bstar, astar);
    count_program(programs.baseline, xbaseline, bbaseline, abaseline);
    const int expected_star_x = 8 * ((1 << (n - 4)) - 1);
    if (bstar != static_cast<std::uint64_t>(2 * n) ||
        astar != static_cast<std::uint64_t>(2 * candidate.masks) ||
        xstar != static_cast<std::uint64_t>(expected_star_x)) {
      throw std::runtime_error(
          "candidate operation counts differ from star receipt formula");
    }
    const int expected_baseline_b =
        baseline_kind == "extra" ? 2 * n : (1 << (n / 2)) + (1 << (n - n / 2));
    const int expected_baseline_a =
        baseline_kind == "extra" ? (n == 6 ? 156 : 828) : 2 * candidate.masks;
    if (bbaseline != static_cast<std::uint64_t>(expected_baseline_b) ||
        abaseline != static_cast<std::uint64_t>(expected_baseline_a) ||
        xbaseline != 0) {
      throw std::runtime_error("baseline operation counts incorrect");
    }
    const auto validation_start = Clock::now();
    validate_formal(programs.star, n, n - 3, "star", true);
    validate_formal(programs.baseline, n, 1, baseline_kind,
                    baseline_kind == "extra", baseline_kind == "gray");

    std::uint64_t checked_star = 0, checked_baseline = 0;
    candidate.roots = n - 3;
    candidate.root_base = n + candidate.masks;
    candidate.scratch_base = candidate.root_base + candidate.roots;
    validate_program(candidate, programs.star, checked_star);
    const double star_validation_ms = std::chrono::duration<double, std::milli>(
                                          Clock::now() - validation_start)
                                          .count();
    const auto baseline_prep_start = Clock::now();
    Fixture baseline = make_fixture(n, L, seed, false);
    // Both schedules use the same resident map tables; the baseline has its own
    // root/output/scratch rows but does not duplicate the expensive matrices.
    baseline.maps_from = &candidate;
    baseline.roots = 1;
    baseline.root_base = n + baseline.masks;
    baseline.scratch_base = baseline.root_base + baseline.roots;
    // Candidate has more roots, so use the same source/output rows and project
    // the same root 0 plus three arbitrary dirty private rows into this layout.
    baseline.rows.assign(static_cast<std::size_t>(baseline.scratch_base +
                                                  baseline.scratch_count) *
                             baseline.words,
                         0);
    baseline.initial_rows = baseline.rows;
    for (int r = 0; r < n + baseline.masks; ++r) {
      const Word *initial = candidate.initial_rows.data() +
                            static_cast<std::size_t>(r) * candidate.words;
      std::copy(initial, initial + candidate.words, row_ptr(baseline, r));
    }
    const Word *initial_root =
        candidate.initial_rows.data() +
        static_cast<std::size_t>(candidate.root_base) * candidate.words;
    std::copy(initial_root, initial_root + candidate.words,
              row_ptr(baseline, baseline.root_base));
    for (int r = 0; r < baseline.scratch_count; ++r) {
      const Word *initial_scratch =
          candidate.initial_rows.data() +
          static_cast<std::size_t>(candidate.scratch_base + r) *
              candidate.words;
      std::copy(initial_scratch, initial_scratch + candidate.words,
                row_ptr(baseline, baseline.scratch_base + r));
    }
    baseline.initial_rows = baseline.rows;
    const double baseline_layout_ms = std::chrono::duration<double, std::milli>(
                                          Clock::now() - baseline_prep_start)
                                          .count();
    const auto baseline_validation_start = Clock::now();
    validate_program(baseline, programs.baseline, checked_baseline);
    const double baseline_validation_ms =
        std::chrono::duration<double, std::milli>(Clock::now() -
                                                  baseline_validation_start)
            .count();

    Stats star_stats, baseline_stats;
    candidate.rows = candidate.initial_rows;
    run_program(candidate, programs.star, &star_stats);
    baseline.rows = baseline.initial_rows;
    run_program(baseline, programs.baseline, &baseline_stats);
    print_stats("star", star_stats);
    print_stats(baseline_kind, baseline_stats);

    std::uint64_t matrix_capacity_bytes = 0;
    std::uint64_t map_container_bytes =
        candidate.b_factors.capacity() * sizeof(std::vector<Matrix>);
    for (const auto &factors : candidate.b_factors) {
      map_container_bytes += factors.capacity() * sizeof(Matrix);
      for (const Matrix &matrix : factors) {
        matrix_capacity_bytes += matrix.cells.capacity() * sizeof(Word);
      }
    }
    std::uint64_t support_capacity_bytes = 0;
    map_container_bytes += candidate.a_support.capacity() * sizeof(Support);
    for (const Support &support : candidate.a_support) {
      support_capacity_bytes +=
          (support.left.capacity() + support.right.capacity()) *
          sizeof(std::uint16_t);
    }
    const std::uint64_t candidate_row_count =
        static_cast<std::uint64_t>(n + candidate.masks + (n - 3) + 3);
    const std::uint64_t baseline_row_count =
        static_cast<std::uint64_t>(n + candidate.masks + 1 + 3);
    const std::uint64_t candidate_row_bytes =
        row_words_for(candidate_row_count, L) * sizeof(Word);
    const std::uint64_t baseline_row_bytes =
        row_words_for(baseline_row_count, L) * sizeof(Word);
    const std::uint64_t total_row_bytes =
        2 * (candidate_row_bytes +
             baseline_row_bytes); // working rows plus dirty-input snapshots
    const std::uint64_t row_capacity_bytes =
        (candidate.rows.capacity() + candidate.initial_rows.capacity() +
         baseline.rows.capacity() + baseline.initial_rows.capacity()) *
        sizeof(Word);
    const std::uint64_t candidate_program_used_bytes =
        programs.star.size() * sizeof(Op);
    const std::uint64_t baseline_program_used_bytes =
        programs.baseline.size() * sizeof(Op);
    const std::uint64_t candidate_program_bytes =
        programs.star.capacity() * sizeof(Op);
    const std::uint64_t baseline_program_bytes =
        programs.baseline.capacity() * sizeof(Op);
    std::cout << "RECEIPT n=" << n << " L=" << L << " roots=" << candidate.roots
              << " B_star=" << bstar << " B_baseline=" << bbaseline
              << " source_saving_pct=" << std::fixed << std::setprecision(1)
              << (100.0 * (static_cast<double>(bbaseline - bstar) / bbaseline))
              << " baseline_kind=" << baseline_kind << " A_star=" << astar
              << " A_baseline=" << abaseline << " transfers=" << xstar
              << " dense_leaves_star=" << star_stats.dense_leaves
              << " dense_leaves_baseline=" << baseline_stats.dense_leaves
              << " checked_child_calls_star=" << checked_star
              << " checked_child_calls_baseline=" << checked_baseline
              << " program_dispatches_star=" << programs.star.size()
              << " program_dispatches_baseline=" << programs.baseline.size()
              << " matrix_vector_capacity_bytes_shared="
              << matrix_capacity_bytes
              << " sparse_index_capacity_bytes=" << support_capacity_bytes
              << " map_container_capacity_bytes=" << map_container_bytes
              << " map_capacity_bytes_shared="
              << (matrix_capacity_bytes + support_capacity_bytes +
                  map_container_bytes)
              << " rows_star_bytes=" << candidate_row_bytes
              << " rows_baseline_bytes=" << baseline_row_bytes
              << " row_snapshot_bytes_star=" << candidate_row_bytes
              << " row_snapshot_bytes_baseline=" << baseline_row_bytes
              << " total_resident_row_payload_bytes=" << total_row_bytes
              << " total_resident_row_capacity_bytes=" << row_capacity_bytes
              << " program_star_used_bytes=" << candidate_program_used_bytes
              << " program_baseline_used_bytes=" << baseline_program_used_bytes
              << " program_star_capacity_bytes=" << candidate_program_bytes
              << " program_baseline_capacity_bytes=" << baseline_program_bytes
              << " total_program_capacity_bytes="
              << (candidate_program_bytes + baseline_program_bytes)
              << " star_event_file_bytes=" << programs.star_file_bytes
              << " baseline_event_file_bytes=" << programs.baseline_file_bytes
              << " total_payload_capacity_bytes_estimate="
              << (matrix_capacity_bytes + support_capacity_bytes +
                  map_container_bytes + row_capacity_bytes +
                  candidate_program_bytes + baseline_program_bytes)
              << " sizeof_op=" << sizeof(Op)
              << " fixture_generation_ms=" << fixture_ms
              << " program_compile_parse_ms=" << program_ms
              << " baseline_layout_ms=" << baseline_layout_ms
              << " star_validation_ms=" << star_validation_ms
              << " baseline_validation_ms=" << baseline_validation_ms
              << " dense_cpu_clean_accumulator_words=1"
              << " B_depth=5 dense_leaves_per_B=28 echo_internal_nodes_per_B=9"
              << " private_scratch_rows_each=3 private_scratch_bits_each="
              << (3 * L)
              << " private_scratch_words_each=" << (3 * candidate.words)
              << '\n';

    // Warm each schedule once, then choose enough repetitions for a measurable
    // resident-memory interval without turning this into a repository build.
    candidate.rows = candidate.initial_rows;
    baseline.rows = baseline.initial_rows;
    const int star_reps = choose_repetitions(candidate, programs.star);
    const int baseline_reps = choose_repetitions(baseline, programs.baseline);
    std::vector<double> star_times, baseline_times;
    for (int trial = 0; trial < 7; ++trial) {
      candidate.rows = candidate.initial_rows;
      baseline.rows = baseline.initial_rows;
      if ((trial & 1) == 0) {
        star_times.push_back(time_program(candidate, programs.star, star_reps));
        baseline_times.push_back(
            time_program(baseline, programs.baseline, baseline_reps));
      } else {
        baseline_times.push_back(
            time_program(baseline, programs.baseline, baseline_reps));
        star_times.push_back(time_program(candidate, programs.star, star_reps));
      }
    }
    std::vector<double> star_sorted = star_times;
    std::vector<double> baseline_sorted = baseline_times;
    std::sort(star_sorted.begin(), star_sorted.end());
    std::sort(baseline_sorted.begin(), baseline_sorted.end());
    const double star_us = star_sorted[star_sorted.size() / 2];
    const double baseline_us = baseline_sorted[baseline_sorted.size() / 2];
    std::cout << "TIMING resident_cpu_median_us star=" << star_us
              << " baseline=" << baseline_us
              << " baseline_kind=" << baseline_kind
              << " ratio_baseline_over_star=" << std::setprecision(3)
              << (baseline_us / star_us) << std::setprecision(1)
              << " trials=7 star_repetitions=" << star_reps
              << " baseline_repetitions=" << baseline_reps
              << " includes_program_dispatch=true includes_data_reset=false"
              << " order=star,baseline;baseline,star;star,baseline;baseline,"
                 "star;star,baseline;"
                 "baseline,star;star,baseline raw_trials ";
    print_trials("star", star_times);
    std::cout << ' ';
    print_trials("baseline", baseline_times);
    std::cout << " excludes_fixture_and_program_preparation=true\n";
    return 0;
  } catch (const std::exception &e) {
    std::cerr << "FAIL " << e.what() << '\n';
    return 1;
  }
}
