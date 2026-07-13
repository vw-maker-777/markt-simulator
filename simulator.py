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
            price_change = 0.0002 + (net_demand / liquidity) * 0.1
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

# --- Analysen & Erklärungen ---
def generate_user_friendly_insight(
    prices, vix_history, retail_quotes, fund_quotes, hft_active_history,
    retail_start, retail_panik_verkauf, retail_gier_kauf,
    fund_leverage_limit, fund_vix_threshold, fund_abfluss_rate,
    hft_vix_abs_schaltung, cb_intervention_schwelle,
    schock_volatilitaet, schock_wahrscheinlichkeit
):
    final_return = (prices[-1] - prices[0]) / prices[0] * 100
    max_vix = max(vix_history)
    hft_off_days = sum(1 for x in hft_active_history if x == 0)
    avg_fund = np.mean(fund_quotes)
    max_drawdown = min([(p - prices[0]) / prices[0] for p in prices]) * 100
    
    if final_return > 10: summary = f"🚀 **Starke Rallye:** Der Markt ist um **{final_return:.1f} %** gestiegen."
    elif final_return > 2: summary = f"📈 **Leichter Anstieg:** Der Markt legte um **{final_return:.1f} %** zu."
    elif final_return > -2: summary = f"➖ **Seitwärtsbewegung:** Der Markt pendelte sich um die Null-Linie ein."
    elif final_return > -15: summary = f"📉 **Moderate Rezession:** Der Markt verlor **{abs(final_return):.1f} %**."
    else: summary = f"💥 **Schwerer Crash:** Der Markt brach um **{abs(final_return):.1f} %** ein."

    params_text = "**⚙️ Wie waren die Marktteilnehmer eingestellt?**\n\n"
    params_text += f"• **🟢 Privatanleger:** Startquote {retail_start*100:.0f}%, Panik-Verkauf {retail_panik_verkauf:.1f}. "
    if retail_panik_verkauf > 0.3: params_text += "Sie reagierten **sehr panisch**.\n"
    else: params_text += "Sie reagierten **gelassen**.\n"
        
    params_text += f"• **🔴 Fonds:** Hebel {fund_leverage_limit:.1f}. "
    if fund_leverage_limit > 1.3: params_text += "**Riskant**: Stark gehebelt.\n"
    else: params_text += "**Konservativ**: Geringes Risiko.\n"
        
    params_text += f"• **🟣 HFTs:** Abschaltung bei VIX > {hft_vix_abs_schaltung}.\n"
    params_text += f"• **🏦 Zentralbank:** Eingriff ab {cb_intervention_schwelle:.0%} Kursverlust.\n\n"

    story_text = "**📖 Die Geschichte dieser Simulation:**\n\n"
    if max_vix > 45:
        story_text += "Es gab eine **extreme Panik-Phase** (VIX > 45). "
        if hft_off_days > 5:
            story_text += f"Die HFTs schalteten für {hft_off_days} Tage ab. Dadurch wurde der Markt extrem illiquide und der Spread explodierte. "
    elif max_vix > 25: story_text += "Es gab eine **moderate Panik-Phase**. "
    else: story_text += "Der Markt war **überraschend ruhig**. "

    if avg_fund > 1.2: story_text += f"Die Fonds waren stark gehebelt ({avg_fund*100:.0f}%). Als die Kurse fielen, mussten sie verkaufen – das **verschärfte den Absturz**. "
    elif avg_fund < 0.95: story_text += "Die Fonds agierten sehr defensiv und stabilisierten den Markt. "

    if hft_off_days > 0: story_text += "Die Liquidität verschwand, aber der Kurs folgte weiterhin dem Angebot und der Nachfrage der Anleger. "

    cb_text = ""
    cb_interventions = 0
    for i in range(1, len(prices)-1):
        if prices[i] > prices[i-1] * 1.03: cb_interventions += 1
    if cb_interventions > 0: cb_text = f"**🏦 Rolle der Zentralbank:** Die Notenbank griff **{cb_interventions} Mal** ein und verhinderte den totalen Zusammenbruch."
    else: cb_text = f"**🏦 Rolle der Zentralbank:** Die Notenbank griff **nicht** ein. Der Markt wurde sich selbst überlassen."

    conclusion = f"**📌 Fazit für Dein Portfolio:** Rendite **{final_return:.1f} %**, max. Drawdown **{abs(max_drawdown):.1f} %**."

    lesson = "**💡 Was Du heute lernen kannst:**\n\n"
    if hft_off_days > 5: lesson += "Wenn HFTs abgeschaltet werden, verschwindet die Liquidität. Ein Markt ohne Käufer ist wie ein Auto ohne Benzin – er steht still und stürzt ab. **Merke: Liquidität ist das Blut des Marktes.**"
    elif fund_leverage_limit > 1.5 and max_drawdown < -15: lesson += "Hoher Hebel mag in Rallyes verlockend sein, aber in Crashs wird er zur tödlichen Falle. Die Fonds mussten verkaufen, weil sie ihre Kredite bedienen mussten – das hat den Absturz massiv verstärkt. **Merke: Hebel verstärkt Gewinne, aber auch Verluste.**"
    elif cb_interventions > 3: lesson += "Die Zentralbank hat mehrfach eingegriffen. Das hat den Markt gestützt, aber auch eine künstliche Blase geschaffen. Anleger verlassen sich oft blind auf die Notenbank. **Merke: Der 'Fed-Put' ist eine Illusion – er funktioniert nur, solange die Zentralbank Geld hat.**"
    elif max_vix < 25 and final_return > 5: lesson += "Ein ruhiger, stetiger Aufwärtstrend ist der Traum eines jeden Anlegers. Ohne Panik, ohne HFT-Abschaltung und ohne übermäßigen Hebel kann der Markt stabil wachsen. **Merke: Geduld und Disziplin schlagen oft die hektische Jagd nach Gewinnen.**"
    else: lesson += "Der Markt ist ein komplexes System aus Angst, Gier und Algorithmen. Jeder Regler, den Du verschiebst, verändert das Gleichgewicht. **Merke: Verstehe die Teilnehmer, bevor Du auf den Markt gehst.**"

    return summary, params_text, story_text, cb_text, conclusion, lesson

