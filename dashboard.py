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
    bg_app = "#0E1117"
    text_color = "#FAFAFA"
    card_bg = "#1E293B"
    text_main = "#F8FAFC"
    text_sub = "#94A3B8"
    text_accent = "#FBBF24"
    wc_bg = "black"
else:
    bg_app = "#F4F6F9"
    text_color = "#111827"
    card_bg = "#FFFFFF"
    text_main = "#0F172A"
    text_sub = "#64748B"
    text_accent = "#D97706"
    wc_bg = "white"

# CSS Custom untuk Hide Deploy, Border Radius Chart, & Styling Tombol Tema
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    
    html, body, .stApp {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: {bg_app} !important;
        color: {text_color} !important;
    }}

    /* HILANGKAN TOMBOL DEPLOY & MENU DOTS (Sidebar expander TETAP ADA) */
    [data-testid="stHeaderActionElements"] {{ display: none !important; }}
    header {{ background-color: transparent !important; }}

    /* BORDER RADIUS UNTUK GRAFIK (PLOTLY CHARTS) */
    [data-testid="stPlotlyChart"] {{
        background-color: {card_bg};
        border-radius: 15px !important;
        padding: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        overflow: hidden;
    }}

    /* Styling tombol icon tema agar menyatu dan tidak kotak kaku */
    div[data-testid="stButton"] button {{
        background-color: transparent !important;
        border: none !important;
        font-size: 28px !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin-top: 15px;
    }}
    div[data-testid="stButton"] button:hover {{
        transform: scale(1.1);
        transition: 0.2s;
    }}
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
        df['created_at'] = pd.to_datetime(df['created_at'])
        return df, info
    except Exception as e:
        return None, None

@st.cache_resource
def load_model():
    if os.path.exists("my_bertopic_model"):
        return BERTopic.load("my_bertopic_model")
    return None

def clean_text_for_wordcloud(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    stopwords = {'yang', 'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'untuk', 'pada', 'adalah', 
                 'dengan', 'karena', 'akan', 'bisa', 'ada', 'tidak', 'sudah', 'atau', 'yg', 
                 'dg', 'amp', 'rt', 'makan', 'gratis', 'program', 'gizi', 'anak'}
    words = [w for w in text.split() if w not in stopwords and len(w) > 3]
    return " ".join(words)

df, info_topik = load_data()
topic_model = load_model()

if df is None:
    st.error("❌ Error: File CSV tidak ditemukan.")
    st.stop()

# ==============================================================================
# 4. PERHITUNGAN DINAMIS (KOHERENSI & PERIODE)
# ==============================================================================
if 'Coherence_Score' in info_topik.columns:
    rata_coherence = info_topik[info_topik['Topic'] != -1]['Coherence_Score'].mean()
    coherence_dinamis = f"{rata_coherence:.2f}"
else:
    coherence_dinamis = "N/A"

min_date = df['created_at'].min()
max_date = df['created_at'].max()
bulan_indo = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mei', 6: 'Jun', 
              7: 'Jul', 8: 'Ags', 9: 'Sep', 10: 'Okt', 11: 'Nov', 12: 'Des'}

start_year = min_date.strftime('%Y')
end_year = max_date.strftime('%Y')
start_month = bulan_indo[min_date.month]
end_month = bulan_indo[max_date.month]

if start_year == end_year:
    tahun_dinamis = start_year
    periode_dinamis = f"{start_month} - {end_month}" if start_month != end_month else start_month
else:
    tahun_dinamis = f"{start_year} - {end_year}"
    periode_dinamis = f"{start_month} '{start_year[-2:]} - {end_month} '{end_year[-2:]}"

