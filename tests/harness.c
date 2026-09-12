/* ==========================================================================
 *  harness.c  --  Banco de pruebas nativo (ring de sumo sin Webots)
 *
 *  Simulador cinematico 2D minimo del dohyo reglamentario. No sustituye a
 *  Webots (no hay dinamica de contacto ni friccion real), pero corre 50
 *  asaltos en milisegundos y permite medir CADA version del algoritmo al
 *  instante. Webots queda como juez final; esto es el sparring diario.
 *
 *  Compilar:  make -C tests
 *  Ejecutar:  ./tests/build/harness --rounds 50 --opponent charger \
 *                                   --out runs/v0.1.0/results.json
 * ========================================================================== */

#include "../algorithms/strategy.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* ---- geometria del dohyo mini-sumo ------------------------------------- */
#define RING_R        0.385f   /* radio del dohyo                          */
#define RING_LINE_R   0.360f   /* radio interior de la banda blanca        */
#define BODY_R        0.055f   /* radio equivalente del robot (10x10 cm)   */
#define CORNER_OFF    0.045f   /* offset de los sensores de linea          */
#define SENSOR_OFF    0.035f   /* los sensores de distancia miran desde aqui*/
#define V_MAX         1.20f    /* m/s a consigna 1.0                       */
#define DT_S          0.008f   /* 8 ms                                     */
#define MATCH_MAX_S   30.0f    /* limite de asalto                         */
#define ARM_DELAY_S   0.20f    /* retardo de arranque del harness          */

typedef enum { OPP_STATIC, OPP_CHARGER, OPP_SPINNER, OPP_MIRROR } opp_kind_t;

typedef struct {
  float x, y, th;
  float cl, cr;          /* consignas aplicadas */
  sumo_strategy_t brain; /* usado por GELATINA y por OPP_MIRROR */
  int   scripted_phase;
  float scripted_t;
} bot_t;

/* ---- PRNG reproducible (xorshift32) ------------------------------------ */
static uint32_t rng_state = 1u;
static float frand(void)
{
  rng_state ^= rng_state << 13; rng_state ^= rng_state >> 17; rng_state ^= rng_state << 5;
  return (float)(rng_state & 0xFFFFFFu) / (float)0x1000000u;
}
static float frand_sym(float a) { return (frand() * 2.0f - 1.0f) * a; }


/* ==========================================================================
 *  Simulacion de sensores
 * ========================================================================== */

/* Interseccion rayo-circulo. Devuelve la distancia o -1 si no hay impacto. */
static float ray_circle(float ox, float oy, float dx, float dy,
                        float cx, float cy, float r)
{
  const float mx = ox - cx, my = oy - cy;
  const float b = mx * dx + my * dy;
  const float c = mx * mx + my * my - r * r;
  if (c > 0.0f && b > 0.0f) return -1.0f;
  const float disc = b * b - c;
  if (disc < 0.0f) return -1.0f;
  float t = -b - sqrtf(disc);
  if (t < 0.0f) t = 0.0f;
  return t;
}

static void sense(const bot_t *me, const bot_t *foe, uint32_t t_ms,
                  bool armed, sumo_sensors_t *s)
{
  memset(s, 0, sizeof(*s));
  s->t_ms  = t_ms;
  s->armed = armed;
  s->yaw_rad = me->th;

  for (int i = 0; i < SUMO_N_DIST; ++i) {
    const float a  = me->th + (float)SUMO_DIST_ANGLE_CDEG[i] / 100.0f * (float)(M_PI / 180.0);
    const float dx = cosf(a), dy = sinf(a);
    const float ox = me->x + SENSOR_OFF * dx, oy = me->y + SENSOR_OFF * dy;
    const float t  = ray_circle(ox, oy, dx, dy, foe->x, foe->y, BODY_R);
    if (t < 0.0f || t > 1.2f) {
      s->dist_mm[i] = SUMO_DIST_NONE;
    } else {
      float mm = t * 1000.0f + frand_sym(6.0f);      /* +-6 mm de ruido */
      if (mm < 0.0f) mm = 0.0f;
      s->dist_mm[i] = (uint16_t)mm;
    }
  }

  static const float cx[SUMO_N_LINE] = { +CORNER_OFF, +CORNER_OFF, -CORNER_OFF, -CORNER_OFF };
  static const float cy[SUMO_N_LINE] = { +CORNER_OFF, -CORNER_OFF, +CORNER_OFF, -CORNER_OFF };
  const float ct = cosf(me->th), st = sinf(me->th);
  for (int i = 0; i < SUMO_N_LINE; ++i) {
    const float wx = me->x + cx[i] * ct - cy[i] * st;
    const float wy = me->y + cx[i] * st + cy[i] * ct;
    s->line[i] = (sqrtf(wx * wx + wy * wy) >= RING_LINE_R);
  }
}


