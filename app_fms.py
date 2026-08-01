import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==================== KONFIGURASI HALAMAN ====================
st.set_page_config(
    page_title="Dashboard FMS - PT. Bumiputera",
    page_icon="🚛",
    layout="wide"
)

# ==================== CSS CUSTOM STYLING ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #f4f7fb;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1600px;
}

/* HEADER */
.dashboard-header {
    background: linear-gradient(135deg, #0f172a, #1d4ed8);
    padding: 30px;
    border-radius: 22px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 15px 35px rgba(0,0,0,.12);
}
.dashboard-header h1 {
    margin: 0;
    font-size: 34px;
    font-weight: 700;
}
.dashboard-header p {
    margin-top: 6px;
    opacity: .8;
}

/* KPI CARDS */
.kpi {
    background: white;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 5px 20px rgba(0,0,0,.05);
    transition: .25s;
    border: 1px solid #edf2f7;
    position: relative;
}
.kpi:hover {
    transform: translateY(-6px);
    box-shadow: 0 15px 35px rgba(0,0,0,.10);
}
.kpi-icon {
    font-size: 28px;
    margin-bottom: 6px;
}
.kpi-title {
    font-size: 13px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: .8px;
    font-weight: 500;
}
.kpi-value {
    font-size: 34px;
    font-weight: 700;
    color: #0f172a;
    margin-top: 6px;
}
.kpi-footer {
    margin-top: 8px;
    color: #2563eb;
    font-size: 13px;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #0f172a;
}
section[data-testid="stSidebar"] * {
    color: white;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stFileUploader label {
    color: #94a3b8 !important;
}
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
    background: rgba(255,255,255,0.06);
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* BUTTON */
.stButton > button {
    background: #2563eb;
    color: white;
    border-radius: 10px;
    border: none;
    padding: .55rem 1rem;
    font-weight: 500;
    transition: .2s;
}
.stButton > button:hover {
    background: #1d4ed8;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(37,99,235,0.3);
}

/* DATAFRAME */
div[data-testid="stDataFrame"] {
    border-radius: 14px;
    border: 1px solid #edf2f7;
    overflow: hidden;
}
div[data-testid="stDataFrame"] thead tr th {
    background: #f8fafc !important;
    font-weight: 600 !important;
}

/* PLOTLY CONTAINER */
.js-plotly-plot .plotly .main-svg {
    border-radius: 12px;
}

/* RESPONSIVE DESIGN */
@media (max-width: 768px) {
    .dashboard-header { padding: 20px; }
    .dashboard-header h1 { font-size: 24px; }
    .kpi { padding: 16px; }
    .kpi-value { font-size: 26px; }
}
</style>
""", unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================
def fmt_num(n):
    return f"{n:,}".replace(',', '.')

def cat_time(t):
    if pd.isna(t):
        return 'Unknown'
    try:
        h = int(str(t).strip().split(':')[0])
    except:
        return 'Unknown'
    return f"{h:02d}:00-{h+1:02d}:59"

def detect_columns(df):
    col_date = next((c for c in df.columns if c.lower() in ['tanggal', 'date']), None)
    col_time = next((c for c in df.columns if c.lower() in ['time', 'jam']), None)
    col_driver = next((c for c in df.columns if c.lower() in ['driver', 'nama']), None)
    col_unit = next((c for c in df.columns if c.lower() in ['lambung', 'unit', 'nopol']), None)
    col_type = next((c for c in df.columns if c.lower() in ['type', 'violation']), None)
    col_location = next((c for c in df.columns if c.lower() in ['posisi', 'location']), None)
    col_shift = next((c for c in df.columns if c.lower() in ['shift']), None)
    col_age = next((c for c in df.columns if c.lower() in ['umur', 'age']), None)
    col_pengawas = next((c for c in df.columns if c.lower() in ['pengawas', 'pengawas in charge']), None)
    
    return {
        'date': col_date, 'time': col_time, 'driver': col_driver,
        'unit': col_unit, 'type': col_type, 'location': col_location,
        'shift': col_shift, 'age': col_age, 'pengawas': col_pengawas
    }

def get_order_months():
    return ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des']

def get_order_2h():
    return [f"{i:02d}:00-{i+1:02d}:59" for i in range(0, 24, 2)]

# ==================== UI COMPONENTS ====================
def kpi(title, value, footer, icon="📊", color="#2563eb"):
    st.markdown(f"""
    <div class="kpi" style="border-top:4px solid {color};">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-footer">{footer}</div>
    </div>
    """, unsafe_allow_html=True)

def insight(color, title, text, icon="💡"):
    st.markdown(f"""
    <div style="background:{color}; padding:16px 20px; border-radius:14px; margin-bottom:10px; border-left:5px solid {color};">
        <div style="font-weight:600; font-size:0.95rem; color:#0f172a;">{icon} {title}</div>
        <div style="font-size:0.85rem; color:#334155; margin-top:4px;">{text}</div>
    </div>
    """, unsafe_allow_html=True)

def rec_card(priority, icon, text):
    bg = '#fef2f2' if 'PRIORITAS' in priority else '#fffbeb'
    border = '#ef4444' if 'PRIORITAS' in priority else '#f59e0b'
    st.markdown(f"""
    <div style="background:{bg}; padding:12px 16px; border-radius:12px; border-left:5px solid {border}; margin:6px 0;">
        <span style="font-weight:600; font-size:0.85rem;">{priority}</span> 
        <span style="font-size:1rem;">{icon}</span> 
        <span style="font-size:0.9rem; color:#1e293b;">{text}</span>
    </div>
    """, unsafe_allow_html=True)

def header(title, subtitle):
    st.markdown(f"""
    <div class="dashboard-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== CHART FUNCTIONS WITH HIGHLIGHT PEAK ====================
def plot_tren(df_fatigue, order_months):
    if df_fatigue.empty:
        return None
    
    trend = df_fatigue.groupby(['Month_Num', 'Bulan']).size().reset_index(name='Total').sort_values('Month_Num')
    if trend.empty:
        return None
    
    max_val = trend['Total'].max()
    
    fig = px.line(
        trend, x='Bulan', y='Total',
        markers=True, title='Tren Fatigue Bulanan',
        color_discrete_sequence=['#2563eb']
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=10))
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5, range=[0, max_val * 1.3]),
        hovermode='x unified',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # Highlight Titik Tertinggi (Konversi eksplisit bool(is_max))
    for i, row in trend.iterrows():
        is_max = bool(row['Total'] == max_val)
        fig.add_annotation(
            x=row['Bulan'], y=row['Total'],
            text=f"🔥 {row['Total']}" if is_max else str(row['Total']),
            showarrow=is_max, arrowhead=1, arrowcolor='#dc2626',
            yshift=14 if is_max else 10,
            font=dict(size=12 if is_max else 11, weight='bold', color='#dc2626' if is_max else '#0f172a'),
            bgcolor='#fee2e2' if is_max else None,
            bordercolor='#ef4444' if is_max else None, borderwidth=1 if is_max else 0
        )
    return fig