# ==============================================================================
# 5. SIDEBAR NAVIGATION & THEME TOGGLE
# ==============================================================================
with st.sidebar:
    # Menggunakan kolom untuk menyejajarkan Logo dan Icon Tema
    col1, col2 = st.columns([3, 1])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=75)
    with col2:
        # Tombol Icon dinamis
        theme_icon = "☀️" if st.session_state.theme_mode == "Dark Mode" else "🌙"
        st.button(theme_icon, on_click=toggle_theme)

    st.markdown("<h3 style='margin-top:-10px; margin-bottom:15px;'>MBG Analytics</h3>", unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["Executive Summary", "Topic Explorer", "Analytical Charts", "Raw Data"],
        icons=["speedometer2", "search", "pie-chart", "database"],
        default_index=0,
        styles={
            "nav-link-selected": {"background-color": "#FFC107", "color": "#000000", "font-weight": "bold"}
        }
    )
    
    st.markdown("---")
    st.info("**Peneliti:**\n\n**Nanda Pramudya Lestari**\n\nTiga Serangkai University")

# ==============================================================================
# 6. MAIN CONTENT
# ==============================================================================

if selected == "Executive Summary":
    st.title("📊 Executive Summary")
    st.markdown("Analisis sentimen dan pemodelan topik program **Makan Bergizi Gratis (MBG)** di media sosial X.")
    
    # METRIC CARDS
    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        ("TOTAL DATASET", f"{len(df):,}", "Tweet"),
        ("TOPIC CLUSTERS", f"{len(info_topik)-1}", "Kategori"),
        ("COHERENCE SCORE", coherence_dinamis, "Nilai C_v Rata-rata"),
        ("TAHUN ANALISIS", tahun_dinamis, f"Periode {periode_dinamis}")
    ]
    
    for col, (t, v, u) in zip([m1, m2, m3, m4], metrics):
        col.markdown(f"""
            <div style="background-color: {card_bg}; border-radius: 15px; padding: 25px 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #FFC107; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
                <p style="color: {text_sub}; font-size: 11px; margin: 0 0 10px 0; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; text-align: center;">{t}</p>
                <h2 style="color: {text_main}; font-size: 34px; margin: 0 0 10px 0; font-weight: 800; text-align: center;">{v}</h2>
                <p style="color: {text_accent}; font-size: 13px; margin: 0; font-weight: 600; text-align: center;">{u}</p>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")
    
    c1, c2 = st.columns(2)
    
    # KUNCI TRANSPARANSI PLOTLY AGAR CSS BORDER RADIUS BERFUNGSI:
    # paper_bgcolor='rgba(0,0,0,0)' dan plot_bgcolor='rgba(0,0,0,0)'
    
    with c1:
        st.markdown(f"<h3 style='color:{text_main};'>🏆 Distribusi Volume Topik</h3>", unsafe_allow_html=True)
        chart_data = info_topik[info_topik['Topic'] != -1].sort_values('Count', ascending=True).tail(8)
        fig_bar = px.bar(chart_data, x='Count', y='Name', orientation='h', color='Count', color_continuous_scale='Viridis')
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_main),
            margin=dict(l=0, r=0, t=10, b=0), height=350, xaxis_title="Jumlah Tweet", yaxis_title=""
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.markdown(f"<h3 style='color:{text_main};'>🎯 Nilai Koherensi per Topik</h3>", unsafe_allow_html=True)
        if 'Coherence_Score' in info_topik.columns:
            coh_data = info_topik[info_topik['Topic'] != -1].dropna(subset=['Coherence_Score']).sort_values('Coherence_Score')
            
            fig_coh = go.Figure()
            line_color = '#475569' if st.session_state.theme_mode == "Dark Mode" else '#CBD5E1'
            for i in range(len(coh_data)):
                fig_coh.add_shape(type='line', x0=0, y0=i, x1=coh_data.iloc[i]['Coherence_Score'], y1=i, line=dict(color=line_color, width=3))
            fig_coh.add_trace(go.Scatter(x=coh_data['Coherence_Score'], y=coh_data['Name'], mode='markers', marker=dict(color='#D97706', size=14)))
            
            fig_coh.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_main),
                margin=dict(l=0, r=0, t=10, b=0), height=350, showlegend=False, xaxis_title="Coherence Score (C_v)", yaxis_title=""
            )
            st.plotly_chart(fig_coh, use_container_width=True)
        else:
            st.warning("Data Coherence_Score tidak ditemukan.")

elif selected == "Topic Explorer":
    st.title("🔍 Topic Explorer")
    
    active_topics = info_topik[info_topik['Topic'] != -1]
    choice = st.selectbox("Pilih Topik untuk Dianalisis:", active_topics['Name'])
    topic_id = active_topics[active_topics['Name'] == choice]['Topic'].values[0]
    
    tab1, tab2, tab3 = st.tabs(["☁️ Word Cloud", "📄 Sample Dokumen", "📊 Keyword Weights"])
    
    with tab1:
        st.subheader("Visualisasi Kata Kunci (WordCloud)")
        text_data = " ".join(df[df['Topic'] == topic_id]['full_text'].astype(str))
        clean_data = clean_text_for_wordcloud(text_data)
        
        if len(clean_data) > 20:
            wc = WordCloud(width=1000, height=500, background_color=wc_bg, colormap='viridis', max_words=100).generate(clean_data)
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            fig.patch.set_facecolor(bg_app)
            st.pyplot(fig)
            plt.clf()
        else:
            st.warning("Data terlalu sedikit untuk membuat WordCloud.")

    with tab2:
        st.subheader(f"Dokumen dalam Topik: {choice}")
        sample_df = df[df['Topic'] == topic_id][['created_at', 'full_text']].head(100)
        st.dataframe(sample_df, use_container_width=True, height=400)

    with tab3:
        st.subheader("Bobot Kata (c-TF-IDF)")
        if topic_model:
            fig_bar = topic_model.visualize_barchart(topics=[topic_id], n_words=10)
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_main))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Visualisasi ini membutuhkan model BERTopic. Pastikan folder 'my_bertopic_model' ada.")

elif selected == "Analytical Charts":
    st.title("📈 Advanced Analytics")
    
    st.subheader("🍭 Distribusi Frekuensi Topik (Lollipop Chart)")
    lolipop_data = info_topik[info_topik['Topic'] != -1].sort_values('Count')
    
    fig_loli = go.Figure()
    line_color = '#475569' if st.session_state.theme_mode == "Dark Mode" else '#CBD5E1'
    for i in range(len(lolipop_data)):
        fig_loli.add_shape(type='line', x0=0, y0=i, x1=lolipop_data.iloc[i]['Count'], y1=i, line=dict(color=line_color, width=2))
    fig_loli.add_trace(go.Scatter(x=lolipop_data['Count'], y=lolipop_data['Name'], mode='markers', marker=dict(color='#FBBF24' if st.session_state.theme_mode == 'Dark Mode' else '#0F172A', size=14)))
    
    fig_loli.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_main), height=450, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    st.plotly_chart(fig_loli, use_container_width=True)

    st.divider()
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("📅 Tren Percakapan Harian")
        trend = df.resample('D', on='created_at').count()['full_text'].reset_index()
        fig_line = px.line(trend, x='created_at', y='full_text', markers=True, color_discrete_sequence=['#F59E0B'])
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_main), height=350, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col_chart2:
        st.subheader("🌳 Treemap Proporsi Topik")
        fig_tree = px.treemap(info_topik[info_topik['Topic'] != -1], path=['Name'], values='Count', color='Count')
        fig_tree.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=text_main), height=350, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_tree, use_container_width=True)

elif selected == "Raw Data":
    st.title("📑 Data Mentah & Koleksi Dokumen")
    search_query = st.text_input("🔍 Cari kata kunci (misal: anggaran, gizi, susu):", "")
    
    if search_query:
        display_df = df[df['full_text'].astype(str).str.contains(search_query, case=False)]
    else:
        display_df = df

    st.write(f"Menampilkan **{len(display_df):,}** baris data.")
    st.dataframe(display_df[['created_at', 'full_text', 'Topic']].head(1000), use_container_width=True, height=500)