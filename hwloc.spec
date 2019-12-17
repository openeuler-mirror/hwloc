Name:           hwloc
Version:        1.11.9
Release:        3
Summary:        Hardware locality utilities and libraries
License:        BSD
URL:            https://www.open-mpi.org/projects/hwloc/
Source0:        https://download.open-mpi.org/release/%{name}/v1.11/%{name}-%{version}.tar.bz2

BuildRequires:  gcc-c++ cairo-devel libpciaccess-devel libtool-ltdl-devel libX11-devel libxml2-devel texlive-latex
BuildRequires:  desktop-file-utils systemd texlive-makeindex ncurses-devel transfig doxygen

Provides:       hwloc-libs hwloc-gui hwloc-plugins
Obsoletes:      hwloc-libs hwloc-gui hwloc-plugins

%description
hwloc provides command line tools and a C API to obtain the hierarchical map of key computing elements,
such as: NUMA memory nodes, shared caches, processor sockets, processor cores, and processor "threads".
hwloc also gathers various attributes such as cache and memory information,
and is portable across a variety of different operating systems and platforms.

%package        devel
Summary:        Development files for hwloc
Requires:       %{name} = %{version}-%{release}

%description    devel
Contains header files, development libraries and shared object symbolic links for hwloc.

%package        help
Summary:        Help files for hwloc

%description    help
Contains documents and manuals files for hwloc

%prep
%autosetup -n %{name}-%{version} -p1

%build
export runstatedir=/run
%configure --enable-plugins --disable-silent-rules
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
%make_build

%install
%make_install
find %{buildroot} -name '*.la' -exec rm -f {} ';'
cp -p AUTHORS COPYING NEWS README VERSION %{buildroot}%{_pkgdocdir}
cp -pr doc/examples %{buildroot}%{_pkgdocdir}

# Fix for BZ1253977
mv  %{buildroot}%{_pkgdocdir}/examples/Makefile  %{buildroot}%{_pkgdocdir}/examples/Makefile_%{_arch}
desktop-file-validate %{buildroot}/%{_datadir}/applications/lstopo.desktop

# Make hwloc-gui not depend on hwl
rm %{buildroot}%{_mandir}/man1/lstopo.1
ln %{buildroot}%{_mandir}/man1/lstopo-no-graphics.1 %{buildroot}%{_mandir}/man1/lstopo.1

# https://github.com/open-mpi/hwloc/issues/221
%ifarch x86_64
install -p %{buildroot}%{_unitdir}
mv %{buildroot}%{_datadir}/%{name}/hwloc-dump-hwdata.service %{buildroot}%{_unitdir}/
%else
rm %{buildroot}%{_datadir}/%{name}/hwloc-dump-hwdata.service
%endif

%check
LD_LIBRARY_PATH=$PWD/src/.libs make check

%ifarch x86_64
%post
%systemd_post hwloc-dump-hwdata.service
%preun
%systemd_preun hwloc-dump-hwdata.service
%postun
%systemd_postun_with_restart hwloc-dump-hwdata.service
%endif

%ldconfig_post
%ldconfig_postun

%files
%dir %{_pkgdocdir}/
%{_pkgdocdir}/*[^c]
%{_bindir}/%{name}*
%{_bindir}/lstopo*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/%{name}.dtd
%{_datadir}/%{name}/%{name}-valgrind.supp
%{_datadir}/applications/lstopo.desktop
%ifarch x86_64
%{_sbindir}/hwloc-dump-hwdata
%{_unitdir}/hwloc-dump-hwdata.service
%endif
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/hwloc*
%{_libdir}/libhwloc*so.5*

%files devel
%{_libdir}/pkgconfig/*
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*
%{_includedir}/%{name}.h
%{_pkgdocdir}/examples
%{_libdir}/*.so

%files help
%{_mandir}/man*/*

%changelog
* Thu Nov 15 2019 chenzhenyu <chenzhenyu13@huawei.com> - 1.11.9-3
- Package init
