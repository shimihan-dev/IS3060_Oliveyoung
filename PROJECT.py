import os
import asyncio
import streamlit as st
import streamlit.components.v1 as components

# ✅ NEW: pydantic_ai가 없을 때 Streamlit Cloud에서 안내 메시지
try:
    from pydantic_ai import Agent
except ModuleNotFoundError:
    st.error(
        "Missing dependency: pydantic_ai\n\n"
        "Streamlit Cloud에서는 requirements.txt에 `pydantic-ai`를 추가해야 합니다."
    )
    st.stop()

from pydantic import BaseModel, Field
from typing import List, Literal, Optional


# ==============================================================================
# PAGE CONFIG
# ==============================================================================
st.set_page_config(page_title="Olive Young QR Demo", layout="wide")

st.markdown("""
<style>
  div[data-testid="column"]:nth-of-type(2) {
      background-color: #f8f9fa;
      border-radius: 15px;
      padding: 18px;
      border: 1px dashed #ccc;
  }
</style>
""", unsafe_allow_html=True)

st.title("🧴 Olive Young QR Demo (n8n Logic → Streamlit)")

# ==============================================================================
# HELPERS
# ==============================================================================
def run_async(coro):
    """Run a coroutine safely in Streamlit."""
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        finally:
            loop.close()

def render_card(title: str, badge: str, body_html: str):
    return f"""
    <div style="background:#fff;border-radius:18px;padding:20px;border:1px solid #eaeaea;
                box-shadow:0 10px 25px rgba(0,0,0,0.08);max-width:760px;margin:0 auto;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
        <div style="font-size:18px;font-weight:900;">{title}</div>
        <div style="font-size:11px;background:#111;color:#fff;padding:6px 10px;border-radius:999px;
                    text-transform:uppercase;letter-spacing:1px;font-weight:800;">{badge}</div>
      </div>
      {body_html}
    </div>
    """

# ==============================================================================
# n8n-like product_id → productData, reviews
# ==============================================================================
def get_product_payload(product_id: str):
    productData = {}
    reviews = []

    if product_id == "1":
        productData = {
            "name": "Round Lab 1025 Dokdo Toner 500 ml Special Set",
            "image_url": "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0013/A00000013718040ko.jpg?l=ko&QT=85&SF=webp&sharpen=1x0.5",
            "description": "A gentle hydrating toner for dry and sensitive skin.",
            "price": 27000
        }
        reviews = [
            "I use it after washing my face in the morning and evening. It absorbs well without itching or stickiness.",
            "I'm using it all the time. It's dry, but I'm using it all four seasons.",
            "This toner contains a perfect balance of high-molecular-weight and low-molecular-weight hyaluronic acid, fundamentally restoring the skin barrier. In particular, it helps maintain the skin’s pH balance perfectly, drastically reducing the likelihood of breakouts. It’s rare to find this kind of ingredient composition at this price point."
        ]
    elif product_id == "2":
        productData = {
            "name": "Torriden Dive Hyaluronic Acid Soothing Cream",
            "image_url": "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0016/A00000016559833ko.jpg?l=ko&QT=85&SF=webp&sharpen=1x0.5",
            "description": "Soothing cream that can help soothe moisture and heat even after a while.",
            "price": 15500
        }
        reviews = [
            "I have sensitive skin, so if it doesn't fit, my skin will turn upside down. This is good because it's gentle. It moisturizes well, so I've been buying and using it well.",
            "It's a cream that soothes irritated skin well. I use it after using a peeling product, and it helps a lot with soothing.",
            "The cream has a light texture that absorbs quickly into the skin without leaving a greasy residue. It provides long-lasting hydration, making my skin feel soft and supple throughout the day.",
            "It's light on application and has almost no white cast, so it's good for daily use. It absorbs quickly without stickiness, so there's no pushiness even if you apply it before makeup, and it's comfortable even after outdoor activities. It has enough UV protection, so I'm using it with confidence even in the summer. It's sensitive skin, and it fits well without any trouble."
        ]
    elif product_id == "3":
        productData = {
            "name": "[Manggom Collaboration] Aviv Eoseongcho Teka Capsule Serum Calming Drop 50 ml Double Plan (+Luggage Tag)",
            "image_url": "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0024/A00000024567211ko.jpg?l=ko&QT=85&SF=webp&sharpen=1x0.5",
            "description": "Trouble soothing capsules that help with excessive oil and sebum care help to effectively soothe the skin without irritation.",
            "price": 29800
        }
        reviews = [
            "It's a serum I've been using very well, but I heard that there was a collaboration between Manggom and I already had it, so I bought it additionally! This is a really good serum for acne control, but it's very moist, so I've been using this one most of the time these days!",
            "The texture is light and fresh, so it absorbs quickly into the skin.",
            "The more you use it, the more comfortable your skin is, and it fits well for soothing before getting any trouble. It's not sticky, so it's good for layering with other base products.",
            "It's light on application and has almost no white cast, so it's good for daily use. It absorbs quickly without stickiness, so there's no pushiness even if you apply it before makeup, and it's comfortable even after outdoor activities. It has enough UV protection, so I'm using it with confidence even in the summer. It's sensitive skin, and it fits well without any trouble."
        ]
    else:
        productData = {
            "name": "Vanilla Co Clean It Zero Pore Clarifying Cleansing Balm 100 ml",
            "image_url": "https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0020/A00000020267821ko.jpg?l=ko&QT=85&SF=webp&sharpen=1x0.5",
            "description": "Smoother oil balm formula melts from blackheads embedded to rough dead skin cells to smooth skin texture!",
            "price": 14800
        }
        reviews = [
            "It's a cleansing balm that's good for daily use. It's gentle and moist.",
            "I'm always using this product, but I can't stand Manggom! Why is Costa so cute and the composition of the 3 travel items is also very good! I wanted to buy pink, but I'm still using pink because it's for winter and I bought green for the spring and summer when it's going to be warm.",
            "Manggom's collaboration product. Manggom did everything cute. I bought it.",
            "It's easy to remove dead skin cells and it cleanses well. I don't know how many times I bought it."
        ]

    return productData, reviews


