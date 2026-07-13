import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Streamlit Setup ---
st.set_page_config(page_title="Marktpsychologie-Simulator", layout="wide")
st.title("🧠 Marktpsychologie-Simulator")
st.markdown("Stelle die Parameter ein, wähle ein vorgefertigtes Szenario oder klicke auf 'Simulation neu starten'.")

# --- Sidebar: Parameter ---
st.sidebar.header("⚙️ Agenten-Parameter")

# Dropdown für Szenarien
scenario = st.sidebar.selectbox(
    "📂 Wähle ein vorgefertigtes Szenario",
    ("Benutzerdefiniert (Manuell)", 
     "1. Reiner Panik-Crash (HFTs schalten ab)", 
     "2. Allmächtige Zentralbank (Fed-Put)", 
     "3. Leverage-Zyklus der Fonds", 
     "4. Perfektes Contango (Ruhe)")
)

# Szenario-Logik
if scenario == "1. Reiner Panik-Crash (HFTs schalten ab)":
    st.session_state["hft_vix"] = 25
    st.session_state["panic_sell"] = 0.40
    st.session_state["cb_intervention"] = 0.30
    st.session_state["fund_leverage"] = 1.50
    st.session_state["retail_start"] = 0.60
elif scenario == "2. Allmächtige Zentralbank (Fed-Put)":
    st.session_state["hft_vix"] = 50
    st.session_state["panic_sell"] = 0.20
    st.session_state["cb_intervention"] = 0.05
    st.session_state["fund_leverage"] = 1.10
    st.session_state["retail_start"] = 0.80
elif scenario == "3. Leverage-Zyklus der Fonds":
    st.session_state["hft_vix"] = 50
    st.session_state["panic_sell"] = 0.20
    st.session_state["cb_intervention"] = 0.15
    st.session_state["fund_leverage"] = 1.50
    st.session_state["retail_start"] = 0.60
elif scenario == "4. Perfektes Contango (Ruhe)":
    st.session_state["hft_vix"] = 60
    st.session_state["panic_sell"] = 0.05
    st.session_state["cb_intervention"] = 0.25
    st.session_state["fund_leverage"] = 0.90
    st.session_state["retail_start"] = 0.75
    st.session_state["schock_volatility"] = 0.20
    st.session_state["schock_prob"] = 0.20
else:
    st.session_state.setdefault("hft_vix", 40)
    st.session_state.setdefault("panic_sell", 0.30)
    st.session_state.setdefault("cb_intervention", 0.15)
    st.session_state.setdefault("fund_leverage", 1.10)
    st.session_state.setdefault("retail_start", 0.60)
    st.session_state.setdefault("schock_volatility", 1.0)
    st.session_state.setdefault("schock_prob", 2.0)

# --- 1. PRIVATANLEGER ---
st.sidebar.subheader("1. 🟢 Privatanleger (Retail)")

retail_start = st.sidebar.slider("Start-Aktienquote", 0.0, 1.0, st.session_state.retail_start, 0.05)
if retail_start < 0.3: st.sidebar.caption("📌 *Sehr defensiv: Kaum Aktien im Depot.*")
elif retail_start < 0.6: st.sidebar.caption("📌 *Ausgewogen: Klassischer Misch-Ansatz.*")
elif retail_start < 0.9: st.sidebar.caption("📌 *Optimistisch: Hohe Aktienquote, viel Risiko.*")
else: st.sidebar.caption("📌 *Maximal riskant: Fast 100% in Aktien.*")

retail_gier_schwelle = st.sidebar.slider("Gier-Schwelle (Tagesrendite)", 0.01, 0.10, 0.03, 0.01)
st.sidebar.caption(f"📌 *Erst ab +{retail_gier_schwelle*100:.1f}% Tagesrendite kaufen sie aggressiv zu.*")

