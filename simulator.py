import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- Streamlit Setup ---
st.set_page_config(page_title="Marktpsychologie-Simulator", layout="wide")
st.title("🧠 Marktpsychologie-Simulator")
st.markdown("Spiele mit den Schiebereglern und beobachte, wie sich Aktienkurse verändern.")

# --- Benutzerfreundlicher Guide (Einklappbar) ---
with st.expander("ℹ️ Kurzanleitung für Neulinge (Klicke hier)"):
    st.markdown("""
    **Herzlich willkommen! So funktioniert der Simulator:**
    
    1. **Stelle die Regler ein:** Auf der linken Seite kannst du das Verhalten von Anlegern, Banken und Handelsrobotern verändern.
    2. **Klicke auf den roten Button:** Drücke *„Simulation neu starten“*, um den Markt zu berechnen.
    3. **Lies die blaue Linie:** Sie zeigt den Aktienkurs. Die orange Linie zeigt die *Angst* der Anleger.
    
    **Wichtig für Anfänger:** Wenn du nicht weißt, was die Regler tun, lass sie einfach so, wie sie sind, und klicke auf den roten Button. Du wirst schnell verstehen, wie die Kurse auf Angst und Gier reagieren!
    """)

# --- Sidebar: Parameter ---
st.sidebar.header("⚙️ Schieberegler zum Experimentieren")

# Dropdown für Szenarien
scenario = st.sidebar.selectbox(
    "📂 Wähle eine vorgefertigte Geschichte",
    ("Benutzerdefiniert (Manuell)", 
     "1. Panik-Crash (Roboter schalten aus)", 
     "2. Allmächtige Notenbank (starker Eingriff)", 
     "3. Gefährlicher Hebel der Fonds", 
     "4. Ruhiger, stetiger Aufwärtstrend")
)

# Szenario-Logik
if scenario == "1. Panik-Crash (Roboter schalten aus)":
    st.session_state["hft_vix"] = 25
    st.session_state["panic_sell"] = 0.40
    st.session_state["cb_intervention"] = 0.30
    st.session_state["fund_leverage"] = 1.50
    st.session_state["retail_start"] = 0.60
elif scenario == "2. Allmächtige Notenbank (starker Eingriff)":
    st.session_state["hft_vix"] = 50
    st.session_state["panic_sell"] = 0.20
    st.session_state["cb_intervention"] = 0.05
    st.session_state["fund_leverage"] = 1.10
    st.session_state["retail_start"] = 0.80
elif scenario == "3. Gefährlicher Hebel der Fonds":
    st.session_state["hft_vix"] = 50
    st.session_state["panic_sell"] = 0.20
    st.session_state["cb_intervention"] = 0.15
    st.session_state["fund_leverage"] = 1.50
    st.session_state["retail_start"] = 0.60
elif scenario == "4. Ruhiger, stetiger Aufwärtstrend":
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
st.sidebar.subheader("1. 🟢 Normale Anleger")

retail_start = st.sidebar.slider("Start-Aktienquote (in %)", 0.0, 1.0, st.session_state.retail_start, 0.05)
if retail_start < 0.3: st.sidebar.caption("📌 *Sehr pessimistisch: Haben kaum Aktien gekauft.*")
elif retail_start < 0.6: st.sidebar.caption("📌 *Ausgewogen: Halten eine normale Menge Aktien.*")
elif retail_start < 0.9: st.sidebar.caption("📌 *Optimistisch: Haben viel in Aktien investiert.*")
else: st.sidebar.caption("📌 *Maximal optimistisch: 100% in Aktien.*")

retail_gier_schwelle = st.sidebar.slider("Gier-Schwelle", 0.01, 0.10, 0.03, 0.01)
st.sidebar.caption(f"📌 *Kaufen massiv, wenn der Markt an einem Tag um +{retail_gier_schwelle*100:.1f}% steigt.*")

retail_panik_schwelle = st.sidebar.slider("Panik-Schwelle", -0.15, -0.01, -0.05, 0.01)
st.sidebar.caption(f"📌 *Verkaufen panisch, wenn der Markt um -{abs(retail_panik_schwelle)*100:.1f}% fällt.*")

retail_panik_verkauf = st.sidebar.slider("Verkaufen bei Panik (Anteil)", 0.1, 0.5, st.session_state.panic_sell, 0.05)
if retail_panik_verkauf < 0.15: st.sidebar.caption("📌 *Gelassen: Verkaufen fast gar nicht.*")
elif retail_panik_verkauf < 0.30: st.sidebar.caption("📌 *Normal: Verkaufen gemäßigt.*")
else: st.sidebar.caption("📌 *Hektisch: Verkaufen fast alles – löst Crashs aus!*")

