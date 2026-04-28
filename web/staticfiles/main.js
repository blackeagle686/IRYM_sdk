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
    if (!canvas) return; // only runs on the home page

    const ctx = canvas.getContext('2d');
    let particles = [];
    const particleCount      = 140;
    const connectionDistance = 140;
    const mouse = { x: null, y: null, radius: 150 };

    window.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        mouse.x = e.clientX - rect.left;
        mouse.y = e.clientY - rect.top;
    });

    window.addEventListener('mouseout', () => {
        mouse.x = null;
        mouse.y = null;
    });

    window.addEventListener('resize', () => resizeCanvas());

    function resizeCanvas() {
        canvas.width  = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        initParticles();
    }

    class Particle {
        constructor() {
            this.x      = Math.random() * canvas.width;
            this.y      = Math.random() * canvas.height;
            this.size   = Math.random() * 1.5 + 0.5;
            this.speedX = (Math.random() - 0.5) * 0.4;
            this.speedY = (Math.random() - 0.5) * 0.4;
            const colors = [
                'rgba(255, 77, 0, 0.8)',
                'rgba(255, 138, 0, 0.7)',
                'rgba(255, 180, 0, 0.6)'
            ];
            this.color = colors[Math.floor(Math.random() * colors.length)];
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            if (this.x > canvas.width)  this.x = 0;
            if (this.x < 0)             this.x = canvas.width;
            if (this.y > canvas.height) this.y = 0;
            if (this.y < 0)             this.y = canvas.height;

            if (mouse.x != null && mouse.y != null) {
                const dx       = mouse.x - this.x;
                const dy       = mouse.y - this.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < mouse.radius) {
                    const force = (mouse.radius - distance) / mouse.radius;
                    this.x += dx * force * 0.03;
                    this.y += dy * force * 0.03;
                }
            }
        }

        draw() {
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function initParticles() {
        particles = [];
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();

            for (let j = i; j < particles.length; j++) {
                const dx       = particles[i].x - particles[j].x;
                const dy       = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < connectionDistance) {
                    ctx.strokeStyle = `rgba(255, 138, 0, ${0.4 * (1 - distance / connectionDistance)})`;
                    ctx.lineWidth   = 0.8;
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
