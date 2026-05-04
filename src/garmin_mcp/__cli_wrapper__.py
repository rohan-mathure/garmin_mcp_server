"""Wrapper for PyInstaller to build CLI binary."""

if __name__ == "__main__":
    from garmin_mcp.cli.__main__ import app

    app()
