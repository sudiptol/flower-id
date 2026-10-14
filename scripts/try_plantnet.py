"""Send one photo to Pl@ntNet from Terminal and print the raw reply. Uses 1 of the 500 daily identifications.

Usage (from the project folder, with .venv active):
    python scripts/try_plantnet.py path/to/photo.jpg
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

# Let this script find plantnet.py in the folder above.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from plantnet import identify_with_plantnet  # noqa: E402

load_dotenv()

photo_path = Path(sys.argv[1])
response = identify_with_plantnet(photo_path.read_bytes())

print("Status code:", response.status_code)
try:
    print(json.dumps(response.json(), indent=2))
except ValueError:
    print(response.text)
