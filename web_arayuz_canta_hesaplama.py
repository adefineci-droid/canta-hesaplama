# web_arayuz_canta_hesaplama.py

import streamlit as st
import pandas as pd
import datetime
import os
import json
from fpdf import FPDF
from auth_system import auth_gate
from hesap_motoru import toplam_maliyet

st.set_page_config(page_title="Çanta Maliyet Hesaplayıcı", layout="centered")

if not auth_gate():
    st.stop()

def load_config():
    config_file = "ayarlar.json"
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "fabric_usd_kg": 1.85, "bopp_usd_kg_12": 3.1, "bopp_usd_kg_20": 2.4,
        "metal_bopp_usd_kg": 2.7, "sap_usd_kg": 2.4, "labor_usd_piece": 0.056,
        "box_usd_piece": 0.006, "lam_outer_usd_m2": 0.08, "lam_inner_usd_m2": 0.06,
        "flexo_setup_usd": 170.0, "flexo_usd_kg": 2.0, "rotogravure_setup_usd": 420.0,
        "rotogravure_usd_kg": 2.8, "plate_cost_eur_cm2": 0.015,
        "usd_to_try": 39.1, "eur_to_try": 42.3,
        "tier1_max_qty": 40000, "tier1_margin_pct": 40.0,
        "tier2_max_qty": 90000, "tier2_margin_pct": 35.0,
        "tier3_margin_pct": 30.0
    }

def get_profit_margin(qty, cfg):
    t1_max = cfg.get("tier1_max_qty", 40000)
    t2_max = cfg.get("tier2_max_qty", 90000)
    
    if qty <= t1_max:
        return cfg.get("tier1_margin_pct", 40.0)
    elif qty <= t2_max:
        return cfg.get("tier2_margin_pct", 35.0)
    else:
        return cfg.get("tier3_margin_pct", 30.0)

st.title("🧮 Çanta Maliyet Hesaplayıcı")
st.markdown("Kumaş çanta üretimi toplam maliyet hesaplama aracı.")

st.subheader("👤 Müşteri Bilgileri")
customer_name = st.text_input("İlgili Kişi")
company_name = st.text_input("Firma Unvanı")

col1, col2, col3 = st.columns(3)
with col1:
    E = st.number_input("En (cm)", value=28)
with col2:
    Y = st.number_input("Yükseklik (cm)", value=28)
with col3:
    K = st.number_input("Körük (cm)", value=15)

print_type = st.selectbox(
    "Baskı Türü Seçiniz",
    ["Logo Baskı (Flekso)", "Fotoğraf Baskı (Rotogravür)"],
    help="Logo baskı için Flekso, fotoğraf baskı için Rotogravür seçiniz."
)

qty = st.number_input("Adet", value=10000, step=1000)
payment_term = st.selectbox(
    "Ödeme Vadesi",
    ["Peşin", "30 Gün", "60 Gün", "90 Gün", "120 Gün"]
)
colors = st.slider("Renk sayısı", min_value=1, max_value=6, value=4)

vade_gun_map = {"Peşin": 0, "30 Gün": 1, "60 Gün": 2, "90 Gün": 3, "120 Gün": 4}

