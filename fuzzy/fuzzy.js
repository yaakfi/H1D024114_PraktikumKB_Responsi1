// Fuzzy Logic Client-Side (Calling Python Backend)

const membership = {
    winrate: {
        rendah: x => x <= 40 ? 1 : (x >= 50 ? 0 : (50 - x) / 10),
        sedang: x => x <= 45 || x >= 65 ? 0 : (x <= 55 ? (x - 45) / 10 : (65 - x) / 10),
        tinggi: x => x <= 60 ? 0 : (x >= 70 ? 1 : (x - 60) / 10)
    },
    durasi: {
        sebentar: x => x <= 2 ? 1 : (x >= 4 ? 0 : (4 - x) / 2),
        sedang: x => x <= 3 || x >= 7 ? 0 : (x <= 5 ? (x - 3) / 2 : (7 - x) / 2),
        lama: x => x <= 6 ? 0 : (x >= 8 ? 1 : (x - 6) / 2)
    },
    tugas: {
        sedikit: x => x <= 2 ? 1 : (x >= 4 ? 0 : (4 - x) / 2),
        sedang: x => x <= 3 || x >= 7 ? 0 : (x <= 5 ? (x - 3) / 2 : (7 - x) / 2),
        banyak: x => x <= 6 ? 0 : (x >= 8 ? 1 : (x - 6) / 2)
    },
    stres: {
        rendah: x => x <= 20 ? 1 : (x >= 40 ? 0 : (40 - x) / 20),
        sedang: x => x <= 30 || x >= 70 ? 0 : (x <= 50 ? (x - 30) / 20 : (70 - x) / 20),
        tinggi: x => x <= 60 ? 0 : (x >= 80 ? 1 : (x - 60) / 20)
    }
};

let charts = {};
let gaugeChart = null;

function initCharts() {
    const commonOptions = { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 1 } }, animation: { duration: 0 } };
    
    // Gauge Chart (Doughnut)
    gaugeChart = new Chart(document.getElementById('gauge-canvas').getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['Stress', 'Remaining'],
            datasets: [{
                data: [0, 100],
                backgroundColor: ['#4dff91', 'rgba(255,255,255,0.1)'],
                borderWidth: 0,
                circumference: 180,
                rotation: 270
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            cutout: '80%',
            plugins: { tooltip: { enabled: false }, legend: { display: false } }
        }
    });

    // Winrate
    charts.winrate = new Chart(document.getElementById('chart-winrate').getContext('2d'), {
        type: 'line',
        data: { labels: Array.from({length: 101}, (_, i) => i), datasets: [
            { label: 'Rendah', data: Array.from({length: 101}, (_, i) => membership.winrate.rendah(i)), borderColor: '#ff5c8a', fill: false, pointRadius: 0 },
            { label: 'Sedang', data: Array.from({length: 101}, (_, i) => membership.winrate.sedang(i)), borderColor: '#ffde59', fill: false, pointRadius: 0 },
            { label: 'Tinggi', data: Array.from({length: 101}, (_, i) => membership.winrate.tinggi(i)), borderColor: '#4dff91', fill: false, pointRadius: 0 }
        ]},
        options: commonOptions
    });
    
    // Durasi
    charts.durasi = new Chart(document.getElementById('chart-durasi').getContext('2d'), {
        type: 'line',
        data: { labels: Array.from({length: 25}, (_, i) => i/2), datasets: [
            { label: 'Sebentar', data: Array.from({length: 25}, (_, i) => membership.durasi.sebentar(i/2)), borderColor: '#4dff91', fill: false, pointRadius: 0 },
            { label: 'Sedang', data: Array.from({length: 25}, (_, i) => membership.durasi.sedang(i/2)), borderColor: '#ffde59', fill: false, pointRadius: 0 },
            { label: 'Lama', data: Array.from({length: 25}, (_, i) => membership.durasi.lama(i/2)), borderColor: '#ff5c8a', fill: false, pointRadius: 0 }
        ]},
        options: commonOptions
    });

    // Tugas
    charts.tugas = new Chart(document.getElementById('chart-tugas').getContext('2d'), {
        type: 'line',
        data: { labels: Array.from({length: 11}, (_, i) => i), datasets: [
            { label: 'Sedikit', data: Array.from({length: 11}, (_, i) => membership.tugas.sedikit(i)), borderColor: '#4dff91', fill: false, pointRadius: 0 },
            { label: 'Sedang', data: Array.from({length: 11}, (_, i) => membership.tugas.sedang(i)), borderColor: '#ffde59', fill: false, pointRadius: 0 },
            { label: 'Banyak', data: Array.from({length: 11}, (_, i) => membership.tugas.banyak(i)), borderColor: '#ff5c8a', fill: false, pointRadius: 0 }
        ]},
        options: commonOptions
    });

    // Output
    charts.output = new Chart(document.getElementById('chart-output').getContext('2d'), {
        type: 'line',
        data: { labels: Array.from({length: 101}, (_, i) => i), datasets: [
            { label: 'Rendah', data: Array.from({length: 101}, (_, i) => membership.stres.rendah(i)), borderColor: '#4dff91', fill: false, pointRadius: 0 },
            { label: 'Sedang', data: Array.from({length: 101}, (_, i) => membership.stres.sedang(i)), borderColor: '#ffde59', fill: false, pointRadius: 0 },
            { label: 'Tinggi', data: Array.from({length: 101}, (_, i) => membership.stres.tinggi(i)), borderColor: '#ff5c8a', fill: false, pointRadius: 0 }
        ]},
        options: commonOptions
    });
}

