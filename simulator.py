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

# Szenario-Logik (setzt ALLE Regler präzise)
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
if retail_start < 0.3:
    st.sidebar.caption("📌 *Sehr defensiv: Kaum Aktien im Depot.*")
elif retail_start < 0.6:
    st.sidebar.caption("📌 *Ausgewogen: Klassischer Misch-Ansatz.*")
elif retail_start < 0.9:
    st.sidebar.caption("📌 *Optimistisch: Hohe Aktienquote, viel Risiko.*")
else:
    st.sidebar.caption("📌 *Maximal riskant: Fast 100% in Aktien.*")

retail_gier_schwelle = st.sidebar.slider("Gier-Schwelle (Tagesrendite)", 0.01, 0.10, 0.03, 0.01)
st.sidebar.caption(f"📌 *Erst ab +{retail_gier_schwelle*100:.1f}% Tagesrendite kaufen sie aggressiv zu.*")

retail_panik_schwelle = st.sidebar.slider("Panik-Schwelle (Tagesrendite)", -0.15, -0.01, -0.05, 0.01)
st.sidebar.caption(f"📌 *Bei -{abs(retail_panik_schwelle)*100:.1f}% Verlust am Tag geraten sie in Panik.*")

retail_panik_verkauf = st.sidebar.slider("Panik-Verkaufsrate (pro Tag)", 0.1, 0.5, st.session_state.panic_sell, 0.05)
if retail_panik_verkauf < 0.15:
    st.sidebar.caption("📌 *Gelassen: Sie halten auch in Krisen ihre Aktien.*")
elif retail_panik_verkauf < 0.30:
    st.sidebar.caption("📌 *Normal: Verkaufen angemessen bei Panik.*")
else:
    st.sidebar.caption("📌 *Hektisch: Bei Panik wird alles verkauft – verschärft den Crash!*")

retail_gier_kauf = st.sidebar.slider("Gier-Kaufrate (pro Tag)", 0.05, 0.3, 0.1, 0.02)
if retail_gier_kauf < 0.10:
    st.sidebar.caption("📌 *Vorsichtig: Kaufen langsam zu.*")
else:
    st.sidebar.caption("📌 *Gierig: Kaufen aggressiv in Rallyes – treibt Blasen.*")

# --- 2. INSTITUTIONELLE FONDS ---
st.sidebar.subheader("2. 🔴 Institutionelle Fonds")

fund_start = st.sidebar.slider("Start-Aktienquote", 0.0, 1.5, st.session_state.fund_leverage, 0.05)
if fund_start < 1.0:
    st.sidebar.caption("📌 *Konservativ: Kein Hebel, kaum Zwangsverkäufe.*")
elif fund_start < 1.3:
    st.sidebar.caption("📌 *Leicht gehebelt: Moderate Risiken.*")
else:
    st.sidebar.caption("📌 *Stark gehebelt: Hohe Gewinne, aber bei Crash muss massiv verkauft werden!*")

fund_leverage_limit = st.sidebar.slider("Maximaler Hebel", 1.0, 2.0, 1.1, 0.1)
if fund_leverage_limit < 1.2:
    st.sidebar.caption("📌 *Sicher: Keine gefährlichen Hebel.*")
elif fund_leverage_limit < 1.5:
    st.sidebar.caption("📌 *Moderat: Etwas Risiko für mehr Rendite.*")
else:
    st.sidebar.caption("📌 *Riskant: Hoher Hebel kann zu Kettenreaktionen führen.*")

fund_vix_threshold = st.sidebar.slider("VIX-Schwelle für Abflüsse", 20, 60, 30, 5)
st.sidebar.caption(f"📌 *Bei einem VIX über {fund_vix_threshold} ziehen Großkunden ihr Geld ab – Fonds müssen dann zwangsverkaufen.*")

fund_abfluss_rate = st.sidebar.slider("Abflussrate bei VIX-Überschreitung", 0.05, 0.5, 0.2, 0.05)
if fund_abfluss_rate < 0.15:
    st.sidebar.caption("📌 *Geduldige Kunden: Wenig Geldabfluss.*")
else:
    st.sidebar.caption("📌 *Panische Kunden: Massiver Geldabzug, der den Crash verstärkt.*")

# --- 3. HFT / MARKET MAKER ---
st.sidebar.subheader("3. 🟣 HFT / Market Maker")

hft_capital = st.sidebar.number_input("Kapital (Volume)", 1000, 50000, 10000, 1000)
if hft_capital < 5000:
    st.sidebar.caption("📌 *Geringe Liquidität: Markt ist oft ausgetrocknet.*")
