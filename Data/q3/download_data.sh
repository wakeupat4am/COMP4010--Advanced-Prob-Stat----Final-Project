#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

gdown --folder https://drive.google.com/drive/folders/18S-Q2UA7w5cjqkmbkbxgyxvhvpCbEQbg?usp=drive_link
gdown --folder https://drive.google.com/drive/folders/14xQKGheTF8nNUjMTYfeMopH8998bD7SI?usp=drive_link
