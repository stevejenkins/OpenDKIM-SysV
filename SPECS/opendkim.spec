# SystemV-compatible version

Summary: A DomainKeys Identified Mail (DKIM) milter to sign and/or verify mail
Name: opendkim
Version: 2.9.0
Release: 1%{?dist}
License: BSD and Sendmail
URL: http://opendkim.org/
Group: System Environment/Daemons
Requires: lib%{name} = %{version}-%{release}
Requires (pre): shadow-utils

# Uncomment for systemd version
#Requires (post): systemd-units
#Requires (preun): systemd-units
#Requires (postun): systemd-units
#Requires (post): systemd-sysv
#BuildRequires: libdb-devel
#BuildRequires: libmemcached-devel

# Uncomment for SystemV version
Requires (post): chkconfig
Requires (preun): chkconfig, initscripts
Requires (postun): initscripts
BuildRequires: db4-devel

BuildRequires: libbsd
BuildRequires: libbsd-devel
BuildRequires: pkgconfig
BuildRequires: openssl-devel
BuildRequires: sendmail-devel
BuildRequires: unbound-devel

Source0: http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz

#Patch0: %{name}-libdb.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
OpenDKIM allows signing and/or verification of email through an open source
library that implements the DKIM service, plus a milter-based filter
application that can plug in to any milter-aware MTA, including sendmail,
Postfix, or any other MTA that supports the milter protocol.

%package -n libopendkim
Summary: An open source DKIM library
Group: System Environment/Libraries

%description -n libopendkim
This package contains the library files required for running services built
using libopendkim.

%package -n libopendkim-devel
Summary: Development files for libopendkim
Group: Development/Libraries
Requires: libopendkim = %{version}-%{release}

%description -n libopendkim-devel
This package contains the static libraries, headers, and other support files
required for developing applications against libopendkim.

#%package sysvinit
#Summary: The SysV init script to manage the OpenDKIM milter.
#Group: System Environmnt/Daemons
#Requires: %{name} = %{version}-%{release}

#%description sysvinit
#OpenDKIM allows signing and/or verification of email through an open source
#library that implements the DKIM service, plus a milter-based filter
#application that can plug in to any milter-aware MTA, including sendmail,
#Postfix, or any other MTA that supports the milter protocol. This package
#contains the SysV init script to manage the OpenDKIM milter when running a
#legacy SysV-compatible init system.

#It is not required when the init system used is systemd.

%prep
%setup -q
#%patch0 -p1

%build
%configure --with-unbound --with-db
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

%install
rm -rf %{buildroot}

make DESTDIR=%{buildroot} install %{?_smp_mflags}
install -d %{buildroot}%{_sysconfdir}
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_initrddir}
#install -d -m 0755 %{buildroot}%{_unitdir}
#install -m 0644 contrib/systemd/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
install -m 0755 contrib/init/redhat/%{name} %{buildroot}%{_initrddir}/%{name}
install -m 0755 contrib/init/redhat/%{name}-default-keygen %{buildroot}%{_sbindir}/%{name}-default-keygen

cat > %{buildroot}%{_sysconfdir}/%{name}.conf << 'EOF'
## BASIC OPENDKIM CONFIGURATION FILE
## See %{name}.conf(5) or %{_pkgdocdir}/%{name}.conf.sample for more

## BEFORE running OpenDKIM you must:

## - make your MTA (Postfix, Sendmail, etc.) aware of OpenDKIM
## - generate keys for your domain (if signing)
## - edit your DNS records to publish your public keys (if signing)

## See %{_pkgdocdir}/INSTALL for detailed instructions.

## CONFIGURATION OPTIONS

# Specifies the path to the process ID file.
PidFile	%{_localstatedir}/run/%{name}/%{name}.pid

# Selects operating modes. Valid modes are s (sign) and v (verify). Default is v.
# Must be changed to s (sign only) or sv (sign and verify) in order to sign outgoing
# messages.
Mode	v

# Log activity to the system log.
Syslog	yes

# Log additional entries indicating successful signing or verification of messages.
SyslogSuccess	yes

# If logging is enabled, include detailed logging about why or why not a message was
# signed or verified. This causes an increase in the amount of log data generated
# for each message, so set this to No (or comment it out) if it gets too noisy.
LogWhy	yes

