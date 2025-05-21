import cv2
from pyzbar.pyzbar import decode
import pandas as pd
from datetime import datetime, time

# Chargement de la base des membres
df_membres = pd.read_csv("membres.csv")
fichier_log = "pointages.csv"
fichier_excel = "export_soirée.xlsx"

def enregistrer_pointage(matricule):
    now = datetime.now()
    heure = now.strftime("%Y-%m-%d %H:%M:%S")

    membre = df_membres[df_membres["matricule"] == int(matricule)]

    if membre.empty:
        print("Matricule non reconnu.")
        return

    nom = membre.iloc[0]["nom"]
    service = membre.iloc[0]["service"]

    try:
        df_log = pd.read_csv(fichier_log)
    except FileNotFoundError:
        df_log = pd.DataFrame(columns=["matricule", "nom", "service", "heure_arrivee", "heure_depart"])

    today = datetime.now().date()
    enregistrement = df_log[(df_log["matricule"] == int(matricule)) & 
                            (pd.to_datetime(df_log["heure_arrivee"]).dt.date == today)]

    if enregistrement.empty:
        new_row = pd.DataFrame([{
            "matricule": matricule,
            "nom": nom,
            "service": service,
            "heure_arrivee": heure,
            "heure_depart": ""
        }])
        df_log = pd.concat([df_log, new_row], ignore_index=True)
        print(f"{nom} enregistré comme arrivé à {heure}")
    else:
        index = enregistrement.index[0]
        df_log.at[index, "heure_depart"] = heure
        print(f"{nom} enregistré comme parti à {heure}")

    df_log.to_csv(fichier_log, index=False)

def scanner_qr():
    cap = cv2.VideoCapture(0)
    print("Scanner un QR code... Appuyez sur Q pour quitter.")

    while True:
        ret, frame = cap.read()
        for barcode in decode(frame):
            matricule = barcode.data.decode("utf-8")
            enregistrer_pointage(matricule)
            cap.release()
            cv2.destroyAllWindows()
            return

        cv2.imshow('Scanner QR', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def export_excel_soir():
    now = datetime.now()
    heure_actuelle = now.time()

    debut = time(21, 0)  # 21h00
    fin = time(5, 0)     # 05h00

    est_autorisé = (heure_actuelle >= debut or heure_actuelle <= fin)

    if not est_autorisé:
        print("⛔ Téléchargement autorisé uniquement entre 21h et 05h.")
        return

    try:
        df_log = pd.read_csv(fichier_log)
    except FileNotFoundError:
        print("⚠️ Aucun fichier de pointage trouvé.")
        return

    df_log.to_excel(fichier_excel, index=False)
    print(f"✅ Export réussi : {fichier_excel}")

# -------------------------------
# Lancement du scan ou de l'export
scanner_qr()           # Pour scanner et enregistrer
# export_excel_soir()    # Pour export de nuit (21h-05h)
# -------------------------------
#import qrcode

#qr = qrcode.make("1001")  # Exemple : matricule 1001
#qr.save("qr_1001.png")