/* ==========================================================================
 *  Rivales de referencia
 * ========================================================================== */

static void opponent_act(bot_t *b, const sumo_sensors_t *s, opp_kind_t kind,
                         sumo_actuators_t *a)
{
  a->led = 0;
  if (!s->armed) { a->left = a->right = 0.0f; return; }

  const bool line_front = s->line[LINE_FL] || s->line[LINE_FR];
  const bool line_rear  = s->line[LINE_RL] || s->line[LINE_RR];

  switch (kind) {
  case OPP_STATIC:
    a->left = a->right = 0.0f;
    break;

  case OPP_SPINNER:
    if (line_front || line_rear) { a->left = -0.6f; a->right = -0.6f; }
    else                         { a->left = -0.5f; a->right = 0.5f; }
    break;

  case OPP_CHARGER:
  default: {
    /* retrocede si ve linea delante, si no embiste hacia el contacto mas cercano */
    if (line_front) { b->scripted_phase = 1; b->scripted_t = 0.0f; }
    if (b->scripted_phase == 1) {
      b->scripted_t += DT_S;
      a->left  = (b->scripted_t < 0.30f) ? -0.8f : -0.6f;
      a->right = (b->scripted_t < 0.30f) ? -0.8f :  0.6f;
      if (b->scripted_t > 0.70f) b->scripted_phase = 0;
      break;
    }
    if (line_rear) { a->left = 0.9f; a->right = 0.9f; break; }

    uint16_t best = SUMO_DIST_NONE; int bi = -1;
    for (int i = 0; i < SUMO_N_DIST; ++i)
      if (s->dist_mm[i] != SUMO_DIST_NONE && s->dist_mm[i] < best) { best = s->dist_mm[i]; bi = i; }

    if (bi < 0) { a->left = -0.45f; a->right = 0.45f; }          /* buscar girando */
    else {
      const float turn = (float)SUMO_DIST_ANGLE_CDEG[bi] / 6000.0f * 0.55f;
      a->left  = 0.95f - turn;
      a->right = 0.95f + turn;
    }
    break;
  }
  }
}


/* ==========================================================================
 *  Integracion del movimiento y resolucion de empuje
 * ========================================================================== */

static void integrate(bot_t *b, float cl, float cr)
{
  b->cl = cl; b->cr = cr;
  const float vl = cl * V_MAX, vr = cr * V_MAX;
  const float v  = 0.5f * (vl + vr);
  const float w  = (vr - vl) / SUMO_TRACK_M;
  b->th += w * DT_S;
  b->x  += v * cosf(b->th) * DT_S;
  b->y  += v * sinf(b->th) * DT_S;
}

/* Empuje: quien tiene mas empuje alineado con la normal de contacto gana. */
static void resolve_push(bot_t *a, bot_t *b)
{
  float dx = b->x - a->x, dy = b->y - a->y;
  float d = sqrtf(dx * dx + dy * dy);
  if (d >= 2.0f * BODY_R) return;
  if (d < 1e-5f) { dx = 1.0f; dy = 0.0f; d = 1e-5f; }
  const float nx = dx / d, ny = dy / d;
  const float pen = 2.0f * BODY_R - d;

  const float va = 0.5f * (a->cl + a->cr) * V_MAX;
  const float vb = 0.5f * (b->cl + b->cr) * V_MAX;
  float ta = va * (cosf(a->th) * nx + sinf(a->th) * ny);   /* A empuja hacia B */
  float tb = vb * (cosf(b->th) * -nx + sinf(b->th) * -ny); /* B empuja hacia A */
  if (ta < 0.0f) ta = 0.0f;
  if (tb < 0.0f) tb = 0.0f;

  const float tot = ta + tb + 0.02f;
  const float share_b = ta / tot;   /* fraccion de penetracion que absorbe B */
  const float share_a = tb / tot;
  const float rest = 1.0f - share_a - share_b;

  b->x += nx * pen * (share_b + rest * 0.5f);
  b->y += ny * pen * (share_b + rest * 0.5f);
  a->x -= nx * pen * (share_a + rest * 0.5f);
  a->y -= ny * pen * (share_a + rest * 0.5f);
}

