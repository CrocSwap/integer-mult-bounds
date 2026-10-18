// Exact GF(2) affine elimination. Input and output words are little endian.
#include <cstdint>
#include <cstdio>
#include <vector>

static bool read32(FILE* f, uint32_t& value) {
    unsigned char b[4];
    if (fread(b, 1, 4, f) != 4) return false;
    value = 0;
    for (int j = 0; j < 4; ++j) value |= uint32_t(b[j]) << (8*j);
    return true;
}
static bool write32(FILE* f, uint32_t value) {
    unsigned char b[4];
    for (int j = 0; j < 4; ++j) b[j] = (value >> (8*j)) & 255;
    return fwrite(b, 1, 4, f) == 4;
}
static bool readrow(FILE* f, std::vector<uint64_t>& row) {
    for (auto& value : row) {
        unsigned char b[8];
        if (fread(b, 1, 8, f) != 8) return false;
        value = 0;
        for (int j = 0; j < 8; ++j) value |= uint64_t(b[j]) << (8*j);
    }
    return true;
}
static bool writerow(FILE* f, const std::vector<uint64_t>& row) {
    for (auto value : row) {
        unsigned char b[8];
        for (int j = 0; j < 8; ++j) b[j] = (value >> (8*j)) & 255;
        if (fwrite(b, 1, 8, f) != 8) return false;
    }
    return true;
}
int main(int argc, char** argv) {
    if (argc != 2) return 2;
    uint32_t n, count;
    if (!read32(stdin, n) || !read32(stdin, count) || !n || n > 10000 || count > 10000000)
        return 2;
    const uint32_t words = (n + 64)/64;
    std::vector<std::vector<uint64_t>> basis(n);
    std::vector<uint64_t> row(words);
    uint32_t rank = 0;
    for (uint32_t k = 0; k < count; ++k) {
        if (!readrow(stdin, row)) return 2;
        if (n % 64 < 63 && row.back() >> ((n % 64)+1)) return 2;
        bool rhs = (row[n/64] >> (n % 64)) & 1;
        row[n/64] &= ~(uint64_t(1) << (n % 64));
        bool inserted = false;
        for (int word = int(words)-1; word >= 0;) {
            if (!row[word]) { --word; continue; }
            uint32_t pivot = word*64+63-__builtin_clzll(row[word]);
            if (pivot >= n) return 2;
            if (basis[pivot].empty()) {
                row[n/64] |= uint64_t(rhs) << (n % 64);
                basis[pivot] = row;
                ++rank;
                inserted = true;
                break;
            }
            rhs ^= (basis[pivot][n/64] >> (n % 64)) & 1;
            for (int j = 0; j <= word; ++j) row[j] ^= basis[pivot][j];
            row[n/64] &= ~(uint64_t(1) << (n % 64));
        }
        if (!inserted && rhs) {
            printf("{\"status\":\"INCONSISTENT\",\"row\":%u}\n", k);
            return 1;
        }
    }
    if (fgetc(stdin) != EOF) return 2;
    std::vector<uint32_t> free;
    for (uint32_t i = 0; i < n; ++i) if (basis[i].empty()) free.push_back(i);
    FILE* output = fopen(argv[1], "wb");
    if (!output) return 2;
    uint32_t solutions = uint32_t(free.size())+1;
    if (!write32(output, n) || !write32(output, solutions)) return 2;
    for (uint32_t k = 0; k < solutions; ++k) {
        std::vector<uint64_t> value(words);
        if (k) value[free[k-1]/64] = uint64_t(1) << (free[k-1] % 64);
        for (uint32_t pivot = 0; pivot < n; ++pivot) {
            if (basis[pivot].empty()) continue;
            int bit = 0;
            for (uint32_t j = 0; j <= pivot/64; ++j)
                bit ^= __builtin_parityll(value[j] & basis[pivot][j]);
            if (!k) bit ^= (basis[pivot][n/64] >> (n % 64)) & 1;
            value[pivot/64] ^= uint64_t(bit) << (pivot % 64);
        }
        if (!writerow(output, value)) return 2;
    }
    if (fclose(output)) return 2;
    printf("{\"status\":\"COMPLETE\",\"variables\":%u,\"rows\":%u,\"rank\":%u,\"nullity\":%zu}\n",
           n, count, rank, free.size());
}
