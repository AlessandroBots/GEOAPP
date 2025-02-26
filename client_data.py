from google.cloud import firestore
import pandas as pd
import time
import json


db = firestore.Client.from_service_account_json("credential.json")


df = pd.read_csv('Geo-referenced Annual Crop Yields - Processed', comment="#").dropna()


collection_name = "crop_yields"


for index, row in df.iterrows():
    data = row.to_dict()

    moisture = data.get("moisture")

    # Controlla se il campo moisture è una stringa e ha più di 6 caratteri
    if isinstance(data["moisture"], str) and len(data["moisture"]) > 6:
        print(f"Ignorato: Il valore di 'moisture' ({data['moisture']}) ha più di 6 caratteri.")
        continue
    # Se moisture è un numero e ha un valore anomalo (negativo o troppo grande), ignorare la riga
    if isinstance(moisture, (int, float)) and (moisture < 0 or moisture > 100):
        print(f"Il documento {data} ha una moisture fuori intervallo.")
        continue

    print(f"Invio dati a Firestore: {json.dumps(data, indent=2)}")

    # Crea una chiave unica
    doc_id = f"{data['longitude']}_{data['latitude']}_{data['yield']}_{data['species']}_{data['moisture']}_{data['year']}"

    # Controlla se il documento esiste già
    doc_ref = db.collection(collection_name).document(doc_id)
    doc = doc_ref.get()

    if doc.exists:
        print(f"Il documento {doc_id} esiste già, non verrà aggiunto.")
    else:
        doc_ref.set(data)
        print(f"Documento {doc_id} aggiunto con successo!")

print("Processo completato: Dati inviati a Firestore!")