else:
    st.sidebar.caption("📌 *Hohe Liquidität: HFTs versorgen den Markt mit Geld.*")

hft_vix_abs_schaltung = st.sidebar.slider("VIX-Schwelle für Abschaltung", 20, 80, st.session_state.hft_vix, 5)
if hft_vix_abs_schaltung < 30:
    st.sidebar.caption("📌 *Frühe Abschaltung: HFTs verschwinden bei leichter Panik → Flash-Crash-Gefahr!*")
elif hft_vix_abs_schaltung < 50:
    st.sidebar.caption("📌 *Normale Abschaltung: Bei großer Panik schalten sie ab.*")
else:
    st.sidebar.caption("📌 *Robust: HFTs bleiben auch in schweren Krisen aktiv – sehr stabil.*")

# --- 4. ZENTRALBANK ---
st.sidebar.subheader("4. 🏦 Zentralbank")

cb_intervention_schwelle = st.sidebar.slider("Interventions-Schwelle (Kursverlust)", 0.05, 0.30, st.session_state.cb_intervention, 0.02)
if cb_intervention_schwelle < 0.10:
    st.sidebar.caption("📌 *Aktive Notenbank: Greift bei kleinsten Verlusten ein – starke Stützung.*")
elif cb_intervention_schwelle < 0.20:
    st.sidebar.caption("📌 *Abwartend: Greift bei moderaten Verlusten ein.*")
else:
    st.sidebar.caption("📌 *Passiv: Greift erst bei schweren Crashs ein – viel Leid vorher.*")

cb_kauf_volumen = st.sidebar.slider("QE-Kaufvolumen (% des Marktes)", 0.01, 0.10, 0.05, 0.01)
if cb_kauf_volumen < 0.04:
    st.sidebar.caption("📌 *Kleine Rettungspakete: Schwacher Effekt auf den Kurs.*")
else:
    st.sidebar.caption("📌 *Große Rettungspakete: Starke Kurssprünge nach Eingriff.*")

cb_vola_reduktion = st.sidebar.slider("Vola-Reduktion nach QE (%)", 0.2, 0.8, 0.30, 0.05)
if cb_vola_reduktion < 0.4:
    st.sidebar.caption("📌 *Geringe Beruhigung: Die Angst bleibt hoch.*")
else:
    st.sidebar.caption("📌 *Starke Beruhigung: VIX fällt drastisch nach Rettung.*")

# --- 5. MARKTUMFELD ---
st.sidebar.subheader("5. 🌍 Marktumfeld")

schock_volatilitaet = st.sidebar.slider("Tägliche Schock-Volatilität (%)", 0.5, 5.0, st.session_state.schock_volatility, 0.5) / 100
if schock_volatilitaet*100 < 1.5:
    st.sidebar.caption("📌 *Ruhiges Umfeld: Wenig überraschende Kurssprünge.*")
elif schock_volatilitaet*100 < 3.0:
    st.sidebar.caption("📌 *Normales Umfeld: Moderate tägliche Schwankungen.*")
else:
    st.sidebar.caption("📌 *Stürmisch: Sehr hohe tägliche Ausschläge – der Markt zittert.*")

schock_wahrscheinlichkeit = st.sidebar.slider("Wahrscheinlichkeit großer Schocks (%)", 0.5, 10.0, st.session_state.schock_prob, 0.5) / 100
if schock_wahrscheinlichkeit*100 < 2.0:
    st.sidebar.caption("📌 *Seltene Krisen: Keine großen Überraschungen.*")
elif schock_wahrscheinlichkeit*100 < 5.0:
    st.sidebar.caption("📌 *Gelegentliche Krisen: Ab und zu ein Crash.*")
else:
    st.sidebar.caption("📌 *Häufige Panik: Ständige Schocks.*")

tage = st.sidebar.slider("Simulations-Tage", 100, 2000, 500, 50)
st.sidebar.caption(f"📌 *Simuliert {tage} Handelstage (ca. {tage/250:.1f} Jahre).*")

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
        
        target_retail = min(1.0, retail_start + (day / tage) * 0.05)
        
        if ret_5d < retail_panik_schwelle:
            retail_quote = max(0, retail_quote - retail_panik_verkauf)
        elif ret_5d > retail_gier_schwelle:
            retail_quote = min(1, retail_quote + retail_gier_kauf)
        else:
            retail_quote += 0.02 * (target_retail - retail_quote)
        
        target_fund = min(fund_leverage_limit, fund_start + (day / tage) * 0.05)
        
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
        
        retail_net = (retail_quote - retail_start) * volume_retail
        fund_net = (fund_quote - fund_start) * fund_volume
        
        if hft_active:
            liquidity = hft_volume
        else:
            liquidity = 0
        
        net_demand = retail_net + fund_net
        if liquidity > 0:
            price_change = 0.0005 + net_demand / (liquidity + 1000)
        else:
            # --- WICHTIGE KORREKTUR: Flash-Crash von -4% auf -0.5% pro Tag gesenkt ---
            if net_demand < 0:
                price_change = -0.005  # früher -0.04 (Total-Crash)
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

