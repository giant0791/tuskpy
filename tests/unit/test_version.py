import importlib.metadata

# The release PR for 0.1.0 (issue #32) removes this test. After the first
# release, tests/e2e/ checks the version format, and release.yml checks
# that the installed version equals the tag.


def test_version_is_0_0_0_before_the_first_release():
    assert importlib.metadata.version("tuskpy") == "0.0.0"
