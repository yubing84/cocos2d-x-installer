#!/bin/bash
INSTALLED_PATH="/Applications/cocos/cocos2d-x"

pushd $INSTALLED_PATH
python ./setup.py
popd
