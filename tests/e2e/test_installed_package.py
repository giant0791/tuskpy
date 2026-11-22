import importlib.metadata
import re

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def test_installed_package_has_a_semver_version():
    assert SEMVER.match(importlib.metadata.version("tuskpy"))
