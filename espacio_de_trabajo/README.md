# Espacio de trabajo (copia)

En la PC original, `Mini-Sumo/` vive dentro de `Gelatina_Nuclear/claude/`, y
estos ficheros quedan fuera del repositorio. Esta carpeta es una copia del
13-09-2026 y solo existe en la rama `ejemplo`.

| Aquí | En la PC original | Qué es |
|---|---|---|
| `COORDINACION_LLM.md` | `Gelatina_Nuclear/COORDINACION_LLM.md` | Tablero de coordinación entre agentes |
| `claude/Tareas/` | `Gelatina_Nuclear/claude/Tareas/` | Sistema de tareas: `tareas.txt`, `tareas.py`, `TAREAS.md` |
| `claude/AGENTS.md` | `Gelatina_Nuclear/claude/AGENTS.md` | Aviso para otros agentes |
| `claude/worlds/Sumo.wbt` | `Gelatina_Nuclear/claude/worlds/Sumo.wbt` | Mundo inicial del proyecto de Webots |

## Rehacer el mismo árbol en otra PC

Los programas (`ml/servidor.py`, `tools/build_site.py`) buscan `Tareas/` un
nivel por encima de `Mini-Sumo/`, como en la PC original:

    mkdir -p Gelatina_Nuclear/claude && cd Gelatina_Nuclear
    git clone -b ejemplo git@github.com:ByEmmanuel/Mini-Sumo.git claude/Mini-Sumo
    cp -r claude/Mini-Sumo/espacio_de_trabajo/claude/. claude/
    cp claude/Mini-Sumo/espacio_de_trabajo/COORDINACION_LLM.md .

## Lo que falta a propósito

`claude/Extras/Reglamento de MINISUMO II .pdf`: este repositorio es público y
el PDF es de la organización del torneo. Cópialo a mano a
`Gelatina_Nuclear/claude/Extras/`. Su resumen, regla por regla, está en
`REGLAMENTO.md`.
