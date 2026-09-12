#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py -- genera site/index.html a partir de versions/.

La pagina es autocontenida: lleva dentro el manifiesto y todos los diffs, asi
que funciona abierta con doble clic (file://) y tambien publicada.
Se regenera sola cada vez que gnver crea una version o carga metricas.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSIONS = ROOT / "versions"
SITE = ROOT / "site"


def collect() -> dict:
    manifest = json.loads((VERSIONS / "manifest.json").read_text(encoding="utf-8"))
    for v in manifest["versions"]:
        d = VERSIONS / v["version"] / "diff.patch"
        v["diff"] = d.read_text(encoding="utf-8", errors="replace") if d.exists() else ""
    return manifest


HTML = r"""<title>Bitácora Gelatina Nuclear</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=JetBrains+Mono:wght@400;500;700&display=swap">
<style>
/* ==========================================================================
   Gelatina Nuclear -- bitacora de algoritmos
   Identidad: placa de instrumento de taller. Rotulacion condensada para la
   estructura, serif de cuaderno para el razonamiento, monoespaciada para todo
   lo que escupe la maquina. Neutros sesgados al verde del esmalte de maquina
   herramienta, azul pizarra como color estructural, y semantica aparte.
   ========================================================================== */
:root{
  --fondo:#E3E6E1;
  --placa:#F1F3EF;
  --placa-alt:#E9ECE6;
  --hueco:#D6DAD3;
  --regla:#C3C8BF;
  --regla-fuerte:#A8AFA3;
  --tinta:#1C2220;
  --tinta-media:#4C544E;
  --tinta-suave:#6E766F;
  --azul:#33506E;
  --azul-vivo:#2B6FA8;
  --mejora:#2C6F4C;
  --regresion:#A8412A;
  --neutro:#8A6A12;
  --mejora-fondo:#DCE9E0;
  --regresion-fondo:#F2DFD8;
  --neutro-fondo:#EFE6CF;
  --azul-fondo:#DDE4EC;
  --add-fondo:#DDEBDF;
  --add-tinta:#1F5537;
  --del-fondo:#F3DFDA;
  --del-tinta:#8C3A24;
  --sombra:0 1px 2px rgba(28,34,32,.09), 0 8px 22px -14px rgba(28,34,32,.35);
  --r:3px;
  color-scheme:light dark;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --fondo:#141816;
    --placa:#1D2321;
    --placa-alt:#232A27;
    --hueco:#111513;
    --regla:#333B37;
    --regla-fuerte:#48524D;
    --tinta:#E6EAE5;
    --tinta-media:#A8B1AB;
    --tinta-suave:#808A84;
    --azul:#8FB2D6;
    --azul-vivo:#6FA8DC;
    --mejora:#63BE8E;
    --regresion:#E08064;
    --neutro:#D4AC48;
    --mejora-fondo:#1B2E23;
    --regresion-fondo:#331E18;
    --neutro-fondo:#2E2717;
    --azul-fondo:#1B2632;
    --add-fondo:#16301F;
    --add-tinta:#84D2A4;
    --del-fondo:#331B15;
    --del-tinta:#EE9679;
    --sombra:0 1px 2px rgba(0,0,0,.4), 0 10px 26px -16px rgba(0,0,0,.8);
  }
}
:root[data-theme="dark"]{
  --fondo:#141816; --placa:#1D2321; --placa-alt:#232A27; --hueco:#111513;
  --regla:#333B37; --regla-fuerte:#48524D;
  --tinta:#E6EAE5; --tinta-media:#A8B1AB; --tinta-suave:#808A84;
  --azul:#8FB2D6; --azul-vivo:#6FA8DC;
  --mejora:#63BE8E; --regresion:#E08064; --neutro:#D4AC48;
  --mejora-fondo:#1B2E23; --regresion-fondo:#331E18; --neutro-fondo:#2E2717;
  --azul-fondo:#1B2632;
  --add-fondo:#16301F; --add-tinta:#84D2A4; --del-fondo:#331B15; --del-tinta:#EE9679;
  --sombra:0 1px 2px rgba(0,0,0,.4), 0 10px 26px -16px rgba(0,0,0,.8);
}

*{box-sizing:border-box}
body{
  background:var(--fondo);
  color:var(--tinta);
  font-family:"Source Serif 4",Georgia,"Times New Roman",serif;
  font-size:16px; line-height:1.6;
  margin:0; padding:0;
  -webkit-font-smoothing:antialiased;
}
.envoltorio{max-width:1240px; margin:0 auto; padding-inline:20px; padding-block:0 64px}

h1,h2,h3,.rotulo,.pestana,.chip,.tecla{
  font-family:Oswald,"Arial Narrow",Haettenschweiler,sans-serif;
  font-weight:600; letter-spacing:.02em;
}
.rotulo{
  font-size:11px; text-transform:uppercase; letter-spacing:.14em;
  color:var(--tinta-suave); font-weight:500;
}
code,pre,.dato,.mono{font-family:"JetBrains Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace}
.dato{font-variant-numeric:tabular-nums}

/* ---------------------------------------------------------------- cabecera */
.cabecera{
  border-bottom:2px solid var(--regla-fuerte);
  padding-block:28px 22px;
  display:flex; flex-wrap:wrap; gap:28px; align-items:flex-start;
  justify-content:space-between;
}
.marca{display:flex; gap:18px; align-items:center; min-width:0}
.marca h1{
  margin:2px 0 0; font-size:clamp(30px,5vw,44px); line-height:.98;
  text-transform:uppercase; letter-spacing:.005em; font-weight:700;
  text-wrap:balance;
}
.marca .sub{margin:6px 0 0; color:var(--tinta-media); font-size:14px}
.ring{flex:0 0 auto; width:76px; height:76px}

.mando{display:flex; flex-direction:column; align-items:flex-end; gap:14px}
.tecla{
  background:var(--placa); color:var(--tinta-media);
  border:1px solid var(--regla); border-radius:var(--r);
  padding:7px 13px; font-size:11px; text-transform:uppercase; letter-spacing:.12em;
  cursor:pointer; line-height:1;
}
.tecla:hover{border-color:var(--regla-fuerte); color:var(--tinta)}
.tecla:focus-visible{outline:2px solid var(--azul-vivo); outline-offset:2px}

.marcadores{display:flex; flex-wrap:wrap; gap:26px}
.marcador{display:flex; flex-direction:column; gap:3px}
.marcador .cifra{
  font-family:Oswald,sans-serif; font-weight:600; font-size:27px; line-height:1;
  font-variant-numeric:tabular-nums;
}

/* ------------------------------------------------------------------ curva */
.curva{
  margin-top:26px; background:var(--placa); border:1px solid var(--regla);
  border-radius:var(--r); padding:20px 22px 14px;
}
.curva header{display:flex; justify-content:space-between; align-items:baseline; gap:16px; flex-wrap:wrap}
.curva h2{margin:0; font-size:15px; text-transform:uppercase; letter-spacing:.1em}
.curva .nota{font-size:13px; color:var(--tinta-suave); font-style:italic}
.lienzo{width:100%; height:auto; display:block; margin-top:10px; overflow:visible}

/* -------------------------------------------------------------- estructura */
.disposicion{display:grid; grid-template-columns:250px minmax(0,1fr); gap:28px; margin-top:28px; align-items:start}
@media (max-width:860px){ .disposicion{grid-template-columns:1fr} }

/* ---------------------------------------------------------------- historia */
.historia{border-left:2px solid var(--regla); padding-left:0; display:flex; flex-direction:column}
.historia > .rotulo{padding:0 0 10px 16px}
.hito{
  position:relative; display:block; width:100%; text-align:left;
  background:none; border:0; border-radius:0;
  padding:11px 12px 12px 16px; cursor:pointer; color:inherit;
  font-family:inherit; border-bottom:1px solid var(--regla);
}
.hito::before{
  content:""; position:absolute; left:-6px; top:18px;
  width:9px; height:9px; border-radius:50%;
  background:var(--fondo); border:2px solid var(--regla-fuerte);
}
.hito:hover{background:var(--placa-alt)}
.hito[aria-current="true"]{background:var(--placa)}
.hito[aria-current="true"]::before{background:var(--azul-vivo); border-color:var(--azul-vivo)}
.hito:focus-visible{outline:2px solid var(--azul-vivo); outline-offset:-2px}
.hito .ver{font-family:Oswald,sans-serif; font-weight:600; font-size:16px; letter-spacing:.03em}
.hito .tit{display:block; font-size:13.5px; color:var(--tinta-media); line-height:1.35; margin-top:2px}
.hito .fila{display:flex; align-items:center; gap:8px; flex-wrap:wrap}

/* ------------------------------------------------------------------ chips */
.chip{
  display:inline-block; font-size:10px; text-transform:uppercase; letter-spacing:.1em;
  padding:2.5px 7px; border-radius:2px; line-height:1.4; font-weight:600;
  background:var(--hueco); color:var(--tinta-media); white-space:nowrap;
}
.chip.baseline,.chip.refactor{background:var(--azul-fondo); color:var(--azul)}
.chip.tuning,.chip.experiment{background:var(--neutro-fondo); color:var(--neutro)}
.chip.nuevo{background:var(--mejora-fondo); color:var(--mejora)}
.chip.bugfix,.chip.revert{background:var(--regresion-fondo); color:var(--regresion)}
.chip.v-mejora{background:var(--mejora-fondo); color:var(--mejora)}
.chip.v-regresion{background:var(--regresion-fondo); color:var(--regresion)}
.chip.v-pendiente{background:var(--neutro-fondo); color:var(--neutro)}

/* --------------------------------------------------------------- expediente */
.expediente{min-width:0; display:flex; flex-direction:column; gap:22px}
.titular{border-bottom:2px solid var(--regla-fuerte); padding-bottom:16px}
.titular .linea{display:flex; align-items:baseline; gap:12px; flex-wrap:wrap}
.titular .num{font-family:Oswald,sans-serif; font-weight:700; font-size:34px; letter-spacing:.01em; line-height:1}
.titular h2{margin:8px 0 0; font-size:23px; font-weight:600; line-height:1.2; text-wrap:balance; text-transform:none; letter-spacing:0}
.titular .meta{margin:9px 0 0; font-size:13px; color:var(--tinta-suave)}

.bloque{background:var(--placa); border:1px solid var(--regla); border-radius:var(--r); padding:20px 22px}
.bloque > h3{
  margin:0 0 12px; font-size:11px; text-transform:uppercase; letter-spacing:.14em;
  color:var(--tinta-suave); font-weight:500;
}
.razonamiento{display:grid; gap:18px}
@media (min-width:720px){ .razonamiento{grid-template-columns:1fr 1fr} }
.razonamiento .campo{display:flex; flex-direction:column; gap:5px; min-width:0}
.razonamiento .campo p{margin:0; font-size:15.5px; max-width:62ch; line-height:1.62}
.razonamiento .campo.ancho{grid-column:1/-1}

table{width:100%; border-collapse:collapse; font-size:13.5px}
.tabla-envoltorio{overflow-x:auto}
th{
  text-align:left; font-family:Oswald,sans-serif; font-weight:500; font-size:10.5px;
  text-transform:uppercase; letter-spacing:.11em; color:var(--tinta-suave);
  padding:0 12px 7px 0; border-bottom:1px solid var(--regla); white-space:nowrap;
}
td{padding:8px 12px 8px 0; border-bottom:1px solid var(--regla); vertical-align:top}
tr:last-child td{border-bottom:0}
td.num{font-family:"JetBrains Mono",monospace; font-variant-numeric:tabular-nums; white-space:nowrap}
.flecha{color:var(--tinta-suave); padding-inline:4px}
.de{color:var(--del-tinta)} .a{color:var(--add-tinta); font-weight:700}

/* --------------------------------------------------------------- metricas */
.rivales{display:flex; flex-direction:column; gap:11px}
.rival{display:grid; grid-template-columns:88px minmax(0,1fr) 96px; gap:12px; align-items:center}
@media (max-width:520px){ .rival{grid-template-columns:74px minmax(0,1fr) 78px; gap:8px} }
.rival .nom{font-family:Oswald,sans-serif; font-size:13px; letter-spacing:.04em; text-transform:uppercase; color:var(--tinta-media)}
.barra{height:14px; background:var(--hueco); border-radius:1px; overflow:hidden}
.barra span{display:block; height:100%; background:var(--azul-vivo)}
.rival .cifra{font-family:"JetBrains Mono",monospace; font-size:12.5px; font-variant-numeric:tabular-nums; text-align:right; color:var(--tinta-media)}

/* ------------------------------------------------------------------- diff */
.diff-cab{display:flex; justify-content:space-between; align-items:baseline; gap:14px; flex-wrap:wrap; margin-bottom:12px}
.recuento{font-family:"JetBrains Mono",monospace; font-size:12.5px; font-variant-numeric:tabular-nums}
.recuento .mas{color:var(--add-tinta); font-weight:700}
.recuento .menos{color:var(--del-tinta); font-weight:700}
pre.diff{
  margin:0; background:var(--placa-alt); border:1px solid var(--regla); border-radius:var(--r);
  font-size:12.5px; line-height:1.55; overflow-x:auto; max-height:560px; overflow-y:auto;
  padding:0; tab-size:2;
}
pre.diff .l{display:block; padding:0 14px; white-space:pre}
pre.diff .l.mas{background:var(--add-fondo); color:var(--add-tinta)}
pre.diff .l.menos{background:var(--del-fondo); color:var(--del-tinta)}
pre.diff .l.trozo{background:var(--azul-fondo); color:var(--azul); font-weight:700}
pre.diff .l.arch{color:var(--tinta-suave); font-weight:700; padding-top:8px}
.vacio{font-style:italic; color:var(--tinta-suave); font-size:14px; margin:0}

.ficheros{display:flex; flex-direction:column; gap:0}
.fichero{display:flex; justify-content:space-between; align-items:baseline; gap:14px; padding:7px 0; border-bottom:1px solid var(--regla); font-size:13px; flex-wrap:wrap}
.fichero:last-child{border-bottom:0}
.fichero .ruta{font-family:"JetBrains Mono",monospace; font-size:12.5px; word-break:break-all}
.fichero .ruta.tocado{color:var(--azul-vivo); font-weight:700}
.fichero .der{font-family:"JetBrains Mono",monospace; font-size:11.5px; color:var(--tinta-suave); font-variant-numeric:tabular-nums; white-space:nowrap}

.pie{margin-top:44px; padding-top:18px; border-top:1px solid var(--regla); font-size:13px; color:var(--tinta-suave)}
.pie code{font-size:12.5px; background:var(--hueco); padding:1px 5px; border-radius:2px}

@media (prefers-reduced-motion: reduce){ *{transition:none !important; animation:none !important} }
</style>

<div class="envoltorio">
  <header class="cabecera">
    <div class="marca">
      <svg class="ring" viewBox="0 0 100 100" role="img" aria-label="Dohyo reglamentario de 770 mm con banda blanca de 25 mm">
        <circle cx="50" cy="50" r="48" fill="var(--regla-fuerte)"></circle>
        <circle cx="50" cy="50" r="44.9" fill="var(--tinta)"></circle>
        <rect x="41.5" y="43.6" width="17" height="1.6" fill="var(--fondo)"></rect>
        <rect x="41.5" y="54.8" width="17" height="1.6" fill="var(--fondo)"></rect>
      </svg>
      <div>
        <p class="rotulo" style="margin:0">Bitácora de algoritmos · Webots</p>
        <h1>Gelatina<br>Nuclear</h1>
        <p class="sub">Mini-sumo · 10 × 10 cm · 500 g · control en C portable</p>
      </div>
    </div>
    <div class="mando">
      <button class="tecla" id="tema" type="button">Tema</button>
      <div class="marcadores" id="marcadores"></div>
    </div>
  </header>

  <section class="curva">
    <header>
      <h2>Curva de aprendizaje</h2>
      <p class="nota" id="curva-nota"></p>
    </header>
    <div id="curva-lienzo"></div>
  </section>

  <div class="disposicion">
    <nav class="historia" id="historia" aria-label="Versiones"></nav>
    <section class="expediente" id="expediente"></section>
  </div>

  <footer class="pie">
    <p>Cada entrada la genera <code>tools/gnver.py</code> al registrar una versión.
    El guardián <code>python3 tools/gnver.py check</code> falla si hay código de control
    modificado sin versionar, que es lo que mantiene esta bitácora completa.</p>
  </footer>
</div>

<script type="application/json" id="datos">/*__DATOS__*/</script>
<script>
(function(){
"use strict";
const D = JSON.parse(document.getElementById("datos").textContent);
const V = D.versions || [];

/* ---- tema ------------------------------------------------------------ */
const raiz = document.documentElement;
document.getElementById("tema").addEventListener("click", function(){
  const oscuroAhora = raiz.getAttribute("data-theme") === "dark" ||
    (!raiz.getAttribute("data-theme") && window.matchMedia("(prefers-color-scheme: dark)").matches);
  raiz.setAttribute("data-theme", oscuroAhora ? "light" : "dark");
  pintarCurva();
});

/* ---- utilidades ------------------------------------------------------ */
const esc = s => String(s == null ? "" : s)
  .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
const pct = x => (x == null) ? "—" : (x*100).toFixed(0) + "%";
const claseTipo = k => ({"new-behavior":"nuevo"})[k] || k;
const fecha = s => { try { return new Date(s).toLocaleDateString("es-ES",
  {day:"2-digit",month:"short",year:"numeric"}); } catch(e){ return s; } };

function conMetricas(){ return V.filter(v => (v.metrics||{}).rounds > 0); }

/* ---- marcadores de cabecera ------------------------------------------ */
(function marcadores(){
  const m = conMetricas();
  const ult = V[V.length-1];
  const ultWr = m.length ? m[m.length-1].metrics.win_rate : null;
  const prevWr = m.length > 1 ? m[m.length-2].metrics.win_rate : null;
  let delta = "—", color = "var(--tinta-suave)";
  if (ultWr != null && prevWr != null) {
    const d = (ultWr - prevWr) * 100;
    delta = (d >= 0 ? "+" : "") + d.toFixed(0) + " pp";
    color = d > 0 ? "var(--mejora)" : (d < 0 ? "var(--regresion)" : "var(--neutro)");
  } else if (ultWr != null) { delta = "línea base"; color = "var(--azul)"; }

  const filas = [
    ["Versiones", V.length, "var(--tinta)"],
    ["Iteración", ult ? ult.iteration : 0, "var(--tinta)"],
    ["Win rate", ultWr == null ? "—" : pct(ultWr), ultWr == null ? "var(--tinta-suave)" : "var(--azul-vivo)"],
    ["Respecto a la previa", delta, color]
  ];
  document.getElementById("marcadores").innerHTML = filas.map(f =>
    '<div class="marcador"><span class="rotulo">'+esc(f[0])+'</span>'+
    '<span class="cifra" style="color:'+f[2]+'">'+esc(f[1])+'</span></div>').join("");
})();

/* ---- curva de aprendizaje -------------------------------------------- */
function pintarCurva(){
  const m = conMetricas();
  const cont = document.getElementById("curva-lienzo");
  const nota = document.getElementById("curva-nota");
  if (!m.length) {
    cont.innerHTML = '<p class="vacio">Todavía no hay combates registrados. '+
      'Ejecuta el banco o el árbitro y carga los resultados con <code>gnver metrics</code>.</p>';
    nota.textContent = "";
    return;
  }
  nota.textContent = m.length === 1
    ? "Un solo punto: es la referencia contra la que se medirá todo lo demás."
    : "Tasa de victoria por versión, medida sobre el mismo banco de rivales.";

  const W = 960, H = 230, ml = 46, mr = 108, mt = 16, mb = 34;
  const iw = W - ml - mr, ih = H - mt - mb;
  const n = m.length;
  const px = i => n === 1 ? ml + iw/2 : ml + (i/(n-1))*iw;
  const py = w => mt + ih - (w||0)*ih;

  let g = "";
  [0,0.25,0.5,0.75,1].forEach(t => {
    const y = py(t);
    g += '<line x1="'+ml+'" y1="'+y+'" x2="'+(ml+iw)+'" y2="'+y+
         '" stroke="var(--regla)" stroke-width="1"'+(t===0?'':' stroke-dasharray="2 4"')+'></line>'+
         '<text x="'+(ml-9)+'" y="'+(y+4)+'" text-anchor="end" fill="var(--tinta-suave)" '+
         'font-family="JetBrains Mono, monospace" font-size="11">'+(t*100)+'%</text>';
  });

  if (n > 1) {
    const d = m.map((v,i) => (i?"L":"M")+px(i).toFixed(1)+" "+py(v.metrics.win_rate).toFixed(1)).join(" ");
    g += '<path d="'+d+'" fill="none" stroke="var(--azul-vivo)" stroke-width="2" '+
         'stroke-linejoin="round" stroke-linecap="round"></path>';
  }
  m.forEach((v,i) => {
    const x = px(i), y = py(v.metrics.win_rate), ultimo = (i === n-1);
    g += '<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+(ultimo?5.5:4)+
         '" fill="'+(ultimo?"var(--azul-vivo)":"var(--placa)")+'" stroke="var(--azul-vivo)" stroke-width="2"></circle>'+
         '<text x="'+x.toFixed(1)+'" y="'+(H-mb+17)+'" text-anchor="middle" fill="var(--tinta-suave)" '+
         'font-family="Oswald, sans-serif" font-size="11.5" letter-spacing="0.04em">'+esc(v.version)+'</text>';
    if (ultimo) {
      g += '<text x="'+(x+12)+'" y="'+(y+4.5)+'" fill="var(--azul-vivo)" '+
           'font-family="JetBrains Mono, monospace" font-size="13" font-weight="700">'+
           pct(v.metrics.win_rate)+'</text>';
    }
  });

  cont.innerHTML = '<svg class="lienzo" viewBox="0 0 '+W+' '+H+'" role="img" '+
    'aria-label="Tasa de victoria por versión"><g>'+g+'</g></svg>';
}

/* ---- carril de versiones --------------------------------------------- */
function pintarHistoria(sel){
  const h = document.getElementById("historia");
  h.innerHTML = '<p class="rotulo">Historial · más reciente arriba</p>' +
    V.slice().reverse().map(v => {
      const mt = v.metrics || {};
      const wr = mt.rounds ? pct(mt.win_rate) : "sin medir";
      return '<button class="hito" type="button" data-v="'+esc(v.version)+'" '+
        'aria-current="'+(v.version===sel)+'">'+
        '<span class="fila"><span class="ver">'+esc(v.version)+'</span>'+
        '<span class="chip '+esc(claseTipo(v.kind))+'">'+esc(v.kind)+'</span></span>'+
        '<span class="tit">'+esc(v.title)+'</span>'+
        '<span class="tit dato" style="color:var(--tinta-suave)">it '+v.iteration+' · '+esc(wr)+'</span>'+
        '</button>';
    }).join("");
  h.querySelectorAll(".hito").forEach(b =>
    b.addEventListener("click", () => mostrar(b.dataset.v)));
}

/* ---- diff ------------------------------------------------------------ */
function pintarDiff(txt){
  if (!txt || !txt.trim()) return '<p class="vacio">Sin cambios de código en esta entrada.</p>';
  const lineas = txt.split("\n").map(l => {
    let c = "l";
    if (l.startsWith("+++") || l.startsWith("---")) c += " arch";
    else if (l.startsWith("@@")) c += " trozo";
    else if (l.startsWith("+")) c += " mas";
    else if (l.startsWith("-")) c += " menos";
    return '<span class="'+c+'">'+esc(l || " ")+'</span>';
  }).join("");
  return '<pre class="diff">'+lineas+'</pre>';
}

/* ---- expediente de una versión --------------------------------------- */
function mostrar(ver){
  const v = V.find(x => x.version === ver) || V[V.length-1];
  if (!v) {
    document.getElementById("expediente").innerHTML =
      '<div class="bloque"><p class="vacio">La bitácora está vacía. '+
      'Crea la primera versión con <code>python3 tools/gnver.py new</code>.</p></div>';
    return;
  }
  const mt = v.metrics || {}, ds = v.diff_stat || {added:0,removed:0,files:0,touched:[]};
  const tocados = new Set(ds.touched || []);
  let H = "";

  /* titular */
  H += '<div class="titular"><div class="linea">'+
       '<span class="num">'+esc(v.version)+'</span>'+
       '<span class="chip '+esc(claseTipo(v.kind))+'">'+esc(v.kind)+'</span>'+
       '<span class="chip v-'+esc(v.verdict||"pendiente")+'">'+esc(v.verdict||"pendiente")+'</span>'+
       '</div><h2>'+esc(v.title)+'</h2>'+
       '<p class="meta dato">Iteración '+v.iteration+' · '+esc(fecha(v.created_at))+
       ' · '+esc(v.author)+(v.parent?' · deriva de '+esc(v.parent):' · sin antecesora')+'</p></div>';

  /* razonamiento */
  const campos = [
    ["Qué cambió", v.summary, true],
    ["Por qué", v.rationale, true],
    ["Hipótesis", v.hypothesis, false],
    ["Efecto esperado", v.expected_effect, false],
    ["Riesgos asumidos", v.risks, false],
    ["Nota para el robot real", v.notes_real_robot, false]
  ].filter(c => c[1]);
  H += '<div class="bloque"><h3>Razonamiento</h3><div class="razonamiento">' +
    campos.map(c => '<div class="campo'+(c[2]?' ancho':'')+'">'+
      '<span class="rotulo">'+esc(c[0])+'</span><p>'+esc(c[1])+'</p></div>').join("") +
    '</div></div>';

  /* parametros */
  if ((v.params_changed||[]).length) {
    H += '<div class="bloque"><h3>Parámetros tocados</h3><div class="tabla-envoltorio"><table>'+
      '<thead><tr><th>Parámetro</th><th>Antes</th><th></th><th>Después</th><th>Motivo</th></tr></thead><tbody>'+
      v.params_changed.map(p => '<tr><td class="num">'+esc(p.name)+'</td>'+
        '<td class="num de">'+esc(p.from)+'</td><td class="flecha">→</td>'+
        '<td class="num a">'+esc(p.to)+'</td><td>'+esc(p.reason||"")+'</td></tr>').join("")+
      '</tbody></table></div></div>';
  }

  /* metricas */
  H += '<div class="bloque"><h3>Resultados en el ring</h3>';
  if (mt.rounds) {
    const ops = Array.isArray(mt.opponents) ? mt.opponents : [];
    H += '<div class="marcadores" style="margin-bottom:'+(ops.length?"18px":"0")+'">'+
      [["Asaltos",mt.rounds,"var(--tinta)"],
       ["Victorias",mt.wins,"var(--mejora)"],
       ["Derrotas",mt.losses,"var(--regresion)"],
       ["Empates",mt.draws,"var(--tinta-media)"],
       ["Win rate",pct(mt.win_rate),"var(--azul-vivo)"],
       ["Auto-salidas",mt.self_outs!=null?mt.self_outs:"—","var(--regresion)"],
       ["Victoria media",mt.avg_win_time_s?mt.avg_win_time_s.toFixed(2)+" s":"—","var(--tinta)"]
      ].map(f => '<div class="marcador"><span class="rotulo">'+esc(f[0])+'</span>'+
        '<span class="cifra" style="color:'+f[2]+'">'+esc(f[1])+'</span></div>').join("")+'</div>';
    if (ops.length) {
      H += '<span class="rotulo">Desglose por rival</span><div class="rivales" style="margin-top:10px">'+
        ops.map(o => {
          const w = Math.max(0, Math.min(1, o.win_rate||0));
          const col = w >= 0.6 ? "var(--mejora)" : (w >= 0.35 ? "var(--neutro)" : "var(--regresion)");
          return '<div class="rival"><span class="nom">'+esc(o.name)+'</span>'+
            '<span class="barra"><span style="width:'+(w*100).toFixed(1)+'%;background:'+col+'"></span></span>'+
            '<span class="cifra">'+pct(o.win_rate)+' · '+o.wins+'/'+o.rounds+'</span></div>';
        }).join("")+'</div>';
    }
  } else {
    H += '<p class="vacio">Sin combates registrados todavía en esta versión.</p>';
  }
  H += '</div>';

  /* diff */
  H += '<div class="bloque"><div class="diff-cab"><h3 style="margin:0">Cambio de código</h3>'+
       '<span class="recuento"><span class="mas">+'+ds.added+'</span> / '+
       '<span class="menos">−'+ds.removed+'</span> en '+ds.files+' fichero(s)</span></div>'+
       pintarDiff(v.diff)+'</div>';

  /* ficheros */
  H += '<div class="bloque"><h3>Estado del árbol de control</h3><div class="ficheros">'+
    (v.files||[]).map(f => '<div class="fichero">'+
      '<span class="ruta'+(tocados.has(f.path)?" tocado":"")+'">'+esc(f.path)+'</span>'+
      '<span class="der">'+f.lines+' líneas · '+esc(String(f.sha256).slice(0,10))+'</span></div>').join("")+
    '</div></div>';

  document.getElementById("expediente").innerHTML = H;
  pintarHistoria(v.version);
  document.querySelectorAll(".hito").forEach(b =>
    b.setAttribute("aria-current", String(b.dataset.v === v.version)));
}

pintarCurva();
mostrar(V.length ? V[V.length-1].version : null);
})();
</script>
"""


def main():
    data = collect()
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "index.html").write_text(HTML.replace("/*__DATOS__*/", payload), encoding="utf-8")
    n = len(data["versions"])
    print(f"[sitio] site/index.html regenerado con {n} version(es)")


if __name__ == "__main__":
    main()
