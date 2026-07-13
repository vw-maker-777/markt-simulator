import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Streamlit Setup ---
st.set_page_config(page_title="Marktpsychologie-Simulator", layout="wide")
st.title("🧠 Marktpsychologie-Simulator")
st.markdown("Stelle die Parameter der Marktteilnehmer ein und beobachte, wie sich Kurs und Volatilität entwickeln.")

# --- Sidebar: Parameter ---
st.sidebar.header("⚙️ Agenten-Parameter")

# Privatanleger
st.sidebar.subheader("1. Privatanleger (Retail)")
retail_start = st.sidebar.slider("Start-Aktienquote", 0.0, 1.0, 0.6, 0.05)
retail_gier_schwelle = st.sidebar.slider("Gier-Schwelle (Tagesrendite)", 0.01, 0.10, 0.03, 0.01)
retail_panik_schwelle = st.sidebar.slider("Panik-Schwelle (Tagesrendite)", -0.15, -0.01, -0.05, 0.01)
retail_panik_verkauf = st.sidebar.slider("Panik-Verkaufsrate (pro Tag)", 0.1, 0.5, 0.3, 0.05)
retail_gier_kauf = st.sidebar.slider("Gier-Kaufrate (pro Tag)", 0.05, 0.3, 0.1, 0.02)

# Institutionelle Fonds
st.sidebar.subheader("2. Institutionelle Fonds")
fund_start = st.sidebar.slider("Start-Aktienquote", 0.0, 1.5, 0.8, 0.05)
fund_leverage_limit = st.sidebar.slider("Maximaler Hebel", 1.0, 2.0, 1.1, 0.1)
fund_vix_threshold = st.sidebar.slider("VIX-Schwelle für Abflüsse", 20, 60, 30, 5)
fund_abfluss_rate = st.sidebar.slider("Abflussrate bei VIX-Überschreitung", 0.05, 0.5, 0.2, 0.05)

# HFT / Market Maker
st.sidebar.subheader("3. HFT / Market Maker")
hft_capital = st.sidebar.number_input("Kapital (Volume)", 1000, 50000, 10000, 1000)
hft_vix_abs_schaltung = st.sidebar.slider("VIX-Schwelle für Abschaltung", 30, 80, 40, 5)

# Zentralbank
st.sidebar.subheader("4. Zentralbank")
cb_intervention_schwelle = st.sidebar.slider("Interventions-Schwelle (Kursverlust in 5 Tagen)", 0.05, 0.30, 0.15, 0.02)
cb_kauf_volumen = st.sidebar.slider("QE-Kaufvolumen (% des Marktes)", 0.01, 0.10, 0.05, 0.01)
cb_vola_reduktion = st.sidebar.slider("Vola-Reduktion nach QE (%)", 0.2, 0.8, 0.30, 0.05)

# Allgemeine Marktparameter
st.sidebar.subheader("5. Marktumfeld")
schock_volatilitaet = st.sidebar.slider("Tägliche Schock-Volatilität (%)", 0.5, 5.0, 1.0, 0.5) / 100
schock_wahrscheinlichkeit = st.sidebar.slider("Wahrscheinlichkeit großer Schocks (%)", 0.5, 10.0, 2.0, 0.5) / 100
tage = st.sidebar.slider("Simulations-Tage", 100, 2000, 500, 50)

# --- Simulations-Funktion ---
def run_simulation(
    tage,
    retail_start, retail_gier_schwelle, retail_panik_schwelle, retail_panik_verkauf, retail_gier_kauf,
    fund_start, fund_leverage_limit, fund_vix_threshold, fund_abfluss_rate,
    hft_capital, hft_vix_abs_schaltung,
    cb_intervention_schwelle, cb_kauf_volumen, cb_vola_reduktion,
    schock_volatilitaet, schock_wahrscheinlichkeit
):
    
    price = 100.0
    vix = 18.0
    prices = [price]
    vix_history = [vix]
    
    retail_quote = retail_start
    fund_quote = fund_start
    hft_active = True
    
    volume_retail = 100
    volume_fund = 1000
    
    retail_quotes = [retail_quote]
    fund_quotes = [fund_quote]
    hft_active_history = [1]
    
    for day in range(tage):
        
        if np.random.rand() < schock_wahrscheinlichkeit:
            shock = np.random.normal(-0.05, 0.02)
        else:
            shock = np.random.normal(0, schock_volatilitaet)
        
        if len(prices) >= 5:
            ret_5d = (prices[-1] - prices[-5]) / prices[-5]
        else:
            ret_5d = 0
        
        if ret_5d < retail_panik_schwelle:
            retail_quote = max(0, retail_quote - retail_panik_verkauf)
        elif ret_5d > retail_gier_schwelle:
            retail_quote = min(1, retail_quote + retail_gier_kauf)
        else:
            retail_quote += 0.02 * (0.6 - retail_quote)
        
        flows = 0
        if vix > fund_vix_threshold:
            flows = -fund_abfluss_rate
        
        if ret_5d > 0.05:
            fund_quote = min(fund_leverage_limit, fund_quote + 0.05)
        elif ret_5d < -0.05:
            fund_quote = max(0.4, fund_quote - 0.1)
        else:
            fund_quote += 0.01 * (0.8 - fund_quote)
        
        fund_volume = volume_fund * (1 + flows)
        fund_volume = max(0, fund_volume)
        
        vix_dec = vix / 100
        if vix_dec > hft_vix_abs_schaltung / 100:
            hft_active = False
            hft_volume = 0
        else:
            hft_active = True
            hft_volume = int(hft_capital / (vix_dec ** 2 + 0.001))
            hft_volume = max(100, hft_volume)
        
        retail_net = (retail_quote - retail_start) * volume_retail
        fund_net = (fund_quote - fund_start) * fund_volume
        
        if hft_active:
            liquidity = hft_volume
        else:
            liquidity = 0
        
        net_demand = retail_net + fund_net
        if liquidity > 0:
            price_change = net_demand / (liquidity + 1000)
        else:
            if net_demand < 0:
                price_change = -0.04
            else:
                price_change = 0
        
        price_change += shock
        price = price * (1 + price_change)
        price = max(1, price)
        prices.append(price)
        
        vix = 15 + np.abs(price_change) * 500 + np.random.normal(0, 2)
        vix = max(10, min(80, vix))
        vix_history.append(vix)
        
        if len(prices) >= 5:
            drop_5d = (prices[-5] - prices[-1]) / prices[-5]
            if drop_5d > cb_intervention_schwelle:
                price = price * (1 + cb_kauf_volumen)
                prices[-1] = price
                vix = vix * (1 - cb_vola_reduktion)
                vix_history[-1] = vix
        
        retail_quotes.append(retail_quote)
        fund_quotes.append(fund_quote)
        hft_active_history.append(1 if hft_active else 0)
    
    return prices, vix_history, retail_quotes, fund_quotes, hft_active_history

