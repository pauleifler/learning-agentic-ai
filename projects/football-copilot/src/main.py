from pathlib import Path
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from pprint import pprint
import json
from data_loader import load_match_data


def main():

    from data_loader import load_match_data
    from agent import run_agent
    from report_formatter import format_report

    data = load_match_data()


    report = run_agent(
        "What are Liverpool's current strengths on 1st October 2024?",
        data,
    )


    formatted_report = format_report(
        report
    )


    print(formatted_report)


if __name__ == "__main__":
    main()