%global _changelog_trimtime %(date +%s -d "1 year ago")

%define po_package gnome-session-3.0

%global with_session_selector 1

Name: gnome-session
Version: 3.28.1
Release: 6%{?dist}
Summary: GNOME session manager

License: GPLv2+
URL: http://www.gnome.org
Source0: http://download.gnome.org/sources/gnome-session/3.28/%{name}-%{version}.tar.xz
Source1: session-properties-icons.tar.xz

# Blacklist NV30: https://bugzilla.redhat.com/show_bug.cgi?id=745202
Patch00: gnome-session-3.3.92-nv30.patch
Patch01: gnome-session-3.6.2-swrast.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1031182
# https://bugzilla.redhat.com/show_bug.cgi?id=1031188
Patch02: 0001-Revert-Remove-all-references-to-gnome-session-proper.patch
Patch03: 0002-Revert-Remove-gnome-session-properties.patch
Patch04: 0003-Revert-Rename-the-desktop-file-to-gnome-session-prop.patch
Patch05: 0004-stop-using-gsm_util_get_current_desktop.patch
Patch06: 0005-session-properties-get-out-of-Other.patch
Patch07: 0006-session-properties-refresh-from-recent-glade.patch
Patch08: 0007-manager-Don-t-clear-saved-session-if-autosaving-is-d.patch
Patch09: 0008-Add-Remember-Currently-Running-Applications-button.patch
Patch10: 0009-Revert-Allow-saved-session-to-be-a-symlink.patch
Patch11: 0010-Allow-saved-session-directory-to-be-a-symlink.patch
Patch12: 0011-Tie-session-selector-to-properties-dialog.patch
Patch13: 0012-make-save-session-stall-until-it-finishes.patch
Patch14: 0013-manager-save-session-type-in-session-dir.patch
Patch15: 0014-session-selector-restore-saved-session-mode.patch
Patch16: 0015-session-selector-refresh-from-recent-glade.patch
Patch17: 0016-session-selector-add-toggle-for-classic-normal-selec.patch
Patch18: 0017-session-selector-use-classic-mode-by-default.patch
Patch19: 0018-manager-port-away-from-dbus-glib-to-GDBus.patch
Patch20: 0019-capplet-fix-disable-check-items.patch

# Fix the build with Python 2
Patch21: gnome-session-python3.patch

Patch31: 0002-autostart-ensure-gnome-shell-and-mutter-get-right-au.patch

Patch40: 0001-main-don-t-call-into-gdbus-before-setting-all-enviro.patch

Patch50: fix-crash-on-no-dispay.patch

BuildRequires: meson
BuildRequires: gcc
BuildRequires: pkgconfig(egl)
BuildRequires: pkgconfig(gl)
BuildRequires: pkgconfig(glesv2)
BuildRequires: pkgconfig(gnome-desktop-3.0)
BuildRequires: pkgconfig(gtk+-3.0)
BuildRequires: pkgconfig(libsystemd)
BuildRequires: pkgconfig(ice)
BuildRequires: pkgconfig(json-glib-1.0)
BuildRequires: pkgconfig(sm)
BuildRequires: pkgconfig(x11)
BuildRequires: pkgconfig(xau)
BuildRequires: pkgconfig(xcomposite)
BuildRequires: pkgconfig(xext)
BuildRequires: pkgconfig(xrender)
BuildRequires: pkgconfig(xtrans)
BuildRequires: pkgconfig(xtst)

# this is so the configure checks find /usr/bin/halt etc.
BuildRequires: usermode

BuildRequires: gettext
BuildRequires: intltool
BuildRequires: xmlto
BuildRequires: /usr/bin/xsltproc

# an artificial requires to make sure we get dconf, for now
Requires: dconf

Requires: system-logos
# Needed for gnome-settings-daemon
Requires: control-center-filesystem

Requires: gsettings-desktop-schemas >= 0.1.7

# pull in dbus-x11, see bug 209924
Requires: dbus-x11

# https://bugzilla.redhat.com/show_bug.cgi?id=1072801
Requires: mesa-dri-drivers

Conflicts: gnome-settings-daemon < 3.27.90

%description
gnome-session manages a GNOME desktop or GDM login session. It starts up
the other core GNOME components and handles logout and saving the session.

%package xsession
Summary: Desktop file for gnome-session
Requires: %{name}%{?_isa} = %{version}-%{release}

%description xsession
Desktop file to add GNOME to display manager session menu.

%package wayland-session
Summary: Desktop file for wayland based gnome session
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: xorg-x11-server-Xwayland%{?_isa}

%description wayland-session
Desktop file to add GNOME on wayland to display manager session menu.

%package custom-session
Summary: A facility to select and store saved sessions
Requires: %{name}%{?_isa} = %{version}-%{release}

%description custom-session
Installs a 'Custom' entry in the display manager session menu that
lets the user manage multiple saved sessions.

%prep
%autosetup -p1
(cd data/icons; tar xvf %{SOURCE1})

%build
%meson                                                          \
%if 0%{?with_session_selector}
           -Dsession_selector=true                              \
%endif
           -Dsystemd=true                                       \
           -Dsystemd_journal=true
%meson_build

%install
%meson_install

rm -f $RPM_BUILD_ROOT%{_datadir}/wayland-sessions/gnome.desktop
mv $RPM_BUILD_ROOT%{_datadir}/xsessions/gnome-xorg.desktop \
   $RPM_BUILD_ROOT%{_datadir}/wayland-sessions/gnome-wayland.desktop
sed -i -e 's/Xorg/Wayland/g' $RPM_BUILD_ROOT%{_datadir}/wayland-sessions/gnome-wayland.desktop

%find_lang %{po_package}

%post
/sbin/ldconfig
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
/sbin/ldconfig
if [ $1 -eq 0 ] ; then
  touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
  gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
  glib-compile-schemas %{_datadir}/glib-2.0/schemas &>/dev/null || :
fi

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
glib-compile-schemas %{_datadir}/glib-2.0/schemas &>/dev/null || :

%files xsession
%{_datadir}/xsessions/gnome.desktop

%files wayland-session
%{_datadir}/wayland-sessions/gnome-wayland.desktop

%files custom-session
%{_datadir}/xsessions/gnome-custom-session.desktop
%{_bindir}/gnome-session-selector
%{_bindir}/gnome-session-custom-session
%{_datadir}/gnome-session/session-selector.ui
%doc %{_mandir}/man*/gnome-session-selector*

