// Ross Richardson / OpenAI Codex, adapted by Philipp / mightyOil with Codex.
// Apache-2.0. PR1216's bit-packed BFS, extended with an independent middle-gate
// meet and explicit target permutation. No ternary row tables are imported.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
using Key = unsigned __int128;
struct Hash {
  std::size_t operator()(Key k) const {
    auto lo=static_cast<std::uint64_t>(k), hi=static_cast<std::uint64_t>(k>>64);
    return std::hash<std::uint64_t>{}(lo ^ (hi*0x9e3779b97f4a7c15ULL));
  }
};
int coefficient(Key key,int n,int row,int column) {
  return (key >> (2*(row*n+column))) & 3;
}
Key change(Key key,int n,int target,int source,int sign) {
  Key result=key;
  for(int column=0;column<n;++column) {
    const int a=coefficient(key,n,target,column), b=coefficient(key,n,source,column);
    const int value=target==source ? (3-a)%3 : (a+sign*b+3)%3;
    const int shift=2*(target*n+column);
    result=(result & ~(Key(3)<<shift)) | (Key(value)<<shift);
  }
  return result;
}
int main(int argc,char**argv) {
  try {
    if(argc!=5) throw std::runtime_error("usage: packed N PERM BALL REPORT");
    const int n=std::stoi(argv[1]);
    if(n<2 || n>6) throw std::runtime_error("dimension 2..6 required");
    std::string permutation(argv[2]);
    if(int(permutation.size())!=n) throw std::runtime_error("permutation length");
    std::vector<int> p(n),negative(n),seen(n);
    for(int i=0;i<n;++i) {
      negative[i]=permutation[i]>='a' && permutation[i]<='f';
      p[i]=permutation[i]-(negative[i]?'a':'0');
      if(p[i]<0 || p[i]>=n || seen[p[i]]++) throw std::runtime_error("permutation");
    }
    Key identity=0;
    for(int i=0;i<n;++i) identity |= Key(1) << (2*(i*n+i));
    std::unordered_map<Key,unsigned char,Hash> distance;
    distance.reserve(n==6?2500000:600000);
    distance.emplace(identity,0);
    std::vector<Key> queue{identity};
    std::array<std::uint64_t,5> layers{1,0,0,0,0};
    for(std::size_t cursor=0;cursor<queue.size();++cursor) {
      Key state=queue[cursor]; const int depth=distance.at(state);
      if(depth==4) continue;
      for(int s=n-1;s>=0;--s) for(int t=n-1;t>=0;--t) for(int sign:{1,-1}) {
        if(s==t && sign==1) continue;
        Key next=change(state,n,t,s,sign);
        if(distance.emplace(next,depth+1).second) {queue.push_back(next);++layers[depth+1];}
      }
    }
    std::uint64_t transitions=0,direct_hits=0,middle_hits=0;
    int minimum=99;
    for(Key state:queue) {
      // Explicit multiplication A P: old column c goes to column p[c].
      Key transformed=0;
      for(int r=0;r<n;++r) for(int c=0;c<n;++c) {
        int value=coefficient(state,n,r,c);
        if(negative[c]) value=(3-value)%3;
        transformed |= Key(value) << (2*(r*n+p[c]));
      }
      auto found=distance.find(transformed);
      if(found!=distance.end()) {
        ++direct_hits; minimum=std::min(minimum,int(distance.at(state))+int(found->second));
      }
      for(int s=n-1;s>=0;--s) for(int t=n-1;t>=0;--t) for(int sign:{1,-1}) {
        if(s==t && sign==1) continue;
        ++transitions;
        found=distance.find(change(transformed,n,t,s,sign));
        if(found!=distance.end()) {
          ++middle_hits; minimum=std::min(minimum,int(distance.at(state))+1+int(found->second));
        }
      }
    }
    std::vector<std::pair<std::uint64_t,unsigned char>> ordered;
    ordered.reserve(distance.size());
    for(const auto& entry:distance) {
      std::uint64_t ternary=0,place=1;
      for(int r=0;r<n;++r) for(int c=0;c<n;++c) {
        ternary+=place*coefficient(entry.first,n,r,c);place*=3;
      }
      ordered.emplace_back(ternary,entry.second);
    }
    std::sort(ordered.begin(),ordered.end());
    std::ofstream ball(argv[3],std::ios::binary);
    if(!ball) throw std::runtime_error("ball open");
    for(auto entry:ordered) {
      for(int i=0;i<8;++i) ball.put(char((entry.first>>(8*i))&255));
      ball.put(char(entry.second));
    }
    ball.close(); if(!ball) throw std::runtime_error("ball write");
    std::ofstream out(argv[4]);
    if(!out) throw std::runtime_error("report open");
    out<<"{\"n\":"<<n<<",\"permutation\":\""<<permutation<<"\",\"layers\":[";
    for(int i=0;i<5;++i) out<<(i?",":"")<<layers[i];
    out<<"],\"states\":"<<queue.size()<<",\"generators\":"<<n*(2*n-1)
       <<",\"transitions\":"<<transitions<<",\"direct_hits\":"<<direct_hits
       <<",\"middle_hits\":"<<middle_hits<<",\"minimum_through_nine\":";
    if(minimum==99) out<<"null"; else out<<minimum;
    out<<"}\n"; out.close(); if(!out) throw std::runtime_error("report write");
    std::cout<<"PASS_PACKED n="<<n<<" states="<<queue.size()<<" transitions="<<transitions<<'\n';
    return 0;
  } catch(const std::exception& error) {
    std::cerr<<error.what()<<'\n';return 1;
  }
}
