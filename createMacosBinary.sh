#!/bin/bash

#Make sure a venv directory is available and pip install -r dependencies has been started
latest_tag=`/usr/bin/git describe --tags --abbrev=0`
replaced_tag=${latest_tag//./_}
basename=dmt-${replaced_tag}-macos
./venv/bin/pyinstaller -y --onefile -w ./src/main.py --name ${basename}
rm -R out
echo ${latest_tag}
mkdir out
cp ./dist/${basename} out
cp dLiveChannelList.xlsx out
cp dLiveChannelList.ods out
echo ${replaced_tag}
cd out
zip -r ${basename}.zip .
mv dmt*.zip ..