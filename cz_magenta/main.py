from commitizen.cz.conventional_commits import ConventionalCommitsCz
from commitizen.cz.exceptions import CzException
from commitizen.defaults import Questions

change_type_map = {
    "build": "Build improvements",
    "ci": "CI improvements",
    "docs": "Documentation",
    "feat": "Features",
    "fix": "Bug Fixes",
    "perf": "Performance improvements",
    "refactor": "Code Refactor",
    "style": "Style",
    "test": "Test improvements",
}
type_regex = "|".join(change_type_map.keys())
commit_regex = (
    f"^(?P<type>{type_regex})"
    "(\\((?P<scope>.+)\\))?"
    "(?P<breaking>!)?"
    ":\\s"
    "(\\[#(?P<ticket>.+)\\]\\s)"
    "(?P<description>.*)?"
    "(\\n\\n(?P<body>(\\n|.)*))?$"
)


class DoNotIncludeBrackets(CzException):
    ...


class TicketNumberShouldBeInteger(CzException):
    ...


def parse_ticketnumber(text: str) -> str:
    # TODO: Extract from branch name?
    if not text:
        return "xxxxx"

    if "[" in text or "]" in text:
        raise DoNotIncludeBrackets("Do not include '[]' in ticket number")

    try:
        ticket_number = int(text)
    except ValueError:
        raise TicketNumberShouldBeInteger("Ticket number should be an integer")
    return ticket_number


class MagentaCz(ConventionalCommitsCz):
    change_type_map = change_type_map
    commit_parser = commit_regex

    def changelog_message_builder_hook(self, parsed_message: dict, commit) -> dict:
        warning = ("\u26A0\uFE0F" + " ") if parsed_message["breaking"] else ""
        body = ("\n\n" + commit.body + "\n") if commit.body else ""
        output = (
            f"{warning}[#{parsed_message['ticket']}] {parsed_message['description']}{body}"
        )
        parsed_message["message"] = output
        return parsed_message

    def questions(self) -> Questions:
        """Questions regarding the commit message."""
        questions = [
            {
                "type": "input",
                "name": "ticket",
                "message": (
                    "What is the relevant ticket number? (press [enter] to skip)\n"
                ),
                "filter": parse_ticketnumber,
            }
        ]
        questions.extend(super().questions())
        return questions

    def message(self, answers: dict) -> str:
        prefix = answers["prefix"]
        scope = answers["scope"]
        ticket = answers["ticket"]
        subject = answers["subject"]
        body = answers["body"]
        footer = answers["footer"]
        is_breaking_change = answers["is_breaking_change"]

        if scope:
            scope = f"({scope})"
        if body:
            body = f"\n\n{body}"
        if is_breaking_change:
            footer = f"BREAKING CHANGE: {footer}"
        if footer:
            footer = f"\n\n{footer}"

        message = f"{prefix}{scope}: [#{ticket}] {subject}{body}{footer}"

        return message

    def example(self) -> str:
        return (
            "fix(module): [#12345] correct minor bug in the code\n"
            "\n"
            "solved the memory leak in module x\n"
            "\n"
            "closes issue #12"
        )

    def schema(self) -> str:
        return (
            "<type>(<scope>): [<ticket>] <subject>\n"
            "<BLANK LINE>\n"
            "<body>\n"
            "<BLANK LINE>\n"
            "(BREAKING CHANGE: )<footer>"
        )

    def schema_pattern(self) -> str:
        return self.commit_parser