retail_panik_schwelle = st.sidebar.slider("Panik-Schwelle (Tagesrendite)", -0.15, -0.01, -0.05, 0.01)
st.sidebar.caption(f"📌 *Bei -{abs(retail_panik_schwelle)*100:.1f}% Verlust am Tag geraten sie in Panik.*")

retail_panik_verkauf = st.sidebar.slider("Panik-Verkaufsrate (pro Tag)", 0.1, 0.5, st.session_state.panic_sell, 0.05)
if retail_panik_verkauf < 0.15: st.sidebar.caption("📌 *Gelassen: Sie halten auch in Krisen ihre Aktien.*")
elif retail_panik_verkauf < 0.30: st.sidebar.caption("📌 *Normal: Verkaufen angemessen bei Panik.*")
else: st.sidebar.caption("📌 *Hektisch: Bei Panik wird alles verkauft – verschärft den Crash!*")

retail_gier_kauf = st.sidebar.slider("Gier-Kaufrate (pro Tag)", 0.05, 0.3, 0.1, 0.02)
if retail_gier_kauf < 0.10: st.sidebar.caption("📌 *Vorsichtig: Kaufen langsam zu.*")
else: st.sidebar.caption("📌 *Gierig: Kaufen aggressiv in Rallyes – treibt Blasen.*")

# --- 2. INSTITUTIONELLE FONDS ---
st.sidebar.subheader("2. 🔴 Institutionelle Fonds")

fund_start = st.sidebar.slider("Start-Aktienquote", 0.0, 1.5, st.session_state.fund_leverage, 0.05)
if fund_start < 1.0: st.sidebar.caption("📌 *Konservativ: Kein Hebel, kaum Zwangsverkäufe.*")
elif fund_start < 1.3: st.sidebar.caption("📌 *Leicht gehebelt: Moderate Risiken.*")
else: st.sidebar.caption("📌 *Stark gehebelt: Hohe Gewinne, aber bei Crash muss massiv verkauft werden!*")

fund_leverage_limit = st.sidebar.slider("Maximaler Hebel", 1.0, 2.0, 1.1, 0.1)
if fund_leverage_limit < 1.2: st.sidebar.caption("📌 *Sicher: Keine gefährlichen Hebel.*")
elif fund_leverage_limit < 1.5: st.sidebar.caption("📌 *Moderat: Etwas Risiko für mehr Rendite.*")
else: st.sidebar.caption("📌 *Riskant: Hoher Hebel kann zu Kettenreaktionen führen.*")

fund_vix_threshold = st.sidebar.slider("VIX-Schwelle für Abflüsse", 20, 60, 30, 5)
st.sidebar.caption(f"📌 *Bei einem VIX über {fund_vix_threshold} ziehen Großkunden ihr Geld ab – Fonds müssen dann zwangsverkaufen.*")

fund_abfluss_rate = st.sidebar.slider("Abflussrate bei VIX-Überschreitung", 0.05, 0.5, 0.2, 0.05)
if fund_abfluss_rate < 0.15: st.sidebar.caption("📌 *Geduldige Kunden: Wenig Geldabfluss.*")
else: st.sidebar.caption("📌 *Panische Kunden: Massiver Geldabzug, der den Crash verstärkt.*")

# --- 3. HFT / MARKET MAKER ---
st.sidebar.subheader("3. 🟣 HFT / Market Maker")

hft_capital = st.sidebar.number_input("Kapital (Volume)", 1000, 50000, 10000, 1000)
if hft_capital < 5000: st.sidebar.caption("📌 *Geringe Liquidität: Markt ist oft ausgetrocknet.*")
else: st.sidebar.caption("📌 *Hohe Liquidität: HFTs versorgen den Markt mit Geld.*")

hft_vix_abs_schaltung = st.sidebar.slider("VIX-Schwelle für Abschaltung", 20, 80, st.session_state.hft_vix, 5)
if hft_vix_abs_schaltung < 30: st.sidebar.caption("📌 *Frühe Abschaltung: HFTs verschwinden bei leichter Panik → Flash-Crash-Gefahr!*")
elif hft_vix_abs_schaltung < 50: st.sidebar.caption("📌 *Normale Abschaltung: Bei großer Panik schalten sie ab.*")
else: st.sidebar.caption("📌 *Robust: HFTs bleiben auch in schweren Krisen aktiv – sehr stabil.*")

