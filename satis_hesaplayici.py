import streamlit as st
import json
import os
import datetime
from fpdf import FPDF

st.set_page_config(page_title="Pusula Basım - Satış Ekibi Teklif Hesabı", layout="centered", page_icon="🛍️")

# Ayarları sadece OKUR, değiştiremez
def ayarları_yukle():
    if os.path.exists("ayarlar.json"):
        try:
            with open("ayarlar.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

ayarlar = ayarları_yukle()

if os.path.exists("pusulabasim_logo.png"):
    st.image("pusulabasim_logo.png", width=220)

st.title("🛍️ Satış Ekibi Teklif Paneli")
st.caption("Pusula Basım & Ambalaj - Hızlı Maliyet ve Fiyat Hesaplama")
st.divider()

col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input("Müşteri / Firma Adı", "Örnek A.Ş.")
with col2:
    customer_name = st.text_input("İlgili Kişi", "Ahmet Bey")

st.subheader("📐 Çanta Ölçüleri ve Detaylar")
c1, c2, c3 = st.columns(3)
with c1:
    E = st.number_input("En (cm)", value=30.0, step=1.0)
with c2:
    Y = st.number_input("Yükseklik (cm)", value=40.0, step=1.0)
with c3:
    K = st.number_input("Körük (cm)", value=10.0, step=1.0)

col_a, col_b = st.columns(2)
with col_a:
    qty = st.number_input("Sipariş Miktarı (Adet)", value=1000, step=500)
    print_type = st.selectbox("Baskı Türü", ["Flexo", "Ofset", "Baskısız"])
with col_b:
    colors = st.slider("Renk Sayısı", min_value=0, max_value=6, value=1)
    lamination = st.selectbox("Laminasyon / Kaplama", ["Var", "Yok"])

st.divider()

if st.button("💰 Fiyat ve Teklif Hesapla", use_container_width=True, type="primary"):
    # Temel formül hesabı (ayarlar.json dosyasındaki güncel değerleri baz alır)
    gramaj = ayarlar.get("varsayilan_gramaj", 80)
    hammadde_fiyat = ayarlar.get("hammadde_kg_fiyat", 2.5)
    kar_marji = ayarlar.get("kar_marji_yuzde", 20)
    
    # Alan ve Ağırlık hesabı
    m2_alan = ((E + K) * 2 * (Y + 5)) / 10000.0
    canta_agirlik_kg = (m2_alan * gramaj) / 1000.0
    
    # Maliyetler
    kumas_maliyeti = canta_agirlik_kg * hammadde_fiyat
    baski_maliyeti = (colors * 0.02) if print_type != "Baskısız" else 0.0
    iscilik_maliyeti = 0.05
    
    toplam_maliyet = kumas_maliyeti + baski_maliyeti + iscilik_maliyeti
    birim_satis_fiyati = toplam_maliyet * (1 + (kar_marji / 100.0))
    toplam_tutar = birim_satis_fiyati * qty

    # Sonuç Ekranı
    st.success("✅ Hesaplama Başarıyla Tamamlandı!")
    
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("Birim Satış Fiyatı", f"{round(birim_satis_fiyati, 4)} TL")
    with res_col2:
        st.metric("Toplam Teklif Tutarı", f"{round(toplam_tutar, 2)} TL")

    # PDF Üretimi
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
