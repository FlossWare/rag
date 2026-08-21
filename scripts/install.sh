#!/bin/bash
# Install rag-ai from GitHub
set -e
pip install "git+https://github.com/FlossWare/rag-ai.git"
echo "rag-ai installed successfully"
python3 -c "import rag_ai; print(f'Version: {rag_ai.__version__}')"
