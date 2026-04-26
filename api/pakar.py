import json
from http.server import BaseHTTPRequestHandler

PAKAR_RULES = {
    'Burnout Akademik': { 'G01': 0.8, 'G02': 0.6, 'G07': 0.7, 'G12': 0.8, 'G14': 0.9, 'G15': 0.7, 'G19': 0.9 },
    'Gangguan Kecemasan (Anxiety)': { 'G03': 0.8, 'G04': 0.6, 'G05': 0.9, 'G08': 0.6, 'G18': 0.8, 'G19': 0.7, 'G20': 0.7 },
    'Gangguan Tidur (Insomnia)': { 'G01': 0.7, 'G20': 0.9, 'G21': 0.9, 'G22': 0.8, 'G23': 0.7 },
    'Indikasi Depresi Ringan-Sedang': { 'G01': 0.6, 'G06': 0.9, 'G09': 0.8, 'G10': 0.7, 'G11': 0.8, 'G13': 0.9, 'G17': 0.6 }
}

SOLUSI = {
    'Burnout Akademik': ["Istirahat sejenak dari tugas kuliah.", "Terapkan manajemen waktu (seperti Pomodoro).", "Jangan ragu untuk menurunkan standar kesempurnaan sementara waktu."],
    'Gangguan Kecemasan (Anxiety)': ["Latih teknik relaksasi pernapasan dalam (Deep Breathing).", "Kurangi konsumsi kafein.", "Coba tuliskan kekhawatiran Anda di jurnal."],
    'Gangguan Tidur (Insomnia)': ["Terapkan Sleep Hygiene.", "Hindari layar gadget 1 jam sebelum tidur.", "Atur jadwal tidur yang konsisten dan hindari kopi di sore/malam hari."],
    'Indikasi Depresi Ringan-Sedang': ["Hubungi layanan konseling atau psikolog kampus.", "Ceritakan perasaan Anda kepada orang yang sangat Anda percayai.", "Jangan isolasi diri Anda."]
}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        try:
            selected_symptoms = data.get('symptoms', [])
            results = {}
            trace_log = []
            
            for disorder, symp_dict in PAKAR_RULES.items():
                cf_list = []
                for g_id, cf_pakar in symp_dict.items():
                    if g_id in selected_symptoms:
                        cf_list.append({"id": g_id, "cf": cf_pakar})
                
                if len(cf_list) > 0:
                    cf_combine = cf_list[0]["cf"]
                    trace_log.append({"id": cf_list[0]["id"], "disorder": disorder, "cf_rule": cf_list[0]["cf"], "cf_combine": cf_combine})
                    
                    for i in range(1, len(cf_list)):
                        cf_combine = cf_combine + cf_list[i]["cf"] * (1 - cf_combine)
                        trace_log.append({"id": cf_list[i]["id"], "disorder": disorder, "cf_rule": cf_list[i]["cf"], "cf_combine": cf_combine})
                        
                    results[disorder] = cf_combine
            
            if len(results) == 0:
                response = {"status": "empty"}
            else:
                sorted_res = sorted(results.items(), key=lambda x: x[1], reverse=True)
                best_match = sorted_res[0][0]
                
                other_res = []
                for k, v in sorted_res[1:]:
                    other_res.append({"name": k, "cf": v})
                    
                response = {
                    "status": "success",
                    "best_match": best_match,
                    "best_cf": sorted_res[0][1],
                    "solutions": SOLUSI[best_match],
                    "other": other_res,
                    "trace": trace_log
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
