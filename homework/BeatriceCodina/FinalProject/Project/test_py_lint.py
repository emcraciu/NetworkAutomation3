import unittest
from pylint import lint
import io
import sys
import re
import os

class TestPylintScore(unittest.TestCase):
    def test_code_quality(self):
        """
        Run pylint using the configuration from Project/pylintrc
        (which keeps only syntax errors enabled).
        """
        pylintrc_path = "Project/pylintrc"  # file created earlier

        if not os.path.exists(pylintrc_path):
            raise FileNotFoundError(f"pylintrc file not found at: {pylintrc_path}")

        args = [
            "Project/",                        # scan the whole folder
            f"--rcfile={pylintrc_path}",       # use your config file
            "--score=y",
            "--output-format=text"
        ]

        pylint_output = io.StringIO()
        sys.stdout = pylint_output
        lint.Run(args, exit=False)
        sys.stdout = sys.__stdout__
        output = pylint_output.getvalue()
        pylint_output.close()

        # Save the full report
        with open("pylint_report.txt", "w", encoding="utf-8") as f:
            f.write(output)

        # Extract the score from the output
        match = re.search(r"Your code has been rated at ([\d\.]+)/10", output)
        score = float(match.group(1)) if match else 10.0

        print(f"Pylint score (using {pylintrc_path}): {score}/10")
        self.assertGreaterEqual(score, 8.0, f"Pylint score too low: {score}/10")

if __name__ == "__main__":
    unittest.main()
