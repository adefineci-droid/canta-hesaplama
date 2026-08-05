import streamlit as st
import json
import os
import datetime
from fpdf import FPDF

# Sayfa Yapılandırması (Orijinal Tasarım)
st.set_page_config(page_title="Çanta Maliyet Hesaplayıcı", layout="centered", page_icon="🧮")

# Sol Menüyü ve Admin Sayfalarını Satış Ekibinden Tamamen Gizle
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# Ayarları ve Parametreleri Sadece Okur
def ayarları_yukle():
    if os.path.exists("ayarlar.json"):
        try:
            with open("ayarlar.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

ayarlar = ayarları_yukle()

# Başlık ve Orijinal Logolar / Başlıklar
st.title("🧮 Çanta Maliyet Hesaplayıcı")
st.caption("Kumaş çanta üretimi toplam maliyet hesaplama aracı.")

st.header("👤 Müşteri Bilgileri")

customer_name = st.text_input("İlgili Kişi", "")
company_name = st.text_input("Firma Unvanı", "")

col1, col2, col3 = st.columns(3)
with col1:
    E = st.number_input("En (cm)", value=28.0, step=1.0)
with col2:
    Y = st.number_input("Yükseklik (cm)", value=28.0, step=1.0)
with col3:
    K = st.number_input("Körük (cm)", value=15.0, step=1.0)

print_type = st.selectbox(
    "Baskı Türü Seçiniz",
    ["Logo Baskı (Flekso)", "Tifdruk (Lamine)", "Baskısız"],
    help="Baskı metoduna göre maliyetler değişkenlik gösterir."
)

qty = st.number_input("Adet", value=10000, step=500, min_value=1)

payment_term = st.selectbox("Ödeme Vadesi", ["Peşin", "30 Gün", "60 Gün", "90 Gün"])

colors = st.slider("Renk sayısı", min_value=0, max_value=6, value=4)

if st.button("💰 Maliyeti Hesapla"):
    # Arka Plan Hesaplama Motoru (Orijinal Mantık)
    gramaj = float(ayarlar.get("varsayilan_gramaj", 80))
    hammadde_fiyat = float(ayarlar.get("hammadde_kg_fiyat", 2.5))
    kar_marji = float(ayarlar.get("kar_marji_yuzde", 20.0))

    # Alan ve Ağırlık Tüketimi
    m2_alan = ((E + K) * 2 * (Y + 5)) / 10000.0
    canta_agirlik_kg = (m2_alan * gramaj) / 1000.0
    kumas_maliyeti = canta_agirlik_kg * hammadde_fiyat

    if "Baskısız" in print_type:
        baski_maliyeti = 0.0
    elif "Flekso" in print_type:
        baski_maliyeti = colors * 0.02
    else:
        baski_maliyeti = colors * 0.035

    iscilik = 0.05
    birim_maliyet = kumas_maliyeti + baski_maliyeti + iscilik
    birim_satis_fiyati = birim_maliyet * (1 + (kar_marji / 100.0))
    toplam_tutar = birim_satis_fiyati * qty

    st.success("✅ Hesaplama Başarıyla Tamamlandı!")
    
    res1, res2 = st.columns(2)
    with res1:
        st.metric("Birim Fiyat", f"{round(birim_satis_fiyati, 4)} TL")
    with res2:
        st.metric("Toplam Tutar", f"{round(toplam_tutar, 2)} TL")

    # PDF Hazırlama
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    def clean_txt(text):
        tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
        return str(text).translate(tr_map)

    if os.path.exists("pusulabasim_logo.png"):
        pdf.image("pusulabasim_logo.png", x=160, y=8, w=35)

    teklif_no = f"TEKLIF-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"

    pdf.ln(20)
    pdf.cell(0, 10, txt=clean_txt("TEKLİF FORMU"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    pdf.cell(0, 10, txt=clean_txt(f"Teklif No: {teklif_no}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"Tarih: {datetime.date.today().strftime('%d.%m.%Y')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"Firma: {company_name}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"İlgili Kişi: {customer_name}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.cell(0, 10, txt=clean_txt(f"Miktar: {qty} adet"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"Ebat: {E}x{Y}x{K} cm"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"Baskı Türü: {print_type} / Renk: {colors}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"Vade: {payment_term}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"Birim Fiyat: TL {round(birim_satis_fiyati, 4)}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"Toplam Tutar: TL {round(toplam_tutar, 2)}"), new_x="LMARGIN", new_y="NEXT")

    pdf_path = f"{teklif_no}.pdf"
    pdf.output(pdf_path)

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📥 PDF Teklifi İndir",
            data=f,
            file_name=pdf_path,
            mime="application/pdf",
            key=f"dl_btn_satis_{teklif_no}"
        )
