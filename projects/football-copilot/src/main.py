from pathlib import Path
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from pprint import pprint
import json
from data_loader import load_match_data
from agent import run_agent


def main():

    data = load_match_data()
    question = "Compare Liverpool and Arsenal on 11 April 2025."

    answer = run_agent(
        user_message=question,
        data=data,
    )

    print(answer)



if __name__ == "__main__":
    main()