import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
from io import BytesIO

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
    padding-top: 0.8rem;
    padding-bottom: 1.5rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    max-width: 1600px;
}

/* HEADER KOMPAK */
.header-compact {
    background: linear-gradient(135deg, #0f172a, #1d4ed8);
    padding: 12px 24px;
    border-radius: 14px;
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 15px rgba(0,0,0,0.10);
    margin-bottom: 18px;
    height: 80px;
}

/* KPI CARDS */
.kpi {
    background: white;
    padding: 16px 20px;
    border-radius: 14px;
    box-shadow: 0 4px 15px rgba(0,0,0,.06);
    transition: .25s;
    border: 1px solid #edf2f7;
    position: relative;
}
.kpi:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px rgba(0,0,0,.10);
}
.kpi-icon {
    font-size: 22px;
    margin-bottom: 4px;
}
.kpi-title {
    font-size: 12px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: .6px;
    font-weight: 500;
}
.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #0f172a;
    margin-top: 4px;
}
.kpi-footer {
    margin-top: 6px;
    font-size: 12px;
}

/* CHART CARDS */
.chart-card {
    background: white;
    border-radius: 16px;
    padding: 20px 20px 10px 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,.06);
    border: 1px solid #edf2f7;
    transition: .25s;
    margin-bottom: 16px;
}
.chart-card:hover {
    box-shadow: 0 8px 30px rgba(0,0,0,.10);
}
.chart-title {
    font-size: 14px;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #0f172a;
    padding-top: 0.5rem;
}
section[data-testid="stSidebar"] * {
    color: white;
}
.sidebar-menu {
    padding: 6px 12px;
    border-radius: 8px;
    margin: 2px 0;
    transition: .2s;
    cursor: pointer;
    font-size: 14px;
}
.sidebar-menu:hover {
    background: rgba(255,255,255,0.08);
}
.sidebar-menu.active {
    background: rgba(37,99,235,0.3);
    border-left: 3px solid #2563eb;
}

/* FILTER BAR */
.filter-bar {
    background: white;
    padding: 12px 20px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,.04);
    margin-bottom: 18px;
    border: 1px solid #edf2f7;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
}

/* SAFETY SCORE */
.safety-score {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,.06);
    border: 1px solid #edf2f7;
    display: flex;
    align-items: center;
    gap: 24px;
}
.safety-number {
    font-size: 48px;
    font-weight: 700;
    line-height: 1;
}
.safety-label {
    font-size: 14px;
    font-weight: 600;
    color: #0f172a;
}

/* RESPONSIVE GRID */
.stColumns {
    gap: 16px;
}

