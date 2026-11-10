# STANDARD_LIBEXEC_PREFIX property frame — conditional native recipe, installed HOLD

The retained source supports **/usr/libexec/gcc/** as the native recipe candidate, with **/usr/libexec/gcc-cross/** as a concrete competing patched candidate. It does not establish the final installed initializer or qualify Q3. This property-specific witness began22:26:30UTC with a fixed22:41:30UTC stop. No execution, code/controller change or new source acquisition occurred.

## Phase linkage resolved from source

Top rules19–29 includes rules.defs/rules.patch, then invokes rules.conf and recursive rules2. rules.defs208–231 can set DEB_CROSS=yes for FORCE_CROSS_LAYOUT=yes even with equal triplets. Its native branch sets build_type but does not clear an externally supplied DEB_CROSS. rules.patch228–231 selects cross-install-location under that selector; the patch158–168 changes the exact STANDARD_LIBEXEC_PREFIX expression to gcc-cross/.

The newly read generator is precise: rules.conf1369–1418 writes version/SONAME/LIBC_DEP metadata only. It emits no DEB_CROSS/FORCE_CROSS_LAYOUT/PF/libexecdir/CXXFLAGS/CPPFLAGS. rules2 includes defs before parameters. Thus the generator introduces no direct layout assignment, but it is not an actual cross-phase selector record. The retained928B parameters says~24.04 without.1; configargs/driver metadata says~24.04.1. It cannot silently become the actual generated build-phase file. Regeneration or overriding values remain possible.

Both single_package branches ultimately set libexecdir=$(PF)/libexec; the earlier1060 assignment is overwritten by1061. PF defaults to usr but deliberately honors nonempty external input. Recorded --prefix=/usr and --libexecdir=/usr/libexec corroborate that recipe candidate. Phobos release checking plus --with-target-system-zlib=auto conditionally identifies DEB_CROSS!=yes at configure-time under the applicable unoverridden CONFARGS recipe. It does not by itself settle earlier patch selection.

Makefile.in635/2328–2345 passes libexecdir into DRIVER_DEFINES and CFLAGS-gcc.o. The object-specific -D precedes CXXFLAGS/INTERNAL_CFLAGS/@DEFS@ and later CPPFLAGS at compilation. rules2:80 clears only flags of origin exactly environment; command-line and make-e environment-override values are outside that filter. rules2 passes nonempty flags to configure and recursive native make. These are localized potential preservation/override surfaces, not evidence an override occurred. A whole finalgcc.o export is one sufficient artifact, not the sole acceptable engineering evidence.

## First indispensable gap and conditional conclusion

If actual patch/configure selector inputs are phase-consistent under the intended fresh recipe, the configure discriminator implies no cross-install-location patch. If the applied Makefile/property and later compile inputs preserve the definition, substitution gives /usr/libexec/gcc/. Those actual-phase and property-preservation premises are not established by the retained generator/parameters. The first STOP is therefore an exact-build property record linking patch/configure DEB_CROSS/origins/stamps, followed by the narrowly relevant definition-preservation evidence. No universal GCC or GNU conformance premise is adopted.

The unsigned buildinfo positively records parallel=4/noudeb/C.UTF-8 metadata; it is not a complete command-line/phase-origin record. Package/member/configure-text association remains useful partial provenance, not semantics. Independent input reviewv2 also preserves the separate documentary archive/body limitation: the no-decode records do not jointly certify compressed archive SHA and these two body hashes. No decode/listing was attempted to repair that limitation.

## Conditional future Q3 relation

Q3 does not expose the scalar. gcc.cc4697–4724 may relocate it; add_prefix3133 applies update_path; machine_suffix8314–8316 and ordered prefix nodes generate the reached programs string. If actual resolved executable directory equals configured/usr/bin, the applicable relocation helper returnsNULL, update_path is identity for the relevant GCC/BINUTILS components, and suffix fields are independently bound, the native candidate component is/usr/libexec/gcc/x86_64-linux-gnu/13/; cross prediction substitutes gcc-cross/.

Position matters: the configured branch5357–5362 adds GCC(require1), then BINUTILS(require2). Under identical transformations, their local emitted window has the machine-suffixed component twice, then the target-only component. Earlier prefix nodes and explicit-B priority blocks must be independently accounted; no global index or arbitrary matching substring is accepted. Changed identity/context, competing cross layout, unexpected transform/order/multiplicity, or ambiguous/truncated output rejects/holds the relation. A match would be finite corroboration, not initializer recovery or complete list/selection truth. Exit0/EOF still cannot establish intended emission completeness.

The selected exact prefix.cc and make-relative-prefix.c bodies are absent. Pro20's upstream comparison links are retained, but those bodies were not fetched/read or promoted to Ubuntu-applied correspondence here. That helper/installed binding remains explicit. PROPERTY-FRAME-v1.json contains the full phase matrix, premises, known-vs-unknown classification and exact next dependency; SOURCE-PINS-v1.json pins the named retained inputs.

Full C05/full V03/field qualification remain false,43.5 and zero added original credit unchanged, canonical recorded98.950533479seconds preserved, physical costs OPEN_NOT_ZERO. All old units remain closed; no query, assurance waiver, budget reset or runtime modification follows.
