#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
cd ${REPO_ROOT}

HOST_TRIPLET=$(rustc -Vv | grep host | cut -f2 -d' ')

uv run pyinstaller --clean webapp.spec
mkdir tauri-app/src-tauri/binaries
cp dist/tracker tauri-app/src-tauri/binaries/tracker-${HOST_TRIPLET}
pnpm tauri build