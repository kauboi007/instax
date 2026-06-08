import streamlit as st
import requests

API = "https://instax-l8iy.onrender.com"

st.title("Instax")

if "token" not in st.session_state:
    st.session_state.token = None

def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# Auth section
if not st.session_state.token:
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            res = requests.post(f"{API}/auth/jwt/login", data={"username": email, "password": password})
            if res.status_code == 200:
                st.session_state.token = res.json()["access_token"]
                st.rerun()
            else:
                st.error("Login failed")

    with tab2:
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            res = requests.post(f"{API}/auth/register", json={"email": email, "password": password})
            if res.status_code == 201:
                st.success("Registered! Now login.")
            else:
                st.error(res.json().get("detail", "Registration failed"))

else:
    # Create post
    st.subheader("Create Post")
    title = st.text_input("Title")
    content = st.text_area("Content")
    if st.button("Post"):
        res = requests.post(f"{API}/posts", json={"title": title, "content": content}, headers=auth_headers())
        if res.status_code == 200:
            st.success("Posted!")
            st.rerun()
        else:
            st.error("Failed to post")

    st.divider()

    # Feed
    st.subheader("Feed")
    res = requests.get(f"{API}/feed", headers=auth_headers())
    if res.status_code == 200:
        posts = res.json()["posts"]
        for post in posts:
            with st.container(border=True):
                st.markdown(f"**{post['title']}**")
                st.write(post["content"])
                st.caption(f"by {post['email']} • {post['created_on'][:19]}")
                if post["is_owner"]:
                    if st.button("Delete", key=post["id"]):
                        requests.delete(f"{API}/posts/{post['id']}", headers=auth_headers())
                        st.rerun()

    if st.button("Logout"):
        st.session_state.token = None
        st.rerun()
