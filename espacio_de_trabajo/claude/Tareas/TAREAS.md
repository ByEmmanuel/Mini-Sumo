# Tablero de tareas — Gelatina Nuclear

> Generado por `Tareas/tareas.py`. **No lo edites a mano.** Las tareas nuevas
> se escriben en `Tareas/tareas.txt`, una por línea, y entran con
> `python3 Tareas/tareas.py importar`. Una tarea solo pasa a hecha con evidencia.

Actualizado: 2026-09-13 09:00 · 13 tareas · 1 pendiente · 12 hecha

## Pendientes

- [ ] **T-006** Ir dando retroalimentacion al modelo  ·  _alta · usuario · ml_
  - Origen: `tareas.txt` línea 13 (lista 13-09-26 V1)
  - Criterio de hecho: El usuario vota comparaciones A/B en la interfaz local; el modelo de recompensa se reentrena con esos votos y guía la siguiente tanda de entrenamiento.
  - Depende de: T-003
  - Nota (2026-09-13 08:58): Hay 12 comparaciones reales esperando voto: v0.3.1 (c-001) contra v0.3.0. Arranca la interfaz con: cd Mini-Sumo && ml/.venv/bin/python -m ml servidor
  - [x] **T-013** Interfaz local de votos A/B con repeticiones de asaltos  ·  _alta · claude · hecha 2026-09-13 08:58_
    - Evidencia (2026-09-13 08:58): Interfaz en ml/web servida por ml/servidor.py (:8765): repeticiones A/B sincronizadas, voto con clic y teclado, etiquetas y nota; probada en el navegador con datos de prueba `Mini-Sumo/ml/web/app.js` `Mini-Sumo/ml/servidor.py`

## Hechas

- [x] **T-001** Leer el reglamento  ·  _alta · claude · reglamento · hecha 2026-09-13 08:42_
  - Origen: `tareas.txt` línea 3 (lista 13-09-26 V1)
  - Criterio de hecho: Resumen del reglamento con cada regla enlazada a su efecto en el proyecto: cumple, ajustado o pendiente.
  - Evidencia (2026-09-13 08:42): Reglamento leído entero (24 págs.); cada regla enlazada a su estado en el proyecto `Mini-Sumo/REGLAMENTO.md`
- [x] **T-002** Ajustar el proyecto que llevamos hasta ahora dependiendo de lo que dice el reglamento  ·  _alta · claude · reglamento · hecha 2026-09-13 08:58_
  - Origen: `tareas.txt` línea 5 (lista 13-09-26 V1)
  - Criterio de hecho: Colocaciones del reglamento (frente, lado y espalda a 5 cm) y combate a 3 rondas en el banco nativo, el simulador de GPU y el árbitro de Webots; versiones anteriores medidas otra vez en ese modo.
  - Depende de: T-001
  - Evidencia (2026-09-13 08:58): Modo reglamento en banco en C, GPU y árbitro; 495 g y pulsador de arranque. Webots con reglamento: v0.3.0 combate 25,9 % con 63 auto-salidas; v0.3.1 100 % sin auto-salidas `Mini-Sumo/REGLAMENTO.md` `Mini-Sumo/runs/webots_v0.3.0_reglamento.json` `Mini-Sumo/runs/webots_c-001_reglamento.json`
  - Nota (2026-09-13 08:42): Hecho: modo --reglamento en harness.c (modo de siempre idéntico), GPU y árbitro; 495 g y pulsador de arranque en hardware/. Falta: tanda de Webots con el reglamento.
