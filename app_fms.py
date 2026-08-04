import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
from google import genai

# ==================== KONFIGURASI HALAMAN ====================
st.set_page_config(
    page_title="DSMS - PT. Bumiputera Maha Terpercaya",
    page_icon="🛡️",
    layout="wide"
)

# ==================== CSS CUSTOM STYLING (SOFT THEME & PRINT FIX) ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* LATAR BELAKANG UTAMA (SOFT & NYAMAN DILIHAT) */
.stApp {
    background-color: #f8fafc !important;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1600px;
}

/* SIDEBAR ADAPTIF TERANG/GELAP */
[data-testid="stSidebar"] {
    background-color: var(--background-color) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stFileUploader label {
    color: var(--text-color) !important;
}

/* KPI CARDS (SOFT & ELEGAN) */
.kpi {
    background-color: #ffffff;
    padding: 18px 16px;
    border-radius: 16px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
    transition: all 0.3s ease;
    border: 1px solid #e2e8f0;
    position: relative;
    box-sizing: border-box;
}
.kpi:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.06);
}
.kpi-icon { font-size: 26px; margin-bottom: 4px; }
.kpi-title { font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: .6px; font-weight: 600; }
.kpi-value { font-size: 28px; font-weight: 700; color: #0f172a; margin-top: 4px; }
.kpi-footer { margin-top: 6px; color: #3b82f6; font-size: 12px; font-weight: 500; }

/* BUTTON STYLING (SOFT BLUE) */
.stButton > button {
    background: #3b82f6;
    color: white !important;
    border-radius: 10px;
    border: none;
    padding: .55rem 1rem;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: #2563eb;
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3);
}

/* KONTAINER GRAFIK ISOLASI */
.chart-box {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
    position: relative !important;
    display: block !important;
    width: 100% !important;
    clear: both !important;
    margin-bottom: 25px !important;
}

/* ==================== OPTIMISASI PRINT PDF ==================== */
@media print {
    section[data-testid="stSidebar"],
    header[data-testid="stHeader"],
    .stButton,
    footer,
    div[data-testid="stTabs"] [role="tablist"],
    .no-print {
        display: none !important;
    }
    
    div[data-testid="stTabs"] [role="tabpanel"] {
        display: block !important;
        opacity: 1 !important;
        visibility: visible !important;
        position: relative !important;
        float: none !important;
        clear: both !important;
        page-break-after: always !important;
        margin-bottom: 30px !important;
    }

    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: space-between !important;
        align-items: stretch !important;
        gap: 10px !important;
        width: 100% !important;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 1 1 25% !important;
        width: 25% !important;
        min-width: 0 !important;
        max-width: 25% !important;
        display: block !important;
        margin-bottom: 0 !important;
    }

    @page {
        size: A4 portrait;
        margin: 10mm;
    }

    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
        background-color: #ffffff !important;
    }

    .chart-box, .js-plotly-plot, [data-testid="stPlotlyChart"] {
        position: relative !important;
        display: block !important;
        clear: both !important;
        float: none !important;
        width: 100% !important;
        height: auto !important;
        max-height: 380px !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
        margin-bottom: 25px !important;
        background-color: #ffffff !important;
        border: none !important;
        box-shadow: none !important;
    }

    .kpi, div[data-testid="stMarkdownContainer"] {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ==================== MEMORI SESSION STATE AI ====================
if 'res_eksekutif' not in st.session_state:
    st.session_state['res_eksekutif'] = None
if 'res_jam' not in st.session_state:
    st.session_state['res_jam'] = None
if 'res_driver' not in st.session_state:
    st.session_state['res_driver'] = None

# ==================== HELPER FUNCTIONS ====================
def fmt_num(n):
    return f"{n:,}".replace(',', '.')

def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except:
        return ""

def cat_time(t):
    if pd.isna(t): return 'Unknown'
    try:
        if isinstance(t, (datetime, pd.Timestamp)): h = t.hour
        elif hasattr(t, 'hour'): h = t.hour
        else: h = int(str(t).strip().split(':')[0])
        return f"{h:02d}:00-{h+1:02d}:59"
    except: return 'Unknown'

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

# ==================== HEADER UTAMA ====================
def header_with_logo(title, subtitle, logo_path="image.png"):
    img_b64 = get_image_base64(logo_path)
    logo_html = f'<img src="data:image/png;base64,{img_b64}" style="height: 55px; object-fit: contain;">' if img_b64 else '<span style="font-size:30px;">🛡️</span>'
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0f172a, #1d4ed8);
        padding: 24px 30px;
        border-radius: 20px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 10px 25px rgba(0,0,0,0.12);
        margin-bottom: 25px;
    ">
        <div>
            <h1 style="margin: 0; font-size: 30px; font-weight: 700; color: white;">{title}</h1>
            <p style="margin: 6px 0 0 0; opacity: 0.9; font-size: 14px; line-height: 1.5; color: white;">{subtitle}</p>
        </div>
        <div style="background: white; padding: 8px 16px; border-radius: 14px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            {logo_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== LOAD & PROCESS DATA ====================
@st.cache_data
def load_and_process_data(file):
    if file.name.endswith('.xlsx'):
        xls = pd.ExcelFile(file)
        sheet = 'Input' if 'Input' in xls.sheet_names else xls.sheet_names[0]
        df_raw = pd.read_excel(file, sheet_name=sheet)
    else:
        df_raw = pd.read_csv(file)

    df = df_raw.dropna(how='all').copy()
    df.columns = [str(c).strip() for c in df.columns]

    cols = detect_columns(df)
    labels = ['<25', '26-30', '31-35', '36-40', '41-45', '46-50', '51-55', '>55']
    
    if not all([cols['date'], cols['type'], cols['driver']]):
        return None, cols, labels

    df = df.dropna(subset=[cols['date'], cols['type'], cols['driver']]).copy()
    df[cols['date']] = pd.to_datetime(df[cols['date']], errors='coerce')
    df = df.dropna(subset=[cols['date']])
    
    df['Month_Num'] = df[cols['date']].dt.month
    bulan_map = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'Mei',6:'Jun',
                 7:'Jul',8:'Ags',9:'Sep',10:'Okt',11:'Nov',12:'Des'}
    df['Bulan'] = df['Month_Num'].map(bulan_map)
    df['Week'] = df[cols['date']].dt.isocalendar().week
    
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
        bins = [0, 25, 30, 35, 40, 45, 50, 55, 100]
        df['Kelompok_Umur'] = pd.cut(df['Umur'], bins=bins, labels=labels, right=True)
    else:
        df['Kelompok_Umur'] = 'N/A'
    
    if cols['shift']:
        df['Shift'] = df[cols['shift']].apply(
            lambda x: f"Shift {int(x)}" if str(x).replace('.','').isdigit() else str(x)
        )
    else:
        df['Shift'] = "Shift 1"
    
    df['Jam_Range'] = df[cols['time']].apply(cat_time) if cols['time'] else 'Unknown'
    
    df = df[~df['Lokasi'].isin(['OUT OF HAULING'])]
    df = df[~df['Driver'].isin(['Unknown'])]
    df = df[~df['Driver'].str.contains('Ba Minergo', case=False, na=False)]
    
    return df, cols, labels

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
    <div style="background:{color}; padding:16px 20px; border-radius:14px; margin-bottom:10px; border-left:5px solid {color}; color:#0f172a;">
        <div style="font-weight:600; font-size:0.95rem; color:#0f172a;">{icon} {title}</div>
        <div style="font-size:0.85rem; color:#334155; margin-top:4px;">{text}</div>
    </div>
    """, unsafe_allow_html=True)

# ==================== RENDERER GRAFIK AMAN PRINT ====================
def render_chart(fig):
    if fig:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== CHART FUNCTIONS ====================
def plot_tren_generic(df_target, title="Tren Bulanan", color="#2563eb"):
    if df_target.empty or 'Month_Num' not in df_target.columns: return None
    trend = df_target.groupby(['Month_Num', 'Bulan']).size().reset_index(name='Total').sort_values('Month_Num')
    if trend.empty: return None
    max_val = trend['Total'].max()
    fig = px.line(trend, x='Bulan', y='Total', markers=True, title=title, color_discrete_sequence=[color])
    fig.update_traces(line=dict(width=3), marker=dict(size=10))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12), xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(150,150,150,0.2)', range=[0, max_val * 1.35]),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    for i, row in trend.iterrows():
        is_max = bool(row['Total'] == max_val)
        fig.add_annotation(
            x=row['Bulan'], y=row['Total'], text=f"🔥 {row['Total']}" if is_max else str(row['Total']),
            showarrow=is_max, arrowhead=1, arrowcolor=color, yshift=14 if is_max else 10,
            font=dict(size=12 if is_max else 11, weight='bold')
        )
    return fig

def plot_weekly_trend_with_trendline(df_fatigue):
    if df_fatigue.empty or 'Week' not in df_fatigue.columns: return None, "Data Kosong"
    weekly = df_fatigue.groupby('Week').size().reset_index(name='Total').sort_values('Week')
    if len(weekly) < 2: return None, "Data Tidak Cukup"
    x = weekly['Week'].values.astype(float)
    y = weekly['Total'].values.astype(float)
    slope, intercept = np.polyfit(x, y, 1)
    trendline_y = slope * x + intercept
    trend_status = "⚠️ CENDERUNG NAIK" if slope > 0.1 else ("✅ CENDERUNG TURUN" if slope < -0.1 else "➡️ STABIL")
    trend_color = "#ef4444" if slope > 0.1 else ("#22c55e" if slope < -0.1 else "#3b82f6")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weekly['Week'], y=weekly['Total'], mode='lines+markers', name='Fatigue', line=dict(color='#ef4444', width=2.5)))
    fig.add_trace(go.Scatter(x=weekly['Week'], y=trendline_y, mode='lines', name=f'Garis Tren ({trend_status})', line=dict(color=trend_color, width=3, dash='dash')))
    
    fig.update_layout(
        title='📊 Tren Fatigue Mingguan (Week 1–52) + Garis Tren',
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12),
        xaxis=dict(title="Minggu Ke- (Week)", showgrid=True, gridcolor='rgba(150,150,150,0.2)', dtick=1, rangeslider=dict(visible=False)),
        yaxis=dict(title="Jumlah Temuan", showgrid=True, gridcolor='rgba(150,150,150,0.2)'),
        margin=dict(l=20, r=20, t=50, b=40)
    )
    return fig, trend_status

def plot_shift_comparison(df_fatigue):
    if df_fatigue.empty: return None
    shift_df = df_fatigue.groupby(['Bulan', 'Shift']).size().reset_index(name='Total')
    if shift_df.empty: return None
    fig = px.line(shift_df, x='Bulan', y='Total', color='Shift', markers=True, title='Perbandingan Shift', color_discrete_map={'Shift 1': '#3b82f6', 'Shift 2': '#8b5cf6'})
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_alarm_distribution(df_fatigue):
    if df_fatigue.empty: return None
    alarm_counts = df_fatigue['Type'].value_counts().reset_index()
    alarm_counts.columns = ['Jenis', 'Total']
    fig = px.bar(alarm_counts, x='Total', y='Jenis', orientation='h', title='Jenis Alarm', color='Jenis', color_discrete_sequence=['#ef4444', '#f59e0b'], text='Total')
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
    return fig

def plot_jam_distribution(df_fatigue, order_2h):
    if df_fatigue.empty: return None
    rj = df_fatigue['Jam_Range'].value_counts().reindex(order_2h, fill_value=0).reset_index()
    rj.columns = ['Jam', 'Total']
    rj = rj[rj['Total'] > 0]
    if rj.empty: return None
    max_val = rj['Total'].max()
    colors = ['#991b1b' if v == max_val else '#f87171' for v in rj['Total']]
    fig = px.bar(rj, x='Jam', y='Total', title='Distribusi Jam Fatigue (Puncak Diberi Penanda)', text='Total')
    fig.update_traces(marker_color=colors, textposition='outside')
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=50, b=20), showlegend=False)
    return fig

def plot_hotspot(df, label="Fatigue"):
    if df.empty: return None
    loc_counts = df['Lokasi'].value_counts().head(10).reset_index()
    loc_counts.columns = ['Lokasi', 'Total']
    loc_counts = loc_counts.sort_values('Total', ascending=True)
    base_color = '#ef4444' if label == "Fatigue" else '#f59e0b'
    fig = px.bar(loc_counts, x='Total', y='Lokasi', orientation='h', title=f'Top 10 Lokasi {label}', text='Total', color_discrete_sequence=[base_color])
    fig.update_traces(textposition='outside')
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20), showlegend=False, height=380)
    return fig

def plot_demografi(df_fatigue, df_overspeed, labels):
    fa = df_fatigue['Kelompok_Umur'].value_counts().reindex(labels, fill_value=0).reset_index()
    fa.columns = ['Kelompok', 'Fatigue']
    oa = df_overspeed['Kelompok_Umur'].value_counts().reindex(labels, fill_value=0).reset_index()
    oa.columns = ['Kelompok', 'Overspeed']
    merged = pd.merge(fa, oa, on='Kelompok')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=merged['Kelompok'], y=merged['Fatigue'], name='Fatigue', marker_color='#ef4444', text=merged['Fatigue'], textposition='outside'))
    fig.add_trace(go.Bar(x=merged['Kelompok'], y=merged['Overspeed'], name='Overspeed', marker_color='#f59e0b', text=merged['Overspeed'], textposition='outside'))
    fig.update_layout(title='Demografi Umur Driver (5 Tahun)', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', barmode='group', margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_top_driver(df_fatigue):
    if df_fatigue.empty: return None
    drv = df_fatigue['Driver'].value_counts().head(15).reset_index()
    drv.columns = ['Driver', 'Total']
    drv = drv.sort_values('Total', ascending=True)
    fig = px.bar(drv, x='Total', y='Driver', orientation='h', title='Top 15 Driver Fatigue', text='Total', color_discrete_sequence=['#ef4444'])
    fig.update_traces(textposition='outside')
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20), showlegend=False, height=420)
    return fig

def plot_heatmap(df_fatigue, order_months, top_n=15):
    if df_fatigue.empty: return None
    top_drivers = df_fatigue['Driver'].value_counts().head(top_n).index
    heatmap_data = df_fatigue[df_fatigue['Driver'].isin(top_drivers)].pivot_table(index='Driver', columns='Bulan', aggfunc='size', fill_value=0)
    avail_months = [m for m in order_months if m in heatmap_data.columns]
    heatmap_data = heatmap_data.reindex(columns=avail_months)
    if heatmap_data.empty: return None
    fig = px.imshow(heatmap_data, title='Heatmap Driver Fatigue per Bulan', text_auto=True, color_continuous_scale='YlOrRd', aspect='auto')
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20), height=420)
    return fig

def plot_forecast(df_fatigue):
    if df_fatigue.empty or 'Month_Num' not in df_fatigue.columns: return None
    monthly_data = df_fatigue.groupby('Month_Num').size().reset_index(name='Total').sort_values('Month_Num')
    if len(monthly_data) < 3: return None
    x, y = monthly_data['Month_Num'].values, monthly_data['Total'].values
    slope, intercept = np.polyfit(x, y, 1)
    future_months = [x[-1] + i for i in range(1, 4)]
    predictions = [slope * m + intercept for m in future_months]
    month_labels = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des']
    hist_months = [month_labels[int(m)-1] for m in x]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist_months, y=y, mode='lines+markers', name='Data Aktual', line=dict(color='#3b82f6', width=3)))
    fig.add_trace(go.Scatter(x=['Bulan+1', 'Bulan+2', 'Bulan+3'], y=predictions, mode='lines+markers', name='Prediksi', line=dict(color='#ef4444', width=3, dash='dash')))
    fig.update_layout(title='Prediksi Tren 3 Bulan ke Depan', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_fatigue_vs_overspeed(df_fatigue, df_overspeed):
    if df_fatigue.empty or df_overspeed.empty: return None
    fatigue_counts = df_fatigue['Driver'].value_counts()
    overspeed_counts = df_overspeed['Driver'].value_counts()
    all_drivers = set(fatigue_counts.index) | set(overspeed_counts.index)
    compare_data = [{'Driver': d, 'Fatigue': fatigue_counts.get(d, 0), 'Overspeed': overspeed_counts.get(d, 0), 'Total': fatigue_counts.get(d, 0)+overspeed_counts.get(d, 0)} for d in all_drivers]
    compare_df = pd.DataFrame(compare_data).sort_values('Total', ascending=False).head(15)
    if compare_df.empty: return None
    fig = go.Figure()
    fig.add_trace(go.Bar(x=compare_df['Driver'], y=compare_df['Fatigue'], name='Fatigue', marker_color='#ef4444'))
    fig.add_trace(go.Bar(x=compare_df['Driver'], y=compare_df['Overspeed'], name='Overspeed', marker_color='#f59e0b'))
    fig.update_layout(title='Fatigue vs Overspeed per Driver', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', barmode='group', margin=dict(l=20, r=20, t=40, b=20), height=420)
    return fig

# ==================== GEMINI AI INTEGRATION (MENGGUNAKAN GEMINI-1.5-FLASH UNTUK MENGHINDARI ERROR 429) ====================
def generate_gemini_analysis(api_key, prompt_text):
    try:
        client = genai.Client(api_key=api_key)
        # Menggunakan model standar 'gemini-flash' atau 'gemini-pro' yang didukung penuh
        response = client.models.generate_content(model='gemini-flash', contents=prompt_text)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"
# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 👨‍✈️ DSMS Dashboard v3.0")
    uploaded_file = st.file_uploader("Upload Log FMS / DSMS", type=['xlsx', 'csv'])
    secret_key = st.secrets.get("GEMINI_API_KEY", "")
    user_api_key = secret_key if secret_key else st.text_input("Gemini API Key", type="password")

# ==================== HEADER UTAMA ====================
header_with_logo(
    "🛡️ Driver Safety Management System",
    "PT. Bumiputera Maha Terpercaya<br>"
    "<b>Monitoring Fatigue • Driver Behavior Analytics • K3 Compliance</b><br>"
    "<span style='font-size:12px; opacity:0.85; display:inline-block; margin-top:4px;'>"
    "Sistem analisis terintegrasi untuk memantau risiko fatigue pengemudi, perilaku berkendara, dan penegakan sanksi K3 secara real-time sesuai SOP BMT-CHL-SOP 011 & BIB-HSE-PPO-035."
    "</span>",
    "image.png"
)

# ==================== MAIN ====================
if uploaded_file is None:
    st.info("👆 Upload file Excel/CSV di sidebar untuk memulai")
else:
    with st.spinner("🔄 Memproses data..."):
        df, cols, age_labels = load_and_process_data(uploaded_file)
        if df is None:
            st.error("❌ File tidak valid")
            st.stop()

        df_fatigue = df[df['Type'].isin(['Mata Tertutup', 'Mengantuk'])].copy()
        df_overspeed = df[df['Type'] == 'Overspeed'].copy()
        order_months, order_2h = get_order_months(), get_order_2h()
        total_f, total_o = len(df_fatigue), len(df_overspeed)
        total_alarm = total_f + total_o
        jam_counts = df_fatigue['Jam_Range'].value_counts()
        top_jam = jam_counts.index[0] if not jam_counts.empty else "N/A"

        # KPI CARDS
        st.markdown("### 📊 Ringkasan")
        c1, c2, c3, c4 = st.columns(4)
        top_fatigue_loc = df_fatigue['Lokasi'].value_counts().index[0] if not df_fatigue.empty else "N/A"
        fatigue_loc_footer = f"{df_fatigue['Lokasi'].value_counts().iloc[0]} kasus" if not df_fatigue.empty else "0 kasus"

        with c1: kpi("Total Alarm", fmt_num(total_alarm), "Semua jenis alarm", "🚨", "#ef4444")
        with c2: kpi("Fatigue", fmt_num(total_f), "Kasus fatigue valid", "😴", "#f59e0b")
        with c3: kpi("Overspeed", fmt_num(total_o), "Kasus overspeed", "🚗", "#3b82f6")
        with c4: kpi("Lokasi Rawan Fatigue", top_fatigue_loc, fatigue_loc_footer, "📍", "#8b5cf6")

        st.markdown("---")
        st.markdown("### 📋 Ringkasan Eksekutif")
        col1, col2 = st.columns(2)
        with col1:
            insight("#fee2e2", "Jam Kritis Sirkadian (BIB PPO-035)", f"Puncak fatigue di {top_jam} — Masuk jam rawan 02.00–06.00 WITA!")
        with col2:
            top_unit = df_fatigue['Unit'].value_counts().index[0] if not df_fatigue.empty else "N/A"
            insight("#fee2e2", "Unit Temuan Berulang Valid (SOP BMT 011)", f"Unit {top_unit} — Prioritaskan Live Streaming Monitoring!")

        # SEKSI AI NARRATIVE GENERATOR
        st.markdown("#### 📄 Laporan Ringkasan Eksekutif K3")
        if user_api_key:
            if st.button("✨ Generate Laporan Ringkasan Eksekutif"):
                with st.spinner("🧠 AI sedang menyusun laporan..."):
                    prompt_eksekutif = f"""
                    Anda adalah Senior Safety Specialist di PT. Bumiputera Maha Terpercaya (BMT).
                    Analisis data DSMS berikut dan buatkan Laporan Ringkasan Eksekutif K3 yang PATUH pada SOP BMT-CHL-SOP 011 dan BIB-HSE-PPO-035.

                    DILARANG MEMBUAT Header Memorandum atau tanda tangan di akhir.
                    DILARANG MENGGUNAKAN TANDA BINTANG (*) SAMA SEKALI DALAM TEKS OUTPUT.

                    Data: Total Alarm: {total_alarm}, Fatigue: {total_f}, Overspeed: {total_o}, Hotspot: {top_fatigue_loc}, Jam Puncak: {top_jam}.

                    Format Output (HTML):
                    <b>📌 1. RINGKASAN SITUASI & EVALUASI COMPLIANCE SAFETY</b><br>
                    Uraikan ringkasan temuan DSMS & sirkadian jam rawan.<br><br>
                    <b>🎯 2. PENILAIAN RISIKO OPERASIONAL & AUDIT ATRIBUT</b><br>
                    Risiko fatalitas & audit kacamata/masker sesuai SOP 011.<br><br>
                    <b>🚀 3. ACTION PLAN TAKTIS TIM K3/SAFETY (KAMPANYE 7B)</b><br>
                    3 langkah taktis pengawalan & verifikasi ADAS.
                    """
                    st.session_state['res_eksekutif'] = generate_gemini_analysis(user_api_key, prompt_eksekutif)
            
            if st.session_state['res_eksekutif']:
                st.markdown(f"<div style='background:white; color:#0f172a; padding:20px; border-radius:14px; border-left:5px solid #2563eb; text-align:justify;'>{st.session_state['res_eksekutif']}</div>", unsafe_allow_html=True)

        st.markdown("---")

        # TABS UTAMA
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Overview Bulanan", "📅 Tren Mingguan (Week 1-52)",
            "🗺️ Lokasi & Waktu", "👥 Driver & Unit", "📋 Data Logs", "🧠 Analisis Lanjutan"
        ])

        with tab1:
            st.markdown("### 📉 Tren Temuan DSMS Bulanan")
            render_chart(plot_tren_generic(df_fatigue, title="Tren Bulanan Kasus Fatigue", color="#ef4444"))
            render_chart(plot_tren_generic(df_overspeed, title="Tren Bulanan Kasus Overspeed", color="#f59e0b"))
            render_chart(plot_tren_generic(df, title="Tren Bulanan Total Seluruh Alarm DSMS", color="#2563eb"))
            render_chart(plot_shift_comparison(df_fatigue))
            render_chart(plot_alarm_distribution(df_fatigue))

        with tab2:
            st.markdown("### 📅 Analisis Tren Fatigue Mingguan (Week 1 - 52)")
            fig_week, trend_status = plot_weekly_trend_with_trendline(df_fatigue)
            if fig_week:
                st.markdown(f"#### Status Tren Keseluruhan: **{trend_status}**")
                render_chart(fig_week)

        # TAB 3: LOKASI & WAKTU + GENERATOR AI DISTRIBUSI WAKTU
        with tab3:
            st.markdown("### 🗺️ Analisis Lokasi & Waktu")
            render_chart(plot_jam_distribution(df_fatigue, order_2h))
            
            if user_api_key:
                with st.expander("💡 Rekomendasi AI: Solusi Proaktif & Strategi Jam Rawan (PPO BIB-035)", expanded=False):
                    if st.button("✨ Generate Temporal Preventive Strategy"):
                        with st.spinner("🧠 AI sedang menganalisis pola jam rawan..."):
                            jam_data = df_fatigue['Jam_Range'].value_counts().head(5).to_dict()
                            prompt_jam_rawan = f"""
                            Anda adalah Senior Safety Specialist operasional tambang PT. BMT.
                            Berdasarkan data distribusi jam puncak fatigue: {jam_data}

                            Berikan STRATEGI PENCEGAHAN TEMPORAL yang patuh pada BIB-HSE-PPO-035.
                            DILARANG MENGGUNAKAN TANDA BINTANG (*) SAMA SEKALI.

                            Format HTML:
                            <b>📌 1. ANALISIS POLA WAKTU & RITME SIRKADIAN (BIB-035)</b><br>
                            Uraikan jam kritis Sirkadian (02.00 - 06.00 WITA).<br><br>
                            <b>🎯 2. ARAH STRATEGI & PENCEGAHAN TEMPORAL</b><br>
                            - Program Wake Up Call Radio (kata sandi).<br>
                            - Istirahat Fleksibel Hauling di rest area.<br><br>
                            <b>🚀 3. REKOMENDASI INTERVENSI PENGAWAS CCR/FMS</b><br>
                            Langkah intervensi jika driver fatigue valid.
                            """
                            st.session_state['res_jam'] = generate_gemini_analysis(user_api_key, prompt_jam_rawan)
                    
                    if st.session_state['res_jam']:
                        st.markdown(f"<div style='background:white; color:#0f172a; padding:20px; border-radius:14px; border-left:5px solid #2563eb; text-align:justify;'>{st.session_state['res_jam']}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            render_chart(plot_hotspot(df_fatigue, "Fatigue"))
            render_chart(plot_hotspot(df_overspeed, "Overspeed"))

        # TAB 4: DRIVER & UNIT + GENERATOR AI ACTION PLAN DRIVER
        with tab4:
            st.markdown("### 👥 Analisis Driver & Unit")
            render_chart(plot_demografi(df_fatigue, df_overspeed, age_labels))
            render_chart(plot_top_driver(df_fatigue))
            
            if user_api_key:
                with st.expander("👤 Rekomendasi AI: Action Plan Driver & Disiplin (SOP BMT 011)", expanded=False):
                    if st.button("✨ Generate Strategy & Preventive Plan"):
                        with st.spinner("🧠 AI sedang menyusun action plan driver..."):
                            top_drivers = df_fatigue['Driver'].value_counts().head(5).to_dict()
                            prompt_top_driver = f"""
                            Anda adalah Senior Safety Specialist PT. BMT.
                            Data Top Driver Fatigue: {top_drivers}

                            Susun ACTION PLAN DISIPLIN DRIVER berdasarkan BMT-CHL-SOP 011.
                            DILARANG MENGGUNAKAN TANDA BINTANG (*) SAMA SEKALI.

                            Format HTML:
                            <b>📌 1. EVALUASI TINGKAT RISIKO & COMPLIANCE THRESHOLD</b><br>
                            Evaluasi threshold 4x fatigue/minggu.<br><br>
                            <b>🎯 2. ACTION PLAN TINDAK LANJUT DISIPLIN & SANKSI</b><br>
                            Penegakan SP1/SP2/SP3 & Fit to Work.<br><br>
                            <b>🚀 3. PENGAWASAN LAPANGAN</b><br>
                            Komitmen pengawasan cegah pembiaran.
                            """
                            st.session_state['res_driver'] = generate_gemini_analysis(user_api_key, prompt_top_driver)
                    
                    if st.session_state['res_driver']:
                        st.markdown(f"<div style='background:white; color:#0f172a; padding:20px; border-radius:14px; border-left:5px solid #2563eb; text-align:justify;'>{st.session_state['res_driver']}</div>", unsafe_allow_html=True)

            st.markdown("---")
            if not df.empty:
                unit = df['Unit'].value_counts().head(10).reset_index()
                unit.columns = ['Unit', 'Total']
                fig_u = px.bar(unit.sort_values('Total'), x='Total', y='Unit', orientation='h', title='Top 10 Unit', text='Total')
                render_chart(fig_u)
            
            render_chart(plot_heatmap(df_fatigue, order_months))

        with tab5:
            st.markdown("### 📋 Data Logs")
            st.dataframe(df.head(100), use_container_width=True, hide_index=True)

        with tab6:
            st.markdown("## 🧠 Analisis Lanjutan & Pencegahan")
            render_chart(plot_forecast(df_fatigue))
            render_chart(plot_fatigue_vs_overspeed(df_fatigue, df_overspeed))

st.markdown("---")
st.caption("© 2026 PT. Bumiputera Maha Terpercaya | Driver Safety Management System v3.0 (Patuh SOP BMT 011 & BIB 035)")