/* TYPOGRAPHY */
h1 { font-size: 28px !important; font-weight: 700 !important; }
h2 { font-size: 22px !important; font-weight: 600 !important; }
h3 { font-size: 18px !important; font-weight: 600 !important; }
.card-title { font-size: 14px !important; font-weight: 600 !important; }
.caption { font-size: 12px !important; color: #64748b; }

/* EMPTY STATE */
.empty-state {
    background: white;
    border-radius: 16px;
    padding: 60px 40px;
    text-align: center;
    border: 2px dashed #e2e8f0;
}
.empty-state-icon {
    font-size: 64px;
    margin-bottom: 16px;
}
.empty-state-title {
    font-size: 20px;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 8px;
}
.empty-state-desc {
    font-size: 14px;
    color: #64748b;
}

/* FOOTER */
.footer {
    margin-top: 32px;
    padding: 16px 24px;
    background: white;
    border-radius: 12px;
    border: 1px solid #edf2f7;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    font-size: 12px;
    color: #64748b;
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

def calculate_safety_score(df_fatigue, df_overspeed, df):
    """Hitung Safety Score berdasarkan faktor-faktor"""
    score = 100
    
    # Faktor 1: Fatigue (max -20)
    fatigue_pct = len(df_fatigue) / len(df) * 100 if len(df) > 0 else 0
    if fatigue_pct > 20:
        score -= 20
    elif fatigue_pct > 10:
        score -= 10
    elif fatigue_pct > 5:
        score -= 5
    
    # Faktor 2: Overspeed (max -15)
    overspeed_pct = len(df_overspeed) / len(df) * 100 if len(df) > 0 else 0
    if overspeed_pct > 15:
        score -= 15
    elif overspeed_pct > 8:
        score -= 10
    elif overspeed_pct > 3:
        score -= 5
    
    # Faktor 3: Repeat Driver (max -15)
    driver_counts = df_fatigue['Driver'].value_counts()
    repeat_drivers = sum(1 for count in driver_counts if count > 5)
    if repeat_drivers > 10:
        score -= 15
    elif repeat_drivers > 5:
        score -= 10
    elif repeat_drivers > 2:
        score -= 5
    
    # Faktor 4: Hotspot (max -10)
    if not df_fatigue.empty:
        loc_counts = df_fatigue['Lokasi'].value_counts()
        if not loc_counts.empty and loc_counts.iloc[0] > 10:
            score -= 10
        elif not loc_counts.empty and loc_counts.iloc[0] > 5:
            score -= 5
    
    return max(0, min(100, score))

def format_safety_score(score):
    if score >= 85:
        return "Excellent", "✅", "#22c55e"
    elif score >= 70:
        return "Good", "👍", "#3b82f6"
    elif score >= 55:
        return "Need Attention", "⚠️", "#f59e0b"
    else:
        return "Critical", "🚨", "#ef4444"

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
def kpi(title, value, footer, icon="📊", color="#2563eb", change=None):
    change_html = ""
    if change is not None:
        if change > 0:
            change_html = f'<span style="color:#22c55e;">▲ +{change:.1f}%</span>'
        elif change < 0:
            change_html = f'<span style="color:#ef4444;">▼ {change:.1f}%</span>'
        else:
            change_html = '<span style="color:#64748b;">→ 0%</span>'
    
    st.markdown(f"""
    <div class="kpi" style="border-top:4px solid {color};">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-footer">{change_html} vs bulan lalu</div>
    </div>
    """, unsafe_allow_html=True)

def executive_summary(items):
    st.markdown("### 📋 Executive Summary")
    for item in items:
        color = item.get('color', '#f8fafc')
        icon = item.get('icon', '•')
        text = item.get('text', '')
        st.markdown(f"""
        <div style="background:{color}; padding:10px 16px; border-radius:10px; margin-bottom:6px; border-left:4px solid {item.get('border', '#2563eb')};">
            <span style="font-size:14px;">{icon} {text}</span>
        </div>
        """, unsafe_allow_html=True)

def chart_card(title, chart, height=400):
    if chart is None:
        return
    
    st.markdown(f"""
    <div class="chart-card">
        <div class="chart-title">{title}</div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(chart, use_container_width=True, config={'displayModeBar': False})

# ==================== CHART FUNCTIONS ====================
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
        color_discrete_sequence=[color]
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=10))
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5, range=[0, max_val * 1.35]),
        hovermode='x unified',
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    
    for i, row in trend.iterrows():
        is_max = bool(row['Total'] == max_val)
        fig.add_annotation(
            x=row['Bulan'], y=row['Total'],
            text=f"🔥 {row['Total']}" if is_max else str(row['Total']),
            showarrow=is_max, arrowhead=1, arrowcolor=color,
            yshift=14 if is_max else 10,
            font=dict(size=12 if is_max else 11, weight='bold', color=color if is_max else '#0f172a'),
            bgcolor='#fee2e2' if is_max and color=='#ef4444' else ('#fef3c7' if is_max and color=='#f59e0b' else None),
            bordercolor=color if is_max else None, borderwidth=1 if is_max else 0
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
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        xaxis=dict(
            title="Minggu Ke- (Week)", showgrid=True, gridcolor='#edf2f7',
            dtick=1, rangeslider=dict(visible=True)
        ),
        yaxis=dict(title="Jumlah Temuan", showgrid=True, gridcolor='#e2e8f0'),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        margin=dict(l=20, r=20, t=50, b=20),
        height=400
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
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
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
        showlegend=False,
        height=400
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
        textfont=dict(size=11, weight='bold')
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
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        xaxis=dict(showgrid=False, tickangle=45),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5, range=[0, max_val * 1.35]),
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
        height=400
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
        showlegend=False,
        height=400
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
        title='Demografi Umur Driver (Rentang 5 Tahun)',
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Inter', size=12),
        xaxis=dict(showgrid=False, title="Rentang Umur (Tahun)"),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5),
        barmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
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
        showlegend=False,
        height=400
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
        return None, None
    
    monthly_data = df_fatigue.groupby('Month_Num').size().reset_index(name='Total')
    monthly_data = monthly_data.sort_values('Month_Num')
    
    if len(monthly_data) < 3:
        return None, None
    
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
    
    # Hitung confidence
    if len(y) > 1:
        y_pred = slope * x + intercept
        residuals = y - y_pred
        mse = np.mean(residuals ** 2)
        confidence = max(50, min(95, 95 - (mse / np.mean(y) * 10)))
    else:
        confidence = 85
    
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
        margin=dict(l=20, r=20, t=40, b=20),
        height=400
    )
    
    # Tentukan trend
    if len(predictions) >= 2 and len(y) >= 1:
        last_actual = y[-1]
        next_pred = predictions[0]
        if next_pred > last_actual * 1.05:
            trend = "Naik 🔺"
            need_action = "⚠️ Perlu tindakan"
        elif next_pred < last_actual * 0.95:
            trend = "Turun 🔻"
            need_action = "✅ Terkendali"
        else:
            trend = "Stabil ➡️"
            need_action = "📊 Monitor"
    else:
        trend = "Tidak tersedia"
        need_action = ""
    
    return fig, {'confidence': confidence, 'trend': trend, 'need_action': need_action}

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
        height=400
    )
    return fig

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:5px 0 15px 0;">
        <div style="font-size:36px;">🚛</div>
        <div style="font-weight:700; font-size:1.1rem; color:white;">FMS Dashboard</div>
        <div style="font-size:0.65rem; color:#94a3b8;">v4.0 · Enterprise</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar Menu
    menu_items = [
        ("📊", "Dashboard"),
        ("📈", "Overview"),
        ("👤", "Driver"),
        ("📍", "Lokasi"),
        ("🔮", "Forecast"),
        ("⚙️", "Settings"),
        ("📁", "Upload")
    ]
    
    for icon, label in menu_items:
        active = "active" if label == "Dashboard" else ""
        st.markdown(f"""
        <div class="sidebar-menu {active}">
            {icon} {label}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Upload section
    st.markdown("### 📁 Upload File")
    uploaded_file = st.file_uploader("Upload Log FMS", type=['xlsx', 'csv'])
    st.markdown("---")
    st.caption("© 2026 PT. Bumiputera")

# ==================== HEADER KOMPAK ====================
st.markdown("""
<div class="header-compact">
    <div>
        <h1 style="margin:0; font-size:28px; color:white;">🚛 Fleet Management System</h1>
        <p style="margin:2px 0 0 0; opacity:0.8; font-size:13px;">PT. Bumiputera Maha Terpercaya · Monitoring Safety Analytics</p>
    </div>
    <div style="display:flex; align-items:center; gap:12px;">
        <span style="font-size:13px; opacity:0.8;">📅 Last update: {}</span>
        <div style="background:white; padding:4px 12px; border-radius:10px;">
            <span style="color:#0f172a; font-weight:600; font-size:14px;">🚛</span>
        </div>
    </div>
</div>
""".format(datetime.now().strftime('%d/%m/%Y %H:%M')), unsafe_allow_html=True)

# ==================== MAIN ====================
if uploaded_file is None:
    # Empty State
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">🚛</div>
        <div class="empty-state-title">Upload File Excel</div>
        <div class="empty-state-desc">Drag & Drop atau Browse File untuk memulai</div>
        <div style="margin-top:16px; color:#94a3b8; font-size:12px;">Format: .xlsx atau .csv</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Preview cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background:white; padding:24px; border-radius:14px; text-align:center; border:1px solid #edf2f7;">
            <div style="font-size:32px;">📊</div>
            <div style="font-weight:600; color:#0f172a; font-size:14px;">Analisis Lengkap</div>
            <div style="font-size:12px; color:#64748b;">Tren fatigue, overspeed, performa</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:white; padding:24px; border-radius:14px; text-align:center; border:1px solid #edf2f7;">
            <div style="font-size:32px;">🗺️</div>
            <div style="font-weight:600; color:#0f172a; font-size:14px;">Spatial & Temporal</div>
            <div style="font-size:12px; color:#64748b;">Hotspot & pola waktu</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:white; padding:24px; border-radius:14px; text-align:center; border:1px solid #edf2f7;">
            <div style="font-size:32px;">👥</div>
            <div style="font-weight:600; color:#0f172a; font-size:14px;">Driver & Fleet</div>
            <div style="font-size:12px; color:#64748b;">Demografi & performa</div>
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
            
            # ========== GLOBAL FILTER ==========
            st.markdown("""
            <div class="filter-bar">
                <span style="font-weight:600; font-size:13px; color:#0f172a;">🔍 Filter Global</span>
            </div>
            """, unsafe_allow_html=True)
            
            f_col1, f_col2, f_col3, f_col4, f_col5, f_col6 = st.columns(6)
            with f_col1:
                filter_tanggal = st.date_input("Tanggal", value=None, key="filter_tanggal")
            with f_col2:
                filter_shift = st.selectbox("Shift", ["Semua", "Shift 1", "Shift 2"], key="filter_shift")
            with f_col3:
                filter_pengawas = st.selectbox("Pengawas", ["Semua"] + sorted(df['Pengawas'].unique().tolist()), key="filter_pengawas")
            with f_col4:
                filter_driver = st.selectbox("Driver", ["Semua"] + sorted(df['Driver'].unique().tolist()), key="filter_driver")
            with f_col5:
                filter_lokasi = st.selectbox("Lokasi", ["Semua"] + sorted(df['Lokasi'].unique().tolist()), key="filter_lokasi")
            with f_col6:
                filter_type = st.selectbox("Jenis Alarm", ["Semua", "Fatigue", "Overspeed"], key="filter_type")
            
            # Apply filters
            filtered_df = df.copy()
            if filter_tanggal:
                filtered_df = filtered_df[filtered_df[cols['date']].dt.date == filter_tanggal]
            if filter_shift != "Semua":
                filtered_df = filtered_df[filtered_df['Shift'] == filter_shift]
            if filter_pengawas != "Semua":
                filtered_df = filtered_df[filtered_df['Pengawas'] == filter_pengawas]
            if filter_driver != "Semua":
                filtered_df = filtered_df[filtered_df['Driver'] == filter_driver]
            if filter_lokasi != "Semua":
                filtered_df = filtered_df[filtered_df['Lokasi'] == filter_lokasi]
            if filter_type == "Fatigue":
                filtered_df = filtered_df[filtered_df['Type'].isin(['Mata Tertutup', 'Mengantuk'])]
            elif filter_type == "Overspeed":
                filtered_df = filtered_df[filtered_df['Type'] == 'Overspeed']
            
            # Update filtered data
            filtered_fatigue = filtered_df[filtered_df['Type'].isin(['Mata Tertutup', 'Mengantuk'])].copy()
            filtered_overspeed = filtered_df[filtered_df['Type'] == 'Overspeed'].copy()
            
            # ========== SAFETY SCORE ==========
            safety_score = calculate_safety_score(filtered_fatigue, filtered_overspeed, filtered_df)
            score_label, score_icon, score_color = format_safety_score(safety_score)
            
            st.markdown("### 🛡️ Safety Index")
            col_s1, col_s2 = st.columns([1, 3])
            with col_s1:
                st.markdown(f"""
                <div class="safety-score">
                    <div>
                        <div class="safety-number" style="color:{score_color};">{safety_score}</div>
                        <div class="safety-label">{score_icon} {score_label}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_s2:
                st.caption(f"""
                Score dihitung dari:
                • Fatigue ({len(filtered_fatigue)} kasus)
                • Overspeed ({len(filtered_overspeed)} kasus)
                • Repeat Driver
                • Hotspot
                """)
            
            st.markdown("---")
            
            # ========== KPI CARDS ==========
            # Calculate monthly changes
            if not filtered_fatigue.empty and len(filtered_fatigue) > 1:
                prev_month = filtered_fatigue['Month_Num'].max() - 1
                current_month = filtered_fatigue['Month_Num'].max()
                prev_count = len(filtered_fatigue[filtered_fatigue['Month_Num'] == prev_month])
                current_count = len(filtered_fatigue[filtered_fatigue['Month_Num'] == current_month])
                f_change = ((current_count - prev_count) / prev_count * 100) if prev_count > 0 else 0
            else:
                f_change = 0
            
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                kpi("🚨 Total Alarm", fmt_num(len(filtered_df)), "Semua jenis", "🚨", "#ef4444", 0)
            with c2:
                kpi("😴 Fatigue", fmt_num(len(filtered_fatigue)), "Kasus fatigue", "😴", "#f59e0b", f_change)
            with c3:
                kpi("🚗 Overspeed", fmt_num(len(filtered_overspeed)), "Kasus overspeed", "🚗", "#3b82f6", 0)
            with c4:
                loc_counts = filtered_fatigue['Lokasi'].value_counts()
                top_loc = loc_counts.index[0] if not loc_counts.empty else "N/A"
                top_loc_val = loc_counts.iloc[0] if not loc_counts.empty else 0
                kpi("📍 Hotspot", top_loc, f"{top_loc_val} kasus", "📍", "#8b5cf6", 0)
            
            st.markdown("---")
            
            # ========== EXECUTIVE SUMMARY ==========
            exec_items = []
            
            # Total alarm change
            if len(filtered_df) > 1:
                prev_month = filtered_df['Month_Num'].max() - 1
                current_month = filtered_df['Month_Num'].max()
                prev_total = len(filtered_df[filtered_df['Month_Num'] == prev_month])
                current_total = len(filtered_df[filtered_df['Month_Num'] == current_month])
                if prev_total > 0:
                    total_change = ((current_total - prev_total) / prev_total * 100)
                    if total_change < -5:
                        exec_items.append({"text": f"✅ Total Alarm turun {abs(total_change):.1f}%", "icon": "📉", "color": "#dcfce7", "border": "#22c55e"})
                    elif total_change > 5:
                        exec_items.append({"text": f"⚠️ Total Alarm naik {total_change:.1f}%", "icon": "📈", "color": "#fee2e2", "border": "#ef4444"})
            
            # Fatigue trend
            if not filtered_fatigue.empty and len(filtered_fatigue) > 1:
                prev_month = filtered_fatigue['Month_Num'].max() - 1
                current_month = filtered_fatigue['Month_Num'].max()
                prev_f = len(filtered_fatigue[filtered_fatigue['Month_Num'] == prev_month])
                current_f = len(filtered_fatigue[filtered_fatigue['Month_Num'] == current_month])
                if prev_f > 0:
                    f_change = ((current_f - prev_f) / prev_f * 100)
                    if f_change > 5:
                        exec_items.append({"text": f"🔴 Fatigue naik {f_change:.1f}%", "icon": "😴", "color": "#fee2e2", "border": "#ef4444"})
                    elif f_change < -5:
                        exec_items.append({"text": f"✅ Fatigue turun {abs(f_change):.1f}%", "icon": "😴", "color": "#dcfce7", "border": "#22c55e"})
            
            # Shift analysis
            if not filtered_fatigue.empty:
                shift_counts = filtered_fatigue['Shift'].value_counts()
                if 'Shift 2' in shift_counts.index and 'Shift 1' in shift_counts.index:
                    if shift_counts['Shift 2'] > shift_counts['Shift 1'] * 1.5:
                        exec_items.append({"text": "🌙 Shift 2 paling tinggi", "icon": "⚠️", "color": "#fef3c7", "border": "#f59e0b"})
            
            # Top driver
            if not filtered_fatigue.empty:
                top_driver = filtered_fatigue['Driver'].value_counts()
                if not top_driver.empty and top_driver.iloc[0] > 3:
                    exec_items.append({"text": f"👤 Driver {top_driver.index[0]} perlu coaching ({top_driver.iloc[0]} kasus)", "icon": "📌", "color": "#fee2e2", "border": "#ef4444"})
            
            # Hotspot
            if not filtered_fatigue.empty:
                loc_counts = filtered_fatigue['Lokasi'].value_counts()
                if not loc_counts.empty and loc_counts.iloc[0] > 5:
                    exec_items.append({"text": f"📍 Hotspot KM {loc_counts.index[0]} ({loc_counts.iloc[0]} kasus)", "icon": "🔥", "color": "#fef3c7", "border": "#f59e0b"})
            
            if exec_items:
                executive_summary(exec_items)
            else:
                st.success("✅ Tidak ada insight kritis saat ini")
            
            st.markdown("---")
            
            # ========== LAYOUT CHART 2x2 ==========
            st.markdown("### 📊 Dashboard Charts")
            
            # Row 1: Fatigue & Overspeed
            col1, col2 = st.columns(2)
            with col1:
                fig_f = plot_tren_generic(filtered_fatigue, title="📉 Tren Fatigue Bulanan", color="#ef4444")
                chart_card("Trend Fatigue", fig_f)
            
            with col2:
                fig_o = plot_tren_generic(filtered_overspeed, title="📉 Tren Overspeed Bulanan", color="#f59e0b")
                chart_card("Trend Overspeed", fig_o)
            
            # Row 2: Total Alarm & Shift Comparison
            col1, col2 = st.columns(2)
            with col1:
                fig_total = plot_tren_generic(filtered_df, title="📊 Total Alarm Bulanan", color="#2563eb")
                chart_card("Total Alarm", fig_total)
            
            with col2:
                fig_shift = plot_shift_comparison(filtered_fatigue)
                chart_card("Perbandingan Shift", fig_shift)
            
            st.markdown("---")
            
            # ========== HEATMAP FULL WIDTH ==========
            st.markdown("### 🗺️ Heatmap Driver Fatigue")
            hm_df = filtered_fatigue.copy()
            fig_heatmap = plot_heatmap(hm_df, order_months, 15)
            if fig_heatmap:
                chart_card("Heatmap Driver per Bulan", fig_heatmap)
            else:
                st.info("Tidak ada data untuk heatmap")
            
            st.markdown("---")
            
            # ========== TABS SISANYA ==========
            tab1, tab2, tab3, tab4 = st.tabs([
                "📍 Lokasi & Waktu",
                "👥 Driver & Unit",
                "📋 Data Logs",
                "🔮 Forecast"
            ])
            
            # ========== TAB 1: LOKASI & WAKTU ==========
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    fig_jam = plot_jam_distribution(filtered_fatigue, order_2h)
                    chart_card("Distribusi Jam Fatigue", fig_jam)
                
                with col2:
                    fig_hotspot_f = plot_hotspot(filtered_fatigue, "Fatigue")
                    chart_card("Top 10 Lokasi Fatigue", fig_hotspot_f)
                
                col3, col4 = st.columns(2)
                with col3:
                    fig_hotspot_o = plot_hotspot(filtered_overspeed, "Overspeed")
                    chart_card("Top 10 Lokasi Overspeed", fig_hotspot_o)
            
            # ========== TAB 2: DRIVER & UNIT ==========
            with tab2:
                fig_demo = plot_demografi(filtered_fatigue, filtered_overspeed, age_labels)
                chart_card("Demografi Umur Driver", fig_demo)
                
                col1, col2 = st.columns(2)
                with col1:
                    fig_driver = plot_top_driver(filtered_fatigue)
                    chart_card("Top 20 Driver Fatigue", fig_driver)
                
                with col2:
                    if not filtered_df.empty:
                        unit = filtered_df['Unit'].value_counts().head(10).reset_index()
                        unit.columns = ['Unit', 'Total']
                        unit = unit.sort_values('Total', ascending=True)
                        
                        max_u = unit['Total'].max()
                        colors_u = ['#1d4ed8' if v == max_u else '#3b82f6' for v in unit['Total']]
                        
                        fig_unit = px.bar(
                            unit, x='Total', y='Unit', orientation='h',
                            title='Top 10 Unit dengan Temuan', text='Total'
                        )
                        fig_unit.update_traces(marker_color=colors_u, textposition='outside', textfont=dict(size=11, weight='bold'))
                        fig_unit.update_layout(
                            plot_bgcolor='white', paper_bgcolor='white',
                            font=dict(family='Inter', size=11),
                            xaxis=dict(showgrid=True, gridcolor='#e2e8f0', gridwidth=0.5, range=[0, max_u * 1.2]),
                            yaxis=dict(showgrid=False),
                            margin=dict(l=20, r=20, t=40, b=20),
                            showlegend=False,
                            height=400
                        )
                        chart_card("Top 10 Unit dengan Temuan", fig_unit)
            
            # ========== TAB 3: DATA LOGS ==========
            with tab3:
                st.markdown("### 📋 Data Logs")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    search = st.text_input("🔍 Cari", placeholder="Driver / Unit / Lokasi")
                with col2:
                    f_month = st.selectbox("Bulan", ["Semua"] + [m for m in order_months if m in filtered_df['Bulan'].unique()])
                with col3:
                    f_type = st.selectbox("Jenis", ["Semua"] + list(filtered_df['Type'].unique()))
                with col4:
                    st.markdown("####")
                    download_all = st.button("📥 Download Excel", use_container_width=True)
                
                # Search filter
                search_df = filtered_df.copy()
                if search.strip():
                    s = search.strip().lower()
                    search_df = search_df[
                        search_df['Driver'].str.lower().str.contains(s, na=False) |
                        search_df['Unit'].str.lower().str.contains(s, na=False) |
                        search_df['Lokasi'].str.lower().str.contains(s, na=False)
                    ]
                if f_month != "Semua":
                    search_df = search_df[search_df['Bulan'] == f_month]
                if f_type != "Semua":
                    search_df = search_df[search_df['Type'] == f_type]
                
                st.caption(f"📊 {fmt_num(len(search_df))} baris data")
                
                if not search_df.empty:
                    cols_show = [cols['date'], cols['time'], 'Bulan', 'Week', 'Shift', 'Driver', 'Umur', 'Unit', 'Type', 'Lokasi']
                    cols_show = [c for c in cols_show if c in search_df.columns]
                    show = search_df[cols_show].copy()
                    show[cols['date']] = show[cols['date']].dt.strftime('%d-%m-%Y')
                    show = show.rename(columns={
                        cols['date']: 'Tanggal', cols['time']: 'Jam', 'Bulan': 'Bulan',
                        'Week': 'Week', 'Shift': 'Shift', 'Driver': 'Driver', 'Umur': 'Umur',
                        'Unit': 'Unit', 'Type': 'Jenis', 'Lokasi': 'Lokasi'
                    })
                    st.dataframe(show, use_container_width=True, hide_index=True, height=400)
                    
                    # Export options
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        csv = show.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name=f"fms_data_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime='text/csv'
                        )
                    with col2:
                        # Excel download
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            show.to_excel(writer, sheet_name='Data', index=False)
                        excel_data = output.getvalue()
                        st.download_button(
                            label="📥 Download Excel",
                            data=excel_data,
                            file_name=f"fms_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                    with col3:
                        st.metric("Jumlah Data", fmt_num(len(show)))
                else:
                    st.warning("Tidak ada data yang cocok")
            
            # ========== TAB 4: FORECAST ==========
            with tab4:
                st.markdown("### 🔮 Forecast & Prediksi")
                
                fig_forecast, forecast_data = plot_forecast(filtered_fatigue)
                if fig_forecast:
                    chart_card("Prediksi 3 Bulan ke Depan", fig_forecast)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Confidence", f"{forecast_data['confidence']:.0f}%")
                    with col2:
                        st.metric("Prediksi", forecast_data['trend'])
                    with col3:
                        st.metric("Status", forecast_data['need_action'])
                else:
                    st.warning("Data kurang dari 3 bulan untuk prediksi")
                
                st.markdown("---")
                
                # Recommendation Cards
                st.markdown("### ✅ Rekomendasi Prioritas")
                
                recs = []
                if not filtered_fatigue.empty:
                    top_d = filtered_fatigue['Driver'].value_counts()
                    if not top_d.empty and top_d.iloc[0] > 5:
                        recs.append(("🔴 PRIORITAS", "👤", f"Coaching Driver: {top_d.index[0]} ({top_d.iloc[0]} kasus)"))
                    
                    shift_counts = filtered_fatigue['Shift'].value_counts()
                    if 'Shift 2' in shift_counts.index and 'Shift 1' in shift_counts.index:
                        ratio = shift_counts['Shift 2'] / shift_counts['Shift 1'] if shift_counts['Shift 1'] > 0 else 0
                        if ratio > 2:
                            recs.append(("🟠 EVALUASI", "🌙", f"Shift Malam: {ratio:.1f}x lebih tinggi"))
                    
                    jam_counts = filtered_fatigue['Jam_Range'].value_counts()
                    if not jam_counts.empty:
                        top_j = jam_counts.index[0]
                        if any(j in top_j for j in ['02:00', '03:00', '04:00']):
                            recs.append(("🟡 INSPEKSI", "☕", f"Istirahat Terjadwal: Puncak jam {top_j}"))
                    
                    unit_counts = filtered_df['Unit'].value_counts()
                    if not unit_counts.empty and unit_counts.iloc[0] > 5:
                        recs.append(("🟢 MONITOR", "🚗", f"Inspeksi Unit: {unit_counts.index[0]}"))
                
                if recs:
                    for rec in recs:
                        bg = '#fef2f2' if 'PRIORITAS' in rec[0] else ('#fffbeb' if 'EVALUASI' in rec[0] else ('#fefce8' if 'INSPEKSI' in rec[0] else '#f0fdf4'))
                        border = '#ef4444' if 'PRIORITAS' in rec[0] else ('#f59e0b' if 'EVALUASI' in rec[0] else ('#eab308' if 'INSPEKSI' in rec[0] else '#22c55e'))
                        st.markdown(f"""
                        <div style="background:{bg}; padding:12px 16px; border-radius:10px; border-left:5px solid {border}; margin:6px 0;">
                            <span style="font-weight:600; font-size:14px;">{rec[0]}</span> 
                            <span style="font-size:18px;">{rec[1]}</span> 
                            <span style="font-size:13px; color:#1e293b;">{rec[2]}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ Tidak ada rekomendasi prioritas saat ini")
            
            st.sidebar.success(f"✅ {fmt_num(len(filtered_df))} data valid")

        except Exception as e:
            st.error(f"❌ Error saat memproses data: {str(e)}")
            with st.expander("🔍 Detail Traceback"):
                import traceback
                st.code(traceback.format_exc())

# ==================== FOOTER ====================
st.markdown("""
<div class="footer">
    <span>🚛 Dashboard v4.0</span>
    <span>Last Update: {}</span>
    <span>Developer: FMS Team</span>
    <span>Version: 4.0.1</span>
    <span>Data Source: Live Database</span>
    <span>© 2026 PT. Bumiputera Maha Terpercaya</span>
</div>
""".format(datetime.now().strftime('%d/%m/%Y %H:%M')), unsafe_allow_html=True)
