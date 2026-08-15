import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PlannerAction:
    name: str
    arguments: tuple[str, ...]


ACTION_PATTERN = re.compile(
    r"^\s*\((\w+)(.*?)\)\s*$"
)


def parse_plan(plan_text: str) -> list[PlannerAction]:

    actions = []

    for line in plan_text.splitlines():

        match = ACTION_PATTERN.match(line)

        if not match:
            continue

        name = match.group(1)
        argument_string = match.group(2).strip()

        arguments = tuple(
            argument_string.split()
        ) if argument_string else ()

        actions.append(
            PlannerAction(
                name=name,
                arguments=arguments,
            )
        )

    return actions