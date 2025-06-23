import streamlit as st
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase başlatma
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase/secrets.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Oturum durumu
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# Giriş ve kayıt sayfası
def login_page():
    st.title("🚛 İhale Oyunu | Giriş")
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])

    with tab1:
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            user_ref = db.collection("users").document(username).get()
            if user_ref.exists and user_ref.to_dict().get("password") == password:
                st.success("Giriş başarılı!")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.experimental_rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre")

    with tab2:
        new_user = st.text_input("Yeni Kullanıcı Adı")
        new_pass = st.text_input("Yeni Şifre", type="password")
        if st.button("Kayıt Ol"):
            if new_user and new_pass:
                user_doc = db.collection("users").document(new_user).get()
                if user_doc.exists:
                    st.error("Bu kullanıcı adı zaten alınmış")
                else:
                    db.collection("users").document(new_user).set({
                        "password": new_pass
                    })
                    st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
            else:
                st.error("Lütfen kullanıcı adı ve şifre girin")

# Kullanıcı oyun bilgileri ilk defa giriliyorsa
def kullanici_bilgileri():
    user_doc = db.collection("kullanicilar").document(st.session_state.username).get()
    if not user_doc.exists:
        st.subheader("🎮 Oyun Bilgilerinizi Girin")
        garaj = st.number_input("Garaj Seviyesi", min_value=1, max_value=10)
        arac_sayisi = st.number_input("Araç Sayısı", min_value=1, max_value=20)
        araclar = []
        for i in range(int(arac_sayisi)):
            araclar.append(st.text_input(f"Araç #{i+1} Adı"))
        dorse = st.number_input("Toplam Dorse Sayısı", min_value=0)

        if st.button("Kaydet"):
            db.collection("kullanicilar").document(st.session_state.username).set({
                "garaj": garaj,
                "arac_sayisi": arac_sayisi,
                "araclar": araclar,
                "dorse": dorse
            })
            st.success("Bilgiler kaydedildi!")
            st.experimental_rerun()
    else:
        st.info("Oyun bilgilerinizi daha önce girdiniz.")

# Ana ekran (sekmeler)
def ana_ekran():
    st.sidebar.title(f"👤 {st.session_state.username}")
    sayfa = st.sidebar.radio("Sayfa Seç", ["İhale Girişi", "Operasyonel Giderler", "Günlük Rapor", "Grafikli Rapor"])

    if sayfa == "İhale Girişi":
        st.header("📦 İhale Girişi")
        ihale_turu = st.text_input("İhale Türü")
        toplam_bedel = st.number_input("Toplam Bedel ($)", min_value=0.0)
        birim_maliyet = st.number_input("Birim Ürün Maliyeti ($)", min_value=0.0)
        urun_sayisi = st.number_input("Ürün Sayısı", min_value=0)

        if st.button("İhaleyi Kaydet"):
            db.collection("ihaleler").document().set({
                "kullanici": st.session_state.username,
                "tarih": datetime.now(),
                "ihale_turu": ihale_turu,
                "toplam_bedel": toplam_bedel,
                "birim_maliyet": birim_maliyet,
                "urun_sayisi": urun_sayisi
            })
            st.success("İhale başarıyla kaydedildi!")

    elif sayfa == "Operasyonel Giderler":
        st.header("🔧 Operasyonel Gider Girişi")
        gider_turu = st.selectbox("Gider Türü", ["Garaj Bakımı", "Garaj Seviye Yükseltme", "Maaş Ödemesi",
                                                  "Araç Bakımı", "Araç Alımı", "Araç Satımı",
                                                  "Dorse Alımı", "Emeklilik/Kovma", "Araç Yükseltme"])
        detay = st.text_input("Detay Bilgisi")
        tutar = st.number_input("Tutar ($)", min_value=0.0)
        gelir_mi = st.checkbox("Bu işlem para kazandırdı mı? (örn: araç satışı)")

        if st.button("Gideri Kaydet"):
            db.collection("giderler").document().set({
                "kullanici": st.session_state.username,
                "tarih": datetime.now(),
                "gider_turu": gider_turu,
                "detay": detay,
                "tutar": tutar,
                "etki": "Gelir" if gelir_mi else "Gider"
            })
            st.success("Gider kaydedildi")

    elif sayfa == "Günlük Rapor":
        st.header("📋 Günlük Rapor")
        st.info("Bu bölümde günlük rapor hesaplamaları olacak. (Henüz eklenmedi)")

    elif sayfa == "Grafikli Rapor":
        st.header("📈 Grafiksel Raporlama")
        st.info("Bu bölümde grafikler olacak. (Henüz eklenmedi)")

# Ana akış
if not st.session_state.logged_in:
    login_page()
else:
    kullanici_bilgileri()
    ana_ekran()
