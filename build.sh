#!/usr/bin/env bash
set -euo pipefail

while [[ $# -gt 0 ]]; do
    case "$1" in
        -a|--all)
            BUILD_ALL=1
            shift
            ;;
        -t|--tauri)
            BUILD_TAURI=1
            shift
            ;;
        -s|--streamlit)
            BUILD_STREAMLIT=1
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [-a|--all] [-t|--tauri] [-s|--streamlit] [-h|--help]"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

REPO_ROOT=$(git rev-parse --show-toplevel)
cd ${REPO_ROOT}

if [[ ${BUILD_ALL:-0} == 1 ]] || [[ ${BUILD_STREAMLIT:-0} == 1 ]]; then 
    uv run pyinstaller --clean webapp.spec
fi

if [[ ${BUILD_ALL:-0} == 1 ]] || [[ ${BUILD_TAURI:-0} == 1 ]]; then 
    HOST_TRIPLET=$(rustc -Vv | grep host | cut -f2 -d' ')
    mkdir -p tauri-app/binaries
    PRACTICUM_TRACKER_DB=${PRACTICUM_TRACKER_DB:-} cp -f dist/tracker tauri-app/binaries/tracker-${HOST_TRIPLET}
    pnpm tauri build
fi