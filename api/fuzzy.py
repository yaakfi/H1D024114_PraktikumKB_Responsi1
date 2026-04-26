import json
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from http.server import BaseHTTPRequestHandler

# Setup Fuzzy Logic (Mamdani)
winrate = ctrl.Antecedent(np.arange(0, 101, 1), 'winrate')
durasi = ctrl.Antecedent(np.arange(0, 13, 0.5), 'durasi')
tugas = ctrl.Antecedent(np.arange(0, 11, 1), 'tugas')
stres = ctrl.Consequent(np.arange(0, 101, 1), 'stres')

winrate['rendah'] = fuzz.trapmf(winrate.universe, [0, 0, 40, 50])
winrate['sedang'] = fuzz.trimf(winrate.universe, [45, 55, 65])
winrate['tinggi'] = fuzz.trapmf(winrate.universe, [60, 70, 100, 100])

durasi['sebentar'] = fuzz.trapmf(durasi.universe, [0, 0, 2, 4])
durasi['sedang'] = fuzz.trimf(durasi.universe, [3, 5, 7])
durasi['lama'] = fuzz.trapmf(durasi.universe, [6, 8, 12, 12])

tugas['sedikit'] = fuzz.trapmf(tugas.universe, [0, 0, 2, 4])
tugas['sedang'] = fuzz.trimf(tugas.universe, [3, 5, 7])
tugas['banyak'] = fuzz.trapmf(tugas.universe, [6, 8, 10, 10])

stres['rendah'] = fuzz.trapmf(stres.universe, [0, 0, 20, 40])
stres['sedang'] = fuzz.trimf(stres.universe, [30, 50, 70])
stres['tinggi'] = fuzz.trapmf(stres.universe, [60, 80, 100, 100])

