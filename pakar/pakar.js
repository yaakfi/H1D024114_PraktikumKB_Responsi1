// Expert System Client-Side (Calling Python Backend)

const symptoms = [
    { id: 'G01', desc: 'Merasa lelah terus-menerus meskipun sudah tidur cukup', group: 'fisik' },
    { id: 'G02', desc: 'Sakit kepala berulang atau tegang otot tanpa sebab medis', group: 'fisik' },
    { id: 'G03', desc: 'Detak jantung terasa lebih cepat/berdebar (Palpitasi)', group: 'fisik' },
    { id: 'G04', desc: 'Gangguan pencernaan saat sedang banyak pikiran', group: 'fisik' },
    { id: 'G05', desc: 'Sering merasa cemas, gugup, atau gelisah berlebihan', group: 'emosi' },
    { id: 'G06', desc: 'Merasa sedih, hampa, atau putus asa terus-menerus', group: 'emosi' },
    { id: 'G07', desc: 'Mudah marah, tersinggung, atau kehilangan kesabaran', group: 'emosi' },
    { id: 'G08', desc: 'Perubahan mood (suasana hati) yang drastis', group: 'emosi' },
    { id: 'G09', desc: 'Merasa tidak berharga atau menyalahkan diri sendiri', group: 'emosi' },
    { id: 'G10', desc: 'Perubahan nafsu makan (makan terlalu banyak/sedikit)', group: 'perilaku' },
    { id: 'G11', desc: 'Menarik diri dari teman, keluarga, atau lingkungan sosial', group: 'perilaku' },
    { id: 'G12', desc: 'Menghindari tanggung jawab atau tugas kuliah', group: 'perilaku' },
    { id: 'G13', desc: 'Menurunnya minat pada hobi atau aktivitas yang biasanya disukai', group: 'perilaku' },
    { id: 'G14', desc: 'Sering menunda pekerjaan (Prokrastinasi ekstrem)', group: 'perilaku' },
    { id: 'G15', desc: 'Kesulitan berkonsentrasi saat belajar atau di kelas', group: 'kognitif' },
    { id: 'G16', desc: 'Sering lupa atau kesulitan mengingat informasi baru', group: 'kognitif' },
    { id: 'G17', desc: 'Kesulitan dalam membuat keputusan sehari-hari', group: 'kognitif' },
    { id: 'G18', desc: 'Pikiran yang terus berpacu (Racing thoughts)', group: 'kognitif' },
    { id: 'G19', desc: 'Sering merasa kewalahan (Overwhelmed) dengan tugas', group: 'kognitif' },
    { id: 'G20', desc: 'Sulit tidur di malam hari (Insomnia awal)', group: 'fisik' },
    { id: 'G21', desc: 'Sering terbangun di tengah malam', group: 'fisik' },
    { id: 'G22', desc: 'Bangun terlalu pagi dan merasa tidak segar', group: 'fisik' },
    { id: 'G23', desc: 'Sering bermimpi buruk', group: 'emosi' }
];

// Render Checkboxes
function initUI() {
    symptoms.forEach(sym => {
        const container = document.getElementById(`group-${sym.group}`);
        if(container) {
            const div = document.createElement('label');
            div.className = 'symptom-item';
            div.innerHTML = `
                <input type="checkbox" value="${sym.id}">
                <div class="custom-checkbox"></div>
                <div class="symptom-name">[${sym.id}] ${sym.desc}</div>
            `;
            div.querySelector('input').addEventListener('change', function() {
                if(this.checked) div.classList.add('checked');
                else div.classList.remove('checked');
                
                const checkedCount = document.querySelectorAll('.symptom-item input:checked').length;
                const total = symptoms.length;
                document.getElementById('prog-completion').textContent = Math.round((checkedCount/total)*100) + '%';
            });
            container.appendChild(div);
        }
    });
}

document.getElementById('btn-diagnose').addEventListener('click', async () => {
    const selected = Array.from(document.querySelectorAll('.symptom-item input:checked')).map(el => el.value);
    
    if(selected.length === 0) {
        alert("Pilih minimal satu gejala!");
        return;
    }

    const btn = document.getElementById('btn-diagnose');
    const origText = btn.innerHTML;
    btn.innerHTML = 'MENGHUBUNGI BACKEND PYTHON...';
    btn.disabled = true;

    try {
        const response = await fetch('/api/pakar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symptoms: selected })
        });
        
        const result = await response.json();
        
        if(result.status === 'empty') {
            alert("Gejala tidak cukup untuk diagnosis di sisi Python backend.");
            return;
        }

        if(result.status === 'success') {
            document.getElementById('result-name').textContent = result.best_match;
            document.getElementById('result-cf').textContent = (result.best_cf * 100).toFixed(2) + '%';
            document.getElementById('result-solusi').innerHTML = result.solutions.map(s => `<li>${s}</li>`).join('');

            let otherHtml = '';
            if(result.other.length > 0) {
                result.other.forEach(item => {
                    otherHtml += `<div class="other-item"><div class="name">${item.name}</div><div class="cf">${(item.cf*100).toFixed(2)}%</div></div>`;
                });
            } else {
                otherHtml = '<div class="other-item"><div class="name">Tidak ada indikasi sekunder</div></div>';
            }
            document.getElementById('other-results').innerHTML = otherHtml;

            let traceHtml = '';
            result.trace.forEach(t => {
                traceHtml += `<tr><td>${t.id}</td><td>${t.disorder}</td><td>${t.cf_rule}</td><td>${t.cf_combine.toFixed(4)}</td></tr>`;
            });
            document.getElementById('trace-table-body').innerHTML = traceHtml;

            document.getElementById('results-section').classList.remove('hidden');
            
            document.querySelectorAll('.quest-steps li')[0].classList.remove('active');
            document.querySelectorAll('.quest-steps li')[2].classList.add('active');
            document.getElementById('prog-completion').textContent = '100%';
        }
    } catch (e) {
        alert("Gagal menghubungi server Python: " + e);
    } finally {
        btn.innerHTML = origText;
        btn.disabled = false;
    }
});

initUI();
