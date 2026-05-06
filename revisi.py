import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. Fitur Login Profesional ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login():
    st.title("Autentikasi Dashboard")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if username == "Kelompok_2" and password == "properti2026":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Tanya Suami Furina buat tau user ama pw nya, Ahihihihihi")

if not st.session_state['logged_in']:
    login()
    st.stop()
else:
    # --- 2. Konfigurasi UI/UX Dashboard ---
    st.set_page_config(page_title="Analisis Strategis Properti", layout="wide")
    
    if st.sidebar.button("Keluar"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>Analisis Strategis Pasar Properti</h1>", unsafe_allow_html=True)

    # --- 3. Fungsi Cache untuk Load Data ---
    @st.cache_data
    def load_data():
        try:
            df = pd.read_csv('Cleaned_Final_Rumah.csv') 
            return df
        except FileNotFoundError:
            return None

    # --- 4. Fungsi Cache untuk Statistik (Agar Perhitungan Lebih Cepat) ---
    @st.cache_data
    def get_location_stats(df):
        location_counts = df['Lokasi'].value_counts().reset_index()
        location_counts.columns = ['Lokasi', 'Jumlah Properti']
        return location_counts

    @st.cache_data
    def get_bedroom_correlation(df):
        # Menghitung rata-rata harga berdasarkan Kamar Tidur
        df_corr = df.groupby('Kamar Tidur')['Harga'].mean().reset_index()
        # Filter angka spesifik sesuai permintaan
        daftar_kt = [2, 3, 4, 5, 6, 7,8,9]
        return df_corr[df_corr['Kamar Tidur'].isin(daftar_kt)]

    dataset = load_data()

    if dataset is not None:
        # Menjalankan fungsi statistik yang sudah di-cache
        location_counts = get_location_stats(dataset)
        df_corr2 = get_bedroom_correlation(dataset)

        # Persiapan data untuk Bar & Pie Chart
        top_50_locations = location_counts.head(50)
        top_5_locations = location_counts.head(5)
        other_count = location_counts['Jumlah Properti'].iloc[5:].sum()
        pie_data = pd.concat([top_5_locations, pd.DataFrame({'Lokasi': ['Lainnya'], 'Jumlah Properti': [other_count]})])

        # --- Baris 1: Bar Chart & Pie Chart ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Jumlah Properti per Lokasi (50 Teratas)")
            fig1, ax1 = plt.subplots(figsize=(10, 8))
            sns.barplot(x='Lokasi', y='Jumlah Properti', data=top_50_locations, hue='Lokasi', palette='viridis', legend=False, ax=ax1)
            plt.xticks(rotation=90)
            ax1.grid(axis='y', linestyle='--', alpha=0.7)
            st.pyplot(fig1)
            
            st.write("""Diagram batang ini menunjukkan jumlah properti di berbagai wilayah. Wilayah dengan batang tertinggi merepresentasikan area dengan tingkat ketersediaan unit yang paling banyak. """)

        with col2:
            st.subheader("Proporsi Properti per Lokasi dengan (%)")
            fig2, ax2 = plt.subplots(figsize=(10, 8))
            ax2.pie(pie_data['Jumlah Properti'], labels=pie_data['Lokasi'], autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'black'})
            st.pyplot(fig2)

            st.write(""" Diagram pie ini memberikan gambaran dari seberapa persen kami memberikan properti ke lokasi dengan menggunakan persen(%). Kita dapat melihat secara instan wilayah mana yang mendominasi inventori properti yang tersedia.""")

        # --- Baris 2: Scatter Plot ---
        st.markdown("---")
        st.subheader("Hubungan Luas Bangunan dan Harga")
        
        def format_harga(nominal):
            if nominal >= 1_000_000_000:
                return f"{nominal / 1_000_000_000:.1f} Miliar".replace('.', ',')
            else:
                return f"{int(nominal / 1_000_000)} Juta"
        
        df_scatter = dataset.head(50).copy()
        df_scatter['Harga_Label'] = df_scatter['Harga'].apply(format_harga)

        fig3, ax3 = plt.subplots(figsize=(16, 10))
        ax3.scatter(df_scatter['Luas Bangunan'], df_scatter['Harga_Label'], alpha=0.6, s=100, color='#2C3E50')
        ax3.grid(True, linestyle='--', alpha=0.7)
        ax3.invert_yaxis() 
        st.pyplot(fig3)

        st.write("""Scatter plot ini buat ngasih tau hubungan antara Luas Bangunan (sumbu X) dan Harga (sumbu Y) untuk data dari rumah pertama sampai ke data ke 32""")

        # --- Baris 3: Diagram Korelasi Kamar Tidur & Harga ---
        st.markdown("---")
        col_diag, col_text = st.columns([2, 1]) 

        with col_diag:
            st.subheader("Korelasi Jumlah Kamar Tidur terhadap Harga")
            
            fig4, ax4 = plt.subplots(figsize=(12, 7))
            sns.barplot(x='Kamar Tidur', y='Harga', data=df_corr2, color='teal', ax=ax4)
            
            def format_func(value, tick_number):
                if value >= 1_000_000_000:
                    return f'{value/1_000_000_000:.1f}M'.replace('.', ',')
                elif value >= 1_000_000:
                    return f'{int(value/1_000_000)}Jt'
                return f'{int(value)}'

            ax4.yaxis.set_major_formatter(plt.FuncFormatter(format_func))
            ax4.set_xlabel("Jumlah Kamar Tidur (Unit)")
            ax4.set_ylabel("Rata-Rata Harga (IDR)")
            st.pyplot(fig4)

        with col_text:
            st.write("""Diagram ini bertujuan untuk memvisualisasikan korelasi antara kapasitas hunian yang direpresentasikan oleh jumlah kamar tidur dengan nilai rata-rata harga properti di pasar. """)

        # --- 5. Fitur Filter Data ---
        st.markdown("---")
        st.subheader("Filter Data Properti")
                
        list_lokasi = dataset['Lokasi'].unique().tolist()
        lokasi_pilihan = st.multiselect("Pilih Lokasi:", options=list_lokasi, default=list_lokasi[:2])
                
        harga_min, harga_max = int(dataset['Harga'].min()), int(dataset['Harga'].max())
        rentang_harga = st.slider("Rentang Harga (IDR):", harga_min, harga_max, (harga_min, harga_max // 4))

        data_terfilter = dataset[
            (dataset['Lokasi'].isin(lokasi_pilihan)) & 
            (dataset['Harga'] >= rentang_harga[0]) & 
            (dataset['Harga'] <= rentang_harga[1])
        ]

        st.write(f"Ditemukan {len(data_terfilter)} properti yang sesuai.")
        st.dataframe(data_terfilter, use_container_width=True)

    else:
        st.error("File 'Cleaned_Final_Rumah.csv' tidak ditemukan.")