static bool out_of_ring(const bot_t *b)
{
  return sqrtf(b->x * b->x + b->y * b->y) > (RING_R + BODY_R * 0.35f);
}


/* ==========================================================================
 *  Un asalto
 * ========================================================================== */

typedef struct { int result; float t_s; const char *reason; } round_res_t;
/* result: +1 gana Gelatina, -1 pierde, 0 empate */

static round_res_t play_round(opp_kind_t kind, const sumo_params_t *params, int idx)
{
  bot_t me = (bot_t){0}, foe = (bot_t){0};
  strategy_init(&me.brain, params);
  if (kind == OPP_MIRROR) {
    sumo_params_t mp = sumo_params_default();
    strategy_init(&foe.brain, &mp);
  }

  /* Colocacion reglamentaria: en diagonal, mirandose, con jitter por asalto */
  const float base = (idx % 2 == 0) ? 0.0f : (float)(M_PI / 2.0);
  const float r0 = 0.18f + frand_sym(0.02f);
  me.x  =  r0 * cosf(base);              me.y  =  r0 * sinf(base);
  foe.x = -r0 * cosf(base);              foe.y = -r0 * sinf(base);
  me.th  = base + (float)M_PI + frand_sym(0.25f);
  foe.th = base + frand_sym(0.25f);

  const int steps = (int)(MATCH_MAX_S / DT_S);
  const int arm_step = (int)(ARM_DELAY_S / DT_S);
  float last_contact_s = -99.0f;   /* para separar expulsion de auto-salida */

  for (int k = 0; k < steps; ++k) {
    const uint32_t t_ms = (uint32_t)(k * 8);
    const bool armed = (k >= arm_step);

    sumo_sensors_t s_me, s_foe;
    sumo_actuators_t a_me = {0}, a_foe = {0};

    sense(&me,  &foe, t_ms, armed, &s_me);
    sense(&foe, &me,  t_ms, armed, &s_foe);

    strategy_step(&me.brain, &s_me, &a_me);
    if (kind == OPP_MIRROR) strategy_step(&foe.brain, &s_foe, &a_foe);
    else                    opponent_act(&foe, &s_foe, kind, &a_foe);

    integrate(&me,  a_me.left,  a_me.right);
    integrate(&foe, a_foe.left, a_foe.right);
    resolve_push(&me, &foe);

    const float t_s = (float)(k - arm_step) * DT_S;
    {
      const float sx = foe.x - me.x, sy = foe.y - me.y;
      if (sqrtf(sx * sx + sy * sy) < 2.0f * BODY_R + 0.012f) last_contact_s = t_s;
    }

    const bool me_out = out_of_ring(&me), foe_out = out_of_ring(&foe);
    if (me_out && foe_out) return (round_res_t){ 0, t_s, "doble salida" };
    if (foe_out)           return (round_res_t){ +1, t_s, "rival fuera" };
    if (me_out) {
      /* Perder empujado es una derrota tactica; perder solo es un fallo del
       * escape de borde. Distinguirlo es lo que hace util la metrica. */
      const bool empujado = (t_s - last_contact_s) < 0.40f;
      return (round_res_t){ -1, t_s, empujado ? "expulsado" : "auto-salida" };
    }
  }
  return (round_res_t){ 0, MATCH_MAX_S, "tiempo agotado" };
}


/* ========================================================================== */

static const char *KIND_NAME[] = { "static", "charger", "spinner", "mirror" };