- [x] **T-003** Realizar un modelo de aprendizaje supervizado por refuerzo de cada algoritmo  ·  _alta · claude · ml · hecha 2026-09-13 09:00_
  - Origen: `tareas.txt` línea 7 (lista 13-09-26 V1)
  - Criterio de hecho: Entrenamiento en GPU de cada algoritmo de movimiento (máquina de estados parametrizada y política neuronal), guiado por un modelo de recompensa aprendido de las preferencias del usuario.
  - Evidencia (2026-09-13 09:00): Dos algoritmos de movimiento entrenados en GPU con modelo de recompensa humana: máquina de estados por CMA-ES (resultado v0.3.1) y política neuronal por PPO. Ciclo completo en python -m ml ciclo `Mini-Sumo/ml/README.md`
  - [x] **T-008** Port vectorizado de strategy.c para evaluar miles de juegos de parámetros a la vez  ·  _alta · claude · hecha 2026-09-13 08:42_
    - Evidencia (2026-09-13 08:42): fsm.py reproduce strategy.c línea a línea; validado con v0.1.0 a v0.3.0 `Mini-Sumo/ml/fsm.py`
  - [x] **T-009** Estrategia evolutiva (CMA-ES) sobre los parámetros de la máquina de estados  ·  _alta · claude · hecha 2026-09-13 08:42_
    - Evidencia (2026-09-13 08:42): CMA-ES en es.py; primera corrida: campeón c-001, derrotas en el banco en C de 38 a 2 (modo banco) y de 66 a 5 (modo reglamento) `Mini-Sumo/ml/es.py` `Mini-Sumo/ml/data/banco_c_c-001.json`
  - [x] **T-010** Modelo de recompensa por preferencias humanas (Bradley-Terry con un conjunto de redes)  ·  _alta · claude · hecha 2026-09-13 08:42_
    - Evidencia (2026-09-13 08:42): recompensa.py: Bradley-Terry, 5 redes con bootstrap, cabeza lineal, validación cruzada; ciclo probado con votos sintéticos en datos aparte (no del usuario) `Mini-Sumo/ml/recompensa.py`
  - [x] **T-011** Liga de versiones y dirección de mejora: hacia qué parámetros se inclinan las mejores versiones  ·  _alta · claude · hecha 2026-09-13 08:42_
    - Evidencia (2026-09-13 08:42): liga.py: Elo por Bradley-Terry todos contra todos y sustituto neuronal (R2 0,77 en 51.200 muestras) cuyo gradiente da la dirección `Mini-Sumo/ml/liga.py` `Mini-Sumo/ml/data/liga.json`
  - [x] **T-012** Política neuronal entrenada con PPO y exportable a C  ·  _media · claude · hecha 2026-09-13 09:00_
    - Evidencia (2026-09-13 09:00): PPO: 315 M pasos en 490 s; gana el combate a static, charger, spinner y v0.1-v0.3.0 (98-100 %) pero pierde contra v0.3.1; actor exportado a C99 (5.698 pesos, 22 KB, error máximo 5e-7). Sin probar en Webots `Mini-Sumo/ml/ppo.py` `Mini-Sumo/ml/data/politicas/p-20260913-084929-reglamento-1/nn_politica.h`
- [x] **T-005** realizar demasiadas simulaciones de los algoritmos que corran en la GPU  ·  _alta · claude · gpu · hecha 2026-09-13 08:42_
  - Origen: `tareas.txt` línea 11 (lista 13-09-26 V1)
  - Criterio de hecho: Simulador vectorizado en la RTX 5070 validado contra tests/harness.c, con más de 100.000 asaltos por minuto.
  - Evidencia (2026-09-13 08:42): Corrida reglamento-1: 7,4 M asaltos en 184 s en la RTX 5070 (100 gen x 512 candidatos x 144 asaltos) `Mini-Sumo/ml/data/corridas`
  - [x] **T-007** Simulador del dohyo vectorizado en PyTorch, equivalente a tests/harness.c y con las colocaciones del reglamento  ·  _alta · claude · hecha 2026-09-13 08:42_
    - Evidencia (2026-09-13 08:42): Simulador vectorizado en PyTorch; 96 comparaciones contra tests/harness.c con |z| <= 2,1 en 4 versiones y 2 modos; 90.700 asaltos/s con 262.144 entornos `Mini-Sumo/ml/sim.py` `Mini-Sumo/ml/data/validacion.json`
- [x] **T-004** Ir al directorio de Gelatina_Nuclear/codex y utilizar unicamente la pagina web para mostrar los cambios de los algoritmos  ·  _media · claude · web · hecha 2026-09-13 08:58_
  - Origen: `tareas.txt` línea 9 (lista 13-09-26 V1)
  - Criterio de hecho: Los cambios de los algoritmos se ven en una interfaz con el diseño de la web de codex/, sin modificar codex/: se copia el diseño en solo lectura.
  - Evidencia (2026-09-13 08:58): La interfaz de ml/ usa el diseño de la web de codex/ (ml/web/codex.css es copia exacta de codex/web/style.css, mismo sha256); muestra versiones, diffs, entrenamientos, liga, dirección y tareas. codex/ no se modificó `Mini-Sumo/ml/web/codex.css`
- [x] **T-013** Interfaz local de votos A/B con repeticiones de asaltos  ·  _alta · claude · hecha 2026-09-13 08:58_
  - Evidencia (2026-09-13 08:58): Interfaz en ml/web servida por ml/servidor.py (:8765): repeticiones A/B sincronizadas, voto con clic y teclado, etiquetas y nota; probada en el navegador con datos de prueba `Mini-Sumo/ml/web/app.js` `Mini-Sumo/ml/servidor.py`
