import os
import requests
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="LinkedIn Post Generator",
    page_icon="💼",
    layout="wide"
)

SYSTEM_PROMPT = """You are an expert LinkedIn copywriter and personal branding strategist.
Write high-performing, engaging LinkedIn posts based on the user's topic and preferences.

Follow these formatting and style rules:
1. Start with a strong, scroll-stopping 1-2 line hook (no generic "I'm excited to announce..." unless requested).
2. Use short paragraphs (1-2 sentences max) with plenty of white space for mobile readability.
3. Deliver genuine insight, actionable takeaways, or a relatable story.
4. End with a clear, low-friction Call to Action (CTA) question to spark comments.
5. Include 3 to 5 relevant hashtags at the very bottom.
6. Do not wrap the post in quotation marks or add introductory filler text—output ONLY the ready-to-paste LinkedIn post."""

def generate_linkedin_post(api_key, topic, tone, audience, length, include_emojis, model_name):
    emoji_instruction = (
        "Use tasteful, relevant emojis to emphasize key points."
        if include_emojis
        else "Do NOT use any emojis."
    )

    user_prompt = f"""
Topic / Rough Notes: {topic}
Target Audience: {audience}
Tone: {tone}
Desired Length: {length}
Emoji Preference: {emoji_instruction}
"""

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    data = response.json()

    if response.status_code != 200:
        error_msg = data.get("error", {}).get("message", f"HTTP {response.status_code}")
        raise RuntimeError(f"Groq API Error: {error_msg}")

    return data["choices"][0]["message"]["content"].strip()


# --- Sidebar: Configuration & API Key ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Checks Streamlit Secrets first, falls back to user input
    default_key = st.secrets.get("GROQ_API_KEY", "") if hasattr(st, "secrets") else ""
    api_key = st.text_input(
        "Groq API Key",
        value=default_key,
        type="password",
        placeholder="gsk_...",
        help="Get a free API key from console.groq.com"
    )

    model_name = st.selectbox(
        "Groq Model",
        options=[
            "llama-3.3-70b-versatile",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "llama-3.1-8b-instant"
        ],
        index=0
    )

    st.divider()
    st.markdown(
        "💡 **Tip:** When deploying on Streamlit Cloud, you can add `GROQ_API_KEY` "
        "in **App Settings → Secrets** so you don't have to paste it manually each time."
    )

# --- Main UI ---
st.title("💼 LinkedIn Post Generator")
st.markdown("Turn rough notes or ideas into scroll-stopping LinkedIn posts powered by **Groq**.")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Post Details")
    topic = st.text_area(
        "Topic, Story, or Rough Notes",
        placeholder="e.g., 3 lessons I learned building and deploying my first AI app...",
        height=160
    )

    audience = st.text_input(
        "Target Audience",
        value="Tech professionals, founders, and developers"
    )

    c1, c2 = st.columns(2)
    with c1:
        tone = st.selectbox(
            "Tone",
            options=[
                "Professional & Insightful",
                "Storytelling & Vulnerable",
                "Bold & Contrarian",
                "Educational / How-To",
                "Casual & Conversational"
            ]
        )
    with c2:
        length = st.selectbox(
            "Post Length",
            options=[
                "Short & Punchy (~100 words)",
                "Medium (~200 words)",
                "Long-form Deep Dive (~350 words)"
            ],
            index=1
        )

    include_emojis = st.checkbox("Include Emojis", value=True)
    generate_clicked = st.button("Generate LinkedIn Post ✨", type="primary", use_container_width=True)

with col2:
    st.subheader("2. Generated Post")
    
    if "generated_post" not in st.session_state:
        st.session_state.generated_post = ""

    if generate_clicked:
        if not api_key.strip():
            st.error("Please enter your Groq API key in the sidebar.")
        elif not topic.strip():
            st.warning("Please enter a topic or rough notes first.")
        else:
            with st.spinner("Crafting your LinkedIn post..."):
                try:
                    st.session_state.generated_post = generate_linkedin_post(
                        api_key=api_key,
                        topic=topic,
                        tone=tone,
                        audience=audience,
                        length=length,
                        include_emojis=include_emojis,
                        model_name=model_name
                    )
                except Exception as e:
                    st.error(str(e))

    if st.session_state.generated_post:
        st.text_area(
            "Ready to copy & paste:",
            value=st.session_state.generated_post,
            height=340
        )
        # Code block provides a built-in one-click copy icon in the top-right corner
        st.caption("Quick Copy:")
        st.code(st.session_state.generated_post, language=None)
    else:
        st.info("Fill in your topic on the left and click **Generate LinkedIn Post ✨**.")
