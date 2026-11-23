"""
Etapa 1 - Tratamiento, limpieza y transformacion del archivo U3_Songs.csv con Pandas.
Cumple los incisos a, b, c, d y e del Proyecto Integrador.
"""

from pathlib import Path
import pandas as pd


def limpiar_catalogo_csv(ruta_entrada: str = "U3_Songs.csv", ruta_salida: str = "U3_Songs_Limpio.csv") -> pd.DataFrame:
    print("=" * 70)
    print("INICIO DEL TRATAMIENTO DE DATOS CON PANDAS")
    print("=" * 70)

    # Lectura del archivo original
    df = pd.read_csv(ruta_entrada, encoding="utf-8")
    print(f"Registros originales cargados: {len(df)}")
    print(f"Columnas originales: {list(df.columns)}\n")

    # Inciso a) Traducir al espanol los encabezados de todas las columnas
    mapa_columnas = {
        "title": "TITULO",
        "description": "DESCRIPCION",
        "appears on": "ALBUM",
        "artist": "ARTISTA",
        "writers": "ESCRITORES",
        "producer": "PRODUCTOR",
        "released": "LANZAMIENTO",
        "streak": "RACHA",
    }
    df = df.rename(columns=mapa_columnas)
    print("[Inciso a] Encabezados traducidos al espanol:")
    print(list(df.columns), "\n")

    # Inciso b) Eliminar la columna DESCRIPTION (DESCRIPCION)
    if "DESCRIPCION" in df.columns:
        df = df.drop(columns=["DESCRIPCION"])
    print("[Inciso b] Columnas despues de eliminar DESCRIPCION:")
    print(list(df.columns), "\n")

    # Normalizar espacios en blanco en todas las columnas de texto
    for col in df.columns:
        df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)

    # Inciso c) Dividir la columna RACHA en dos columnas usando ';' -> RACHA y POSICION
    division = df["RACHA"].fillna("").astype(str).str.split(";", n=1, expand=True)
    df["RACHA"] = division[0].str.strip()
    df["POSICION"] = division[1].str.strip() if division.shape[1] > 1 else ""

    # Convertir cadenas vacias a valores nulos para administrarlos formalmente en el inciso d
    df["RACHA"] = df["RACHA"].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    df["POSICION"] = df["POSICION"].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

    print("[Inciso c] Muestra de division de RACHA y POSICION:")
    print(df[["TITULO", "ARTISTA", "RACHA", "POSICION"]].head(10).to_string(index=False), "\n")

    # Inciso d) Administrar valores nulos
    nulos_antes = df.isnull().sum()
    print("[Inciso d] Valores nulos detectados antes de la imputacion:")
    print(nulos_antes.to_string(), "\n")

    # Homogeneizar textos de RACHA sin posicion en listas
    normalizacion_racha = {
        "did not chart": "Sin ingreso en lista",
        "Did Not Chart": "Sin ingreso en lista",
        "Did not chart": "Sin ingreso en lista",
        "Non-Single": "No es sencillo",
        "Non-single": "No es sencillo",
        "predates chart": "Anterior a la lista",
    }
    df["RACHA"] = df["RACHA"].replace(normalizacion_racha)

    # Rellenar valores nulos con etiquetas consistentes
    df["TITULO"] = df["TITULO"].fillna("Sin titulo")
    df["ALBUM"] = df["ALBUM"].fillna("Sin album")
    df["ARTISTA"] = df["ARTISTA"].fillna("Artista desconocido")
    df["ESCRITORES"] = df["ESCRITORES"].fillna("No especificado")
    df["PRODUCTOR"] = df["PRODUCTOR"].fillna("No especificado")
    df["LANZAMIENTO"] = df["LANZAMIENTO"].fillna("Sin fecha")
    df["RACHA"] = df["RACHA"].fillna("Sin registro")
    df["POSICION"] = df["POSICION"].fillna("Sin posicion")

    nulos_despues = df.isnull().sum()
    print("[Inciso d] Valores nulos despues de la administracion:")
    print(nulos_despues.to_string(), "\n")

    # Inciso e) Administrar valores duplicados
    duplicados_detectados = int(df.duplicated().sum())
    print(f"[Inciso e] Filas duplicadas detectadas: {duplicados_detectados}")
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"[Inciso e] Total de registros unicos conservados: {len(df)}\n")

    # Exportar el archivo limpio
    df.to_csv(ruta_salida, index=False, encoding="utf-8-sig")
    print(f"Archivo limpio generado correctamente en: {Path(ruta_salida).resolve()}")
    print("=" * 70)
    return df


if __name__ == "__main__":
    limpiar_catalogo_csv()
