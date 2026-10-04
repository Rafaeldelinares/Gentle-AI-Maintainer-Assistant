# Qué puede y qué no puede decir esta herramienta

> Autoexamen, escrito **en castellano** para el responsable del proyecto y para cualquier
> lector hispanohablante. La versión en inglés es el documento hermano:
> [`SELF-EXAMINATION.md`](SELF-EXAMINATION.md). **Son el mismo documento en dos idiomas: si
> una cifra cambia, cambia en los dos.** El guardián de cifras (`tools/figures_check.py`)
> escanea los dos archivos, así que las afirmaciones numéricas de ambos están verificadas
> contra la realidad, no transcriptas.
>
> Está dirigido a los responsables de `gentle-ai`, `engram` y `gentle-shell` — la gente
> cuyos issues abiertos esto lee. Es la mitad honesta del proyecto: no lo que construimos,
> sino qué está autorizado a afirmar.
>
> Instantánea congelada: **1228 issues abiertos** en tres repositorios, en los commits
> registrados en `tools/vendor.py`. Solo lectura: este proyecto **no escribe nada** en
> ningún repositorio, y cada fila que produce queda en `veredicto_humano: pendiente`.

## 1. Qué es esto

Un análisis de solo lectura de los issues abiertos de tres repositorios. Hace cinco cosas:

| Módulo | Pregunta que responde | Reporte |
| --- | --- | --- |
| A | ¿A qué reportes les falta la información que necesitás? | `report-completeness.md` |
| B | ¿Qué pares de issues parecen el mismo reporte dos veces? | `report-duplicates.md` |
| C | ¿Qué issues se refieren a issues de los otros repositorios, y esos siguen existiendo? | `report-cross-links.md` |
| D | ¿Qué issues apuntan a cosas que ya no existen? | `report-obsolete.md` |
| E | ¿Dónde caería un cambio, si tuvieras que elegir un lugar para mirar? | `report-concentration.md` |

Más un tablero Kanban local que convierte la salida del motor en columnas en tu propia
máquina (`BOARD.md`), y un motor de reglas determinista que sugiere una banda para cada
issue (`db/rules.py`).

**No comenta, no etiqueta, no cierra, no transfiere ni manda nada por correo.** La sección
5 explica cómo eso se **verifica**, en vez de prometerse.

## 2. Qué puede decirte hoy

Cada cifra de abajo la produce el comando que se nombra al lado. Corrélo y obtenés los
mismos números — eso está chequeado (`DETERMINISM.md`).

**Qué reportes están incompletos y en qué** — `python3 modules/completeness.py`:

De **1043** issues presentados por formulario, **313** no cumplen al menos un campo de
contenido requerido. Las faltas más frecuentes son `AI Agent / Client` (159),
`Gentle AI Version` (153), `📋 Affected Area` (151), `Operating System` (150),
`🔄 Steps to Reproduce` (113) y `📝 Bug Description` (94). Por repositorio: `engram` 4
(7.1%), `gentle-ai` 201 (32.1%), `gentle-shell` 108 (30.0%).

Es el módulo con el camino más corto a las manos de un responsable: es una lista de "pedí
esta sola cosa y el reporte se vuelve accionable".

**Qué pares parecen duplicados** — `python3 modules/duplicates.py`:

**108** pares candidatos, de los cuales **7** traen evidencia fuerte (identificadores
distintivos compartidos) y 101 evidencia débil. La evidencia fuerte **ordena tu lectura**,
no sentencia: dos issues hermanos sobre la misma funcionalidad suelen compartir nombres de
excepción.

**Referencias entre repositorios** — `python3 modules/cross_repo.py`:

**48** referencias explícitas `repo#N`, de las cuales **15** resuelven a un issue abierto
de la instantánea y **33** no. Una referencia que no resuelve puede significar que el
destino se cerró, se renombró o es un error de tipeo — el reporte dice cuál, y no adivina.

**Posiblemente obsoletos** — `python3 modules/obsolete.py`:

**54** issues referencian una ruta que existe en la historia del repositorio como
*borrado* (Clase A — obsolescencia verificable) y **155** referencian una ruta, flag o
símbolo ausente **sin registro de borrado** (Clase B). **La Clase B no es evidencia de
obsolescencia**: la ruta puede pertenecer a otro repositorio, al layout del paquete
instalado, o a trabajo que todavía no aterrizó. Las dos clases se mantienen separadas a
propósito, para que la señal fuerte no se diluya con la débil.

**Dónde caen los problemas** — `python3 modules/concentration.py`:

**458** de 1228 issues nombran una ruta del repositorio, **770** no nombran ninguna, y hay
**164** subsistemas distintos. Los diez subsistemas principales cubren **299** de los 458
(65%) — encabezados por `gentle-shell` `extensions` (99), `gentle-shell` `lib` (98) y
`gentle-ai` `internal/cli` (55).

