# ================================================================
#  app.py — Frontend package entry point
#  Mutual Fund Analytics | frontend/app.py
#  (Alternative single-file launch, imports dashboard app)
# ================================================================

"""
This file serves as the frontend package entry.
The main app is in dashboard/streamlit_app.py.

To launch the dashboard, run:
    streamlit run dashboard/streamlit_app.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def launch_dashboard():
    """Launch the Streamlit dashboard as a subprocess."""
    app_path = ROOT / "dashboard" / "streamlit_app.py"
    print(f"Launching dashboard from: {app_path}")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path)],
        cwd=str(ROOT),
    )


if __name__ == "__main__":
    launch_dashboard()
