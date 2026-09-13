# Tareas

Tres ficheros, cada uno con un papel:

| Fichero | Quién lo escribe | Para qué |
|---|---|---|
| `tareas.txt` | **El usuario**, a mano | Bandeja de entrada. Una tarea por línea, en texto libre. |
| `tareas.json` | `tareas.py` | Fuente de verdad: estado, prioridad, responsable, criterio, evidencia e historial de cada tarea. |
| `TAREAS.md` | `tareas.py` | Tablero legible. Se regenera en cada cambio; no se edita a mano. |

## Añadir tareas

Escribe en `tareas.txt`. Una lista nueva empieza con una cabecera como la que ya
hay, con fecha y número de versión:

```text
Lista de tareas por cumplir en el proyecto 14-09-26 V2

Probar el robot contra una caja
Medir el peso real de la batería
```

Luego, desde `claude/`:

```bash
python3 Tareas/tareas.py importar
```

`tareas.txt` no se modifica nunca. Cada línea se reconoce por su huella (el
texto sin acentos, mayúsculas ni espacios de más), así que importar dos veces
no duplica nada. Si reescribes una tarea ya importada, entra como tarea nueva:
descarta la antigua con `descartar`.

## Llevar el estado

```bash
python3 Tareas/tareas.py lista                 # abiertas, por prioridad
python3 Tareas/tareas.py siguiente             # la próxima disponible
python3 Tareas/tareas.py empezar T-003
python3 Tareas/tareas.py nota T-003 "texto"
python3 Tareas/tareas.py hecha T-003 --evidencia "qué se hizo" --ruta Mini-Sumo/ml/README.md
python3 Tareas/tareas.py bloquear T-003 --motivo "por qué"
python3 Tareas/tareas.py nueva "texto" --padre T-003    # subtarea
```

Reglas que el script hace cumplir:

- **Nada pasa a hecho sin evidencia.** `hecha` exige `--evidencia`, y cada
  `--ruta` debe existir.
- **Una tarea con subtareas abiertas no se cierra.**
- **Las dependencias se respetan.** `empezar` se niega si falta una tarea de
  `depende_de` (con `--forzar` se salta, y queda en el historial).
- Cada cambio de estado queda en el historial con fecha y motivo.

Cada tarea tiene un **criterio de hecho**: la condición concreta que la cierra.
Sin él, "hecho" es una opinión.
