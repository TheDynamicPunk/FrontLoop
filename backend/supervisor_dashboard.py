import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.title("🧑‍💼 FrontLoop Supervisor Dashboard")

# Fetch pending requests
resp = requests.get(f"{API_BASE}/requests?status=pending")
requests_data = resp.json()

if st.button("🔁 Refresh Requests"):
    # st.experimental_rerun()
    resp = requests.get(f"{API_BASE}/requests?status=pending")
    requests_data = resp.json()

if not requests_data:
    st.info("No pending help requests 🎉")

else:
    for req in requests_data:
        with st.expander(f"Request from {req['customer_name']}"):
            st.write(f"**Question:** {req['question']}")
            answer = st.text_area("Your answer")
            if st.button(f"Submit Answer for {req['id']}"):
                payload = {"request_id": req["id"], "answer": answer}
                res = requests.post(f"{API_BASE}/respond", json=payload)
                if res.status_code == 200:
                    st.success("✅ Answer submitted and AI notified!")
                else:
                    st.error("⚠️ Failed to submit answer")

st.header("📘 Learned Answers")

kb_resp = requests.get(f"{API_BASE}/knowledge-base")
kb_data = kb_resp.json()

if kb_data:
    for item in kb_data:
        st.markdown(f"**Q:** {item['question']}")
        st.markdown(f"**A:** {item['answer']}")
        st.markdown("---")
else:
    st.info("No learned answers yet.")

