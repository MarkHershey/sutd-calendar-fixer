import sys
from pathlib import Path

import calendarFixer

curr_folder = Path(__file__).parent.resolve()
project_root = curr_folder.parent
src_path = project_root / "src"

sys.path.insert(0, str(src_path))


test_file = "tests/resources/original_ics/schedule.ics"

calendarFixer.fix(test_file)