def generate_coach_explanation(retail_panik_verkauf, max_vix, hft_off_days, final_return, retail_start, fund_leverage_limit):
    text = "**🔍 Was ist hier passiert?**\n\n"
    if max_vix > 45 and hft_off_days > 3: text += "⚠️ **Liquiditätskrise durch HFT-Abschaltung!** Der VIX schoss über 45, die HFTs verließen den Markt. Ohne Liquidität brach der Markt zusammen.\n\n"
    elif retail_panik_verkauf > 0.35: text += "🚨 **Problem: Privatanleger sind zu panisch.** Die Panik-Verkaufsrate ist hoch. Sie verkaufen bei jedem kleinen Rücksetzer massiv.\n\n"
    elif retail_start < 0.50: text += "⚠️ **Problem: Start-Aktienquote zu niedrig.** Zu wenig langfristige Kaufkraft im Markt.\n\n"
    elif fund_leverage_limit > 1.5: text += "💥 **Problem: Fonds zu stark gehebelt.** Zwangsverkäufe verschärfen den Absturz.\n\n"
    else: text += "✅ **Gute Einstellungen!** Deine Panik-Rate ist niedrig und die Startquote ist optimistisch. Das führt in der Regel zu einem stabilen Aufwärtstrend.\n\n"
    
    if final_return < -10: text += f"📉 **Das Ergebnis:** Der Markt brach um **{abs(final_return):.1f} %** ein. "
    elif final_return > 10: text += f"📈 **Das Ergebnis:** Der Markt stieg um **{final_return:.1f} %**. Eine starke Rallye!"
    else: text += f"📊 **Das Ergebnis:** Der Markt bewegte sich seitwärts mit einer Rendite von **{final_return:.1f} %**."
    return text

