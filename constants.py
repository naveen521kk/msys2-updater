import re
from pathlib import Path
checksum_regex = re.compile(r"(?P<type>\w*)sums=\('(?P<checksum_old>.*)'\)")
PACKAGES_PATH = Path('./packages')