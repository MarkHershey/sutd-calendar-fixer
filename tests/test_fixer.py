import sys
from pathlib import Path
from unittest import TestCase

sys.path.append(str(Path(__file__).parent.parent / "src"))
from calendarFixer import fix

test_dir = Path(__file__).parent
resources_dir = test_dir / "resources"
in_dir = resources_dir / "ics_inputs"
out_dir = resources_dir / "ics_outputs"


class TestFixer(TestCase):
    def test_fix(self):
        # get test files
        test_files = list(in_dir.glob("*.ics"))
        test_files.sort()
        for test_file in test_files:
            with self.subTest(test_file=test_file):
                # read expected output file
                expected_out = out_dir / test_file.name

                # run the fixer
                fixed_lines = fix(
                    ics_path=test_file,
                    out_path=expected_out,
                    overwrite=True,
                )

                # make sure the output file is produced
                self.assertTrue(expected_out.exists())

                # NOTE: this unit test does not check the correctness of the fixer
                #       it only checks if the fixer runs without error
                # NOTE: please manually check the changes using 'git diff' or similar tools
                #       to ensure any differences made are correct and desired.


if __name__ == "__main__":
    from unittest import main

    main()
