document.addEventListener('DOMContentLoaded', () => {
    
    // Tab Switching Logic for Input Page
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    if (tabBtns && tabBtns.length > 0) {
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active', 'btn-primary'));
                tabBtns.forEach(b => b.classList.add('btn-outline'));
                
                btn.classList.add('active', 'btn-primary');
                btn.classList.remove('btn-outline');
                
                const target = btn.getAttribute('data-target');
                tabPanes.forEach(pane => {
                    if (pane && pane.id === target) {
                        pane.classList.remove('hidden');
                    } else if (pane) {
                        pane.classList.add('hidden');
                    }
                });
            });
        });
    }

    // Form Submission Logic
    const analyzeForm = document.getElementById('analyzeForm');
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const activeTabBtn = document.querySelector('.tab-btn.active');
            if (!activeTabBtn) return;

            const activeTab = activeTabBtn.getAttribute('data-target');
            let data = {};
            
            const newsTextArea = document.getElementById('newsText');
            const newsUrlInput = document.getElementById('newsUrl');

            if (activeTab === 'text-input' && newsTextArea) {
                data.text = newsTextArea.value;
            } else if (newsUrlInput) {
                data.url = newsUrlInput.value;
            }
            
            const loadingSec = document.getElementById('loadingSection');
            const resultSec = document.getElementById('resultSection');
            const errorMsg = document.getElementById('errorMessage');
            
            if (errorMsg) errorMsg.classList.add('hidden');
            if (resultSec) resultSec.classList.add('hidden');
            if (loadingSec) loadingSec.classList.remove('hidden');
            
            try {
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (!response.ok) {
                    throw new Error(result.error || 'Server error occurred');
                }
                
                // Populate Results (with defensive null-checks)
                const badge = document.getElementById('resultBadge');
                const confText = document.getElementById('confidenceText');
                const pBar = document.getElementById('progressBar');
                const hlBox = document.getElementById('highlightBox');
                const exportBtn = document.getElementById('exportBtn');
                const reasoningText = document.getElementById('reasoningText');
                const sourcesSec = document.getElementById('sourcesSection');
                const sourcesList = document.getElementById('sourcesList');
                const queryStrategy = document.getElementById('queryStrategy');
                const optimizedQueryText = document.getElementById('optimizedQueryText');
                
                if (queryStrategy) {
                    if (result.optimized_query) {
                        if (optimizedQueryText) optimizedQueryText.textContent = result.optimized_query;
                        queryStrategy.style.display = 'block';
                    } else {
                        queryStrategy.style.display = 'none';
                    }
                }

                if (badge) {
                    badge.textContent = result.prediction.toUpperCase();
                    badge.className = 'result-badge ' + (result.prediction === 'Real' ? 'badge-real' : 'badge-fake');
                }
                
                if (confText) confText.textContent = `${result.confidence}%`;
                
                // Animate progress bar
                if (pBar) {
                    pBar.style.width = '0%';
                    pBar.className = 'progress-bar ' + (result.prediction === 'Real' ? 'progress-real' : 'progress-fake');
                    setTimeout(() => { pBar.style.width = `${result.confidence}%`; }, 100);
                }
                
                if (hlBox) hlBox.innerHTML = result.highlighted_text || 'No text processed.';
                if (reasoningText) reasoningText.textContent = result.reasoning || "No detailed reasoning provided.";
                
                // Render Sources
                if (sourcesList) {
                    sourcesList.innerHTML = '';
                    if (result.sources && result.sources.length > 0) {
                        result.sources.forEach(src => {
                            const link = document.createElement('a');
                            link.href = src.link;
                            link.target = '_blank';
                            link.className = 'btn btn-outline';
                            link.style.display = 'block';
                            link.style.textAlign = 'left';
                            link.style.fontSize = '0.9rem';
                            link.style.padding = '0.5rem 1rem';
                            link.innerHTML = `🌐 <strong>${src.title}</strong><br><small style="color: var(--text-secondary); opacity: 0.8;">${src.link.substring(0, 70)}...</small>`;
                            sourcesList.appendChild(link);
                        });
                        if (sourcesSec) sourcesSec.classList.remove('hidden');
                    } else {
                        if (sourcesSec) sourcesSec.classList.add('hidden');
                    }
                }
                
                if (exportBtn && result.prediction_id) {
                    exportBtn.href = `/export/${result.prediction_id}`;
                    exportBtn.classList.remove('hidden');
                }
                
                if (loadingSec) loadingSec.classList.add('hidden');
                if (resultSec) {
                    resultSec.classList.remove('hidden');
                    resultSec.scrollIntoView({ behavior: 'smooth' });
                }
                
            } catch (err) {
                if (loadingSec) loadingSec.classList.add('hidden');
                if (errorMsg) {
                    errorMsg.textContent = err.message;
                    errorMsg.classList.remove('hidden');
                }
            }
        });
    }
});
