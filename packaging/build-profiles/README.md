Revision 18 uses one shared plugin in both CPU catalogs; its portable catalog
and installer policy pin the NOAVX build. The AVX-only plugin patch below is
historical for revision 17 and is not needed for revision 18.

# CPU-specific test builds

The main MongoDB port recipe builds portable NOAVX 8.0.34_3. The main os-cellular recipe retains that minimum dependency.

The private AVX test catalog uses the validated official 8.0.34_1 artifact without renaming or relabeling it. For that catalog only, apply os-cellular-avx-test.patch to a separate checkout/overlay and generate the package dependency manifest from the official artifact rather than the NOAVX artifact. The plugin still requires all eight runtime dependencies, including opncell-pymongo. The installer gates the mislabeled official binary using its exact SHA256 and an AVX2 CPU profile. See ../../docs/releases/26.7.2_17-avx-test.md.

mongodb80-avx2.patch and build-mongodb-avx2.sh preserve the optional source-build path. It is not required for the already-tested precompiled artifact. The source-build launcher needs root on the FreeBSD build server and defaults to a dry run.

Keep complete AVX and NOAVX catalogs separate. Nothing in this directory activates the public repository or changes installed packages.
