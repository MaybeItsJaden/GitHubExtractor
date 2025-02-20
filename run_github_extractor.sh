#!/bin/bash
echo "Opening GitHub Extractor..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && python3 github_extractor.py\""