# ==============================================================================
# Read query param (Streamlit new API)
# ==============================================================================
# URL example: http://localhost:8501/?product_id=1
product_id = st.query_params.get("product_id", "1")  # default "1"
productData, reviews = get_product_payload(str(product_id))

# ==============================================================================
# Session state for outputs (one-screen UX)
# ==============================================================================
st.session_state.setdefault("review_summary", None)
st.session_state.setdefault("translation", None)
st.session_state.setdefault("chat_answer", None)

# ==============================================================================
# LAYOUT
# ==============================================================================
left, right = st.columns([1, 1])

# ==============================================================================
# LEFT: Controls (API key + inputs)
# ==============================================================================
with left:
    st.subheader("🛠 Control Center")

        # --- DEMO: product_id selector (QR simulation) ---
    query_pid = st.query_params.get("product_id", "1")

    with st.container(border=True):
        st.markdown("#### 🏷️ Product Selector (Demo)")
        pid = st.selectbox(
            "product_id",
            options=["1", "2", "3", "4"],
            index=(["1", "2", "3", "4"].index(query_pid) if query_pid in ["1","2","3","4"] else 0),
        )

        if pid != query_pid:
            st.query_params["product_id"] = pid
            st.rerun()


    # API Key
    with st.container(border=True):
        st.markdown("#### 1️⃣ API Activation")
        api_key = st.text_input("OpenAI API Key", type="password")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.caption("✅ Active")
        else:
            st.caption("🔴 Locked")

    # Inputs
    with st.container(border=True):
        st.markdown("#### 2️⃣ Inputs")

        system_prompt = st.text_area(
            "System Persona",
            value=(
                "You are an Olive Young in-store assistant. "
                "Be concise, neutral, and practical. Avoid exaggerated marketing."
            ),
            height=100,
        )

        st.markdown("**Translate Input**")
        text_to_translate = st.text_area(
            "Text",
            value="",
            height=80
        )
        target_lang = st.selectbox("Target Language", ["English", "Korean", "Japanese", "Chinese (Simplified)"], index=0)

        st.markdown("**Chatbot Input**")
        user_question = st.text_area(
            "Customer Question",
            value="Is this product okay for sensitive skin?",
            height=80
        )