document.querySelectorAll('input[type=range]').forEach(input => {
    input.addEventListener('input', (e) => {
        document.getElementById(`value-${e.target.id.split('-')[1]}`).textContent = e.target.value;
    });
});

document.getElementById('btn-calculate').addEventListener('click', async () => {
    const btn = document.getElementById('btn-calculate');
    const originalText = btn.textContent;
    btn.textContent = 'MENGHUBUNGI BACKEND PYTHON...';
    btn.disabled = true;

    const winrate = parseFloat(document.getElementById('slider-winrate').value);
    const durasi = parseFloat(document.getElementById('slider-durasi').value);
    const tugas = parseFloat(document.getElementById('slider-tugas').value);

    try {
        const response = await fetch('/api/fuzzy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ winrate, durasi, tugas })
        });
        
        const result = await response.json();
        
        if(result.status === 'success') {
            const crispResult = result.crisp_result;
            
            // UI Updates
            document.getElementById('results-section').classList.remove('hidden');
            const lvlEl = document.getElementById('stress-level');
            lvlEl.textContent = crispResult.toFixed(2);
            
            let color = '#4dff91';
            if(crispResult > 65) color = '#ff5c8a';
            else if(crispResult > 35) color = '#ffde59';

            lvlEl.style.color = color;

            // Update Gauge
            gaugeChart.data.datasets[0].data = [crispResult, 100 - crispResult];
            gaugeChart.data.datasets[0].backgroundColor[0] = color;
            gaugeChart.update();

            // HP Bar
            const hpVal = Math.round(100 - crispResult);
            document.getElementById('hp-value').textContent = `${hpVal} / 100`;
            const segments = document.querySelectorAll('#hp-bar .seg');
            const filled = Math.round((hpVal / 100) * 6);
            segments.forEach((seg, i) => {
                if(i < filled) { seg.className='seg filled'; seg.style.background=color; seg.style.boxShadow=`0 0 10px ${color}`; }
                else { seg.className='seg'; seg.style.background='rgba(255,255,255,0.1)'; seg.style.boxShadow='none'; }
            });

            // Impact Labels
            document.getElementById('impact-winrate').textContent = winrate < 45 ? 'CRITICAL (-)' : 'POSITIVE (+)';
            document.getElementById('impact-winrate').style.color = winrate < 45 ? '#ff5c8a' : '#4dff91';
            document.getElementById('impact-tugas').textContent = tugas > 6 ? 'HIGH LOAD' : 'NORMAL';
            document.getElementById('impact-tugas').style.color = tugas > 6 ? '#ff5c8a' : '#4dff91';
            document.getElementById('impact-durasi').textContent = durasi > 6 ? 'EXCESSIVE' : 'BALANCED';
            document.getElementById('impact-durasi').style.color = durasi > 6 ? '#ffde59' : '#4dff91';

            // Fuzzification Table
            let fuzzHtml = '';
            if(result.fuzz_table && result.fuzz_table.length > 0) {
                result.fuzz_table.forEach(f => {
                    fuzzHtml += `<tr><td>${f.var}</td><td>${f.set}</td><td>${f.val.toFixed(2)}</td></tr>`;
                });
            } else {
                fuzzHtml = `<tr><td colspan="3" style="text-align:center;">Data tidak ditemukan.</td></tr>`;
            }
            document.getElementById('fuzz-table-body').innerHTML = fuzzHtml;

            // Fired Rules Table
            let rulesHtml = '';
            if(result.rules_log && result.rules_log.length > 0) {
                result.rules_log.forEach(r => {
                    rulesHtml += `<tr><td>R${r.rule_idx}</td><td>IF ${r.if}</td><td>THEN ${r.then}</td><td>${r.alpha.toFixed(2)}</td></tr>`;
                });
            } else {
                rulesHtml = `<tr><td colspan="4" style="text-align:center;">Tidak ada aturan yang terpicu (>0).</td></tr>`;
            }
            document.getElementById('rules-table-body').innerHTML = rulesHtml;
        }
    } catch (err) {
        alert('Gagal menghubungi backend Python: ' + err);
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
});

// Initialize
initCharts();
