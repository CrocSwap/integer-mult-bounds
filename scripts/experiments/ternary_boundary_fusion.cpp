// Exact F3 boundary ranks for an externally certified common-frame partition.
// The partition must identify equal frames and have an acyclic quotient.
// Inputs: exact producer DAG, then one uint32 class ID per DAG node.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <unordered_map>
#include <vector>
using U = uint32_t;
using W = uint64_t;
U word(std::ifstream& f) { U x; f.read(reinterpret_cast<char*>(&x),4); if(!f) throw std::runtime_error("Short input"); return x; }
template<class T> std::vector<T> words(std::ifstream& f,size_t n) {
  std::vector<T> x(n);f.read(reinterpret_cast<char*>(x.data()),sizeof(T)*n);
  if(!f)throw std::runtime_error("Short vector");return x;
}
struct Row {std::vector<W> one,two; explicit Row(size_t blocks=0):one(blocks),two(blocks){} };
void subtract(Row& x,const Row& y,U factor) {
  for(size_t k=0;k<x.one.size();k++) {
    W a=x.one[k],b=x.two[k],c=factor==1?y.two[k]:y.one[k],d=factor==1?y.one[k]:y.two[k];
    W aa=a|b,bb=c|d;
    x.one[k]=(c&~aa)|(a&~bb)|(b&d);
    x.two[k]=(d&~aa)|(b&~bb)|(a&c);
  }
}
U rank(std::vector<std::vector<W>>& values,const std::vector<U>& output,size_t p) {
  size_t blocks=(p+63)/64;std::vector<int> where(p,-1);std::vector<Row> basis;
  for(U i:output) {
    Row row(blocks);row.one=values[i];
    while(true) {
      size_t k=0;while(k<blocks&&!(row.one[k]|row.two[k]))k++;
      if(k==blocks)break;
      U pivot=U(k*64+__builtin_ctzll(row.one[k]|row.two[k]));
      U factor=(row.one[k]>>(pivot%64))&1?1:2;
      if(where[pivot]<0) {
        if(factor==2)std::swap(row.one,row.two);
        where[pivot]=int(basis.size());basis.push_back(std::move(row));break;
      }
      subtract(row,basis[where[pivot]],factor);
    }
  }
  return basis.size();
}
int main(int argc,char**argv) {
  if(argc!=3)return 2;
  auto started=std::chrono::steady_clock::now();std::ifstream f(argv[1],std::ios::binary),g(argv[2],std::ios::binary);
  U h=word(f),v=word(f),n=word(f),q=word(f);
  auto parents=words<std::pair<U,U>>(f,n);auto roots=words<U>(f,q);auto active=words<uint8_t>(f,n);auto labels=words<U>(g,n);
  U nc=*std::max_element(labels.begin(),labels.end())+1;
  std::vector<U> head(nc),next(n),sizes(nc),uses(n);
  uint64_t active_nodes=0,additions=0,classes=0,merged_classes=0;
  U max_nodes=0;
  for(U i=n;i-->1;)if(active[i]) {
    if(!labels[i]||labels[i]>=0x80000000U)throw std::runtime_error("Bad class ID");
    U cl=labels[i];next[i]=head[cl];head[cl]=i;sizes[cl]++;active_nodes++;additions+=i>v;
  }
  for(U cl=1;cl<nc;cl++)if(sizes[cl]){classes++;merged_classes+=sizes[cl]>1;max_nodes=std::max(max_nodes,sizes[cl]);}
  std::vector<W> ports;ports.reserve(2*additions+q);
  for(U i=1;i<n;i++)if(active[i]&&i>v)for(U a:{parents[i].first,parents[i].second}) {
    if(!a||a>=i||!active[a])throw std::runtime_error("Bad active DAG edge");
    if(labels[a]!=labels[i])ports.push_back((W(a)<<32)|labels[i]);
  }
  for(U i=0;i<q;i++)ports.push_back((W(roots[i])<<32)|(0x80000000U+i));
  std::sort(ports.begin(),ports.end());ports.erase(std::unique(ports.begin(),ports.end()),ports.end());
  for(W port:ports)uses[port>>32]++;
  uint64_t boundary_ports=ports.size();std::vector<W>().swap(ports);
  uint64_t rank_sum=classes-merged_classes,done=0,merged_nodes=0;
  U max_inputs=0,max_outputs=0;std::map<U,uint64_t> rank_histogram;
  for(U cl=1;cl<nc;cl++)if(sizes[cl]>1) {
    std::vector<U> nodes,sources,output;
    for(U i=head[cl];i;i=next[i]) {
      nodes.push_back(i);if(i<=v)throw std::runtime_error("Merged class contains an input");
      for(U a:{parents[i].first,parents[i].second})if(labels[a]!=cl)sources.push_back(a);
    }
    std::sort(sources.begin(),sources.end());sources.erase(std::unique(sources.begin(),sources.end()),sources.end());
    max_inputs=std::max(max_inputs,U(sources.size()));merged_nodes+=nodes.size();
    size_t p=sources.size(),blocks=(p+63)/64;
    std::unordered_map<U,U> local;local.reserve(sources.size()+nodes.size());
    std::vector<std::vector<W>> values;values.reserve(sources.size()+nodes.size());
    for(U i=0;i<p;i++){local.emplace(sources[i],i);values.emplace_back(blocks);values.back()[i/64]|=W(1)<<(i%64);}
    for(U node:nodes) {
      U a=local.at(parents[node].first),b=local.at(parents[node].second);
      U at=values.size();values.emplace_back(blocks);
      for(size_t k=0;k<blocks;k++) {
        if(values[a][k]&values[b][k])throw std::runtime_error("Local coefficient overlap");
        values[at][k]=values[a][k]|values[b][k];
      }
      local.emplace(node,at);if(uses[node])output.push_back(at);
    }
    if(output.empty())throw std::runtime_error("Empty boundary output");
    U r=rank(values,output,p);rank_sum+=r;rank_histogram[r]++;max_outputs=std::max(max_outputs,U(output.size()));
    if(++done%100000==0)std::cerr<<"ranked "<<done<<"/"<<merged_classes<<" merged classes\n";
  }
  uint64_t original_roles=additions+q,new_roles=v+boundary_ports-rank_sum;
  if(new_roles>original_roles)throw std::runtime_error("Fusion increased roles");
  double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();
  std::cout<<"{\"status\":\"EXACT F3 BOUNDARY RANKS; FRAME PARTITION CERTIFIED EXTERNALLY\",\"h\":"<<h
    <<",\"inputs\":"<<v<<",\"active_nodes\":"<<active_nodes<<",\"classes\":"<<classes
    <<",\"merged_classes\":"<<merged_classes<<",\"merged_nodes\":"<<merged_nodes
    <<",\"maximum_class_nodes\":"<<max_nodes<<",\"maximum_class_inputs\":"<<max_inputs
    <<",\"maximum_class_output_values\":"<<max_outputs<<",\"boundary_ports\":"<<boundary_ports
    <<",\"boundary_rank_sum\":"<<rank_sum<<",\"original_roles\":"<<original_roles
    <<",\"new_roles\":"<<new_roles<<",\"saving\":"<<original_roles-new_roles<<",\"rank_histogram\":{";
  bool first=true;for(auto [r,count]:rank_histogram){if(!first)std::cout<<',';first=false;std::cout<<'"'<<r<<"\":"<<count;}
  std::cout<<"},\"seconds\":"<<seconds<<"}\n";
}
