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
Execute the `build.bat` file.
The batch file should install all required dependencies via pip before starting the build process.
If the batch file fully executes successfully, `build`, `dist` and `releases` folders will be created.
The `build` folder is for debugging purposes, the `dist` folder will contain a single sub-folder `SmartScheduler`.
The `SmartScheduler` sub-folder will contain the stand alone exe, and will be packaged in a TAR archive inside `releases`.
