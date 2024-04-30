#!/bin/sh -eu

cd "`git rev-parse --show-toplevel`"

NOINDEX_FILES="./docs-conf/toio.rst ./docs-conf/toio.cube.rst ./docs-conf/toio.cube.api.rst"

if [ "${1:-}" = "--rebuild" ] ; then
  echo "rebuild all documents"
  rm -fr docs docs-conf
fi

if [ ! -d ./docs-conf ] ; then
  echo "generate new sphinx project"
  poetry run sphinx-apidoc -d 3 -F -f -e -A "Sony Interactive Entertainment Inc." -H toio.py -o docs-conf toio toio/device_interface/pythonista3corebluetooth
  poetry run python ./mkdocs/add_noindex.py ${NOINDEX_FILES}

  cp ./mkdocs/conf.py ./docs-conf
  cp ./mkdocs/_templates/version.html ./docs-conf/_templates/

  m2r --overwrite ./pythonista3/*.md
  mv ./pythonista3/*.rst ./docs-conf
fi

poetry run sphinx-build docs-conf docs
poetry run sphinx-multiversion docs-conf docs

LATEST=`git tag --sort=committerdate | egrep -e '^\d+\.\d+\.(\d+|\d(a|b|rc)*\d+|\d+\.post\d+)$' | tail -1`

cp ./mkdocs/index.html ./docs/index.html
pushd docs
ln -s ${LATEST} latest
mkdir examples
pushd examples
ln -s ../../examples/*.py .
ln -s ../../examples-simple/*.py .
popd
../pythonista3/make_install_script.sh install_toio.py
popd
