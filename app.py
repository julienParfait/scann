import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit.components.v1 import html

st.set_page_config(page_title="Scanner QR Code", page_icon="🛂")

st.title("🛂 Pointage par QR Code")

# Charger la base
@st.cache_data
def load_membres():
    return pd.read_csv("membres.csv")

# Sauvegarder pointage
def enregistrer_pointage(matricule, action):
    membres = load_membres()
    membre = membres[membres["matricule"] == int(matricule)]
    if membre.empty:
        st.error("Matricule inconnu.")
        return
    nom = membre.iloc[0]["nom"]
    service = membre.iloc[0]["service"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        df = pd.read_csv("pointages.csv")
    except:
        df = pd.DataFrame(columns=["matricule", "nom", "service", "heure_arrivee", "heure_depart"])

    index = df[df["matricule"] == int(matricule)].index
    if action == "Arrivée":
        if not index.empty:
            df.at[index[0], "heure_arrivee"] = now
        else:
            df.loc[len(df)] = [matricule, nom, service, now, ""]
    else:
        if not index.empty:
            df.at[index[0], "heure_depart"] = now
        else:
            df.loc[len(df)] = [matricule, nom, service, "", now]

    df.to_csv("pointages.csv", index=False)
    st.success(f"{action} de {nom} enregistrée à {now}")

# Interface utilisateur
st.subheader("Scanner votre badge")

code = st.text_input("Résultat du scan (automatique si scan réussi)", key="qr")

html("""
<script src="https://unpkg.com/html5-qrcode"></script>
<div id="reader" width="600px"></div>
<script>
function docReady(fn) {
    if (document.readyState === "complete" || document.readyState === "interactive") {
        setTimeout(fn, 1);
    } else {
        document.addEventListener("DOMContentLoaded", fn);
    }
}
docReady(function () {
    const qr = new Html5Qrcode("reader");
    qr.start({ facingMode: "environment" }, {
        fps: 10,
        qrbox: 250
    }, qrCodeMessage => {
        const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
        if (input) {
            input.value = qrCodeMessage;
            const event = new Event('input', { bubbles: true });
            input.dispatchEvent(event);
        }
        qr.stop();
    });
});
</script>
""", height=350)

# Affichage des infos
if code:
    st.success(f"QR Code détecté : {code}")
    membres = load_membres()
    membre = membres[membres["matricule"] == int(code)]
    if not membre.empty:
        nom = membre.iloc[0]["nom"]
        service = membre.iloc[0]["service"]
        st.write(f"**Nom :** {nom}")
        st.write(f"**Service :** {service}")
        action = st.radio("Type de pointage", ["Arrivée", "Départ"], horizontal=True)
        if st.button("Enregistrer"):
            enregistrer_pointage(code, action)
    else:
        st.error("Matricule non reconnu.")

# Affichage historique
st.subheader("📋 Derniers pointages")
try:
    st.dataframe(pd.read_csv("pointages.csv").tail(10))
except:
    st.info("Aucun pointage enregistré.")
