from __future__ import annotations
from typing import List, Dict



class PersonasEquipos:
    """Clase para manejar una lista de diccionarios con estructura str:str"""
    
    def __init__(self, nombres: list[dict[str, str]])-> None:
        """
        Inicializa la clase con una lista de diccionarios.
        
        Args:
            nombres: Lista de diccionarios con claves y valores de tipo str
        """
        self.nombres: list[dict[str, str]] = nombres if nombres is not None else []
    
    def agregar(self, item: dict[str, str]):
        """Agrega un nuevo diccionario a la lista"""
        self.nombres.append(item)
    
    def obtener_nombres(self) -> list[dict[str, str]]:
        """Retorna la lista de diccionarios"""
        if self.nombres is None:
            raise TypeError("No se han agregado nombres y equipos a la lista")
        else:
            return str(self.nombres)

    def recorrer_diccionario(self)-> list[str]:
        if len(self.nombres) == 0:
            raise TypeError("Hay 0 nombres en la lista")
        
        else:
            valores_diccionario = self.nombres
            for i in valores_diccionario:
                for i,j in i.items():
                    print(f"equipos: {j} nombres: {i}", end=" ")



personas_equipos = PersonasEquipos([
        {'nombre': 'Juan',
        'equipo': 'Barcelona'
        }, 
        {'nombre': 'Maria', 
        'equipo': 'Curico Unido'
        }])
personas_equipos.recorrer_diccionario()
        
    
    

    