retail_gier_kauf = st.sidebar.slider("Kaufen bei Gier (Anteil)", 0.05, 0.3, 0.1, 0.02)
if retail_gier_kauf < 0.10: st.sidebar.caption("📌 *Vorsichtig: Kaufen nur langsam.*")
else: st.sidebar.caption("📌 *Gierig: Kaufen extrem schnell – treibt Blasen.*")

# --- 2. INSTITUTIONELLE FONDS ---
st.sidebar.subheader("2. 🔴 Profi-Fonds (Große Anleger)")

fund_start = st.sidebar.slider("Start-Risiko (Hebel)", 0.0, 1.5, st.session_state.fund_leverage, 0.05)
if fund_start < 1.0: st.sidebar.caption("📌 *Konservativ: Kein Risiko, kaum Zwangsverkäufe.*")
elif fund_start < 1.3: st.sidebar.caption("📌 *Leicht riskant: Moderate Verstärkung.*")
else: st.sidebar.caption("📌 *Sehr riskant: Große Verstärkung, aber bei Crash massive Verluste!*")

fund_leverage_limit = st.sidebar.slider("Maximales Risiko (Hebel)", 1.0, 2.0, 1.1, 0.1)
if fund_leverage_limit < 1.2: st.sidebar.caption("📌 *Sicher: Keine gefährlichen Wetten.*")
elif fund_leverage_limit < 1.5: st.sidebar.caption("📌 *Moderat: Etwas Risiko für mehr Gewinne.*")
else: st.sidebar.caption("📌 *Riskant: Hoher Hebel führt oft zu Kettenreaktionen.*")

fund_vix_threshold = st.sidebar.slider("Angst-Schwelle für Geldabzug", 20, 60, 30, 5)
st.sidebar.caption(f"📌 *Wenn die Angst (VIX) über {fund_vix_threshold} steigt, ziehen Kunden ihr Geld ab.*")

fund_abfluss_rate = st.sidebar.slider("Abzug bei Angst", 0.05, 0.5, 0.2, 0.05)
if fund_abfluss_rate < 0.15: st.sidebar.caption("📌 *Geduldige Kunden: Wenig Abzug.*")
else: st.sidebar.caption("📌 *Panische Kunden: Massiver Abzug, der Abstürze verschärft.*")

# --- 3. HFT / MARKET MAKER ---
st.sidebar.subheader("3. 🟣 Handelsroboter (HFTs)")

hft_capital = st.sidebar.number_input("Liquidität (Geld)", 1000, 50000, 10000, 1000)
if hft_capital < 5000: st.sidebar.caption("📌 *Wenig Geld: Markt ist oft ausgetrocknet.*")
else: st.sidebar.caption("📌 *Viel Geld: Roboter versorgen den Markt ständig mit Liquidität.*")

hft_vix_abs_schaltung = st.sidebar.slider("Abschaltung bei Angst", 20, 80, st.session_state.hft_vix, 5)
if hft_vix_abs_schaltung < 30: st.sidebar.caption("📌 *Frühe Abschaltung: Roboter verschwinden sofort → Flash-Crash-Gefahr!*")
elif hft_vix_abs_schaltung < 50: st.sidebar.caption("📌 *Normale Abschaltung: Bei großer Angst schalten sie ab.*")
else: st.sidebar.caption("📌 *Robust: Roboter bleiben auch in Krisen aktiv – sehr stabil.*")

# --- 4. ZENTRALBANK ---
st.sidebar.subheader("4. 🏦 Notenbank")

cb_intervention_schwelle = st.sidebar.slider("Eingriff bei Crash", 0.05, 0.30, st.session_state.cb_intervention, 0.02)
if cb_intervention_schwelle < 0.10: st.sidebar.caption("📌 *Aktiv: Greift bei kleinsten Verlusten ein.*")
elif cb_intervention_schwelle < 0.20: st.sidebar.caption("📌 *Abwartend: Greift bei moderaten Verlusten ein.*")
else: st.sidebar.caption("📌 *Passiv: Greift erst bei schweren Crashs ein – viel Schmerz vorher.*")

cb_kauf_volumen = st.sidebar.slider("Geldmenge beim Eingriff", 0.01, 0.10, 0.05, 0.01)
if cb_kauf_volumen < 0.04: st.sidebar.caption("📌 *Kleine Rettungspakete: Schwacher Effekt.*")
else: st.sidebar.caption("📌 *Große Rettungspakete: Starke Kurssprünge.*")

