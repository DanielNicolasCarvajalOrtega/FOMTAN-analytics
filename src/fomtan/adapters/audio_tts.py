def speak_estado(estado: str):
    """
    Reproduce el audio del estado (VERDE/AMARILLO/ROJO) de la fruta o verdura.
    Este estado debe ser determinado por un modelo de visión o sensor.
    """
    estado_lower = estado.lower()
    if estado_lower not in ["verde", "amarillo", "rojo"]:
        print(f"[TTS] Estado desconocido: {estado}. No se reproduce audio.")
        return

    f = AUDIO_DIR / f"{estado_lower}.mp3"
    if not f.exists():
        ensure_cache()
    if f.exists():
        _play(f)


