import streamlit as st
import os
import asyncio
from pydantic_ai import Agent
from pydantic import BaseModel, Field

# Set page title and layout
st.set_page_config(page_title="U-Shop AI Pipeline", layout="wide")

# --- CUSTOM CSS FOR STYLING ---
st.markdown("""
<style>
    /* Global Font adjustments */
    .stTextArea textarea {
        font-family: monospace;
    }
    /* Highlight the Right Column (Output area) */
    div[data-testid="column"]:nth-of-type(2) {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        border: 1px dashed #ccc;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Phase-Based LLM Automation Dashboard")
st.write("This dashboard demonstrates a 3-phase automated system for generating U-Shop product listings.")

# --- HELPER FUNCTION: RENDER CARD ---
def render_product_card(product_name, price, marketing_copy, is_preview=False):
    """
    Generates the HTML for the U-Shop Product Card.
    """
    
    # Conditional styling for "Preview" mode
    status_badge = "Official U-Shop Merch"
    badge_color = "#CC0000"
    
    if is_preview:
        status_badge = "TEMPLATE PREVIEW"
        badge_color = "#999"

    html_code = f"""
    <div style="
        background-color: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        font-family: 'Helvetica Neue', sans-serif;
        max-width: 400px;
        margin: auto;
    ">
        <div style="
            background-color: {badge_color}; 
            color: white; 
            text-transform: uppercase; 
            font-weight: bold; 
            font-size: 10px; 
            padding: 5px 12px; 
            border-radius: 15px; 
            display: inline-block; 
            margin-bottom: 15px;
            letter-spacing: 1px;
        ">
            {status_badge}
        </div>
        
        <!-- Placeholder Image Circle -->
        <div style="
            width: 60px; height: 60px; 
            background-color: #f0f0f0; 
            border-radius: 50%; 
            margin-bottom: 15px;
            display: flex; align-items: center; justify-content: center;
            font-size: 24px;
        ">👕</div>
        
        <h2 style="
            margin: 0; 
            color: #1a1a1a; 
            font-size: 26px; 
            line-height: 1.2;
        ">{product_name}</h2>
        
        <div style="
            margin-top: 15px; 
            font-size: 32px; 
            color: #CC0000; 
            font-weight: 800;
        ">${price}</div>
        
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        
        <p style="
            color: #555; 
            font-size: 16px; 
            line-height: 1.6; 
            font-style: italic;
        ">
            "{marketing_copy}"
        </p>
        
        <button style="
            background-color: #1a1a1a; 
            color: white; 
            border: none; 
            width: 100%; 
            padding: 15px; 
            border-radius: 10px; 
            font-weight: bold; 
            font-size: 16px; 
            cursor: pointer; 
            margin-top: 10px;
            transition: background-color 0.3s;
        ">
            Add to Cart &nbsp; 🛒
        </button>
    </div>
    """
    return html_code


# Create main layout columns
left_column, right_column = st.columns([1, 1])

# ==============================================================================
# LEFT COLUMN: INPUTS
# ==============================================================================
with left_column:
    st.subheader("🛠️ Control Center")
    
    # PHASE 1: ACTIVATION
    with st.container(border=True):
        st.markdown("#### 1️⃣ API Activation")
        api_key_input = st.text_input("OpenAI API Key:", type="password", help="Your key is not stored permanently.")
        
        if api_key_input:
            masked = f"{api_key_input[:3]}...{api_key_input[-4:]}"
            st.caption(f"✅ Active: `{masked}`")
            os.environ["OPENAI_API_KEY"] = api_key_input
        else:
            st.caption("🔴 Locked")

    # PHASE 2: INSERTION
    with st.container(border=True):
        st.markdown("#### 2️⃣ Prompt Engineering")
        
        tab1, tab2 = st.tabs(["System Persona", "User Request"])
        
        with tab1:
            system_prompt = st.text_area(
                "System Role", 
                value="You are a professional U-Shop marketing expert for the University of Utah.",
                height=120
            )
        
        with tab2:
            user_prompt = st.text_area(
                "Product Description", 
                value="A crimson red hoodie with a white interlocking U logo.",
                height=120
            )

        st.write("") 
        run_automation = st.button("⚡ Run Generation Pipeline", type="primary", use_container_width=True)

# ==============================================================================
# RIGHT COLUMN: OUTPUTS (Live Preview)
# ==============================================================================
with right_column:
    
    # --- PHASE 3: EXECUTION ---
    if run_automation:
        st.subheader("📱 Live Result")
        
        if not api_key_input:
            st.error("🔒 Please activate Phase 1 with your API Key.")
        else:
            async def generate_product():
                class UShopProduct(BaseModel):
                    product_name: str = Field(description="Professional product name")
                    marketing_copy: str = Field(description="2 sentences, spirited tone, ends with #GoUtes")
                    price: float = Field(ge=5.0, description="Price in USD, must be at least $5")
                    
                agent = Agent("openai:gpt-4o-mini", output_type=UShopProduct, system_prompt=system_prompt)
                result = await agent.run(user_prompt)
                return result.output

            try:
                with st.spinner("✨ AI is crafting the product..."):
                    data = asyncio.run(generate_product())
                
                # RENDER LIVE ECOMMERCE PREVIEW (HTML)
                real_card_html = render_product_card(
                    data.product_name,
                    f"{data.price:.2f}",
                    data.marketing_copy,
                    is_preview=False
                )
                real_card_html = "\n".join(line.lstrip() for line in real_card_html.splitlines())
                ecommerce_preview_html = "\n".join([
                    '<div style="background: linear-gradient(135deg, #f6f6f6, #ffffff); padding: 28px; border-radius: 18px; border: 1px solid #e6e6e6;">',
                    '<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px;">',
                    '<div style="font-size: 20px; font-weight: 800; letter-spacing: 0.5px;">U‑Shop Official Store</div>',
                    '<div style="font-size: 12px; background: #111; color: #fff; padding: 6px 10px; border-radius: 999px; text-transform: uppercase; letter-spacing: 1px;">Featured Drop</div>',
                    '</div>',
                    '<div style="display: grid; grid-template-columns: 1fr; gap: 18px;">',
                    '<div style="background: #fff; border-radius: 14px; padding: 16px 18px; border: 1px solid #eee; box-shadow: 0 6px 16px rgba(0,0,0,0.06);">',
                    '<div style="font-size: 14px; color: #555; margin-bottom: 8px;">Campaign Copy</div>',
                    f'<div style="font-size: 18px; line-height: 1.5; color: #222;">{data.marketing_copy}</div>',
                    '</div>',
                    real_card_html,
                    '</div>',
                    '<div style="margin-top: 18px; font-size: 12px; color: #777;">Preview only · Pricing and availability may change</div>',
                    '</div>',
                ])
                st.markdown(ecommerce_preview_html, unsafe_allow_html=True)
                
                st.write("")
                with st.expander("🔍 View Raw JSON Schema"):
                    st.json(data.model_dump())
                    
                st.success("✅ Generation Complete")

            except Exception as e:
                st.error(f"Error: {e}")
    
    # --- TEMPLATE STATE (When Idle) ---
    else:
        st.subheader("📱 Template Preview")
        st.caption("This is how your product will look after generation.")
        
        # RENDER PREVIEW CARD
        preview_html = render_product_card(
            "Sample Product Name", 
            "0.00", 
            "Your AI-generated marketing copy will appear right here. It will be persuasive, on-brand, and follow your system instructions.",
            is_preview=True
        )
        st.markdown(preview_html, unsafe_allow_html=True)
