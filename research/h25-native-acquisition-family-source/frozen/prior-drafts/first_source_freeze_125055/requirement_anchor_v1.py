"""Source-fixed exact recipe and implemented-body anchors; no runtime admission."""
REQUIREMENTS_SHA256 = '87373f414997ff2f84a02945d249dbabcd840a3c059f267afa8f898937ea5d9f'
COMPONENT_ROOT_SHA256 = '111dbefd7bcc148232975a1fe0bd91ebcdf7dc6c3f630645eef1a64a939f0b03'
COMPONENT_VALIDATOR_SHA256 = '5efe853710a9f5022bcf5d18446820c3b51380568e04352794e9d1b165351de3'
FAMILY_COUNT = 212
CURRENT_UNITS = 86
BODYLESS_FAMILIES = 151
PARTIAL_FAMILIES = 61

OPERATIONAL_SOURCE_PINS = {'queue': '1348a7b4d7cc1f9fef556f5e0abdaf04411a998afdcd574d7812c76ab37dcf68', 'wrapper': 'ea4c07337ccc1865accfd1b1fe485d51057a04a49e4bfb5f10cc36dc92b5f9a8', 'supervisor': 'fdbfbaa2bc2836e1bad1199c99162db8f73ac1c17768e29a617e596fc1364521', 'runner': 'bd882e3dadb1b6aeaa63ee824f1a1c58f8ef2546b6840a2bffa46885a184d3eb', 'envelope': 'afb4f72c36bad015fdf23221a00a4730387a5e8df4999b14a4d1614ee135c84a', 'validator': '5efe853710a9f5022bcf5d18446820c3b51380568e04352794e9d1b165351de3'}
STAGE_ENTRY_SHA256 = '8462925a8e620a4dd56e60b6fe15663b10c7085da2c17f608a441ecc88c6417d'

# Additive source construction only. These three units do not complete C03.
# Original212 and original86 remain byte-for-byte unchanged.
NATIVE_ACQUISITION_EXTENSION = {'root_template_sha256': '2563779a2a385d86f012c45cb9cdba7837138899e0f0a62d7c173629a330a0e1', 'copy_template_sha256': 'b8303732ede41dd48aa767f2c40cbbff249f34e2621f532b5484d38a218a0f69', 'schema_template_sha256': 'b89a789654be87bde40a47300f4d9702dce2b90e6ab3be9a2025f6d8041b3e9a', 'units': {'epoch-v4/C03/native-enoent': {'body_sha256': 'e451f6fb13be5367de79089376f571e6bfe9a4a963b1f55360b6d2df9c99e872', 'error_type': 'builtins.FileNotFoundError', 'errno': 2, 'primary_phase': 'inspect'}, 'epoch-v4/C03/native-eexist': {'body_sha256': 'e451f6fb13be5367de79089376f571e6bfe9a4a963b1f55360b6d2df9c99e872', 'error_type': 'builtins.FileExistsError', 'errno': 17, 'primary_phase': 'write_once'}, 'epoch-v4/C03/native-eloop': {'body_sha256': 'e451f6fb13be5367de79089376f571e6bfe9a4a963b1f55360b6d2df9c99e872', 'error_type': 'builtins.OSError', 'errno': 40, 'primary_phase': 'inspect'}}}
