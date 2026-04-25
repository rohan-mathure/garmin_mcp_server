from garmin_mcp.server import mcp

# Import all tool modules to register their @mcp.tool() decorators
import garmin_mcp.tools.auth  # noqa: F401
import garmin_mcp.tools.daily  # noqa: F401
import garmin_mcp.tools.activities  # noqa: F401
import garmin_mcp.tools.body  # noqa: F401
import garmin_mcp.tools.devices  # noqa: F401


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
