pkgname = landcarbon
pkgroot = $(pkgname)

staticdir = $(pkgname)/static
appdirs = $(addprefix $(pkgname)/, app)
# Support virtualenvwrapper installations and ../env
venvdir ?= $(or $(wildcard ../env), $(HOME)/.virtualenvs/landcarbon-cdi)

# The order of fixtures is important as we need to preserve the sequence of
# loading.
fixtures = $(pkgname)/app/fixtures/app.json

# Source files
pysrc = $(wildcard $(addsuffix /*.py,$(pkgname) $(appdirs)))

# Environment variables for all subshells.
# Always use a virtualenv.
export VIRTUAL_ENV=$(venvdir)
export PATH := $(venvdir)/bin:$(PATH)

INSTALL ?= install
# Find path to compileall.py to create python bytecode
PYC ?= python $(shell python -c 'import compileall; print(compileall.__file__)')
pyver ?= $(shell python -c \
	"import sys; print('python{}.{}'.format(sys.version_info.major, sys.version_info.minor))")

.PHONY : all build build-static collectstatic clean dist migrate venv venv-*

all: build

%.pyc: %.py
	$(PYC) $^

$(firstword $(mapsrc)): $(pkgname)/templates/coredata/mapstyles.xml
	python manage.py mapconfig --map > $@

$(lastword $(mapsrc)):
	python manage.py mapconfig --tiles > $@

# Create virtualenv for managing Python dependencies
venv: $(venvdir)/bin/activate
$(venvdir)/bin/activate: requirements.txt
	test -d $(venvdir) || virtualenv $(venvdir)
# Use this version of pip to avoid incompatible flags below.
	. $@; pip install "pip==8.1.2"
# Numpy must be installed before any packages which depend on it so we can
# specify the correct headers within the virtualenv and avoid the system version.
	. $@; pip install "$$(grep '^numpy==' $^)"
# Set includes for the proper Numpy headers. GDAL also needs the header
# location specified to compile the Python bindings.
	. $@; CFLAGS="-I/usr/include/gdal -I$$VIRTUAL_ENV/lib/$(pyver)/site-packages/numpy/core/include" pip install -r $^
	touch $@

build: venv migrate collectstatic $(addsuffix c, $(pysrc))

install:
	@$(INSTALL) -d -m755 $(addprefix $(DESTDIR)$(pkgroot)/, \
							$(sort $(dir $(pysrc))) $(staticdir))
	@git rev-parse HEAD > $(DESTDIR)$(pkgroot)/revision.txt
	@$(INSTALL) -m644 $(wildcard $(addprefix $(pkgname)/, *.py*)) \
		$(DESTDIR)$(pkgroot)/$(pkgname)
	@cp -r $(appdirs) $(DESTDIR)$(pkgroot)/$(pkgname)
	@$(INSTALL) -m644 manage.py Makefile requirements.txt $(DESTDIR)$(pkgroot)
	@rm $(DESTDIR)$(pkgroot)/landcarbon/settings_*.py*

uninstall:
	-[ -d pkg/landcarbon ] && rm -r pkg/landcarbon

clean:
	-[ -d $(staticdir)/build ] && rm -r $(staticdir)/build
	-rm $(mapsrc)

# Create a basic installable package for deployment
package:
	$(MAKE) DESTDIR=pkg/ install
	cd pkg && tar -czf $(pkgname)-$$(date +%Y%m%d).tar.gz $(pkgroot)

# Create a source only tarball for release
dist:
	@$(INSTALL) -d $@
	git archive --prefix=$(pkgname)/ -o $@/$(pkgname)-$$(date +%Y%m%d).tar.gz HEAD

# Run unit tests
check:
	python manage.py test --settings=landcarbon.settings_test \
		$(subst /,.,$(appdirs))

$(dir $(fixtures)): $(fixtures)
	python manage.py loaddata $(filter $@%, $^)
	@touch $@

migrate:
	@install -d logs
	python manage.py migrate $*
#migrate-%:
#	@install -d logs
#	python manage.py migrate $*

# Run migrations for all defined apps
#migrate: $(addprefix migrate-, $(notdir $(appdirs))) $(dir $(fixtures))

collectstatic:
	-@[ -d $(staticdir)/public ] && rm -r $(staticdir)/public
	@python manage.py collectstatic --noinput -i '*component*'
