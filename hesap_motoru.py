# hesap_motoru.py

def hesap_kumas(g):
    en = g["E"]
    yuk = g["Y"]
    koruk = g["K"]
    adet = g["qty"]
    m2_per_piece = ((2 * yuk + koruk + 14) / 100) * ((en + koruk + 2) / 100)
    total_m2 = m2_per_piece * adet * g["fire_mid"]
    kg = total_m2 * g["fabric_g_m2"] / 1000
    maliyet = kg * g["fabric_usd_kg"] * g["usd_to_try"]
    return kg, total_m2, maliyet

def hesap_bopp(g, base_m2):
    m2 = base_m2 * g["bopp_fire"]
    kg = m2 * g["bopp_g_m2"] / 1000
    maliyet = kg * g["bopp_usd_kg"] * g["usd_to_try"]
    return kg, m2, maliyet

def hesap_metal_bopp(g, base_m2):
    m2 = base_m2 * g["fire_mid"]
    kg = m2 * g["metal_bopp_g_m2"] / 1000
    maliyet = kg * g["metal_bopp_usd_kg"] * g["usd_to_try"]
    return kg, m2, maliyet

def hesap_laminasyon(g, dis_m2, ic_m2):
    dis = dis_m2 * g["lam_outer_usd_m2"] * g["usd_to_try"]
    ic = ic_m2 * g["lam_inner_usd_m2"] * g["usd_to_try"]
    return dis + ic

def hesap_sap(g):
    area = (g["sap_length_cm"] / 100) * (g["sap_width_cm"] / 100)
    total_area = area * g["qty"]
    kg = total_area * g["sap_g_m2"] / 1000
    maliyet = kg * g["sap_usd_kg"] * g["usd_to_try"]
    return kg, maliyet

def hesap_iscilik(g):
    return g["qty"] * g["labor_usd_piece"] * g["usd_to_try"]

def hesap_koli(g):
    return g["qty"] * g["box_usd_piece"] * g["usd_to_try"]

def hesap_flexo(g, bopp_kg):
    ek_kg = max(0, bopp_kg - 100)
    usd = g["flexo_setup_usd"] + ek_kg * g["flexo_usd_kg"]
    return usd * g["usd_to_try"]

def hesap_klise(g):
    genislik = (2 * g["Y"] + g["K"] + 14)
    uzunluk = (g["E"] + g["K"] + 2)
    alan_cm2 = genislik * uzunluk * g["num_colors"]
    eur = alan_cm2 * g["plate_cost_eur_cm2"]
    return eur * g["eur_to_try"]

def toplam_maliyet(g):
    kumas_kg, kumas_m2, kumas_tl = hesap_kumas(g)
    bopp_kg, bopp_m2, bopp_tl = hesap_bopp(g, kumas_m2 / g["fire_mid"])
    metal_kg, metal_m2, metal_tl = hesap_metal_bopp(g, kumas_m2 / g["fire_mid"])
    lam_tl = hesap_laminasyon(g, bopp_m2, metal_m2)
    sap_kg, sap_tl = hesap_sap(g)
    iscilik_tl = hesap_iscilik(g)
    koli_tl = hesap_koli(g)
    flexo_tl = hesap_flexo(g, bopp_kg)
    klise_tl = hesap_klise(g)

    toplam = kumas_tl + bopp_tl + metal_tl + lam_tl + sap_tl + iscilik_tl + koli_tl + flexo_tl + klise_tl
    return round(toplam, 2)
