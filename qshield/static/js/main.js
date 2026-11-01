/* ============================================================
   Q‑SHIELD — main.js  (Complete Cinematic Edition)
   ============================================================ */
window.QState = {
    mlTrained: false,
    lastQber: null,
    siftedCount: 0,
    rawCount: 256,
    finalKeyLen: 32,
    qberHistory: [],
    chartInstances: {},
    d3Simulation: null,
    blochScene: null,
    blochSphere: null
};

document.addEventListener('DOMContentLoaded', () => {

    // ===================== CUSTOM QUANTUM CURSOR =====================
    const cursor = document.getElementById('quantumCursor');
    document.addEventListener('mousemove', e => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
    });
    document.querySelectorAll('.btn-neon, .glass-card, .nav-dot, textarea, select, input[type="number"]').forEach(el => {
        el.addEventListener('mouseenter', () => cursor.classList.add('hover'));
        el.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
    });

    // ===================== AMBIENT AUDIO (activated on first click) =====================
    const ambientAudio = document.getElementById('ambientAudio');
    if (ambientAudio) {
        ambientAudio.volume = 0.08;
        document.addEventListener('click', () => {
            if (ambientAudio.paused) ambientAudio.play().catch(() => {});
        }, { once: true });
    }

    // ===================== 3D CARD TILT =====================
    document.querySelectorAll('.glass-card').forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;
            card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });

    // ===================== MAGNETIC BUTTONS =====================
    document.querySelectorAll('.btn-neon').forEach(btn => {
        btn.addEventListener('mousemove', e => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px) scale(1.03)`;
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = '';
        });
    });

    // ===================== GSAP SCROLL ANIMATIONS =====================
    gsap.registerPlugin(ScrollTrigger);
    document.querySelectorAll('[data-scroll-animate]').forEach(section => {
        const elements = section.querySelectorAll('.glass-card, .hero-content > *, .chart-container');
        gsap.fromTo(elements,
            { opacity: 0, y: 40 },
            {
                opacity: 1, y: 0,
                duration: 0.8,
                stagger: 0.1,
                ease: 'power2.out',
                scrollTrigger: {
                    trigger: section,
                    start: 'top 80%',
                    toggleActions: 'play none none reverse'
                }
            }
        );
    });

    // ===================== PARALLAX STARFIELD (with depth layers) =====================
    const canvas = document.getElementById('quantumCanvas'),
        ctx = canvas.getContext('2d');
    let stars = [],
        mouseX = -1000,
        mouseY = -1000;
    const STAR_COUNT = 45;
    let lastMouseMove = 0;

    window.addEventListener('mousemove', e => {
        const now = Date.now();
        if (now - lastMouseMove < 30) return;
        lastMouseMove = now;
        mouseX = e.clientX;
        mouseY = e.clientY;
    });
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    class Star {
        constructor(depth) {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.2;
            this.vy = (Math.random() - 0.5) * 0.2;
            this.r = depth === 0 ? Math.random() * 1.2 + 0.3 : Math.random() * 2.2 + 0.8;
            this.brightness = Math.random();
            this.twinkle = 0.003 + Math.random() * 0.008;
            this.hue = Math.random() < 0.7 ? 245 : 190;
            this.depth = depth; // 0 = far, 1 = near
            this.parallax = depth === 1 ? 0.012 : 0.004;
        }
        update() {
            const dx = this.x - mouseX,
                dy = this.y - mouseY,
                dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 160) {
                this.vx += (dx / dist) * this.parallax;
                this.vy += (dy / dist) * this.parallax;
            }
            this.vx *= 0.998;
            this.vy *= 0.998;
            this.x += this.vx;
            this.y += this.vy;
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
            this.brightness += this.twinkle;
            if (this.brightness > 1 || this.brightness < 0.3) this.twinkle *= -1;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.r, 0, 2 * Math.PI);
            ctx.fillStyle = `hsla(${this.hue},60%,70%,${this.brightness})`;
            ctx.fill();
        }
    }
    for (let i = 0; i < STAR_COUNT; i++) {
        stars.push(new Star(i < STAR_COUNT * 0.4 ? 1 : 0));
    }

    function animateStars() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        stars.forEach(s => { s.update(); s.draw(); });
        requestAnimationFrame(animateStars);
    }
    animateStars();

    // ===================== PARTICLE DISSOLVE (Hero title) =====================
    const heroTitle = document.getElementById('heroTitle');
    if (heroTitle) {
        window.addEventListener('scroll', () => {
            const opacity = Math.max(0, 1 - window.scrollY / 300);
            heroTitle.style.opacity = opacity;
            if (opacity < 0.3) heroTitle.classList.add('dissolving');
            else heroTitle.classList.remove('dissolving');
        });
    }

    // ===================== PARTICLE BURST =====================
    function spawnBurst(x, y, colors = ['#8b5cf6', '#06b6d4', '#10b981']) {
        const c = document.getElementById('particleContainer');
        for (let i = 0; i < 22; i++) {
            const p = document.createElement('div');
            p.className = 'btn-particle';
            p.style.cssText = `left:${x}px;top:${y}px;width:${3+Math.random()*6}px;height:${3+Math.random()*6}px;background:${colors[Math.floor(Math.random()*colors.length)]};--px:${Math.cos(Math.random()*2*Math.PI)*50}px;--py:${Math.sin(Math.random()*2*Math.PI)*50}px;`;
            c.appendChild(p);
            setTimeout(() => p.remove(), 600);
        }
    }
    document.querySelectorAll('.btn-neon').forEach(b => b.addEventListener('click', e => {
        const r = b.getBoundingClientRect();
        spawnBurst(r.left + r.width / 2, r.top + r.height / 2);
    }));

    // ===================== SIDE NAVIGATION =====================
    const sections = document.querySelectorAll('.full-section');
    const navDots = document.querySelectorAll('.nav-dot');
    document.getElementById('gotoQuantumBtn').addEventListener('click', () =>
        document.getElementById('section-quantum').scrollIntoView({ behavior: 'smooth' }));
    window.addEventListener('scroll', () => {
        const sp = window.scrollY + window.innerHeight / 2;
        sections.forEach((s, i) => {
            if (sp >= s.offsetTop && sp < s.offsetTop + s.offsetHeight) {
                navDots.forEach(d => d.classList.remove('active'));
                if (navDots[i]) navDots[i].classList.add('active');
            }
        });
    });
    navDots.forEach((d, i) => d.addEventListener('click', e => {
        e.preventDefault();
        sections[i].scrollIntoView({ behavior: 'smooth' });
    }));

    // ===================== WEBSOCKET =====================
    const socket = io();
    socket.on('connect', () => console.log('WS live'));
    socket.on('qkd_start', () => updateStatus('active', false));
    socket.on('key_ready', d => {
        document.getElementById('qberValue').textContent = d.qber + '%';
        QState.lastQber = parseFloat(d.qber);
        updateAllGauges(QState.lastQber);
    });
    socket.on('eve_detected', d => {
        updateStatus(false, true);
        document.getElementById('qberValue').textContent = d.qber + '%';
    });

    function updateStatus(active, compromised) {
        const dot = document.getElementById('statusDot'),
            txt = document.getElementById('statusText');
        dot.classList.remove('active', 'compromised', 'dot-idle');
        if (compromised) { dot.classList.add('compromised'); txt.textContent = '⚠️ Eavesdropper Detected'; }
        else if (active) { dot.classList.add('active'); txt.textContent = '● Quantum Channel Active'; }
        else { dot.classList.add('dot-idle'); txt.textContent = 'System Idle'; }
    }

    // ===================== PROTOCOL FLOW ANIMATION =====================
    const flowSteps = document.querySelectorAll('.flow-step');
    function activateFlowStep(name) {
        flowSteps.forEach(s => s.classList.remove('active'));
        const step = document.querySelector(`.flow-step[data-step="${name}"]`);
        if (step) step.classList.add('active');
    }
    socket.on('alice_prepared', () => activateFlowStep('prepare'));
    socket.on('bob_measured', () => activateFlowStep('measure'));
    socket.on('sifting_done', () => activateFlowStep('sift'));
    socket.on('qber_computed', () => activateFlowStep('qber'));
    socket.on('key_ready', () => activateFlowStep('final'));

    // ===================== TYPING EFFECT & GLITCH =====================
    function typeWriter(el, text, speed = 20, cb) {
        let i = 0; el.textContent = '';
        function type() { if (i < text.length) { el.textContent += text.charAt(i); i++; setTimeout(type, speed); } else if (cb) cb(); }
        type();
    }
    function glitchElement(el) { el.classList.add('glitch'); setTimeout(() => el.classList.remove('glitch'), 300); }

    // ===================== NUMBER COUNTER ANIMATION =====================
    function animateValue(el, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            el.textContent = (progress * (end - start) + start).toFixed(1) + '%';
            if (progress < 1) window.requestAnimationFrame(step);
        };
        window.requestAnimationFrame(step);
    }

    // ===================== CHART INITIALIZATION (with animation) =====================
    function initChartWhenReady(canvasId, chartKey, createFn) {
        const el = document.getElementById(canvasId);
        if (!el || QState.chartInstances[chartKey]) return;
        if (el.clientWidth === 0 || el.clientHeight === 0) {
            requestAnimationFrame(() => initChartWhenReady(canvasId, chartKey, createFn));
            return;
        }
        QState.chartInstances[chartKey] = createFn(el);
    }
    function lazyInitAllCharts() {
        initChartWhenReady('qberHistoryChart', 'qberHistory', (el) => new Chart(el.getContext('2d'), {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'QBER %', data: [], borderColor: '#10b981', tension: 0.3 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 20, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }, x: { ticks: { color: '#94a3b8' } } }, animation: { duration: 800, easing: 'easeOutBounce' } }
        }));
        initChartWhenReady('bitDistChart', 'bitDist', (el) => new Chart(el.getContext('2d'), {
            type: 'bar',
            data: { labels: ['Raw', 'Sifted', 'Final'], datasets: [{ data: [0, 0, 0], backgroundColor: ['#8b5cf6', '#06b6d4', '#10b981'] }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }, x: { ticks: { color: '#94a3b8' } } }, animation: { duration: 800 } }
        }));
        initChartWhenReady('anomalyGaugeChart', 'anomalyGauge', (el) => new Chart(el.getContext('2d'), {
            type: 'doughnut',
            data: { labels: ['Normal', 'Attack'], datasets: [{ data: [100, 0], backgroundColor: ['#10b981', '#ef4444'] }] },
            options: { responsive: true, maintainAspectRatio: false, cutout: '65%', plugins: { legend: { display: false } } }
        }));
        initChartWhenReady('forecastChart', 'forecastChart', (el) => new Chart(el.getContext('2d'), {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'SKR bps', data: [], borderColor: '#0ea5e9', tension: 0.3 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }, x: { ticks: { color: '#94a3b8' } } } }
        }));
        initChartWhenReady('benchmarkChart', 'benchmarkChart', (el) => new Chart(el.getContext('2d'), {
            type: 'bar',
            data: { labels: ['RSA-2048', 'ECDH-P256', 'Q-SHIELD'], datasets: [{ data: [0, 0, 0], backgroundColor: ['#8b5cf6', '#06b6d4', '#10b981'] }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }, x: { ticks: { color: '#94a3b8' } } } }
        }));
    }
    window.addEventListener('load', lazyInitAllCharts);
    window.addEventListener('resize', lazyInitAllCharts);

    // ===================== D3 QUANTUM NETWORK (Alice‑Bob) =====================
    let qD3ready = false;
    function initQKDNetworkViz() {
        if (qD3ready) return;
        const container = document.getElementById('qkdNetworkViz');
        if (!container || container.clientWidth === 0) { requestAnimationFrame(initQKDNetworkViz); return; }
        const w = container.clientWidth, h = container.clientHeight;
        d3.select('#qkdNetworkViz').selectAll('*').remove();
        const svg = d3.select('#qkdNetworkViz').append('svg').attr('width', w).attr('height', h);
        const nodes = [{ id: 'Alice', x: w * 0.2, y: h / 2 }, { id: 'Bob', x: w * 0.8, y: h / 2 }];
        const links = [{ source: 'Alice', target: 'Bob' }];
        const sim = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(300))
            .force('charge', d3.forceManyBody().strength(-200))
            .force('center', d3.forceCenter(w / 2, h / 2));
        svg.append('g').selectAll('line').data(links).join('line').attr('stroke', '#8b5cf6').attr('stroke-width', 2).attr('stroke-dasharray', '8,8');
        svg.append('g').selectAll('circle').data(nodes).join('circle').attr('r', 22).attr('fill', d => d.id === 'Alice' ? '#a5b4fc' : '#67e8f9');
        svg.append('g').selectAll('text').data(nodes).join('text').text(d => d.id).attr('fill', '#e2e8f0').attr('font-family', 'Inter, sans-serif').attr('font-size', '13px').attr('dx', 28).attr('dy', 5);
        sim.on('tick', () => {
            svg.selectAll('line').attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
            svg.selectAll('circle').attr('cx', d => d.x).attr('cy', d => d.y);
            svg.selectAll('text').attr('x', d => d.x).attr('y', d => d.y);
        });
        QState.d3Simulation = sim;
        qD3ready = true;
    }
    function animateQubitFlow() {
        if (!qD3ready || !QState.d3Simulation) return;
        const svg = d3.select('#qkdNetworkViz svg');
        const alice = QState.d3Simulation.nodes().find(n => n.id === 'Alice');
        const bob = QState.d3Simulation.nodes().find(n => n.id === 'Bob');
        if (!alice || !bob) return;
        for (let i = 0; i < 20; i++) {
            svg.append('circle').attr('r', 3).attr('fill', '#f472b6').attr('cx', alice.x).attr('cy', alice.y)
                .transition().duration(600).delay(i * 40).attr('cx', bob.x).attr('cy', bob.y).remove();
        }
    }
    window.addEventListener('load', initQKDNetworkViz);
    window.addEventListener('resize', () => { qD3ready = false; initQKDNetworkViz(); });
    socket.on('alice_prepared', () => { initQKDNetworkViz(); animateQubitFlow(); });
    socket.on('key_ready', () => { initQKDNetworkViz(); });

    // ===================== BLOCH SPHERE (Three.js) =====================
    function initBlochSphere() {
        const container = document.getElementById('blochContainer');
        if (!container || QState.blochSphere) return;
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
        camera.position.z = 3.5;
        const renderer = new THREE.WebGLRenderer({ alpha: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);
        const geometry = new THREE.SphereGeometry(1.2, 32, 32);
        const material = new THREE.MeshBasicMaterial({ color: 0x8b5cf6, wireframe: true, transparent: true, opacity: 0.25 });
        const sphere = new THREE.Mesh(geometry, material);
        scene.add(sphere);
        const axesHelper = new THREE.AxesHelper(1.8);
        scene.add(axesHelper);
        function animate() {
            requestAnimationFrame(animate);
            sphere.rotation.y += 0.002;
            sphere.rotation.x += 0.001;
            renderer.render(scene, camera);
        }
        animate();
        QState.blochSphere = sphere;
        QState.blochScene = scene;
    }
    window.addEventListener('load', () => setTimeout(initBlochSphere, 600));
    window.addEventListener('resize', () => {
        const container = document.getElementById('blochContainer');
        if (!container || !QState.blochSphere) return;
        const w = container.clientWidth, h = container.clientHeight;
        QState.blochScene.camera.aspect = w / h;
        QState.blochScene.camera.updateProjectionMatrix();
        QState.blochScene.renderer.setSize(w, h);
    });

    // ===================== GAUGE & METRICS UPDATE =====================
    function updateAllGauges(qber) {
        const cls = qber < 5 ? 'safe' : (qber <= 11 ? 'warning' : 'danger');
        ['qberGaugeFill', 'expGaugeFill'].forEach(id => {
            const f = document.getElementById(id); if (!f) return;
            const dashLen = (qber / 20) * 240;
            f.setAttribute('stroke-dasharray', `${Math.min(dashLen, 240)} 240`);
            f.classList.remove('safe', 'warning', 'danger'); f.classList.add(cls);
        });
        const v1 = document.getElementById('qberGaugeValue');
        if (v1) animateValue(v1, 0, qber, 800);
        const v2 = document.getElementById('expGaugeValue');
        if (v2) v2.textContent = qber.toFixed(1) + '%';
    }
    function updateSparklines(raw, sifted, finalLen) {
        const max = Math.max(raw, sifted, finalLen, 1);
        ['barRaw', 'barSifted', 'barFinal'].forEach((id, i) => {
            const el = document.getElementById(id); if (!el) return;
            el.style.height = ([raw, sifted, finalLen][i] / max * 100) + '%';
        });
    }
    function updateCharts(qber, raw, sifted, finalLen) {
        const qh = QState.chartInstances.qberHistory;
        if (qh) { qh.data.labels.push('R' + (qh.data.labels.length + 1)); qh.data.datasets[0].data.push(qber); if (qh.data.labels.length > 10) { qh.data.labels.shift(); qh.data.datasets[0].data.shift(); } qh.update(); }
        const bd = QState.chartInstances.bitDist;
        if (bd) { bd.data.datasets[0].data = [raw, sifted, finalLen]; bd.update(); }
    }

    // ===================== GENERATE KEYS (BB84) =====================
    document.getElementById('generateBtn').addEventListener('click', async () => {
        const btn = document.getElementById('generateBtn');
        btn.disabled = true; btn.querySelector('.btn-content').textContent = 'Generating...';
        try {
            const res = await fetch('/generate_keys', { method: 'POST' });
            const data = await res.json();
            const term = document.getElementById('keyTerminalBody');
            if (data.status === 'success') {
                term.innerHTML = '';
                typeWriter(term, `✅ Keys Ready\nQKD: ${data.qkd_key_snippet}\nPQC: ${data.pqc_key_snippet}\nHybrid: ${data.final_key_snippet}\nQBER: ${data.qber_percent}%`, 15);
                QState.lastQber = data.qber_percent; QState.siftedCount = Math.floor(data.qber_percent * 10); QState.finalKeyLen = 32;
                updateAllGauges(data.qber_percent);
                updateSparklines(256, QState.siftedCount, QState.finalKeyLen);
                updateCharts(data.qber_percent, 256, QState.siftedCount, QState.finalKeyLen);
                updateStatus(true, false);
                document.getElementById('qberValue').textContent = data.qber_percent + '%';
                initQKDNetworkViz(); animateQubitFlow();
            } else {
                term.innerHTML = `<div class="terminal-error">⚠️ ${data.message}</div>`;
                glitchElement(term); updateStatus(false, true);
            }
        } catch (e) { console.error(e); }
        finally { btn.disabled = false; btn.querySelector('.btn-content').textContent = 'Generate Keys'; }
    });

    // ===================== E91 PROTOCOL =====================
    document.getElementById('e91Btn')?.addEventListener('click', async () => {
        const btn = document.getElementById('e91Btn');
        btn.disabled = true; btn.querySelector('.btn-content').textContent = 'E91...';
        try {
            const res = await fetch('/generate_keys_e91', { method: 'POST' });
            const data = await res.json();
            const term = document.getElementById('keyTerminalBody');
            if (data.status === 'success') {
                term.innerHTML = '';
                typeWriter(term, `✅ E91 Keys Ready\nQKD: ${data.qkd_key_snippet}\nPQC: ${data.pqc_key_snippet}\nHybrid: ${data.final_key_snippet}\nQBER: ${data.qber_percent}%`, 15);
                QState.lastQber = data.qber_percent;
                updateAllGauges(data.qber_percent);
                updateStatus(true, false);
            } else {
                term.innerHTML = `<div class="terminal-error">⚠️ ${data.message || 'E91 failed'}</div>`;
                glitchElement(term);
            }
        } catch (e) { console.error(e); }
        finally { btn.disabled = false; btn.querySelector('.btn-content').textContent = 'E91 Protocol'; }
    });

    // ===================== MDI QKD (placeholder) =====================
    document.getElementById('mdiBtn')?.addEventListener('click', async () => {
        alert('MDI‑QKD simulation will be fully integrated soon. Currently running BB84 as a stand‑in.');
        document.getElementById('generateBtn').click();
    });

    // ===================== ENCRYPT / DECRYPT =====================
    document.getElementById('encryptBtn').addEventListener('click', async () => {
        const msg = document.getElementById('messageInput').value.trim();
        if (!msg) return alert('Type a message');
        try {
            const res = await fetch('/encrypt', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: msg }) });
            const data = await res.json();
            document.getElementById('encryptTerminalBody').innerHTML = data.status === 'encrypted' ?
                `<div class="terminal-success">🔒 Encrypted</div>Ciphertext: ${data.ciphertext_snippet}` :
                `<div class="terminal-error">${data.message}</div>`;
        } catch (e) { console.error(e); }
    });
    document.getElementById('decryptBtn').addEventListener('click', async () => {
        try {
            const res = await fetch('/decrypt', { method: 'POST' });
            const data = await res.json();
            document.getElementById('decryptTerminalBody').innerHTML = data.status === 'decrypted' ?
                `<div class="terminal-success">✅ Decrypted</div>Message: "${data.plaintext}"` :
                `<div class="terminal-error">${data.message}</div>`;
        } catch (e) { console.error(e); }
    });

    // ===================== NETWORK SIMULATION (with D3 graph) =====================
    document.getElementById('simulateNetworkBtn').addEventListener('click', async () => {
        let netRes = document.getElementById('networkResult');
        netRes.innerHTML = '<span class="terminal-prompt">$</span> Creating network…';
        await fetch('/api/network/create', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nodes: [{ id: 'Alice' }, { id: 'T1', name: 'Trusted Relay 1' }, { id: 'T2', name: 'Trusted Relay 2' }, { id: 'Bob' }],
                links: [{ node1: 'Alice', node2: 'T1', distance_km: 30 }, { node1: 'T1', node2: 'T2', distance_km: 50 }, { node1: 'T2', node2: 'Bob', distance_km: 20 }]
            })
        });
        const simRes = await fetch('/api/network/simulate', { method: 'POST' });
        const simData = await simRes.json();
        let html = '<div class="terminal-success">✅ Network Simulated</div>';
        (simData.summary?.simulation_log || []).forEach(l => html += `<div>${l.link}: QBER ${l.qber}%, Key ${l.key_length}B</div>`);
        try {
            const e2e = await fetch('/api/network/key/Alice/Bob');
            const e2eData = await e2e.json();
            html += `<div class="mt-2"><strong>End‑to‑End Key:</strong> ${e2eData.key}</div>`;
        } catch (e) {}
        netRes.innerHTML = html;

        // Draw multi‑node graph in networkGraphViz
        const container = document.getElementById('networkGraphViz');
        if (!container || container.clientWidth === 0) return;
        const w = container.clientWidth, h = 420;
        d3.select('#networkGraphViz').selectAll('*').remove();
        const svg = d3.select('#networkGraphViz').append('svg').attr('width', w).attr('height', h);
        const nodes = [{ id: 'A', x: 80, y: 210 }, { id: 'T1', x: 280, y: 110 }, { id: 'T2', x: 520, y: 310 }, { id: 'B', x: 720, y: 210 }];
        const links = [{ source: 'A', target: 'T1' }, { source: 'T1', target: 'T2' }, { source: 'T2', target: 'B' }];
        const sim = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(180))
            .force('charge', d3.forceManyBody().strength(-250))
            .force('center', d3.forceCenter(400, 210));
        svg.selectAll('line').data(links).join('line').attr('stroke', '#8b5cf6').attr('stroke-width', 2);
        svg.selectAll('circle').data(nodes).join('circle').attr('r', 16).attr('fill', d => d.id === 'A' ? '#a5b4fc' : d.id === 'B' ? '#67e8f9' : '#fbbf24');
        svg.selectAll('text').data(nodes).join('text').text(d => d.id).attr('fill', '#e2e8f0').attr('dx', 20).attr('dy', 5).attr('font-size', '11px');
        sim.on('tick', () => {
            svg.selectAll('line').attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
            svg.selectAll('circle').attr('cx', d => d.x).attr('cy', d => d.y);
            svg.selectAll('text').attr('x', d => d.x).attr('y', d => d.y);
        });
    });

    // ===================== RELAY CHAIN (optional) =====================
    document.getElementById('relayChainBtn')?.addEventListener('click', async () => {
        const res = await fetch('/api/network/relay_chain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chain: ['Alice', 'T1', 'T2', 'Bob'] })
        });
        const data = await res.json();
        document.getElementById('networkResult').innerHTML = `<div class="terminal-success">✅ Relay Chain</div>End‑to‑End Key: ${data.end_to_end_key}`;
    });

    // ===================== SATELLITE LINK BUDGET =====================
    document.getElementById('calculateLinkBudgetBtn').addEventListener('click', async () => {
        const payload = {
            altitude_km: +document.getElementById('satAltitude').value,
            zenith_deg: +document.getElementById('satZenith').value,
            atmospheric_db: +document.getElementById('satAtm').value
        };
        const res = await fetch('/api/satellite/link_budget', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        const data = await res.json();
        document.getElementById('satResult').innerHTML = `<div class="terminal-success">🛰️ Results</div>Distance: ${data.link_distance_km} km<br>Total Loss: ${data.total_loss_db} dB<br><strong>SKR: ${data.estimated_skr_bps} bps</strong>`;
        const orbDiv = document.getElementById('satOrbitViz');
        if (!orbDiv) return;
        const ow = orbDiv.clientWidth || 400, oh = 380;
        d3.select('#satOrbitViz').selectAll('*').remove();
        const osvg = d3.select('#satOrbitViz').append('svg').attr('width', ow).attr('height', oh);
        osvg.append('circle').attr('cx', ow / 2).attr('cy', oh / 2).attr('r', 120).attr('fill', 'none').attr('stroke', 'rgba(255,255,255,0.1)').attr('stroke-width', 2);
        osvg.append('circle').attr('cx', ow / 2).attr('cy', oh / 2).attr('r', 6).attr('fill', '#10b981');
        osvg.append('text').attr('x', ow / 2).attr('y', oh / 2 - 15).text('🌍 Ground').attr('fill', '#e2e8f0').attr('text-anchor', 'middle').attr('font-size', '12px');
        const satX = ow / 2 + 120 * Math.cos(Math.random() * 2 * Math.PI), satY = oh / 2 + 120 * Math.sin(Math.random() * 2 * Math.PI);
        osvg.append('circle').attr('cx', satX).attr('cy', satY).attr('r', 8).attr('fill', '#fbbf24');
        osvg.append('text').attr('x', satX).attr('y', satY - 15).text('🛰️ Sat').attr('fill', '#e2e8f0').attr('text-anchor', 'middle').attr('font-size', '12px');
        osvg.append('line').attr('x1', ow / 2).attr('y1', oh / 2).attr('x2', satX).attr('y2', satY).attr('stroke', '#06b6d4').attr('stroke-width', 1).attr('stroke-dasharray', '6,6');
    });

    // ===================== ML ANOMALY DETECTION =====================
    document.getElementById('trainMLBtn')?.addEventListener('click', async () => {
        const res = await fetch('/api/ml/train', { method: 'POST' });
        const data = await res.json();
        window.QState.mlTrained = true;
        document.getElementById('mlStatus').innerHTML = '<span style="color:#10b981;">✅ ' + data.message + '</span>';
    });
    document.getElementById('predictAttackBtn')?.addEventListener('click', async () => {
        if (!window.QState.mlTrained) return alert('Train models first');
        const sample = { qber: Math.random() * 20, sifted_count: 120, errors_corrected: 5, final_key_length: 100 };
        const res = await fetch('/api/ml/predict_attack', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(sample) });
        const data = await res.json();
        document.getElementById('anomalyResult').innerHTML = `Prediction: <strong>${data.prediction}</strong> (Conf: ${data.confidence})`;
        const gc = QState.chartInstances.anomalyGauge;
        if (gc) { gc.data.datasets[0].data = data.prediction === 'attack' ? [20, 80] : [80, 20]; gc.update(); }
    });
    document.getElementById('incrementalLearnBtn')?.addEventListener('click', async () => {
        const sample = { qber: Math.random() * 20, sifted_count: 120, errors_corrected: 5, final_key_length: 100, label: Math.random() > 0.5 ? 1 : 0 };
        const res = await fetch('/api/ml/partial_train', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(sample) });
        const data = await res.json();
        document.getElementById('mlStatus').innerHTML = '<span style="color:#10b981;">✅ ' + data.message + '</span>';
    });

    // ===================== KEY RATE FORECAST =====================
    document.getElementById('forecastBtn')?.addEventListener('click', async () => {
        if (!window.QState.mlTrained) return alert('Train models first');
        const res = await fetch('/api/ml/forecast');
        const data = await res.json();
        document.getElementById('forecastResult').innerHTML = `<div class="terminal-success">📈 Forecast</div>Mean SKR: ${data.summary?.mean_skr} bps<br>Next 3: ${(data.forecast?.forecast || []).join(', ')} bps`;
        const fc = QState.chartInstances.forecastChart;
        if (fc && data.forecast?.forecast) {
            fc.data.labels = ['R-2', 'R-1', 'Now', '+1', '+2', '+3'];
            fc.data.datasets[0].data = [4800, 4900, 4950, ...data.forecast.forecast];
            fc.update();
        }
    });

    // ===================== AUDIT TRAIL =====================
    document.getElementById('refreshAuditBtn')?.addEventListener('click', async () => {
        const res = await fetch('/api/audit/logs');
        const data = await res.json();
        let html = `<div><strong>Chain Valid:</strong> ${data.chain_valid ? '✅' : '❌'} · ${data.chain_length} blocks</div>`;
        (data.events || []).forEach(e => html += `<div class="small">#${e.index} ${new Date(e.timestamp * 1000).toLocaleString()} — ${e.hash?.slice(0, 12)}</div>`);
        document.getElementById('auditResult').innerHTML = html;

        const bcDiv = document.getElementById('blockchainViz');
        if (!bcDiv) return;
        const bw = bcDiv.clientWidth || 400, bh = 320;
        d3.select('#blockchainViz').selectAll('*').remove();
        const bsvg = d3.select('#blockchainViz').append('svg').attr('width', bw).attr('height', bh);
        const count = Math.min(data.chain_length || 1, 8);
        for (let i = 0; i < count; i++) {
            const bx = 60 + i * 90, by = bh / 2;
            bsvg.append('rect').attr('x', bx).attr('y', by - 25).attr('width', 70).attr('height', 50).attr('rx', 8)
                .attr('fill', i === count - 1 ? 'rgba(16,185,129,0.2)' : 'rgba(139,92,246,0.15)')
                .attr('stroke', i === count - 1 ? '#10b981' : '#8b5cf6').attr('stroke-width', 1.5);
            bsvg.append('text').attr('x', bx + 35).attr('y', by - 8).text(`#${i}`).attr('fill', '#e2e8f0').attr('text-anchor', 'middle').attr('font-size', '10px');
            bsvg.append('text').attr('x', bx + 35).attr('y', by + 8).text(data.chain_valid ? '✓' : '?').attr('fill', '#10b981').attr('text-anchor', 'middle').attr('font-size', '14px');
            if (i < count - 1) bsvg.append('line').attr('x1', bx + 70).attr('y1', by).attr('x2', bx + 90).attr('y2', by)
                .attr('stroke', 'rgba(255,255,255,0.15)').attr('stroke-width', 2);
        }
    });

    // ===================== BENCHMARK =====================
    document.getElementById('runBenchmarkBtn')?.addEventListener('click', async () => {
        const res = await fetch('/api/benchmark/run', { method: 'POST' });
        const data = await res.json();
        let html = '<div class="terminal-success">⚡ Benchmark Complete</div>';
        (data.results || []).forEach(r => html += `<div><strong>${r.algorithm}</strong>: ${r.time_seconds}s, Q‑Safe: ${r.quantum_vulnerable ? '❌' : '✅'}</div>`);
        document.getElementById('benchmarkResult').innerHTML = html;
        const bc = QState.chartInstances.benchmarkChart;
        if (bc && data.results) { bc.data.datasets[0].data = data.results.map(r => r.time_seconds || 0); bc.update(); }
    });

    // ===================== EXPERIMENT LAB (with decoy‑state) =====================
    document.getElementById('runExperimentBtn')?.addEventListener('click', async () => {
        const useDecoy = document.getElementById('expDecoy')?.value === 'on';
        const payload = {
            num_bits: +document.getElementById('expQubits').value || 256,
            eavesdropper: document.getElementById('expEveToggle')?.checked || false,
            attack_type: document.getElementById('expAttack')?.value || 'intercept_resend',
            eve_intercept_prob: 0.3,
            noise_model: 'none',
            decoy_state: useDecoy
        };
        const res = await fetch('/generate_keys', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        const data = await res.json();
        if (data.status === 'success') {
            document.getElementById('experimentResult').innerHTML = `<div class="terminal-success">🧪 Complete</div>QBER: ${data.qber_percent}%${useDecoy ? ' (decoy)' : ''}`;
            updateAllGauges(data.qber_percent);
        } else {
            document.getElementById('experimentResult').innerHTML = `<div class="terminal-error">${data.message}</div>`;
        }
    });

    console.log('%c🛡️ Q‑SHIELD %cCinematic Edition Ready', 'color:#a78bfa;font-weight:bold;', 'color:#94a3b8;');
});