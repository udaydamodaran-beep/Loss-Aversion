import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import os
from datetime import datetime

# Ensure responses.csv will always be saved in the same directory as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "responses.csv")

st.set_page_config(page_title="Stock Simulator", layout="centered")

# Title and intro
st.markdown(
    """
    <div style="background: linear-gradient(90deg, #f0f2f6, #d9e2ec); padding: 20px; border-radius: 10px;">
    <h2 style="text-align:center;">📈 Stock Simulator</h2>
    <p style="text-align:center;">
    You are going to play a game. At every stage of a stock’s price movement, you will be forced to take a decision on whether to <b>buy</b>, <b>hold</b>, or <b>sell</b>. The assumption is that at every stage you have enough money to buy and enough stock to sell.
    </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Define deterministic path
price_path = [125, 100, 90, 100, 110]
stages_text = [
    "You bought a stock at Rs.125. It has now come down to Rs.100. You think now there is a 45% chance that it will rise to Rs.110 and a 55% chance that it will drop to Rs.90. What will you do?",
    "The stock falls to Rs.90. You think now there is a 50% chance that it will rise back to Rs.100 and a 50% chance that it will drop to Rs.78. What will you do?",
    "The stock rises to Rs.100. You think now there is a 50% chance that it will rise back to Rs.110 and a 50% chance that it will drop to Rs.92. What will you do?",
    "The stock rises to Rs.110. You think now there is a 55% chance that it will rise to Rs.115 and a 45% chance that it will drop back to Rs.100. What will you do?"
]

# Session state init
if "stage" not in st.session_state:
    st.session_state.stage = 0
    st.session_state.choices = []

# Function to plot timeline
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
        xaxis_title="Stage",
        yaxis_title="Price (Rs.)",
        template="plotly_white"
    )
    return fig

# Display stage
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

# Final stage handling
else:
    final_price = 115 if random.random() < 0.55 else 100
    full_path = price_path + [final_price]

    st.plotly_chart(plot_timeline(full_path), use_container_width=True)

    st.success(f"The game ends! Final stock price: Rs.{final_price}")

    # Save responses silently
    df = pd.DataFrame({
        "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "choices": [st.session_state.choices],
        "final_price": [final_price]
    })
    if not os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, index=False)
    else:
        df.to_csv(CSV_FILE, mode="a", header=False, index=False)

    # Explanation of loss aversion
    st.markdown(
        """
        ### 💡 Understanding Loss Aversion
        Research in behavioral finance shows that people dislike losses more than they like equivalent gains. 
        This simulation highlights how hard it can be to sell at a loss, even when probabilities suggest it might be rational.
        """
    )

    st.markdown(
        """
        <p style="text-align:center; font-size:13px; color:grey;">
        Developed by Uday Damodaran purely for pedagogical purposes
        </p>
        """,
        unsafe_allow_html=True
    )

    # Reset button
    if st.button("Play Again"):
        st.session_state.stage = 0
        st.session_state.choices = []
        st.rerun()
