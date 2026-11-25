import streamlit as st
import google.genai as genai
from PIL import Image

# Page Configuration for Mobile
st.set_page_config(
    page_title="Card Show Negotiator", 
    page_icon="🏷️",
    layout="centered"
)

# Custom CSS for Mobile Card Show UI
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3em; font-size: 1.2rem; font-weight: bold; background-color: #0080FF; color: white; }
    .metric-card { background-color: #1E1E1E; border-radius: 10px; padding: 15px; margin-bottom: 10px; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

st.title("🏷️ Card Show Negotiator")
st.caption("AI-Powered Buying & Pitch Generator")

# Initialize Session State for Free Trial / Credit System
if "scans_left" not in st.session_state:
    st.session_state.scans_left = 3  # 3 Free Scans per session

# Display Scans Remaining Badge
col_a, col_b = st.columns([2, 1])
with col_a:
    st.write(f"🎟️ **Scans Remaining:** {st.session_state.scans_left}")
with col_b:
    if st.session_state.scans_left == 0:
        st.error("Out of Credits")

# Input Form
asking_price = st.number_input("Seller Asking Price ($):", min_value=1.0, value=120.0, step=5.0)
uploaded_file = st.file_uploader("Snap or Upload Card Photo", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Card Preview", use_container_width=True)

    if st.button("🔍 ANALYZE & CALCULATE PITCH"):
        if st.session_state.scans_left <= 0:
            st.warning("⚠️ You've reached your free 3-scan limit! Upgrade to a $4.99 Day Pass for unlimited show scans.")
            st.markdown("[👉 Unlock 24-Hour Card Show Pass ($4.99)](#)") # Add your Stripe link here later
        else:
            # Check for API Key in Secrets
            if "GEMINI_API_KEY" not in st.secrets:
                st.error("API Key missing! Add GEMINI_API_KEY to Streamlit Secrets.")
            else:
                with st.spinner("Analyzing centering, grade floor, and negotiating math..."):
                    try:
                        # Deduct scan
                        st.session_state.scans_left -= 1
                        
                        # Call Gemini API
                        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                        
                        prompt = f"""
                        You are an expert sports card evaluator and buyer's negotiator at a live card show.
                        Analyze this raw card image and the seller's asking price of ${asking_price}.

                        Perform these calculations:
                        1. Inspect centering (top/bottom & left/right ratios), corners, edges, and surface wax/scratches.
                        2. Predict the realistic maximum grade (e.g. PSA 8, PSA 8.5, PSA 9, PSA 10).
                        3. Estimate current market value for that predicted grade.
                        4. Calculate: Max Walk-Away Buy Price = (Predicted Graded Value - $35 Fees) / 1.20 (for 20% margin).
                        5. Write a concise, polite 2-sentence counter-offer script the buyer can read out loud to the seller.

                        Output format strictly in Markdown:
                        ### 📊 AI Condition Report
                        - **Predicted Grade Floor**: [Grade]
                        - **Primary Visual Flaws**: [Details like Top/Bottom 65/35 centering]
                        - **Market Value (Predicted Grade)**: $[Amount]
                        - **Grading & Shipping Fee**: -$35.00

                        ### 🎯 Target Offer
                        - **MAX WALK-AWAY BUY PRICE**: **$[Amount]**
                        - **DEAL STATUS**: [OVERPRICED / FAIR / GREAT DEAL]

                        ### 💬 Verbal Counter-Offer Pitch
                        > "[2-sentence script state the visual flaw, fee math, and cash offer]"
                        """

                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[prompt, image]
                        )

                        st.success("Analysis Complete!")
                        st.markdown(response.text)

                    except Exception as e:
                        st.error(f"Error analyzing image: {str(e)}")
