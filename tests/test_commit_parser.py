import re

import pytest

from cz_magenta.main import commit_regex

commit_pattern = re.compile(commit_regex)


@pytest.mark.parametrize(
    "commit_message,groupdict",
    [
        # Bad commit messages
        ("No scope or ticket number", {}),
        (": missing change verb", {}),
        ("bump: bad change verb", {}),
        ("ci: missing ticket number", {}),
        ("ci: [#] missing ticket number", {}),
        ("ci(: [#1] bad scope", {}),
        ("ci(): [#1] bad scope", {}),
        # Good commit messages
        (
            "feat: [#12345] ordinary change here",
            {
                "type": "feat",
                "scope": None,
                "breaking": None,
                "ticket": "12345",
                "description": "ordinary change here",
                "body": None,
            },
        ),
        (
            "feat!: [#1] breaking change here",
            {
                "type": "feat",
                "scope": None,
                "breaking": "!",
                "ticket": "1",
                "description": "breaking change here",
                "body": None,
            },
        ),
        (
            "feat(module): [#54321] module change here",
            {
                "type": "feat",
                "scope": "module",
                "breaking": None,
                "ticket": "54321",
                "description": "module change here",
                "body": None,
            },
        ),
        (
            "feat(module)!: [#987654321] breaking module change here",
            {
                "type": "feat",
                "scope": "module",
                "breaking": "!",
                "ticket": "987654321",
                "description": "breaking module change here",
                "body": None,
            },
        ),
        (
            "fix(module): [#42069] module fix here",
            {
                "type": "fix",
                "scope": "module",
                "breaking": None,
                "ticket": "42069",
                "description": "module fix here",
                "body": None,
            },
        ),
        (
            "ci(pipeline): [#xxxxx] ad-hoc CI fix here\n\nFull\ndescription\nhere",
            {
                "type": "ci",
                "scope": "pipeline",
                "breaking": None,
                "ticket": "xxxxx",
                "description": "ad-hoc CI fix here",
                "body": "Full\ndescription\nhere",
            },
        ),
        (
            "ci(pipeline): [#xxxxx] tricky ([# This should not conflict])",
            {
                "type": "ci",
                "scope": "pipeline",
                "breaking": None,
                "ticket": "xxxxx",
                "description": "tricky ([# This should not conflict])",
                "body": None,
            },
        ),
    ],
)
def test_parser(commit_message: str, groupdict: dict) -> None:
    x = commit_pattern.match(commit_message)
    expected = {} if x is None else x.groupdict()
    assert expected == groupdict
