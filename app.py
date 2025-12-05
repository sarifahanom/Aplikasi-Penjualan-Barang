%%writefile app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
from dotenv import load_dotenv
import os

st.set_page_config(page_title="Analisis Pemasukan Barang", page_icon="📦", layout="wide")

st.title("📦 Analisis Data Pemasukan Barang – Toko Sembako")
st.write("Upload file pemasukan barang (CSV / Excel) untuk melihat analisis otomatis.")

# Upload file
file = st.file_uploader("📤 Upload file CSV atau Excel", type=["csv", "xlsx"])

if file:
    # Baca file
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    # Bersihkan kolom indeks otomatis
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    st.subheader("📄 Data Pemasukan Barang")
    st.dataframe(df)

    # Pastikan kolom sesuai
    required_cols = ["tanggal", "nama.barang", "kuantum"]
    if not all(col in df.columns for col in required_cols):
        st.error("⚠️ Data harus berisi kolom: tanggal, nama.barang, kuantum")
        st.stop()

    # Konversi tanggal
    df["tanggal"] = pd.to_datetime(df["tanggal"])

    # Grafik barang paling banyak masuk
    st.subheader("📊 Barang Dengan Pemasukan Terbesar")
    top_items = df.groupby("nama.barang")["kuantum"].sum().reset_index()

    fig1 = px.bar(top_items, x="nama.barang", y="kuantum", title="Total Kuantitas Barang Masuk")
    st.plotly_chart(fig1, use_container_width=True)

    # Tren pemasukan barang
    st.subheader("📈 Tren Pemasukan Barang dari Waktu ke Waktu")
    fig2 = px.line(df, x="tanggal", y="kuantum", color="nama.barang", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

    # ============================
    # 🔥 FITUR BARU: AI COPILOT
    # ============================

    st.subheader("🤖 AI Tanya Jawab Tentang Data")

    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        st.error("❌ GROQ_API_KEY belum diatur di .env")
        st.stop()

    client = Groq(api_key=api_key)

    # Chat box
    user_question = st.text_input("💬 Tanyakan apa saja tentang data pemasukan barang:")

    if user_question:
        df_text = df.to_string()

        prompt = f"""
        Kamu adalah asisten AI untuk analisis pemasukan barang toko sembako.
        Berikut data pemasukan barang:

        {df_text}

        Pertanyaan pengguna:
        {user_question}

        Buat jawaban yang jelas, ringkas, dan berbasis data.
        """

        ai = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        st.success(ai.choices[0].message.content)

else:
    st.info("Silakan upload file dulu untuk memulai analisis.")
