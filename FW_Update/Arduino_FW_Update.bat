echo off

echo 'Getting the COM port number for the Arduino Due Programming port"
wmic path win32_pnpentity get caption  /format:table | find "Arduino Due Prog" >ProgPort.xml 
set /p ComPortFull=<ProgPort.xml
del ProgPort.xml /f /s /q

IF "%ComPortFull%"=="" (
echo "Arduino Programming port not connected"
goto END
) ELSE (
for /F "tokens=2 delims=()" %%a in ("%ComPortFull%") do (
set ProgrammingPort=%%a
)
)
echo Arduino Due Programming port connected on %ProgrammingPort%

echo 'Erase flash"
@mode %ProgrammingPort%:1200
echo 'Erase flash done"

echo 'WARNING : To allow the Firmware programming to be successfull, be sure that ONLY the programming port of the Arduino Due board is connected !!!"

echo ' '

echo 'Next step = flash programming, wait 1s en press enter"
pause

echo "Flash programming"

@mode %ProgrammingPort%:115200

bossac.exe -i -d --port=%ProgrammingPort% -U false -e -w -v -b i2c_master_due.ino.bin -R

pause