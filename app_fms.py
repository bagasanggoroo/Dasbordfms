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

# ==================== CSS CUSTOM STYLING (PERBAIKAN KONTRAST TEKS) ====================
# ==================== CSS CUSTOM STYLING (PERBAIKAN KONTRAST TEKS & PRINT PDF) ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1600px;
}

/* FIX LATAR & TEKS UTAMA */
.stApp {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
}

/* FIX SIDEBAR / PANEL KIRI */
[data-testid="stSidebar"] {
    background-color: var(--background-secondary-color) !important;
}

[data-testid="stSidebar"] *, 
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {
    color: var(--text-color) !important;
}

/* KPI CARDS */
.kpi {
    background-color: var(--background-secondary-color, #ffffff);
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,.05);
    transition: all .25s ease;
    border: 1px solid var(--border-color, #e2e8f0);
    position: relative;
}
.kpi:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px rgba(0,0,0,.1);
}
.kpi-icon {
    font-size: 28px;
    margin-bottom: 6px;
}
.kpi-title {
    font-size: 13px;
    opacity: 0.8;
    text-transform: uppercase;
    letter-spacing: .8px;
    font-weight: 600;
}
.kpi-value {
    font-size: 34px;
    font-weight: 700;
    color: var(--text-color);
    margin-top: 6px;
}
.kpi-footer {
    margin-top: 8px;
    color: #3b82f6;
    font-size: 13px;
    font-weight: 500;
}

/* BUTTON STYLING */
.stButton > button {
    background: #3b82f6;
    color: #ffffff !important;
    border-radius: 10px;
    border: none;
    padding: .55rem 1rem;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    transition: all .2s ease;
}
.stButton > button:hover {
    background: #2563eb;
    color: #ffffff !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(37,99,235,0.3);
}

