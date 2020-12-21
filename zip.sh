#!/bin/bash

set -e

TEMPDIR=$(mktemp -d)/qgis-intelligent-search
mkdir -p $TEMPDIR

cp --parents $(git ls-tree --full-tree -r --name-only HEAD) $TEMPDIR

OLD_PWD=$PWD
cd $TEMPDIR/..

if [ -f $OLD_PWD/pth-qgis-plugin.zip ]; then
	rm $OLD_PWD/pth-qgis-plugin.zip
fi

zip $OLD_PWD/pth-qgis-plugin.zip -r qgis-intelligent-search/


