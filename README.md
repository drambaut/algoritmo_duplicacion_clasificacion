# Deteccion de duplicidad de propuestas PND

Aplicacion local para identificar parejas de propuestas potencialmente duplicadas y priorizarlas para revision humana. La logica sigue la presentacion suministrada:

- Coseno lexico sobre bolsas de palabras tras normalizar tildes y palabras frecuentes.
- Jaccard sobre fragmentos contiguos de cinco caracteres, util ante errores de digitacion.
- Coseno semantico por embeddings locales opcionales, util para sinonimos y parafrasis.

La comparacion agrupa primero por municipio y, por defecto, por eje. El puntaje final combina las senales con pesos configurables y clasifica cada pareja como `posible_duplicado`, `revisar` o `sin_alerta`.

## Inicio rapido

Se requiere Python 3.10 o una version superior.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
streamlit run app.py
```

Para activar la senal semantica basada en un modelo local:

```powershell
pip install -e .[semantic,dev]
```

La primera carga semantica puede obtener pesos. En un entorno institucional conviene precargar el modelo o configurar un repositorio autorizado antes de analizar informacion real.

## Estructura de entrada

Cargue un CSV, XLSX o XLS con estas columnas:

| Columna | Requerida | Uso |
| --- | --- | --- |
| `proposal_id` | Si | Identificador unico |
| `municipality` | Si | Contexto territorial |
| `axis` | Si | Eje tematico |
| `proposal` | Si | Texto principal |
| `expected_result` | No | Resultado esperado a 2030 |

La aplicacion tambien reconoce la plantilla `Plantilla_Cortes_PND_8bloques.xlsx`:

- **Hoja `Consulta`:** usa `id_propuesta`, `p_propuesta`, `p_mcpio_nombre`, `eje_vigente` y `p_resultado`. Si el municipio o eje principal no existe, aplica campos alternos de esa hoja.
- **Hoja `corte`:** transforma los ocho grupos `ejeN_propuesta` en una fila por propuesta. Forma el contexto territorial con `ejeN_dpto` y `ejeN_mcpio`, conserva el bloque de origen como eje y toma `ejeN_resultado` como resultado esperado.

Al cargar un libro con ambas hojas, la app usa `Consulta` cuando tiene registros; en caso contrario utiliza `corte`. Los campos de persona, como sexo, orientacion, discapacidad e IP, no entran en el calculo.

No cargue datos sensibles que no describan el contenido de la propuesta. La herramienta no usa sexo, orientacion sexual ni discapacidad.

## Uso responsable

La aplicacion genera candidatos para revision, no decide fusionar ni descartar propuestas. Revise una muestra etiquetada por personas y calibre pesos y umbrales antes de una decision operativa. La funcion `recommend_threshold` selecciona un umbral usando F1 a partir de parejas marcadas por revisores.

## Pruebas

```powershell
pytest
ruff check .
```

## Escalabilidad

Para evitar una matriz global cuadratica, el servicio compara dentro de grupos de municipio y eje, y conserva los `top_k_neighbors` cercanos por propuesta. Con volumen alto, genere candidatos mediante un indice invertido o busqueda aproximada de vecinos previo al puntaje completo.
