Name:           hwloc
Version:        2.2.0
Release:        1
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
make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot} INSTALL="%{__install} -p"
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
install -d %{buildroot}%{_unitdir}
mv %{buildroot}%{_datadir}/%{name}/hwloc-dump-hwdata.service %{buildroot}%{_unitdir}/
%else
rm %{buildroot}%{_datadir}/%{name}/hwloc-dump-hwdata.service
%endif

%check
LD_LIBRARY_PATH=$PWD/hwloc/.libs make check

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
%{_sysconfdir}/bash_completion.d/*
%dir %{_pkgdocdir}/
%{_pkgdocdir}/*[^c]
%{_bindir}/%{name}*
%{_bindir}/lstopo*
%dir %{_datadir}/%{name}
%{_datadir}/hwloc/hwloc-ps.www/
%{_datadir}/hwloc/hwloc2.dtd
%{_datadir}/hwloc/hwloc2-diff.dtd
%{_datadir}/%{name}/%{name}.dtd
%{_datadir}/%{name}/%{name}-valgrind.supp
%{_datadir}/applications/lstopo.desktop
%ifarch x86_64
%{_sbindir}/hwloc-dump-hwdata
%{_unitdir}/hwloc-dump-hwdata.service
%endif
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/hwloc*
%{_libdir}/libhwloc*so.15*

%files devel
%{_libdir}/pkgconfig/*
%{_mandir}/man3/*
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*
%{_includedir}/%{name}.h
%{_pkgdocdir}/examples
%{_libdir}/*.so

%files help
%{_mandir}/man*/*

%changelog
* Tue Mar 08 2022 misaka00251 <misaka00251@misakanet.cn> - 2.2.0-1
- Upgrade version to 2.2.0

* Thu Jul 22 2021 shixuantong <shixuantong@huawei.com> - 1.11.9-4
- move %{_pkgdocdir} to help subpackage

* Thu Nov 15 2019 chenzhenyu <chenzhenyu13@huawei.com> - 1.11.9-3
- Package init
