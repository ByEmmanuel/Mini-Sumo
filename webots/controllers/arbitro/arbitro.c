/* ==========================================================================
 *  arbitro.c  --  Supervisor de combate (juez y estadistico)
 *
 *  Cierra el bucle de aprendizaje: coloca a los robots, da la senal de
 *  arranque, detecta la expulsion, repite N asaltos y escribe un JSON con el
 *  MISMO esquema que el banco nativo. Ese JSON entra en la bitacora con:
 *
 *      python3 tools/gnver.py metrics vX.Y.Z --from runs/webots_vX.Y.Z.json
 *
 *  Sin esto no hay metricas, y sin metricas una iteracion es una opinion.
 * ========================================================================== */

#include <webots/robot.h>
#include <webots/supervisor.h>
#include <webots/emitter.h>

#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* M_PI no lo garantiza C99 estricto; glibc lo oculta bajo -std=c99. */
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define RING_R       0.385
#define OUT_MARGIN   0.030   /* centro del robot mas alla de esto = fuera   */
#define FALL_Z      -0.012   /* o directamente se ha caido del dohyo        */
#define CONTACT_D    0.125   /* centros a menos de esto = estan en contacto  */
#define SETTLE_MS      300.0
#define DEFAULT_TIMEOUT 30.0

typedef struct { WbNodeRef node; WbFieldRef tr, rot; } fighter_t;

static void place(const fighter_t *f, double x, double y, double yaw)
{
  const double t[3] = { x, y, 0.001 };
  const double r[4] = { 0.0, 0.0, 1.0, yaw };
  wb_supervisor_field_set_sf_vec3f(f->tr, t);
  wb_supervisor_field_set_sf_rotation(f->rot, r);
  wb_supervisor_node_reset_physics(f->node);
}

static bool is_out(const fighter_t *f)
{
  const double *p = wb_supervisor_node_get_position(f->node);
  const double rad = sqrt(p[0] * p[0] + p[1] * p[1]);
  return (rad > RING_R + OUT_MARGIN) || (p[2] < FALL_Z);
}

static void broadcast(WbDeviceTag tx, const char *msg)
{
  wb_emitter_send(tx, msg, (int)strlen(msg) + 1);
}