# --- 4. ZENTRALBANK ---
st.sidebar.subheader("4. 🏦 Zentralbank")

cb_intervention_schwelle = st.sidebar.slider("Interventions-Schwelle (Kursverlust)", 0.05, 0.30, st.session_state.cb_intervention, 0.02)
if cb_intervention_schwelle < 0.10: st.sidebar.caption("📌 *Aktive Notenbank: Greift bei kleinsten Verlusten ein – starke Stützung.*")
elif cb_intervention_schwelle < 0.20: st.sidebar.caption("📌 *Abwartend: Greift bei moderaten Verlusten ein.*")
else: st.sidebar.caption("📌 *Passiv: Greift erst bei schweren Crashs ein – viel Leid vorher.*")

cb_kauf_volumen = st.sidebar.slider("QE-Kaufvolumen (% des Marktes)", 0.01, 0.10, 0.05, 0.01)
if cb_kauf_volumen < 0.04: st.sidebar.caption("📌 *Kleine Rettungspakete: Schwacher Effekt auf den Kurs.*")
else: st.sidebar.caption("📌 *Große Rettungspakete: Starke Kurssprünge nach Eingriff.*")

cb_vola_reduktion = st.sidebar.slider("Vola-Reduktion nach QE (%)", 0.2, 0.8, 0.30, 0.05)
if cb_vola_reduktion < 0.4: st.sidebar.caption("📌 *Geringe Beruhigung: Die Angst bleibt hoch.*")
else: st.sidebar.caption("📌 *Starke Beruhigung: VIX fällt drastisch nach Rettung.*")

# --- 5. MARKTUMFELD ---
st.sidebar.subheader("5. 🌍 Marktumfeld")

schock_volatilitaet = st.sidebar.slider("Tägliche Schock-Volatilität (%)", 0.5, 5.0, st.session_state.schock_volatility, 0.5) / 100
if schock_volatilitaet*100 < 1.5: st.sidebar.caption("📌 *Ruhiges Umfeld: Wenig überraschende Kurssprünge.*")
elif schock_volatilitaet*100 < 3.0: st.sidebar.caption("📌 *Normales Umfeld: Moderate tägliche Schwankungen.*")
else: st.sidebar.caption("📌 *Stürmisch: Sehr hohe tägliche Ausschläge – der Markt zittert.*")

schock_wahrscheinlichkeit = st.sidebar.slider("Wahrscheinlichkeit großer Schocks (%)", 0.5, 10.0, st.session_state.schock_prob, 0.5) / 100
if schock_wahrscheinlichkeit*100 < 2.0: st.sidebar.caption("📌 *Seltene Krisen: Keine großen Überraschungen.*")
elif schock_wahrscheinlichkeit*100 < 5.0: st.sidebar.caption("📌 *Gelegentliche Krisen: Ab und zu ein Crash.*")
else: st.sidebar.caption("📌 *Häufige Panik: Ständige Schocks.*")

tage = st.sidebar.slider("Simulations-Tage", 100, 2000, 500, 50)
st.sidebar.caption(f"📌 *Simuliert {tage} Handelstage (ca. {tage/250:.1f} Jahre).*")

