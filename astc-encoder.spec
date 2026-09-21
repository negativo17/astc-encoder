%global sover 5

# One binary and one library are built per SIMD variant; pick the ones that make
# sense for the architecture. NEON is mandatory on ARMv8, SSE2 is the Fedora
# baseline on both x86 architectures.
%ifarch x86_64
%global isa -DASTCENC_ISA_SSE2=ON -DASTCENC_ISA_SSE41=ON -DASTCENC_ISA_AVX2=ON
%global variants sse2 sse4.1 avx2
%endif
%ifarch %{ix86}
%global isa -DASTCENC_ISA_SSE2=ON
%global variants sse2
%endif
%ifarch aarch64
%global isa -DASTCENC_ISA_NEON=ON
%global variants neon
%endif
%if %{undefined isa}
%global isa -DASTCENC_ISA_NONE=ON
%global variants none
%endif

Name:           astc-encoder
Version:        5.7.0
Release:        1%{?dist}
Summary:        Adaptive Scalable Texture Compression encoder
License:        Apache-2.0
URL:            https://github.com/ARM-software/astc-encoder

Source0:        %{url}/archive/%{version}/%{name}-%{version}.tar.gz
# Upstream sets no SOVERSION and never includes GNUInstallDirs, so the library
# is unversioned and lands in %%{_prefix}/lib:
Patch0:         %{name}-cmake.patch

BuildRequires:  cmake
BuildRequires:  gcc-c++

%description
The Arm ASTC Encoder is a command line compressor for the Adaptive Scalable
Texture Compression format, a texture compression format used by the Vulkan and
OpenGL ES graphics APIs. One command line tool is built per SIMD variant, so
that the one matching the host processor can be used.

%package        libs
Summary:        Codec library for %{name}

%description    libs
The codec library used by %{name}, for applications that compress or
decompress ASTC textures themselves.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%autosetup -p1

%build
# The CLI veneers are declared without a library type, so %%cmake turning
# BUILD_SHARED_LIBS on makes the tools link against uninstalled libraries. The
# codec library itself is declared SHARED and is unaffected.
# Warnings are errors upstream, which is too brittle for a distribution build.
%cmake \
    -DBUILD_SHARED_LIBS=OFF \
    -DASTCENC_CLI=ON \
    -DASTCENC_SHAREDLIB=ON \
    -DASTCENC_WERROR=OFF \
    %{isa}
%cmake_build

%install
%cmake_install

install -p -m 0644 -D Source/astcenc.h %{buildroot}%{_includedir}/astcenc.h

%files
%license LICENSE.txt
%doc README.md
%{expand:%(for v in %{variants}; do echo "%{_bindir}/astcenc-$v"; done)}

%files libs
%license LICENSE.txt
%{expand:%(for v in %{variants}; do echo "%{_libdir}/libastcenc-$v-shared.so.%{sover}"; echo "%{_libdir}/libastcenc-$v-shared.so.%{version}"; done)}

%files devel
%{_includedir}/astcenc.h
%{expand:%(for v in %{variants}; do echo "%{_libdir}/libastcenc-$v-shared.so"; done)}

%changelog
* Mon Sep 21 2026 Simone Caronni <negativo17@gmail.com> - 5.7.0-1
- First build.
