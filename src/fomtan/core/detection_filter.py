from collections import defaultdict, deque
import time

class TemporalDetectionFilter:
    """
    Filtro temporal que solo acepta detecciones consistentes en múltiples frames.
    Elimina "parpadeos" y falsos positivos esporádicos.
    """
    
    def __init__(self, required_frames=3, timeout=2.0):
        """
        Args:
            required_frames: Número de frames consecutivos para confirmar detección
            timeout: Segundos después de los cuales se olvida una detección
        """
        self.required_frames = required_frames
        self.timeout = timeout
        
        # Historial de detecciones por nombre de objeto
        # {nombre: [(timestamp, confidence), ...]}
        self.detection_history = defaultdict(lambda: deque(maxlen=10))
    
    def add_detections(self, detections_df):
        """
        Añade nuevas detecciones al historial
        """
        current_time = time.time()
        
        if detections_df is None or detections_df.empty:
            return
        
        # Añadir detecciones actuales al historial
        for _, row in detections_df.iterrows():
            name = row['name']
            confidence = row['confidence']
            self.detection_history[name].append((current_time, confidence))
    
    def get_validated_detections(self, detections_df):
        """
        Retorna solo las detecciones que han sido consistentes
        en los últimos N frames.
        """
        if detections_df is None or detections_df.empty:
            return detections_df.iloc[0:0]  # DataFrame vacío
        
        current_time = time.time()
        validated_rows = []
        
        for idx, row in detections_df.iterrows():
            name = row['name']
            history = self.detection_history[name]
            
            # Limpiar detecciones antiguas
            while history and (current_time - history[0][0]) > self.timeout:
                history.popleft()
            
            # Contar detecciones recientes
            recent_count = sum(1 for (ts, _) in history 
                             if (current_time - ts) < self.timeout)
            
            # Solo validar si aparece suficientes veces
            if recent_count >= self.required_frames:
                validated_rows.append(idx)
        
        return detections_df.loc[validated_rows]
    
    def reset(self):
        """Limpia todo el historial"""
        self.detection_history.clear()