def plot_shift_comparison(df_fatigue):
    if df_fatigue.empty:
        return None
    
    shift_df = df_fatigue.groupby(['Bulan', 'Shift']).size().reset_index(name='Total')
    if shift_df.empty:
        return None
    
    fig = px.line(
        shift_df, x='Bulan', y='Total', color='Shift',
        markers=True, title='Perbandingan Shift',
        color_discrete_map={'Shift 1': '#3b82f6', 'Shift 2': '#8b5cf6'}
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=8))
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def plot_alarm_distribution(df_fatigue):
    if df_fatigue.empty:
        return None
    
    alarm_counts = df_fatigue['Type'].value_counts().reset_index()
    alarm_counts.columns = ['Jenis', 'Total']
    
    colors = ['#ef4444', '#f59e0b']
    fig = px.bar(
        alarm_counts, x='Total', y='Jenis', orientation='h',
        title='Jenis Alarm', color='Jenis',
        color_discrete_sequence=colors, text='Total'
    )
    fig.update_traces(textposition='outside', textfont=dict(size=12, weight='bold'))
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        xaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5),
        yaxis=dict(showgrid=False),
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    return fig

def plot_jam_distribution(df_fatigue, order_2h):
    if df_fatigue.empty:
        return None
    
    rj = df_fatigue['Jam_Range'].value_counts().reindex(order_2h, fill_value=0).reset_index()
    rj.columns = ['Jam', 'Total']
    rj = rj[rj['Total'] > 0]
    
    if rj.empty:
        return None
    
    # DETEKSI DAN HIGHLIGHT BATANG TERTINGGI (PEAK)
    max_val = rj['Total'].max()
    colors = ['#991b1b' if v == max_val else '#f87171' for v in rj['Total']]
    
    fig = px.bar(
        rj, x='Jam', y='Total',
        title='Distribusi Jam Fatigue (Puncak Diberi Penanda)',
        text='Total'
    )
    
    fig.update_traces(
        marker_color=colors,
        textposition='outside', 
        textfont=dict(size=11, weight='bold')
    )
    
    # Kotak Penanda Puncak
    max_row = rj[rj['Total'] == max_val].iloc[0]
    fig.add_annotation(
        x=max_row['Jam'], 
        y=max_val + (max_val * 0.12),
        text="⚠️ PUNCAK TERTIAGGI",
        showarrow=True, arrowhead=2, arrowcolor='#991b1b', arrowsize=1.2,
        font=dict(size=11, color='white', weight='bold'),
        bgcolor='#991b1b', bordercolor='#7f1d1d', borderwidth=2, borderpad=4
    )
    
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        xaxis=dict(showgrid=False, tickangle=45),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5, range=[0, max_val * 1.35]),
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False
    )
    return fig

