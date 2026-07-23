import streamlit as st

from data_loader import load_match_data
from main import ask_football_copilot


st.set_page_config(
    page_title="Football Copilot",
    page_icon="⚽",
    layout="centered",
)


@st.cache_data
def get_match_data():
    """Load and cache the football match dataset."""
    return load_match_data()


data = get_match_data()

# ---------------------------------------------------------
# Build available league and team options
# ---------------------------------------------------------

league_order = [
    "Premier League",
    "Championship",
    "League One",
    "League Two",
]

available_leagues = set(
    data["league"]
    .dropna()
    .unique()
)

leagues = [
    league
    for league in league_order
    if league in available_leagues
]


with st.sidebar:
    st.title("⚽ Football Copilot")
    st.caption("2024/25 Historic Season")

    st.divider()

    st.write(
        "Historic football analysis powered by an AI agent."
    )

    # ---------------------------------------------------------
    # Optional structured context
    # ---------------------------------------------------------

    with st.expander("Optional context"):

        selected_league_option = st.selectbox(
            "League",
            options=["Not specified"] + leagues,
        )

        selected_league = (
            None
            if selected_league_option == "Not specified"
            else selected_league_option
        )

        if selected_league:
            team_data = data[
                data["league"] == selected_league
            ]
        else:
            team_data = data

        teams = sorted(
            set(team_data["home_team"].dropna())
            | set(team_data["away_team"].dropna())
        )

        selected_team_option = st.selectbox(
            "Team",
            options=["Not specified"] + teams,
        )

        selected_team = (
            None
            if selected_team_option == "Not specified"
            else selected_team_option
        )

        use_analysis_date = st.checkbox(
            "Specify an analysis date"
        )

        if use_analysis_date:
            analysis_date = st.date_input(
                "Analysis date",
                value=data["date"].max().date(),
                min_value=data["date"].min().date(),
                max_value=data["date"].max().date(),
            )
        else:
            analysis_date = None


st.write(
    """
    Ask questions about team performance, league rankings,
    recent form and upcoming fixtures.
    """
)

# ---------------------------------------------------------
# Initialise conversation history
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------------------------------
# Display conversation history
# ---------------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message("user"):
        st.write(message["question"])

    with st.chat_message("assistant"):
        st.markdown(message["answer"])

        tool_calls = message.get("tool_calls", [])

        if tool_calls:
            with st.expander("Tools used"):
                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    arguments = tool_call.get("arguments", {})
                    success = tool_call.get("success", False)

                    if success:
                        st.markdown(f"**✓ `{tool_name}`**")
                    else:
                        st.markdown(f"**✗ `{tool_name}`**")

                    if arguments:
                        st.markdown("**Arguments**")

                        for argument_name, argument_value in arguments.items():
                            st.markdown(
                                f"- `{argument_name}`: {argument_value}"
                            )

                    if not success and tool_call.get("error"):
                        st.error(tool_call["error"])

# ---------------------------------------------------------
# Question form
# ---------------------------------------------------------

with st.form(
    "question_form",
    clear_on_submit=True,
):
    question = st.text_area(
        "Ask a question",
        placeholder=(
            "Examples:\n"
            "Who is ranked 11th for goals scored in the "
            "Premier League on 11 November 2024?\n"
            "How has QPR performed in its last six matches "
            "as of 16 March 2025?\n"
            "How do Man Utd compare with their next opponent "
            "after 1 October 2024?"
        ),
        height=140,
    )

    submitted = st.form_submit_button(
        "Analyse",
        type="primary",
        use_container_width=True,
    )


# ---------------------------------------------------------
# Run the agent
# ---------------------------------------------------------

if submitted:
    cleaned_question = question.strip()

    if not cleaned_question:
        st.warning("Please enter a football question.")

    else:
        try:
            with st.spinner("Analysing football data..."):
                result = ask_football_copilot(
                    user_question=cleaned_question,
                    conversation_history = st.session_state.messages,
                    data=data,
                    league=selected_league,
                    team=selected_team,
                    analysis_date=analysis_date,
                )

            st.session_state.messages.append(
                {
                    "question": cleaned_question,
                    "answer": result["answer"],
                    "tool_calls":result["tool_calls"]
                }
            )

            st.rerun()

        except Exception as error:
            st.error("The analysis could not be completed.")

            with st.expander("Technical details"):
                st.exception(error)