if st.button("💰 Maliyeti Hesapla"):
    cfg = load_config()

    if print_type == "Logo Baskı (Flekso)":
        bopp_g_m2 = 20 * 0.91
        bopp_usd_kg = cfg.get("bopp_usd_kg_20", 2.4)
        flexo_setup_usd = cfg.get("flexo_setup_usd", 170.0)
        flexo_usd_kg = cfg.get("flexo_usd_kg", 2.0)
        plate_cost_eur_cm2 = cfg.get("plate_cost_eur_cm2", 0.015)
    else:
        bopp_g_m2 = 12 * 0.91
        bopp_usd_kg = cfg.get("bopp_usd_kg_12", 3.1)
        flexo_setup_usd = cfg.get("rotogravure_setup_usd", 420.0)
        flexo_usd_kg = cfg.get("rotogravure_usd_kg", 2.8)
        plate_cost_eur_cm2 = 0.0

    girdi = {
        "E": E, "Y": Y, "K": K, "qty": qty, "num_colors": colors,
        "fabric_g_m2": 50, "fabric_usd_kg": cfg.get("fabric_usd_kg", 1.85),
        "bopp_g_m2": bopp_g_m2, "metal_bopp_g_m2": 11.83,
        "sap_g_m2": 65, "sap_usd_kg": cfg.get("sap_usd_kg", 2.4),
        "labor_usd_piece": cfg.get("labor_usd_piece", 0.056),
        "box_usd_piece": cfg.get("box_usd_piece", 0.006),
        "lam_outer_usd_m2": cfg.get("lam_outer_usd_m2", 0.08),
        "lam_inner_usd_m2": cfg.get("lam_inner_usd_m2", 0.06),
        "metal_bopp_usd_kg": cfg.get("metal_bopp_usd_kg", 2.7),
        "bopp_usd_kg": bopp_usd_kg,
        "usd_to_try": cfg.get("usd_to_try", 39.1),
        "eur_to_try": cfg.get("eur_to_try", 42.3),
        "fire_low": 1.05, "fire_mid": 1.04, "fire_high": 1.03,
        "bopp_fire": 1.08, "labor_fire": 1.0,
        "sap_length_cm": 90, "sap_width_cm": 5,
        "flexo_setup_usd": flexo_setup_usd,
        "flexo_usd_kg": flexo_usd_kg,
        "plate_cost_eur_cm2": plate_cost_eur_cm2,
        "payment_term": payment_term
    }

    toplam = toplam_maliyet(girdi)
    kar_orani = get_profit_margin(qty, cfg)
    maliyet_uzeri_vade_farki = toplam * (0.05 * vade_gun_map[payment_term])
    satis_fiyati = (toplam + maliyet_uzeri_vade_farki) * (1 + kar_orani / 100)
    birim_fiyat = satis_fiyati / qty

    st.success(f"Toplam Maliyet: ₺{toplam:,.2f}")
    st.info(f"Satış Fiyatı (%{kar_orani} Kar + Vade): ₺{satis_fiyati:,.2f}")
    st.info(f"Birim Satış Fiyatı: ₺{birim_fiyat:,.4f}")

    teklif_no = f"TEKLIF-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    teklif_kaydi = {
        "Teklif No": teklif_no,
        "Tarih": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "İlgili Kişi": customer_name,
        "Firma": company_name,
        "Adet": qty,
        "En": E,
        "Boy": Y,
        "Körük": K,
        "Baskı Türü": print_type,
        "Vade": payment_term,
        "Renk Sayısı": colors,
        "Toplam Maliyet (TRY)": round(toplam, 2),
        "Satış Fiyatı (TRY)": round(satis_fiyati, 2),
        "Birim Fiyat (TRY)": round(birim_fiyat, 4)
    }

    dosya_yolu = "teklif_kayitlari.csv"
    df = pd.DataFrame([teklif_kaydi])
    if os.path.exists(dosya_yolu):
        df.to_csv(dosya_yolu, mode="a", index=False, header=False, encoding="utf-8-sig")
    else:
        df.to_csv(dosya_yolu, index=False, encoding="utf-8-sig")

    st.success(f"📄 Teklif kaydedildi: {teklif_no}")

    # PDF Üretimi
   # PDF Üretimi (Unicode / Türkçe Karakter Güvenli)
    pdf = FPDF()
    pdf.add_page()
    
    # DejaVuSans fontu varsa yükle, yoksa latin-1 dönüşümlü varsayılan font kullan
    has_unicode_font = False
    if os.path.exists("DejaVuSans.ttf"):
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf')
        if os.path.exists("DejaVuSans-Bold.ttf"):
            pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf')
        pdf.set_font("DejaVu", size=12)
        has_unicode_font = True
    elif os.path.exists("ttf/DejaVuSans.ttf"):
        pdf.add_font('DejaVu', '', 'ttf/DejaVuSans.ttf')
        if os.path.exists("ttf/DejaVuSans-Bold.ttf"):
            pdf.add_font('DejaVu', 'B', 'ttf/DejaVuSans-Bold.ttf')
        pdf.set_font("DejaVu", size=12)
        has_unicode_font = True
    else:
        pdf.set_font("Helvetica", size=12)

    def clean_txt(text):
        if has_unicode_font:
            return str(text)
        # Unicode font yoksa Türkçe karakterleri latin-1 uyumlu harflere çevirir
        tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
        return str(text).translate(tr_map)

    if os.path.exists("pusulabasim_logo.png"):
        pdf.image("pusulabasim_logo.png", x=160, y=8, w=35)

    pdf.ln(20)
    pdf.cell(0, 10, txt=clean_txt("TEKLİF FORMU"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    pdf.cell(0, 10, txt=clean_txt(f"Teklif No: {teklif_no}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"Tarih: {teklif_kaydi['Tarih']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"Firma: {company_name}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"İlgili Kişi: {customer_name}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.cell(0, 10, txt=clean_txt(f"Miktar: {qty} adet"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"Ebat: {E}x{Y}x{K} cm"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"Baskı Türü: {print_type} / Renk: {colors}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"Birim Fiyat: TL {round(birim_fiyat,4)}"), new_x="LMARGIN", new_y="NEXT")

    pdf_path = f"{teklif_no}.pdf"
    pdf.output(pdf_path)

    with open(pdf_path, "rb") as f:
        st.download_button("📥 PDF Teklifi İndir", f, file_name=pdf_path)

    with open(pdf_path, "rb") as f:
        st.download_button("📥 PDF Teklifi İndir", f, file_name=pdf_path)
