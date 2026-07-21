from models import OppositionReport


def format_report(
    report: OppositionReport,
) -> str:
    """
    Convert a structured OppositionReport
    into a readable markdown report.
    """

    output = []

    output.append("# Opposition Analysis Report\n")

    output.append(
        "## Executive Summary\n"
    )

    output.append(
        report.executive_summary
    )

    output.append(
        "\n## Team Strengths\n"
    )

    for strength in report.team_strengths:
        output.append(
            f"- {strength}"
        )

    output.append(
        "\n## Opponent Strengths\n"
    )

    for strength in report.opponent_strengths:
        output.append(
            f"- {strength}"
        )

    output.append(
        "\n## Opponent Weaknesses\n"
    )

    for weakness in report.opponent_weaknesses:
        output.append(
            f"- {weakness}"
        )

    output.append(
        "\n## Key Battles\n"
    )

    for battle in report.key_battles:

        output.append(
            f"### {battle.area}"
        )

        output.append(
            battle.detail
        )

    output.append(
        "\n## Risks\n"
    )

    for risk in report.risks:

        output.append(
            f"### {risk.area}"
        )

        output.append(
            f"Evidence: {risk.evidence}"
        )

        output.append(
            f"Implication: {risk.implication}"
        )

    return "\n\n".join(output)