%files -f %{po_package}.lang
%doc AUTHORS NEWS README
%license COPYING
%doc %{_mandir}/man*/*
%{_bindir}/*
%{_libexecdir}/gnome-session-binary
%{_libexecdir}/gnome-session-check-accelerated
%{_libexecdir}/gnome-session-check-accelerated-gl-helper
%{_libexecdir}/gnome-session-check-accelerated-gles-helper
%{_libexecdir}/gnome-session-failed
%{_datadir}/applications/session-properties.desktop
%{_datadir}/gnome-session/
%{_datadir}/doc/gnome-session/dbus/gnome-session.html
%{_datadir}/icons/hicolor/*/apps/session-properties.png
%{_datadir}/icons/hicolor/symbolic/apps/session-properties-symbolic.svg
%{_datadir}/icons/hicolor/scalable/apps/session-properties.svg
%{_datadir}/GConf/gsettings/gnome-session.convert
%{_datadir}/glib-2.0/schemas/org.gnome.SessionManager.gschema.xml

%changelog
* Tue Oct 02 2018 Ray Strode <rstrode@redhat.com> - 3.28.1-6
- Fix crash in gles helper if there's no display
  Resolves: #1627056

* Thu Jul 26 2018 Ray Strode <rstrode@redhat.com> - 3.28.1-5
- Fix gnome-disk-utility timeout at startup
  Resolves: #1593215
- add back session properties icons
  Related: #1568620

* Tue Jul 24 2018 Ray Strode <rstrode@redhat.com> - 3.28.1-4
- Fix pot file generation
  Resolves: #1371019

* Tue Jul 17 2018 Ray Strode <rstrode@redhat.com> - 3.28.1-3
- Make sure gnome-session-custom-session is only shipped in its subpackage
  Resolves: #1600560

* Thu Jun 21 2018 Ray Strode <rstrode@redhat.com> - 3.28.1-2
- Add back GNOME on Wayland session
  Resolves: #1591614

* Tue Apr 10 2018 Kalev Lember <klember@redhat.com> - 3.28.1-1
- Update to 3.28.1
- Resolves: #1568620

* Wed Feb 14 2018 Ray Strode <rstrode@redhat.com> - 3.26.1-11
- Fix rare crash at start up for VNC sessions
  Resolves: #1545234

* Fri Jan 19 2018 Ray Strode <rstrode@redhat.com> - 3.26.1-10
- Correct app id test in upgrade compat fix for wayland
  sessions.
  Related: #1529175

* Thu Jan 18 2018 Ray Strode <rstrode@redhat.com> - 3.26.1-9
- Fix wayland when user has saved sessions
  Resolves: #1529175

* Fri Nov 10 2017 Ray Strode <rstrode@redhat.com> 3.26.1-8
- New sed incantation is still overzealous.  Rework how
  gnome-wayland session file is generated.
  Resolves: #1510391

* Tue Nov 07 2017 Ray Strode <rstrode@redhat.com> - 3.26.1-7
- Fix sed script so we don't change DesktopNames (oops)
  Related: #1482140
  Resolves: 1510391

* Mon Nov 06 2017 Ray Strode <rstrode@redhat.com> - 3.26.1-6
- Add Requires for Xwayland to wayland subpackage
  Related: #1482140
  Resolves: 1509247

* Thu Oct 19 2017 Ray Strode <rstrode@redhat.com> - 3.26.1-1
- add wayland session file
  Resolves: #1482140
- update to 3.26.1 to work with wayland sessions
  Resolves: 1504156

* Tue May 30 2017 Ray Strode <rstrode@redhat.com> - 3.22.3-4
- fix crash in fail whale
  Resolves: #1392970

* Mon Mar 27 2017 Ray Strode <rstrode@redhat.com> - 3.22.3-3
- Fix the ability to disable a service from session properties
  Resolves: #1310975

* Thu Mar 16 2017 Ray Strode <rstrode@redhat.com> - 3.22.3-2
- Drop gnome-xorg.desktop
  Related: #1386957

* Wed Mar 08 2017 Ray Strode <rstrode@redhat.com> - 3.22.3-1
- Rebase to 3.22.3
  Resolves: #1386957

* Mon Jun 27 2016 Ray Strode <rstrode@redhat.com> - 3.14.0-6
- update ko and it translations
  Related: #1272374

* Mon Apr  4 2016 Matthias Clasen <mclasen@redhat.com> 3.14.0-5
- Update translations
  Resolves: #1272374

* Fri Jul 03 2015 Ray Strode <rstrode@redhat.com> 3.14.0-4
- Fix up custom sessions patch more
  Resolves: #1091453

* Wed May 13 2015 Ray Strode <rstrode@redhat.com> 3.14.0-3
- Fix up custom sessions patch
- Related: #1174597

* Mon Mar 23 2015 Richard Hughes <rhughes@redhat.com> - 3.14.0-1
- Update to 3.14.0
- Resolves: #1174597

* Mon Mar 10 2014 Ray Strode <rstrode@redhat.com> 3.8.4-11
- Require mesa-dri-drivers be installed so software GL is
  available.
  Resolves: #1072801

* Wed Jan 29 2014 Ray Strode <rstrode@redhat.com> 3.8.4-10
- more translation updates
  Resolves: #1054583

* Wed Jan 29 2014 Ray Strode <rstrode@redhat.com> 3.8.4-9
- Fix crash when all clients exit
  Resolves: #1036038

* Tue Jan 28 2014 Ray Strode <rstrode@redhat.com> 3.8.4-8
- Fix crasher in session selector if ~/.config/gnome-session
  doesn't exist
  Related: #1031182

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 3.8.4-7
- Mass rebuild 2014-01-24

* Wed Jan 08 2014 Ray Strode <rstrode@redhat.com> 3.8.4-6
- Add back custom session selector from RHEL 6
  Resolves: #1031188
  Resolves: #1031182

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 3.8.4-5
- Mass rebuild 2013-12-27

* Thu Dec 12 2013 Matthias Clasen <mclasen@redhat.com> - 3.8.4-4
- Update translations
- Resolves: #1030346

* Wed Nov 27 2013 Florian Müllner <fmuellner@redhat.com> - 3.8.4-3
- Fix mispositioned fail-whale dialog
  Resolves: #1031117

* Fri Nov  1 2013 Matthias Clasen <mclasen@redhat.com> - 3.8.4-2
- Fix a possible crash in the presence interface
- Resolves: #1022521

* Tue Jul 30 2013 Ray Strode <rstrode@redhat.com> - 3.8.4-1
- Update to 3.8.4

