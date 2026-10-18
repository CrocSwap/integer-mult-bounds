#include "json.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
using J=nlohmann::json;
J read(const char*p){std::ifstream f(p);if(!f)throw std::runtime_error("missing result");J j;f>>j;return j;}
int main(int argc,char**argv){try{if(argc!=3)throw std::runtime_error("frozen-result FRESH FROZEN");J a=read(argv[1]),b=read(argv[2]);for(const char*k:{"status","kappa","bit_profile","complex_profile","ordinary_chain","a_bit","a_complex","assembly"})if(a.at(k)!=b.at(k))throw std::runtime_error(std::string("frozen result mismatch: ")+k);std::cout<<"PASS immutable complete exact result: "<<a.at("kappa")<<"\n";return 0;}catch(std::exception&e){std::cerr<<"FAIL "<<e.what()<<"\n";return 1;}}