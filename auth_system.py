# auth_system.py

import streamlit as st
import hashlib
import os
import json
import datetime

auth_file = "users.json"

def default_users():
    return {
        "admin": {
            "password": hashlib.sha256("admin123".encode()).hexdigest(),
            "created": str(datetime.datetime.now()),
            "role": "admin"
        }
    }

def load_users():
    if os.path.exists(auth_file):
        with open(auth_file, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        users = default_users()
        with open(auth_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
        return users

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login():
    st.subheader("🔐 Giriş Yap")
    username = st.text_input("Kullanıcı Adı", key="login_username")
    password = st.text_input("Şifre", type="password", key="login_password")
    login_button = st.button("Giriş")

    users = load_users()
    if login_button:
        if username in users and users[username]["password"] == hash_password(password):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["role"] = users[username].get("role", "user")
            st.success("Giriş başarılı!")
            st.rerun()
        else:
            st.error("Kullanıcı adı veya şifre yanlış.")
    return False

def auth_gate():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        login_success = login()
        if not login_success:
            st.warning("Sisteme giriş izniniz yok. Lütfen yöneticinize başvurun.")
            return False
    return True

def admin_gate():
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.error("Bu sayfa yalnızca yöneticiler içindir.")
        return False
    if st.session_state.get("role") != "admin":
        st.error("Yalnızca yönetici yetkisine sahip kullanıcılar erişebilir.")
        return False
    return True

def add_user():
    users = load_users()
    new_username = st.text_input("Yeni Kullanıcı Adı", key="admin_new_username")
    new_password = st.text_input("Şifre", type="password", key="admin_new_password")
    role = st.selectbox("Rol", ["user", "admin"], key="admin_user_role")
    add_button = st.button("Kullanıcıyı Ekle")

    if add_button:
        if not new_username or not new_password:
            st.warning("Lütfen tüm alanları doldurun.")
        elif new_username in users:
            st.warning("Bu kullanıcı adı zaten mevcut.")
        else:
            users[new_username] = {
                "password": hash_password(new_password),
                "created": str(datetime.datetime.now()),
                "role": role
            }
            with open(auth_file, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=4)
            st.success("Yeni kullanıcı başarıyla eklendi.")

def get_all_users():
    return load_users()

def delete_user(username):
    users = load_users()
    if username in users:
        del users[username]
        with open(auth_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)