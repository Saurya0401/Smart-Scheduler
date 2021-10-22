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
pyinstaller --onefile smartscheduler.spec && (
  ECHO SmartScheduler.exe successfully built.
  (call )
) || (
  ECHO SmartScheduler.exe build faied.
  PAUSE
  exit /b
)
ECHO SmartScheduler.exe placed in dist/
ECHO Build successful.
PAUSE