# ==============================================================================
# RIGHT: One-screen dashboard (product + buttons + results)
# ==============================================================================
with right:
    st.subheader("📱 Product Page (QR landing)")

    # Product Card
    img = productData.get("image_url", "")
    img_html = ""
    if img:
        img_html = f"""
          <img src="{img}" style="width:100%;max-width:380px;max-height:380px;object-fit:cover;
                                  border-radius:16px;border:1px solid #eee;display:block;margin-bottom:10px;">
        """

    reviews_html = "No reviews for this product_id."
    if reviews:
        reviews_html = "".join(
        f"""
            <div style="border:1px solid #eee;border-radius:12px;padding:12px;background:#fff;margin-bottom:10px;">
          <div style="font-size:12px;color:#777;margin-bottom:6px;"><b>Review {i+1}</b></div>
          <div style="font-size:13px;line-height:1.6;color:#333;white-space:pre-wrap;">{rv}</div>
        </div>
        """
        for i, rv in enumerate(reviews[:5])
    )


    product_body = f"""
      <div style="display:flex;gap:16px;flex-wrap:wrap;">
        <div style="flex:1;min-width:260px;">{img_html}</div>
        <div style="flex:1;min-width:260px;">
          <div style="font-size:12px;color:#777;">Product</div>
          <div style="font-size:22px;font-weight:900;margin:6px 0 10px 0;">{productData.get("name","")}</div>
          <div style="font-size:12px;color:#777;">Description</div>
          <div style="font-size:14px;line-height:1.5;margin-top:6px;">{productData.get("description","")}</div>
          <div style="margin-top:12px;font-size:12px;color:#777;">Price</div>
          <div style="font-size:28px;font-weight:900;">₩ {productData.get("price",0):,}</div>
        </div>
      </div>
      <hr style="border:none;border-top:1px solid #eee;margin:14px 0;">
      <div style="font-size:12px;color:#777;margin-bottom:8px;">Reviews loaded: <b>{len(reviews)}</b></div>
      <div>
  {reviews_html}
</div>

    """
    components.html(render_card("Product Card", f"product_id={product_id}", product_body), height=680, scrolling=True)

    # Action buttons (one screen)
    c1, c2, c3 = st.columns(3)
    do_summary = c1.button("🧾 Review Summary", use_container_width=True)
    do_translate = c2.button("🌐 Translate", use_container_width=True)
    do_chat = c3.button("💬 AI Chatbot", use_container_width=True)

    # Guard
    if (do_summary or do_translate or do_chat) and not api_key:
        st.error("🔒 Please activate Phase 1 with your API Key.")
        st.stop()

    # --- 1) Review Summary ---
    if do_summary:
        class ReviewSummary(BaseModel):
            overall_sentiment: Literal["positive", "mixed", "negative"] = Field(description="Overall sentiment")
            one_line_summary: str = Field(description="One sentence summary")
            pros: List[str] = Field(description="Top 3 pros")
            cons: List[str] = Field(description="Top 3 cons")

        async def gen_review_summary():
            agent = Agent("openai:gpt-4o-mini", output_type=ReviewSummary, system_prompt=system_prompt)
            prompt = f"""
Summarize customer reviews for this product.

Product: {productData.get("name")}
Reviews:
{chr(10).join(reviews)}

Rules:
- pros/cons max 3 each
- neutral, practical tone
"""
            r = await agent.run(prompt)
            return r.output

        with st.spinner("✨ Summarizing reviews..."):
            st.session_state.review_summary = run_async(gen_review_summary())

    # --- 2) Translation ---
    if do_translate:
        class Translation(BaseModel):
            translated_text: str = Field(description="Translated text")

        async def gen_translation():
            agent = Agent("openai:gpt-4o-mini", output_type=Translation, system_prompt=system_prompt)
            prompt = f"""
Translate the following text to {target_lang}.

Text:
{text_to_translate}
"""
            r = await agent.run(prompt)
            return r.output

        with st.spinner("✨ Translating..."):
            st.session_state.translation = run_async(gen_translation())

    # --- 3) Chatbot ---
    if do_chat:
        class ChatAnswer(BaseModel):
            answer: str = Field(description="Answer in 3-5 sentences")
            safety_note: str = Field(description="One short safety note")

        async def gen_chat():
            agent = Agent("openai:gpt-4o-mini", output_type=ChatAnswer, system_prompt=system_prompt)
            prompt = f"""
You are an in-store assistant. Answer the customer's question using only the product info and reviews below.

Product info:
{productData}

Reviews:
{reviews}

Customer question:
{user_question}

Rules:
- If uncertain, say what's missing briefly
- Include a short safety_note (patch test/irritation caution when relevant)
"""
            r = await agent.run(prompt)
            return r.output

        with st.spinner("✨ Generating answer..."):
            st.session_state.chat_answer = run_async(gen_chat())

    # Render results (persist on same screen)
    if st.session_state.review_summary:
        d = st.session_state.review_summary
        body = f"""
          <div style="font-size:12px;color:#777;margin-bottom:8px;">Sentiment: <b>{d.overall_sentiment}</b></div>
          <div style="padding:12px;border:1px solid #eee;border-radius:12px;background:#fafafa;margin-bottom:10px;">
            <b>One-line</b><br>{d.one_line_summary}
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div style="border:1px solid #eee;border-radius:12px;padding:12px;">
              <b>Pros</b><ul>{''.join(f'<li>{p}</li>' for p in d.pros)}</ul>
            </div>
            <div style="border:1px solid #eee;border-radius:12px;padding:12px;">
              <b>Cons</b><ul>{''.join(f'<li>{c}</li>' for c in d.cons)}</ul>
            </div>
          </div>
        """
        components.html(render_card("Review Summary", "AI", body), height=420, scrolling=True)

    if st.session_state.translation:
        d = st.session_state.translation
        body = f"""
          <div style="font-size:12px;color:#777;margin-bottom:8px;">Target: <b>{target_lang}</b></div>
          <div style="white-space:pre-wrap;padding:12px;border:1px solid #eee;border-radius:12px;background:#fafafa;">
            {d.translated_text}
          </div>
        """
        components.html(render_card("Translation", "AI", body), height=260, scrolling=True)

    if st.session_state.chat_answer:
        d = st.session_state.chat_answer
        body = f"""
          <div style="border:1px solid #eee;border-radius:12px;padding:12px;background:#fafafa;white-space:pre-wrap;">
            <b>Answer</b><br>{d.answer}
          </div>
          <div style="margin-top:10px;font-size:12px;color:#666;">
            <b>Safety</b>: {d.safety_note}
          </div>
        """
        components.html(render_card("AI Chatbot", "AI", body), height=320, scrolling=True)
