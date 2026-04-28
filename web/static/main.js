/* ══════════════════════════════════════════════════════
   Phoenix AI SDK — Global JavaScript
   Extracted from base.html and home.html
   ══════════════════════════════════════════════════════ */

/* ── Theme & Mermaid ────────────────────────────────── */
const html      = document.documentElement;
const themeIcon = document.getElementById('themeIcon');

const cacheMermaidSources = () => {
    document.querySelectorAll('pre.mermaid').forEach(el => {
        if (!el.dataset.src) el.dataset.src = el.textContent.trim();
    });
};

const applyTheme = (theme) => {
    html.setAttribute('data-bs-theme', theme);
    localStorage.setItem('phoenix-theme-v2', theme);
    themeIcon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
    const mTheme = theme === 'dark' ? 'dark' : 'default';
    mermaid.initialize({ startOnLoad: false, theme: mTheme, securityLevel: 'loose' });
    document.querySelectorAll('pre.mermaid').forEach(el => {
        if (el.dataset.src) { el.innerHTML = el.dataset.src; el.removeAttribute('data-processed'); }
    });
    mermaid.run({ querySelector: 'pre.mermaid' });
};

/* ── Copy Buttons ───────────────────────────────────── */
const initCopyButtons = () => {
    document.querySelectorAll('pre:not(.mermaid)').forEach(pre => {
        const wrapper = document.createElement('div');
        wrapper.className = 'pre-wrapper';
        pre.parentNode.insertBefore(wrapper, pre);
        wrapper.appendChild(pre);

        const button = document.createElement('button');
        button.className = 'copy-btn';
        button.innerHTML = '<i class="bi bi-clipboard"></i>';
        wrapper.appendChild(button);

        button.addEventListener('click', () => {
            const code = pre.querySelector('code') || pre;
            navigator.clipboard.writeText(code.textContent.trim()).then(() => {
                button.innerHTML = '<i class="bi bi-check2"></i>';
                button.classList.add('copied');
                setTimeout(() => {
                    button.innerHTML = '<i class="bi bi-clipboard"></i>';
                    button.classList.remove('copied');
                }, 2000);
            });
        });
    });
};

/* ── DOMContentLoaded Bootstrap ─────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
    cacheMermaidSources();
    hljs.highlightAll();
    initCopyButtons();
    const saved = localStorage.getItem('phoenix-theme-v2') || 'dark';
    applyTheme(saved);
});

document.getElementById('themeToggle').addEventListener('click', () => {
    applyTheme(html.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark');
});

/* ══════════════════════════════════════════════════════
   Home Page — Network Canvas Animation
   ══════════════════════════════════════════════════════ */
(function initNetworkCanvas() {
    const canvas = document.getElementById('networkCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let particles = [];
    let stars = [];
    const particleCount = 24; // Fewer, more distinct "planets"
    const starCount = 100;    // Background stars
    const mouse = { x: null, y: null, radius: 200 };
    let centerX, centerY;

    window.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        mouse.x = e.clientX - rect.left;
        mouse.y = e.clientY - rect.top;
    });

    window.addEventListener('mouseout', () => { mouse.x = null; mouse.y = null; });
    window.addEventListener('resize', () => resizeCanvas());

    function resizeCanvas() {
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        
        // Center orbits around the logo image
        const logo = document.querySelector('.hero-logo-img');
        if (logo) {
            const logoRect = logo.getBoundingClientRect();
            const canvasRect = canvas.getBoundingClientRect();
            centerX = (logoRect.left + logoRect.width / 2) - canvasRect.left;
            centerY = (logoRect.top + logoRect.height / 2) - canvasRect.top;
        } else {
            centerX = canvas.width / 2;
            centerY = canvas.height / 2;
        }
        
        initCelestialBodies();
    }

    class Star {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 1.2;
            this.opacity = Math.random();
            this.blinkSpeed = 0.005 + Math.random() * 0.015;
        }
        draw() {
            this.opacity += this.blinkSpeed;
            if (this.opacity > 1 || this.opacity < 0.2) this.blinkSpeed *= -1;
            ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    class Planet {
        constructor(index) {
            this.init(index);
        }

        init(index) {
            const minDim = Math.min(canvas.width, canvas.height);
            // Evenly spaced orbits
            this.orbitRadius = 100 + (index * (minDim / 2.5 / particleCount)) + (Math.random() * 20);
            this.angle = Math.random() * Math.PI * 2;
            
            // Kepler's law simplification: closer is faster
            this.orbitSpeed = (0.015 / Math.sqrt(this.orbitRadius)) * (Math.random() > 0.5 ? 1 : -0.8);
            
            this.size = 1 + Math.random() * 4;
            const colors = [
                '#FF4D00', '#FF8A00', '#FFB400', '#FFD700', '#E6E6FA', '#87CEEB'
            ];
            this.color = colors[Math.floor(Math.random() * colors.length)];
            
            this.driftX = 0;
            this.driftY = 0;
            this.hasRing = Math.random() > 0.8;
            this.updateCoords();
        }

        updateCoords() {
            this.x = centerX + Math.cos(this.angle) * this.orbitRadius + this.driftX;
            this.y = centerY + Math.sin(this.angle) * this.orbitRadius + this.driftY;
        }

        update() {
            this.angle += this.orbitSpeed;

            if (mouse.x != null && mouse.y != null) {
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < mouse.radius) {
                    const force = (mouse.radius - dist) / mouse.radius;
                    this.driftX -= dx * force * 0.04;
                    this.driftY -= dy * force * 0.04;
                }
            }
            this.driftX *= 0.96;
            this.driftY *= 0.96;
            this.updateCoords();
        }

        draw() {
            // Draw Orbit Ring
            ctx.strokeStyle = 'rgba(255, 77, 0, 0.04)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.arc(centerX, centerY, this.orbitRadius, 0, Math.PI * 2);
            ctx.stroke();

            // Planet Glow
            ctx.shadowBlur = this.size * 2;
            ctx.shadowColor = this.color;
            
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            
            // Planet Ring (like Saturn)
            if (this.hasRing) {
                ctx.strokeStyle = `rgba(255, 255, 255, 0.2)`;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.ellipse(this.x, this.y, this.size * 2.2, this.size * 0.8, this.angle, 0, Math.PI * 2);
                ctx.stroke();
            }
            
            ctx.shadowBlur = 0;
        }
    }

    function initCelestialBodies() {
        particles = [];
        stars = [];
        for (let i = 0; i < starCount; i++) stars.push(new Star());
        for (let i = 0; i < particleCount; i++) particles.push(new Planet(i));
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Dynamic center tracking (in case of layout shifts)
        const logo = document.querySelector('.hero-logo-img');
        if (logo) {
            const logoRect = logo.getBoundingClientRect();
            const canvasRect = canvas.getBoundingClientRect();
            centerX = (logoRect.left + logoRect.width / 2) - canvasRect.left;
            centerY = (logoRect.top + logoRect.height / 2) - canvasRect.top;
        }

        // Draw Stars
        stars.forEach(s => s.draw());

        // Update and Draw Planets
        particles.forEach(p => {
            p.update();
            p.draw();
        });

        // Dynamic Connections (Constellations)
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 120) {
                    const opacity = 0.15 * (1 - distance / 120);
                    ctx.strokeStyle = `rgba(255, 138, 0, ${opacity})`;
                    ctx.lineWidth = 0.5;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animate);
    }

    resizeCanvas();
    animate();
})();