# Attempt to become the specified user before starting operations.
UserID	%{name}:%{name}

# Create a socket through which your MTA can communicate.
Socket	inet:8891@localhost

# Required to use local socket with MTAs that access the socket as a non-
# privileged user (e.g. Postfix)
Umask	002

# This specifies a text file in which to store DKIM transaction statistics.
# OpenDKIM must be manually compiled with --enable-stats to enable this feature.
#Statistics	%{_localstatedir}/spool/%{name}/stats.dat

## SIGNING OPTIONS

# Selects the canonicalization method(s) to be used when signing messages.
Canonicalization	relaxed/relaxed

# Domain(s) whose mail should be signed by this filter. Mail from other domains will
# be verified rather than being signed. Uncomment and use your domain name.
# This parameter is not required if a SigningTable is in use.
#Domain	example.com

# Defines the name of the selector to be used when signing messages.
Selector	default

# Specifies the minimum number of key bits for acceptable keys and signatures.
MinimumKeyBits 1024

# Gives the location of a private key to be used for signing ALL messages. This
# directive is ignored if KeyTable is enabled.
KeyFile	%{_sysconfdir}/%{name}/keys/default.private

# Gives the location of a file mapping key names to signing keys. In simple terms,
# this tells OpenDKIM where to find your keys. If present, overrides any KeyFile
# directive in the configuration file. Requires SigningTable be enabled.
#KeyTable	%{_sysconfdir}/%{name}/KeyTable

# Defines a table used to select one or more signatures to apply to a message based
# on the address found in the From: header field. In simple terms, this tells
# OpenDKIM how to use your keys. Requires KeyTable be enabled.
#SigningTable	refile:%{_sysconfdir}/%{name}/SigningTable

# Identifies a set of "external" hosts that may send mail through the server as one
# of the signing domains without credentials as such.
#ExternalIgnoreList	refile:%{_sysconfdir}/%{name}/TrustedHosts

# Identifies a set "internal" hosts whose mail should be signed rather than verified.
#InternalHosts	refile:%{_sysconfdir}/%{name}/TrustedHosts
EOF

cat > %{buildroot}%{_sysconfdir}/sysconfig/%{name} << 'EOF'
# Set the necessary startup options
OPTIONS="-x %{_sysconfdir}/%{name}.conf -P %{_localstatedir}/run/%{name}/%{name}.pid"

# Determine whether default DKIM keys are automatically created on start
AUTOCREATE_DKIM_KEYS=YES

# Set the default DKIM selector
DKIM_SELECTOR=default

# Set the default DKIM key location
DKIM_KEYDIR=%{_sysconfdir}/%{name}/keys
EOF

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
cat > %{buildroot}%{_sysconfdir}/%{name}/SigningTable << 'EOF'
# OPENDKIM SIGNING TABLE
# This table controls how to apply one or more signatures to outgoing messages based
# on the address found in the From: header field. In simple terms, this tells
# OpenDKIM "how" to apply your keys.

# To use this file, uncomment the SigningTable option in %{_sysconfdir}/%{name}.conf,
# then uncomment one of the usage examples below and replace example.com with your
# domain name, then restart OpenDKIM.

# WILDCARD EXAMPLE
# Enables signing for any address on the listed domain(s), but will work only if
# "refile:%{_sysconfdir}/%{name}/SigningTable" is included in %{_sysconfdir}/%{name}.conf.
# Create additional lines for additional domains.

#*@example.com default._domainkey.example.com

# NON-WILDCARD EXAMPLE
# If "file:" (instead of "refile:") is specified in %{_sysconfdir}/%{name}.conf, then
# wildcards will not work. Instead, full user@host is checked first, then simply host,
# then user@.domain (with all superdomains checked in sequence, so "foo.example.com"
# would first check "user@foo.example.com", then "user@.example.com", then "user@.com"),
# then .domain, then user@*, and finally *. See the %{name}.conf(5) man page under
# "SigningTable" for more details.

#example.com default._domainkey.example.com
EOF

cat > %{buildroot}%{_sysconfdir}/%{name}/KeyTable << 'EOF'
# OPENDKIM KEY TABLE
# To use this file, uncomment the #KeyTable option in %{_sysconfdir}/%{name}.conf,
# then uncomment the following line and replace example.com with your domain
# name, then restart OpenDKIM. Additional keys may be added on separate lines.

