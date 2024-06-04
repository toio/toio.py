#!/bin/sh -eu
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
REPO_TOP=$(git rev-parse --show-toplevel)

DOWNLOAD_URL="https://toio.github.io/toio.py/examples"
DOWNLOAD_URL_SIMPLE="https://toio.github.io/toio.py/examples-simple"
EXAMPLES_DIR="${REPO_TOP}/docs/examples"
EXAMPLES_SIMPLE_DIR="${REPO_TOP}/docs/examples-simple"

function examples() {
    for pyfile in *.py ; do
        echo "   \"${1}/${pyfile}\","
    done
}

pushd ${EXAMPLES_DIR}
export EXAMPLE_FILES=`examples ${DOWNLOAD_URL}`
popd
pushd ${EXAMPLES_SIMPLE_DIR}
export EXAMPLE_SIMPLE_FILES=`examples ${DOWNLOAD_URL_SIMPLE}`
popd

cat ${SCRIPT_DIR}/install_toio.py.in | envsubst > $1