/* ── Terminal Copy ───────────────────────────────────── */
(function initTerminalCopy() {
    const terminalCopyBtn = document.querySelector('.terminal-copy-btn');
    if (!terminalCopyBtn) return;

    terminalCopyBtn.addEventListener('click', () => {
        const cmd  = document.querySelector('#terminalCmdBlock .cmd').textContent;
        navigator.clipboard.writeText(cmd).then(() => {
            const icon = document.getElementById('terminalCopyIcon');
            icon.classList.replace('bi-clipboard', 'bi-check2');
            terminalCopyBtn.classList.add('text-success');
            setTimeout(() => {
                icon.classList.replace('bi-check2', 'bi-clipboard');
                terminalCopyBtn.classList.remove('text-success');
            }, 2000);
        });
    });
})();

/* ── Feature Card Modals ─────────────────────────────── */
function openCardModal(modalId) {
    const modalEl = document.getElementById(modalId);
    if (!modalEl || typeof bootstrap === 'undefined') return;
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
    modalEl.addEventListener('shown.bs.modal', function onShown() {
        modalEl.querySelectorAll('pre code').forEach(block => {
            if (typeof hljs !== 'undefined') hljs.highlightElement(block);
        });
        modalEl.removeEventListener('shown.bs.modal', onShown);
    }, { once: true });
}

window.openCardModal = openCardModal;

/* ══════════════════════════════════════════════════════
   Docs Page — TOC & Sidebar Logic
   ══════════════════════════════════════════════════════ */
(function initDocsLogic() {
    document.addEventListener('DOMContentLoaded', () => {
        const tocContainer = document.getElementById('toc-container');
        if (!tocContainer) return;

        const headings = document.querySelectorAll('.docs-body h2, .docs-body h3');
        
        // Style and add collapse logic to the auto-generated TOC
        const tocUl = tocContainer.querySelector('ul');
        if (tocUl) {
            tocUl.classList.add('list-unstyled', 'ms-0');
            
            // Add toggle buttons for parents
            tocContainer.querySelectorAll('li').forEach(li => {
                const subUl = li.querySelector('ul');
                if (subUl) {
                    li.classList.add('has-children');
                    const toggle = document.createElement('span');
                    toggle.className = 'toc-toggle';
                    toggle.innerHTML = '<i class="bi bi-chevron-right"></i>';
                    li.insertBefore(toggle, li.firstChild);

                    toggle.addEventListener('click', (e) => {
                        e.preventDefault();
                        li.classList.toggle('expanded');
                    });
                    
                    // Auto-expand if active child
                    if (li.querySelector('a.is-active')) {
                        li.classList.add('expanded');
                    }
                }
            });

            tocContainer.querySelectorAll('a').forEach(a => {
                a.classList.add('sidebar-link');
            });
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(e => {
                if (e.isIntersecting) {
                    const id = e.target.id;
                    const link = tocContainer.querySelector(`a[href="#${id}"]`);
                    if (link) {
                        tocContainer.querySelectorAll('a').forEach(l => l.classList.remove('is-active'));
                        link.classList.add('is-active');
                        
                        // Ensure parent is expanded
                        let parent = link.closest('li.has-children');
                        while (parent) {
                            parent.classList.add('expanded');
                            parent = parent.parentElement.closest('li.has-children');
                        }
                    }
                }
            });
        }, { rootMargin: '-20% 0px -70% 0px' });

        headings.forEach(h => observer.observe(h));

        // Sidebar Toggle Logic (Universal)
        const sidebarCol = document.getElementById('sidebarColumn');
        const toggles = ['sidebarToggleMobile', 'sidebarToggleDesktop'];
        
        toggles.forEach(id => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.addEventListener('click', () => {
                    if (sidebarCol) sidebarCol.classList.toggle('active');
                    if (id === 'sidebarToggleMobile') {
                        const icon = btn.querySelector('i');
                        if (icon) {
                            icon.classList.toggle('bi-list');
                            icon.classList.toggle('bi-x-lg');
                        }
                    }
                });
            }
        });
    });
})();