def plot_hotspot(df, label="Fatigue"):
    if df.empty:
        return None
    
    loc_counts = df['Lokasi'].value_counts().head(10).reset_index()
    loc_counts.columns = ['Lokasi', 'Total']
    loc_counts = loc_counts.sort_values('Total', ascending=True)
    
    max_val = loc_counts['Total'].max()
    base_color = '#ef4444' if label == "Fatigue" else '#f59e0b'
    dark_color = '#991b1b' if label == "Fatigue" else '#b45309'
    colors = [dark_color if v == max_val else base_color for v in loc_counts['Total']]
    
    fig = px.bar(
        loc_counts, x='Total', y='Lokasi', orientation='h',
        title=f'Top 10 Lokasi {label}', text='Total'
    )
    fig.update_traces(marker_color=colors, textposition='outside', textfont=dict(size=11, weight='bold'))
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        xaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5, range=[0, max_val * 1.2]),
        yaxis=dict(showgrid=False),
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False, height=400
    )
    return fig

def plot_demografi(df_fatigue, df_overspeed, labels):
    fa = df_fatigue['Kelompok_Umur'].value_counts().reindex(labels, fill_value=0).reset_index()
    fa.columns = ['Kelompok', 'Fatigue']
    
    oa = df_overspeed['Kelompok_Umur'].value_counts().reindex(labels, fill_value=0).reset_index()
    oa.columns = ['Kelompok', 'Overspeed']
    
    merged = pd.merge(fa, oa, on='Kelompok')
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=merged['Kelompok'], y=merged['Fatigue'],
        name='Fatigue', marker_color='#ef4444',
        text=merged['Fatigue'], textposition='outside'
    ))
    fig.add_trace(go.Bar(
        x=merged['Kelompok'], y=merged['Overspeed'],
        name='Overspeed', marker_color='#f59e0b',
        text=merged['Overspeed'], textposition='outside'
    ))
    fig.update_layout(
        title='Demografi Umur Driver',
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5),
        barmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def plot_top_driver(df_fatigue):
    if df_fatigue.empty:
        return None
    
    drv = df_fatigue['Driver'].value_counts().head(20).reset_index()
    drv.columns = ['Driver', 'Total']
    drv = drv.sort_values('Total', ascending=True)
    
    max_val = drv['Total'].max()
    colors = ['#991b1b' if v == max_val else '#ef4444' for v in drv['Total']]
    
    fig = px.bar(
        drv, x='Total', y='Driver', orientation='h',
        title='Top 20 Driver Fatigue', text='Total'
    )
    fig.update_traces(marker_color=colors, textposition='outside', textfont=dict(size=10, weight='bold'))
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=11),
        xaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5, range=[0, max_val * 1.2]),
        yaxis=dict(showgrid=False),
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False, height=500
    )
    return fig

def plot_heatmap(df_fatigue, order_months, top_n=15):
    if df_fatigue.empty:
        return None
    
    top_drivers = df_fatigue['Driver'].value_counts().head(top_n).index
    heatmap_data = df_fatigue[df_fatigue['Driver'].isin(top_drivers)].pivot_table(
        index='Driver', columns='Bulan', aggfunc='size', fill_value=0
    )
    
    avail_months = [m for m in order_months if m in heatmap_data.columns]
    heatmap_data = heatmap_data.reindex(columns=avail_months)
    
    heatmap_data['Total'] = heatmap_data.sum(axis=1)
    heatmap_data = heatmap_data.sort_values('Total', ascending=False).drop('Total', axis=1)
    
    if heatmap_data.empty:
        return None
    
    fig = px.imshow(
        heatmap_data,
        title='Heatmap Driver Fatigue per Bulan',
        text_auto=True, color_continuous_scale='YlOrRd', aspect='auto'
    )
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=11),
        xaxis=dict(side='bottom'), yaxis=dict(title='Driver'),
        margin=dict(l=20, r=20, t=40, b=20),
        height=max(400, len(heatmap_data) * 25)
    )
    fig.update_xaxes(title='Bulan')
    fig.update_yaxes(title='Driver')
    return fig