/* DATAFRAME STYLING */
div[data-testid="stDataFrame"] {
    border-radius: 14px;
    border: 1px solid var(--border-color, #e2e8f0);
    overflow: hidden;
}

/* PLOTLY CONTAINER */
.js-plotly-plot .plotly .main-svg {
    border-radius: 12px;
}

/* ==================== KHUSUS SAAT CETAK / SIMPAN PDF (@media print) ==================== */
@media print {
    /* Sembunyikan Sidebar, Header Bawaan, Button, Footer */
    section[data-testid="stSidebar"],
    header[data-testid="stHeader"],
    .stButton,
    footer,
    .no-print {
        display: none !important;
    }
    
    /* SEMBUNYIKAN JUDUL/TAB NAVIGASI (Overview Bulanan, Tren Mingguan, dll) */
    div[data-testid="stTabs"] [role="tablist"],
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        display: none !important;
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
}
</style>
""", unsafe_allow_html=True)

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
    if pd.isna(t):
        return 'Unknown'
    try:
        if isinstance(t, (datetime, pd.Timestamp)):
            h = t.hour
        elif hasattr(t, 'hour'):
            h = t.hour
        else:
            h = int(str(t).strip().split(':')[0])
        return f"{h:02d}:00-{h+1:02d}:59"
    except:
        return 'Unknown'

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

# ==================== HEADER DENGAN INTEGRASI LOGO ====================
def header_with_logo(title, subtitle, logo_path="image.png"):
    img_b64 = get_image_base64(logo_path)
    logo_html = f'<img src="data:image/png;base64,{img_b64}" style="height: 55px; object-fit: contain;">' if img_b64 else '<span style="font-size:30px;">🚛</span>'
    
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
            <p style="margin: 6px 0 0 0; opacity: 0.85; font-size: 14px; line-height: 1.4; color: white;">{subtitle}</p>
        </div>
        <div style="
            background: white;
            padding: 8px 16px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        ">
            {logo_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== DATA PROCESSING WITH CACHE ====================
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

def rec_card(priority, icon, text):
    bg = '#fef2f2' if 'PRIORITAS' in priority else '#fffbeb'
    border = '#ef4444' if 'PRIORITAS' in priority else '#f59e0b'
    st.markdown(f"""
    <div style="background:{bg}; padding:12px 16px; border-radius:12px; border-left:5px solid {border}; margin:6px 0; color:#1e293b;">
        <span style="font-weight:600; font-size:0.85rem;">{priority}</span> 
        <span style="font-size:1rem;">{icon}</span> 
        <span style="font-size:0.9rem; color:#1e293b;">{text}</span>
    </div>
    """, unsafe_allow_html=True)

# ==================== CHART FUNCTIONS (DISET TEKS JELAS TERBACA) ====================
def plot_tren_generic(df_target, title="Tren Bulanan", color="#2563eb"):
    if df_target.empty or 'Month_Num' not in df_target.columns:
        return None
    
    trend = df_target.groupby(['Month_Num', 'Bulan']).size().reset_index(name='Total').sort_values('Month_Num')
    if trend.empty:
        return None
    
    max_val = trend['Total'].max()
    
    fig = px.line(
        trend, x='Bulan', y='Total',
        markers=True, title=title,
        color_discrete_sequence=[color],
        text='Total'
    )
    fig.update_traces(
        line=dict(width=3), 
        marker=dict(size=10),
        textposition="top center",
        textfont=dict(size=11, color='#0f172a', weight='bold')
    )
    fig.update_layout(
        plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
        font=dict(family='Inter', size=12, color='#0f172a'),
        title=dict(font=dict(color='#0f172a', size=14, weight='bold')),
        xaxis=dict(showgrid=False, tickfont=dict(color='#0f172a', size=11), title=dict(font=dict(color='#0f172a'))),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=1, range=[0, max_val * 1.35], tickfont=dict(color='#0f172a', size=11), title=dict(font=dict(color='#0f172a'))),
        hovermode='x unified',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    for i, row in trend.iterrows():
        is_max = bool(row['Total'] == max_val)
        if is_max:
            fig.add_annotation(
                x=row['Bulan'], y=row['Total'],
                text=f"🔥 {row['Total']}",
                showarrow=True, arrowhead=1, arrowcolor=color,
                yshift=14,
                font=dict(size=12, color='#0f172a', weight='bold'),
                bgcolor='#fee2e2' if color=='#ef4444' else '#fef3c7',
                bordercolor=color, borderwidth=1
            )
    return fig

def plot_weekly_trend_with_trendline(df_fatigue):
    if df_fatigue.empty or 'Week' not in df_fatigue.columns:
        return None, "Data Kosong"
    
    weekly = df_fatigue.groupby('Week').size().reset_index(name='Total').sort_values('Week')
    if len(weekly) < 2:
        return None, "Data Tidak Cukup"
    
    x = weekly['Week'].values.astype(float)
    y = weekly['Total'].values.astype(float)
    
    slope, intercept = np.polyfit(x, y, 1)
    trendline_y = slope * x + intercept
    
    if slope > 0.1:
        trend_status = "⚠️ CENDERUNG NAIK (Memburuk)"
        trend_color = "#ef4444"
    elif slope < -0.1:
        trend_status = "✅ CENDERUNG TURUN (Membaik)"
        trend_color = "#22c55e"
    else:
        trend_status = "➡️ STABIL"
        trend_color = "#3b82f6"

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=weekly['Week'], y=weekly['Total'],
        mode='lines+markers',
        name='Temuan Fatigue Mingguan',
        line=dict(color='#ef4444', width=2.5),
        marker=dict(size=6),
        hovertemplate='<b>Week %{x}</b>: %{y} kasus<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=weekly['Week'], y=trendline_y,
        mode='lines',
        name=f'Garis Tren ({trend_status})',
        line=dict(color=trend_color, width=3, dash='dash')
    ))

    fig.update_layout(
        title='📊 Tren Temuan Fatigue Mingguan (Week 1–52) + Garis Tren',
        plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
        font=dict(family='Inter', size=12, color='#0f172a'),
        title_font=dict(color='#0f172a'),
        xaxis=dict(
            title="Minggu Ke- (Week)", showgrid=True, gridcolor='#e2e8f0',
            dtick=1, rangeslider=dict(visible=False), tickfont=dict(color='#0f172a'), title_font=dict(color='#0f172a')
        ),
        yaxis=dict(title="Jumlah Temuan", showgrid=True, gridcolor='#e2e8f0', tickfont=dict(color='#0f172a'), title_font=dict(color='#0f172a')),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, font=dict(color='#0f172a')),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig, trend_status

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
        plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
        font=dict(family='Inter', size=12, color='#0f172a'),
        title_font=dict(color='#0f172a'),
        xaxis=dict(showgrid=False, tickfont=dict(color='#0f172a')),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=1, tickfont=dict(color='#0f172a')),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, font=dict(color='#0f172a')),
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
    fig.update_traces(textposition='outside', textfont=dict(size=12, color='#0f172a', weight='bold'))
    fig.update_layout(
        plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
        font=dict(family='Inter', size=12, color='#0f172a'),
        title_font=dict(color='#0f172a'),
        xaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=1, tickfont=dict(color='#0f172a')),
        yaxis=dict(showgrid=False, tickfont=dict(color='#0f172a')),
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
        textfont=dict(size=11, color='#0f172a', weight='bold')
    )
    
    max_row = rj[rj['Total'] == max_val].iloc[0]
    fig.add_annotation(
        x=max_row['Jam'], 
        y=max_val + (max_val * 0.12),
        text="⚠️ PUNCAK TERTINGGI",
        showarrow=True, arrowhead=2, arrowcolor='#991b1b', arrowsize=1.2,
        font=dict(size=11, color='white', weight='bold'),
        bgcolor='#991b1b', bordercolor='#7f1d1d', borderwidth=2, borderpad=4
    )
    
    fig.update_layout(
        plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
        font=dict(family='Inter', size=12, color='#0f172a'),
        title_font=dict(color='#0f172a'),
        xaxis=dict(showgrid=False, tickangle=45, tickfont=dict(color='#0f172a')),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=1, range=[0, max_val * 1.35], tickfont=dict(color='#0f172a')),
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
    fig.update_traces(marker_color=colors, textposition='outside', textfont=dict(size=11, color='#0f172a', weight='bold'))
    fig.update_layout(
        plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
        font=dict(family='Inter', size=12, color='#0f172a'),
        title_font=dict(color='#0f172a'),
        xaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=1, range=[0, max_val * 1.2], tickfont=dict(color='#0f172a')),
        yaxis=dict(showgrid=False, tickfont=dict(color='#0f172a')),
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
        text=merged['Fatigue'], textposition='outside',
        textfont=dict(color='#0f172a', weight='bold')
    ))
    fig.add_trace(go.Bar(
        x=merged['Kelompok'], y=merged['Overspeed'],
        name='Overspeed', marker_color='#f59e0b',
        text=merged['Overspeed'], textposition='outside',
        textfont=dict(color='#0f172a', weight='bold')
    ))
    fig.update_layout(
        title='Demografi Umur Driver (Rentang 5 Tahun)',
        plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
        font=dict(family='Inter', size=12, color='#0f172a'),
        title_font=dict(color='#0f172a'),
        xaxis=dict(showgrid=False, title="Rentang Umur (Tahun)", tickfont=dict(color='#0f172a'), title_font=dict(color='#0f172a')),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=1, tickfont=dict(color='#0f172a'), title_font=dict(color='#0f172a')),
        barmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, font=dict(color='#0f172a')),
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
    fig.update_traces(marker_color=colors, textposition='outside', textfont=dict(size=10, color='#0f172a', weight='bold'))
    fig.update_layout(
        plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
        font=dict(family='Inter', size=11, color='#0f172a'),
        title_font=dict(color='#0f172a'),
        xaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=1, range=[0, max_val * 1.25], tickfont=dict(color='#0f172a')),
        yaxis=dict(showgrid=False, tickfont=dict(color='#0f172a')),
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
        plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
        font=dict(family='Inter', size=11, color='#0f172a'),
        title_font=dict(color='#0f172a'),
        xaxis=dict(side='bottom', tickfont=dict(color='#0f172a')), 
        yaxis=dict(title='Driver', tickfont=dict(color='#0f172a'), title_font=dict(color='#0f172a')),
        margin=dict(l=20, r=20, t=40, b=20),
        height=max(400, len(heatmap_data) * 25)
    )
    fig.update_xaxes(title='Bulan', title_font=dict(color='#0f172a'))
    fig.update_yaxes(title='Driver', title_font=dict(color='#0f172a'))
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
        plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
        font=dict(family='Inter', size=12, color='#0f172a'),
        title_font=dict(color='#0f172a'),
        xaxis=dict(showgrid=False, tickfont=dict(color='#0f172a')),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=1, tickfont=dict(color='#0f172a')),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, font=dict(color='#0f172a')),
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
        plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
        font=dict(family='Inter', size=11, color='#0f172a'),
        title_font=dict(color='#0f172a'),
        xaxis=dict(showgrid=False, tickangle=45, tickfont=dict(color='#0f172a')),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=1, tickfont=dict(color='#0f172a')),
        barmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, font=dict(color='#0f172a')),
        margin=dict(l=20, r=20, t=40, b=20),
        height=450
    )
    return fig

# ==================== FUNGSI INTEGRASI GEMINI AI ====================
def generate_gemini_analysis(api_key, prompt_text):
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-flash',
            contents=prompt_text,
        )
        return response.text
    except Exception as e:
        return f"❌ Error saat memproses AI: {str(e)}"

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:10px 0 20px 0;">
        <div style="font-size:40px;">🛡️</div>
        <div style="font-weight:700; font-size:1.2rem;">DSMS Dashboard</div>
        <div style="font-size:0.7rem; opacity:0.8;">v3.0 · Enterprise</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📁 Data Source")
    uploaded_file = st.file_uploader("Upload File Log FMS", type=['xlsx', 'csv'])
    
    st.markdown("---")
    st.markdown("### 🤖 Config Gemini AI")
    
    secret_key = st.secrets.get("GEMINI_API_KEY", "")
    if secret_key:
        user_api_key = secret_key
        st.success("🔑 Gemini API Key terhubung dari Secrets")
    else:
        user_api_key = st.text_input("Masukkan Gemini API Key", type="password", help="Dapatkan API Key gratis di Google AI Studio")
    
    st.markdown("---")
    st.caption("© 2026 PT. Bumiputera Maha Terpercaya")

# ==================== HEADER DENGAN INTEGRASI LOGO ====================
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
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background:white; padding:30px; border-radius:18px; text-align:center; border:1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <div style="font-size:40px;">📊</div>
            <div style="font-weight:700; color:#0f172a; font-size:1.1rem; margin-top:8px;">Analisis Lengkap</div>
            <div style="font-size:0.85rem; color:#475569; margin-top:4px;">Tren fatigue, overspeed, performa</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:white; padding:30px; border-radius:18px; text-align:center; border:1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <div style="font-size:40px;">🗺️</div>
            <div style="font-weight:700; color:#0f172a; font-size:1.1rem; margin-top:8px;">Spatial & Temporal</div>
            <div style="font-size:0.85rem; color:#475569; margin-top:4px;">Hotspot & pola waktu</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:white; padding:30px; border-radius:18px; text-align:center; border:1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <div style="font-size:40px;">👥</div>
            <div style="font-weight:700; color:#0f172a; font-size:1.1rem; margin-top:8px;">Driver & Fleet</div>
            <div style="font-size:0.85rem; color:#475569; margin-top:4px;">Demografi & performa</div>
        </div>
        """, unsafe_allow_html=True)
