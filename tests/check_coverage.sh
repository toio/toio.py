#!/bin/sh -u

cd `git rev-parse --show-toplevel`

poetry run coverage run --source=toio -m pytest

for test_file in examples-simple/* ; do
	echo "*** TEST:${test_file}"
	poetry run coverage run --append --source=toio ${test_file}
done

poetry run coverage report
poetry run coverage html

