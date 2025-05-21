import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
from pyzbar import pyzbar
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Pointage QR Code", page_icon="🛂")

# Charger la base des membres
@st.cache_data
def load_membres():
    return pd.read_csv("membres.csv")

# Fonction pour enregistrer le pointage
def enregistrer_pointage(matricule, action):
    membres = load_membres()
    membre = membres[membres["matricule"] == int(matricule)]
    if membre.empty:
        st.error("⚠️ Matricule inconnu.")
        return False

    nom = membre.iloc[0]["nom"]
    service = membre.iloc[0]["service"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        df = pd.read_csv("pointages.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["matricule", "nom", "service", "heure_arrivee", "heure_depart"])

    index = df[df["matricule"] == int(matricule)].index

    if action == "Arrivée":
        if not index.empty:
            df.at[index[0], "heure_arrivee"] = now
        else:
            df.loc[len(df)] = [matricule, nom, service, now, ""]
        st.success(f"✅ {nom} enregistré comme arrivé à {now}")
    else:
        if not index.empty:
            df.at[index[0], "heure_depart"] = now
        else:
            df.loc[len(df)] = [matricule, nom, service, "", now]
        st.success(f"👋 {nom} enregistré comme parti à {now}")

    df.to_csv("pointages.csv", index=False)
    return True

# Traitement de la vidéo sans opencv
class VideoProcessor:
    def __init__(self):
        self.processing = False

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        if self.processing:
            return frame
        self.processing = True

        decoded_objects = pyzbar.decode(img)
        if decoded_objects:
            qr_data = decoded_objects[0].data.decode("utf-8")
            st.session_state['qr_code'] = qr_data

        self.processing = False
        return frame

st.title("🛂 Pointage par QR Code")

if 'qr_code' not in st.session_state:
    st.session_state['qr_code'] = None

webrtc_ctx = webrtc_streamer(
    key="qr-code-scanner",
    video_processor_factory=VideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

if st.session_state['qr_code']:
    matricule = st.session_state['qr_code']
    st.info(f"QR Code détecté : {matricule}")

    membres = load_membres()
    membre = membres[membres["matricule"] == int(matricule)]

    if membre.empty:
        st.error("Matricule inconnu.")
        st.session_state['qr_code'] = None
    else:
        nom = membre.iloc[0]["nom"]
        service = membre.iloc[0]["service"]
        st.write(f"**Nom:** {nom}")
        st.write(f"**Service:** {service}")

        action = st.radio("Type de pointage :", ["Arrivée", "Départ"], horizontal=True)
        if st.button("Enregistrer le pointage"):
            success = enregistrer_pointage(matricule, action)
            if success:
                st.session_state['qr_code'] = None

st.subheader("📋 Derniers pointages")
try:
    df_pointages = pd.read_csv("pointages.csv")
    st.dataframe(df_pointages.tail(10))
except FileNotFoundError:
    st.info("Aucun pointage enregistré pour le moment.")