# --- Simulations-Funktion ---
def run_simulation(**kwargs):
    tage = kwargs.get('tage', 500)
    retail_start = kwargs.get('retail_start', 0.6)
    retail_gier_schwelle = kwargs.get('retail_gier_schwelle', 0.03)
    retail_panik_schwelle = kwargs.get('retail_panik_schwelle', -0.05)
    retail_panik_verkauf = kwargs.get('retail_panik_verkauf', 0.3)
    retail_gier_kauf = kwargs.get('retail_gier_kauf', 0.1)
    fund_start = kwargs.get('fund_start', 1.1)
    fund_leverage_limit = kwargs.get('fund_leverage_limit', 1.1)
    fund_vix_threshold = kwargs.get('fund_vix_threshold', 30)
    fund_abfluss_rate = kwargs.get('fund_abfluss_rate', 0.2)
    hft_capital = kwargs.get('hft_capital', 10000)
    hft_vix_abs_schaltung = kwargs.get('hft_vix_abs_schaltung', 40)
    cb_intervention_schwelle = kwargs.get('cb_intervention_schwelle', 0.15)
    cb_kauf_volumen = kwargs.get('cb_kauf_volumen', 0.05)
    cb_vola_reduktion = kwargs.get('cb_vola_reduktion', 0.3)
    schock_volatilitaet = kwargs.get('schock_volatilitaet', 0.01)
    schock_wahrscheinlichkeit = kwargs.get('schock_wahrscheinlichkeit', 0.02)
    
    price = 100.0
    vix = 18.0
    prices = [price]
    vix_history = [vix]
    
    retail_quote = retail_start
    fund_quote = fund_start
    retail_quote_prev = retail_quote
    fund_quote_prev = fund_quote
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
        
        target_retail = min(1.0, retail_start + (day / tage) * 0.10)
        if ret_5d < retail_panik_schwelle:
            retail_quote = max(0, retail_quote - retail_panik_verkauf)
        elif ret_5d > retail_gier_schwelle:
            retail_quote = min(1, retail_quote + retail_gier_kauf)
        else:
            retail_quote += 0.02 * (target_retail - retail_quote)
        
        target_fund = min(fund_leverage_limit, fund_start + (day / tage) * 0.10)
        flows = 0
        if vix > fund_vix_threshold:
            flows = -fund_abfluss_rate
        
        if ret_5d > 0.05:
            fund_quote = min(fund_leverage_limit, fund_quote + 0.05)
        elif ret_5d < -0.05:
            fund_quote = max(0.4, fund_quote - 0.1)
        else:
            fund_quote += 0.01 * (target_fund - fund_quote)
        
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
        
        retail_net = (retail_quote - retail_quote_prev) * volume_retail
        fund_net = (fund_quote - fund_quote_prev) * fund_volume
        net_demand = retail_net + fund_net
        
        total_liquidity = volume_retail + volume_fund
        if hft_active:
            liquidity = total_liquidity
        else:
            liquidity = max(100, total_liquidity * 0.2)
        
        if liquidity > 0:
            price_change = 0.0001 + (net_demand / liquidity) * 0.1
        else:
            price_change = 0.0001 - 0.001
        
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
        retail_quote_prev = retail_quote
        fund_quote_prev = fund_quote
    
    return prices, vix_history, retail_quotes, fund_quotes, hft_active_history

