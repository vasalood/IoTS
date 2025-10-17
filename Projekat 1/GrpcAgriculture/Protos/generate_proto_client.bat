@echo off
cd /d %~dp0
setlocal

if "%~1"=="" (
    echo Moras proslediti ime .proto fajla, npr:
    echo generate_proto_client.bat greet
    exit /b
)

set PROTO_NAME=%~1

echo Generisanje Python gRPC fajlova iz %PROTO_NAME%.proto...

py -m grpc_tools.protoc -I. ^
    --python_out=../../RESTAgriculture/services/GeneratedProtoClient ^
    --grpc_python_out=../../RESTAgriculture/services/GeneratedProtoClient ^
    %PROTO_NAME%.proto

echo Generisanje zavrseno za %PROTO_NAME%.proto

