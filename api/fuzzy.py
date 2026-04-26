import json
from http.server import BaseHTTPRequestHandler

def trapmf(x, abcd):
    a, b, c, d = abcd
    if x <= a or x >= d: return 0.0
    if a <= x <= b: return 1.0 if a == b else (x - a) / (b - a)
    if b <= x <= c: return 1.0
    if c <= x <= d: return 1.0 if c == d else (d - x) / (d - c)
    return 0.0

def trimf(x, abc):
    a, b, c = abc
    if x <= a or x >= c: return 0.0
    if a <= x <= b: return 1.0 if a == b else (x - a) / (b - a)
    if b <= x <= c: return 1.0 if b == c else (c - x) / (c - b)
    return 0.0

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            wr_val = float(data.get('winrate', 50))
            dr_val = float(data.get('durasi', 4))
            tg_val = float(data.get('tugas', 5))

            # 1. Fuzzification
            wr_r = trapmf(wr_val, [0, 0, 40, 50])
            wr_s = trimf(wr_val, [45, 55, 65])
            wr_t = trapmf(wr_val, [60, 70, 100, 100])

            dr_seb = trapmf(dr_val, [0, 0, 2, 4])
            dr_sed = trimf(dr_val, [3, 5, 7])
            dr_lam = trapmf(dr_val, [6, 8, 12, 12])

            tg_sdk = trapmf(tg_val, [0, 0, 2, 4])
            tg_sdg = trimf(tg_val, [3, 5, 7])
            tg_bny = trapmf(tg_val, [6, 8, 10, 10])

            fuzz_vals = {
                'winrate': {'rendah': wr_r, 'sedang': wr_s, 'tinggi': wr_t},
                'durasi': {'sebentar': dr_seb, 'sedang': dr_sed, 'lama': dr_lam},
                'tugas': {'sedikit': tg_sdk, 'sedang': tg_sdg, 'banyak': tg_bny}
            }

            fuzz_table = []
            for var_name, var_dict in fuzz_vals.items():
                for set_name, val in var_dict.items():
                    if val > 0:
                        fuzz_table.append({"var": var_name.upper(), "set": set_name.upper(), "val": val})

            # 2. Rule Evaluation
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

            rules_log = []
            rule_alphas = {'rendah': 0.0, 'sedang': 0.0, 'tinggi': 0.0}

            for i, (conds, out) in enumerate(rule_defs):
                alpha = min(fuzz_vals['winrate'][conds[0]], fuzz_vals['durasi'][conds[1]], fuzz_vals['tugas'][conds[2]])
                if alpha > 0:
                    rules_log.append({
                        "rule_idx": i+1,
                        "if": f"Winrate {conds[0]} AND Durasi {conds[1]} AND Tugas {conds[2]}",
                        "then": f"Stres {out}",
                        "alpha": float(alpha)
                    })
                    if alpha > rule_alphas[out]:
                        rule_alphas[out] = alpha

            # 3. Defuzzification (Centroid)
            numerator = 0.0
            denominator = 0.0
            
            for x in range(0, 101):
                mu_r = trapmf(x, [0, 0, 20, 40])
                mu_s = trimf(x, [30, 50, 70])
                mu_t = trapmf(x, [60, 80, 100, 100])
                
                cut_r = min(mu_r, rule_alphas['rendah'])
                cut_s = min(mu_s, rule_alphas['sedang'])
                cut_t = min(mu_t, rule_alphas['tinggi'])
                
                agg = max(cut_r, cut_s, cut_t)
                
                numerator += x * agg
                denominator += agg

            if denominator == 0:
                hasil = 50.0
            else:
                hasil = numerator / denominator

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
