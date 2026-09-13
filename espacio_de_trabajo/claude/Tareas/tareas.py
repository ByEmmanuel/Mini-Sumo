#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tareas.py -- sistema de tareas de Gelatina Nuclear.

La bandeja de entrada es tareas.txt: el usuario escribe una tarea por linea,
en texto libre, bajo una cabecera "Lista de tareas ... <fecha> V<n>". Este
script la importa a tareas.json, que es la fuente de verdad; lleva el estado
de cada tarea con su evidencia y regenera TAREAS.md, el tablero legible.

tareas.txt no se modifica nunca: cada linea se reconoce por su huella, asi
que importar dos veces no duplica nada.

    python3 Tareas/tareas.py importar
    python3 Tareas/tareas.py lista [--todas]
    python3 Tareas/tareas.py siguiente
    python3 Tareas/tareas.py ver T-003
    python3 Tareas/tareas.py nueva "texto" [--prioridad alta] [--padre T-003]
    python3 Tareas/tareas.py editar T-003 [--prioridad] [--responsable] [--criterio] [--etiqueta] [--depende]
    python3 Tareas/tareas.py empezar T-003
    python3 Tareas/tareas.py nota T-003 "texto"
    python3 Tareas/tareas.py hecha T-003 --evidencia "que se hizo" [--ruta fichero]...
    python3 Tareas/tareas.py bloquear T-003 --motivo "por que"
    python3 Tareas/tareas.py descartar T-003 --motivo "por que"
    python3 Tareas/tareas.py reabrir T-003 --motivo "por que"
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

DIR = Path(__file__).resolve().parent
BANDEJA = DIR / "tareas.txt"
DATOS = DIR / "tareas.json"
TABLERO = DIR / "TAREAS.md"

ESTADOS = ["pendiente", "en_curso", "bloqueada", "hecha", "descartada"]
PRIORIDADES = ["alta", "media", "baja"]
RESPONSABLES = ["claude", "codex", "usuario"]

CABECERA = re.compile(r"^\s*lista de tareas\b", re.IGNORECASE)
ID_LISTA = re.compile(r"(\d{1,2}-\d{1,2}-\d{2,4})\s*(v\s*\d+)?", re.IGNORECASE)
VINETA = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")


# --------------------------------------------------------------------------
# utilidades
# --------------------------------------------------------------------------

