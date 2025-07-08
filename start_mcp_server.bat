@echo off
echo Starting Trading MCP Server... >> mcp_debug.log 2>&1

REM Set environment variable to disable console logging
set TRADING_MCP_LOG_CONSOLE=false

REM Activate conda environment
call C:\Users\mrina\miniconda3\Scripts\activate.bat base >> mcp_debug.log 2>&1
if errorlevel 1 (
    echo Failed to activate conda environment >> mcp_debug.log 2>&1
    exit /b 1
)

REM Change to project directory
cd /d C:\Projects\trade-mcp >> mcp_debug.log 2>&1

REM Run the MCP server
echo Running server... >> mcp_debug.log 2>&1
python -m trading_mcp.server 2>> mcp_debug.log