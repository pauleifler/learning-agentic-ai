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
    data = pd.read_csv(file_path)
    data["date"] = pd.to_datetime(data["date"])
    data = (
        data
        .sort_values("date")
        .reset_index(drop=True)
    )
    return data


def calculate_metrics(data: pd.DataFrame) -> dict:
    """Calculate key metrics and performance changes."""

    total_sessions = int(data["sessions"].sum())
    total_conversions = int(data["conversions"].sum())
    total_revenue = float(data["revenue"].sum())

    conversion_rate = total_conversions / total_sessions * 100
    revenue_per_session = total_revenue / total_sessions
    average_order_value = total_revenue / total_conversions

    first_day = data.iloc[0]
    last_day = data.iloc[-1]

    sessions_change = (
        (last_day["sessions"] - first_day["sessions"])
        / first_day["sessions"]
        * 100
    )

    conversion_rate_by_day = (
        data["conversions"] / data["sessions"] * 100
    )

    best_conversion_day_index = conversion_rate_by_day.idxmax()
    worst_conversion_day_index = conversion_rate_by_day.idxmin()

    return {
        "total_sessions": total_sessions,
        "total_conversions": total_conversions,
        "total_revenue": total_revenue,
        "conversion_rate": conversion_rate,
        "revenue_per_session": revenue_per_session,
        "average_order_value": average_order_value,
        "sessions_change_first_to_last_day": float(sessions_change),
        "best_conversion_day": str(
            data.loc[best_conversion_day_index, "date"]
        ),
        "best_conversion_rate": float(
            conversion_rate_by_day.loc[best_conversion_day_index]
        ),
        "worst_conversion_day": str(
            data.loc[worst_conversion_day_index, "date"]
        ),
        "worst_conversion_rate": float(
            conversion_rate_by_day.loc[worst_conversion_day_index]
        ),
    }


def format_metrics(metrics: dict) -> str:
    """Convert calculated metrics into readable text."""

    return (
        f"Total sessions: {metrics['total_sessions']}\n"
        f"Total conversions: {metrics['total_conversions']}\n"
        f"Total revenue: £{metrics['total_revenue']:.2f}\n"
        f"Overall conversion rate: {metrics['conversion_rate']:.2f}%\n"
        f"Revenue per session: £{metrics['revenue_per_session']:.2f}\n"
        f"Average order value: £{metrics['average_order_value']:.2f}\n"
        f"Sessions change from first to last day: {metrics['sessions_change_first_to_last_day']:.2f}%\n"
        f"Best conversion day: {metrics['best_conversion_day']} "
        f"({metrics['best_conversion_rate']:.2f}%)\n"
        f"Worst conversion day: {metrics['worst_conversion_day']} "
        f"({metrics['worst_conversion_rate']:.2f}%)"
    )


def build_prompt(metrics_text: str) -> str:

    """Build the analytical instruction sent to the LLM."""

    return f"""
Analyse the calculated digital-performance metrics below.
Your audience is a senior commercial stakeholder.
Produce the following sections:

1. Executive summary
2. Most commercially important findings
3. Potential hypotheses
4. Recommended follow-up analyses
5. Data limitations

Requirements:
- Do not merely repeat the metrics.
- Separate observed facts from hypotheses.
- Do not imply causation from this data.
- Prioritise findings by likely commercial importance.
- Do not invent industry benchmarks.
- State clearly where the available data is insufficient.
- Keep the response concise but analytically substantive.
Calculated metrics:
{metrics_text}

""".strip()


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
    metrics = calculate_metrics(data)
    metrics_text = format_metrics(metrics)
    prompt = build_prompt(metrics_text)
    summary = generate_summary(prompt)
    print("\nExecutive Summary:")
    print(summary)

    save_report(summary, OUTPUT_FILE)
    print(f"\nReport saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()