## 3. Dos mediciones que contradijeron nuestras propias premisas

Esta es la parte que nos quedaríamos si tiráramos el resto, porque las dos veces la
medición dio vuelta una premisa sobre la que el proyecto estaba construido.

### 3.1 "Los issues sin clasificar son 718" estaba mal por un 45%

El motor deja issues sin banda cuando no dispara ninguna regla. El conteo es **718** — y ese
número se trataba como "718 issues trabados". No lo es. Una medición de sesión encontró que
**255** de ellos ya estaban siendo enviados a una columna **bloqueante** (normalmente
"falta información"), y quedan unos **400** sin banda, sin columna sugerida, completos y sin
bandera de revisión humana.

> **Declarado:** esa aritmética de 255/400 **no tiene productor commiteado** en este
> repositorio, así que por nuestra propia taxonomía (`STATUS.md`) es **Clase C** — una
> medición local, no verificable desde el artefacto. Solo el 718 es reproducible (`decide()`
> devuelve `band: None`). Promover el resto a un módulo es una unidad abierta, no un pie de
> página que nos olvidamos.

La lección generaliza: **un conteo no es un hallazgo hasta que te preguntás qué deja afuera.**

### 3.2 Los clusters no colapsan: concentración es acumulación, no duplicación

Si 99 issues caen en `gentle-shell/extensions`, la esperanza obvia es que sean **un** problema
reportado 99 veces, y que agrupar te dé una lista corta. Lo medimos con dos instrumentos
independientes, y los dos dicen que no:

| Cluster | Issues | Firmas de evidencia distintas | Grupo repetido más grande |
| --- | ---: | ---: | ---: |
| `gentle-shell` `extensions` | 99 | 58 | 3 |
| `gentle-shell` `lib` | 98 | 56 | — |
| `gentle-ai` `internal/cli` | 55 | 41 | — |
| `gentle-shell` `tests` | 39 | 18 | — |
| `gentle-ai` `docs` | 35 | 12 | — |

El análisis de títulos casi duplicados coincide: en esos clusters existen solo **4** grupos de
títulos parecidos, todos de tamaño 2–3 — y **todos ellos son pedidos de funcionalidad, no
bugs**. Los pedidos duplicados son normales (varias personas quieren lo mismo); los bugs
duplicados son raros.

Así que un directorio que carga muchos reportes carga muchos problemas **distintos**. Es una
afirmación sobre **dónde se acumulan** los problemas, no sobre una causa compartida — que es
exactamente por qué el Módulo E reporta ubicación y nunca causalidad. Y el límite honesto:
**la ausencia de evidencia no es prueba de que sean distintos.** Un issue sin firma está
incorrelacionado, no establecido como diferente.

Las dos mediciones están en `report-concentration.md`, bajo "Do the clusters collapse?",
producidas por el propio módulo.

## 4. Qué no puede decir

No es "todavía no" — es **no puede**, por razones estructurales:

- **Ninguna prioridad, ninguna severidad, ningún "primero lo más importante".** Los datos no
  tienen proxy determinista de impacto: ni SLA, ni campo de severidad, ni cantidad de
  usuarios afectados, ni ingresos. Cualquier número de prioridad sería inventado, y una
  prioridad inventada es peor que ninguna, porque alguien va a actuar sobre ella.
- **Ninguna causalidad.** Estar en el mismo lugar no es compartir causa raíz (§3.2 es la
  evidencia).
- **Ninguna afirmación de precisión.** Nunca medimos si las sugerencias P0/P1 del motor son
  **correctas**, porque eso requiere una muestra etiquetada por humanos y nadie etiquetó
  ninguna. Es la decisión D-010 y sigue vigente. Lo que el motor sí afirma es que su salida
  es **reproducible y explicable**: cada banda viene con la regla que la produjo.
- **Ningún aprendizaje.** El sistema acumula decisiones; no entrena con ellas (D-025). Las
  reglas cambian cuando un humano edita `db/rules.py`, nunca solas.
- **Ninguna cobertura de los 770 issues que no nombran ninguna ruta.** Ninguna regla los
  alcanza; necesitan lectura humana. Están contados en el reporte en vez de disimulados.

## 5. Qué no va a hacer nunca

El invariante de solo lectura se sostiene con un chequeo que **hace fallar la build**, no con
disciplina: `python3 tools/readonly_check.py`. Escanea cada archivo Python del repositorio
buscando escrituras hacia afuera — verbos HTTP, subcomandos mutantes de `gh`, `git push`,
`http.client` crudo (prohibido de plano) — y exime exactamente una llamada: un `POST` a
`127.0.0.1` en la suite de pruebas del propio tablero.

`DECISIONS.md` D-036 registra la corrección que importó: el invariante es sobre **escrituras,
no sobre HTTP**. Una versión anterior prohibía los clientes HTTP enteros, lo cual confundía
un proxy con la regla. Las lecturas son cómo este proyecto obtiene sus entradas.

