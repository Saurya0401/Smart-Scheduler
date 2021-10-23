@ECHO OFF
TITLE Smart Scheduler Builder
ECHO ==============================
ECHO Installing dependencies...
ECHO ==============================
pip install -r requirements.txt && (
  ECHO Dependencies successfully installed.
  (call )
) || (
  ECHO Dependencies installation failed.
  PAUSE
  exit /b
)
ECHO ==============================
ECHO Building SmartScheduler.exe...
ECHO ==============================
pyinstaller --clean --distpath ./dist/SmartScheduler smartscheduler.spec && (
  ECHO SmartScheduler.exe successfully built.
  (call )
) || (
  ECHO SmartScheduler.exe build failed.
  PAUSE
  exit /b
)
ECHO SmartScheduler.exe placed in dist/
ECHO ==============================
ECHO Making SmartScheduler.tar...
ECHO ==============================
if not exist releases mkdir releases
tar -cvf releases\SmartScheduler.tar -C dist SmartScheduler && (
  ECHO SmartScheduler.tar successfully created.
  (call )
) || (
  ECHO SmartScheduler.tar creation failed.
  PAUSE
  exit /b
)
ECHO SmartScheduler.tar placed in releases directory.
ECHO Build successful.
PAUSE