# --- Hauptbereich ---
if st.button("🚀 Simulation neu starten", type="primary"):
    with st.spinner("Simuliere Marktverhalten..."):
        prices, vix_history, retail_quotes, fund_quotes, hft_active_history = run_simulation(
            tage,
            retail_start, retail_gier_schwelle, retail_panik_schwelle, retail_panik_verkauf, retail_gier_kauf,
            fund_start, fund_leverage_limit, fund_vix_threshold, fund_abfluss_rate,
            hft_capital, hft_vix_abs_schaltung,
            cb_intervention_schwelle, cb_kauf_volumen, cb_vola_reduktion,
            schock_volatilitaet, schock_wahrscheinlichkeit
        )
        
        st.success("Simulation abgeschlossen!")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Startkurs", f"{prices[0]:.2f}")
        col2.metric("Endkurs", f"{prices[-1]:.2f}")
        col3.metric("Gesamtrendite", f"{(prices[-1]/prices[0]-1)*100:.1f} %")
        col4.metric("Max. VIX", f"{max(vix_history):.1f}")
        
        st.subheader("📈 Kurs- und VIX-Verlauf")
        fig, ax = plt.subplots(2, 1, figsize=(12, 8))
        ax[0].plot(prices, label="Aktienkurs", color="blue", linewidth=1.5)
        ax[0].set_ylabel("Kurs")
        ax[0].legend()
        ax[0].grid(True)
        
        ax[1].plot(vix_history, label="VIX (Volatilität)", color="orange", linewidth=1.5)
        ax[1].axhline(y=30, color="red", linestyle="--", label="Panik-Schwelle")
        ax[1].axhline(y=15, color="green", linestyle="--", label="Ruhe-Schwelle")
        ax[1].set_ylabel("VIX")
        ax[1].legend()
        ax[1].grid(True)
        st.pyplot(fig)
        
        st.subheader("🤖 Agenten-Verhalten (Aktienquoten)")
        fig2, ax2 = plt.subplots(figsize=(12, 5))
        ax2.plot(retail_quotes, label="Privatanleger", color="green", linewidth=1.5)
        ax2.plot(fund_quotes, label="Institutionelle Fonds", color="red", linewidth=1.5)
        ax2.plot(hft_active_history, label="HFT aktiv (1=ja, 0=nein)", color="purple", linewidth=1, linestyle="--")
        ax2.set_ylabel("Aktienquote / Aktivität")
        ax2.set_xlabel("Tage")
        ax2.legend()
        ax2.grid(True)
        st.pyplot(fig2)
        
        st.subheader("📊 Renditeverteilung (Fat Tails)")
        returns = [ (prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices)) ]
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        ax3.hist(returns, bins=50, color="blue", alpha=0.7)
        ax3.set_xlabel("Tägliche Rendite")
        ax3.set_ylabel("Häufigkeit")
        ax3.set_title("Die Verteilung zeigt 'Fat Tails' (extreme Ausreißer)")
        st.pyplot(fig3)
        
        st.subheader("📋 Marktphasen-Statistik")
        df = pd.DataFrame({
            "Tag": range(len(prices)),
            "Kurs": prices,
            "VIX": vix_history,
            "Retail Quote": retail_quotes,
            "Fonds Quote": fund_quotes,
            "HFT aktiv": hft_active_history
        })
        
        df["Phase"] = "Normal"
        df.loc[df["VIX"] < 15, "Phase"] = "🟢 Ruhe (Contango)"
        df.loc[df["VIX"] > 30, "Phase"] = "🔴 Panik (Crash)"
        df.loc[df["VIX"] > 50, "Phase"] = "⛔ Flash-Crash (Illiquidität)"
        
        phase_counts = df["Phase"].value_counts()
        st.bar_chart(phase_counts)
        
st.subheader("📊 Letzte 50 Tage (Detail)")
# Daten für die Tabelle vorbereiten
display_df = df.tail(50).copy()
display_df["Kurs"] = display_df["Kurs"].apply(lambda x: f"{x:.2f}")
display_df["VIX"] = display_df["VIX"].apply(lambda x: f"{x:.1f}")

# Farben für die VIX-Spalte hinzufügen
def highlight_vix(val):
    try:
        vix_val = float(val)
        if vix_val > 30:
            return "background-color: #ffcccc"
        elif vix_val < 15:
            return "background-color: #ccffcc"
    except:
        pass
    return ""
    
        st.dataframe(display_df.style.applymap(highlight_vix, subset=["VIX"]))
    else:
        st.info("👈 Stelle die Parameter in der Sidebar ein und klicke auf 'Simulation neu starten'.")
