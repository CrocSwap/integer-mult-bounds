// Canonical rational target-span classes for the certified ternary producer.
// Every input row is a five-set indicator in Q^h, h<=28. Hadamard bounds
// every square minor by 5^14 < P. Hence reduction preserves the ranks of
// A, B, and [A;B], and modular row spaces agree iff rational row spaces do.
// Hashing selects buckets only; complete canonical tuples are compared.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <stdexcept>
#include <unordered_map>
#include <vector>
using U=uint32_t;using W=uint64_t;
constexpr W P=(W(1)<<61)-1;
U word(std::ifstream& f){U x;f.read(reinterpret_cast<char*>(&x),4);if(!f)throw std::runtime_error("Short input");return x;}
template<class T>std::vector<T> words(std::ifstream& f,size_t n){std::vector<T>x(n);f.read(reinterpret_cast<char*>(x.data()),sizeof(T)*n);if(!f)throw std::runtime_error("Short vector");return x;}
W product(W a,W b){__uint128_t x=__uint128_t(a)*b;W r=W(x&P)+W(x>>61);r=(r&P)+(r>>61);return r>=P?r-P:r;}
W inverse(W a){
  if(a==1||a==P-1)return a;
  static std::unordered_map<W,W> cache;auto found=cache.find(a);if(found!=cache.end())return found->second;
  W r=1,b=a;for(W n=P-2;n;n>>=1,b=product(b,b))if(n&1)r=product(r,b);
  cache.emplace(a,r);return r;
}
struct Span {
  U h,limit;std::vector<std::array<W,28>> rows;std::vector<U> pivots;
  Span(U ground,U bound):h(ground),limit(bound){}
  void add(U mask){
    if(rows.size()==limit)return;
    std::array<W,28> row{};for(U j=0;j<h;j++)row[j]=(mask>>j)&1;
    for(U i=0;i<rows.size();i++)if(W a=row[pivots[i]])
      for(U j=pivots[i];j<h;j++){W b=product(a,rows[i][j]);row[j]=row[j]>=b?row[j]-b:row[j]+P-b;}
    U pivot=0;while(pivot<h&&!row[pivot])pivot++;if(pivot==h)return;
    W scale=inverse(row[pivot]);for(U j=pivot;j<h;j++)row[j]=product(row[j],scale);
    for(auto&old:rows)if(W a=old[pivot])for(U j=pivot;j<h;j++){W b=product(a,row[j]);old[j]=old[j]>=b?old[j]-b:old[j]+P-b;}
    U at=std::lower_bound(pivots.begin(),pivots.end(),pivot)-pivots.begin();
    pivots.insert(pivots.begin()+at,pivot);rows.insert(rows.begin()+at,row);
  }
  std::vector<W> key()const{std::vector<W>out;out.reserve(rows.size()*h);for(const auto&row:rows)out.insert(out.end(),row.begin(),row.begin()+h);return out;}
};
struct ZNode{U var,lo,hi,count,core;};
void enumerate(const std::vector<ZNode>&z,U at,U mask,Span&span,uint64_t&leaves){
  if(!at||span.rows.size()==span.limit)return;
  if(at==1){span.add(mask);leaves++;return;}
  auto n=z[at];enumerate(z,n.lo,mask,span,leaves);enumerate(z,n.hi,mask|(U(1)<<n.var),span,leaves);
}
struct Hash{size_t operator()(const std::vector<W>&key)const{W h=0x84222325cbf29ce4ULL;for(W x:key){h^=x+0x9e3779b97f4a7c15ULL+(h<<6)+(h>>2);}return h;}};
int main(int argc,char**argv){
  if(argc!=4)return 2;auto start=std::chrono::steady_clock::now();
  std::ifstream f(argv[1],std::ios::binary),t(argv[2],std::ios::binary);
  U h=word(f),v=word(f),n=word(f),q=word(f);if(h>28)throw std::runtime_error("Dimension exceeds minor bound");
  f.seekg(8*uint64_t(n)+4*uint64_t(q),std::ios::cur);auto active=words<uint8_t>(f,n);auto core=words<U>(f,n);
  U th=word(t),tn=word(t),nz=word(t);if(th!=h||tn!=n)throw std::runtime_error("Target export mismatch");
  auto z=words<ZNode>(t,nz);auto reach=words<U>(t,n);auto delayed=words<uint8_t>(t,n);
  std::vector<U> united(nz),classes(nz),labels(n);
  for(U i=2;i<nz;i++){if(z[i].lo>=i||z[i].hi>=i)throw std::runtime_error("Non-topological ZDD");united[i]=united[z[i].lo]|united[z[i].hi]|(U(1)<<z[i].var);}
  std::vector<U> families;
  for(U i=1;i<n;i++)if(active[i]&&__builtin_popcount(core[i])<2&&!delayed[i]){
    U r=reach[i];if(!r)throw std::runtime_error("Missing target family");if(!classes[r]){classes[r]=1;families.push_back(r);}
  }
  auto signature=[&](U r)->W{return (W(z[r].core)<<h)|united[r];};
  std::sort(families.begin(),families.end(),[&](U a,U b){return signature(a)==signature(b)?a<b:signature(a)<signature(b);});
  U next_class=0;uint64_t leaves=0,multi_buckets=0,canonicalized=0;std::map<U,uint64_t> ranks;
  for(size_t begin=0;begin<families.size();){
    size_t end=begin+1;while(end<families.size()&&signature(families[end])==signature(families[begin]))end++;
    if(end==begin+1)classes[families[begin]]=++next_class;
    else{
      multi_buckets++;std::unordered_map<std::vector<W>,U,Hash> known;
      for(size_t j=begin;j<end;j++){
        U r=families[j],vary=__builtin_popcount(united[r])-__builtin_popcount(z[r].core);
        U bound=std::min(z[r].count,vary?vary:1);Span span(h,bound);enumerate(z,r,0,span,leaves);
        auto key=span.key();auto found=known.find(key);
        if(found==known.end()){U id=++next_class;known.emplace(std::move(key),id);classes[r]=id;}else classes[r]=found->second;
        ranks[span.rows.size()]++;canonicalized++;
      }
    }
    begin=end;
    if(begin%10000<end-begin)std::cerr<<"classified "<<begin<<"/"<<families.size()<<" target families\n";
  }
  U dual_classes=next_class;uint64_t source_nodes=0,dual_nodes=0;
  for(U i=1;i<n;i++)if(active[i]){
    if(__builtin_popcount(core[i])<2&&!delayed[i]){labels[i]=classes[reach[i]];dual_nodes++;}
    else{labels[i]=++next_class;source_nodes++;}
  }
  std::ofstream out(argv[3],std::ios::binary);out.write(reinterpret_cast<char*>(labels.data()),4*uint64_t(n));
  double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  std::cout<<"{\"status\":\"EXACT RATIONAL DUAL-TARGET SPAN CLASSES\",\"h\":"<<h
    <<",\"prime\":"<<P<<",\"source_nodes_left_singleton\":"<<source_nodes<<",\"dual_nodes\":"<<dual_nodes
    <<",\"target_families\":"<<families.size()<<",\"rational_span_classes\":"<<dual_classes
    <<",\"family_classes_merged\":"<<families.size()-dual_classes<<",\"multi_signature_buckets\":"<<multi_buckets
    <<",\"canonicalized_families\":"<<canonicalized<<",\"enumerated_original_rows\":"<<leaves
    <<",\"total_classes\":"<<next_class<<",\"rank_histogram\":{";
  bool first=true;for(auto[r,c]:ranks){if(!first)std::cout<<',';first=false;std::cout<<'"'<<r<<"\":"<<c;}
  std::cout<<"},\"seconds\":"<<seconds<<"}\n";
  return 0;
}
