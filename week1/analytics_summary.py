from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY was not found. Check that it exists in your .env file."
    )

client = OpenAI(api_key=api_key)

DATA_FILE = Path(__file__).parent / "data" / "analytics_data.csv"
OUTPUT_FILE = Path(__file__).parent / "outputs" / "analytics_report.md"


def load_data(file_path: Path) -> pd.DataFrame:
    """Load analytics data from a CSV file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")

    return pd.read_csv(file_path)

def generate_summary(metrics: str) -> str:
    """Generate an executive summary using GPT."""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior digital analytics consultant. "
                    "Analyse the provided metrics and produce a concise executive summary."
                ),
            },
            {
                "role": "user",
                "content": metrics,
            },
        ],
    )
    return response.choices[0].message.content


def save_report(summary: str, output_path: Path) -> None:
    """Save the generated summary as a Markdown file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")


def main() -> None:
    data = load_data(DATA_FILE)
    total_sessions = data["sessions"].sum()
    total_conversions = data["conversions"].sum()
    total_revenue = data["revenue"].sum()
    conversion_rate = total_conversions / total_sessions * 100
    print(f"Total sessions: {total_sessions}")
    print(f"Total conversions: {total_conversions}")
    print(f"Total revenue: £{total_revenue}")
    print(f"Conversion rate: {conversion_rate:.2f}%")

    metrics = (
        f"Total sessions: {total_sessions}\n"
        f"Total conversions: {total_conversions}\n"
        f"Total revenue: £{total_revenue}\n"
        f"Conversion rate: {conversion_rate:.2f}%"
    )
    
    summary = generate_summary(metrics)
    print("\nExecutive Summary:")
    print(summary)

    save_report(summary, OUTPUT_FILE)
    print(f"\nReport saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()