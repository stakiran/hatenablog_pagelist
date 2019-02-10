@echo off
setlocal
set url=http://stakiran.hatenablog.com/
set inputfilename=stakiran.hatenablog.com.export.txt
set outputfilename=archive_stamemo.md

pushd %~dp0

python generate.py -i %inputfilename% -o %outputfilename% -u %url%

pause
