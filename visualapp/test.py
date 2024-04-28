import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_DIR = os.path.join(BASE_DIR, '.venv')
SITE_PACKAGES_DIR = os.path.join(VENV_DIR, 'Lib', 'site-packages')
sys.path.insert(0, SITE_PACKAGES_DIR)

import transformers
print(transformers.__version__)