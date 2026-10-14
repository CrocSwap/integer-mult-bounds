# Native arithmetic dependencies

Boost.Multiprecision 1.89.0 headers: official commit e0c112538ff1e903594d039f2eb97e0057737e5d at https://github.com/boostorg/multiprecision/tree/boost-1.89.0 .
Boost.Config 1.89.0 headers: official commit bf8c8bd7960cd8505210838f86bd28fb4fb71071 at https://github.com/boostorg/config/tree/boost-1.89.0 .
Both use the Boost Software License 1.0, preserved in BOOST-LICENSE-1.0.txt and the source headers.
The nlohmann single-header JSON library uses the MIT license, preserved in include/json.hpp. See its version and complete copyright/license header there.
These are unmodified upstream include trees, copied from pinned local downloads. They supply exact integer arithmetic and JSON parsing, not mathematical proof assumptions. Compile with -std=c++20 -O3 -I native-deps/include .