int main(int argc, char **argv)
{
  int rounds = 50;
  opp_kind_t kind = OPP_CHARGER;
  const char *out = NULL;
  const char *ver = "WORK";
  bool all = false;
  rng_state = 12345u;

  for (int i = 1; i < argc; ++i) {
    if (!strcmp(argv[i], "--rounds")   && i + 1 < argc) rounds = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--seed") && i + 1 < argc) rng_state = (uint32_t)atoi(argv[++i]) | 1u;
    else if (!strcmp(argv[i], "--out")  && i + 1 < argc) out = argv[++i];
    else if (!strcmp(argv[i], "--version") && i + 1 < argc) ver = argv[++i];
    else if (!strcmp(argv[i], "--all")) all = true;
    else if (!strcmp(argv[i], "--opponent") && i + 1 < argc) {
      const char *k = argv[++i];
      for (int j = 0; j < 4; ++j) if (!strcmp(k, KIND_NAME[j])) kind = (opp_kind_t)j;
    }
  }

  const sumo_params_t params = sumo_params_default();
  const int k0 = all ? 0 : (int)kind;
  const int k1 = all ? 3 : (int)kind;

  int tw = 0, tl = 0, td = 0, tself = 0, tr = 0;
  float twin_t = 0.0f;
  char per_opp[1024]; size_t po = 0;
  per_opp[0] = '\0';

  printf("\n  Gelatina Nuclear -- banco nativo   estrategia %s\n", strategy_version());
  printf("  %-9s %6s %6s %6s %8s %10s\n", "RIVAL", "W", "L", "D", "win%", "t_med(s)");
  printf("  ------------------------------------------------------------\n");

  for (int kk = k0; kk <= k1; ++kk) {
    int w = 0, l = 0, d = 0, so = 0; float wt = 0.0f;
    for (int i = 0; i < rounds; ++i) {
      const round_res_t r = play_round((opp_kind_t)kk, &params, i);
      if (r.result > 0)      { w++; wt += r.t_s; }
      else if (r.result < 0) { l++; if (!strcmp(r.reason, "auto-salida")) so++; }
      else                     d++;
    }
    const float wr = (float)w / (float)rounds;
    printf("  %-9s %6d %6d %6d %7.1f%% %10.2f\n", KIND_NAME[kk], w, l, d,
           wr * 100.0f, w ? wt / (float)w : 0.0f);
    po += (size_t)snprintf(per_opp + po, sizeof(per_opp) - po,
                           "%s{\"name\":\"%s\",\"rounds\":%d,\"wins\":%d,\"losses\":%d,"
                           "\"draws\":%d,\"win_rate\":%.3f}",
                           po ? "," : "", KIND_NAME[kk], rounds, w, l, d, (double)wr);
    tw += w; tl += l; td += d; tself += so; tr += rounds; twin_t += wt;
  }

  const float total_wr = tr ? (float)tw / (float)tr : 0.0f;
  printf("  ------------------------------------------------------------\n");
  printf("  %-9s %6d %6d %6d %7.1f%% %10.2f\n\n", "TOTAL", tw, tl, td,
         total_wr * 100.0f, tw ? twin_t / (float)tw : 0.0f);

  if (out) {
    FILE *f = fopen(out, "w");
    if (!f) { fprintf(stderr, "no puedo escribir %s\n", out); return 1; }
    fprintf(f,
      "{\n  \"version\": \"%s\",\n  \"engine\": \"harness-nativo\",\n"
      "  \"strategy_build\": \"%s\",\n  \"metrics\": {\n"
      "    \"rounds\": %d,\n    \"wins\": %d,\n    \"losses\": %d,\n    \"draws\": %d,\n"
      "    \"win_rate\": %.3f,\n    \"avg_win_time_s\": %.2f,\n    \"self_outs\": %d,\n"
      "    \"opponents\": [%s]\n  }\n}\n",
      ver, strategy_version(), tr, tw, tl, td, (double)total_wr,
      tw ? (double)(twin_t / (float)tw) : 0.0, tself, per_opp);
    fclose(f);
    printf("  resultados -> %s\n\n", out);
  }
  return 0;
}
