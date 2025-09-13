import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import os
from datetime import datetime

# -----------------------------
# Configuration
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "responses.csv")
TEACHER_SECRET = "mysecret123"  # Change this to your own secret

st.set_page_config(page_title="Stock Simulator", layout="centered")

# -----------------------------
# Intro
# -----------------------------
st.markdown(
    """
    <div style="background: linear-gradient(90deg, #f0f2f6, #d9e2ec); padding: 20px; border-radius: 10px;">
    <h2 style="text-align:center;">📈 Stock Simulator</h2>
    <p style="text-align:center;">
    You are going to play a game. At every stage of a stock’s price movement, you will be forced to take a decision on whether to <b>buy</b>, <b>hold</b>, or <b>sell</b>. 
    The assumption is that at every stage you have enough money to buy and enough stock to sell.
    </p>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Teacher-only CSV download
# -----------------------------
password = st.text_input("Enter teacher password to enable CSV download (hidden from students)", type="password")
if password == TEACHER_SECRET and os.path.exists(CSV_FILE):
    with open(CSV_FILE, "rb") as f:
        st.download_button(
            label="Download Responses CSV",
            data=f,
            file_name="responses.csv",
            mime="text/csv"
        )

# -----------------------------
# Deterministic stock path
# -----------------------------
price_path = [125, 100, 90, 100, 110]
stages_text = [
    "You bought a stock at Rs.125. It has now come down to Rs.100. You think now there is a 45% chance that it will rise to Rs.110 and a 55% chance that it will drop to Rs.90. What will you do?",
    "The stock falls to Rs.90. You think now there is a 50% chance that it will rise back to Rs.100 and a 50% chance that it will drop to Rs.78. What will you do?",
    "The stock rises to Rs.100. You think now there is a 50% chance that it will rise back to Rs.110 and a 50% chance that it will drop to Rs.92. What will you do?",
    "The stock rises to Rs.110. You think now there is a 55% chance that it will rise to Rs.120 and a 45% chance that it will drop back to Rs.100. What will you do?"
]

# -----------------------------
# Session state
# -----------------------------
if "stage" not in st.session_state:
    st.session_state.stage = 0
    st.session_state.choices = []

# -----------------------------
# Plotting function
# -----------------------------
def plot_timeline(prices):
    colors = ["grey"]
    for i in range(1, len(prices)):
        colors.append("green" if prices[i] > prices[i-1] else "red")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(prices))),
        y=prices,
        mode="lines+markers",
        line=dict(color="black"),
        marker=dict(size=10, color=colors)
    ))
    fig.update_layout(
        title="Stock Price Movement",
        xaxis_title="Stock Moves Over Time",
        xaxis=dict(dtick=1),
        yaxis_title="Price (Rs.)",
        template="plotly_white"
    )
    return fig

# -----------------------------
# Game flow
# -----------------------------
if st.session_state.stage < len(stages_text):
    st.markdown(f"**{stages_text[st.session_state.stage]}**")
    st.plotly_chart(plot_timeline(price_path[:st.session_state.stage+2]), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Buy"):
            st.session_state.choices.append("Buy")
            st.session_state.stage += 1
            st.rerun()
    with col2:
        if st.button("Hold"):
            st.session_state.choices.append("Hold")
            st.session_state.stage += 1
            st.rerun()
    with col3:
        if st.button("Sell"):
            st.session_state.choices.append("Sell")
            st.session_state.stage += 1
            st.rerun()

# -----------------------------
# Final stage handling
# -----------------------------
else:
    final_price = 120 if random.random() < 0.55 else 100
    full_path = price_path + [final_price]
    st.plotly_chart(plot_timeline(full_path), use_container_width=True)
    st.success(f"The game ends! Final stock price: Rs.{final_price}")

    # -----------------------------
    # Prepare results table
    # -----------------------------
    moves = [
        ["125 to 100", "110,.45", "90,.55"],
        ["100 to 90", "100,.5", "78,.5"],
        ["90 to 100", "110,.5", "92,.5"],
        ["100 to 110", "120,.55", "100,.45"]
    ]
    row_names = ["1st Stock Move", "2nd Stock Move", "3rd Stock Move", "4th Stock Move"]
    df_table = pd.DataFrame({
        "Previous Move": [m[0] for m in moves],
        "UpMove Forecast": [m[1] for m in moves],
        "Down Move Forecast": [m[2] for m in moves],
        "Your Action": st.session_state.choices
    }, index=row_names)
    st.table(df_table)

    # -----------------------------
    # Save CSV silently
    # -----------------------------
    df_csv = pd.DataFrame({
        "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "choices": [st.session_state.choices],
        "final_price": [final_price]
    })
    if not os.path.exists(CSV_FILE):
        df_csv.to_csv(CSV_FILE, index=False)
    else:
        df_csv.to_csv(CSV_FILE, mode="a", header=False, index=False)

    # -----------------------------
    # Reset button
    # -----------------------------
    if st.button("Play Again"):
        st.session_state.stage = 0
        st.session_state.choices = []
        st.rerun()
