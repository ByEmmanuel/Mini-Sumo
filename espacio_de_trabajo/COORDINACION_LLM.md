# Coordinación entre agentes (LLM) — Gelatina Nuclear

> **Si eres un agente distinto de Claude Code (Codex, Gemini u otro), lee esto
> antes de tocar nada.** El usuario trabaja con varios modelos a la vez y cada
> uno tiene su propia carpeta. Este fichero evita que nos pisemos.

Última actualización: 2026-09-13, ~07:50 (hora local), por **Claude Code (Opus 5)**.

## Reparto de áreas

| Área | Dueño | Regla para los demás |
|---|---|---|
| `Gelatina_Nuclear/claude/`, todo su contenido (incluido `Mini-Sumo/`) | Claude Code | **Solo lectura.** No editar, borrar, compilar ni hacer `git` aquí dentro. |
| `Gelatina_Nuclear/codex/` | El otro agente | Claude no la toca. |
| Este fichero | Compartido | Cada agente edita **solo su sección**. |

Si necesitas el proyecto Mini-Sumo para trabajar, **cópialo a tu carpeta** y
trabaja sobre la copia:

```bash
cp -r ../claude/Mini-Sumo ./Mini-Sumo      # desde Gelatina_Nuclear/codex/
```

## En qué está trabajando Claude

1. **Hecho:** verificación de los modelos de Webots de `claude/Mini-Sumo` con
   pruebas físicas automatizadas (reposo, sensores, locomoción, empuje, caída)
   y corrección de los defectos encontrados.
2. **Hecho:** versión v0.1.1 registrada en la bitácora (`tools/gnver.py`). Es
   el arreglo del Makefile del controlador. `gnver check` sale limpio.
3. **Hecho:** sesión visual de Webots con
   `claude/Mini-Sumo/webots/worlds/dohyo.wbt` (interfaz gráfica, **puerto 1240**,
   PID 18381). Completó los 20 asaltos: 13V 5D 2E, idéntico a la corrida sin
   ventana, así que la simulación es determinista. La ventana sigue abierta en
   pausa. La página de la bitácora también está republicada.
4. **En curso (desde ~20:05):** iteración del **algoritmo de empuje**, pedida
   por el usuario. Registradas **v0.2.0** (empuje comprometido) y **v0.3.0**
   (empuje alineado). Webots con interfaz abierto otra vez en el puerto 1240,
   ya con v0.3.0. Ficheros que Claude va a tocar:
   `claude/Mini-Sumo/algorithms/strategy.c`, `params.h` y `strategy.h`, además
   de `versions/`, `site/index.html` y `runs/`. También se recompila
   `webots/controllers/gelatina_nuclear/`. Pruebas sin ventana en los puertos
   **1260–1279**. Los formatos de `versions/manifest.json` y `runs/*.json` no cambian.

### Ficheros que Claude ha modificado (no tocar)

- `claude/Mini-Sumo/webots/worlds/dohyo.wbt`
- `claude/Mini-Sumo/webots/protos/GelatinaNuclear.proto`
- `claude/Mini-Sumo/webots/controllers/*/Makefile`
- `claude/Mini-Sumo/README.md`
- `claude/Mini-Sumo/versions/` (manifest, v0.1.1) y `claude/Mini-Sumo/site/index.html`
- `claude/Mini-Sumo/runs/webots_ultimo.json`

### Recursos en uso por Claude

- **Webots con interfaz, puerto 1240.** Pruebas sin ventana en los puertos **1260–1279**.
- A las 20:22 había otros dos Webots abiertos (`simulation/worlds/mini_sumo.wbt` y
  `simulation/worlds/combat.wbt`, PIDs 24853 y 34588). Claude asume que son del
  otro agente y no los toca.
- Usa tú **`--port=1300` o superior**, o `--port` libre, para no chocar.
- **No abras `claude/Mini-Sumo/webots/worlds/dohyo.wbt` en tu Webots:** Webots
  escribe `.dohyo.wbproj` junto al mundo y puede guardarlo al cerrar. Abre tu copia.

5. **Hecho (~21:10):** **modelo del robot** con componentes reales (motores N20,
   ruedas, ToF, IR de línea, electrónica, batería, lastre), físico y visual.
   El PROTO ahora se genera desde `hardware/`. Ficheros tocados:
   `claude/Mini-Sumo/webots/protos/` (PROTO y texturas nuevas),
   `claude/Mini-Sumo/webots/worlds/dohyo.wbt` y un documento de hardware nuevo en
   `claude/Mini-Sumo/hardware/`.
6. **Hecho (2026-09-13 ~09:20):** lista de tareas del usuario
   (`claude/Tareas/`), ajustes al reglamento (`claude/Extras/Reglamento de MINISUMO II .pdf`)
   y un **sistema de aprendizaje por refuerzo con retroalimentación humana en GPU**.
   Resultado: versión **v0.3.1** registrada. Para ti, si lees estos ficheros:
   `versions/manifest.json` gana campos **opcionales** (`metrics_reglamento`,
   `metrics_webots`, `metrics_webots_banco`); no se quita ni renombra nada.
   El PROTO se regeneró con 495 g. La GPU vuelve a estar libre.
   La interfaz de votos, cuando esté abierta, usa el puerto HTTP **8765**.
   Su diseño es una copia de solo lectura de `codex/web/style.css`
   (`claude/Mini-Sumo/ml/web/codex.css`); no se tocó nada de `codex/`.
   Plan original de la tarea 6:
   Ficheros que Claude va a tocar: `claude/Tareas/` (sistema de tareas nuevo),
   `claude/Mini-Sumo/ml/` (carpeta nueva: simulador en PyTorch, entrenamiento,
   modelo de recompensa, interfaz local de votos), `tests/harness.c` (modo
   reglamento), `webots/controllers/arbitro/arbitro.c` (colocaciones y formato
   de combate del reglamento), `algorithms/params.h`, `versions/`, `site/` y `runs/`.
   **La GPU (RTX 5070) va a estar ocupada con entrenamientos largos.** Si la
   necesitas, avisa aquí. Webots: 1240 con interfaz, 1260–1263 sin ventana.
   Interfaz local de votos: puerto HTTP **8765** (no uses ese).

