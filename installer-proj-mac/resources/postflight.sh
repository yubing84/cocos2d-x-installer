#!/bin/bash

SRC_X_DIR="/Applications/cocos/frameworks/cocos2d-x"
DST_X_DIR="/Applications/cocos/frameworks/cocos2d-js/frameworks/js-bindings"

REMOVE_LIST=("templates" "tests" "tools")

# copy the -x into -js
if [ -d ${SRC_X_DIR} ]; then
    if [ ! -d "${DST_X_DIR}" ]; then
        mkdir -p "${DST_X_DIR}"
    fi
    cp -R ${SRC_X_DIR} ${DST_X_DIR}

    # modify the macro
    CONFIG_FILE="${DST_X_DIR}/cocos2d-x/cocos/base/ccConfig.h"
    if [ -f ${CONFIG_FILE} ]; then
        # get the match line
        MATCH_LINE=`grep '^#define[ ]\{1,\}CC_CONSTRUCTOR_ACCESS' ${CONFIG_FILE}`

        if [ -n "${MATCH_LINE}" ]; then
            # write temp file
            TEMP_FILE="${CONFIG_FILE}.txt"
            if [ -f "${TEMP_FILE}" ]; then
                rm -f "${TEMP_FILE}"
            fi

            while read LINE
            do
                if [ "${LINE}" = "${MATCH_LINE}" ]; then
                    echo "#define CC_CONSTRUCTOR_ACCESS public" >> "${TEMP_FILE}"
                else
                    echo "${LINE}" >> "${TEMP_FILE}"
                fi
            done  < $CONFIG_FILE

            # delete the config file
            rm -f "${CONFIG_FILE}"

            # rename the temp file
            mv -f "${TEMP_FILE}" "${CONFIG_FILE}"

            # delete the temp file
            rm -f "${TEMP_FILE}"
        fi
    fi

    # remove the dirs not used by js
    REMOVE_NUM=${#REMOVE_LIST[@]}
    for ((i=0; i<${REMOVE_NUM}; i++))
    do
        REMOVE_DIR="${DST_X_DIR}/cocos2d-x/${REMOVE_LIST[$i]}"
        if [ -d "${REMOVE_DIR}" ]; then
            rm -rf "${REMOVE_DIR}"
        fi
    done

    chmod -R a+w "${DST_X_DIR}"
fi

open "/Applications/cocos"
