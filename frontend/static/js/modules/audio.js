import { activityFeed } from './feed.js';

export function playAudio(text) {
    if (!text) {
        const activePane = document.querySelector('.intel-pane.active');
        if (activePane) {
            const titles = Array.from(
                activePane.querySelectorAll('.news-title,.ti-title,.sched-name')
            ).map(el => el.textContent).join('. ');
            if (titles) text = `Summarizing ${activePane.id.replace('pane-','')}: ${titles}`;
        }
    }
    if (!text) return;
    window.speechSynthesis.cancel();
    const utt  = new SpeechSynthesisUtterance(text);
    utt.rate   = 1.0;
    utt.pitch  = 1.0;
    window.speechSynthesis.speak(utt);
    activityFeed.log(`🔊 Speaking: "${text.substring(0,50)}…"`, 'status', 'AUDIO');
}

export function toggleVoiceInput() {
    const btn = document.getElementById('nl-mic-btn');
    if (!btn) return;
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;
    const rec    = new SR();
    rec.lang     = 'en-US';
    rec.onstart  = () => { btn.classList.add('active');    btn.innerHTML = '<span class="ms sm fa-spin">graphic_eq</span>'; };
    rec.onresult = e  => { window.setGoal(e.results[0][0].transcript); };
    rec.onend    = () => { btn.classList.remove('active'); btn.innerHTML = '<span class="ms sm">mic</span>'; };
    rec.start();
}

window.playAudio        = playAudio;
window.toggleVoiceInput = toggleVoiceInput;