def ahora() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def die(msg: str, code: int = 1):
    print(f"[tareas] ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def normaliza(texto: str) -> str:
    """Minusculas, sin acentos y con espacios colapsados: la identidad de una linea."""
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(t.lower().split())


def huella(texto: str) -> str:
    return hashlib.sha256(normaliza(texto).encode("utf-8")).hexdigest()[:16]


def cargar() -> dict:
    if not DATOS.exists():
        return {"esquema": 1, "listas": [], "tareas": []}
    return json.loads(DATOS.read_text(encoding="utf-8"))


def guardar(d: dict):
    DATOS.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    TABLERO.write_text(tablero_md(d), encoding="utf-8")


def buscar(d: dict, tid: str) -> dict:
    tid = tid.upper()
    if not tid.startswith("T-"):
        tid = "T-" + tid.zfill(3)
    for t in d["tareas"]:
        if t["id"] == tid:
            return t
    die(f"no existe la tarea {tid}")


def nuevo_id(d: dict) -> str:
    n = max((int(t["id"][2:]) for t in d["tareas"]), default=0)
    return f"T-{n + 1:03d}"


def crear(d: dict, texto: str, origen: dict, prioridad="media", padre=None) -> dict:
    t = {
        "id": nuevo_id(d),
        "texto": texto.strip(),
        "huella": huella(texto),
        "origen": origen,
        "estado": "pendiente",
        "prioridad": prioridad,
        "responsable": "claude",
        "etiquetas": [],
        "criterio": "",
        "depende_de": [],
        "padre": padre,
        "creada": ahora(),
        "actualizada": ahora(),
        "evidencia": [],
        "notas": [],
        "historial": [],
    }
    d["tareas"].append(t)
    return t


def cambia_estado(t: dict, nuevo: str, motivo: str = ""):
    if t["estado"] == nuevo:
        return
    t["historial"].append({"fecha": ahora(), "de": t["estado"], "a": nuevo, "motivo": motivo})
    t["estado"] = nuevo
    t["actualizada"] = ahora()


def hijas(d: dict, t: dict) -> list[dict]:
    return [x for x in d["tareas"] if x.get("padre") == t["id"]]


def bloqueantes(d: dict, t: dict) -> list[str]:
    """Dependencias que aun no estan hechas."""
    por_id = {x["id"]: x for x in d["tareas"]}
    return [i for i in t.get("depende_de", []) if por_id.get(i, {}).get("estado") != "hecha"]


# --------------------------------------------------------------------------
# importacion de la bandeja
# --------------------------------------------------------------------------

def parsea_bandeja(texto: str) -> list[tuple[str, int, str]]:
    """Devuelve (lista, numero_de_linea, texto) por cada tarea de tareas.txt."""
    lista = "sin-lista"
    out = []
    for n, linea in enumerate(texto.splitlines(), start=1):
        limpia = linea.strip()
        if not limpia or limpia.startswith("#"):
            continue
        if CABECERA.match(limpia):
            m = ID_LISTA.search(limpia)
            if m:
                lista = m.group(1) + (" " + m.group(2).replace(" ", "").upper() if m.group(2) else "")
            else:
                lista = limpia
            continue
        out.append((lista, n, VINETA.sub("", limpia)))
    return out


def cmd_importar(a):
    if not BANDEJA.exists():
        die(f"no existe {BANDEJA.name}")
    d = cargar()
    vistas = {t["huella"] for t in d["tareas"]}
    nuevas = 0
    for lista, n, texto in parsea_bandeja(BANDEJA.read_text(encoding="utf-8")):
        if huella(texto) in vistas:
            continue
        if lista not in [x["id"] for x in d["listas"]]:
            d["listas"].append({"id": lista, "fichero": BANDEJA.name, "importada": ahora()})
        t = crear(d, texto, {"fichero": BANDEJA.name, "linea": n, "lista": lista})
        vistas.add(t["huella"])
        nuevas += 1
        print(f"  + {t['id']}  {t['texto']}")
    guardar(d)
    print(f"[tareas] {nuevas} tarea(s) nueva(s). Tablero: {TABLERO.name}")


# --------------------------------------------------------------------------
# comandos de estado
# --------------------------------------------------------------------------

def cmd_nueva(a):
    d = cargar()
    padre = buscar(d, a.padre)["id"] if a.padre else None
    t = crear(d, a.texto, {"fichero": None, "linea": None, "lista": a.lista or "claude"},
              prioridad=a.prioridad, padre=padre)
    if a.responsable:
        t["responsable"] = a.responsable
    if a.criterio:
        t["criterio"] = a.criterio
    guardar(d)
    print(f"[tareas] creada {t['id']}: {t['texto']}")


def cmd_editar(a):
    d = cargar()
    t = buscar(d, a.id)
    if a.texto:
        t["texto"] = a.texto
    if a.prioridad:
        t["prioridad"] = a.prioridad
    if a.responsable:
        t["responsable"] = a.responsable
    if a.criterio is not None:
        t["criterio"] = a.criterio
    for e in a.etiqueta or []:
        if e not in t["etiquetas"]:
            t["etiquetas"].append(e)
    for dep in a.depende or []:
        dep_id = buscar(d, dep)["id"]
        if dep_id not in t["depende_de"]:
            t["depende_de"].append(dep_id)
    t["actualizada"] = ahora()
    guardar(d)
    print(f"[tareas] {t['id']} actualizada")


def cmd_empezar(a):
    d = cargar()
    t = buscar(d, a.id)
    pend = bloqueantes(d, t)
    if pend and not a.forzar:
        die(f"{t['id']} depende de {', '.join(pend)}, que no estan hechas (usa --forzar)")
    cambia_estado(t, "en_curso", a.motivo or "")
    guardar(d)
    print(f"[tareas] {t['id']} en curso")


def cmd_nota(a):
    d = cargar()
    t = buscar(d, a.id)
    t["notas"].append({"fecha": ahora(), "texto": a.texto})
    t["actualizada"] = ahora()
    guardar(d)
    print(f"[tareas] nota anadida a {t['id']}")


def cmd_hecha(a):
    d = cargar()
    t = buscar(d, a.id)
    abiertas = [h["id"] for h in hijas(d, t) if h["estado"] not in ("hecha", "descartada")]
    if abiertas and not a.forzar:
        die(f"{t['id']} tiene subtareas abiertas: {', '.join(abiertas)} (usa --forzar)")
    if not a.evidencia:
        die("una tarea no se da por hecha sin --evidencia: que se hizo y donde se comprueba")
    rutas = a.ruta or []
    faltan = [r for r in rutas if not (DIR.parent / r).exists() and not Path(r).exists()]
    if faltan:
        die("la evidencia apunta a rutas que no existen: " + ", ".join(faltan))
    t["evidencia"].append({"fecha": ahora(), "texto": a.evidencia, "rutas": rutas})
    cambia_estado(t, "hecha", a.evidencia[:120])
    guardar(d)
    print(f"[tareas] {t['id']} hecha")


def _cambio_con_motivo(estado: str):
    def run(a):
        d = cargar()
        t = buscar(d, a.id)
        cambia_estado(t, estado, a.motivo)
        if a.motivo:
            t["notas"].append({"fecha": ahora(), "texto": f"[{estado}] {a.motivo}"})
        guardar(d)
        print(f"[tareas] {t['id']} -> {estado}")
    return run


# --------------------------------------------------------------------------
# lectura
# --------------------------------------------------------------------------

ORDEN_P = {p: i for i, p in enumerate(PRIORIDADES)}


def ordenadas(ts: list[dict]) -> list[dict]:
    return sorted(ts, key=lambda t: (ORDEN_P.get(t["prioridad"], 9), t["id"]))


def cmd_lista(a):
    d = cargar()
    ts = d["tareas"] if a.todas else [t for t in d["tareas"] if t["estado"] not in ("hecha", "descartada")]
    if not ts:
        print("[tareas] no hay tareas abiertas")
        return
    print(f"\n  {'ID':<6} {'ESTADO':<11} {'PRIO':<6} {'QUIEN':<8} TAREA")
    print("  " + "-" * 86)
    for t in ordenadas(ts):
        sangria = "  " if t.get("padre") else ""
        print(f"  {t['id']:<6} {t['estado']:<11} {t['prioridad']:<6} {t['responsable']:<8} {sangria}{t['texto'][:60]}")
    print()


def cmd_siguiente(a):
    d = cargar()
    cands = [t for t in d["tareas"] if t["estado"] in ("pendiente", "en_curso") and not bloqueantes(d, t)]
    if not cands:
        print("[tareas] nada disponible: todo hecho o bloqueado por dependencias")
        return
    en_curso = [t for t in cands if t["estado"] == "en_curso"]
    t = ordenadas(en_curso or cands)[0]
    print(f"[tareas] siguiente: {t['id']} ({t['estado']}, {t['prioridad']})  {t['texto']}")
    if t["criterio"]:
        print(f"         criterio: {t['criterio']}")


def cmd_ver(a):
    d = cargar()
    t = buscar(d, a.id)
    print(json.dumps(t, indent=2, ensure_ascii=False))


# --------------------------------------------------------------------------
# tablero
# --------------------------------------------------------------------------

SECCIONES = [
    ("en_curso", "En curso"),
    ("pendiente", "Pendientes"),
    ("bloqueada", "Bloqueadas"),
    ("hecha", "Hechas"),
    ("descartada", "Descartadas"),
]


def _fecha(s: str) -> str:
    return s[:16].replace("T", " ") if s else ""


def _bloque(d: dict, t: dict, nivel: int = 0) -> list[str]:
    pre = "  " * nivel
    marca = "x" if t["estado"] == "hecha" else " "
    extra = [t["prioridad"], t["responsable"]]
    if t["etiquetas"]:
        extra.append(", ".join(t["etiquetas"]))
    if t["estado"] == "hecha":
        extra.append("hecha " + _fecha(t["actualizada"]))
    out = [f"{pre}- [{marca}] **{t['id']}** {t['texto']}  ·  _{' · '.join(extra)}_"]
    if t["origen"].get("linea"):
        out.append(f"{pre}  - Origen: `{t['origen']['fichero']}` línea {t['origen']['linea']} (lista {t['origen']['lista']})")
    if t["criterio"]:
        out.append(f"{pre}  - Criterio de hecho: {t['criterio']}")
    pend = bloqueantes(d, t)
    if t["depende_de"]:
        out.append(f"{pre}  - Depende de: {', '.join(t['depende_de'])}" + (f" (faltan {', '.join(pend)})" if pend else ""))
    for e in t["evidencia"]:
        rutas = "".join(f" `{r}`" for r in e["rutas"])
        out.append(f"{pre}  - Evidencia ({_fecha(e['fecha'])}): {e['texto']}{rutas}")
    for n in t["notas"][-3:]:
        out.append(f"{pre}  - Nota ({_fecha(n['fecha'])}): {n['texto']}")
    for h in ordenadas(hijas(d, t)):
        out.extend(_bloque(d, h, nivel + 1))
    return out


def tablero_md(d: dict) -> str:
    ts = d["tareas"]
    cuenta = {e: sum(1 for t in ts if t["estado"] == e) for e in ESTADOS}
    L = [
        "# Tablero de tareas — Gelatina Nuclear",
        "",
        "> Generado por `Tareas/tareas.py`. **No lo edites a mano.** Las tareas nuevas",
        "> se escriben en `Tareas/tareas.txt`, una por línea, y entran con",
        "> `python3 Tareas/tareas.py importar`. Una tarea solo pasa a hecha con evidencia.",
        "",
        f"Actualizado: {_fecha(ahora())} · {len(ts)} tareas · "
        + " · ".join(f"{cuenta[e]} {e.replace('_', ' ')}" for e in ESTADOS if cuenta[e]),
        "",
    ]
    for estado, titulo in SECCIONES:
        raices = [t for t in ts if t["estado"] == estado and not t.get("padre")]
        # una subtarea cuyo padre esta en otra seccion se lista en la suya
        sueltas = [t for t in ts if t["estado"] == estado and t.get("padre")
                   and next((p for p in ts if p["id"] == t["padre"]), {}).get("estado") != estado]
        if not raices and not sueltas:
            continue
        L += [f"## {titulo}", ""]
        for t in ordenadas(raices):
            L += _bloque(d, t)
        for t in ordenadas(sueltas):
            L += _bloque(d, t)
        L.append("")
    return "\n".join(L).rstrip() + "\n"


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(prog="tareas", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("importar", help="lee tareas.txt y anade las lineas nuevas").set_defaults(func=cmd_importar)

    p = sub.add_parser("lista", help="tareas abiertas")
    p.add_argument("--todas", action="store_true")
    p.set_defaults(func=cmd_lista)

    sub.add_parser("siguiente", help="la proxima tarea disponible").set_defaults(func=cmd_siguiente)

    p = sub.add_parser("ver", help="detalle completo de una tarea")
    p.add_argument("id")
    p.set_defaults(func=cmd_ver)

    p = sub.add_parser("nueva", help="crea una tarea (o subtarea con --padre)")
    p.add_argument("texto")
    p.add_argument("--prioridad", choices=PRIORIDADES, default="media")
    p.add_argument("--responsable", choices=RESPONSABLES)
    p.add_argument("--criterio")
    p.add_argument("--padre")
    p.add_argument("--lista")
    p.set_defaults(func=cmd_nueva)

    p = sub.add_parser("editar", help="cambia metadatos de una tarea")
    p.add_argument("id")
    p.add_argument("--texto")
    p.add_argument("--prioridad", choices=PRIORIDADES)
    p.add_argument("--responsable", choices=RESPONSABLES)
    p.add_argument("--criterio")
    p.add_argument("--etiqueta", action="append")
    p.add_argument("--depende", action="append")
    p.set_defaults(func=cmd_editar)

    p = sub.add_parser("empezar")
    p.add_argument("id")
    p.add_argument("--motivo")
    p.add_argument("--forzar", action="store_true")
    p.set_defaults(func=cmd_empezar)

    p = sub.add_parser("nota")
    p.add_argument("id")
    p.add_argument("texto")
    p.set_defaults(func=cmd_nota)

    p = sub.add_parser("hecha")
    p.add_argument("id")
    p.add_argument("--evidencia", required=True)
    p.add_argument("--ruta", action="append", help="fichero que lo demuestra, relativo a claude/")
    p.add_argument("--forzar", action="store_true")
    p.set_defaults(func=cmd_hecha)

    for nombre, estado in (("bloquear", "bloqueada"), ("descartar", "descartada"), ("reabrir", "pendiente")):
        p = sub.add_parser(nombre)
        p.add_argument("id")
        p.add_argument("--motivo", required=True)
        p.set_defaults(func=_cambio_con_motivo(estado))

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
