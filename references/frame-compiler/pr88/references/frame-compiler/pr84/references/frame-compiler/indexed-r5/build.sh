#!/bin/sh
set -eu
mkdir -p bin
c++ -O3 -std=c++17 -I references/frame-compiler/pr48/scripts/partial_swap scripts/experiments/profile_oracle.cpp -o bin/profile-oracle
c++ -O3 -std=c++17 -I references/frame-compiler/pr48/scripts/partial_swap scripts/experiments/binary_frame_profiles.cpp -o bin/profiles
