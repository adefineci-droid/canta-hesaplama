# back_office_admin_panel.py

import streamlit as st
import json
import os
from auth_system import auth_gate

st.set_page_config(page_title="🔧 Yönetim Paneli", layout="centered")

if not auth_gate():
    st.stop()

st.title("🔧 Arka Plan Değişkenleri Yönetimi")

config_file = "ayarlar.json"

def default_config():
    return {
        "fabric_usd_kg": 1.85,
        "bopp_usd_kg_12": 3.1,
        "bopp_usd_kg_20": 2.4,
        "metal_bopp_usd_kg": 2.7,
        "sap_usd_kg": 2.4,
        "labor_usd_piece": 0.056,
        "box_usd_piece": 0.006,
        "lam_outer_usd_m2": 0.08,
        "lam_inner_usd_m2": 0.06,
        "flexo_setup_usd": 170.0,
        "flexo_usd_kg": 2.0,
        "rotogravure_setup_usd": 420.0,
        "rotogravure_usd_kg": 2.8,
        "plate_cost_eur_cm2": 0.015,
        "usd_to_try": 39.1,
        "eur_to_try": 42.3,
        "tier1_max_qty": 40000,
        "tier1_margin_pct": 40.0,
        "tier2_max_qty": 90000,
        "tier2_margin_pct": 35.0,
        "tier3_margin_pct": 30.0
    }

if os.path.exists(config_file):
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
        for k, v in default_config().items():
            if k not in config:
                config[k] = v
else:
    config = default_config()

st.markdown("Aşağıdaki değerleri güncelleyerek hesaplama motoruna etki edebilirsiniz.")

with st.form("config_form"):
    updated_config = {}
    
    st.subheader("💵 Hammadde ve Operasyon Maliyetleri")
    for key, val in config.items():
        if "tier" not in key:
            if isinstance(val, (float, int)):
                updated_config[key] = st.number_input(f"{key.replace('_', ' ').title()}", value=float(val), format="%.4f")
            else:
                updated_config[key] = val

    st.subheader("📈 Kâr Marjı ve Adet Kademeleri")
    col1, col2 = st.columns(2)
    with col1:
        updated_config["tier1_max_qty"] = st.number_input("1. Kademe Maksimum Adet", value=int(config.get("tier1_max_qty", 40000)), step=5000)
        updated_config["tier2_max_qty"] = st.number_input("2. Kademe Maksimum Adet", value=int(config.get("tier2_max_qty", 90000)), step=5000)
    with col2:
        updated_config["tier1_margin_pct"] = st.number_input("1. Kademe Kâr Oranı (%)", value=float(config.get("tier1_margin_pct", 40.0)), step=1.0)
        updated_config["tier2_margin_pct"] = st.number_input("2. Kademe Kâr Oranı (%)", value=float(config.get("tier2_margin_pct", 35.0)), step=1.0)
        updated_config["tier3_margin_pct"] = st.number_input("3. Kademe (Üstü) Kâr Oranı (%)", value=float(config.get("tier3_margin_pct", 30.0)), step=1.0)

    submitted = st.form_submit_button("💾 Kaydet")

if submitted:
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(updated_config, f, indent=4)
    st.success("Ayarlar başarıyla kaydedildi.")