## 6. Cómo se chequea a sí mismo

Cinco mecanismos, porque los primeros cuatro encontraron defectos reales en el quinto:

- **Entradas fijadas** (`tools/vendor.py`, D-035). Los repositorios auditados están fijados
  por hash completo de commit en **un solo lugar**. Reejecutar el setup no puede mover una
  cifra en silencio. Cuando descubrimos que un `git pull` hacía exactamente eso, explicó un
  conteo publicado que se había movido solo.
- **Chequeo de determinismo** (`python3 tools/determinism_check.py`). Cada reporte generado
  tiene un digest, recalculado desde los mismos datos bajo dos semillas de hash distintas y
  comparado.
- **Guardián de cifras** (`python3 tools/figures_check.py`). Los conteos publicados se
  escriben en una forma legible por máquina — `marcador → N/N` — y el guardián reejecuta el
  productor y compara. Existe porque un conteo publicado quedó viejo dos veces, cada vez en
  un archivo que nadie había mirado.
- **El gate** — `python3 tools/verify_all.py` → 10/10 el gate rápido.
- El mismo gate con `--full` → 12/12.
- **CI** en cada push, en un entorno limpio y con las entradas fijadas traídas desde
  `raw.githubusercontent.com` en el commit exacto.

## 7. Cómo correrlo

```
git clone https://github.com/Rafaeldelinares/Gentle-AI-Maintainer-Assistant
cd Gentle-AI-Maintainer-Assistant
./sync-products.sh              # trae los repositorios auditados en sus commits fijados
python3 tools/verify_all.py     # el gate
python3 modules/completeness.py # cualquier módulo; cada uno escribe un reporte en la raíz
python3 board/server.py --ingest --port 8770   # el tablero, en http://127.0.0.1:8770/
```

Necesita Python 3.12+. No lee nada fuera de tu máquina salvo las descargas fijadas.

## 8. Qué no sabemos de nuestra propia herramienta

Dicho sin adornos, porque un lector merece esto más de lo que nosotros merecemos parecer
terminados:

- **Ningún humano la operó nunca.** El tablero registra **cero** decisiones humanas. Las
  cifras de arriba son mediciones de *sus* repositorios; no son evidencia de que a alguien le
  hayan servido. No estamos reclamando un servicio que nunca vimos usar.
- **Las revisiones que custodian los cambios tienen un muro.** Una revisión de cuatro lentes
  de nivel alto se relay a través del host con un límite de unos dieciséis minutos; dos
  unidades de hoy lo excedieron y quedaron sin revisar por nadie. Partir el candidato a la
  mitad **no movió el muro**, así que la restricción es el límite, no el contenido.
- **Los valores de digest no están cubiertos por el guardián de cifras.** Hueco declarado;
  cuando uno se movió, se detectó leyendo la salida, no con un chequeo.
- **El punto de entrada único y el escaneo ampliado no tienen tests.** Las herramientas
  existen; los tests de las herramientas no.
- **Las revisiones inspeccionan el cambio, no el estado del mundo.** Cuatro lentes pasaron
  por encima de dos documentos mientras de ellos se había borrado un dato verdadero con una
  justificación falsa. Se descubrió abriendo la aplicación, no con la revisión.

## 9. Ideas que vale la pena afanarse, aunque nunca corras esto

- **Fijá tus entradas en un solo lugar.** Un conteo que depende del día en que lo corriste no
  es una cifra. Poné los commits en un archivo y hacé que la descarga falle fuerte.
- **Hacé que tus afirmaciones sean legibles por máquina.** Nosotros escribimos los conteos
  como `marcador → N/N`, así un script reejecuta el productor y compara. Un guardián en prosa
  que *adivina* la atribución termina apagado, y eso es peor que no tener guardián.
- **Una búsqueda fallida no es prueba de ausencia.** Verificar "ningún comando produce este
  valor" exige **enumerar los productores**, no buscar el valor: un número calculado en
  tiempo de ejecución no tiene literal en ningún lado. Nosotros borramos un dato verdadero
  por invertir esto.
- **Mantené la evidencia fuerte separada de la débil.** Clase A (un borrado registrado) y
  Clase B (una referencia sin resolver) se reportan por separado para que 54 filas
  verificables no se lean como 209.
- **Poné los límites del instrumento dentro del artefacto.** "La ausencia de evidencia no es
  prueba" va en el reporte, no en la cabeza del autor.
- **Separá la decisión de su explicación.** Las reglas del motor son una función que devuelve
  una decisión; la capa de explicación del tablero no importa ninguna de sus tripas. Costó un
  refactor y se pagó solo la primera vez que hubo que probarlas por separado.

## 10. Si algo de acá está mal

Decilo, idealmente con el comando que lo demuestra. Cada cifra de este documento tiene uno, y
una cifra sin productor es un bug de este proyecto, no un error de redondeo.
