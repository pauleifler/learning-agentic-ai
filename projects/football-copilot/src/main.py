from pathlib import Path
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from pprint import pprint
import json
from data_loader import load_match_data
from agent import run_agent
from datetime import date
from typing import Any
from models import AgentResult

def ask_football_copilot(
    user_question: str,
    conversation_history: list[dict],
    data,
    league: str | None = None,
    team: str | None = None,
    analysis_date: date | None = None,
) -> AgentResult:
    """
    Send a user's question to the football agent and return its answer.

    Optional league and team selections are added as context to reduce
    ambiguity in the user's question.
    """

    context = []

    if league:
        context.append(f"Selected league: {league}")

    if team:
        context.append(f"Selected team: {team}")

    if analysis_date:
        context.append(
            f"Analysis date: {analysis_date.isoformat()}"
        )

    context.append(f"User question: {user_question}")

    enriched_question = "\n".join(context)

    return run_agent(
        user_message=enriched_question,
        conversation_history=conversation_history,
        data=data,
    )

def main():

    data = load_match_data()

    question = (
        "Which three teams had the best defensive record "
        "on 11 April 2025?"
    )

    answer = ask_football_copilot(
        user_question=question,
        data=data,
        league="Premier League",
    )

    print(answer)



if __name__ == "__main__":
    main()