# --- Analyse & Coach ---
def generate_user_friendly_insight(prices, vix_history, retail_quotes, fund_quotes, hft_active_history, params):
    final_return = (prices[-1] - prices[0]) / prices[0] * 100
    max_vix = max(vix_history)
    hft_off_days = sum(1 for x in hft_active_history if x == 0)
    max_drawdown = min([(p - prices[0]) / prices[0] for p in prices]) * 100
    
    if final_return > 10: summary = f"🚀 **Starke Rallye:** +{final_return:.1f} %"
    elif final_return > 2: summary = f"📈 **Leichter Anstieg:** +{final_return:.1f} %"
    elif final_return > -2: summary = f"➖ **Seitwärts:** {final_return:.1f} %"
    elif final_return > -15: summary = f"📉 **Moderate Rezession:** {abs(final_return):.1f} %"
    else: summary = f"💥 **Schwerer Crash:** {abs(final_return):.1f} %"
    
    params_text = f"**⚙️ Einstellungen:** 🟢 Quote {params['retail_start']*100:.0f}%, Panik {params['retail_panik_verkauf']:.1f}. 🔴 Hebel {params['fund_leverage_limit']:.1f}. 🟣 HFT-Abschaltung {params['hft_vix_abs_schaltung']}. 🏦 ZB-Eingriff {params['cb_intervention_schwelle']:.0%}.\n\n"
    story_text = "**📖 Geschichte:**\n\n"
    if max_vix > 45:
        story_text += "Extreme Panik-Phase (VIX > 45). "
        if hft_off_days > 5: story_text += f"HFTs {hft_off_days} Tage aus. Markt illiquide. "
    elif max_vix > 25: story_text += "Moderate Panik-Phase. "
    else: story_text += "Ruhiger Markt. "
    if np.mean(fund_quotes) > 1.2: story_text += "Fonds stark gehebelt => verschärft Absturz. "
    if hft_off_days > 0: story_text += "Liquidität brach weg. "
    
    cb_text = ""
    cb_interventions = 0
    for i in range(1, len(prices)-1):
        if prices[i] > prices[i-1] * 1.03: cb_interventions += 1
    if cb_interventions > 0: cb_text = f"🏦 ZB griff {cb_interventions}x ein."
    else: cb_text = "🏦 ZB griff nicht ein."
    
    return summary, params_text, story_text, cb_text

def generate_coach_explanation(final_return, max_vix, hft_off_days, retail_panik_verkauf, retail_start, fund_leverage_limit):
    text = "**🔍 Was ist hier passiert?**\n\n"
    if max_vix > 45 and hft_off_days > 3:
        text += "⚠️ **Liquiditätskrise durch HFT-Abschaltung!** VIX > 45, HFTs abgeschaltet. Liquidität weg => Flash-Crash.\n\n"
    elif retail_panik_verkauf > 0.35:
        text += "🚨 **Panik-Verkäufe zu hoch!** Anleger verkaufen bei jedem Rücksetzer.\n\n"
    elif retail_start < 0.50:
        text += "⚠️ **Startquote zu niedrig.** Keine langfristige Kaufkraft.\n\n"
    elif fund_leverage_limit > 1.5:
        text += "💥 **Fonds zu stark gehebelt.** Zwangsverkäufe verschärfen den Crash.\n\n"
    else:
        text += "✅ **Stabile Einstellungen.** Kurs folgt Angebot und Nachfrage.\n\n"
    if final_return < -10: text += f"📉 **Ergebnis:** {abs(final_return):.1f} % Verlust."
    elif final_return > 10: text += f"📈 **Ergebnis:** {final_return:.1f} % Gewinn."
    else: text += f"📊 **Ergebnis:** Seitwärts ({final_return:.1f} %)."
    return text

