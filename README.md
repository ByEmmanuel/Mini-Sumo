# Gelatina Nuclear

Robot **mini-sumo** de competición: 10 × 10 cm, 500 g máximo, objetivo tirar al
rival fuera del dohyo. Se diseña y se mide en **Webots**, y está escrito para
acabar corriendo en el robot físico sin reescribir el algoritmo.

El proyecto avanza por iteraciones sucesivas, y **cada cambio en el sistema de
control queda registrado en una bitácora navegable**:

📊 **[Bitácora de algoritmos](https://claude.ai/code/artifact/2fe653b8-287f-46ce-abb4-0ef248b5941d)** — qué cambió, por qué, y qué resultado dio en el ring.

---

## La idea en una frase

El algoritmo no sabe dónde corre. `algorithms/strategy.c` consume un
`sumo_sensors_t` y produce un `sumo_actuators_t`; nada más. La plataforma entra
por detrás, a través de `hal.h`:

```
                    ┌──────────────────────────┐
                    │  algorithms/strategy.c   │   <- lo que versiona la bitácora
                    │  (C99 puro, sin deps)    │
                    └────────────┬─────────────┘
                                 │  sumo_types.h
              ┌──────────────────┼──────────────────┐
              │                  │                  │
       hal_webots.c        tests/harness.c     hal_<mcu>.c
       (simulación)        (banco nativo)      (robot real, pendiente)
```

Portar Gelatina Nuclear al hardware real consiste en escribir un backend nuevo.
Ni una línea de la estrategia cambia.

## Estructura

| Ruta | Qué es |
|---|---|
| `algorithms/` | **El cerebro.** Lógica pura versionada: contrato, parámetros y máquina de estados. |
| `webots/protos/` | El robot: geometría, masas, 5 sensores de distancia, 4 de línea, IMU, encoders. |
| `webots/worlds/dohyo.wbt` | Dohyo reglamentario de 770 mm con banda blanca de 25 mm. |
| `webots/controllers/gelatina_nuclear/` | Lazo de control y backend de Webots. |
| `webots/controllers/oponente/` | Rivales de referencia. Es el examen, no el alumno. |
| `webots/controllers/arbitro/` | Supervisor: coloca, arbitra, cuenta y exporta métricas. |
| `tests/harness.c` | Ring simulado sin Webots. 240 asaltos en milisegundos. |
| `tools/gnver.py` | La bitácora de algoritmos. |
| `tools/build_site.py` | Genera la página de la bitácora. |
| `versions/` | Una carpeta por versión: metadatos, instantánea del código y diff. |

## Uso

```bash
make medir     # compila el algoritmo y lo mide contra los 4 rivales
make check     # falla si hay código de control sin versionar
make sitio     # regenera site/index.html
```

`make medir` no necesita Webots y tarda menos de un segundo. Es el sparring
diario; Webots es el juez final.

## Ejecutar en Webots

Webots no está instalado todavía en esta máquina. En Arch:

```bash
yay -S webots-bin          # o descargar de https://cyberbotics.com/
export WEBOTS_HOME=/usr/local/webots
make links                 # rehace los enlaces del controlador
webots webots/worlds/dohyo.wbt
```

Webots compila los controladores solo al abrir el mundo. Para una tanda de
combates automatizada, el árbitro ya está en el mundo: escribe
`runs/webots_ultimo.json`, que se carga en la bitácora con
`python3 tools/gnver.py metrics vX.Y.Z --from runs/webots_ultimo.json`.

Si abres el mundo sin árbitro, los robots se arman solos a los 5 s, que es el
retardo que exige el reglamento.

### Calibrar los sensores de línea

El umbral de línea (`LINE_TH_DEFAULT = 400` en `hal_webots.c`) es un valor de
partida. Para verificar las lecturas reales, arranca el controlador con
`controllerArgs [ "--calib" ]` y observa la consola: sobre negro debería leer
cerca de 20 y sobre la banda blanca cerca de 900.

## Estado actual

**v0.1.0** — línea base. Máquina de estados reactiva de seis estados con
prioridad absoluta del borde. Win rate del 48,8 % sobre el banco: gana siempre
al rival que gira, gana 3 de cada 4 al inmóvil, y **pierde 4 de cada 5 contra
el rival agresivo**. 19 de sus 63 derrotas son auto-expulsiones sin contacto,
es decir, fallos del escape de borde y no del combate.

Ahí es donde apunta la siguiente iteración.