# --- Coach Funktion ---
def generate_coach_explanation(
    retail_start, retail_panik_verkauf, retail_gier_kauf,
    fund_leverage_limit, hft_vix_abs_schaltung, cb_intervention_schwelle,
    final_return, max_vix, max_drawdown
):
    text = "**🔍 Was ist hier passiert?**\n\n"
    
    if retail_panik_verkauf > 0.30:
        text += "🚨 **Problem 1: Die Privatanleger sind viel zu panisch.** Du hast die Panik-Verkaufsrate sehr hoch eingestellt. "
        text += "Das führt dazu, dass sie bei jedem kleinen Rücksetzer massiv verkaufen. Dieser Verkaufsdruck summiert sich über die Zeit und drückt den Kurs nach unten – auch wenn der Markt eigentlich steigen sollte.\n\n"
    elif retail_start < 0.50:
        text += "⚠️ **Problem 2: Die Start-Aktienquote ist zu niedrig.** Die Anleger starten mit zu wenig Aktien. "
        text += "Da sie bei jedem Rücksetzer zusätzlich verkaufen, fehlt dem Markt die langfristige Kaufkraft.\n\n"
    elif fund_leverage_limit > 1.5:
        text += "💥 **Problem 3: Die Fonds sind übermäßig gehebelt.** Ein Hebel über 1.5 ist in diesem Simulator extrem riskant. "
        text += "Sobald der Kurs fällt, müssen die Fonds Aktien verkaufen, um ihre Kredite zu bedienen – das verschärft den Absturz massiv.\n\n"
    else:
        text += "✅ **Gute Einstellungen!** Deine Panik-Rate ist niedrig und die Startquote ist optimistisch. "
        text += "Das führt in der Regel zu einem stabilen Aufwärtstrend. Wenn der Kurs dennoch gefallen ist, lag es wahrscheinlich an einem zufällig großen Schock (dem 'Fat Tail').\n\n"
    
    if final_return < -10:
        text += f"📉 **Das Ergebnis:** Der Markt brach um **{abs(final_return):.1f} %** ein. "
        if max_vix > 50:
            text += "Der VIX (Angst-Index) schoss über 50, was auf einen extremen Flash-Crash hindeutet. "
    elif final_return > 10:
        text += f"📈 **Das Ergebnis:** Der Markt stieg um **{final_return:.1f} %**. Eine starke Rallye!"
    else:
        text += f"📊 **Das Ergebnis:** Der Markt bewegte sich seitwärts mit einer Rendite von **{final_return:.1f} %**."
    
    return text