int main(int argc, char **argv)
{
  wb_robot_init();
  const int step = (int)wb_robot_get_basic_time_step();

  int rounds = 20;
  double timeout = DEFAULT_TIMEOUT;
  const char *out_path = "../../../runs/webots_ultimo.json";
  const char *version  = "WORK";
  const char *rival    = "charger";

  for (int i = 1; i < argc; ++i) {
    if      (!strcmp(argv[i], "--rounds")  && i + 1 < argc) rounds   = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--timeout") && i + 1 < argc) timeout  = atof(argv[++i]);
    else if (!strcmp(argv[i], "--out")     && i + 1 < argc) out_path = argv[++i];
    else if (!strcmp(argv[i], "--version") && i + 1 < argc) version  = argv[++i];
    else if (!strcmp(argv[i], "--rival")   && i + 1 < argc) rival    = argv[++i];
  }

  fighter_t me = {0}, foe = {0};
  me.node  = wb_supervisor_node_get_from_def("GELATINA");
  foe.node = wb_supervisor_node_get_from_def("RIVAL");
  if (!me.node || !foe.node) {
    fprintf(stderr, "[arbitro] faltan los DEF GELATINA / RIVAL en el mundo\n");
    wb_robot_cleanup();
    return 1;
  }
  me.tr   = wb_supervisor_node_get_field(me.node,  "translation");
  me.rot  = wb_supervisor_node_get_field(me.node,  "rotation");
  foe.tr  = wb_supervisor_node_get_field(foe.node, "translation");
  foe.rot = wb_supervisor_node_get_field(foe.node, "rotation");

  WbDeviceTag tx = wb_robot_get_device("emisor");

  int wins = 0, losses = 0, draws = 0, self_outs = 0;
  double win_time_sum = 0.0;

  printf("\n[arbitro] %d asaltos contra '%s', limite %.0f s por asalto\n",
         rounds, rival, timeout);
  fflush(stdout);

  for (int k = 0; k < rounds && wb_robot_step(step) != -1; ++k) {

    /* --- puesta en escena ------------------------------------------------ */
    broadcast(tx, "STOP");
    const double base = (k % 2 == 0) ? 0.0 : M_PI / 2.0;
    const double jit  = ((k * 37) % 17 - 8) * 0.004;   /* +-32 mm determinista */
    const double r0   = 0.18;
    place(&me,   r0 * cos(base) + jit,  r0 * sin(base),        base + M_PI);
    place(&foe, -r0 * cos(base),       -r0 * sin(base) + jit,  base);
    wb_supervisor_simulation_reset_physics();

    const double t_settle_end = wb_robot_get_time() * 1000.0 + SETTLE_MS;
    while (wb_robot_get_time() * 1000.0 < t_settle_end)
      if (wb_robot_step(step) == -1) goto done;

    /* --- combate ---------------------------------------------------------- */
    broadcast(tx, "ARM");
    const double t_start = wb_robot_get_time();
    double last_contact = -99.0;
    int result = 0;
    const char *reason = "tiempo agotado";

    while (wb_robot_get_time() - t_start < timeout) {
      if (wb_robot_step(step) == -1) goto done;
      const double t_now = wb_robot_get_time() - t_start;

      const double *pm = wb_supervisor_node_get_position(me.node);
      const double *pf = wb_supervisor_node_get_position(foe.node);
      const double sx = pf[0] - pm[0], sy = pf[1] - pm[1];
      if (sqrt(sx * sx + sy * sy) < CONTACT_D) last_contact = t_now;

      const bool mo = is_out(&me), fo = is_out(&foe);
      if (mo && fo) { result = 0;  reason = "doble salida"; break; }
      if (fo)       { result = 1;  reason = "rival fuera";  break; }
      if (mo) {
        result = -1;
        reason = (t_now - last_contact < 0.40) ? "expulsado" : "auto-salida";
        break;
      }
    }
    const double dur = wb_robot_get_time() - t_start;

    if (result > 0)      { wins++;   win_time_sum += dur; }
    else if (result < 0) { losses++; if (!strcmp(reason, "auto-salida")) self_outs++; }
    else                   draws++;

    printf("[arbitro] asalto %2d/%d  %-14s  %+d  %5.2f s\n",
           k + 1, rounds, reason, result, dur);
    fflush(stdout);
  }

done:
  broadcast(tx, "STOP");
  {
    const int total = wins + losses + draws;
    const double wr = total ? (double)wins / total : 0.0;
    printf("\n[arbitro] RESULTADO  %dW %dL %dD  win rate %.1f%%  "
           "auto-salidas %d  t medio de victoria %.2f s\n\n",
           wins, losses, draws, wr * 100.0, self_outs,
           wins ? win_time_sum / wins : 0.0);

    FILE *f = fopen(out_path, "w");
    if (f) {
      fprintf(f,
        "{\n  \"version\": \"%s\",\n  \"engine\": \"webots\",\n"
        "  \"metrics\": {\n"
        "    \"rounds\": %d,\n    \"wins\": %d,\n    \"losses\": %d,\n    \"draws\": %d,\n"
        "    \"win_rate\": %.3f,\n    \"avg_win_time_s\": %.2f,\n    \"self_outs\": %d,\n"
        "    \"opponents\": [{\"name\":\"%s\",\"rounds\":%d,\"wins\":%d,"
        "\"losses\":%d,\"draws\":%d,\"win_rate\":%.3f}]\n  }\n}\n",
        version, total, wins, losses, draws, wr,
        wins ? win_time_sum / wins : 0.0, self_outs,
        rival, total, wins, losses, draws, wr);
      fclose(f);
      printf("[arbitro] resultados -> %s\n", out_path);
    } else {
      fprintf(stderr, "[arbitro] no puedo escribir %s\n", out_path);
    }
    fflush(stdout);
  }

  wb_supervisor_simulation_set_mode(WB_SUPERVISOR_SIMULATION_MODE_PAUSE);
  wb_robot_cleanup();
  return 0;
}
