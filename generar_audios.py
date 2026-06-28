import os
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)

os.makedirs("audios", exist_ok=True)
os.makedirs("audios/oraciones", exist_ok=True)

# Audios de vocabulario (los 16 verbos)
verbos = [
    "play", "eat", "read", "sing", "write", "sleep",
    "run", "talk", "dance", "listen", "speak", "ask",
    "answer", "learn", "teach", "practice"
]

for verbo in verbos:
    ruta = f"audios/{verbo}.wav"
    engine.save_to_file(verbo, ruta)
    print(f"Generado: {ruta}")

# Audios de oraciones desde verbos.json
import json
with open("datos/verbos.json", "r", encoding="utf-8") as f:
    verbos_data = json.load(f)

for verbo, datos in verbos_data.items():
    for tiempo, info in datos["oraciones"].items():
        oracion = " ".join(info["correcta"])
        ruta = f"audios/oraciones/{verbo}_{tiempo}.wav"
        engine.save_to_file(oracion, ruta)
        print(f"Generado: {ruta}")

engine.runAndWait()
print("✅ Todos los audios generados correctamente")