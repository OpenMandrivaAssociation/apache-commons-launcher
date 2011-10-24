%global base_name launcher
%global short_name commons-%{base_name}

Name:          apache-%{short_name}
Version:       1.1
Release:       7.20100521svn936225
Summary:       A cross platform Java application launcher
Group:         Development/Java
License:       ASL 2.0
URL:           http://commons.apache.org/%{base_name}/

# The last release of this package was many years ago and in that time there
# have only been two extremely minor changes to the source code, [1] and [2].
# It seems a new release is unlikely to be forthcoming in the near future.
# 
# [1] - http://svn.apache.org/viewvc/commons/proper/launcher/trunk/src/java/org/apache/commons/launcher/ChildMain.java?r1=138801&r2=138803
# [2] - http://svn.apache.org/viewvc/commons/proper/launcher/trunk/src/java/org/apache/commons/launcher/Launcher.java?r1=138801&r2=138802
# 
# During that time however, support for the maven 2 build system has been
# added. So in order to make my life easier as a maintainer, with regard to
# supporting OSGi manifests and installing poms, etc, I have elected to package
# a maven2 supporting snapshot instead of maintaining patches in our SRPM. As
# an added bonus, the snapshot also has more accurate javadocs.
# 
# How to generate source tarball from source control:
#  $ svn export -r 936225 http://svn.apache.org/repos/asf/commons/proper/launcher/trunk/ commons-launcher-1.1-src
#  $ tar -zcf commons-launcher-1.1-src.tar.gz commons-launcher-1.1-src
Source0:       %{short_name}-%{version}-src.tar.gz

# remove unnecessary build dependency on ant-optional (ant no longer ships this jar)
Patch0:        %{short_name}-pom.patch

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:     noarch

BuildRequires: java-devel >= 0:1.6.0
BuildRequires: jpackage-utils
BuildRequires: maven-antrun-plugin
BuildRequires: maven-assembly-plugin
BuildRequires: maven-compiler-plugin
BuildRequires: maven-idea-plugin
BuildRequires: maven-install-plugin
BuildRequires: maven-jar-plugin
BuildRequires: maven-javadoc-plugin
BuildRequires: maven-resources-plugin
BuildRequires: maven-doxia-sitetools
BuildRequires: maven-plugin-bundle
BuildRequires: maven-surefire-maven-plugin
BuildRequires: maven-surefire-provider-junit
Requires:      java >= 0:1.6.0
Requires:      jpackage-utils
Requires(post):jpackage-utils
Requires(postun):jpackage-utils

Provides:      jakarta-%{short_name} = %{version}-%{release}
Obsoletes:     jakarta-%{short_name} < %{version}-%{release}

%description
Commons-launcher eliminates the need for a batch or shell script to launch a 
Java class. Some situations where elimination of a batch or shell script may 
be desirable are:

* You want to avoid having to determining where certain application paths are
e.g. your application's home directory, etc. Determining this dynamically in 
a Windows batch scripts is very tricky on some versions of Windows or when 
soft links are used on Unix platforms.

* You want to avoid having to handle native file and path separators or native
path quoting issues.

* You need to enforce certain system properties.

* You want to allow users to pass in custom JVM arguments or system properties
without having to parse and reorder arguments in your script. This can be 
tricky and/or messy in batch and shell scripts.

* You want to bootstrap system properties from a configuration file instead 
hard-coding them in your batch and shell scripts.

* You want to provide localized error messages which is very tricky to do in
batch and shell scripts.

%package javadoc
Summary:       API documentation for %{name}
Group:         Development/Java
Requires:      jpackage-utils
Obsoletes:     jakarta-%{short_name}-javadoc < %{version}-%{release}

%description javadoc
%{summary}.

%prep
%setup -q -n %{short_name}-%{version}-src

# apply patches
%patch0 -p0 -b .orig

sed -i 's/\r//' README.txt LICENSE.txt NOTICE.txt
sed -i "s|\<groupId\>ant\<\/groupId\>|<groupId>org.apache.ant</groupId>|g" build.xml

%build
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mkdir -p $MAVEN_REPO_LOCAL

mvn-jpp -Dmaven.repo.local=$MAVEN_REPO_LOCAL install javadoc:javadoc

%install
rm -rf %{buildroot}

# jars
install -pD -T target/%{short_name}-%{version}.jar \
  %{buildroot}%{_javadir}/%{short_name}-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|%{short_name}|%{name}|g"`; done)
(cd %{buildroot}%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

# javadocs
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -pr target/site/apidocs/* %{buildroot}%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

# pom
install -pD -T -m 644 pom.xml %{buildroot}%{_mavenpomdir}/JPP-%{short_name}.pom
%add_to_maven_depmap org.apache.commons %{short_name} %{version} JPP %{short_name}

# following line is only for backwards compatibility. New packages
# should use proper groupid org.apache.commons
%add_to_maven_depmap %{short_name} %{short_name} %{version} JPP %{short_name}

%clean
rm -rf %{buildroot}

%post
%update_maven_depmap

%postun
%update_maven_depmap

%files
%defattr(-,root,root,-)
%doc LICENSE.txt NOTICE.txt README.txt
%{_mavendepmapfragdir}/*
%{_mavenpomdir}/*
%{_javadir}/*

%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}

