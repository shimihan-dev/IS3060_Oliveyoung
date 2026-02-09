import streamlit as st

st.write("Hello, KIA Tigers will win the championship this season.")
input_text=st.text_input("Text:", type="password")
st.caption(f"{input_text}")

###########################################
# Section2. Prompt
###########################################

sys={"sys_prompt":"",
     "user_prompt":""}
## System Prompt

system_prompt = st.text_input("Insert system prompt here:")#user input
st.caption(f"{system_prompt}")#Test and preview
sys["sys_prompt"]=system_prompt#Store text into DB

## User Prompt
user_prompt = st.text_input("Insert user prompt here:")
st.caption(f"{user_prompt}")
sys["user_prompt"]=user_prompt

# Look into Sys object
st.write(sys)