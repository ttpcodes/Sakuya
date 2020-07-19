#!/usr/bin/env bash
# This script requires grpcio-tools to run.
cd $(dirname $(realpath $0))
python -m grpc_tools.protoc -I MeteoNook/proto --python_out=proto --grpc_python_out=proto MeteoNook/proto/meteonook.proto
sed -i 's/import meteonook_pb2/import sakuya.plugins.acnh.proto.meteonook_pb2/g' proto/meteonook_pb2_grpc.py
