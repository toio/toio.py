#!/bin/sh -eu
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
REPO_TOP=$(git rev-parse --show-toplevel)

DOWNLOAD_URL="https://toio.github.io/toio.py"
EXAMPLES_DIR="${REPO_TOP}/docs/examples"
EXAMPLES_SIMPLE_DIR="${REPO_TOP}/docs/examples-simple"

function examples() {
    for pyfile in *.py ; do
        echo "   \"${DOWNLOAD_URL}/${pyfile}\","
    done
}

pushd ${EXAMPLES_DIR}
export EXAMPLE_FILES=`examples`
popd
pushd ${EXAMPLES_SIMPLE_DIR}
export EXAMPLE_SIMPLE_FILES=`examples`
popd

cat ${SCRIPT_DIR}/install_toio.py.in | envsubst > $1


