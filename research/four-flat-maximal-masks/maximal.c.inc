/* Apache-2.0. Tekalign, substantial OpenAI Codex assistance.
 * Input: distinct masks. Output: all inclusion-maximal masks, integer-sorted.
 * The caller retains its original sorted-deduplicated input construction.
 */
static int maximal_masks(const u128 *input, int count, u128 *output) {
  int sizes[129] = {0}, offsets[129], used[129] = {0};
  if (count < 0) { fprintf(stderr, "negative mask count\n"); exit(2); }
  if (!count) return 0;
  int *order = malloc(sizeof(*order) * (size_t)count);
  if (!order) { fprintf(stderr, "mask allocation failed\n"); exit(2); }
  for (int i = 0; i < count; i++) sizes[pc(input[i])]++;
  int pos = 0;
  for (int weight = 128; weight >= 0; weight--) {
    offsets[weight] = pos;
    pos += sizes[weight];
  }
  for (int i = 0; i < count; i++) {
    int weight = pc(input[i]);
    order[offsets[weight] + used[weight]++] = i;
  }
  int kept = 0;
  for (int weight = 128; weight >= 0; weight--) {
    /* Distinct masks of the same cardinality cannot strictly contain one
       another. Only maxima retained from larger-cardinality buckets matter. */
    int larger = kept;
    for (int j = 0; j < sizes[weight]; j++) {
      u128 mask = input[order[offsets[weight] + j]];
      int contained = 0;
      for (int k = 0; k < larger; k++) {
        if ((mask & output[k]) == mask) { contained = 1; break; }
      }
      if (!contained) output[kept++] = mask;
    }
  }
  free(order);
  qsort(output, (size_t)kept, sizeof(u128), cmp128);
  return kept;
}