else:
    with st.spinner("🔄 Memproses data..."):
        try:
            df, cols, age_labels = load_and_process_data(uploaded_file)
            
            if df is None:
                st.error("❌ Kolom minimum wajib ada: Tanggal, Type, Driver")
                st.stop()

            df_fatigue = df[df['Type'].isin(['Mata Tertutup', 'Mengantuk'])].copy()
            df_overspeed = df[df['Type'] == 'Overspeed'].copy()
            
            order_months = get_order_months()
            order_2h = get_order_2h()
            
            total_f = len(df_fatigue)
            total_o = len(df_overspeed)
            total_alarm = total_f + total_o
            
            jam_counts = df_fatigue['Jam_Range'].value_counts()
            top_jam = jam_counts.index[0] if not jam_counts.empty else "N/A"
            top_jam_val = jam_counts.iloc[0] if not jam_counts.empty else 0
            
            loc_counts = df_fatigue['Lokasi'].value_counts()
            top_loc = loc_counts.index[0] if not loc_counts.empty else "N/A"
            top_loc_val = loc_counts.iloc[0] if not loc_counts.empty else 0
            
            # ========== KPI CARDS ==========
            st.markdown("### 📊 Ringkasan")
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                kpi("Total Alarm", fmt_num(total_alarm), "Semua jenis alarm", "🚨", "#ef4444")
            with c2:
                kpi("Fatigue", fmt_num(total_f), "Kasus fatigue", "😴", "#f59e0b")
            with c3:
                kpi("Overspeed", fmt_num(total_o), "Kasus overspeed", "🚗", "#3b82f6")
            with c4:
                kpi("Lokasi Rawan (Hotspot)", top_loc, f"{top_loc_val} kasus", "📍", "#8b5cf6")
            
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
                        insight("#fee2e2", "Jam Kritis Sirkadian (BIB PPO-035)", f"Puncak fatigue di {top_jam} ({top_val} kasus, {pct:.1f}%) — Masuk jam rawan utama 02.00–06.00 WITA!")
                    else:
                        insight("#dbeafe", "Jam Rawan", f"{top_jam} ({top_val} kasus, {pct:.1f}%)")
                
                shift_counts = df_fatigue['Shift'].value_counts()
                if 'Shift 2' in shift_counts.index and 'Shift 1' in shift_counts.index:
                    s2, s1 = shift_counts['Shift 2'], shift_counts['Shift 1']
                    if s1 > 0:
                        ratio = s2 / s1
                        if ratio > 2:
                            insight("#fee2e2", "Shift Malam (Kritis)", f"{ratio:.1f}x lebih tinggi ({s2} vs {s1}) — tingkatkan Wake Up Call!")
                        elif ratio > 1.2:
                            insight("#fef3c7", "Shift Malam", f"{ratio:.1f}x lebih tinggi ({s2} vs {s1})")
                        else:
                            insight("#dcfce7", "Shift Seimbang", f"{s2} vs {s1}")
            
            with col2:
                if not df_fatigue.empty and 'Week' in df_fatigue.columns:
                    weekly_driver_fatigue = df_fatigue.groupby(['Driver', 'Week']).size().reset_index(name='Weekly_Count')
                    max_weekly_row = weekly_driver_fatigue.sort_values('Weekly_Count', ascending=False).iloc[0]
                    
                    top_driver_name = max_weekly_row['Driver']
                    max_weekly_val = max_weekly_row['Weekly_Count']
                    top_driver_total_all = df_fatigue['Driver'].value_counts().get(top_driver_name, 0)
                    
                    if max_weekly_val >= 4:
                        insight("#fee2e2", "Driver Risk High (SOP BMT 011)", 
                                f"{top_driver_name} ({max_weekly_val} kasus di Week {max_weekly_row['Week']} | Total: {top_driver_total_all} kasus) — Menyentuh threshold SP1 & Lubang 1!")
                    else:
                        insight("#fef3c7", "Driver Berisiko", 
                                f"{top_driver_name} (Maks {max_weekly_val} kasus/minggu | Total: {top_driver_total_all} kasus) — Perlu monitoring")
                else:
                    top_driver_name = "N/A"
                    max_weekly_val = 0

                unit_counts = df_fatigue['Unit'].value_counts()
                if not unit_counts.empty:
                    top_unit = unit_counts.index[0]
                    top_val = unit_counts.iloc[0]
                    if top_val > 5:
                        insight("#fee2e2", "Unit Temuan Berulang Valid (SOP BMT 011)", 
                                f"{top_unit} ({top_val} temuan valid) — Prioritaskan untuk Live Streaming Monitoring CCR!")
                    else:
                        insight("#dbeafe", "Unit Temuan Berulang", f"{top_unit} ({top_val} temuan valid)")

            # SEKSI AI NARRATIVE GENERATOR
            st.markdown("#### 🤖 Laporan Narasi Otomatis (Gemini AI - Standard Compliance)")
            if user_api_key:
                if st.button("✨ Generate Narasi Laporan Eksekutif dengan Gemini AI"):
                    with st.spinner("🧠 AI sedang menganalisis data berdasarkan SOP BMT 011 & PPO BIB 035..."):
                        prompt_eksekutif = f"""
                        Anda adalah Senior Safety Specialist di PT. Bumiputera Maha Terpercaya (BMT) untuk operasional tambang PT Borneo Indobara (BIB).
                        Analisis data Fleet Management System (FMS) berikut dan buatkan Laporan Ringkasan Eksekutif K3 yang SEPENUHNYA PATUH pada SOP BMT-CHL-SOP 011 dan BIB-HSE-PPO-035.

                        RULES PENULISAN (SANGAT KETAT):
                        - DILARANG MEMBUAT Header Memorandum (KEPADA, DARI, PERIHAL, dll).
                        - DILARANG MEMBUAT pembuka formalitas atau salam/penutup/tanda tangan.
                        - DILARANG MENGGUNAKAN TANDA BINTANG (*) SAMA SEKALI DALAM TEKS OUTPUT.

                        ACUAN STANDAR REGULASI:
                        1. Threshold Fatigue Valid BMT/BIB: Maksimal 4x temuan/minggu. Jika >=4x dikenakan sanksi bertingkat (SP1+Lubang 1).
                        2. Jam Rawan Utama PPO BIB-035: Pukul 02.00 - 06.00 WITA (Wajib intensifkan Wake Up Call kata sandi).
                        3. Intervensi Driver Fatigue Valid: Kecepatan maks 30 kph, hazard ON, dikawal (escorted) ke Rest Area/Office, dan verifikasi ADAS dengan handbrake & wheel chock.
                        4. Kampanye 7B: Berhenti, Beritahu, Bernafas, Beristirahat, Bekerja kembali, Berolahraga ringan, Berdoa.

                        DATA UTAMA FMS:
                        - Total Seluruh Alarm: {total_alarm} kasus
                        - Total Kasus Fatigue: {total_f} kasus
                        - Total Kasus Overspeed: {total_o} kasus
                        - Lokasi Rawan (Hotspot) Utama: {top_loc}
                        - Jam Puncak Rawan Fatigue: {top_jam}
                        - Driver Berisiko Tinggi (Mingguan): {top_driver_name} ({max_weekly_val} kasus di minggu puncak)

                        LANGSUNG TAMPILKAN FORMAT BERIKUT (Gunakan tag HTML <b> untuk judul):

                        <b>📌 1. RINGKASAN SITUASI & EVALUASI COMPLIANCE SAFETY</b><br>
                        Uraikan ringkasan temuan FMS, bahaya micro-sleep di jam rawan sirkadian BIB (02.00-06.00 WITA), serta evaluasi kepatuhan driver terhadap threshold 4x fatigue/minggu.

                        <br><b>🎯 2. PENILAIAN RISIKO OPERASIONAL & AUDIT ATRIBUT</b><br>
                        - Risiko Fatalitas (Collision / Run-off-road) di area Hotspot.<br>
                        - Audit Atribut Driver (Evaluasi larangan kacamata hitam, topi, dan penutup mulut/masker sesuai SOP 011).<br>
                        - Driver Berisiko Tinggi & Sanksi Bertingkat (SP1/SP2/SP3).

                        <br><b>🚀 3. ACTION PLAN TAKTIS TIM K3/SAFETY (BERDASARKAN KAMPANYE 7B & SOP 011)</b><br>
                        Berikan 3 langkah taktis instruksi kerja tim Safety/CCR (Pengawalan ke rest area, pergantian driver spare, dan verifikasi fisik ADAS).

                        Gunakan bahasa yang padat, lugas, tegas, berorientasi K3 pertambangan, dan profesional.
                        """
                        st.session_state['res_eksekutif'] = generate_gemini_analysis(user_api_key, prompt_eksekutif)
                
                if st.session_state['res_eksekutif']:
                    st.markdown(f"""
                    <div style="background:white; color:#0f172a; padding:20px; border-radius:16px; border-left:5px solid #2563eb; box-shadow:0 4px 15px rgba(0,0,0,0.05); line-height:1.6;">
                        {st.session_state['res_eksekutif']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("💡 Tempel Gemini API Key di sidebar untuk mengaktifkan pembuat laporan narasi AI otomatis.")
            
            st.markdown("---")
            
            # ========== TABS UTAMA ==========
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📊 Overview Bulanan",
                "📅 Tren Mingguan (Week 1-52)",
                "🗺️ Lokasi & Waktu",
                "👥 Driver & Unit",
                "📋 Data Logs",
                "🧠 Analisis Lanjutan"
            ])
            
            # ========== TAB 1: OVERVIEW BULANAN ==========
            with tab1:
                st.markdown("### 📉 Tren Temuan FMS Bulanan")
                
                fig_f = plot_tren_generic(df_fatigue, title="Tren Bulanan Kasus Fatigue", color="#ef4444")
                if fig_f:
                    st.plotly_chart(fig_f, use_container_width=True)
                else:
                    st.info("Tidak ada data fatigue")
                
                fig_o = plot_tren_generic(df_overspeed, title="Tren Bulanan Kasus Overspeed", color="#f59e0b")
                if fig_o:
                    st.plotly_chart(fig_o, use_container_width=True)
                else:
                    st.info("Tidak ada data overspeed")

                fig_total = plot_tren_generic(df, title="Tren Bulanan Total Seluruh Alarm FMS", color="#2563eb")
                if fig_total:
                    st.plotly_chart(fig_total, use_container_width=True)
                else:
                    st.info("Tidak ada data alarm")

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
            
            # ========== TAB 2: TREN MINGGUAN ==========
            with tab2:
                st.markdown("### 📅 Analisis Tren Fatigue Mingguan (Week 1 - 52)")
                st.caption("Dilengkapi dengan Garis Tren (Trendline) untuk melihat arah perkembangan kasus sepanjang tahun.")
                
                fig_week, trend_status = plot_weekly_trend_with_trendline(df_fatigue)
                if fig_week:
                    st.markdown(f"#### Status Tren Keseluruhan: **{trend_status}**")
                    st.plotly_chart(fig_week, use_container_width=True)
                else:
                    st.warning("Data minggu tidak mencukupi untuk menampilkan grafik.")

            # ========== TAB 3: LOKASI & WAKTU ==========
            with tab3:
                fig = plot_jam_distribution(df_fatigue, order_2h)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Tidak ada data jam")
                
                if user_api_key:
                    with st.expander("💡 Rekomendasi AI: Solusi Proaktif & Strategi Jam Rawan (PPO BIB-035)", expanded=False):
                        if st.button("✨ Generate Temporal Preventive Strategy"):
                            with st.spinner("🧠 AI sedang menganalisis pola jam rawan berdasarkan PPO BIB-035..."):
                                jam_data = df_fatigue['Jam_Range'].value_counts().head(5).to_dict()
                                prompt_jam_rawan = f"""
                                Anda adalah Senior Safety Specialist operasional tambang PT. BMT (Mitra Kerja PT Borneo Indobara).
                                Berdasarkan rekapitulasi data distribusi jam puncak rawan fatigue berikut: {jam_data}

                                Berikan STRATEGI PENCEGAHAN TEMPORAL yang patuh pada BIB-HSE-PPO-035 secara langsung tanpa basa-basi.

                                DILARANG MEMBUAT:
                                - Header Memorandum, pembuka formalitas, maupun tanda tangan di akhir.
                                - DILARANG MENGGUNAKAN TANDA BINTANG (*) SAMA SEKALI DALAM TEKS OUTPUT.

                                ACUAN ATURAN:
                                - Puncak Sirkadian Rendah: Jam 02.00 - 06.00 WITA. Wajib pemantauan Wake Up Call (kata sandi radio) maks 3x panggilan.
                                - Jam Rawan Acak: 14.00-16.00 (Shift 1) & 23.00-02.00 (Shift 2).
                                - Istirahat Fleksibel Hauling: Minimal 1 jam di workshop/rest area per shift.

                                LANGSUNG TAMPILKAN FORMAT BERIKUT (Gunakan tag HTML <b> untuk judul):

                                <b>📌 1. ANALISIS POLA WAKTU & RITME SIRKADIAN (BIB-035)</b><br>
                                Uraikan kecenderungan jam kritis FMS vs jam rawan resmi BIB (02.00 - 06.00 WITA).

                                <br><b>🎯 2. ARAH STRATEGI & PENCEGAHAN TEMPORAL</b><br>
                                - <b>Program Wake Up Call Radio</b>: Pengoperasian kata sandi harian per shift di jam kritis.<br>
                                - <b>Manajemen Rest Area</b>: Pengaturan istirahat tidur minimal 1 jam di workshop/rest area.<br>
                                - <b>Inspeksi Fisik & Mental</b>: Pelaksanaan fatigue check acak pada shift 1 & 2.

                                <br><b>🚀 3. REKOMENDASI INTERVENSI PENGAWAS CCR/FMS</b><br>
                                Langkah intervensi cepat jika driver tidak merespon Wake Up Call atau terdeteksi fatigue valid.

                                Gunakan bahasa yang padat, lugas, langsung ke solusi, dan profesional.
                                """
                                st.session_state['res_jam'] = generate_gemini_analysis(user_api_key, prompt_jam_rawan)
                        
                        if st.session_state['res_jam']:
                            st.markdown(f"""
                            <div style="background:white; color:#0f172a; padding:20px; border-radius:16px; border-left:5px solid #2563eb; box-shadow:0 4px 15px rgba(0,0,0,0.05); line-height:1.6;">
                                {st.session_state['res_jam']}
                            </div>
                            """, unsafe_allow_html=True)
                
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
                        fig.update_traces(marker_color=colors_o, textposition='outside', textfont=dict(size=11, color='#0f172a', weight='bold'))
                        fig.update_layout(
                            plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
                            font=dict(family='Inter', size=12, color='#0f172a'),
                            title_font=dict(color='#0f172a'),
                            xaxis=dict(showgrid=False, tickangle=45, tickfont=dict(color='#0f172a')),
                            yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=1, range=[0, max_o_val * 1.25], tickfont=dict(color='#0f172a')),
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
            
            # ========== TAB 4: DRIVER & UNIT ==========
            with tab4:
                fig = plot_demografi(df_fatigue, df_overspeed, age_labels)
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
                            title='Top 10 Unit dengan Temuan Berulang', text='Total'
                        )
                        fig.update_traces(marker_color=colors_u, textposition='outside', textfont=dict(size=11, color='#0f172a', weight='bold'))
                        fig.update_layout(
                            plot_bgcolor='#ffffff', paper_bgcolor='#ffffff',
                            font=dict(family='Inter', size=11, color='#0f172a'),
                            title_font=dict(color='#0f172a'),
                            xaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=1, range=[0, max_u * 1.2], tickfont=dict(color='#0f172a')),
                            yaxis=dict(showgrid=False, tickfont=dict(color='#0f172a')),
                            margin=dict(l=20, r=20, t=40, b=20),
                            showlegend=False, height=450
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Tidak ada data unit")
                
                if user_api_key:
                    with st.expander("👤 Rekomendasi AI: Action Plan Driver & Disiplin (SOP BMT 011)", expanded=False):
                        if st.button("✨ Generate Strategy & Preventive Plan"):
                            with st.spinner("🧠 AI sedang menyusun action plan disiplin driver..."):
                                top_driver_fatigue = df_fatigue['Driver'].value_counts().head(5).to_dict()
                                
                                prompt_top_driver = f"""
                                Anda adalah Senior Safety Specialist operasional tambang PT. BMT.
                                Berdasarkan data driver dengan frekuensi fatigue terbanyak berikut: {top_driver_fatigue}

                                Susun ACTION PLAN DISIPLIN DRIVER yang patuh pada BMT-CHL-SOP 011 secara langsung tanpa basa-basi.

                                DILARANG MEMBUAT:
                                - Header Memorandum, pembuka formalitas, maupun tanda tangan di akhir.
                                - DILARANG MENGGUNAKAN TANDA BINTANG (*) SAMA SEKALI DALAM TEKS OUTPUT.

                                ATURAN SANKSI BERTINGKAT BMT 011:
                                - Batas Fatigue Valid: Maksimal 4x / minggu.
                                - Minggu 1 (4x fatigue): SP1 + Lubang 1.
                                - Minggu 2 (4x fatigue): SP2 + Lubang 2 + Dirumahkan 3 Hari + Pemanggilan Keluarga ke Office.
                                - Minggu 3 (4x fatigue): SP3 + Lubang 3.
                                - Sanksi Pengawas: Jika terjadi pembiaran fatigue driver, SIMPER/Mine Permit Pengawas dicabut PERMANEN.

                                LANGSUNG TAMPILKAN FORMAT BERIKUT (Gunakan tag HTML <b> untuk judul):

                                <b>📌 1. EVALUASI TINGKAT RISIKO & COMPLIANCE THRESHOLD</b><br>
                                Uraikan secara spesifik driver dari data ({top_driver_fatigue}) beserta jumlah kejadiannya. Evaluasi posisinya terhadap threshold 4x fatigue/minggu sesuai SOP BMT 011.

                                <br><b>🎯 2. ACTION PLAN TINDAK LANJUT DISIPLIN & SANKSI</b><br>
                                - <b>Penegakan Sanksi Bertingkat</b>: Rekomendasi penerbitan SP1/SP2/SP3 & Pemanggilan keluarga.<br>
                                - <b>Pemeriksaan Fit to Work</b>: Verifikasi jam tidur (<4 jam dilarang bekerja) & konsumsi obat.<br>
                                - <b>Prosedur Pengawalan Lapangan</b>: Prosedur penjemputan driver ke office oleh Safety Patrol & penyiapan driver spare.

                                <br><b>🚀 3. PENGAWASAN KEPADA PENGAWAS LAPANGAN</b><br>
                                Peringatan komitmen kepengawasan untuk mencegah pembiaran fatigue (Ancaman pencabutan SIMPER permanen).

                                Gunakan bahasa yang padat, lugas, langsung ke solusi, dan tegas.
                                """
                                st.session_state['res_driver'] = generate_gemini_analysis(user_api_key, prompt_top_driver)
                        
                        if st.session_state['res_driver']:
                            st.markdown(f"""
                            <div style="background:white; color:#0f172a; padding:20px; border-radius:16px; border-left:5px solid #2563eb; box-shadow:0 4px 15px rgba(0,0,0,0.05); line-height:1.6;">
                                {st.session_state['res_driver']}
                            </div>
                            """, unsafe_allow_html=True)

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
            
            # ========== TAB 5: DATA LOGS ==========
            with tab5:
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
                    cols_show = [cols['date'], cols['time'], 'Bulan', 'Week', 'Shift', 'Driver', 'Umur', 'Unit', 'Type', 'Lokasi']
                    cols_show = [c for c in cols_show if c in filtered.columns]
                    show = filtered[cols_show].copy()
                    show[cols['date']] = show[cols['date']].dt.strftime('%d-%m-%Y')
                    show = show.rename(columns={
                        cols['date']: 'Tanggal', cols['time']: 'Jam', 'Bulan': 'Bulan',
                        'Week': 'Week', 'Shift': 'Shift', 'Driver': 'Driver', 'Umur': 'Umur',
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
            
            # ========== TAB 6: ANALISIS LANJUTAN ==========
            with tab6:
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
                
                st.markdown("### ✅ Rekomendasi Otomatis (Compliance BMT & BIB)")
                
                recs = []
                if not df_fatigue.empty:
                    if 'Week' in df_fatigue.columns:
                        weekly_df = df_fatigue.groupby(['Driver', 'Week']).size().reset_index(name='Weekly_Count')
                        high_risk_rows = weekly_df[weekly_df['Weekly_Count'] >= 4]
                        if not high_risk_rows.empty:
                            top_risk = high_risk_rows.sort_values('Weekly_Count', ascending=False).iloc[0]
                            recs.append(("🔴 PRIORITAS HIGH", "🚨", f"Penegakan Sanksi BMT 011: Driver {top_risk['Driver']} mencapai {top_risk['Weekly_Count']} kasus di Week {top_risk['Week']} (SP1 + Lubang 1)"))
                    
                    shift_counts = df_fatigue['Shift'].value_counts()
                    if 'Shift 2' in shift_counts.index and 'Shift 1' in shift_counts.index:
                        ratio = shift_counts['Shift 2'] / shift_counts['Shift 1'] if shift_counts['Shift 1'] > 0 else 0
                        if ratio > 1.5:
                            recs.append(("🔴 PRIORITAS", "📻", f"Wake Up Call Radio (BIB 035): Intensifkan pemanggilan kata sandi jam 02.00–06.00 WITA"))
                    
                    jam_counts = df_fatigue['Jam_Range'].value_counts()
                    if not jam_counts.empty:
                        top_j = jam_counts.index[0]
                        if any(j in top_j for j in ['02:00', '03:00', '04:00', '05:00']):
                            recs.append(("🟡 PENTING", "☕", f"Istirahat Fleksibel: Puncak fatigue di jam sirkadian {top_j}. Instruksikan istirahat 1 jam di rest area"))
                    
                    unit_counts = df_fatigue['Unit'].value_counts()
                    if not unit_counts.empty and unit_counts.iloc[0] > 5:
                        recs.append(("🟡 PENTING", "🎥", f"Monitoring Live Streaming CCR (SOP BMT 011): Unit {unit_counts.index[0]} ({unit_counts.iloc[0]} temuan valid) wajib diprioritaskan"))
                
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
st.caption("© 2026 PT. Bumiputera Maha Terpercaya | DSMS Dashboard v3.0 (Patuh SOP BMT 011 & BIB 035)")
