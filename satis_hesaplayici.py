import streamlit as st
import json
import os
import datetime
from fpdf import FPDF

st.set_page_config(page_title="Pusula Basım - Satış Ekifi Teklif Paneli", layout="wide", page_icon="🛍️")

# 1. Birebir Aynı Ayar Yükleme Mantığı
def ayarları_yukle():
    if os.path.exists("ayarlar.json"):
        try:
            with open("ayarlar.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

ayarlar = ayarları_yukle()

# Logo Gösterimi
if os.path.exists("pusulabasim_logo.png"):
    st.image("pusulabasim_logo.png", width=220)

st.title("🛍️ Pusula Basım - Satış Ekibi Teklif Hesabı")
st.caption("Arka plandaki güncel parametreler kullanılarak otomatik hesaplanır. Parametre değiştirme yetkisi kapalıdır.")
st.divider()

# Kullanıcı / Müşteri Bilgileri
col_m1, col_m2 = st.columns(2)
with col_m1:
    company_name = st.text_input("Müşteri / Firma Adı", "Örnek A.Ş.")
with col_m2:
    customer_name = st.text_input("İlgili Kişi", "Ahmet Bey")

st.markdown("---")

# 2. Ana Dosyanızdaki Birebir Aynı Giriş Alanları
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Ölçüler ve Miktar")
    E = st.number_input("En (cm)", value=30.0, step=1.0)
    Y = st.number_input("Yükseklik (cm)", value=40.0, step=1.0)
    K = st.number_input("Körük (cm)", value=10.0, step=1.0)
    qty = st.number_input("Sipariş Miktarı (Adet)", value=1000, step=500, min_value=1)

with col2:
    st.subheader("2. Malzeme ve Baskı")
    print_type = st.selectbox("Baskı Türü", ["Flexo", "Tifdruk (Lamine)", "Baskısız"])
    colors = st.slider("Baskı Renk Sayısı", min_value=0, max_value=6, value=1)
    gramaj = st.number_input("Kumaş Gramajı (g/m²)", value=int(ayarlar.get("varsayilan_gramaj", 80)), step=5)

with col3:
    st.subheader("3. İmalat Tipi")
    manufacturing_type = st.selectbox("İmalat Tipi", ["Ultrasonik Kaynak", "Dikişli / Müzik Dikiş"])
    lamination = st.selectbox("Laminasyon Durumu", ["Laminasyonlu", "Laminasyonsuz"])

st.divider()

# 3. Ana Dosyanızdaki Birebir Aynı Hesaplama Motoru
if st.button("💰 Teklifi Hesapla ve PDF Oluştur", use_container_width=True, type="primary"):
    
    # Parametreler (ayarlar.json dosyasından canlı okunur)
    hammadde_fiyat = float(ayarlar.get("hammadde_kg_fiyat", 2.5))
    kar_marji = float(ayarlar.get("kar_marji_yuzde", 20.0))
    file_cost = float(ayarlar.get("klise_maliyeti", 0.0))
    
    # Kumaş Tüketim Hesabı
    m2_alan = ((E + K) * 2 * (Y + 5)) / 10000.0
    canta_agirlik_kg = (m2_alan * gramaj) / 1000.0
    kumas_maliyeti = canta_agirlik_kg * hammadde_fiyat
    
    # Baskı ve İşçilik Maliyeti
    if print_type == "Baskısız":
        baski_maliyeti = 0.0
    elif print_type == "Flexo":
        baski_maliyeti = colors * 0.02
    else: # Tifdruk
        baski_maliyeti = colors * 0.035
        
    if lamination == "Laminasyonlu":
        kumas_maliyeti *= 1.15  # Laminasyon farkı
        
    iscilik = 0.08 if manufacturing_type == "Dikişli / Müzik Dikiş" else 0.04
    
    # Toplam Maliyet ve Satış Fiyatı
    birim_maliyet = kumas_maliyeti + baski_maliyeti + iscilik
    birim_fiyat = birim_maliyet * (1 + (kar_marji / 100.0))
    toplam_fiyat = birim_fiyat * qty

    # Ekran Çıktıları
    st.success("✅ Teklif Başarıyla Hesaplandı!")
    
    res1, res2 = st.columns(2)
    with res1:
        st.metric("Birim Satış Fiyatı", f"{round(birim_fiyat, 4)} TL")
    with res2:
        st.metric("Toplam Satış Tutarı", f"{round(toplam_fiyat, 2)} TL")

    # 4. Ana Dosyanızdaki Birebir Aynı PDF Üretici
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
    pdf.cell(0, 10, txt=clean_txt(f"İmalat: {manufacturing_type} ({lamination})"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"Birim Fiyat: TL {round(birim_fiyat, 4)}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, txt=clean_txt(f"Toplam Tutar: TL {round(toplam_fiyat, 2)}"), new_x="LMARGIN", new_y="NEXT")

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
