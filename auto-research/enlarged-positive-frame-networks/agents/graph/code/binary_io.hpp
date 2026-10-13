// Copyright 2026 icekylinx. Apache-2.0; written with AI assistance.
// The on-disk arrays are little endian, regardless of the host architecture.
#pragma once
#include <stdexcept>
#include <type_traits>

inline unsigned popcount64(uint64_t value) {
    unsigned count = 0;
    while (value) { value &= value-1; ++count; }
    return count;
}

inline bool little_endian() {
    const uint16_t one = 1;
    return *reinterpret_cast<const uint8_t*>(&one) == 1;
}
template<class T> void normalize_le(T& value) {
    static_assert(std::is_integral<T>::value, "integer array required");
    if (!little_endian()) {
        auto p = reinterpret_cast<uint8_t*>(&value);
        std::reverse(p, p + sizeof(T));
    }
}
template<class T, size_t N> void normalize_le(std::array<T,N>& row) {
    for (auto& value : row) normalize_le(value);
}
template<class T> void readv(std::ifstream& f, std::vector<T>& values) {
    f.read(reinterpret_cast<char*>(values.data()), values.size()*sizeof(T));
    if (!f) throw std::runtime_error("Truncated producer array");
    if (!little_endian()) for (auto& value : values) normalize_le(value);
}
template<class T, size_t N> void read_array(std::ifstream& f, T (&values)[N]) {
    f.read(reinterpret_cast<char*>(values), sizeof(values));
    if (!f) throw std::runtime_error("Truncated producer header");
    for (auto& value : values) normalize_le(value);
}
template<class T, size_t N> void write_array(std::ofstream& f, const T (&values)[N]) {
    for (auto value : values) {
        normalize_le(value);
        f.write(reinterpret_cast<const char*>(&value), sizeof(T));
    }
    if (!f) throw std::runtime_error("Cannot write producer array");
}
