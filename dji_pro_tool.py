import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN DE LA UI ---
st.set_page_config(page_title="DJI Pro Inversor", layout="wide")
st.title("🦅 DJI Pro: Terminal de Inversión Estratégica")

# --- BARRA LATERAL (PARÁMETROS) ---
st.sidebar.header("🔧 Configuración de Estrategia")
capital_total = st.sidebar.number_input("Capital Inicial ($)", value=50000)
trigger_caida = st.sidebar.slider("Gatillo de Compra (% caída)", 1.0, 5.0, 3.0) / 100
multiplicador = st.sidebar.selectbox("Multiplicador en caída", [2, 3, 4, 5], index=1)
profit_target = st.sidebar.slider("Toma de Ganancia (% PnL)", 5.0, 15.0, 8.0) / 100
cash_yield = st.sidebar.slider("Interés sobre Efectivo (APR %)", 0.0, 7.0, 5.0) / 100

# --- CONEXIÓN A YAHOO FINANCE ---
@st.cache_data
def fetch_dji_data():
    # Descargamos el Dow Jones (^DJI)
    ticker = yf.Ticker("^DJI")
    # Traemos datos desde 2015 hasta la fecha actual
    df = ticker.history(start="2015-01-01", interval="1mo")
    return df

with st.spinner('Obteniendo datos reales de Yahoo Finance...'):
    data = fetch_dji_data()
    prices = data['Close'].tolist()
    dates = data.index.tolist()

# --- MOTOR DE LA ESTRATEGIA ---
def simulate():
    num_months = len(prices)
    monthly_base = capital_total / num_months
    cash = capital_total
    shares = 0
    invested_basis = 0
    history = []

    for i, price in enumerate(prices):
        # 1. Yield del efectivo
        cash *= (1 + cash_yield / 12)
        
        # 2. Análisis de caída
        monthly_ret = (price - prices[i-1]) / prices[i-1] if i > 0 else 0
        is_dip = monthly_ret <= -trigger_caida
        
        # 3. Compra DCA
        buy_amt = monthly_base * multiplicador if is_dip else monthly_base
        actual_buy = min(buy_amt, cash)
        shares += actual_buy / price
        cash -= actual_buy
        invested_basis += actual_buy
        
        # 4. Profit Taking (Venta parcial)
        equity = shares * price
        if invested_basis > 0 and (equity/invested_basis - 1) > profit_target:
            surplus = equity - (invested_basis * (1 + profit_target))
            shares -= surplus / price
            invested_basis -= surplus * (invested_basis / (shares + (surplus/price)))
            cash += surplus
            
        # 5. Rebalanceo 80/20
        equity = shares * price
        total_val = cash + equity
        target_eq = total_val * 0.8
        adj = target_eq - equity
        
        if adj > 0: # Comprar para equilibrar
            v = min(adj, cash)
            shares += v / price
            cash -= v
            invested_basis += v
        else: # Vender para equilibrar
            v = abs(adj)
            shares_sold = v / price
            invested_basis -= shares_sold * (invested_basis / shares) if shares > 0 else 0
            shares -= shares_sold
            cash += v

        history.append({
            "Fecha": dates[i],
            "Precio": price,
            "Total": cash + (shares * price),
            "Efectivo": cash,
            "Acciones": shares * price,
            "Dip": is_dip
        })
    return pd.DataFrame(history)

df_results = simulate()

# --- DASHBOARD ---
# Métricas principales
m1, m2, m3 = st.columns(3)
final_v = df_results['Total'].iloc[-1]
m1.metric("Patrimonio Actual", f"${final_v:,.2f}", f"{((final_v/capital_total)-1)*100:.2f}%")
m2.metric("Efectivo en Reserva", f"${df_results['Efectivo'].iloc[-1]:,.2f}")
m3.metric("Último Precio DJI", f"${prices[-1]:,.2f}")

# Gráfica Interactiva de Crecimiento
st.subheader("Evolución del Portafolio vs Inversión")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_results['Fecha'], y=df_results['Total'], name="Valor Total", fill='tozeroy', line=dict(color='#2ecc71')))
fig.add_trace(go.Scatter(x=df_results['Fecha'], y=df_results['Acciones'], name="Valor en Acciones", line=dict(color='#3498db')))
fig.update_layout(hovermode="x unified", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# Señales de Mercado
st.subheader("Análisis de Oportunidades (Gatillos)")
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df_results['Fecha'], y=df_results['Precio'], name="Precio DJI", line=dict(color='white', width=1)))
dips = df_results[df_results['Dip']]
fig2.add_trace(go.Scatter(x=dips['Fecha'], y=dips['Precio'], mode='markers', name="Gatillo 3% Activado", marker=dict(color='red', size=8)))
fig2.update_layout(template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

st.success(f"Simulación completada con datos de Yahoo Finance hasta hoy: {datetime.now().strftime('%d/%m/%Y')}")

# Guardar resultados para el backup
df_results.to_csv("ultimo_analisis.csv", index=False)
st.info("✅ Datos locales actualizados para el backup.")