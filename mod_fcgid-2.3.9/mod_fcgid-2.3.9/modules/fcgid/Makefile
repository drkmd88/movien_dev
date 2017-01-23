##
##  Makefile.apxs -- Build procedure for mod_fcgid Apache module
##
##  Do not use this target; build from the mod_fcgid dir root
##
 
# top_builddir and top_srcdir are misnomers, because build/*.mk
# scripts expect it them be the parent of the build directory,
# and fail to trust the installbuilddir.
exp_installbuilddir=/usr/lib64/httpd/build
top_srcdir=/usr/lib64/httpd
top_builddir=/usr/lib64/httpd

fcgid_builddir=/var/www/movien_dev/mod_fcgid-2.3.9/mod_fcgid-2.3.9
fcgid_srcdir=/var/www/movien_dev/mod_fcgid-2.3.9/mod_fcgid-2.3.9
builddir=/var/www/movien_dev/mod_fcgid-2.3.9/mod_fcgid-2.3.9/modules/fcgid
srcdir=/var/www/movien_dev/mod_fcgid-2.3.9/mod_fcgid-2.3.9/modules/fcgid

CLEAN_TARGETS = *.loT
include /usr/lib64/httpd/build/special.mk

all: local-shared-build all-recursive

#   additional defines, includes and libraries
DEFS=-DFCGID_APXS_BUILD
INCLUDES=-I$(builddir) -I$(srcdir) -I$(fcgid_srcdir)/include
#LIBS=-Lmy/lib/dir -lmylib

