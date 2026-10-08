// Exact target-family audit for the source-core/dual-target frame cut.
// Integer row elimination certifies the actual rational target span; a full
// modular Gram rank then proves that span nondegenerate over Q.
#define TERNARY_EXACT_SUPPORT
#define TERNARY_NO_MAIN
#include "ternary_target_fingerprint.cpp"
#include <algorithm>
#include <climits>
#include <map>
#include <numeric>
#include <unordered_set>

using I=long long;
using Big=__int128_t;
Big gcd_big(Big a,Big b){if(a<0)a=-a;if(b<0)b=-b;while(b){Big c=a%b;a=b;b=c;}return a;}
struct ExactSpan {
  U h;
  std::vector<std::pair<U,std::vector<I>>> rows;
  std::vector<U> selected;
  explicit ExactSpan(U ground):h(ground){}
  void add(U mask){
    std::vector<I> row(h);for(U j=0;j<h;j++)row[j]=(mask>>j)&1;
    for(const auto&entry:rows){
      U pivot=entry.first;const auto&b=entry.second;if(!row[pivot])continue;
      I factor=row[pivot],scale=b[pivot];std::vector<Big> next(h);Big divisor=0;
      for(U j=0;j<h;j++){next[j]=Big(scale)*row[j]-Big(factor)*b[j];divisor=gcd_big(divisor,next[j]);}
      if(!divisor)return;
      for(U j=0;j<h;j++){
        Big value=next[j]/divisor;if(value>LLONG_MAX||value<LLONG_MIN)throw std::runtime_error("Exact-span integer overflow");
        row[j]=I(value);
      }
    }
    U pivot=0;while(pivot<h&&!row[pivot])pivot++;if(pivot==h)return;
    I divisor=0;for(I x:row)divisor=std::gcd(divisor,x<0?-x:x);if(row[pivot]<0)divisor=-divisor;
    for(I&x:row)x/=divisor;
    rows.emplace_back(pivot,std::move(row));std::sort(rows.begin(),rows.end(),[](const auto&a,const auto&b){return a.first<b.first;});
    selected.push_back(mask);
  }
};
void enumerate(const ZDD&z,U root,U mask,ExactSpan&span){
  if(!root)return;if(root==1){span.add(mask);return;}auto n=z.nodes[root];
  enumerate(z,n.lo,mask,span);enumerate(z,n.hi,mask|(U(1)<<n.var),span);
}
uint64_t power(uint64_t a,uint64_t b,uint64_t p){uint64_t r=1;for(;b;b>>=1,a=a*a%p)if(b&1)r=r*a%p;return r;}
U gram_rank(const std::vector<U>& selected,U p){
  U n=selected.size();std::vector<std::vector<uint64_t>> a(n,std::vector<uint64_t>(n));
  for(U i=0;i<n;i++)for(U j=0;j<n;j++)a[i][j]=(p+__builtin_popcount(selected[i]&selected[j])-2)%p;
  U rank=0;
  for(U col=0;col<n&&rank<n;col++){
    U found=rank;while(found<n&&!a[found][col])found++;if(found==n)continue;std::swap(a[rank],a[found]);
    auto inverse=power(a[rank][col],p-2,p);for(U j=col;j<n;j++)a[rank][j]=a[rank][j]*inverse%p;
    for(U i=rank+1;i<n;i++)if(a[i][col]){auto factor=a[i][col];for(U j=col;j<n;j++)a[i][j]=(a[i][j]+p-factor*a[rank][j]%p)%p;}
    rank++;
  }
  return rank;
}
int main(int argc,char**argv){
  if(argc<2||argc>5)return 2;auto started=std::chrono::steady_clock::now();std::ifstream f(argv[1],std::ios::binary);
  U h=read(f),v=read(f),n=read(f),q=read(f);std::vector<std::pair<U,U>> parents(n);
  f.read(reinterpret_cast<char*>(parents.data()),8*n);auto roots=reads(f,q);std::vector<uint8_t> active(n);
  f.read(reinterpret_cast<char*>(active.data()),n);auto cores=reads(f,n);if(!f)throw std::runtime_error("Missing exact support cores");
  ZDD targets(h);std::vector<U> reachable(n,0);U target_index=0;
  for(U a=0;a<h;a++)for(U b=a+1;b<h;b++)for(U c=b+1;c<h;c++)for(U d=c+1;d<h;d++)for(U e=d+1;e<h;e++){
    U node=roots[target_index++];if(__builtin_popcount(cores[node])<2){
      U mask=(U(1)<<a)|(U(1)<<b)|(U(1)<<c)|(U(1)<<d)|(U(1)<<e);
      reachable[node]=targets.unite(reachable[node],targets.singleton(mask));
    }
  }
  if(target_index!=v)throw std::runtime_error("Target order mismatch");
  uint64_t cut_nodes=0,positive_source_nodes=0;
  for(U node=n;node-->1;){
    if(!active[node])continue;
    if(__builtin_popcount(cores[node])>=2){positive_source_nodes++;continue;}
    if(!reachable[node])throw std::runtime_error("Cut node has no side target");cut_nodes++;
    for(U parent:{parents[node].first,parents[node].second})if(parent&&__builtin_popcount(cores[parent])<2)
      reachable[parent]=targets.unite(reachable[parent],reachable[node]);
  }
  std::unordered_map<U,U> exceptional;uint64_t exception_nodes=0,positive_target_nodes=0;
  for(U node=1;node<n;node++)if(active[node]&&__builtin_popcount(cores[node])<2){
    if(__builtin_popcount(targets.nodes[reachable[node]].core)>=2)positive_target_nodes++;
    else {exception_nodes++;exceptional.emplace(reachable[node],node);}
  }
  std::cerr<<"cut nodes "<<cut_nodes<<" exception nodes "<<exception_nodes<<" unique families "<<exceptional.size()<<" target ZDD "<<targets.nodes.size()<<'\n';
  U maximum_cardinality=0;uint64_t enumerated=0;std::map<U,U> rank_counts;std::vector<std::pair<U,std::vector<U>>> unresolved;
  std::unordered_set<U> bad_families;size_t done=0;
  for(auto [family,node]:exceptional){
    ExactSpan span(h);enumerate(targets,family,0,span);U rank=span.selected.size();
    maximum_cardinality=std::max(maximum_cardinality,targets.nodes[family].count);enumerated+=targets.nodes[family].count;rank_counts[rank]++;
    if(gram_rank(span.selected,1000000007)!=rank&&gram_rank(span.selected,1000000009)!=rank){
      unresolved.emplace_back(node,span.selected);bad_families.insert(family);
    }
    if(++done%1000==0)std::cerr<<"checked "<<done<<"/"<<exceptional.size()<<" unresolved "<<unresolved.size()<<'\n';
  }
  if(argc>=3){
    std::ofstream out(argv[2]);for(auto&entry:unresolved){out<<entry.first;for(U mask:entry.second)out<<' '<<mask;out<<'\n';}
  }
  // Delay the source-to-dual cut past every unresolved dual frame. The new
  // source region is ancestor-closed, so every mixed edge still goes from an
  // actual source span into a reachable-target orthogonal complement.
  std::vector<uint8_t> delayed(n,0);uint64_t delayed_seed_nodes=0,delayed_nodes=0;
  for(U node=1;node<n;node++)if(active[node]&&bad_families.count(reachable[node])){
    delayed[node]=1;delayed_seed_nodes++;
  }
  for(U node=n;node-->1;)if(delayed[node]){
    delayed_nodes++;
    for(U parent:{parents[node].first,parents[node].second})if(parent&&__builtin_popcount(cores[parent])<2)delayed[parent]=1;
  }
  for(U node=1;node<n;node++)if(active[node]&&(__builtin_popcount(cores[node])>=2||delayed[node]))
    for(U parent:{parents[node].first,parents[node].second})if(parent&&__builtin_popcount(cores[parent])<2&&!delayed[parent])
      throw std::runtime_error("Repaired source region is not ancestor-closed");
  U center_index=v;
  for(U a=0;a<h;a++)for(U b=a+1;b<h;b++){
    U pair=(U(1)<<a)|(U(1)<<b);
    if((cores[roots[center_index++]]&pair)!=pair)throw std::runtime_error("Center leaves common-pair source region");
  }
  if(center_index!=q)throw std::runtime_error("Wrong retained-total count");
  std::cerr<<"delayed-cut seeds "<<delayed_seed_nodes<<" ancestor-closed source nodes "<<delayed_nodes<<'\n';
  std::vector<U> input_masks(1,0);
  for(U a=0;a<h;a++)for(U b=a+1;b<h;b++)for(U c=b+1;c<h;c++)for(U d=c+1;d<h;d++)for(U e=d+1;e<h;e++)
    input_masks.push_back((U(1)<<a)|(U(1)<<b)|(U(1)<<c)|(U(1)<<d)|(U(1)<<e));
  uint64_t source_leaves=0;std::map<U,U> delayed_rank_counts;
  std::vector<std::pair<U,std::vector<U>>> bad_sources;
  for(U node=1;node<n;node++)if(delayed[node]){
    ExactSpan span(h);std::vector<U> stack{node};
    while(!stack.empty()){
      U at=stack.back();stack.pop_back();
      if(at<=v){span.add(input_masks[at]);source_leaves++;}
      else {stack.push_back(parents[at].first);stack.push_back(parents[at].second);}
    }
    U rank=span.selected.size();delayed_rank_counts[rank]++;
    if(gram_rank(span.selected,1000000007)!=rank&&gram_rank(span.selected,1000000009)!=rank)bad_sources.emplace_back(node,span.selected);
  }
  if(argc>=3){std::ofstream out(std::string(argv[2])+".sources");for(auto&entry:bad_sources){out<<entry.first;for(U mask:entry.second)out<<' '<<mask;out<<'\n';}}
  if(argc>=4){
    std::ofstream out(argv[3],std::ios::binary);std::vector<U> classes(n,0);
    std::unordered_map<U,U> dual_classes;U next_class=0;
    for(U node=1;node<n;node++)if(active[node]){
      if(__builtin_popcount(cores[node])>=2||delayed[node])classes[node]=++next_class;
      else {auto [it,inserted]=dual_classes.emplace(reachable[node],0);if(inserted)it->second=++next_class;classes[node]=it->second;}
    }
    out.write(reinterpret_cast<const char*>(classes.data()),4*n);
    std::cerr<<"conservative label classes "<<next_class<<" distinct dual families "<<dual_classes.size()<<'\n';
  }
  if(argc==5){
    std::ofstream out(argv[4],std::ios::binary);U zn=targets.nodes.size();
    for(U word:{h,n,zn})out.write(reinterpret_cast<const char*>(&word),4);
    out.write(reinterpret_cast<const char*>(targets.nodes.data()),20*zn);
    out.write(reinterpret_cast<const char*>(reachable.data()),4*n);
    out.write(reinterpret_cast<const char*>(delayed.data()),n);
  }
  double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();
  std::cout<<"{\"status\":\"EXACT SOURCE-CORE / DUAL-TARGET FRAME AUDIT\",\"h\":"<<h
    <<",\"positive_source_nodes\":"<<positive_source_nodes<<",\"dual_nodes\":"<<cut_nodes
    <<",\"positive_target_nodes\":"<<positive_target_nodes<<",\"exceptional_nodes\":"<<exception_nodes
    <<",\"exceptional_target_families\":"<<exceptional.size()<<",\"target_zdd_nodes\":"<<targets.nodes.size()
    <<",\"enumerated_targets\":"<<enumerated<<",\"maximum_family_size\":"<<maximum_cardinality
    <<",\"unresolved_gram_families\":"<<unresolved.size()
    <<",\"delayed_seed_nodes\":"<<delayed_seed_nodes<<",\"delayed_source_nodes\":"<<delayed_nodes
    <<",\"delayed_source_leaves\":"<<source_leaves<<",\"unresolved_source_nodes\":"<<bad_sources.size()
    <<",\"every_final_frame_nondegenerate\":"<<(bad_sources.empty()?"true":"false")
    <<",\"source_region_ancestor_closed\":true,\"all_centers_in_source_region\":true"
    <<",\"rank_histogram\":{";
  bool first=true;for(auto [rank,count]:rank_counts){if(!first)std::cout<<',';first=false;std::cout<<'"'<<rank<<"\":"<<count;}
  std::cout<<"},\"delayed_source_rank_histogram\":{";first=true;
  for(auto [rank,count]:delayed_rank_counts){if(!first)std::cout<<',';first=false;std::cout<<'"'<<rank<<"\":"<<count;}
  std::cout<<"},\"seconds\":"<<elapsed<<"}\n";
  if(!bad_sources.empty())return 1;
}