* Tue Jul 30 2013 Matthias Clasen <mclasen@redhat.com> - 3.8.3-1
- Fix a crash when talking to systemd (#977575)

* Sat Jun 22 2013 Matthias Clasen <mclasen@redhat.com> - 3.8.2.1-2
- Trim %%changelog

* Wed May 15 2013 Matthias Clasen <mclasen@redhat.com> - 3.8.2.1-1
- Update to 3.8.2.1
- Conditionally build session selector

* Mon May 13 2013 Matthias Clasen <mclasen@redhat.com> - 3.8.2-1
- Update to 3.8.2

* Tue Apr 30 2013 Kalev Lember <kalevlember@gmail.com> - 3.8.1-2
- Use the upstream xsession desktop file
- Drop the fallback mode authentication agent autostart file

* Mon Apr 15 2013 Kalev Lember <kalevlember@gmail.com> - 3.8.1-1
- Update to 3.8.1

* Thu Apr 11 2013 Adam Jackson <ajax@redhat.com> 3.8.0-2
- gnome-session-3.6.2-swrast.patch: Allow running on the classic software
  renderer.  No effect on arches where we build llvmpipe, but on ppc/s390
  classic swrast is marginally less painful than softpipe.

* Tue Mar 26 2013 Kalev Lember <kalevlember@gmail.com> - 3.8.0-1
- Update to 3.8.0

* Wed Mar 20 2013 Richard Hughes <rhughes@redhat.com> - 3.7.92-1
- Update to 3.7.92

* Wed Mar  6 2013 Matthias Clasen <mclasen@redhat.com> - 3.7.91-1
- Update to 3.7.91

* Sun Feb 24 2013 Matthias Clasen <mclasen@redhat.com> - 3.7.90-2
- Drop obsolete requires (polkit-gnome, polkit-desktop-policy,
  notification-daemon)

* Wed Feb 20 2013 Richard Hughes <rhughes@redhat.com> - 3.7.90-1
- Update to 3.7.90

* Wed Feb 06 2013 Kalev Lember <kalevlember@gmail.com> - 3.7.4-1
- Update to 3.7.4

* Thu Dec 20 2012 Kalev Lember <kalevlember@gmail.com> - 3.7.3-1
- Update to 3.7.3
- Drop the upstreamed llvmpipe patch
- Adjust buildrequires

* Tue Nov 20 2012 Richard Hughes <hughsient@gmail.com> - 3.7.2-1
- Update to 3.7.2

* Fri Nov 09 2012 Kalev Lember <kalevlember@gmail.com> - 3.7.1-1
- Update to 3.7.1

* Thu Oct 18 2012 Florian Müllner <fmuellner@redhat.com> - 3.6.1-2
- Set XDG_MENU_PREFIX to pick the correct menu layout in
  gnome-shell and alacarte

* Tue Oct 16 2012 Kalev Lember <kalevlember@gmail.com> - 3.6.1-1
- Update to 3.6.1

* Tue Sep 25 2012 Matthias Clasen <mclasen@redhat.com> - 3.6.0-1
- Update to 3.6.0

* Thu Sep 06 2012 Richard Hughes <hughsient@gmail.com> - 3.5.91-1
- Update to 3.5.91

* Tue Aug 07 2012 Richard Hughes <hughsient@gmail.com> - 3.5.5-1
- Update to 3.5.5

* Fri Jul 27 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.5.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 17 2012 Richard Hughes <hughsient@gmail.com> - 3.5.4-1
- Update to 3.5.4

* Thu Jun 07 2012 Richard Hughes <hughsient@gmail.com> - 3.5.2-1
- Update to 3.5.2

* Fri May 18 2012 Richard Hughes <hughsient@gmail.com> - 3.4.2-1
- Update to 3.4.2

* Tue Apr 24 2012 Kalev Lember <kalevlember@gmail.com> - 3.4.1-2
- Silence rpm scriptlet output

* Tue Apr 17 2012 Kalev Lember <kalevlember@gmail.com> - 3.4.1-1
- Update to 3.4.1
- Dropped upstreamed systemd patch

* Thu Apr  5 2012 Matthias Clasen <mclasen@redhat.com> - 3.4.0-2
- Fix a looping PolicyKit dialog on shutdown

* Tue Mar 27 2012 Richard Hughes <hughsient@gmail.com> - 3.4.0-1
- Update to 3.4.0

* Thu Mar 22 2012 Adam Williamson <awilliam@redhat.com> - 3.3.92-2
- blacklist NV30 family until RH #745202 is resolved

* Wed Mar 21 2012 Kalev Lember <kalevlember@gmail.com> - 3.3.92-1
- Update to 3.3.92

* Sun Feb 26 2012 Matthias Clasen <mclasen@redhat.com> - 3.3.90-1
- Update to 3.3.90

* Thu Feb  9 2012 Matthias Clasen <mclasen@redhat.com> - 3.3.5-2
- Fix a bug in the new system interface registration

* Tue Feb  7 2012 Matthias Clasen <mclasen@redhat.com> - 3.3.5-1
- Update to 3.3.5
- Use systemd for session tracking

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Dec 21 2011 Matthias Clasen <mclasen@redhat.com> 3.3.3-1
- Update to 3.3.3

* Tue Dec 13 2011 Adam Jackson <ajax@redhat.com> 3.3.2-2
- gnome-session-3.3.2-radeon.patch: Blacklist pre-R300 radeons (#758422)

* Wed Nov 23 2011 Matthias Clasen <mclasen@redhat.com> 3.3.2-1
- Update to 3.3.2

* Thu Nov 03 2011 Adam Jackson <ajax@redhat.com> 3.3.1-2
- gnome-session-3.3.1-llvmpipe.patch: Don't consider llvmpipe unsupported.

* Wed Nov  2 2011 Matthias Clasen <mclasen@redhat.com> - 3.3.1-1
- Update to 3.3.1

* Wed Oct 26 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.1-2
- Rebuilt for glibc bug#747377

* Tue Oct 18 2011 Matthias Clasen <mclasen@redhat.com> - 3.2.1-1
- Update to 3.2.1

* Tue Sep 27 2011 Ray <rstrode@redhat.com> - 3.2.0-1
- Update to 3.2.0

* Tue Sep 20 2011 Matthias Clasen <mclasen@redhat.com> 3.1.92-1
- Update to 3.1.92

* Fri Sep  9 2011 Matthias Clasen <mclasen@redhat.com> 3.1.91-3
- Some fixes to make gdm fallback mode login work

* Thu Sep  8 2011 Matthias Clasen <mclasen@redhat.com> 3.1.91-2
- Drop GConf2-gtk dep

* Tue Sep  6 2011 Matthias Clasen <mclasen@redhat.com> 3.1.91-1
- Update to 3.1.91

* Wed Aug 31 2011 Matthias Clasen <mclasen@redhat.com> 3.1.90-1
- Update to 3.1.90

* Wed Aug 17 2011 Matthias Clasen <mclasen@redhat.com> 3.1.5-1
- Update to 3.1.5

* Mon Jul 04 2011 Bastien Nocera <bnocera@redhat.com> 3.1.3-1
- Update to 3.1.3

* Wed Jun 15 2011 Tomas Bzatek <tbzatek@redhat.com> - 3.1.2-1
- Update to 3.1.2

* Wed Apr 27 2011 Owen Taylor <otaylor@redhat.com> - 3.0.1-2
- Add a quick-and-dirty blacklist for Radeon R100, R200, Intel 8xx

* Tue Apr 26 2011 Matthias Clasen <mclasen@redhat.com> 3.0.1-1
- Update to 3.0.1

* Mon Apr  4 2011 Matthias Clasen <mclasen@redhat.com> 3.0.0-1
- Update to 3.0.0

* Mon Mar 28 2011 Matthias Clasen <mclasen@redhat.com> 2.91.94-1
- Update to 2.91.94

* Wed Mar 23 2011 Ray Strode <rstrode@redhat.com> 2.91.93-1
- Update to 2.91.93

* Wed Mar 23 2011 Matthias Clasen <mclasen@redhat.com> 2.91.92-1
- Update to 2.91.92

* Wed Mar  9 2011 Matthias Clasen <mclasen@redhat.com> 2.91.91.3-1
- Update to 2.91.91.3

* Wed Mar  9 2011 Matthias Clasen <mclasen@redhat.com> 2.91.91.2-1
- Update to 2.91.91.2

* Tue Mar  8 2011 Matthias Clasen <mclasen@redhat.com> 2.91.91-2
- Fix the check-accel utility exit status

* Mon Mar  7 2011 Matthias Clasen <mclasen@redhat.com> 2.91.91-1
- Update to 2.91.91

* Mon Feb 28 2011 Matthias Clasen <mclasen@redhat.com> 2.91.90-5
- Make the new if-session Autostart condition work

* Mon Feb 28 2011 Matthias Clasen <mclasen@redhat.com> 2.91.90-4
- Fix the autostart syntax

* Tue Feb 22 2011 Matthias Clasen <mclasen@redhat.com> 2.91.90-3
- Install an autostart file for the authentication agent
  in the fallback session

* Tue Feb 22 2011 Ray Strode <rstrode@redhat.com> 2.91.90-2
- Fix crashity crash crash

* Mon Feb 21 2011 Matthias Clasen <mclasen@redhat.com> 2.91.90-1
- Update to 2.91.90

* Fri Feb 11 2011 Matthias Clasen <mclasen@redhat.com> 2.91.6-3
- Rebuild against newer gtk

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.91.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Feb  2 2011 Matthias Clasen <mclasen@redhat.com> 2.91.6-1
- 2.91.6

* Tue Jan 25 2011 Matthias Clasen <mclasen@redhat.com> 2.91.4-3
- Just require control-center-filesystem (#661565)

* Fri Jan 14 2011 Matthias Clasen <mclasen@redhat.com> 2.91.4-2
- Don't run the shell on softpipe

* Sun Jan  9 2011 Matthias Clasen <mclasen@redhat.com> 2.91.4-1
- Update to 2.91.4

* Fri Dec  3 2010 Matthias Clasen <mclasen@redhat.com> 2.91.0-7
- Rebuild against new gtk

* Sun Nov 07 2010 Ray Strode <rstrode@redhat.com> 2.91.0-6
- Fix some cases where the inhibitor dialog shows up when it isn't
  supposed to.

* Tue Nov  2 2010 Matthias Clasen <mclasen@redhat.com> - 2.91.0-5
- Prepare for libnotify 0.7.0

* Mon Nov  1 2010 Matthias Clasen <mclasen@redhat.com> - 2.91.0-4
- Rebuild against newer gtk3

* Tue Oct 26 2010 Parag Nemade <paragn AT fedoraproject.org> - 2.91.0-3
- Gconf2 scriptlet accepts schema file names without file extension.

* Fri Oct 15 2010 Parag Nemade <paragn AT fedoraproject.org> - 2.91.0-2
- Merge-review cleanup (#225835)

* Wed Oct  6 2010 Matthias Clasen <mclasen@redhat.com> - 2.91.0-1
- Update to 2.91.0

* Thu Sep 30 2010 Matthias Clasen <mclasen@redhat.com> - 2.32.0-1
- Update to 2.32.0

* Wed Sep 29 2010 jkeating - 2.31.6-3
- Rebuilt for gcc bug 634757

* Tue Sep 21 2010 Ray Strode <rstrode@redhat.com> - 2.31.6-2
- build fixes

* Fri Aug  6 2010 Matthias Clasen <mclasen@redhat.com> - 2.31.6-1
- Update to 2.31.6

* Thu Jul  8 2010 Matthias Clasen <mclasen@redhat.com> - 2.31.2-2
- Require dconf

* Thu May 27 2010 Matthias Clasen <mclasen@redhat.com> - 2.31.2-1
- Update to 2.31.2

* Fri May 07 2010 Colin Walters <walters@verbum.org> - 2.30.0-2
- Use upstream commit for library linking

* Mon Mar 29 2010 Matthias Clasen <mclasen@redhat.com> - 2.30.0-1
- Update to 2.30.0

* Tue Mar 09 2010 Bastien Nocera <bnocera@redhat.com> 2.29.92-1
- Update to 2.29.92

* Thu Feb 11 2010 Matthias Clasen <mclasen@redhat.com> - 2.29.6-1
- Update to 2.29.6

* Fri Jan 15 2010 Ray Strode <rstrode@redhat.com> - 2.28.0-4
- Nag user if they try to log in as root

* Fri Nov  6 2009 Matthias Clasen  <mclasen@redhat.com> - 2.28.0-3
- Add ability to perform actions after a period of idleness

* Fri Oct 23 2009 Matthias Clasen  <mclasen@redhat.com> - 2.28.0-2
- Avoid a crash on certain xsmp error conditions

* Wed Sep 23 2009 Matthias Clasen  <mclasen@redhat.com> - 2.28.0-1
- Update to 2.28.0

* Wed Sep  9 2009 Matthias Clasen  <mclasen@redhat.com> - 2.27.92-1
- Update to 2.27.92

* Thu Aug 13 2009 Matthias Clasen  <mclasen@redhat.com> - 2.27.5-2
- Require polkit-desktop-policy

* Tue Jul 28 2009 Matthias Clasen  <mclasen@redhat.com> - 2.27.5-1
- Update to 2.27.5

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 20 2009 Matthias Clasen  <mclasen@redhat.com> - 2.27.4-2
- Require polkit-gnome, we need an authentication agent in the session

* Wed Jul 15 2009 Matthias Clasen  <mclasen@redhat.com> - 2.27.4-1
- Update to 2.27.4

* Fri Jul 10 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.1-5
- Avoid pointless warnings

* Sun Jun 14 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.1-4
- Drop unused files

* Fri Jun 12 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.1-3
- Fix some oversights in the PolicyKit port

* Tue May 12 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.1-2
- Port to PolicyKit 1

* Tue Apr 14 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.1-1
- Update to 2.26.1
- See http://download.gnome.org/sources/gnome-session/2.26/gnome-session-2.26.1.news

* Wed Apr  8 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.0.90-1
- Update to 2.26.0.90

* Sun Apr  5 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.0-2
- Avoid some warnings (#493688)

* Mon Mar 16 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Fri Mar  6 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.92-2
- Turn off excessive debug spew

* Tue Mar  3 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.92-1
- Update to 2.25.92

* Thu Feb 26 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.91-4
- Make -xsession arch again
- Fix xsync usage

* Tue Feb 24 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.91-3
- Make -xsession noarch

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 18 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.91-1
- Update to 2.25.91

* Tue Feb  3 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.90-1
- Update to 2.25.90

* Tue Jan 20 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.5-2
- Update to 2.25.5
- Fix BuildRequires

* Wed Dec 17 2008 Matthias Clasen  <mclasen@redhat.com> - 2.25.3-1
- Update to 2.25.3

* Thu Dec  4 2008 Matthias Clasen  <mclasen@redhat.com> - 2.25.2-2
- Update to 2.25.2

* Tue Nov 25 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.1-5
- Spec file cleanups

* Mon Nov 10 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.1-4
- Fix client registration in some cases 

* Sun Oct 26 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.1-3
- Make the capplet resizable (#468577)

* Wed Oct 22 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.1-1
- Update to 2.24.1
- Drop upstreamed patches

* Wed Oct 15 2008 Ray Strode <rstrode@redhat.com> - 2.24.0-11
- Remove some dubious code to fix panel race at startup that
  would make shutdown menu item disappear for some users.

* Fri Oct 10 2008 Ray Strode <rstrode@redhat.com> - 2.24.0-10
- Rewrite patch another time leverage better api and be more
  terse

* Fri Oct 10 2008 Ray Strode <rstrode@redhat.com> - 2.24.0-9
- Bring shutdown menu item back.  More fallout from my buggy
  patch introduced in -7

* Thu Oct  9 2008 Ray Strode <rstrode@redhat.com> - 2.24.0-8
- Fix assertion failure in last patch

* Thu Oct  9 2008 Ray Strode <rstrode@redhat.com> - 2.24.0-7
- Add new api for panel to figure out whether or not to show
  Shutdown menu item.

* Fri Oct  3 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.0-6
- Fix missing translations in the capplet
- Fix small UI issues in the capplet

* Sun Sep 28 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.0-5
- BR xorg-x11-xtrans-devel (#464316)

* Fri Sep 26 2008 Ray Strode  <rstrode@redhat.com> - 2.24.0-4
- Make the new xsession subpackage require the version of
  gnome-session it's built against

* Thu Sep 25 2008 Ray Strode  <rstrode@redhat.com> - 2.24.0-3
- Split gnome-session.desktop off into subpackage

* Mon Sep 22 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.0-2
- Update to 2.24.0
- Drop upstreamed patches

* Thu Sep 18 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.92-6
- Plug memory leaks

* Thu Sep 18 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.92-5
- Plug memory leaks

* Mon Sep 15 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.92-4
- Plug memory leaks

* Sun Sep 14 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.92-3
- Plug memory leaks

* Sun Sep 14 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.92-2
- Plug memory leaks

* Mon Sep  8 2008 Jon McCann  <jmccann@redhat.com> - 2.23.92-1
- Update to 2.23.92

* Tue Sep  2 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.91-1
- Update to 2.23.91

* Thu Aug 28 2008 Jon McCann  <jmccann@redhat.com> - 2.23.91.0.2008.08.28.1
- Update to snapshot

* Fri Aug 22 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.90-1
- Update to 2.23.90

* Thu Aug 14 2008 Lennart Poettering  <lpoetter@redhat.com> - 2.23.6-4
- Drop login/logout sound scripts since we do this now in libcanberra

* Tue Aug 12 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.6-3
- Fix a crash in the at-spi-registryd-wrapper

* Thu Aug  7 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.6-2
- Fix another icon name

* Tue Aug  5 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.6-1
- Update to 2.23.6

* Wed Jul 30 2008 Jon McCann  <jmccann@redhat.com> - 2.23.6.0.2008.07.30.1
- New snapshot from DBus branch

* Mon Jul 29 2008 Jon McCann  <jmccann@redhat.com> - 2.23.6.0.2008.07.29.1
- New snapshot from DBus branch

* Mon Jul 28 2008 Jon McCann  <jmccann@redhat.com> - 2.23.5.0.2008.07.28.1
- New snapshot from DBus branch

* Thu Jul 24 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.5.0.2008.07.21.4
- Fix a crash

* Mon Jul 22 2008 Jon McCann  <jmccann@redhat.com> - 2.23.5.0.2008.07.21.3
- Add BuildRequires PolicyKit-gnome-devel

* Mon Jul 21 2008 Jon McCann  <jmccann@redhat.com> - 2.23.5.0.2008.07.21.2
- New snapshot to fix build

* Mon Jul 21 2008 Jon McCann  <jmccann@redhat.com> - 2.23.5.0.2008.07.21.1
- Snapshot from DBus branch

* Wed Jul  9 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.4.1-4
- Fix a typo in the previous patch

* Wed Jul  9 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.4.1-3
- Use more standard icon names

* Tue Jul  8 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.4.1-2
- Escape comments for markup

* Wed Jun 18 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.4.1-1
- Update to 2.23.4.1

* Wed Jun  4 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.3-1
- Update to 2.23.3

* Fri May 16 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.2.2-3
- Make nautilus start again

* Thu May 15 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.2.2-2
- Don't crash while handling legacy sessions

* Wed May 14 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.2.2-1
- Update to 2.23.2.2

* Fri Apr 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.1-1
- Update to 2.23.1

* Thu Apr 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1.1-1
- Update to 2.22.1.1 (fixes a crash in the trash migration code)

* Mon Apr  7 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1-1
- Update to 2.22.1

* Sun Apr  6 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-2
- Drop gnome-volume-manager from the default session

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-1
- Update to 2.22.0

* Thu Mar 06 2008 - Bastien Nocera <bnocera@redhat.com> - 2.21.93-1
- Update to 2.21.93, drop esound dependencies and patches

* Tue Feb 26 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.92-1
- Update to 2.21.92

* Tue Feb 12 2008  Matthias Clasen <mclasen@redhat.com> - 2.21.91-1
- Update to 2.21.91

* Mon Feb 11 2008 - Bastien Nocera <bnocera@redhat.com> - 2.21.90-2
- Add patch to make login sounds work
- Remove unneeded patch to launch gnome-user-share, it launches
  using autostart now

* Tue Jan 29 2008  Matthias Clasen <mclasen@redhat.com> - 2.21.90-1
- Update to 2.21.90

* Tue Jan 15 2008  Matthias Clasen <mclasen@redhat.com> - 2.21.5-1
- Update to 2.21.5

* Tue Nov 27 2007  Matthias Clasen <mclasen@redhat.com> - 2.20.2-1
- Update to 2.20.2 (translation updates)

* Tue Oct 30 2007 - Bastien Nocera <bnocera@redhat.com> - 2.20.1-2
- Enable sound by default, without looking at the prefs

* Mon Oct 15 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-1
- Update to 2.20.1 (translation updates)

* Thu Sep 27 2007 Ray Strode <rstrode@redhat.com> - 2.20.0-2
- drop redhat-artwork dep.  We don't need it.

* Mon Sep 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-1
- Update to 2.20.0

* Tue Sep 11 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.92-3
- Plug memory leaks in the ICE code

* Wed Sep  5 2007 Kristian Høgsberg <krh@redhat.com> - 2.19.92-2
- Update gnome-session-2.17.5-window-manager.patch to apply (remove
  chunks that are now upstream).

* Tue Sep  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.92-1
- Update to 2.19.92

* Thu Aug 23 2007 Adam Jackson <ajax@redhat.com> - 2.19.90-2
- Rebuild for build ID

* Mon Aug 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.90-1
- Update to 2.19.90

* Fri Aug 10 2007 Kristian Høgsberg <krh@redhat.com> - 2.19.6-5
- Edit window manager patch again to add 'glib' to compiz launch.

* Thu Aug  9 2007 Kristian Høgsberg <krh@redhat.com> - 2.19.6-4
- Edit the right window manager patch and delete the old one.

* Thu Aug  9 2007 Kristian Høgsberg <krh@redhat.com> - 2.19.6-3
- Export LIBGL_ALWAYS_INDIRECT before starting compiz.

* Fri Aug  3 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.6-2
- Update license field

* Mon Jul 30 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.6-1
- Update to 2.19.6

* Sun Jul  8 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.5-1
- Update to 2.19.5

* Fri Jul  6 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.4-3
- Move /usr/share/gnome/wm-properties to control-center-filesystem

* Tue Jun 19 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.4-2
- Fix a hang on login with a11y

* Sun Jun 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.4-1
- Update to 2.19.4

* Mon Jun  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.3-1
- Update to 2.19.3
- Drop upstreamed patch

* Tue May 22 2007 - Bastien Nocera <bnocera@redhat.com> - 2.19.2-2
- Fix up logic in iris patch

* Sun May 20 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.2-1
- Update to 2.19.2

* Tue May 15 2007 Ray Strode <rstrode@redhat.com> - 2.18.0-7
- Don't show iris animation when using compiz (bug 237842)

* Sun May  6 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-6
- Don't own /usr/share/applications

* Sat Apr 14 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-5
- Add a dependency on dbus-x11

* Thu Apr 12 2007 David Zeuthen <davidz@redhat.com> - 2.18.0-4
- start same kind of AT's in session as started in gdm (#229912)

* Fri Mar 30 2007 Ray Strode <rstrode@redhat.com> - 2.18.0-3
- remove xdg autostart dir since it's part of filesystem now

* Wed Mar 21 2007 Ray Strode <rstrode@redhat.com> - 2.18.0-2
- remove eggcups from default session (bug 233261)

* Tue Mar 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-1
- Update to 2.18.0

* Wed Feb 28 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.92-1
- Update to 2.17.92

* Fri Feb 23 2007 Jeremy Katz <katzj@redhat.com> - 2.17.91-2
- disable a11y registry timeout so that we don't get the popup with 
  the livecd (#227214)

* Tue Feb 13 2007 Matthisa Clasen <mclasen@redhat.com> - 2.17.91-1
- Update to 2.17.91

* Tue Feb  6 2007 Kristian Høgsberg <krh@redhat.com> - 2.17.90.1-3
- Update gnome-session-2.15.90-window-manager.patch to start
  gtk-window-decorator instead of gnome-window-decorator for compiz.

  [ Update: the patch is not applied and upstream gnome-session does
    the right thing. ]

* Mon Feb  5 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.90.1-2
- Require GConf2-gtk for gconf-sanity-check 

* Tue Jan 23 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.90.1-1
- Update to 2.17.90.1

* Sun Jan 21 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.90-1
- Update to 2.17.90
- Clean up BuildRequires

* Wed Jan 10 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.5-1
- Update to 2.17.5

* Mon Nov 27 2006 Ray Strode <rstrode@redhat.com> - 2.17.2-6
- don't set http_proxy variable if proxy requires password (bug
  217332)

* Wed Nov 22 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.2-4
- Own the /usr/share/gnome/wm-properties directory (#216514)

* Mon Nov 20 2006 Ray Strode <rstrode@redhat.com> - 2.17.2-3
- don't make gnome.desktop executable (bug 196105)

* Sat Nov 11 2006 Matthias Clasen  <mclasen@redhat.com> - 2.17.2-2
- Fix gnome-wm for compiz

* Tue Nov  7 2006 Matthias Clasen  <mclasen@redhat.com> - 2.17.2-1
- Update to 2.17.2

* Thu Oct 26 2006 Ray Strode <rstrode@redhat.com> - 2.16.1-2.fc7
- don't hose users with a stale http_proxy variable if they
  use autoconfiguration and uses to use manual configuration.
  Patch by Mark McLoughlin (bug 212319)

* Sat Oct 21 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.1-1
- Update to 2.16.1

* Wed Oct 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-4
- Fix scripts according to the packaging guidelines

* Thu Sep  7 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-3.fc6
- Fix position of icons in the splash screen  (#205508)

* Wed Sep  6 2006 Ray Strode <rstrode@redhat.com> - 2.16.0-2.fc6
- set http_proxy environment variable from GNOME settings 
  (bug 190041)

* Mon Sep  4 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-1.fc6
- Update to 2.16.0

* Mon Aug 21 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.92-1.fc6
- Update to 2.15.92
- Add %%preun and %%postun scripts

* Mon Aug 14 2006 Ray Strode <rstrode@redhat.com> - 2.15.91-1.fc6
- Update to 2.15.91

* Sun Aug 13 2006 Ray Strode <rstrode@redhat.com> - 2.15.90-4.fc6
- fix window manager launching script. Patch from 
  Tim Vismor <tvismor@acm.org> (bug 202312)

* Fri Aug 11 2006 Ray Strode <rstrode@redhat.com> - 2.15.90-3.fc6
- start gnome-window-decorator and pass "gconf" when invoking
  compiz

* Thu Aug 10 2006 Ray Strode <rstrode@redhat.com> - 2.15.90-2.fc6
- update patch from 2.15.4-3 to be more session friendly (bug 201473)

* Fri Aug  4 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.90-1.fc6
- Update to 2.15.90

* Thu Aug  3 2006 Soren Sandmann <sandmann@redhat.com> - 2.15.4-3
- Add patch to (a) add configuration option for window manager, (b) start the window
  manager, and (c) disable splash screen by default.

* Wed Jul 19 2006 John (J5) Palmieri <johnp@redhat.com> - 2.15.4-2
- Add BR for dbus-glib-devel

* Thu Jul 13 2006 Ray Strode <rstrode@redhat.com> - 2.15.4-1
- Update to 2.15.4

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.15.1-5.1
- rebuild

* Mon Jun 12 2006 Bill Nottingham  <notting@redhat.com> 2.15.1-5
- remove obsolete automake14 buildreq

* Fri Jun  9 2006 Matthias Clasen  <mclasen@redhat.com> 2.15.1-4
- Add more missing BuildRequires

* Tue Jun  6 2006 Matthias Clasen  <mclasen@redhat.com> 2.15.1-3
- Add BuildRequires: intltool, autoconf, automake 

* Mon Jun  5 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.1-2
- Require system-logos, not fedora-logos

* Wed May 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.1-1
- Update to 2.15.1

* Mon Apr 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.1-2
- Update to 2.14.1

* Mon Mar 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.0-1
- Update to 2.14.0

* Thu Mar 09 2006 Ray Strode <rstrode@redhat.com> - 2.13.92-5
- fix up path creation functions 

* Thu Mar 09 2006 Ray Strode <rstrode@redhat.com> - 2.13.92-4
- create ~/.config/autostart before trying to migrate
  session-manual to it (bug 179602).

* Mon Mar 06 2006 Ray Strode <rstrode@redhat.com> - 2.13.92-3
- Patch from Vincent Untz to fix session editing (upstream bug 333641)
- Desensitize buttons for operations that the user isn't allowed
  to do (bug 179479).

* Wed Mar 01 2006 Karsten Hopp <karsten@redhat.de> 2.13.92-2
- BuildRequires: gnome-desktop-devel, libX11-devel, libXt-devel

* Tue Feb 28 2006 Ray Strode <rstrode@redhat.com> - 2.13.92-1
- Update to 2.13.92
- Add patch from CVS HEAD to maintain compatibility with
  version 2.13.91

* Thu Feb 23 2006 Ray Strode <rstrode@redhat.com> - 2.13.91-2
- take ownership of autostart dir (bug 182335)

* Mon Feb 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.91-1
- Update to 2.13.91

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.13.90-1.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.13.90-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Sat Jan 28 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.90-1
- Update to 2.13.90

* Tue Jan 17 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.5-1
- Update to 2.13.5

* Mon Jan 16 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.4-2
- Disable the fatal-criticals, since it crashes too much 

* Fri Jan 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.4-1
- Update to 2.13.4

* Thu Jan 12 2006 Ray Strode <rstrode@redhat.com> - 2.12.0-6
- Fix screen corruption around splash screen shape (bug 177502)

* Tue Dec 20 2005 John (J5) Palmieri <johnp@redhat.com> - 2.12.0-5
- Handle shaped window for splash screen

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Nov  9 2005 Alexander Larsson <alexl@redhat.com> - 2.12.0-4
- Add gnome-user-share patch

* Tue Nov 8 2005 Ray Strode <rstrode@redhat.com> - 2.12.0-3
- fix up the dummy client ids to match the id passed initially
  passed to the programs in the default session 
  (broke in last update).

* Mon Oct 31 2005 Ray Strode <rstrode@redhat.com> - 2.12.0-2
- remove rhn applet from default session
- s/magicdev/gnome-volume-manager/

* Thu Sep  8 2005 Matthias Clasen <mclasen@redhat.com> - 2.12.0-1
- Update to 2.12.0

* Tue Sep  6 2005 Ray Strode <rstrode@redhat.com> - 2.11.91-3
- Don't take ownership of /usr/share/xsessions (bug 145791).

* Tue Aug 16 2005 Warren Togami <wtogami@redhat.com> - 2.11.91-2
- rebuild for new cairo

* Tue Aug  9 2005 Ray Strode <rstrode@redhat.com> - 2.11.91-1
- Update to upstream version 2.11.91 (fixes bug 165357).
- drop some patches

* Thu Apr 18 2005 Ray Strode <rstrode@redhat.com> - 2.10.0-2
- Install gnome.desktop to /usr/share/xsessions (bug 145791)

* Thu Mar 17 2005 Ray Strode <rstrode@redhat.com> - 2.10.0-1
- Update to upstream version 2.10.0

* Wed Feb  2 2005 Matthias Clasen <mclasen@redhat.com> 2.9.4-1
- Update to 2.9.4

* Mon Dec 20 2004 Daniel Reed <djr@redhat.com> 2.8.0-7
- rebuild for new libhowl.so.0 library (for GnomeMeeting 1.2) (this was a mistake)

* Tue Nov 02 2004 Ray Strode <rstrode@redhat.com> 2.8.0-6
- Rebuild for devel branch

 * Tue Nov 02 2004 Ray Strode <rstrode@redhat.com> 2.8.0-5
- Convert Tamil translation to UTF8 
  (Patch from Lawrence Lim <llim@redhat.com>, bug 135351)

* Fri Oct 08 2004 Ray Strode <rstrode@redhat.com> 2.8.0-4
- Add g-v-m to default session since it wasn't already (?).
- Remove g-v-m from default session on s390

* Thu Oct 07 2004 Ray Strode <rstrode@redhat.com> 2.8.0-3
- Check for NULL program name when looking for client
  match in session.

* Fri Sep 24 2004 Ray Strode <rstrode@redhat.com> 2.8.0-2
- Add "Session" item to More Preferences menu

* Fri Sep 17 2004 Ray Strode <rstrode@redhat.com> 2.8.0-1
- Update to 2.8.0 
- Remove "Session" item from Preferences menu

* Fri Sep 03 2004 Ray Strode <rstrode@redhat.com> 2.7.91-2
- Fix from Federico for infamous hanging splash screen problem.
  (http://bugzilla.gnome.org/show_bug.cgi?id=151664)

* Tue Aug 31 2004 Ray Strode <rstrode@redhat.com> 2.7.91-1
- Update to 2.7.91

* Wed Aug 18 2004 Ray Strode <rstrode@redhat.com> 2.7.4-3
- Change folder name from "autostart" to more aptly named
  "session-upgrades" from suggestion by Colin Walters.
- put non-upstream gconf key in rh_extensions

* Wed Aug 18 2004 Ray Strode <rstrode@redhat.com> 2.7.4-2
- Provide drop-a-desktop-file method of adding programs
  to the user's session.

* Fri Jul 30 2004 Ray Strode <rstrode@redhat.com> 2.7.4-1
- Update to 2.7.4

* Wed Jul 14 2004 root <markmc@localhost.localdomain> - 2.6.0-7
- Add patch to activate vino based on the "remote_access/enabled"
  preference

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Jun 14 2004 Ray Strode <rstrode@redhat.com> 2.6.0-5
- Prevent having duplicate packages in different collections

* Mon Jun 14 2004 Ray Strode <rstrode@redhat.com> 2.6.0-4
- Use desktop-file-install instead of patching 
  session-properties.desktop.  Add X-Red-Hat-Base category.

* Thu Jun 10 2004 Ray Strode <rstrode@redhat.com> 2.6.0-3
- Add terminating list delimiter to OnlyShowIn entry of 
  session-properties.desktop

* Fri Apr 16 2004 Warren Togami <wtogami@redhat.com> 2.6.0-2
- #110725 BR automake14 autoconf gettext

* Wed Mar 31 2004 Mark McLoughlin <markmc@redhat.com> 2.6.0-1
- Update to 2.6.0

* Wed Mar 10 2004 Mark McLoughlin <markmc@redhat.com>
- Update to 2.5.91

* Tue Feb 24 2004 Mark McLoughlin <markmc@redhat.com> 2.5.90-1
- Update to 2.5.90
- Remove extraneous fontconfig BuildRequires
- Resolve conflicts with the icons and splash-repaint patches

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Jan 26 2004 Alexander Larsson <alexl@redhat.com> 2.5.3-1
- Update to 2.5.3

* Wed Nov 05 2003 Than Ngo <than@redhat.com> 2.4.0-2
- don't show gnome-session-properties in KDE (bug #102533)

* Fri Aug 29 2003 Alexander Larsson <alexl@redhat.com> 2.3.7-3
- fix up gnome.desktop location

* Fri Aug 29 2003 Alexander Larsson <alexl@redhat.com> 2.3.7-2
- add gnome.desktop session for new gdm

* Wed Aug 27 2003 Alexander Larsson <alexl@redhat.com> 2.3.7-1
- update to 2.3.7
- require control-center (#100562)

* Fri Aug 15 2003 Alexander Larsson <alexl@redhat.com> 2.3.6.2-1
- update for gnome 2.3

* Sun Aug 10 2003 Elliot Lee <sopwith@redhat.com> 2.2.2-4
- Rebuild

* Tue Jul 22 2003 Jonathan Blandford <jrb@redhat.com>
- at-startup patch to add let at's start

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jun  3 2003 Jeff Johnson <jbj@redhat.com>
- add explicit epoch's where needed.

* Tue May 27 2003 Alexander Larsson <alexl@redhat.com> 2.2.2-1
- Update to 2.2.2
- Add XRandR backport
- Fix up old patches, patch7 was upstream

* Mon Feb 24 2003 Owen Taylor <otaylor@redhat.com> 2.2.0.2-5
- Wait for GSD to start before continuing with session

* Tue Feb 18 2003 Havoc Pennington <hp@redhat.com> 2.2.0.2-4
- repaint proper area of text in splash screen, #84527

* Tue Feb 18 2003 Havoc Pennington <hp@redhat.com> 2.2.0.2-3
- change icon for magicdev to one that exists in Bluecurve theme
  (part of #84491)

* Thu Feb 13 2003 Havoc Pennington <hp@redhat.com> 2.2.0.2-2
- load icons from icon theme

* Wed Feb  5 2003 Havoc Pennington <hp@redhat.com> 2.2.0.2-1
- 2.2.0.2

* Tue Feb  4 2003 Jonathan Blandford <jrb@redhat.com>
- remove extraneous separator.  Still ugly.

* Wed Jan 29 2003 Havoc Pennington <hp@redhat.com>
- add icons for the stuff in the default session #81489

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Sat Jan 11 2003 Havoc Pennington <hp@redhat.com>
- 2.1.90
- drop purgedelay patch, as it was increased upstream (though only to 2 minutes instead of 5)

* Fri Dec  6 2002 Tim Waugh <twaugh@redhat.com> 2.1.2-2
- Add eggcups to default session.

* Wed Nov 13 2002 Havoc Pennington <hp@redhat.com>
- 2.1.2

* Tue Sep  3 2002 Owen Taylor <otaylor@redhat.com>
- Up purge delay for session manager to 5 minutes to avoid problem 
  with openoffice.org timing out

* Wed Aug 28 2002 Havoc Pennington <hp@redhat.com>
- put gdm session in here, conflict with old gdm
- use DITHER_MAX for dithering to make splash screen look good in 16
  bit

* Tue Aug 27 2002 Havoc Pennington <hp@redhat.com>
- fix missing icons and misaligned text in splash

* Fri Aug 23 2002 Tim Waugh <twaugh@redhat.com>
- Fix login sound disabling (bug #71664).

* Wed Aug 14 2002 Havoc Pennington <hp@redhat.com>
- put rhn applet in default session

* Wed Aug 14 2002 Havoc Pennington <hp@redhat.com>
- fix the session file, should speed up login a lot
- put magicdev in default session

* Thu Aug  8 2002 Havoc Pennington <hp@redhat.com>
- 2.0.5 with more translations

* Tue Aug  6 2002 Havoc Pennington <hp@redhat.com>
- 2.0.4
- remove gnome-settings-daemon from default session

* Wed Jul 31 2002 Havoc Pennington <hp@redhat.com>
- 2.0.3
- remove splash screen, require redhat-artwork instead

* Wed Jul 24 2002 Owen Taylor <otaylor@redhat.com>
- Set GTK_RC_FILES so we can change the gtk1 theme

* Tue Jul 16 2002 Havoc Pennington <hp@redhat.com>
- pass --with-halt-command=/usr/bin/poweroff
  --with-reboot-command=/usr/bin/reboot

* Tue Jun 25 2002 Owen Taylor <otaylor@redhat.com>
- Version 2.0.1, fixing missing po files

* Wed Jun 19 2002 Havoc Pennington <hp@redhat.com>
- put in new default session with pam-panel-icon
- disable schema install in make install, fixes rebuild failure.

* Sun Jun 16 2002 Havoc Pennington <hp@redhat.com>
- rebuild with new libraries

* Thu Jun 13 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Thu Jun 13 2002 Havoc Pennington <hp@redhat.com>
- add fix from Nalin to build require usermode

* Tue Jun 11 2002 Havoc Pennington <hp@redhat.com>
- 2.0.0

* Mon Jun 10 2002 Havoc Pennington <hp@redhat.com>
- install the schemas, so we get a logout dialog and splash
- put in the splash from 7.3

* Sun Jun 09 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Sun Jun 09 2002 Havoc Pennington <hp@redhat.com>
- rebuild in new environment, require newer gtk2

* Sun Jun  9 2002 Havoc Pennington <hp@redhat.com>
- remove obsoletes/provides gnome-core

* Fri Jun 07 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Wed Jun  5 2002 Havoc Pennington <hp@redhat.com>
- 1.5.21

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- 1.5.19
- add more build reqs to chill out build system
- provide gnome-core

* Fri May  3 2002 Havoc Pennington <hp@redhat.com>
- obsolete gnome-core
- 1.5.18

* Fri Apr 19 2002 Havoc Pennington <hp@redhat.com>
- default to metacity

* Tue Apr 16 2002 Havoc Pennington <hp@redhat.com>
- Initial build.


