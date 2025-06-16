import os
import re
import sys

# Carpeta raíz del proyecto
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(ROOT_DIR)
from column_name_map import normalize_dataframe_columns, rename_columns_for_readability

# Expresiones regulares para detectar accesos a columnas de DataFrame
patterns = [
    r"\[\s*['\"]([A-Za-z0-9 _\-\.]+)['\"]\s*\]",  # df['columna']
    r"\.get\(\s*['\"]([A-Za-z0-9 _\-\.]+)['\"]",  # df.get('columna')
    r"\[\s*\[([^\]]+)\]\s*\]",                   # df[['col1', 'col2']]
]

def buscar_accesos_columnas():
    resultados = []
    for root, _, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, encoding='utf-8') as f:
                    for i, line in enumerate(f, 1):
                        for pat in patterns:
                            for match in re.finditer(pat, line):
                                # Si es una lista de columnas, separa por coma
                                cols = match.group(1)
                                if ',' in cols:
                                    cols = [c.strip().strip("'\"") for c in cols.split(',')]
                                else:
                                    cols = [cols.strip().strip("'\"")]
                                for col in cols:
                                    if col:  # Evita vacíos
                                        resultados.append((filepath, i, col, line.strip()))
    return resultados

if __name__ == "__main__":
    accesos = buscar_accesos_columnas()
    # Normalización y legibilidad de nombres de columnas en los resultados
    accesos_normalizados = [(filepath, lineno, normalize_dataframe_columns(col), rename_columns_for_readability(col), line)
                           for filepath, lineno, col, line in accesos]
    output_path = os.path.join(os.path.dirname(__file__), "accesos_columnas_encontrados.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Accesos a columnas encontrados:\n\n")
        for filepath, lineno, col, col_legible, line in accesos_normalizados:
            f.write(f"{filepath}:{lineno}  ->  '{col}' | '{col_legible}'  |  {line}\n")
        f.write(f"\nTotal de accesos encontrados: {len(accesos)}\n")
    print(f"Resultado guardado en {output_path}")