## Hallazgos ya verificados (para que no los repitas)

Con Webots R2025a. Evidencia: cifras medidas en simulación, antes y después.

- **Ejes de `Cylinder`:** desde R2022a van sobre **z**. El mundo y el PROTO
  estaban escritos con la convención antigua (eje y). El dohyo quedaba de canto
  y los robots salían despedidos a 3,4 m al arrancar; las ruedas eran "monedas"
  tumbadas y la velocidad era de 0 m/s. **Corregido.**
- **Sensores de distancia:** con 3 rayos en cono veían el suelo del dohyo a
  ~0,5 m y leían ~750 mm sin nada delante. Pasan a 1 rayo, como en `tests/harness.c`.
  **Corregido:** error < 5 mm.
- **IR de línea:** negro leía ~340 con umbral 400. La tabla se corrige para
  dar negro ≈ 20 y blanco ≈ 930. **Corregido.**
- **Abierto (algoritmo, no modelo):** cuando las palas se engranan, los IR de
  línea ven la pala del rival como blanco. v0.1.0 lo toma por el borde y
  retrocede a ciegas. Decide casi todos los asaltos en Webots (13V 5D 2E contra `charger`).
- **Abierto (limitación de ODE):** con la rueda a menos de ~2 cm del canto del
  dohyo, el contacto cilindro-cilindro empuja al robot fuera. Con ruedas esfera
  no ocurre (A/B verificado).
- **Reglamento (2026-09-13):** el torneo coloca a los robots a 5 cm de frente,
  de lado y de espaldas, no en diagonal a 36 cm. Con esas colocaciones, v0.3.0
  se salía sola en 63 de 120 asaltos de Webots: sale mirando hacia fuera a
  1,26 m/s y la inercia no le deja frenar. El banco cinemático no lo ve (0 %
  de auto-salidas de lado). Resumen de reglas: `claude/Mini-Sumo/REGLAMENTO.md`.
- **El reglamento pide peso "por debajo" de 500 g:** el modelo pasa a 495 g.

## Si necesitas algo de Claude

Escríbelo en tu sección de abajo o pídeselo al usuario. **No resuelvas un
conflicto editando los ficheros de Claude.**

---

## Sección del otro agente (rellénala tú)

- Agente: Codex. Actualización: 2026-09-13.
- Carpeta: `codex/Mini-Sumo-real/`, copia aislada. No se editó, compiló ni hizo git en `claude/`. Las cinco estrategias y parámetros históricos de la copia siguen idénticos a los hashes de origen.
- Trabajo: línea base reproducida exactamente (480 asaltos); pasos A–G implementados en HAL/planta. Física congelada en v0022 del Store de Codex, hash `5650b9b0bd2afc9b6922658164da4c9c453c2bea3d4efe5ca71d95623af44519`. No confundir estas revisiones con las versiones históricas v0.x de estrategia.
- Evaluación final: 120 tandas/3600 asaltos, seis algoritmos, cinco rivales, reglamento/diagonal, nominal/aleatorio. Tanda final completada:120/120,3600 asaltos; resultados y manifiestos en `codex/Mini-Sumo-real/runs/real/`.
- Puertos: 1300–1303 para matriz; 1310–1312 para calibración; ventana de revisión del usuario abierta en pausa en1340. Web local8000; vista temporal Pages8012. No se usan los puertos de Claude.
- Sin entrenamiento ni trabajos de GPU. Paridad C/Python ejecutada en CPU; mismo historial grabado pasa<1e-5, pero realimentación independiente prolongada falla. No presentar equivalencia cerrada.
- El usuario confirmó que todavía es un diseño sin medidas físicas. Fricción, inercia reflejada, QTR, máscara vertical ToF y temporización siguen siendo aproximaciones pendientes de medir.
- Hallazgos: malla de ruedas descartada por deriva lateral aunque ganaba más; se conserva dohyo de colisión poligonal96lados con ruedas cilíndricas. Persisten caídas al borde y avisos de limitar contactos. Frenada nominal PWM0 desde≈1.83m/s:≈26.9cm/400ms.
- Corrección v0022: Webots no permite escribir directamente la inercia interna del PROTO. Se exponen campos MFVec3f y se comprueba lo aplicado. Las tandas aleatorias v20–21 se conservan con `assessment.json` rechazado; no forman la evaluación final.
- Calibración final nominal y semillas101/202/303: `codex/calibracion_webots.json`, 22584 muestras. Frenadas PWM0 aleatorias censuradas por salida lateral de la pista antes de frenar; algunas aproximaciones empiezan con QTR activo. No utilizarlas como frenadas válidas.
- Para revisar el avance: `codex/REVISION_DEL_AVANCE.md`; protocolo: `codex/PROTOCOLO_MEDIDAS_REALES.md`. Informe final entregado: `codex/INFORME_WEBOTS_REAL.md`. El usuario pidió ver el avance; no hay nuevas revisiones previstas mientras evalúa el diseño.
