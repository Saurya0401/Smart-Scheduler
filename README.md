# Smart Scheduler \[Beta Versions\]
Smart Scheduler is a desktop application aimed at helping students at the Faculty of Engineering, Multimedia University,
 with managing their registered subjects and schedule. The application has the following features: <br />
 - Create and manage an account whose data is stored in the cloud and can be accessed from any suitable PC.
 - Register any subject made available by the faculty or edit previously registered subjects.
 - Build and edit a schedule with the registered subjects.
 - Get information about current and upcoming classes in the schedule.
 - Automatically open the current class in a browser window.
 - Open any class link in the browser window from the schedule.
 - Scan QR codes for attendance.

The beta versions of this application are not production ready and are meant for internal use and distribution to the client only.
## Application Releases
The releases of this application can be found in [releases](https://github.com/Saurya0401/Smart-Scheduler/releases), remember to download a beta version release. <br />
Each release will be a `.tar` file containing a single folder, `Smart Scheduler`. This folder will contain the 
application executable `SmartScheduler.exe`, a `config.ini` file, and a sub-folder titled `remote_server`.
## Application GUI Configuration
The `config.ini` file contains configuration info for the GUI. It is not essential for proper functioning of the application, but the application will display a warning if the file is not found or corrupted. <br /> 
The `config.ini` file can be used to change the colours, the font family and the font sizes used in the GUI. 
## Testing
Python 3.8 and above is required for testing.
#### Start Test Server
Start test server in a new console window:
```cmd
cd path/to/base/directory
python -m test.test_server.test_server
```
If the test server starts successfully, the console will print:
```cmd
Test server started.
```
#### Run Tests
Open a new console window before running any tests.
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
#### Stop Test Server
Go back to the test server console, and press `Ctrl` + `C` to stop the test server. The console should print the following:
```cmd
Test server terminated by Ctrl + C.
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
[^2]:  There is a chance that antivirus software may detect the executable binary as a false positive trojan.
