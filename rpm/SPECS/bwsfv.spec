%define name bwsfv
%define version 0.6.0
%define unmangled_version 0.6.0
%define release 1
%define _topdir /build
%define _tmppath /tmp

Summary: An application to verify file consistency with .sfv files
Name: %{name}
Version: %{version}
Release: %{release}
Source0: /build/SOURCES/%{name}-%{unmangled_version}.tar.gz
License: GPLv3
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Antti-Pekka Meronen <anttipekkameronen@google.com>
Packager: Antti-Pekka Meronen <anttipekkameronen@google.com>
Url: https://github.com/bulkware/bwsfv

%description
An application to verify file consistency with .sfv files

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python3 setup.py build

%install
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