# --- NEUE HILFSFUNKTION: DeepSeek-Export ---
def generate_deepseek_export(params, prices, vix_history, hft_active_history, scenario):
    final_return = (prices[-1] - prices[0]) / prices[0] * 100
    max_vix = max(vix_history)
    hft_off_days = sum(1 for x in hft_active_history if x == 0)
    max_drawdown = min([(p - prices[0]) / prices[0] for p in prices]) * 100
    
    text = "=== DEEPSEEK PLAUSIBILITÄTS-CHECK PROTOKOLL ===\n\n"
    text += f"Szenario: {scenario}\n"
    text += f"Simulierte Tage: {params['tage']}\n\n"
    
    text += "--- EINGESTELLTE PARAMETER ---\n"
    text += f"Privatanleger Startquote: {params['retail_start']:.2f}\n"
    text += f"Privatanleger Panik-Verkauf: {params['retail_panik_verkauf']:.2f}\n"
    text += f"Privatanleger Gier-Kauf: {params['retail_gier_kauf']:.2f}\n"
    text += f"Fonds Maximaler Hebel: {params['fund_leverage_limit']:.2f}\n"
    text += f"Fonds VIX-Schwelle für Abflüsse: {params['fund_vix_threshold']:.0f}\n"
    text += f"HFT Abschaltung bei VIX: {params['hft_vix_abs_schaltung']:.0f}\n"
    text += f"Zentralbank Eingriff ab: {params['cb_intervention_schwelle']*100:.1f}% Verlust\n"
    text += f"Tägliche Volatilität: {params['schock_volatilitaet']*100:.2f}%\n"
    text += f"Schock-Wahrscheinlichkeit: {params['schock_wahrscheinlichkeit']*100:.2f}%\n\n"
    
    text += "--- ERGEBNISSE ---\n"
    text += f"Startkurs: 100.00\n"
    text += f"Endkurs: {prices[-1]:.2f}\n"
    text += f"Gesamtrendite: {final_return:.1f} %\n"
    text += f"Max. Drawdown: {abs(max_drawdown):.1f} %\n"
    text += f"Max. VIX (Angst): {max_vix:.1f}\n"
    text += f"HFT-Aus-Tage: {hft_off_days}\n\n"
    
    text += "--- FRAGE AN DEEPSEEK ---\n"
    text += "Bitte prüfe diese Simulation auf logische Konsistenz und Plausibilität.\n"
    text += "Sind die eingestellten Parameter und das erzielte Ergebnis logisch miteinander vereinbar?\n"
    text += "Falls nicht, wo liegt der Widerspruch?\n"
    text += "Gibt es ein mathematisches oder konzeptionelles Problem im Simulator?\n"
    
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
        ax[1].plot(vix_history, label="😨 Angst-Index (VIX)", color="orange"); ax[1].axhline(y=30, color="red", linestyle="--", label="Panik-Schwelle"); ax[1].legend(); ax[1].grid(True)
        st.pyplot(fig)
        
        fig2, ax2 = plt.subplots(figsize=(12, 5))
        ax2.plot(retail_quotes, label="🟢 Normale Anleger", color="green")
        ax2.plot(fund_quotes, label="🔴 Profi-Fonds", color="red")
        ax2.plot(hft_active_history, label="🟣 Handelsroboter aktiv", color="purple", linestyle="--")
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

        # --- ANALYSE & INTERPRETATION ---
        st.subheader("🧠 Analyse & Interpretation für Dich")
        
        if scenario != "Benutzerdefiniert (Manuell)":
            if scenario == "1. Panik-Crash (Roboter schalten aus)":
                fixed_text = "**Analyse:** Die Handelsroboter (HFTs) sind so eingestellt, dass sie sich bereits bei einem niedrigen VIX (25) abschalten. Gleichzeitig reagieren die Privatanleger extrem panisch (Verkaufsrate 0.40) auf Verluste. Das führt zu einem perfekten Sturm: Sobald die Kurse leicht fallen, steigt die Angst, die Roboter schalten ab (Liquidität verschwindet), und die panischen Anleger verkaufen massiv in einen Markt ohne Käufer – ein klassischer Flash-Crash."
            elif scenario == "2. Allmächtige Notenbank (starker Eingriff)":
                fixed_text = "**Analyse:** Die Zentralbank ist extrem aktiv eingestellt (Eingriff schon ab 5% Kursverlust). Sie reagiert sofort und mit großen Geldmengen auf jede Krise. Das führt zu einem starken 'Fed-Put': Anleger wissen, dass die Notenbank sie auffängt. Jeder kleine Rücksetzer wird sofort mit einem Rettungspaket beantwortet, was zu einer künstlichen, nicht fundamental getriebenen Rallye führt. Die Angst (VIX) bleibt dadurch oft niedrig."
            elif scenario == "3. Gefährlicher Hebel der Fonds":
                fixed_text = "**Analyse:** Die Profi-Fonds hebeln sich stark auf (1.5-fach). Dadurch sind sie extrem anfällig für Kursbewegungen. Wenn der Markt fällt, müssen sie Aktien verkaufen, um ihre geliehenen Kredite (Margin Calls) zu bedienen. Dieser 'Zwangsverkauf' verschärft den Absturz massiv, da die Fonds weiterverkaufen, je tiefer der Kurs fällt – eine gefährliche Abwärtsspirale."
            elif scenario == "4. Ruhiger, stetiger Aufwärtstrend":
                fixed_text = "**Analyse:** Die ideale Ruhephase. Die Anleger sind gelassen (sehr niedrige Panik-Verkaufsrate 0.05), die HFTs bleiben auch bei hoher Angst aktiv (Abschaltung bei VIX > 60), und die Zentralbank greift nur im absoluten Notfall ein (ab 25% Verlust). Der Markt hat eine stabile Grundliquidität, reagiert rational auf Angebot und Nachfrage, und zeigt einen ruhigen, stetigen Aufwärtstrend ohne Extreme."
            else:
                fixed_text = "Voreingestelltes Szenario geladen."
            st.info(fixed_text)
            
        else:
            final_return = (prices[-1] - prices[0]) / prices[0] * 100
            max_vix = max(vix_history)
            hft_off_days = sum(1 for x in hft_active_history if x == 0)
            
            summary, params_text, story_text, cb_text, conclusion, lesson = generate_user_friendly_insight(
                prices, vix_history, retail_quotes, fund_quotes, hft_active_history,
                retail_start, retail_panik_verkauf, retail_gier_kauf,
                fund_leverage_limit, fund_vix_threshold, fund_abfluss_rate,
                hft_vix_abs_schaltung, cb_intervention_schwelle,
                schock_volatilitaet, schock_wahrscheinlichkeit
            )
            
            coach_text = generate_coach_explanation(
                retail_panik_verkauf, max_vix, hft_off_days, final_return, retail_start, fund_leverage_limit
            )

            st.success(summary)
            st.markdown(params_text)
            st.markdown(story_text)
            st.markdown(cb_text)
            st.markdown(conclusion)
            st.info(lesson)
            st.warning(coach_text)