cb_vola_reduktion = st.sidebar.slider("Beruhigung der Angst (%)", 0.2, 0.8, 0.30, 0.05)
if cb_vola_reduktion < 0.4: st.sidebar.caption("📌 *Geringe Beruhigung: Die Angst bleibt hoch.*")
else: st.sidebar.caption("📌 *Starke Beruhigung: Die Angst fällt drastisch.*")

# --- 5. MARKTUMFELD ---
st.sidebar.subheader("5. 🌍 Zufällige Schocks")

schock_volatilitaet = st.sidebar.slider("Tägliches Rauschen (%)", 0.5, 5.0, st.session_state.schock_volatility, 0.5) / 100
if schock_volatilitaet*100 < 1.5: st.sidebar.caption("📌 *Ruhig: Wenig Schwankungen.*")
elif schock_volatilitaet*100 < 3.0: st.sidebar.caption("📌 *Normal: Moderate Schwankungen.*")
else: st.sidebar.caption("📌 *Stürmisch: Hohe tägliche Schwankungen – Markt zittert.*")

schock_wahrscheinlichkeit = st.sidebar.slider("Wahrscheinlichkeit großer Schocks (%)", 0.5, 10.0, st.session_state.schock_prob, 0.5) / 100
if schock_wahrscheinlichkeit*100 < 2.0: st.sidebar.caption("📌 *Seltene Krisen: Keine großen Überraschungen.*")
elif schock_wahrscheinlichkeit*100 < 5.0: st.sidebar.caption("📌 *Gelegentliche Krisen: Ab und zu ein Crash.*")
else: st.sidebar.caption("📌 *Häufige Panik: Ständige Schocks.*")

tage = st.sidebar.slider("Simulations-Länge (Tage)", 100, 2000, 500, 50)
st.sidebar.caption(f"📌 *Simuliert {tage} Tage (ca. {tage/250:.1f} Jahre).*")

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

# --- Analyse & Coach (Vereinfacht für Endnutzer) ---
def generate_simple_insight(prices, vix_history, retail_quotes, fund_quotes, hft_active_history, params):
    final_return = (prices[-1] - prices[0]) / prices[0] * 100
    max_vix = max(vix_history)
    hft_off_days = sum(1 for x in hft_active_history if x == 0)
    max_drawdown = min([(p - prices[0]) / prices[0] for p in prices]) * 100
    
    # Kurz-Zusammenfassung für Anfänger
    if final_return > 15: status = "🚀 **Massiver Gewinn!**"
    elif final_return > 5: status = "📈 **Guter Gewinn.**"
    elif final_return > -5: status = "➖ **Seitwärts (keine große Bewegung).**"
    elif final_return > -20: status = "📉 **Mäßiger Verlust.**"
    else: status = "💥 **Schwerer Crash!**"

    if max_vix > 45 and hft_off_days > 3:
        reason = "🚨 **Grund:** Die Angst war extrem hoch (VIX > 45). Die Handelsroboter (HFTs) haben abgeschaltet. Dadurch war kein Geld mehr da, um Aktien zu kaufen – der Markt brach zusammen."
    elif params['retail_panik_verkauf'] > 0.35:
        reason = "🚨 **Grund:** Die normalen Anleger haben bei jedem kleinen Crash panisch verkauft. Das hat die Kurse immer weiter nach unten gedrückt."
    elif params['fund_leverage_limit'] > 1.5:
        reason = "⚡ **Grund:** Die großen Profi-Fonds hatten zu viel Risiko (hohen Hebel). Als die Kurse fielen, mussten sie sofort verkaufen, um ihre Kredite zu bedienen – das hat den Absturz massiv verschärft."
    else:
        reason = "✅ **Grund:** Die Einstellungen waren gut. Die Kurve ist dem natürlichen Angebot und der Nachfrage gefolgt."

    return status, reason, final_return, max_drawdown

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
        col1.metric("Startkurs", f"{prices[0]:.2f}")
        col2.metric("Endkurs", f"{prices[-1]:.2f}")
        col3.metric("Gesamtrendite", f"{(prices[-1]/prices[0]-1)*100:.1f} %")
        col4.metric("Max. Angst (VIX)", f"{max(vix_history):.1f}")
        
        fig, ax = plt.subplots(2, 1, figsize=(12, 8))
        ax[0].plot(prices, label="📊 Aktienkurs", color="blue"); ax[0].legend(); ax[0].grid(True)
        ax[1].plot(vix_history, label="😨 Angst-Index (VIX)", color="orange"); ax[1].axhline(y=30, color="red", linestyle="--", label="Panik-Schwelle"); ax[1].legend(); ax[1].grid(True)
        st.pyplot(fig)
        
        fig2, ax2 = plt.subplots(figsize=(12, 5))
        ax2.plot(retail_quotes, label="🟢 Normale Anleger", color="green")
        ax2.plot(fund_quotes, label="🔴 Profi-Fonds", color="red")
        ax2.plot(hft_active_history, label="🟣 Handelsroboter aktiv", color="purple", linestyle="--")
        ax2.legend(); ax2.grid(True)
        st.pyplot(fig2)

        # --- Vereinfachte Analyse für Endnutzer ---
        st.subheader("🧠 Zusammenfassung für Dich")
        status, reason, final_return, max_drawdown = generate_simple_insight(prices, vix_history, retail_quotes, fund_quotes, hft_active_history, params)
        
        st.success(status)
        st.markdown(f"**🔍 {reason}**")
        st.caption(f"*Der größte zwischenzeitliche Verlust (Drawdown) betrug {abs(max_drawdown):.1f} %.*")

