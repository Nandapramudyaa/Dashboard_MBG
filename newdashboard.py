import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from bertopic import BERTopic
import re
from streamlit_option_menu import option_menu 

# ==============================================================================
# 1. PAGE CONFIG & SESSION STATE (UNTUK TEMA)
# ==============================================================================
st.set_page_config(
    page_title="Dashboard MBG | Nanda Pramudya Lestari",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inisialisasi state untuk mode Dark/Light
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark Mode"

def toggle_theme():
    if st.session_state.theme_mode == "Dark Mode":
        st.session_state.theme_mode = "Light Mode"
    else:
        st.session_state.theme_mode = "Dark Mode"

# ==============================================================================
# 2. THEME VARIABLES & DYNAMIC CSS
# ==============================================================================
if st.session_state.theme_mode == "Dark Mode":
    bg_app, text_color, card_bg, text_main, text_sub, text_accent, wc_bg = "#0E1117", "#FAFAFA", "#1E293B", "#F8FAFC", "#94A3B8", "#FBBF24", "black"
else:
    bg_app, text_color, card_bg, text_main, text_sub, text_accent, wc_bg = "#F4F6F9", "#111827", "#FFFFFF", "#0F172A", "#64748B", "#D97706", "white"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    
    html, body, .stApp {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: {bg_app} !important; color: {text_color} !important; }}
    [data-testid="stHeaderActionElements"] {{ display: none !important; }}
    header {{ background-color: transparent !important; }}
    [data-testid="stPlotlyChart"] {{ background-color: {card_bg}; border-radius: 15px !important; padding: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); overflow: hidden; }}
    div[data-testid="stButton"] button {{ background-color: transparent !important; border: none !important; font-size: 28px !important; box-shadow: none !important; padding: 0 !important; margin-top: 15px; }}
    div[data-testid="stButton"] button:hover {{ transform: scale(1.1); transition: 0.2s; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. HELPER FUNCTIONS & DATA LOADING
# ==============================================================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data_hasil_topik.csv")
        info = pd.read_csv("info_topik_lengkap.csv")
        
        # Load data tren jika ada
        try:
            df_trend = pd.read_csv("trend_waktu_topik.csv")
        except:
            df_trend = None

        # Menyesuaikan kolom waktu
        date_col = next((c for c in df.columns if c in ['waktu_tweet', 'created_at', 'date']), None)
        if date_col:
            df['waktu_tweet'] = pd.to_datetime(df[date_col], errors='coerce')
        else:
            df['waktu_tweet'] = pd.to_datetime('2025-01-01')

        return df, info, df_trend
    except Exception as e:
        return None, None, None

@st.cache_resource
def load_model():
    if os.path.exists("my_bertopic_model"):
        return BERTopic.load("my_bertopic_model")
    return None

df, info_topik, df_trend = load_data()
topic_model = load_model()

if df is None:
    st.error("❌ Error: File CSV tidak ditemukan. Pastikan data_hasil_topik.csv dan info_topik_lengkap.csv ada di folder yang sama.")
    st.stop()

# Kalkulasi Metrik
if 'Coherence_Score' in info_topik.columns:
    rata_coherence = info_topik[info_topik['Topic'] != -1]['Coherence_Score'].mean()
    coherence_dinamis = f"{rata_coherence:.3f}"
else:
    coherence_dinamis = "N/A"

# ==============================================================================
# 4. SIDEBAR NAVIGATION
# ==============================================================================
with st.sidebar:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=75)
    with col2:
        theme_icon = "☀️" if st.session_state.theme_mode == "Dark Mode" else "🌙"
        st.button(theme_icon, on_click=toggle_theme)

    st.markdown("<h3 style='margin-top:-10px; margin-bottom:15px;'>MBG Analytics</h3>", unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["Executive Summary", "Topic Explorer", "Trend Analysis", "Model Evaluation", "Data Preprocessing"],
        icons=["speedometer2", "search", "graph-up-arrow", "check-circle", "database-gear"],
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#FFC107", "color": "#000000", "font-weight": "bold"}}
    )
    
    st.markdown("---")
    st.info("**Peneliti:**\n\n**Nanda Pramudya Lestari**\n\nUniversitas Tiga Serangkai")

# ==============================================================================
# 5. MAIN CONTENT ROUTING
# ==============================================================================

if selected == "Executive Summary":
    st.title("📊 Executive Summary")
    st.markdown("Analisis diskursus publik mengenai **Program Makan Bergizi Gratis (MBG)** di media sosial X.")
    
    # METRIC CARDS
    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        ("TOTAL DOKUMEN", f"{len(df):,}", "Tweet Dianalisis"),
        ("TOPIC CLUSTERS", f"{len(info_topik)-1}", "Kategori Topik"),
        ("COHERENCE SCORE", coherence_dinamis, "Kualitas Model (c_v)"),
        ("ALGORITMA", "BERTopic", "BERT + HDBSCAN")
    ]
    
    for col, (t, v, u) in zip([m1, m2, m3, m4], metrics):
        col.markdown(f"""
            <div style="background-color: {card_bg}; border-radius: 15px; padding: 25px 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #FFC107; text-align: center; height: 100%;">
                <p style="color: {text_sub}; font-size: 11px; font-weight: 700; margin: 0;">{t}</p>
                <h2 style="color: {text_main}; font-size: 30px; font-weight: 800; margin: 10px 0;">{v}</h2>
                <p style="color: {text_accent}; font-size: 12px; font-weight: 600; margin: 0;">{u}</p>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<h4 style='color:{text_main};'>🏆 Distribusi Volume Topik</h4>", unsafe_allow_html=True)
        chart_data = info_topik[info_topik['Topic'] != -1].sort_values('Count', ascending=True)
        fig_bar = px.bar(chart_data, x='Count', y='Name', orientation='h', color='Count', color_continuous_scale='Blues')
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_main), height=380, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("📊 Persentase Volume Topik")
        valid_topics = info_topik[info_topik['Topic'] != -1]
        
        fig_pie = px.pie(
            valid_topics, 
            names='Name', 
            values='Count',
            hole=0.4, # Membuat bagian tengah bolong (Donut Chart) agar lebih elegan
            color_discrete_sequence=px.colors.sequential.YlOrBr_r
        )
        
        # Menampilkan persentase di dalam diagram
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font=dict(color=text_main), 
            height=350, 
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False # Disembunyikan karena label sudah ada di dalam diagram
        )
        st.plotly_chart(fig_pie, use_container_width=True)
# ------------------------------------------------------------------------------
elif selected == "Topic Explorer":
    st.title("🔍 Topic Explorer")

    active_topics = info_topik[info_topik['Topic'] != -1]
    choice = st.selectbox("Pilih Topik untuk Dianalisis:", active_topics['Name'])
    topic_id = active_topics[active_topics['Name'] == choice]['Topic'].values[0]
    
    tab1, tab2, tab3 = st.tabs(["☁️ Word Cloud", "📊 Keyword Weights (c-TF-IDF)", "📄 Sample Dokumen"])
    
    with tab1:
        text_data = " ".join(df[df['Topic'] == topic_id]['step_6_final'].dropna().astype(str))
        if len(text_data) > 20:
            wc = WordCloud(width=1000, height=450, background_color=wc_bg, colormap='viridis', max_words=80).generate(text_data)
            fig, ax = plt.subplots(figsize=(10, 4.5))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            fig.patch.set_facecolor(bg_app)
            st.pyplot(fig)
            plt.clf()
        else:
            st.warning("Data terlalu sedikit untuk membuat WordCloud.")

    with tab2:
        if topic_model:
            fig_bar = topic_model.visualize_barchart(topics=[topic_id], n_words=10)
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_main))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Model BERTopic tidak termuat.")

    with tab3:
        sample_df = df[df['Topic'] == topic_id][['waktu_tweet', 'full_text']].head(50)
        st.dataframe(sample_df, use_container_width=True)

# ------------------------------------------------------------------------------
elif selected == "Trend Analysis":
    st.title("📈 Trend Analysis (Intensitas Pembahasan)")
   
    if df_trend is not None:
        # Hapus kolom 'Name' bawaan lama agar tidak terjadi bentrok (Name_x / Name_y)
        if 'Name' in df_trend.columns:
            df_trend = df_trend.drop(columns=['Name'])
            
        # Menyatukan data dengan nama topik terbaru dari info_topik
        df_trend = df_trend.merge(info_topik[['Topic', 'Name']], on='Topic', how='left')
        
        # Membuat grafik garis
        fig_trend = px.line(df_trend, x='Timestamp', y='Frequency', color='Name', markers=True, 
                            title="Topics over Time (Berdasarkan Bulan)")
        
        # PERBARUAN: Menghapus pengaturan letak legend agar otomatis pindah ke samping kanan
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font=dict(color=text_main), 
            height=500, 
            xaxis_title="Waktu", 
            yaxis_title="Frekuensi Tweet",
            legend_title_text="Daftar Topik" # Memberi judul pada legend di samping
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.info("💡 **Analisis:** Grafik di atas menunjukkan pergerakan intensitas setiap topik. Topik yang grafiknya melonjak tajam menandakan adanya isu viral (puncak pembahasan) pada periode waktu tersebut.")
    else:
        st.error("⚠️ File 'trend_waktu_topik.csv' tidak ditemukan. Pastikan sudah didownload dari Colab.")

# ------------------------------------------------------------------------------
elif selected == "Model Evaluation":
    st.title("✅ Model Evaluation")
    
    tab_coh, tab_dist = st.tabs(["🎯 Lollipop Chart (Koherensi)", "🌌 Intertopic Distance Map (UMAP)"])
    
    with tab_coh:
        st.subheader("Evaluasi Koherensi Topik (c_v)")
        if 'Coherence_Score' in info_topik.columns:
            coh_data = info_topik[info_topik['Topic'] != -1].dropna(subset=['Coherence_Score']).sort_values('Coherence_Score')
            fig_coh = go.Figure()
            line_color = '#475569' if st.session_state.theme_mode == "Dark Mode" else '#CBD5E1'
            for i in range(len(coh_data)):
                fig_coh.add_shape(type='line', x0=0, y0=i, x1=coh_data.iloc[i]['Coherence_Score'], y1=i, line=dict(color=line_color, width=3, dash='dot'))
            fig_coh.add_trace(go.Scatter(
                x=coh_data['Coherence_Score'], y=coh_data['Name'], mode='markers+text',
                text=[f"{x:.3f}" for x in coh_data['Coherence_Score']], textposition="middle right",
                marker=dict(color='#D97706', size=16, line=dict(color='white', width=2))
            ))
            fig_coh.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_main), height=450, showlegend=False, xaxis=dict(range=[0, max(coh_data['Coherence_Score']) + 0.1]))
            st.plotly_chart(fig_coh, use_container_width=True)
            st.success(f"📌 **Rata-rata Koherensi:** {coherence_dinamis}. Skor ini sangat representatif untuk analisis *noisy text* pada media sosial.")
        else:
            st.warning("Data Koherensi tidak tersedia.")

    with tab_dist:
        st.subheader("Pola Persebaran Topik (Intertopic Distance Map)")
        if topic_model:
            fig_dist = topic_model.visualize_topics()
            fig_dist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_main), height=600)
            st.plotly_chart(fig_dist, use_container_width=True)
            st.info("📌 **Cara Membaca:** Kedekatan antar lingkaran menandakan kemiripan makna semantik. Lingkaran yang menyendiri memiliki kata kunci yang sangat unik/berbeda dari topik lainnya.")
        else:
            st.warning("⚠️ Model BERTopic tidak termuat, grafik jarak topik tidak dapat ditampilkan.")

# ------------------------------------------------------------------------------
elif selected == "Data Preprocessing":
    st.title("📑 Data Transparency & Preprocessing")
    st.markdown("Halaman ini membuktikan tahapan pembersihan data (*text preprocessing*) sebelum dimasukkan ke dalam algoritma BERTopic.")
    
    tab_raw, tab_prep = st.tabs(["🔎 Dataset Final", "🔄 Jejak Preprocessing (Before-After)"])
    
    with tab_raw:
        st.subheader("Dataset Lengkap dengan Label Topik")
        query = st.text_input("🔍 Cari Keyword pada Teks Asli:")
        df_safe = df.fillna("")
        res = df_safe[df_safe['full_text'].str.contains(query, case=False)] if query else df_safe
        st.dataframe(res[['waktu_tweet', 'full_text', 'step_6_final', 'Topic']].head(500), use_container_width=True)

    with tab_prep:
        st.subheader("Transformasi Teks (Before - After)")
        if 'step_2_cleaning' in df.columns:
            st.dataframe(
                df[['full_text', 'step_2_cleaning', 'step_4_str', 'step_5_stemmed', 'step_6_final']].head(100), 
                use_container_width=True,
                column_config={
                    "full_text": "1. Asli (Kotor)",
                    "step_2_cleaning": "2. Cleaning",
                    "step_4_str": "3. Normalisasi",
                    "step_5_stemmed": "4. Stemming",
                    "step_6_final": "5. Final (Siap Model)"
                }
            )
        else:
            st.warning("⚠️ Kolom riwayat preprocessing tidak ditemukan di dalam CSV. Pastikan dataframe disave secara utuh dari Colab.")