# --- NEU: DEEPSEEK PLAUSIBILITÄTS-CHECK EXPORT ---
if st.button("🧐 DeepSeek-Plausibilitäts-Check vorbereiten"):
    with st.spinner("Erstelle Protokoll für DeepSeek..."):
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
        
        # Wir brauchen eine Dummy-Simulation, um die Daten zu bekommen (oder wir laden die letzte nicht. 
        # Um den Export auch ohne letzte Simulation nutzbar zu machen, starten wir eine Standard-Simulation im Hintergrund)
        # ABER: Besser ist, wir nutzen die *letzte* Simulation, wenn vorhanden. 
        # Da streamlit den State nicht persistent speichert, lassen wir die App einfach eine neue Simulation im Hintergrund laufen.
        
        prices, vix_history, retail_quotes, fund_quotes, hft_active_history = run_simulation(**params)
        
        # Wenn eine Simulation gelaufen ist, haben wir diese Daten.
        export_text = generate_deepseek_export(params, prices, vix_history, hft_active_history, scenario)
        
        st.subheader("📄 DeepSeek-Protokoll (Kopieren & Einfügen)")
        st.info("Kopiere den folgenden Text, füge ihn in einen neuen Chat mit DeepSeek ein und frage: 'Bitte prüfe diese Simulation auf Plausibilität und Logik!'")
        st.code(export_text, language="text")

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
