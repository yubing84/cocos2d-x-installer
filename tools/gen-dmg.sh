#!/bin/bash
# gen-dmg.sh

PROJ_NAME=$1

BASEDIR="$( cd "$( dirname "$0" )" && pwd )"
RELEASE_DIR="${BASEDIR}/../release"
PKG_FILE_PATH="${RELEASE_DIR}/${PROJ_NAME}.pkg"

#check if the app is exist
if [ ! -d "${PKG_FILE_PATH}" ]; then
    echo "The app file ${PKG_FILE_PATH} is not exist. Can't create dmg file!"
    exit 1
fi

TARGET_NAME="${PROJ_NAME}.dmg"
TMP_DIR="/tmp/${PROJ_NAME}"
RES_DIR="${BASEDIR}/../installer-proj-mac/resources"

if [ -d "${TMP_DIR}" ]; then
    rm -rf "${TMP_DIR}"
fi

mkdir "${TMP_DIR}"

cp -rf "${PKG_FILE_PATH}" "${TMP_DIR}"

# remove the alias file in pkg
NEED_REMOVE_FILE="${TMP_DIR}/${PROJ_NAME}.pkg/Contents/Resources/${PROJ_NAME}.pax.gz"
if [ -f "${NEED_REMOVE_FILE}" ]; then
    rm -rf "${NEED_REMOVE_FILE}"
fi

# create dmg file
pushd /tmp

"${BASEDIR}/create-dmg/create-dmg" \
    --volicon "${RES_DIR}/Icon.icns" \
    --volname "${PROJ_NAME}" \
    --icon-size 128 \
    "${PROJ_NAME}.dmg" "${TMP_DIR}/${PROJ_NAME}.pkg"

popd

if [ ! -d "${RELEASE_DIR}" ]; then
    mkdir "${RELEASE_DIR}"
fi

# remove the old dmg file in release dir
if [ -f "${RELEASE_DIR}/${TARGET_NAME}" ]; then
    rm -rf "${RELEASE_DIR}/${TARGET_NAME}"
fi

# copy the dmg file from tmp to release dir
cp "/tmp/${TARGET_NAME}" "${RELEASE_DIR}"

# remove temp files
rm -rf "${TMP_DIR}"
rm "/tmp/${TARGET_NAME}"
