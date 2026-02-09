import streamlit as st
import os
import asyncio
import html
from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# ==============================================================================
# PAGE CONFIG
# ==============================================================================
st.set_page_config(page_title="Olive Young In-Store AI", layout="wide")

# --- CUSTOM CSS (keep minimal + right column highlight) ---
st.markdown("""
<style>
    .stTextArea textarea { font-family: monospace; }
    div[data-testid="column"]:nth-of-type(2) {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        border: 1px dashed #ccc;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧴 Olive Young In-Store AI (QR Decision Support)")
st.write("3 features only: Review Summary · Translation · AI Chatbot")

# ==============================================================================
# HELPERS
# ==============================================================================
def run_async(coro):
    """
    Streamlit sometimes runs in an environment where asyncio.run may conflict.
    This helper tries asyncio.run first, then falls back to creating a new loop.
    """
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        finally:
            loop.close()


def safe(s: str) -> str:
    """Escape any model/user text before inserting into HTML."""
    return html.escape(s or "")


def render_card(title: str, badge: str, body_html: str):
    """Simple unified card renderer."""
    return f"""
    <div style="
        background-color: white;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        border: 1px solid #eaeaea;
        font-family: 'Helvetica Neue', sans-serif;
        max-width: 720px;
        margin: 0 auto;
    ">
        <div style="
            display:flex; align-items:center; justify-content:space-between;
            margin-bottom: 14px;
        ">
            <div style="font-size: 18px; font-weight: 900; letter-spacing: 0.2px;">
                {safe(title)}
            </div>
            <div style="
                font-size: 11px;
                background: #111;
                color: #fff;
                padding: 6px 10px;
                border-radius: 999px;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 800;
            ">{safe(badge)}</div>
        </div>
        {body_html}
    </div>
    """


# ==============================================================================
# LAYOUT
# ==============================================================================
left_column, right_column = st.columns([1, 1])

# ==============================================================================
# LEFT: CONTROL CENTER
# ==============================================================================
with left_column:
    st.subheader("🛠️ Control Center")

    # Phase 1: API Activation
    with st.container(border=True):
        st.markdown("#### 1️⃣ API Activation")
        api_key_input = st.text_input(
            "OpenAI API Key:",
            type="password",
            help="Your key is not stored permanently."
        )
        if api_key_input:
            masked = f"{api_key_input[:3]}...{api_key_input[-4:]}"
            st.caption(f"✅ Active: `{masked}`")
            os.environ["OPENAI_API_KEY"] = api_key_input
        else:
            st.caption("🔴 Locked")

    # Phase 2: Service Mode + Inputs
    with st.container(border=True):
        st.markdown("#### 2️⃣ Service Mode & Inputs")

        service_mode = st.selectbox(
            "Choose one feature:",
            ["Review Summary", "Translation", "AI Chatbot"],
            index=0
        )

        tab1, tab2 = st.tabs(["System Persona", "User Inputs"])

        with tab1:
            default_system = (
                "You are an Olive Young in-store assistant. "
                "Be concise, neutral, and practical. Avoid exaggerated marketing."
            )
            system_prompt = st.text_area("System Role", value=default_system, height=120)

        with tab2:
            if service_mode == "Review Summary":
                product_name = st.text_input("Product Name", value="Bringgreen Tea Tree Toner")
                reviews_text = st.text_area(
                    "Paste Reviews (Korean/English mixed OK)",
                    value="지성 피부에 산뜻해요.\n민감 피부는 따가울 수 있어요.\n흡수가 빨라요.",
                    height=140
                )
                summary_lang = st.selectbox("Output Language", ["Korean", "English"], index=0)

            elif service_mode == "Translation":
                source_text = st.text_area(
                    "Text to Translate",
                    value="이 제품은 지성 피부에 산뜻하고, 여름에 사용하기 좋아요.",
                    height=140
                )
                target_lang = st.selectbox(
                    "Target Language",
                    ["English", "Korean", "Japanese", "Chinese (Simplified)"],
                    index=0
                )
                tone = st.selectbox("Tone", ["Natural", "Formal", "Short"], index=0)

            else:  # AI Chatbot
                product_context = st.text_area(
                    "Product Context (short JSON or bullet OK)",
                    value='{"name":"Bringgreen Tea Tree Toner","key_ingredients":["Tea tree","Panthenol"],"skin_type":["oily","combination"]}',
                    height=120
                )
                reviews_hint = st.text_area(
                    "Review Hint (optional)",
                    value="지성 피부에는 산뜻하다는 의견이 많고, 민감 피부는 따가움이 있을 수 있어요.",
                    height=80
                )
                user_question = st.text_area(
                    "Customer Question",
                    value="지성 피부인데 트러블에도 괜찮아?",
                    height=80
                )

        st.write("")
        run_automation = st.button("⚡ Run", type="primary", use_container_width=True)

# ==============================================================================
# RIGHT: OUTPUTS
# ==============================================================================
with right_column:
    if run_automation:
        st.subheader("📱 Live Result")

        if not api_key_input:
            st.error("🔒 Please activate Phase 1 with your API Key.")
        else:
            try:
                with st.spinner("✨ AI is working..."):

                    # -----------------------------
                    # MODE 1: Review Summary
                    # -----------------------------
                    if service_mode == "Review Summary":
                        class ReviewSummary(BaseModel):
                            overall_sentiment: Literal["positive", "mixed", "negative"] = Field(
                                description="Overall sentiment"
                            )
                            pros: List[str] = Field(description="Top 3 pros")
                            cons: List[str] = Field(description="Top 3 cons")
                            cautions: List[str] = Field(description="Potential cautions (max 3)")
                            one_line_summary: str = Field(description="One sentence summary")

                        async def gen_review_summary():
                            persona = system_prompt
                            agent = Agent(
                                "openai:gpt-4o-mini",
                                output_type=ReviewSummary,
                                system_prompt=persona,
                            )
                            prompt = f"""
TASK: Summarize reviews for an Olive Young product.

Product: {product_name}
Output language: {summary_lang}

Reviews:
{reviews_text}

Rules:
- pros/cons/cautions: max 3 each
- neutral, practical tone
- no marketing hype
"""
                            r = await agent.run(prompt)
                            return r.output

                        data = run_async(gen_review_summary())

                        body = f"""
                        <div style="font-size: 13px; color:#666; margin-bottom:10px;">
                            Product: <b>{safe(product_name)}</b>
                        </div>
                        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:12px;">
                            <div style="padding:6px 10px; border-radius:999px; background:#eee; font-size:12px;">
                                Sentiment: <b>{safe(data.overall_sentiment)}</b>
                            </div>
                        </div>
                        <div style="margin-top:10px;">
                            <div style="font-weight:800; margin-bottom:6px;">One-line Summary</div>
                            <div style="padding:12px; border:1px solid #eee; border-radius:12px; background:#fafafa;">
                                {safe(data.one_line_summary)}
                            </div>
                        </div>
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:14px;">
                            <div style="border:1px solid #eee; border-radius:12px; padding:12px;">
                                <div style="font-weight:800; margin-bottom:6px;">Pros</div>
                                <ul style="margin:0; padding-left:18px;">
                                    {''.join(f"<li>{safe(x)}</li>" for x in data.pros)}
                                </ul>
                            </div>
                            <div style="border:1px solid #eee; border-radius:12px; padding:12px;">
                                <div style="font-weight:800; margin-bottom:6px;">Cons</div>
                                <ul style="margin:0; padding-left:18px;">
                                    {''.join(f"<li>{safe(x)}</li>" for x in data.cons)}
                                </ul>
                            </div>
                        </div>
                        <div style="margin-top:12px; border:1px solid #eee; border-radius:12px; padding:12px;">
                            <div style="font-weight:800; margin-bottom:6px;">Cautions</div>
                            <ul style="margin:0; padding-left:18px;">
                                {''.join(f"<li>{safe(x)}</li>" for x in data.cautions)}
                            </ul>
                        </div>
                        """

                        st.markdown(render_card("Review Summary", "In-Store AI", body), unsafe_allow_html=True)
                        with st.expander("🔍 Raw JSON"):
                            st.json(data.model_dump())

                    # -----------------------------
                    # MODE 2: Translation
                    # -----------------------------
                    elif service_mode == "Translation":
                        class TranslationResult(BaseModel):
                            translated_text: str = Field(description="Translated text")
                            brief_notes: Optional[str] = Field(
                                default=None,
                                description="Optional note (1 sentence) about tone/choices"
                            )

                        async def gen_translation():
                            agent = Agent(
                                "openai:gpt-4o-mini",
                                output_type=TranslationResult,
                                system_prompt=system_prompt,
                            )
                            prompt = f"""
TASK: Translate the text.

Target language: {target_lang}
Tone: {tone}

Text:
{source_text}

Rules:
- Keep meaning faithful
- Keep it natural
"""
                            r = await agent.run(prompt)
                            return r.output

                        data = run_async(gen_translation())

                        body = f"""
                        <div style="font-size: 13px; color:#666; margin-bottom:10px;">
                            Target: <b>{safe(target_lang)}</b> · Tone: <b>{safe(tone)}</b>
                        </div>
                        <div style="margin-top:8px;">
                            <div style="font-weight:800; margin-bottom:6px;">Translated Text</div>
                            <div style="white-space:pre-wrap; padding:12px; border:1px solid #eee; border-radius:12px; background:#fafafa;">
                                {safe(data.translated_text)}
                            </div>
                        </div>
                        """
                        if data.brief_notes:
                            body += f"""
                            <div style="margin-top:10px; font-size: 12px; color:#666;">
                                Note: {safe(data.brief_notes)}
                            </div>
                            """

                        st.markdown(render_card("Translation", "In-Store AI", body), unsafe_allow_html=True)
                        with st.expander("🔍 Raw JSON"):
                            st.json(data.model_dump())

                    # -----------------------------
                    # MODE 3: AI Chatbot
                    # -----------------------------
                    else:
                        class ChatbotAnswer(BaseModel):
                            answer: str = Field(description="2–4 sentences answer")
                            follow_up_question: str = Field(description="One short follow-up question if needed")
                            safety_note: str = Field(description="One short safety note (e.g., patch test)")

                        async def gen_chatbot():
                            agent = Agent(
                                "openai:gpt-4o-mini",
                                output_type=ChatbotAnswer,
                                system_prompt=system_prompt,
                            )
                            prompt = f"""
TASK: Answer the customer's question as an Olive Young in-store assistant.
Use ONLY the provided product context and review hint.

Product context:
{product_context}

Review hint:
{reviews_hint}

Customer question:
{user_question}

Rules:
- answer: 2–4 sentences, Korean if question is Korean
- If info is missing, say what's missing briefly + ask follow_up_question
- Always include a short safety_note (patch test / irritation caution when relevant)
"""
                            r = await agent.run(prompt)
                            return r.output

                        data = run_async(gen_chatbot())

                        body = f"""
                        <div style="display:grid; grid-template-columns:1fr; gap:12px;">
                            <div style="border:1px solid #eee; border-radius:12px; padding:12px;">
                                <div style="font-size:12px; color:#666; margin-bottom:6px;">Customer Question</div>
                                <div style="font-weight:800;">{safe(user_question)}</div>
                            </div>
                            <div style="border:1px solid #eee; border-radius:12px; padding:12px; background:#fafafa;">
                                <div style="font-size:12px; color:#666; margin-bottom:6px;">AI Answer</div>
                                <div style="white-space:pre-wrap; line-height:1.5;">{safe(data.answer)}</div>
                            </div>
                            <div style="border:1px solid #eee; border-radius:12px; padding:12px;">
                                <div style="font-size:12px; color:#666; margin-bottom:6px;">Follow-up</div>
                                <div>{safe(data.follow_up_question)}</div>
                            </div>
                            <div style="border:1px solid #eee; border-radius:12px; padding:12px;">
                                <div style="font-size:12px; color:#666; margin-bottom:6px;">Safety Note</div>
                                <div>{safe(data.safety_note)}</div>
                            </div>
                        </div>
                        """

                        st.markdown(render_card("AI Chatbot", "In-Store AI", body), unsafe_allow_html=True)
                        with st.expander("🔍 Raw JSON"):
                            st.json(data.model_dump())

                st.success("✅ Complete")

            except Exception as e:
                st.error(f"Error: {e}")

    else:
        st.subheader("📱 Template Preview")
        st.caption("Select a feature and click Run to generate results.")

        preview_body = """
        <div style="color:#444; line-height:1.6;">
            <b>Included features</b>
            <ul>
                <li>Review Summary (structured insights)</li>
                <li>Translation (target language output)</li>
                <li>AI Chatbot (in-store Q&A)</li>
            </ul>
            <div style="margin-top:10px; padding:12px; border:1px solid #eee; border-radius:12px; background:#fafafa;">
                This is a preview state. Click <b>Run</b> to see live AI outputs.
            </div>
        </div>
        """
        st.markdown(render_card("Olive Young In-Store AI", "Template Preview", preview_body), unsafe_allow_html=True)
