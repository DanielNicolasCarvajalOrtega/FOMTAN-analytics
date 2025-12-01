import os
import time
import threading
from collections import Counter
import tempfile
import subprocess

class VoiceAssistant:
    def __init__(self):
        # Diccionario para controlar el tiempo de la última mención de cada objeto
        self.last_spoken = {}
        self.cooldown = 10.0  # Segundos de espera entre avisos (AUMENTADO de 4 a 10)
        self.temp_dir = tempfile.gettempdir()
        
        # VOZ NEURAL CONFIGURADA (Calidad Humana)
        # Opciones populares:
        # es-MX-DaliaNeural  (Mujer, México - Muy natural)
        # es-MX-JorgeNeural  (Hombre, México)
        # es-ES-AlvaroNeural (Hombre, España)
        # es-ES-ElviraNeural (Mujer, España)
        # es-AR-TomasNeural  (Hombre, Argentina)
        self.voice = "es-MX-DaliaNeural" 
        
        print(f"✅ Sistema de voz Neural (Edge TTS) inicializado con voz: {self.voice}")

    def clean_label(self, label):
        """
        Extrae el nombre base del objeto ignorando estados.
        Ejemplo: 'Manzana-buen-estado' -> 'Manzana'
        """
        if '-' in label:
            return label.split('-')[0]
        return label

    def speak(self, text):
        """Genera audio Neural y lo reproduce en segundo plano"""
        def _speak_thread():
            try:
                # Generar nombre de archivo único
                filename = os.path.join(self.temp_dir, f"fomtan_neural_{int(time.time())}.mp3")
                
                # 1. Generar audio usando el comando CLI de edge-tts
                # Esto evita problemas de async/await en el hilo principal
                cmd_gen = [
                    "edge-tts",
                    "--voice", self.voice,
                    "--text", text,
                    "--write-media", filename
                ]
                
                # Ejecutar generación (esperar a que termine)
                subprocess.run(cmd_gen, check=True, capture_output=True)
                
                # 2. Reproducir en Mac usando afplay
                if os.path.exists(filename):
                    os.system(f"afplay '{filename}'")
                    
                    # 3. Limpiar
                    try:
                        os.remove(filename)
                    except:
                        pass
                        
            except Exception as e:
                print(f"❌ Error en Voz Neural: {e}")

        # Ejecutar todo el proceso en un hilo para no detener la cámara
        threading.Thread(target=_speak_thread, daemon=True).start()

    def process_detections(self, detections_df):
        """
        Lógica de Negocio:
        1. Filtra detecciones con confianza > 75% (MÁS ESTRICTO)
        2. Agrupa y cuenta objetos por tipo (limpiando etiquetas)
        3. Si hay al menos 2 objetos (MENOS REPETITIVO), verifica el tiempo de espera (cooldown)
        4. Si cumple todo, habla.
        """
        if detections_df is None or detections_df.empty:
            return

        # 1. Filtrar por confianza (Umbral MÁS ESTRICTO)
        high_conf_detections = detections_df[detections_df['confidence'] > 0.75]
        
        if high_conf_detections.empty:
            return

        # 2. Limpiar nombres y contar
        clean_names = []
        for _, row in high_conf_detections.iterrows():
            raw_name = row['name']
            clean_name = self.clean_label(raw_name)
            clean_names.append(clean_name)

        counts = Counter(clean_names)
        current_time = time.time()

        # 3. Verificar reglas por objeto
        for obj_name, count in counts.items():
            # Regla: Al menos 2 objetos (REDUCIR RUIDO DE VOZ)
            if count >= 2:
                # Verificar cooldown (10 segundos)
                last_time = self.last_spoken.get(obj_name, 0)
                
                if current_time - last_time >= self.cooldown:
                    # CUMPLIÓ TODAS LAS CONDICIONES
                    print(f"🎤 HABLANDO (Neural): {count} {obj_name}s")
                    
                    # Actualizar tiempo
                    self.last_spoken[obj_name] = current_time
                    
                    # Generar mensaje natural
                    if count == 1:
                        message = f"Veo una {obj_name}"
                    else:
                        message = f"Veo {count} {obj_name}s"
                        
                    self.speak(message)
