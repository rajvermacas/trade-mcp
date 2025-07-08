@echo off
echo Test started at %date% %time% > test_output.txt
echo Python location: >> test_output.txt
where python >> test_output.txt 2>&1
echo. >> test_output.txt
echo Conda location: >> test_output.txt
where conda >> test_output.txt 2>&1
echo. >> test_output.txt
echo Current directory: >> test_output.txt
cd >> test_output.txt
echo. >> test_output.txt
echo Environment variables: >> test_output.txt
set TRADING_MCP >> test_output.txt 2>&1
echo. >> test_output.txt
echo Testing Python import: >> test_output.txt
python -c "import sys; print('Python:', sys.version); print('Path:', sys.executable)" >> test_output.txt 2>&1
echo. >> test_output.txt
echo Testing module import: >> test_output.txt
python -c "import trading_mcp; print('Module found')" >> test_output.txt 2>&1
echo. >> test_output.txt
echo Test completed >> test_output.txt