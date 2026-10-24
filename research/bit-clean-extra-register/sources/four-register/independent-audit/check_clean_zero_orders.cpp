// Check every order with dependence signatures, without a normal-form algorithm.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;

int product(int a, int b) {
    int result=0;
    for(int i=0;i<4;++i)for(int j=0;j<4;++j) {
        int bit=0;
        for(int k=0;k<4;++k)bit^=((a>>(4*i+k))&1)&((b>>(4*k+j))&1);
        result|=bit<<(4*i+j);
    }
    return result;
}

int outer(int x,int y) {
    int result=0;
    for(int i=0;i<4;++i)if((x>>i)&1)result|=y<<(4*i);
    return result;
}

int main(int argc,char**argv) {
    try {
        if(argc!=3)throw runtime_error("Need expected family metadata and binary words");
        vector<int> matrices;
        for(int i=0;i<3;++i) {
            int e=1<<i;
            matrices.push_back(outer(e,e));
            matrices.push_back(outer(e,e|8));
            matrices.push_back(outer(e|8,e));
        }
        matrices.push_back(outer(15,8));matrices.push_back(outer(8,15));
        vector<pair<int,int>> dependent;
        for(int i=0;i<11;++i)for(int j=i+1;j<11;++j)
            if(product(matrices[i],matrices[j])!=product(matrices[j],matrices[i]))dependent.emplace_back(i,j);
        vector<pair<int,int>> choices;
        for(int i=0;i<3;++i)for(int j=i;j<3;++j)choices.emplace_back(i,j);
        ifstream metadata(argv[1]), binary(argv[2],ios::binary);
        if(!metadata || !binary)throw runtime_error("Cannot open input");
        uint64_t raw=0,total=0,families=0;
        for(auto a:choices)for(auto b:choices)for(auto c:choices) {
            array<int,11> counts{};
            int family=0;
            for(auto pair:{a,b,c}) {
                ++counts[3*family+pair.first];++counts[3*family+pair.second];++family;
            }
            counts[9]=counts[10]=1;
            for(int n:counts) { int expected;metadata>>expected;if(!metadata || expected!=n)throw runtime_error("Family mismatch"); }
            uint64_t expected_raw,expected_offset,expected_orders;
            metadata>>expected_raw>>expected_offset>>expected_orders;
            if(!metadata || expected_offset!=total)throw runtime_error("Offset mismatch");
            vector<int> word;
            for(int i=0;i<11;++i)for(int j=0;j<counts[i];++j)word.push_back(i);
            unordered_map<string,uint32_t> minimum;
            uint64_t family_raw=0;
            do {
                uint32_t packed=0;
                for(int letter:word)packed=(packed<<4)|letter;
                string signature;
                for(auto [i,j]:dependent) {
                    unsigned char bits=0;
                    for(int letter:word)if(letter==i || letter==j)bits=(bits<<1)|(letter==j);
                    signature.push_back(char(bits));
                }
                auto [it,fresh]=minimum.emplace(signature,packed);
                if(!fresh && packed<it->second)it->second=packed;
                ++family_raw;
            }while(next_permutation(word.begin(),word.end()));
            if(family_raw!=expected_raw || minimum.size()!=expected_orders)throw runtime_error("Family order count mismatch");
            vector<uint32_t> representatives;
            for(auto &entry:minimum)representatives.push_back(entry.second);
            sort(representatives.begin(),representatives.end());
            for(uint32_t representative:representatives) {
                unsigned char record[16];
                if(!binary.read(reinterpret_cast<char*>(record),16))throw runtime_error("Binary input ended early");
                for(int i=0;i<8;++i) {
                    int letter=(representative>>(4*(7-i)))&15;
                    if(record[2*i]+256*record[2*i+1]!=matrices[letter])throw runtime_error("Binary word mismatch");
                }
            }
            raw+=family_raw;total+=minimum.size();++families;
        }
        int extra;if(metadata>>extra)throw runtime_error("Unused metadata");
        if(binary.peek()!=char_traits<char>::eof())throw runtime_error("Unused binary words");
        cout<<"{\"status\":\"PASS_INDEPENDENT_CLEAN_ZERO_ORDER_COVERAGE\",\"families\":"<<families
            <<",\"raw_orders\":"<<raw<<",\"commutation_orders\":"<<total
            <<",\"binary_word_stream_identical\":true,\"reversal_used\":false}\n";
    }catch(const exception&error){cerr<<error.what()<<'\n';return 1;}
}