# --- Analyse-Funktion ---
def generate_user_friendly_insight(
    prices, vix_history, retail_quotes, fund_quotes, hft_active_history,
    retail_start, retail_panik_verkauf, retail_gier_kauf,
    fund_leverage_limit, fund_vix_threshold, fund_abfluss_rate,
    hft_vix_abs_schaltung, cb_intervention_schwelle,
    schock_volatilitaet, schock_wahrscheinlichkeit, scenario_name
):
    
    final_return = (prices[-1] - prices[0]) / prices[0] * 100
    max_vix = max(vix_history)
    hft_off_days = sum(1 for x in hft_active_history if x == 0)
    avg_fund = np.mean(fund_quotes)
    max_drawdown = min([(p - prices[0]) / prices[0] for p in prices]) * 100
    
    if final_return > 10:
        summary = f"🚀 **Starke Rallye:** Der Markt ist um **{final_return:.1f} %** gestiegen."
    elif final_return > 2:
        summary = f"📈 **Leichter Anstieg:** Der Markt legte um **{final_return:.1f} %** zu."
    elif final_return > -2:
        summary = f"➖ **Seitwärtsbewegung:** Der Markt pendelte sich um die Null-Linie ein."
    elif final_return > -15:
        summary = f"📉 **Moderate Rezession:** Der Markt verlor **{abs(final_return):.1f} %**."
    else:
        summary = f"💥 **Schwerer Crash:** Der Markt brach um **{abs(final_return):.1f} %** ein."

    params_text = "**⚙️ Wie waren die Marktteilnehmer eingestellt?**\n\n"
    params_text += f"• **🟢 Privatanleger:** Startquote {retail_start*100:.0f}%, Panik-Verkauf {retail_panik_verkauf:.1f}. "
    if retail_panik_verkauf > 0.3:
        params_text += "Sie reagierten **sehr panisch**.\n"
    else:
        params_text += "Sie reagierten **gelassen**.\n"
        
    params_text += f"• **🔴 Fonds:** Hebel {fund_leverage_limit:.1f}. "
    if fund_leverage_limit > 1.3:
        params_text += "**Riskant**: Stark gehebelt.\n"
    else:
        params_text += "**Konservativ**: Geringes Risiko.\n"
        
    params_text += f"• **🟣 HFTs:** Abschaltung bei VIX > {hft_vix_abs_schaltung}.\n"
    params_text += f"• **🏦 Zentralbank:** Eingriff ab {cb_intervention_schwelle:.0%} Kursverlust.\n\n"

    story_text = "**📖 Die Geschichte dieser Simulation:**\n\n"
    if max_vix > 45:
        story_text += "Es gab eine **extreme Panik-Phase** (VIX > 45). "
        if hft_off_days > 5:
            story_text += f"Die HFTs schalteten für {hft_off_days} Tage ab, der Handel brach zusammen. "
    elif max_vix > 25:
        story_text += "Es gab eine **moderate Panik-Phase**. "
    else:
        story_text += "Der Markt war **überraschend ruhig**. "

    if avg_fund > 1.2:
        story_text += f"Die Fonds waren stark gehebelt ({avg_fund*100:.0f}%). Als die Kurse fielen, mussten sie verkaufen – das **verschärfte den Absturz**. "
    elif avg_fund < 0.95:
        story_text += "Die Fonds agierten sehr defensiv und stabilisierten den Markt. "

    if hft_off_days > 0:
        story_text += "Für eine Weile verschwand die Liquidität, weil die HFTs den Markt verließen. "

    cb_text = ""
    cb_interventions = 0
    for i in range(1, len(prices)-1):
        if prices[i] > prices[i-1] * 1.03:
            cb_interventions += 1
    
    if cb_interventions > 0:
        cb_text = f"**🏦 Rolle der Zentralbank:** Die Notenbank griff **{cb_interventions} Mal** ein und verhinderte den totalen Zusammenbruch."
    else:
        cb_text = f"**🏦 Rolle der Zentralbank:** Die Notenbank griff **nicht** ein. Der Markt wurde sich selbst überlassen."

    conclusion = f"**📌 Fazit für Dein Portfolio:** Rendite **{final_return:.1f} %**, max. Drawdown **{abs(max_drawdown):.1f} %**."

    lesson = "**💡 Was Du heute lernen kannst:**\n\n"
    if hft_off_days > 5:
        lesson += "Wenn HFTs abgeschaltet werden, verschwindet die Liquidität. Ein Markt ohne Käufer ist wie ein Auto ohne Benzin – er steht still und stürzt ab. **Merke: Liquidität ist das Blut des Marktes.**"
    elif fund_leverage_limit > 1.5 and max_drawdown < -15:
        lesson += "Hoher Hebel mag in Rallyes verlockend sein, aber in Crashs wird er zur tödlichen Falle. Die Fonds mussten verkaufen, weil sie ihre Kredite bedienen mussten – das hat den Absturz massiv verstärkt. **Merke: Hebel verstärkt Gewinne, aber auch Verluste.**"
    elif cb_interventions > 3:
        lesson += "Die Zentralbank hat mehrfach eingegriffen. Das hat den Markt gestützt, aber auch eine künstliche Blase geschaffen. Anleger verlassen sich oft blind auf die Notenbank. **Merke: Der 'Fed-Put' ist eine Illusion – er funktioniert nur, solange die Zentralbank Geld hat.**"
    elif max_vix < 25 and final_return > 5:
        lesson += "Ein ruhiger, stetiger Aufwärtstrend ist der Traum eines jeden Anlegers. Ohne Panik, ohne HFT-Abschaltung und ohne übermäßigen Hebel kann der Markt stabil wachsen. **Merke: Geduld und Disziplin schlagen oft die hektische Jagd nach Gewinnen.**"
    else:
        lesson += "Der Markt ist ein komplexes System aus Angst, Gier und Algorithmen. Jeder Regler, den Du verschiebst, verändert das Gleichgewicht. **Merke: Verstehe die Teilnehmer, bevor Du auf den Markt gehst.**"

    return summary, params_text, story_text, cb_text, conclusion, lesson

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
        ax[0].plot(prices, label="📊 Aktienkurs", color="blue", linewidth=1.5)
        ax[0].set_ylabel("Kurs")
        ax[0].legend()
        ax[0].grid(True)
        
        ax[1].plot(vix_history, label="😨 VIX (Angst-Index)", color="orange", linewidth=1.5)
        ax[1].axhline(y=30, color="red", linestyle="--", label="🔴 Panik-Schwelle")
        ax[1].axhline(y=15, color="green", linestyle="--", label="🟢 Ruhe-Schwelle")
        ax[1].set_ylabel("VIX")
        ax[1].legend()
        ax[1].grid(True)
        st.pyplot(fig)
        
        st.subheader("🤖 Agenten-Verhalten (Aktienquoten)")
        fig2, ax2 = plt.subplots(figsize=(12, 5))
        ax2.plot(retail_quotes, label="🟢 Privatanleger", color="green", linewidth=1.5)
        ax2.plot(fund_quotes, label="🔴 Institutionelle Fonds", color="red", linewidth=1.5)
        ax2.plot(hft_active_history, label="🟣 HFT aktiv (1=ja, 0=nein)", color="purple", linewidth=1, linestyle="--")
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
        display_df = df.tail(50).copy()
        display_df["Kurs"] = display_df["Kurs"].apply(lambda x: f"{x:.2f}")
        display_df["VIX"] = display_df["VIX"].apply(lambda x: f"{x:.1f}")
        
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
            
        st.dataframe(display_df.style.map(highlight_vix, subset=["VIX"]))

        st.subheader("🧠 Analyse & Interpretation für Dich")
        
        if scenario != "Benutzerdefiniert (Manuell)":
            if scenario == "1. Reiner Panik-Crash (HFTs schalten ab)":
                fixed_text = "**Analyse:** Die HFTs haben bei VIX > 25 abgeschaltet. Dadurch verschwand die Liquidität schlagartig. Privatanleger verkauften massiv, ohne dass Market Maker als Gegenpartei da waren. Der Kurs fiel in einen Flash-Crash."
            elif scenario == "2. Allmächtige Zentralbank (Fed-Put)":
                fixed_text = "**Analyse:** Die Zentralbank griff bei jedem kleinen Kursverlust sofort ein. Jede Panik wurde sofort erstickt, was zu einer künstlichen, nicht fundamentalen Rallye führte."
            elif scenario == "3. Leverage-Zyklus der Fonds":
                fixed_text = "**Analyse:** Die Fonds hebeln sich stark auf. Bei einem Schock zogen die Kunden massiv Geld ab, was die Fonds zwang, Aktien zu verkaufen. Dieser 'Zwangsverkauf' verschärfte den Absturz massiv."
            elif scenario == "4. Perfektes Contango (Ruhe)":
                fixed_text = "**Analyse:** Die Volatilität war extrem niedrig und es gab kaum große Schocks. Die HFTs blieben dauerhaft aktiv. Es entstand ein ruhiger, stetiger Aufwärtstrend."
            else:
                fixed_text = "Simulation durchgeführt."
            st.info(fixed_text)
            
        else:
            summary, params, story, cb, conclusion, lesson = generate_user_friendly_insight(
                prices, vix_history, retail_quotes, fund_quotes, hft_active_history,
                retail_start, retail_panik_verkauf, retail_gier_kauf,
                fund_leverage_limit, fund_vix_threshold, fund_abfluss_rate,
                hft_vix_abs_schaltung, cb_intervention_schwelle,
                schock_volatilitaet, schock_wahrscheinlichkeit, scenario
            )
            
            final_return = (prices[-1] - prices[0]) / prices[0] * 100
            max_vix = max(vix_history)
            max_drawdown = min([(p - prices[0]) / prices[0] for p in prices]) * 100
            
            st.success(summary)
            st.markdown(params)
            st.markdown(story)
            st.markdown(cb)
            st.markdown(conclusion)
            st.info(lesson)
            
            coach_text = generate_coach_explanation(
                retail_start, retail_panik_verkauf, retail_gier_kauf,
                fund_leverage_limit, hft_vix_abs_schaltung, cb_intervention_schwelle,
                final_return, max_vix, max_drawdown
            )
            st.warning(coach_text)

else:
    st.info("👈 Wähle ein Szenario oder stelle die Parameter manuell ein, dann klicke auf 'Simulation neu starten'.")