# --- Experten-Modus (Einklappbar für Profis) ---
with st.expander("🧪 Erweiterte Tests für Experten (Klicke hier)"):
    st.markdown("Dieser Test verändert Deine aktuellen Einstellungen um kleine Schritte, um zu zeigen, wie empfindlich der Markt auf Änderungen reagiert.")
    
    if st.button("🧪 Sensitivität testen (Dauer ca. 15 Sekunden)"):
        with st.spinner("Teste die Auswirkungen..."):
            base_params = params = {
                'tage': tage, 'retail_start': retail_start, 'retail_gier_schwelle': retail_gier_schwelle,
                'retail_panik_schwelle': retail_panik_schwelle, 'retail_panik_verkauf': retail_panik_verkauf,
                'retail_gier_kauf': retail_gier_kauf, 'fund_start': fund_start, 'fund_leverage_limit': fund_leverage_limit,
                'fund_vix_threshold': fund_vix_threshold, 'fund_abfluss_rate': fund_abfluss_rate,
                'hft_capital': hft_capital, 'hft_vix_abs_schaltung': hft_vix_abs_schaltung,
                'cb_intervention_schwelle': cb_intervention_schwelle, 'cb_kauf_volumen': cb_kauf_volumen,
                'cb_vola_reduktion': cb_vola_reduktion, 'schock_volatilitaet': schock_volatilitaet,
                'schock_wahrscheinlichkeit': schock_wahrscheinlichkeit
            }

            test_defs = [
                {"name": "Panik-Verkäufe", "param": "retail_panik_verkauf", "delta": 0.1, "desc": "Verkaufsdruck"},
                {"name": "Roboter-Abschaltung", "param": "hft_vix_abs_schaltung", "delta": 10, "desc": "Liquidität"},
                {"name": "Fonds-Risiko", "param": "fund_leverage_limit", "delta": 0.2, "desc": "Hebel-Risiko"},
                {"name": "Eingriff der Notenbank", "param": "cb_intervention_schwelle", "delta": 0.05, "desc": "Rettung"},
                {"name": "Markt-Rauschen", "param": "schock_volatilitaet", "delta": 0.005, "desc": "Tägliche Schwankungen"}
            ]

            results = []
            for test in test_defs:
                param = test["param"]; delta = test["delta"]
                current_val = base_params[param]
                low_val = max(current_val - delta, 0.0)
                high_val = current_val + delta
                
                returns_low = []
                for _ in range(5):
                    p_low = base_params.copy(); p_low[param] = low_val
                    p, v, r, f, h = run_simulation(**p_low)
                    returns_low.append((p[-1] - p[0]) / p[0] * 100)
                
                returns_high = []
                for _ in range(5):
                    p_high = base_params.copy(); p_high[param] = high_val
                    p, v, r, f, h = run_simulation(**p_high)
                    returns_high.append((p[-1] - p[0]) / p[0] * 100)
                
                avg_low = np.mean(returns_low); avg_high = np.mean(returns_high)
                impact = avg_high - avg_low
                
                if impact > 15: explanation = "🔥 Sehr starker Einfluss!"
                elif impact > 5: explanation = "📊 Moderater Einfluss."
                elif impact > -5: explanation = "✅ Robuster Wert (geringer Einfluss)."
                else: explanation = "❌ Starker negativer Einfluss (Rendite wird stark zerstört!)."

                results.append({
                    "Getesteter Regler": test["name"],
                    "Niedriger Wert (-)": f"{low_val:.2f}",
                    "Höherer Wert (+)": f"{high_val:.2f}",
                    "Rendite bei Niedrig": f"{avg_low:.1f} %",
                    "Rendite bei Hoch": f"{avg_high:.1f} %",
                    "Einfluss": f"{impact:.1f} %",
                    "Ergebnis": explanation
                })

            st.success("Test abgeschlossen!")
            st.dataframe(pd.DataFrame(results), use_container_width=True)
