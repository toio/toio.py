#!/bin/bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "usage: $0 <output file>" >&2
    exit 1
fi

if ! command -v envsubst > /dev/null; then
    echo "envsubst is required (it is included in gettext)" >&2
    exit 1
fi

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_TOP=$(git rev-parse --show-toplevel)

DOWNLOAD_URL="https://toio.github.io/toio.py/examples"
DOWNLOAD_URL_SIMPLE="https://toio.github.io/toio.py/examples-simple"
EXAMPLES_DIR="${REPO_TOP}/docs/examples"
EXAMPLES_SIMPLE_DIR="${REPO_TOP}/docs/examples-simple"

function examples() {
    local directory="${1}"
    local url="${2}"
    local pyfile
    for pyfile in "${directory}"/*.py ; do
        echo "   \"${url}/$(basename "${pyfile}")\","
    done
}

EXAMPLE_FILES=$(examples "${EXAMPLES_DIR}" "${DOWNLOAD_URL}")
EXAMPLE_SIMPLE_FILES=$(examples "${EXAMPLES_SIMPLE_DIR}" "${DOWNLOAD_URL_SIMPLE}")
export EXAMPLE_FILES EXAMPLE_SIMPLE_FILES

# Only these variables are replaced, so a "$" in the template stays as it is.
# shellcheck disable=SC2016
envsubst '${EXAMPLE_FILES} ${EXAMPLE_SIMPLE_FILES}' \
    < "${SCRIPT_DIR}/install_toio.py.in" > "${1}"