def plot_forecast(df_fatigue):
    if df_fatigue.empty or 'Month_Num' not in df_fatigue.columns:
        return None
    
    monthly_data = df_fatigue.groupby('Month_Num').size().reset_index(name='Total')
    monthly_data = monthly_data.sort_values('Month_Num')
    
    if len(monthly_data) < 3:
        return None
    
    x = monthly_data['Month_Num'].values
    y = monthly_data['Total'].values
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    numerator = np.sum((x - x_mean) * (y - y_mean))
    denominator = np.sum((x - x_mean) ** 2)
    slope = numerator / denominator if denominator != 0 else 0
    intercept = y_mean - slope * x_mean
    
    last_month = x[-1]
    future_months = [last_month + i for i in range(1, 4)]
    predictions = [slope * m + intercept for m in future_months]
    
    month_labels = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des']
    hist_months = [month_labels[int(m)-1] for m in x]
    future_labels = ['Bulan+1', 'Bulan+2', 'Bulan+3']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist_months, y=y,
        mode='lines+markers', name='Data Aktual',
        line=dict(color='#3b82f6', width=3), marker=dict(size=10)
    ))
    fig.add_trace(go.Scatter(
        x=future_labels, y=predictions,
        mode='lines+markers', name='Prediksi',
        line=dict(color='#ef4444', width=3, dash='dash'),
        marker=dict(size=10, color='#ef4444')
    ))
    fig.update_layout(
        title='Prediksi Tren 3 Bulan ke Depan',
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def plot_fatigue_vs_overspeed(df_fatigue, df_overspeed):
    if df_fatigue.empty or df_overspeed.empty:
        return None
    
    fatigue_counts = df_fatigue['Driver'].value_counts()
    overspeed_counts = df_overspeed['Driver'].value_counts()
    
    all_drivers = set(fatigue_counts.index) | set(overspeed_counts.index)
    compare_data = []
    for driver in all_drivers:
        f = fatigue_counts.get(driver, 0)
        o = overspeed_counts.get(driver, 0)
        total = f + o
        if total > 0:
            compare_data.append({'Driver': driver, 'Fatigue': f, 'Overspeed': o, 'Total': total})
    
    compare_df = pd.DataFrame(compare_data).sort_values('Total', ascending=False).head(15)
    
    if compare_df.empty:
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=compare_df['Driver'], y=compare_df['Fatigue'],
        name='Fatigue', marker_color='#ef4444'
    ))
    fig.add_trace(go.Bar(
        x=compare_df['Driver'], y=compare_df['Overspeed'],
        name='Overspeed', marker_color='#f59e0b'
    ))
    fig.update_layout(
        title='Fatigue vs Overspeed per Driver',
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=11),
        xaxis=dict(showgrid=False, tickangle=45),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5),
        barmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        margin=dict(l=20, r=20, t=40, b=20),
        height=450
    )
    return fig

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:10px 0 20px 0;">
        <div style="font-size:40px;">🚛</div>
        <div style="font-weight:700; font-size:1.2rem; color:white;">FMS Dashboard</div>
        <div style="font-size:0.7rem; color:#94a3b8;">v3.0 · Enterprise</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📁 Data Source")
    uploaded_file = st.file_uploader("Upload File Log FMS", type=['xlsx', 'csv'])
    st.markdown("---")
    st.caption("© 2026 PT. Bumiputera Maha Terpercaya")

# ==================== HEADER ====================
header(
    "🚛 Fleet Management System",
    "PT. Bumiputera Maha Terpercaya<br>Monitoring Fatigue • Overspeed • Safety Analytics"
)

