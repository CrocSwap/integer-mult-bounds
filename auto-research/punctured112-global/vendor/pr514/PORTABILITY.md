# Portable replay and browser uploads

No hidden file is required. MANIFEST.json binds every included file except itself. Each entry declares either exact raw-byte hashing (gzip and other binary inputs) or SHA-256 after converting CRLF to LF (recognized text files). This accepts only the platform newline distinction; it does not ignore whitespace, JSON values, source code or any other content. An omitted file or changed token still fails.

verify.py copies static work inputs into its new output directory, canonicalizes recognized text there, and creates an LF copy of the frozen asynchronous plan. Only those canonical copies enter runtime raw-byte template hashes. Each child executes through code/run_portable.py, which preserves argv, import path and working directory while forcing generated Path.write_text output to UTF-8/LF. Generated adapter JSON therefore has the same embedded hash on Windows and Linux.

Gzip transport bytes are manifest-bound. Newly generated gzip container headers can vary across Python versions; the expected final template hash binds decompressed canonical content instead. Mathematical input fields are checked independently. The normalized local word omits only two irrelevant inherited display floats and a checked redundant dimension field.

The package is tested locally with assertions enabled. Optimized Python is rejected. The final portability test changes every recognized package text file to CRLF and runs the complete verifier against the frozen expected result. This is a Windows line-ending test, not a claim that Linux or Python 3.14 ran locally.

Upload batches contain at most 40 files each, have no hidden files, and reproduce the same research/partial-kernel92-async directory. Upload each batch's research folder at your fork's repository root, on one fresh branch. Do not upload the part folder itself. After all batches are committed, open one PR from that branch. Nothing in the verifier publishes, deletes files or modifies a fork.