#default._domainkey.example.com example.com:default:%{_sysconfdir}/%{name}/keys/default.private
EOF

cat > %{buildroot}%{_sysconfdir}/%{name}/TrustedHosts << 'EOF'
# OPENDKIM TRUSTED HOSTS
# To use this file, uncomment the #ExternalIgnoreList and/or the #InternalHosts
# option in %{_sysconfdir}/%{name}.conf then restart OpenDKIM. Additional hosts
# may be added on separate lines (IP addresses, hostnames, or CIDR ranges).
# The localhost IP (127.0.0.1) should always be the first entry in this file.
127.0.0.1
#host.example.com
#192.168.1.0/24
EOF

install -p -d %{buildroot}%{_sysconfdir}/tmpfiles.d
cat > %{buildroot}%{_sysconfdir}/tmpfiles.d/%{name}.conf <<'EOF'
D %{_localstatedir}/run/%{name} 0700 %{name} %{name} -
EOF

rm -r %{buildroot}%{_prefix}/share/doc/%{name}
rm %{buildroot}%{_libdir}/*.a
rm %{buildroot}%{_libdir}/*.la

mkdir -p %{buildroot}%{_localstatedir}/spool/%{name}
mkdir -p %{buildroot}%{_localstatedir}/run/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir %{buildroot}%{_sysconfdir}/%{name}/keys

install -m 0755 stats/%{name}-reportstats %{buildroot}%{_prefix}/sbin/%{name}-reportstats
sed -i 's|^OPENDKIMSTATSDIR="/var/db/opendkim"|OPENDKIMSTATSDIR="%{_localstatedir}/spool/%{name}"|g' %{buildroot}%{_prefix}/sbin/%{name}-reportstats
sed -i 's|^OPENDKIMDATOWNER="mailnull:mailnull"|OPENDKIMDATOWNER="%{name}:%{name}"|g' %{buildroot}%{_prefix}/sbin/%{name}-reportstats

chmod 0644 contrib/convert/convert_keylist.sh

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
	useradd -r -g %{name} -G mail -d %{_localstatedir}/run/%{name} -s /sbin/nologin \
	-c "OpenDKIM Milter" %{name}
exit 0

%post
#if [ $1 -eq 1 ] ; then 
#    # Initial installation 
#    /bin/systemctl enable %{name}.service >/dev/null 2>&1 || :
#fi

#%post sysvinit
/sbin/chkconfig --add %{name} || :

%preun
#if [ $1 -eq 0 ] ; then
#    # Package removal, not upgrade
#    /bin/systemctl --no-reload disable %{name}.service > /dev/null 2>&1 || :
#    /bin/systemctl stop %{name}.service > /dev/null 2>&1 || :
#fi

#%preun sysvinit
if [ $1 -eq 0 ]; then
	service %{name} stop >/dev/null || :
	/sbin/chkconfig --del %{name} || :
fi
exit 0

%postun
#/bin/systemctl daemon-reload >/dev/null 2>&1 || :
#if [ $1 -ge 1 ] ; then
#    # Package upgrade, not uninstall
#    /bin/systemctl try-restart %{name}.service >/dev/null 2>&1 || :
#fi

#%postun sysvinit
if [ "$1" -ge "1" ] ; then
	/sbin/service %{name} condrestart >/dev/null 2>&1 || :
fi
exit 0

#%triggerun -- %{name} < 2.8.0-1
#/usr/bin/systemd-sysv-convert --save %{name} >/dev/null 2>&1 || :
#/bin/systemctl enable %{name}.service >/dev/null 2>&1
#/sbin/chkconfig --del %{name} >/dev/null 2>&1 || :
#/bin/systemctl try-restart %{name}.service >/dev/null 2>&1 || :

#%triggerpostun -n opendkim-sysvinit -- %{name} < 2.8.0-1
#/sbin/chkconfig --add %{name} >/dev/null 2>&1 || :

%post -n libopendkim -p /sbin/ldconfig

%postun -n libopendkim -p /sbin/ldconfig

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc FEATURES KNOWNBUGS LICENSE LICENSE.Sendmail RELEASE_NOTES RELEASE_NOTES.Sendmail INSTALL
%doc contrib/convert/convert_keylist.sh %{name}/*.sample
%doc %{name}/%{name}.conf.simple-verify %{name}/%{name}.conf.simple
%doc %{name}/README contrib/lua/*.lua
%doc contrib/stats/README.%{name}-reportstats
%config(noreplace) %{_sysconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/tmpfiles.d/%{name}.conf
%config(noreplace) %attr(640,%{name},%{name}) %{_sysconfdir}/%{name}/SigningTable
%config(noreplace) %attr(640,%{name},%{name}) %{_sysconfdir}/%{name}/KeyTable
%config(noreplace) %attr(640,%{name},%{name}) %{_sysconfdir}/%{name}/TrustedHosts
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_sbindir}/*
%{_mandir}/*/*
%dir %attr(-,%{name},%{name}) %{_localstatedir}/spool/%{name}
%dir %attr(-,%{name},%{name}) %{_localstatedir}/run/%{name}
%dir %attr(-,root,%{name}) %{_sysconfdir}/%{name}
%dir %attr(750,root,%{name}) %{_sysconfdir}/%{name}/keys
#%attr(0644,root,root) %{_unitdir}/%{name}.service
#%attr(0755,root,root) %{_sbindir}/%{name}-default-keygen