rules = [
    ctrl.Rule(winrate['rendah'] & durasi['lama'] & tugas['banyak'], stres['tinggi']),
    ctrl.Rule(winrate['rendah'] & durasi['lama'] & tugas['sedang'], stres['tinggi']),
    ctrl.Rule(winrate['rendah'] & durasi['lama'] & tugas['sedikit'], stres['tinggi']),
    ctrl.Rule(winrate['rendah'] & durasi['sedang'] & tugas['banyak'], stres['tinggi']),
    ctrl.Rule(winrate['rendah'] & durasi['sedang'] & tugas['sedang'], stres['tinggi']),
    ctrl.Rule(winrate['rendah'] & durasi['sedang'] & tugas['sedikit'], stres['sedang']),
    ctrl.Rule(winrate['rendah'] & durasi['sebentar'] & tugas['banyak'], stres['tinggi']),
    ctrl.Rule(winrate['rendah'] & durasi['sebentar'] & tugas['sedang'], stres['sedang']),
    ctrl.Rule(winrate['rendah'] & durasi['sebentar'] & tugas['sedikit'], stres['sedang']),

    ctrl.Rule(winrate['sedang'] & durasi['lama'] & tugas['banyak'], stres['tinggi']),
    ctrl.Rule(winrate['sedang'] & durasi['lama'] & tugas['sedang'], stres['sedang']),
    ctrl.Rule(winrate['sedang'] & durasi['lama'] & tugas['sedikit'], stres['sedang']),
    ctrl.Rule(winrate['sedang'] & durasi['sedang'] & tugas['banyak'], stres['tinggi']),
    ctrl.Rule(winrate['sedang'] & durasi['sedang'] & tugas['sedang'], stres['sedang']),
    ctrl.Rule(winrate['sedang'] & durasi['sedang'] & tugas['sedikit'], stres['rendah']),
    ctrl.Rule(winrate['sedang'] & durasi['sebentar'] & tugas['banyak'], stres['sedang']),
    ctrl.Rule(winrate['sedang'] & durasi['sebentar'] & tugas['sedang'], stres['rendah']),
    ctrl.Rule(winrate['sedang'] & durasi['sebentar'] & tugas['sedikit'], stres['rendah']),

    ctrl.Rule(winrate['tinggi'] & durasi['lama'] & tugas['banyak'], stres['sedang']),
    ctrl.Rule(winrate['tinggi'] & durasi['lama'] & tugas['sedang'], stres['sedang']),
    ctrl.Rule(winrate['tinggi'] & durasi['lama'] & tugas['sedikit'], stres['rendah']),
    ctrl.Rule(winrate['tinggi'] & durasi['sedang'] & tugas['banyak'], stres['sedang']),
    ctrl.Rule(winrate['tinggi'] & durasi['sedang'] & tugas['sedang'], stres['rendah']),
    ctrl.Rule(winrate['tinggi'] & durasi['sedang'] & tugas['sedikit'], stres['rendah']),
    ctrl.Rule(winrate['tinggi'] & durasi['sebentar'] & tugas['banyak'], stres['sedang']),
    ctrl.Rule(winrate['tinggi'] & durasi['sebentar'] & tugas['sedang'], stres['rendah']),
    ctrl.Rule(winrate['tinggi'] & durasi['sebentar'] & tugas['sedikit'], stres['rendah']),
]
stres_ctrl = ctrl.ControlSystem(rules)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        try:
            stres_sim = ctrl.ControlSystemSimulation(stres_ctrl)
            stres_sim.input['winrate'] = float(data.get('winrate', 50))
            stres_sim.input['durasi'] = float(data.get('durasi', 4))
            stres_sim.input['tugas'] = float(data.get('tugas', 5))
            stres_sim.compute()
            
            hasil = stres_sim.output['stres']
            
            wr_val = float(data.get('winrate', 50))
            dr_val = float(data.get('durasi', 4))
            tg_val = float(data.get('tugas', 5))

            fuzz_table = []
            wr_r = fuzz.interp_membership(winrate.universe, winrate['rendah'].mf, wr_val)
            wr_s = fuzz.interp_membership(winrate.universe, winrate['sedang'].mf, wr_val)
            wr_t = fuzz.interp_membership(winrate.universe, winrate['tinggi'].mf, wr_val)
            if wr_r > 0: fuzz_table.append({"var": "WINRATE", "set": "RENDAH", "val": float(wr_r)})
            if wr_s > 0: fuzz_table.append({"var": "WINRATE", "set": "SEDANG", "val": float(wr_s)})
            if wr_t > 0: fuzz_table.append({"var": "WINRATE", "set": "TINGGI", "val": float(wr_t)})

            dr_seb = fuzz.interp_membership(durasi.universe, durasi['sebentar'].mf, dr_val)
            dr_sed = fuzz.interp_membership(durasi.universe, durasi['sedang'].mf, dr_val)
            dr_lam = fuzz.interp_membership(durasi.universe, durasi['lama'].mf, dr_val)
            if dr_seb > 0: fuzz_table.append({"var": "DURASI", "set": "SEBENTAR", "val": float(dr_seb)})
            if dr_sed > 0: fuzz_table.append({"var": "DURASI", "set": "SEDANG", "val": float(dr_sed)})
            if dr_lam > 0: fuzz_table.append({"var": "DURASI", "set": "LAMA", "val": float(dr_lam)})

            tg_sdk = fuzz.interp_membership(tugas.universe, tugas['sedikit'].mf, tg_val)
            tg_sdg = fuzz.interp_membership(tugas.universe, tugas['sedang'].mf, tg_val)
            tg_bny = fuzz.interp_membership(tugas.universe, tugas['banyak'].mf, tg_val)
            if tg_sdk > 0: fuzz_table.append({"var": "TUGAS", "set": "SEDIKIT", "val": float(tg_sdk)})
            if tg_sdg > 0: fuzz_table.append({"var": "TUGAS", "set": "SEDANG", "val": float(tg_sdg)})
            if tg_bny > 0: fuzz_table.append({"var": "TUGAS", "set": "BANYAK", "val": float(tg_bny)})

            rules_log = []
            fuzz_vals = {
                'winrate': {'rendah': wr_r, 'sedang': wr_s, 'tinggi': wr_t},
                'durasi': {'sebentar': dr_seb, 'sedang': dr_sed, 'lama': dr_lam},
                'tugas': {'sedikit': tg_sdk, 'sedang': tg_sdg, 'banyak': tg_bny}
            }
            
            rule_defs = [
                (['rendah', 'lama', 'banyak'], 'tinggi'), (['rendah', 'lama', 'sedang'], 'tinggi'), (['rendah', 'lama', 'sedikit'], 'tinggi'),
                (['rendah', 'sedang', 'banyak'], 'tinggi'), (['rendah', 'sedang', 'sedang'], 'tinggi'), (['rendah', 'sedang', 'sedikit'], 'sedang'),
                (['rendah', 'sebentar', 'banyak'], 'tinggi'), (['rendah', 'sebentar', 'sedang'], 'sedang'), (['rendah', 'sebentar', 'sedikit'], 'sedang'),
                (['sedang', 'lama', 'banyak'], 'tinggi'), (['sedang', 'lama', 'sedang'], 'sedang'), (['sedang', 'lama', 'sedikit'], 'sedang'),
                (['sedang', 'sedang', 'banyak'], 'tinggi'), (['sedang', 'sedang', 'sedang'], 'sedang'), (['sedang', 'sedang', 'sedikit'], 'rendah'),
                (['sedang', 'sebentar', 'banyak'], 'sedang'), (['sedang', 'sebentar', 'sedang'], 'rendah'), (['sedang', 'sebentar', 'sedikit'], 'rendah'),
                (['tinggi', 'lama', 'banyak'], 'sedang'), (['tinggi', 'lama', 'sedang'], 'sedang'), (['tinggi', 'lama', 'sedikit'], 'rendah'),
                (['tinggi', 'sedang', 'banyak'], 'sedang'), (['tinggi', 'sedang', 'sedang'], 'rendah'), (['tinggi', 'sedang', 'sedikit'], 'rendah'),
                (['tinggi', 'sebentar', 'banyak'], 'sedang'), (['tinggi', 'sebentar', 'sedang'], 'rendah'), (['tinggi', 'sebentar', 'sedikit'], 'rendah'),
            ]

            for i, (conds, out) in enumerate(rule_defs):
                alpha = min(fuzz_vals['winrate'][conds[0]], fuzz_vals['durasi'][conds[1]], fuzz_vals['tugas'][conds[2]])
                if alpha > 0:
                    rules_log.append({
                        "rule_idx": i+1,
                        "if": f"Winrate {conds[0]} AND Durasi {conds[1]} AND Tugas {conds[2]}",
                        "then": f"Stres {out}",
                        "alpha": float(alpha)
                    })

            response = {
                "status": "success",
                "crisp_result": float(hasil),
                "fuzz_table": fuzz_table,
                "rules_log": rules_log
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        self.end_headers()