# --- Hauptsimulation ---
if st.button("🚀 Simulation neu starten", type="primary"):
    params = {
        'tage': tage, 'retail_start': retail_start, 'retail_gier_schwelle': retail_gier_schwelle,
        'retail_panik_schwelle': retail_panik_schwelle, 'retail_panik_verkauf': retail_panik_verkauf,
        'retail_gier_kauf': retail_gier_kauf, 'fund_start': fund_start, 'fund_leverage_limit': fund_leverage_limit,
        'fund_vix_threshold': fund_vix_threshold, 'fund_abfluss_rate': fund_abfluss_rate,
        'hft_capital': hft_capital, 'hft_vix_abs_schaltung': hft_vix_abs_schaltung,
        'cb_intervention_schwelle': cb_intervention_schwelle, 'cb_kauf_volumen': cb_kauf_volumen,
        'cb_vola_reduktion': cb_vola_reduktion, 'schock_volatilitaet': schock_volatilitaet,
        'schock_wahrscheinlichkeit': schock_wahrscheinlichkeit
    }
    with st.spinner("Simuliere Marktverhalten..."):
        prices, vix_history, retail_quotes, fund_quotes, hft_active_history = run_simulation(**params)
        
        st.success("Simulation abgeschlossen!")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Start", f"{prices[0]:.2f}")
        col2.metric("Ende", f"{prices[-1]:.2f}")
        col3.metric("Rendite", f"{(prices[-1]/prices[0]-1)*100:.1f} %")
        col4.metric("Max. VIX", f"{max(vix_history):.1f}")
        
        fig, ax = plt.subplots(2, 1, figsize=(12, 8))
        ax[0].plot(prices, label="📊 Aktienkurs", color="blue"); ax[0].legend(); ax[0].grid(True)
        ax[1].plot(vix_history, label="😨 VIX", color="orange"); ax[1].axhline(y=30, color="red", linestyle="--"); ax[1].axhline(y=15, color="green", linestyle="--"); ax[1].legend(); ax[1].grid(True)
        st.pyplot(fig)
        
        fig2, ax2 = plt.subplots(figsize=(12, 5))
        ax2.plot(retail_quotes, label="🟢 Privatanleger", color="green")
        ax2.plot(fund_quotes, label="🔴 Fonds", color="red")
        ax2.plot(hft_active_history, label="🟣 HFT aktiv", color="purple", linestyle="--")
        ax2.legend(); ax2.grid(True)
        st.pyplot(fig2)

        fig3, ax3 = plt.subplots(figsize=(10, 5))
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        ax3.hist(returns, bins=50, color="blue", alpha=0.7)
        ax3.set_xlabel("Tägliche Rendite"); ax3.grid(True)
        st.pyplot(fig3)
        
        df = pd.DataFrame({"Tag": range(len(prices)), "VIX": vix_history})
        df["Phase"] = "Normal"
        df.loc[df["VIX"] < 15, "Phase"] = "🟢 Ruhe"
        df.loc[df["VIX"] > 30, "Phase"] = "🔴 Panik"
        df.loc[df["VIX"] > 50, "Phase"] = "⛔ Flash-Crash"
        st.bar_chart(df["Phase"].value_counts())
        
        st.subheader("🧠 Analyse & Interpretation")
        if scenario != "Benutzerdefiniert (Manuell)": st.info("**Analyse:** Voreingestelltes Szenario geladen.")
        else:
            final_return = (prices[-1] - prices[0]) / prices[0] * 100
            max_vix = max(vix_history)
            hft_off_days = sum(1 for x in hft_active_history if x == 0)
            
            summary, params_text, story, cb = generate_user_friendly_insight(prices, vix_history, retail_quotes, fund_quotes, hft_active_history, params)
            st.success(summary)
            st.markdown(params_text)
            st.markdown(story)
            st.markdown(cb)
            st.info(generate_coach_explanation(final_return, max_vix, hft_off_days, retail_panik_verkauf, retail_start, fund_leverage_limit))

# --- NEU: Dynamischer Wissenschaftlicher Test-Modus ---
st.markdown("---")
st.subheader("🧪 Wissenschaftlicher Test-Modus")
st.markdown("**Neu:** Dieser Test nimmt Deine *aktuellen* Einstellungen und variiert sie um +/- einen Schritt. So siehst Du, wie empfindlich der Markt auf kleine Änderungen an Deinen Reglern reagiert.")

