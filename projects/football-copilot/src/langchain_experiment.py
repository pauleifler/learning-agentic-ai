from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from tools import compare_teams
import pandas as pd

model = ChatOpenAI(
    model="gpt-4.1-mini"
)

def create_compare_teams_tool(data: pd.DataFrame):
    """
    Create a LangChain tool that compares two teams using
    the application's shared football dataset.
    """

    @tool
    def compare_teams_tool(
        team: str,
        opponent: str,
        league: str,
        analysis_date: str,
    ) -> dict:
        """
        Compare two football teams using season, recent,
        home and away performance statistics.
        """

        return compare_teams(
            data=data,
            team=team,
            opponent=opponent,
            league=league,
            analysis_date=analysis_date,
        )

    return compare_teams_tool