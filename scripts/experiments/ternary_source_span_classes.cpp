// Refine the source side of an already certified source/dual frame partition.
// Equality is canonical modular RREF of original five-set incidence rows;
// the deterministic Hadamard proof is in ternary_target_span_classes.cpp.
#define main target_span_classes_main
#include "ternary_target_span_classes.cpp"
#undef main

void source_rows(const std::vector<std::pair<U,U>>&parents,const std::vector<U>&masks,
                 U at,U v,Span&span,uint64_t&leaves){
  if(span.rows.size()==span.limit)return;
  if(at<=v){span.add(masks[at]);leaves++;return;}
  source_rows(parents,masks,parents[at].first,v,span,leaves);
  source_rows(parents,masks,parents[at].second,v,span,leaves);
}
int main(int argc,char**argv){
  if(argc!=5)return 2;auto start=std::chrono::steady_clock::now();
  std::ifstream f(argv[1],std::ios::binary),t(argv[2],std::ios::binary),old(argv[3],std::ios::binary);
  U h=word(f),v=word(f),n=word(f),q=word(f);if(h>28)throw std::runtime_error("Dimension exceeds minor bound");
  auto parents=words<std::pair<U,U>>(f,n);f.seekg(4*uint64_t(q),std::ios::cur);
  auto active=words<uint8_t>(f,n);auto core=words<U>(f,n);auto labels=words<U>(old,n);
  U th=word(t),tn=word(t),nz=word(t);if(th!=h||tn!=n)throw std::runtime_error("Target export mismatch");
  t.seekg(20*uint64_t(nz)+4*uint64_t(n),std::ios::cur);auto delayed=words<uint8_t>(t,n);
  std::vector<U> masks(1,0),united(n),nodes;
  for(U a=0;a<h;a++)for(U b=a+1;b<h;b++)for(U c=b+1;c<h;c++)for(U d=c+1;d<h;d++)for(U e=d+1;e<h;e++)
    masks.push_back((U(1)<<a)|(U(1)<<b)|(U(1)<<c)|(U(1)<<d)|(U(1)<<e));
  if(masks.size()!=v+1)throw std::runtime_error("Source enumeration mismatch");
  U next_class=0;
  for(U i=1;i<n;i++)if(active[i]){
    united[i]=i<=v?masks[i]:united[parents[i].first]|united[parents[i].second];
    if(__builtin_popcount(core[i])>=2||delayed[i])nodes.push_back(i);
    else next_class=std::max(next_class,labels[i]);
  }
  U dual_classes=next_class;
  auto signature=[&](U i)->W{return(W(core[i])<<h)|united[i];};
  std::sort(nodes.begin(),nodes.end(),[&](U a,U b){return signature(a)==signature(b)?a<b:signature(a)<signature(b);});
  uint64_t leaves=0,multi_buckets=0,canonicalized=0,done=0;std::map<U,uint64_t> ranks,merged_by_core;
  for(size_t begin=0;begin<nodes.size();){
    size_t end=begin+1;while(end<nodes.size()&&signature(nodes[end])==signature(nodes[begin]))end++;
    if(end==begin+1)labels[nodes[begin]]=++next_class;
    else{
      multi_buckets++;std::unordered_map<std::vector<W>,U,Hash> known;
      for(size_t j=begin;j<end;j++){
        U at=nodes[j],vary=__builtin_popcount(united[at])-__builtin_popcount(core[at]);
        Span span(h,vary?vary:1);source_rows(parents,masks,at,v,span,leaves);
        auto key=span.key();auto found=known.find(key);
        if(found==known.end()){U id=++next_class;known.emplace(std::move(key),id);labels[at]=id;}
        else{labels[at]=found->second;merged_by_core[__builtin_popcount(core[at])]++;}
        ranks[span.rows.size()]++;canonicalized++;
      }
    }
    begin=end;
    if(begin/500000>done){done=begin/500000;std::cerr<<"classified "<<begin<<"/"<<nodes.size()<<" source nodes\n";}
  }
  std::ofstream out(argv[4],std::ios::binary);out.write(reinterpret_cast<char*>(labels.data()),4*uint64_t(n));
  double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  std::cout<<"{\"status\":\"EXACT RATIONAL SOURCE-SPAN CLASSES\",\"h\":"<<h
    <<",\"prime\":"<<P<<",\"source_nodes\":"<<nodes.size()<<",\"source_span_classes\":"<<next_class-dual_classes
    <<",\"source_nodes_merged\":"<<nodes.size()-(next_class-dual_classes)<<",\"multi_signature_buckets\":"<<multi_buckets
    <<",\"canonicalized_nodes\":"<<canonicalized<<",\"enumerated_original_rows\":"<<leaves
    <<",\"total_classes\":"<<next_class<<",\"merged_by_core\":{";
  bool first=true;for(auto[k,c]:merged_by_core){if(!first)std::cout<<',';first=false;std::cout<<'"'<<k<<"\":"<<c;}
  std::cout<<"},\"rank_histogram\":{";first=true;
  for(auto[r,c]:ranks){if(!first)std::cout<<',';first=false;std::cout<<'"'<<r<<"\":"<<c;}
  std::cout<<"},\"seconds\":"<<seconds<<"}\n";
}
