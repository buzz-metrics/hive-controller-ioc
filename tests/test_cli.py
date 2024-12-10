import subprocess
import sys

from hive_controller_ioc import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "hive_controller_ioc", "--version"]
    assert __version__ in subprocess.check_output(cmd).decode().strip()
