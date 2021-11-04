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
pyinstaller --clean --distpath "./Smart Scheduler" smartscheduler_build.spec && (
  ECHO SmartScheduler.exe successfully built.
  (call )
) || (
  ECHO SmartScheduler.exe build failed.
  PAUSE
  exit /b
)
ECHO SmartScheduler.exe placed in dist/SmartScheduler/
ECHO ==============================
ECHO Deleting unnecessary files...
ECHO ==============================
RMDIR /S /Q build && (
  ECHO Unnecessary files deleted.
  (call )
) || (
  ECHO SmartScheduler.exe build failed.
  PAUSE
  exit /b
)
ECHO Build successful.
PAUSE
