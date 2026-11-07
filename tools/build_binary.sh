#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SRC="${PROJECT_ROOT}/assets/binary/vuln.c"
OUT="${PROJECT_ROOT}/assets/binary/vuln"

echo "[*] Compiling ${SRC} -> ${OUT} with protections disabled..."

# Compile without stack protector, with executable stack, without PIE
gcc -std=gnu99 -fno-stack-protector -no-pie -z execstack -Wno-deprecated-declarations -Wno-implicit-function-declaration -o "${OUT}" "${SRC}"

echo "[+] Compilation successful: ${OUT}"
ls -la "${OUT}"

