@echo off
setlocal EnableDelayedExpansion

:: ------------------------------------------------------------
:: GPU Performance Optimizer - Windows + NVIDIA
:: ------------------------------------------------------------
:: This script switches Windows to a performance-focused power
:: plan and applies NVIDIA command-line tweaks (when supported)
:: to reduce latency on systems with NVIDIA GPUs.
:: ------------------------------------------------------------

:: Check for administrative privileges (required for powercfg / registry / nvidia-smi tweaks)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [!] Please run this script as Administrator ^(right-click ^> Run as administrator^).
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   GPU PERFORMANCE OPTIMIZATION - %DATE% %TIME%
echo ============================================================
echo.

:: Prepare logging
set "LOG_DIR=%~dp0tuning_logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1

for /f "tokens=2 delims==" %%A in ('wmic os get localdatetime /value 2^>nul ^| find "LocalDateTime"') do set "LDT=%%A"
if defined LDT (
    set "STAMP=!LDT:~0,4!-!LDT:~4,2!-!LDT:~6,2!_!LDT:~8,2!-!LDT:~10,2!-!LDT:~12,2!"
) else (
    set "STAMP=%DATE:/=-%_%TIME::=-%"
)
set "LOG_FILE=%LOG_DIR%\gpu_opt_%STAMP%.log"

echo [*] Writing diagnostic output to: "%LOG_FILE%"
echo GPU optimization started at %DATE% %TIME% > "%LOG_FILE%"

echo.
echo [1/4] Capturing current NVIDIA GPU status...
where nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo     [!] NVIDIA command line tools (nvidia-smi) not found. Skipping GPU-specific tweaks.
    echo [!] nvidia-smi not found in PATH. Install/repair NVIDIA drivers with CLI support. >> "%LOG_FILE%"
) else (
    nvidia-smi --query-gpu=name,driver_version,pstate,power.management,power.draw,power.limit,clocks.current.graphics,clocks.current.memory --format=csv >> "%LOG_FILE%" 2>&1
    echo     [+] Saved static GPU snapshot to log.
)

echo.
echo [2/4] Switching Windows power plan to performance focused profile...
set "CURRENT_PLAN="
for /f "tokens=4" %%G in ('powercfg /getactivescheme') do set "CURRENT_PLAN=%%G"
if defined CURRENT_PLAN (
    set "CURRENT_PLAN=%CURRENT_PLAN:~0,36%"
    echo     [i] Current power plan GUID: %CURRENT_PLAN% >> "%LOG_FILE%"
)

set "TARGET_PLAN="
for /f "tokens=4" %%G in ('powercfg /list ^| findstr /i "Ultimate Performance"') do (
    set "TARGET_PLAN=%%G"
)
if defined TARGET_PLAN (
    set "TARGET_PLAN=!TARGET_PLAN:~0,36!"
    powercfg /S !TARGET_PLAN! >> "%LOG_FILE%" 2>&1
    if %errorlevel% equ 0 (
        echo     [+] Ultimate Performance plan activated.
    ) else (
        echo     [!] Failed to activate Ultimate Performance. Falling back to High Performance.
        powercfg /S SCHEME_MIN >> "%LOG_FILE%" 2>&1
    )
) else (
    powercfg /S SCHEME_MIN >> "%LOG_FILE%" 2>&1
    if %errorlevel% equ 0 (
        echo     [+] High Performance plan activated ^(SCHEME_MIN^).
    ) else (
        echo     [!] Unable to switch to High Performance. See log for details.
    )
)

echo     [i] Setting processor performance parameters for AC power...
powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PERFBOOSTMODE 0 >> "%LOG_FILE%" 2>&1
powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 100 >> "%LOG_FILE%" 2>&1
powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMIN 100 >> "%LOG_FILE%" 2>&1
powercfg /setacvalueindex SCHEME_CURRENT SUB_PCIEXPRESS ASPM 0 >> "%LOG_FILE%" 2>&1


echo.
echo [3/4] Applying NVIDIA driver level tweaks (if supported)...
if not exist "%SystemRoot%\System32\nvidia-smi.exe" (
    echo     [!] Native NVIDIA utilities not detected in System32. Skipping persistence/app clock changes.
    echo [!] nvidia-smi.exe missing from System32; persistence mode skipped. >> "%LOG_FILE%"
) else (
    nvidia-smi -pm 1 >> "%LOG_FILE%" 2>&1
    if %errorlevel% equ 0 (
        echo     [+] Persistence mode enabled (keeps GPU in P0 when idle).
    ) else (
        echo     [!] Persistence mode not supported on this GPU/driver.
    )

    nvidia-smi --auto-boost-default=1 >> "%LOG_FILE%" 2>&1
    if %errorlevel% equ 0 (
        echo     [+] Auto-boost default enabled to let the GPU boost clocks under load.
    ) else (
        echo     [!] Auto-boost setting unsupported (expected on consumer/mobile GPUs).
    )
)


if exist "%SystemRoot%\System32\nvidia-smi.exe" (
    nvidia-smi -q -d PERFORMANCE >> "%LOG_FILE%" 2>&1
)

echo.
echo [4/4] Optional Windows GPU scheduling tweak...
reg query "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode >nul 2>&1
if %errorlevel% neq 0 (
    echo     [i] Hardware accelerated GPU scheduling registry key not set. Creating and enabling ^(requires reboot^).
) else (
    echo     [i] Updating Hardware accelerated GPU scheduling to enabled ^(requires reboot^).
)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 1 /f >> "%LOG_FILE%" 2>&1


echo ------------------------------------------------------------ >> "%LOG_FILE%"
echo Final GPU snapshot after tweaks: >> "%LOG_FILE%"
if exist "%SystemRoot%\System32\nvidia-smi.exe" (
    nvidia-smi --query-gpu=name,pstate,clocks.current.graphics,clocks.current.memory,power.draw --format=csv >> "%LOG_FILE%" 2>&1
) else (
    echo nvidia-smi unavailable for final snapshot. >> "%LOG_FILE%"
)

echo.
echo Done!
if defined CURRENT_PLAN (
    echo [i] Original power plan GUID stored in log if you need to restore manually.
)
echo [i] A reboot is recommended for the GPU scheduling change to take effect.
echo.
pause
exit /b 0
