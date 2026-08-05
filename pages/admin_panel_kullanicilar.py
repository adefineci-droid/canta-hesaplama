import streamlit as st
from auth_system import admin_gate, add_user, get_all_users, delete_user

st.set_page_config(page_title="Kullanıcı Yönetimi", layout="centered")
st.title("👮 Kullanıcı Yönetim Paneli")

if not admin_gate():
    st.stop()

st.subheader("➕ Yeni Kullanıcı Ekle")
add_user()

st.subheader("👥 Mevcut Kullanıcılar")

users = get_all_users()

if users:
    for username, info in users.items():
        col1, col2 = st.columns([6, 2])
        with col1:
            st.markdown(f"**{username}** (Rol: `{info.get('role', 'user')}`)")
        with col2:
            if st.button("🗑 Sil", key=f"del_{username}"):
                delete_user(username)
                st.success(f"'{username}' adlı kullanıcı silindi.")
                st.rerun()
else:
    st.warning("Henüz kullanıcı eklenmemiş.")

st.info("Bu sayfa sadece yöneticilere özeldir.")