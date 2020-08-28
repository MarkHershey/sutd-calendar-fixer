import sys
from pathlib import Path

curr_folder = Path(__file__).parent.resolve()
project_root = curr_folder.parent
src_path = project_root / "src"

sys.path.insert(0, str(src_path))

import calendarFixer

test_file = "tests/resources/original_ics/schedule.ics"

calendarFixer.fix(test_file)