# ==================== MAIN ====================
if uploaded_file is None:
    st.info("👆 Upload file Excel/CSV di sidebar untuk memulai")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background:white; padding:30px; border-radius:18px; text-align:center; border:1px solid #edf2f7;">
            <div style="font-size:40px;">📊</div>
            <div style="font-weight:600; color:#0f172a;">Analisis Lengkap</div>
            <div style="font-size:0.85rem; color:#64748b;">Tren fatigue, overspeed, performa</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:white; padding:30px; border-radius:18px; text-align:center; border:1px solid #edf2f7;">
            <div style="font-size:40px;">🗺️</div>
            <div style="font-weight:600; color:#0f172a;">Spatial & Temporal</div>
            <div style="font-size:0.85rem; color:#64748b;">Hotspot & pola waktu</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:white; padding:30px; border-radius:18px; text-align:center; border:1px solid #edf2f7;">
            <div style="font-size:40px;">👥</div>
            <div style="font-weight:600; color:#0f172a;">Driver & Fleet</div>
            <div style="font-size:0.85rem; color:#64748b;">Demografi & performa</div>
        </div>
        """, unsafe_allow_html=True)
else:
    with st.spinner("🔄 Memproses data..."):
        try:
            # ========== BACA DATA ==========
            if uploaded_file.name.endswith('.xlsx'):
                xls = pd.ExcelFile(uploaded_file)
                sheet = 'Input' if 'Input' in xls.sheet_names else xls.sheet_names[0]
                df_raw = pd.read_excel(uploaded_file, sheet_name=sheet)
            else:
                df_raw = pd.read_csv(uploaded_file)

            df = df_raw.dropna(how='all').copy()
            df.columns = [str(c).strip() for c in df.columns]

            # ========== DETEKSI & CLEANING DATA ==========
            cols = detect_columns(df)
            
            if not all([cols['date'], cols['type'], cols['driver']]):
                st.error("❌ Kolom minimum wajib ada: Tanggal, Type, Driver")
                st.stop()
            
            df = df.dropna(subset=[cols['date'], cols['type'], cols['driver']]).copy()
            df[cols['date']] = pd.to_datetime(df[cols['date']], errors='coerce')
            df = df.dropna(subset=[cols['date']])
            
            # Kolom Turunan
            df['Month_Num'] = df[cols['date']].dt.month
            bulan_map = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'Mei',6:'Jun',
                         7:'Jul',8:'Ags',9:'Sep',10:'Okt',11:'Nov',12:'Des'}
            df['Bulan'] = df['Month_Num'].map(bulan_map)
            
            df['Driver'] = df[cols['driver']].astype(str).str.replace('_', ' ').str.strip().str.title()
            df['Unit'] = df[cols['unit']].astype(str).str.strip().str.upper() if cols['unit'] else "N/A"
            df['Lokasi'] = df[cols['location']].astype(str).str.strip().str.upper() if cols['location'] else "N/A"
            df['Type'] = df[cols['type']].astype(str).str.strip().str.title()
            
            if cols['pengawas']:
                df['Pengawas'] = df[cols['pengawas']].astype(str).str.strip().str.title()
            else:
                df['Pengawas'] = 'Tidak Diketahui'
            
            if cols['age']:
                df['Umur'] = pd.to_numeric(df[cols['age']], errors='coerce')
                bins = [18,25,35,45,55,100]
                labels = ['18-25','26-35','36-45','46-55','>55']
                df['Kelompok_Umur'] = pd.cut(df['Umur'], bins=bins, labels=labels, right=True)
            else:
                df['Kelompok_Umur'] = 'N/A'
                labels = ['18-25','26-35','36-45','46-55','>55']
            
            if cols['shift']:
                df['Shift'] = df[cols['shift']].apply(
                    lambda x: f"Shift {int(x)}" if str(x).replace('.','').isdigit() else str(x)
                )
            else:
                df['Shift'] = "Shift 1"
            
            df['Jam_Range'] = df[cols['time']].apply(cat_time) if cols['time'] else 'Unknown'
            
            # Filter Data
            df = df[~df['Lokasi'].isin(['OUT OF HAULING'])]
            df = df[~df['Driver'].isin(['Unknown'])]
            df = df[~df['Driver'].str.contains('Ba Minergo', case=False, na=False)]
            
            df_fatigue = df[df['Type'].isin(['Mata Tertutup', 'Mengantuk'])].copy()
            df_overspeed = df[df['Type'] == 'Overspeed'].copy()
            
            order_months = get_order_months()
            order_2h = get_order_2h()
            
            # ========== HITUNG METRIK ==========
            total_f = len(df_fatigue)
            total_o = len(df_overspeed)
            total_alarm = total_f + total_o
            
            jam_counts = df_fatigue['Jam_Range'].value_counts()
            top_jam = jam_counts.index[0] if not jam_counts.empty else "N/A"
            top_jam_val = jam_counts.iloc[0] if not jam_counts.empty else 0
            
            loc_counts = df_fatigue['Lokasi'].value_counts()
            top_loc = loc_counts.index[0] if not loc_counts.empty else "N/A"
            top_loc_val = loc_counts.iloc[0] if not loc_counts.empty else 0
            
            safety_score = max(0, min(100, 100 - (total_f * 0.3)))
            
            # ========== KPI CARDS ==========
            st.markdown("### 📊 Ringkasan")
            c1, c2, c3, c4, c5 = st.columns(5)
            
            with c1:
                kpi("Total Alarm", fmt_num(total_alarm), "Semua jenis alarm", "🚨", "#ef4444")
            with c2:
                kpi("Fatigue", fmt_num(total_f), "Kasus fatigue", "😴", "#f59e0b")
            with c3:
                kpi("Overspeed", fmt_num(total_o), "Kasus overspeed", "🚗", "#3b82f6")
            with c4:
                kpi("Hotspot", top_loc, f"{top_loc_val} kasus", "📍", "#8b5cf6")
            with c5:
                kpi("Safety Score", f"{safety_score:.0f}/100", "Semakin tinggi semakin baik", "🛡️", "#22c55e")
            
            st.markdown("---")
            
            # ========== RINGKASAN EKSEKUTIF ==========
            st.markdown("### 📋 Ringkasan Eksekutif")
            col1, col2 = st.columns(2)
            
            with col1:
                if not jam_counts.empty:
                    top_jam = jam_counts.index[0]
                    top_val = jam_counts.iloc[0]
                    pct = top_val / jam_counts.sum() * 100
                    if any(j in top_jam for j in ['00:00','01:00','02:00','03:00','04:00','05:00']):
                        insight("#fee2e2", "Jam Kritis", f"Puncak fatigue di {top_jam} ({top_val} kasus, {pct:.1f}%) — waspada!")
                    else:
                        insight("#dbeafe", "Jam Rawan", f"{top_jam} ({top_val} kasus, {pct:.1f}%)")
                
                shift_counts = df_fatigue['Shift'].value_counts()
                if 'Shift 2' in shift_counts.index and 'Shift 1' in shift_counts.index:
                    s2, s1 = shift_counts['Shift 2'], shift_counts['Shift 1']
                    if s1 > 0:
                        ratio = s2 / s1
                        if ratio > 2:
                            insight("#fee2e2", "Shift Malam", f"{ratio:.1f}x lebih tinggi ({s2} vs {s1}) — evaluasi!")
                        elif ratio > 1.2:
                            insight("#fef3c7", "Shift Malam", f"{ratio:.1f}x lebih tinggi ({s2} vs {s1})")
                        else:
                            insight("#dcfce7", "Shift Seimbang", f"{s2} vs {s1}")
            
            with col2:
                driver_counts = df_fatigue['Driver'].value_counts()
                if not driver_counts.empty:
                    top_driver = driver_counts.index[0]
                    top_val = driver_counts.iloc[0]
                    insight("#fef3c7", "Driver Berisiko", f"{top_driver} ({top_val} kasus) — perlu monitoring")
                
                unit_counts = df['Unit'].value_counts()
                if not unit_counts.empty:
                    top_unit = unit_counts.index[0]
                    top_val = unit_counts.iloc[0]
                    if top_val > 5:
                        insight("#fee2e2", "Unit Bermasalah", f"{top_unit} ({top_val} temuan) — inspeksi!")
                    else:
                        insight("#dbeafe", "Unit Bermasalah", f"{top_unit} ({top_val} temuan)")
            
            st.markdown("---")
            
            # ========== TABS UTAMA ==========
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Overview",
                "🗺️ Lokasi & Waktu",
                "👥 Driver & Unit",
                "📋 Data Logs",
                "🧠 Analisis Lanjutan"
            ])
            
            # ========== TAB 1: OVERVIEW ==========
            with tab1:
                fig = plot_tren(df_fatigue, order_months)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Tidak ada data fatigue")
                
                st.markdown("---")
                
                c1, c2 = st.columns(2)
                with c1:
                    fig = plot_shift_comparison(df_fatigue)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Tidak ada data shift")
                
                with c2:
                    fig = plot_alarm_distribution(df_fatigue)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Tidak ada data alarm")
            
            # ========== TAB 2: LOKASI & WAKTU ==========
            with tab2:
                fig = plot_jam_distribution(df_fatigue, order_2h)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Tidak ada data jam")
                
                st.markdown("---")
                
                if not df_overspeed.empty:
                    rj_o = df_overspeed['Jam_Range'].value_counts().reindex(order_2h, fill_value=0)
                    rj_o = rj_o[rj_o > 0].reset_index()
                    rj_o.columns = ['Jam', 'Total']
                    if not rj_o.empty:
                        max_o_val = rj_o['Total'].max()
                        colors_o = ['#b45309' if v == max_o_val else '#f59e0b' for v in rj_o['Total']]
                        
                        fig = px.bar(
                            rj_o, x='Jam', y='Total',
                            title='Distribusi Jam Overspeed', text='Total'
                        )
                        fig.update_traces(marker_color=colors_o, textposition='outside', textfont=dict(size=11, weight='bold'))
                        fig.update_layout(
                            plot_bgcolor='white', paper_bgcolor='white',
                            font=dict(family='Inter', size=12),
                            xaxis=dict(showgrid=False, tickangle=45),
                            yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5, range=[0, max_o_val * 1.25]),
                            margin=dict(l=20, r=20, t=40, b=20),
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        st.caption("💡 Overspeed umumnya terjadi pada jam operasional puncak")
                
                st.markdown("---")
                
                c1, c2 = st.columns(2)
                with c1:
                    fig = plot_hotspot(df_fatigue, "Fatigue")
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Tidak ada data lokasi fatigue")
                
                with c2:
                    fig = plot_hotspot(df_overspeed, "Overspeed")
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Tidak ada data lokasi overspeed")
            
            # ========== TAB 3: DRIVER & UNIT ==========
            with tab3:
                fig = plot_demografi(df_fatigue, df_overspeed, labels)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                c1, c2 = st.columns(2)
                with c1:
                    fig = plot_top_driver(df_fatigue)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Tidak ada data driver")
                
                with c2:
                    if not df.empty:
                        unit = df['Unit'].value_counts().head(10).reset_index()
                        unit.columns = ['Unit', 'Total']
                        unit = unit.sort_values('Total', ascending=True)
                        
                        max_u = unit['Total'].max()
                        colors_u = ['#1d4ed8' if v == max_u else '#3b82f6' for v in unit['Total']]
                        
                        fig = px.bar(
                            unit, x='Total', y='Unit', orientation='h',
                            title='Top 10 Unit Bermasalah', text='Total'
                        )
                        fig.update_traces(marker_color=colors_u, textposition='outside', textfont=dict(size=11, weight='bold'))
                        fig.update_layout(
                            plot_bgcolor='white', paper_bgcolor='white',
                            font=dict(family='Inter', size=11),
                            xaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5, range=[0, max_u * 1.2]),
                            yaxis=dict(showgrid=False),
                            margin=dict(l=20, r=20, t=40, b=20),
                            showlegend=False, height=450
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Tidak ada data unit")
                
                st.markdown("---")
                
                st.markdown("#### 🔥 Heatmap Driver per Bulan")
                col_h1, col_h2, col_h3 = st.columns(3)
                with col_h1:
                    top_n = st.slider("Jumlah Driver", 5, 30, 15, key="hm_top")
                with col_h2:
                    shift_filter = st.selectbox(
                        "Shift", ["Semua"] + sorted(df_fatigue['Shift'].unique().tolist()),
                        key="hm_shift"
                    )
                with col_h3:
                    type_filter = st.selectbox(
                        "Jenis Alarm", ["Semua"] + sorted(df_fatigue['Type'].unique().tolist()),
                        key="hm_type"
                    )
                
                hm_df = df_fatigue.copy()
                if shift_filter != "Semua":
                    hm_df = hm_df[hm_df['Shift'] == shift_filter]
                if type_filter != "Semua":
                    hm_df = hm_df[hm_df['Type'] == type_filter]
                
                fig = plot_heatmap(hm_df, order_months, top_n)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    top_driver = hm_df['Driver'].value_counts().index[0] if not hm_df.empty else None
                    if top_driver:
                        st.caption(f"💡 Insight: Driver **{top_driver}** memiliki kasus terbanyak")
                else:
                    st.warning("Data tidak cukup untuk heatmap")
            
            # ========== TAB 4: DATA LOGS ==========
            with tab4:
                st.markdown("### 📋 Data Logs")
                
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1:
                    search = st.text_input("🔍 Cari", placeholder="Driver / Unit / Lokasi")
                with c2:
                    f_month = st.selectbox("Bulan", ["Semua"] + [m for m in order_months if m in df['Bulan'].unique()])
                with c3:
                    f_type = st.selectbox("Jenis", ["Semua"] + list(df['Type'].unique()))
                
                filtered = df.copy()
                if search.strip():
                    s = search.strip().lower()
                    filtered = filtered[
                        filtered['Driver'].str.lower().str.contains(s, na=False) |
                        filtered['Unit'].str.lower().str.contains(s, na=False) |
                        filtered['Lokasi'].str.lower().str.contains(s, na=False)
                    ]
                if f_month != "Semua":
                    filtered = filtered[filtered['Bulan'] == f_month]
                if f_type != "Semua":
                    filtered = filtered[filtered['Type'] == f_type]
                
                if filtered.empty:
                    st.warning("Tidak ada data yang cocok")
                else:
                    st.markdown(f"**{fmt_num(len(filtered))} baris**")
                    cols_show = [cols['date'], cols['time'], 'Bulan', 'Shift', 'Driver', 'Umur', 'Unit', 'Type', 'Lokasi']
                    cols_show = [c for c in cols_show if c in filtered.columns]
                    show = filtered[cols_show].copy()
                    show[cols['date']] = show[cols['date']].dt.strftime('%d-%m-%Y')
                    show = show.rename(columns={
                        cols['date']: 'Tanggal', cols['time']: 'Jam', 'Bulan': 'Bulan',
                        'Shift': 'Shift', 'Driver': 'Driver', 'Umur': 'Umur',
                        'Unit': 'Unit', 'Type': 'Jenis', 'Lokasi': 'Lokasi'
                    })
                    st.dataframe(show, use_container_width=True, hide_index=True, height=400)
                    
                    csv = show.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"data_fms_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime='text/csv'
                    )
            
            # ========== TAB 5: ANALISIS LANJUTAN ==========
            with tab5:
                st.markdown("## 🧠 Analisis Lanjutan untuk Pencegahan")
                st.caption("Analisis ini membantu mengidentifikasi pola dan risiko untuk tindakan preventif")
                st.markdown("---")
                
                st.markdown("### 📈 Prediksi Tren")
                fig = plot_forecast(df_fatigue)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    if not df_fatigue.empty:
                        monthly = df_fatigue.groupby('Month_Num').size()
                        if len(monthly) >= 3:
                            current = int(monthly.iloc[-1])
                            x = monthly.index.values
                            y = monthly.values
                            x_mean = np.mean(x)
                            y_mean = np.mean(y)
                            slope = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
                            intercept = y_mean - slope * x_mean
                            next_pred = max(0, int(slope * (x[-1] + 1) + intercept))
                            pct = ((next_pred - current) / current * 100) if current > 0 else 0
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📊 Bulan Ini", f"{current} kasus")
                            with col2:
                                st.metric("📈 Prediksi Depan", f"{next_pred} kasus", f"{pct:+.1f}%")
                            with col3:
                                if pct > 10:
                                    st.warning("⚠️ Prediksi peningkatan >10%")
                                elif pct < -10:
                                    st.success("✅ Prediksi penurunan >10%")
                                else:
                                    st.info("📊 Prediksi stabil")
                else:
                    st.warning("Data kurang dari 3 bulan untuk prediksi")
                
                st.markdown("---")
                
                st.markdown("### 🔄 Fatigue vs Overspeed")
                fig = plot_fatigue_vs_overspeed(df_fatigue, df_overspeed)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Data tidak cukup")
                
                st.markdown("---")
                
                st.markdown("### ✅ Rekomendasi Otomatis")
                
                recs = []
                if not df_fatigue.empty:
                    top_d = df_fatigue['Driver'].value_counts()
                    if not top_d.empty and top_d.iloc[0] > 5:
                        recs.append(("🔴 PRIORITAS", "👤", f"Coaching Personal: Driver {top_d.index[0]} memiliki {top_d.iloc[0]} kasus"))
                    
                    shift_counts = df_fatigue['Shift'].value_counts()
                    if 'Shift 2' in shift_counts.index and 'Shift 1' in shift_counts.index:
                        ratio = shift_counts['Shift 2'] / shift_counts['Shift 1'] if shift_counts['Shift 1'] > 0 else 0
                        if ratio > 2:
                            recs.append(("🔴 PRIORITAS", "🌙", f"Rotasi Shift: {ratio:.1f}x lebih tinggi di Shift Malam"))
                    
                    jam_counts = df_fatigue['Jam_Range'].value_counts()
                    if not jam_counts.empty:
                        top_j = jam_counts.index[0]
                        if any(j in top_j for j in ['02:00', '03:00', '04:00']):
                            recs.append(("🟡 PENTING", "☕", f"Istirahat Terjadwal: Puncak fatigue di jam {top_j}"))
                    
                    unit_counts = df['Unit'].value_counts()
                    if not unit_counts.empty and unit_counts.iloc[0] > 5:
                        recs.append(("🟡 PENTING", "🚗", f"Inspeksi Unit: {unit_counts.index[0]} ({unit_counts.iloc[0]} temuan)"))
                
                if recs:
                    for rec in recs:
                        rec_card(rec[0], rec[1], rec[2])
                else:
                    st.success("✅ Tidak ada rekomendasi prioritas saat ini")
            
            st.sidebar.success(f"✅ {fmt_num(len(df))} data valid")

        except Exception as e:
            st.error(f"❌ Error saat memproses data: {str(e)}")
            with st.expander("🔍 Detail Traceback"):
                import traceback
                st.code(traceback.format_exc())

# ==================== FOOTER ====================
st.markdown("---")
st.caption("© 2026 PT. Bumiputera Maha Terpercaya | Dashboard FMS v3.0")
