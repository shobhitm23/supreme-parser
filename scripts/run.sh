#!/bin/bash -ex
# /app/test-files must exist as it is used as a mount point within testing
docker run -d -v $1:/app/test-files -p 8279:8279 supreme-parser:latest
