// Extract exact four-point-star boundaries from a certified five-set DAG.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <unordered_map>
#include <vector>
using U=uint32_t;
U read(std::ifstream& f){U x;f.read(reinterpret_cast<char*>(&x),4);if(!f)throw std::runtime_error("Truncated DAG");return x;}
int main(int argc,char**argv){
  if(argc!=3&&argc!=5)return 2;
  std::ifstream f(argv[1],std::ios::binary);
  U h=read(f),v=read(f),n=read(f),q=read(f);
  if(h>31||h<8)throw std::runtime_error("Unsupported ground size");
  std::vector<std::pair<U,U>> parents(n);f.read(reinterpret_cast<char*>(parents.data()),8*n);
  std::vector<U> roots(q);f.read(reinterpret_cast<char*>(roots.data()),4*q);
  std::vector<uint8_t> active(n);f.read(reinterpret_cast<char*>(active.data()),n);
  std::vector<U> cores(n),unions(n);f.read(reinterpret_cast<char*>(cores.data()),4*n);
  if(!f)throw std::runtime_error("Missing exact source cores");
  U input=0;
  for(U a=0;a<h;a++)for(U b=a+1;b<h;b++)for(U c=b+1;c<h;c++)for(U d=c+1;d<h;d++)for(U e=d+1;e<h;e++){
    U mask=(1U<<a)|(1U<<b)|(1U<<c)|(1U<<d)|(1U<<e);
    if(++input>v||cores[input]!=mask)throw std::runtime_error("Input order/core mismatch");
    unions[input]=mask;
  }
  if(input!=v)throw std::runtime_error("Wrong number of inputs");
  std::map<U,U> sizes;std::map<U,std::set<U>> demands;
  uint64_t additions=0;
  for(U node=v+1;node<n;node++){
    auto [a,b]=parents[node];
    if(!a||!b||a>=node||b>=node)throw std::runtime_error("Non-topological addition");
    if(cores[node]!=(cores[a]&cores[b]))throw std::runtime_error("Incorrect source core");
    unions[node]=unions[a]|unions[b];
    if(!active[node])continue;
    if(!active[a]||!active[b])throw std::runtime_error("Active graph not ancestor-closed");
    additions++;
    if(__builtin_popcount(cores[node])==4){
      sizes[cores[node]]++;
      // Within a star the varying fifth point identifies every source exactly.
      if((unions[a]&~cores[node])&(unions[b]&~cores[node]))throw std::runtime_error("Overlapping star supports");
    }
    for(U parent:{a,b})if(__builtin_popcount(cores[parent])==4&&cores[parent]!=cores[node])
      demands[cores[parent]].insert(unions[parent]&~cores[parent]);
  }
  for(U node:roots){
    if(node>=n||!active[node])throw std::runtime_error("Inactive output");
    if(__builtin_popcount(cores[node])==4)demands[cores[node]].insert(unions[node]&~cores[node]);
  }
  if(sizes.size()!=demands.size())throw std::runtime_error("Star without boundary");
  std::ofstream out(argv[2]);uint64_t old=0,boundary=0;
  for(auto [core,size]:sizes){
    old+=size;out<<core<<' '<<size;
    for(U mask:demands.at(core)){out<<' '<<mask;boundary++;}out<<'\n';
  }
  if(!out)throw std::runtime_error("Could not write boundaries");
  uint64_t rewritten_additions=additions;
  if(argc==5){
    std::ifstream tf(argv[3],std::ios::binary);
    if(read(tf)!=h)throw std::runtime_error("Wrong template ground size");
    U nt=read(tf);
    std::vector<std::pair<U,U>> np(v+1,{0,0});
    std::vector<U> nc(cores.begin(),cores.begin()+v+1),mapping(n);
    std::unordered_map<U,U> input_index;
    for(U node=1;node<=v;node++){mapping[node]=node;input_index.emplace(cores[node],node);}
    std::map<U,std::unordered_map<U,U>> replacements;
    for(U t=0;t<nt;t++){
      U core=read(tf),count=read(tf),ng=read(tf);
      std::set<U> targets;
      for(U j=0;j<count;j++)targets.insert(read(tf));
      if(!demands.count(core)||targets!=demands.at(core)||replacements.count(core)||ng>=sizes.at(core))
        throw std::runtime_error("Replacement boundary or saving mismatch");
      auto& values=replacements[core];
      for(U j=0;j<h;j++)if(!(core>>j&1))values.emplace(1U<<j,input_index.at(core|(1U<<j)));
      for(U j=0;j<ng;j++){
        U a=read(tf),b=read(tf);
        if(!a||!b||(a&b)||!values.count(a)||!values.count(b)||values.count(a|b))
          throw std::runtime_error("Invalid disjoint replacement");
        U id=np.size();np.emplace_back(values.at(a),values.at(b));nc.push_back(core);values.emplace(a|b,id);
      }
      for(U mask:targets)if(!values.count(mask))throw std::runtime_error("Missing replacement output");
    }
    for(U node=v+1;node<n;node++)if(active[node]){
      auto found=replacements.find(cores[node]);
      if(found!=replacements.end()){
        auto value=found->second.find(unions[node]&~cores[node]);
        if(value!=found->second.end())mapping[node]=value->second;
      }else{
        auto [a,b]=parents[node];a=mapping[a];b=mapping[b];
        if(!a||!b)throw std::runtime_error("Unrepresented external star use");
        mapping[node]=np.size();np.emplace_back(a,b);nc.push_back(cores[node]);
      }
    }
    std::vector<U> nr;for(U node:roots){if(!mapping[node])throw std::runtime_error("Missing rewritten output");nr.push_back(mapping[node]);}
    std::vector<uint8_t> used(np.size());std::vector<U> stack(nr);rewritten_additions=0;
    while(!stack.empty()){
      U node=stack.back();stack.pop_back();if(used[node])continue;used[node]=1;
      if(node>v){rewritten_additions++;stack.push_back(np[node].first);stack.push_back(np[node].second);}
    }
    for(U node=1;node<=v;node++)if(!used[node])throw std::runtime_error("Rewritten producer drops an input");
    std::ofstream dump(argv[4],std::ios::binary);U nn=np.size();
    for(U word:{h,v,nn,q})dump.write(reinterpret_cast<char*>(&word),4);
    dump.write(reinterpret_cast<char*>(np.data()),8*np.size());
    dump.write(reinterpret_cast<char*>(nr.data()),4*nr.size());
    dump.write(reinterpret_cast<char*>(used.data()),used.size());
    dump.write(reinterpret_cast<char*>(nc.data()),4*nc.size());
    if(!dump)throw std::runtime_error("Could not write rewritten DAG");
  }
  std::cout<<"{\"h\":"<<h<<",\"inputs\":"<<v<<",\"outputs\":"<<q
    <<",\"additions\":"<<additions<<",\"stars\":"<<sizes.size()
    <<",\"old_star_additions\":"<<old<<",\"boundary_sums\":"<<boundary
    <<",\"rewritten_additions\":"<<rewritten_additions<<"}\n";
}
