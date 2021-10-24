# Smart Scheduler \[Alpha Versions\]
The alpha versions of this application are not production ready and are meant for internal use only.
## Testing
Run all tests: 
```cmd
cd path/to/base/directory
python -m unittest discover -v -s test
```
Run individual tests:
```cmd
cd path/to/base/directory
python -m unittest -v test.<test_file>
```
## Building
Execute the `build.bat` file[^1].
This batch file should install all required dependencies via pip before starting the build process. <br />
If the batch file executes successfully, `build`, `dist` and `releases` folders will be created.
The `build` folder is for debugging purposes, while the `dist` folder will contain a single sub-folder `SmartScheduler`.
The `SmartScheduler` sub-folder will contain the stand alone `.exe`[^2], and will also itself be packaged in a TAR 
archive inside `releases`. <br />

[^1]:  It is advisable to exclude the directory containing `build.bat` from antivirus programs as they might prevent 
`pyinstaller` from getting access to resources necessary for building the executable binary.
[^2]:  There is a chance that antivirus software may detect the executable binary as false positive trojan.