#%files sysvinit
#%defattr(-,root,root)
%attr(0755,root,root) %{_initrddir}/%{name}

%files -n libopendkim
%defattr(-,root,root)
%doc LICENSE LICENSE.Sendmail README
%{_libdir}/libopendkim.so.*

%files -n libopendkim-devel
%defattr(-,root,root)
%doc LICENSE LICENSE.Sendmail
%doc libopendkim/docs/*.html
%{_includedir}/%{name}
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc

%changelog
* Wed Dec 18 2013 Steve Jenkins <steve stevejenkins com> - 2.9.0-1
- Update to use newer upstream 2.9.0 source code
- Added libbsd-devel to BuildRequires
- Removed listrl references from libopendkim files section (handled by libbsd-devel)

* Sun Nov  3 2013 Steve Jenkins <steve stevejenkins com> - 2.8.4-4
- Rebuild of all release packages to sync version numbers

* Sun Nov  3 2013 Ville Skytta <ville.skytta@iki.fi> - 2.8.4-3
- Fix path to docs in sample config when doc dir is unversioned (#993997).

* Sat Aug 03 2013 Petr Pisar <ppisar@redhat.com> - 2.8.4-2
- Perl 5.18 rebuild

* Tue Jul 23 2013 Steve Jenkins <steve stevejenkins com> 2.8.4-1
- Updated to use newer upstream 2.8.4 source code
- Added libbsd build requirement

* Fri May 17 2013 Steve Jenkins <steve stevejenkins com> 2.8.3-2
- Removed libmemcached support from SysV version (requires > v0.36)

* Sun May 12 2013 Steve Jenkins <steve stevejenkins com> 2.8.3-1
- Updated to use newer upstream 2.8.3 source code
- Added unbound, libmcached, and db support on configure

* Fri Apr 29 2013 Steve Jenkins <steve stevejenkins com> 2.8.2-1
- Updated to use newer upstream 2.8.2 source code

* Tue Mar 19 2013 Steve Jenkins <steve stevejenkins com> 2.8.1-1
- Updated to use newer upstream 2.8.1 source code
- Removed patches for bugs fixed in upstream source

* Wed Feb 27 2013 Steve Jenkins <steve stevejenkins com> 2.8.0-4
- Added patch from upstream to fix libdb compatibility issues

* Tue Feb 26 2013 Steve Jenkins <steve stevejenkins com> 2.8.0-3
- Split into two spec files: systemd (F17+) and SysV (EL5-6)
- systemd-only: Removed leading / from unitdir variables
- Removed commented source lines
- Created comment sections for easy switching between systemd and SysV

* Mon Feb 25 2013 Steve Jenkins <steve stevejenkins com> 2.8.0-2
- Added / in front of unitdir variables

* Thu Feb 21 2013 Steve Jenkins <steve stevejenkins com> 2.8.0-1
- Happy Birthday to me! :)
- Updated to use newer upstream 2.8.0 source code
- Migration from SysV initscript to systemd unit file
- Added systemd build requirement
- Edited comments in default configuration files
- Changed default Canonicalization to relaxed/relaxed in config file
- Changed default values in EnvironmentFile
- Moved program startup options into EnvironmentFile
- Moved default key check and generation on startup to external script
- Removed AutoRestart directives from default config (systemd will handle)
- Incorporated additional variable names throughout spec file
- Added support for new opendkim-sysvinit package for legacy SysV systems

* Tue Jan 08 2013 Steve Jenkins <steve stevejenkins com> 2.7.4-1
- Updated to use newer upstream 2.7.4 source code
- Added AutoRestart and AutoRestartRate directives to default configuration
- Changed default SigningTable directive to include refile: for wildcard support

* Tue Dec 04 2012 Steve Jenkins <steve stevejenkins com> 2.7.3-2
- Set /etc/opendkim/keys default permissions to 750 (Thanks patrick at puzzled.xs4al.nl)

* Thu Nov 29 2012 Steve Jenkins <steve stevejenkins com> 2.7.3-1
- Updated to use newer upstream 2.7.3 source code

* Mon Nov 19 2012 Steve Jenkins <steve stevejenkins com> 2.7.2-1
- Updated to use newer upstream 2.7.2 source code

* Tue Oct 30 2012 Steve Jenkins <steve stevejenkins com> 2.7.1-1
- Updated to use newer upstream 2.7.1 source code
- Updated to reflect source code move of files from /usr/bin to /usr/sbin
- Removed --enable-stats configure option to avoid additional dependencies
- Added support for strlcat() and strlcopy() previously in libopendkim
- Added new MinimumKeyBits configuration option with default of 1024

* Wed Aug 22 2012 Steve Jenkins <steve stevejenkins com> 2.6.7-1
- Updated to use newer upstream 2.6.7 source code
- Removed patches from 2.4.2 which were incorporated upstream
- Updated install directory of opendkim-reportstats

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Sep 22 2011 Steve Jenkins <steve stevejenkins com> 2.4.2-5
- Changed ownernship of directories to comply with selinux-policy
- Added default KeyTable and TrustedHosts files
- Added config(noreplace) to sysconfig file

* Mon Sep 19 2011 Steve Jenkins <steve stevejenkins com> 2.4.2-4
- Use Fedora standard method to fix pkg supplied libtool (Todd Lyons)
- Updated Summary and Description
- Fixed default stats file location in sample config file
- Install opendkim-reportstats and README.opendkim-reportstats
- Changed default stop priority in init script
- Added example SigningTable
- Added sysconfig support for AUTOCREATE_DKIM_KEYS, DKIM_SELECTOR, DKIM_KEYDIR
- Enabled SysLogSuccess and LogWhy by default

* Mon Aug 22 2011 Steve Jenkins <steve stevejenkins com> 2.4.2-3
- Mad props to Matt Domsch for sponsoring and providing feedback
- Removed {?OSshort} variable in Release: header
- Removed explicit Requires: in header
- Added support for tmpfiles.d
- Replaced opendkim with {name} variable throughout
- Replaced RPM_BUILD_ROOT with {buildroot}
- Moved changelog to bottom of file
- Removed "All Rights Reserved" from top of spec file
- Removed Prefix: line in header
- Pointed Source*: to the upstream tarballs
- Changed BuildRoot: format
- Changed makeinstall to make install
- Moved creation of working dirs to install
- Moved ownership of working dirs to files
- Moved user and group creation to pre
- Moved permissions setting to files with attr
- Created directory for user keys
- Removed testing for working directories; mkdir -p will suffice
- Revised Summary
- Removed static libraries from -devel package
- Removed extra spaces
- Removed usermod command to add opendkim to mail group
- Removed echo in post
- General tidying up
- Moved INSTALL readme information into patch
- Removed CPPFLAGS from configure
- Added _smp_mflags to make
- Changed which README from source is written to doc directory
- Added licenses to all subpackages
- Changed default runlevel in init script

* Tue Aug 16 2011  Steve Jenkins <steve stevejenkins com> 2.4.2-2
- Added -q to setup -a 1
- Added x86_64 libtool support (Mad props to Todd Lyons)
- Added {?dist} variable support in Release: header
- Changed Statistics storage location
- Statistics option now commented in opendkim.conf by default
- Check for existing private key before attempting to build keys
- Check for domain name before attempting to build keys

* Mon Aug 15 2011  Steve Jenkins <steve stevejenkins com> 2.4.2-1
- Initial Packaging of opendkim
