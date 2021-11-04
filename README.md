# Smart Scheduler
Smart Scheduler is a desktop application aimed at helping students at the Faculty of Engineering, Multimedia University,
 with managing their registered subjects and schedule. The application has the following features: <br />
 - Create and manage an account whose data is stored in the cloud and can be accessed from any suitable PC.
 - Register any subject made available by the faculty or edit previously registered subjects.
 - Build and edit a schedule with the registered subjects.
 - Get information about current and upcoming classes in the schedule.
 - Automatically open the current class in a browser window.
 - Open any class link in the browser window from the schedule.
 - Scan QR codes for attendance.
## Application Releases
The application releases can be found [here](https://github.com/Saurya0401/Smart-Scheduler/releases). It is recommended to download the latest stable release for the best experience. <br />
Each release will be a `.tar` file containing a single folder, `Smart Scheduler`. This folder will contain the 
application executable `SmartScheduler.exe`, and the `config.ini` configuration file.
## Application GUI Configuration
The `config.ini` file contains configuration info for the GUI. It is not essential for proper functioning of the application, but the application will display a warning if the file is not found or corrupted. <br /> 
This file can be used to change the colours, the font family and the font sizes used in the GUI. 
## Manually Building the Application
*NOTE: Python 3.8 (32-bit) and above is required for the build process.* <br />
To manually build the application, execute the `smartscheduler_build.bat` file[^1].
This batch file should install all required dependencies via pip before starting the build process. <br />
If the batch file executes successfully, a `Smart Scheduler` folder will be created. This folder will contain the executable `SmartScheduler.exe`[^2] and the `config.ini` configuration file. <br />

[^1]:  It is advisable to exclude the directory containing `build.bat` from antivirus programs as they might prevent 
`pyinstaller` from getting access to resources necessary for building the executable binary.
[^2]:  There is a chance that antivirus software may detect the executable binary as a false positive trojan.