if st.button("🧪 Führe Sensitivitäts-Test durch (Dauer ca. 15 Sekunden)"):
    with st.spinner("Teste die Auswirkungen basierend auf Deinen jetzigen Einstellungen..."):
        base_params = {
            'tage': tage, 'retail_start': retail_start, 'retail_gier_schwelle': retail_gier_schwelle,
            'retail_panik_schwelle': retail_panik_schwelle, 'retail_panik_verkauf': retail_panik_verkauf,
            'retail_gier_kauf': retail_gier_kauf, 'fund_start': fund_start, 'fund_leverage_limit': fund_leverage_limit,
            'fund_vix_threshold': fund_vix_threshold, 'fund_abfluss_rate': fund_abfluss_rate,
            'hft_capital': hft_capital, 'hft_vix_abs_schaltung': hft_vix_abs_schaltung,
            'cb_intervention_schwelle': cb_intervention_schwelle, 'cb_kauf_volumen': cb_kauf_volumen,
            'cb_vola_reduktion': cb_vola_reduktion, 'schock_volatilitaet': schock_volatilitaet,
            'schock_wahrscheinlichkeit': schock_wahrscheinlichkeit
        }

        # Definiere die Tests basierend auf den AKTUELLEN Werten
        # Schrittweite: 10% des aktuellen Wertes oder ein fester Delta-Wert
        test_defs = [
            {"name": "Panik-Rate", "param": "retail_panik_verkauf", "delta": 0.1, "desc": "Verkaufsdruck bei Panik"},
            {"name": "HFT-Abschaltung", "param": "hft_vix_abs_schaltung", "delta": 10, "desc": "Liquidität durch HFTs"},
            {"name": "Fonds-Hebel", "param": "fund_leverage_limit", "delta": 0.2, "desc": "Risiko durch Hebel"},
            {"name": "ZB-Eingriff", "param": "cb_intervention_schwelle", "delta": 0.05, "desc": "Reaktion der Notenbank"},
            {"name": "Markt-Vola", "param": "schock_volatilitaet", "delta": 0.005, "desc": "Tägliches Rauschen"}
        ]

        results = []
        for test in test_defs:
            param = test["param"]
            delta = test["delta"]
            current_val = base_params[param]
            
            # Niedrig-Wert: current - delta (nicht unter 0)
            low_val = max(current_val - delta, 0.0)
            # Hoch-Wert: current + delta
            high_val = current_val + delta
            
            # 5 Runs für Low
            returns_low = []
            for _ in range(5):
                p_low = base_params.copy()
                p_low[param] = low_val
                p, v, r, f, h = run_simulation(**p_low)
                returns_low.append((p[-1] - p[0]) / p[0] * 100)
            
            # 5 Runs für High
            returns_high = []
            for _ in range(5):
                p_high = base_params.copy()
                p_high[param] = high_val
                p, v, r, f, h = run_simulation(**p_high)
                returns_high.append((p[-1] - p[0]) / p[0] * 100)
            
            avg_low = np.mean(returns_low)
            avg_high = np.mean(returns_high)
            impact = avg_high - avg_low
            
            # Dynamische Erklärung basierend auf den Zahlen
            direction = "steigt" if impact > 0 else "fällt"
            abs_impact = abs(impact)
            if abs_impact > 15:
                explanation = f"Sehr starker Einfluss! Wenn Du '{test['desc']}' um {delta} erhöhst, {direction} die Rendite um {abs_impact:.1f} %. Das ist realistisch, weil dieser Parameter eine Schlüsselrolle spielt."
            elif abs_impact > 5:
                explanation = f"Moderater Einfluss. Eine Erhöhung um {delta} lässt die Rendite um {abs_impact:.1f} % {direction}. Ein typisches Marktverhalten."
            else:
                explanation = f"Geringer Einfluss (+/- {abs_impact:.1f} %). Dein aktueller Wert scheint in diesem Bereich robust zu sein."

            results.append({
                "Parameter": test["name"],
                f"Niedriger Wert (Abweichung)": f"{low_val:.2f} (-{delta})",
                f"Höherer Wert (Abweichung)": f"{high_val:.2f} (+{delta})",
                "Ø Rendite (Niedrig)": f"{avg_low:.1f} %",
                "Ø Rendite (Hoch)": f"{avg_high:.1f} %",
                "Einfluss (Differenz)": f"{impact:.1f} %",
                "Analyse & Realismus": explanation
            })

        st.success("Sensitivitätstest abgeschlossen!")
        st.dataframe(pd.DataFrame(results), use_container_width=True)
        st.info("💡 **Tipp:** Ein negativer Einfluss bedeutet: Wenn Du diesen Regler erhöhst, zerstört er tendenziell Deine Rendite. Ein positiver Einfluss treibt die Rallye an.")
