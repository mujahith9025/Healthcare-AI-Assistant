// Frontend Chat Controller with Multi-Turn History, Guided Symptom Triage, RAG Grounding, Medication Guard, and Uncertainty Calibration

const chatHistory = document.getElementById('chat-history');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const regionSelect = document.getElementById('region-select');
const disclaimerModal = document.getElementById('disclaimer-modal');
const ackCheckbox = document.getElementById('ack-checkbox');
const modalAgreeBtn = document.getElementById('modal-agree-btn');
const footerEmergencyNote = document.getElementById('footer-emergency-note');

// Triage Modal Elements
const triageModal = document.getElementById('triage-modal');
const triageBody = document.getElementById('triage-body');
const triageStepIndicator = document.getElementById('triage-step-indicator');
const triageProgressFill = document.getElementById('triage-progress-fill');
const triagePrevBtn = document.getElementById('triage-prev-btn');
const triageNextBtn = document.getElementById('triage-next-btn');

// In-memory conversation history
let conversationHistory = [];

// Regional emergency phone numbers for footer text & sidebar widgets
const REGION_FOOTER_HOTLINES = {
    'US': 'In severe emergencies, call 911 (or 988 for crisis support) immediately.',
    'UK': 'In severe emergencies, call 999 (or 111 for NHS urgent care) immediately.',
    'IN': 'In severe emergencies, call 112 / 108 (or 14416 for Tele-MANAS) immediately.',
    'CA': 'In severe emergencies, call 911 (or 988 for crisis helpline) immediately.',
    'GLOBAL': 'In severe emergencies, call 112 / 911 or visit an emergency room immediately.'
};

const REGION_SIDEBAR_HOTLINES = {
    'US': { primary: '911', crisis: '988', label: 'US (911/988)' },
    'UK': { primary: '999', crisis: '111', label: 'UK (999/111)' },
    'IN': { primary: '112 / 108', crisis: '14416', label: 'IN (112/108)' },
    'CA': { primary: '911', crisis: '988', label: 'CA (911/988)' },
    'GLOBAL': { primary: '112 / 911', crisis: 'Local ER', label: 'GLOBAL' }
};

// Default fallback triage options in case network fetch delays
let TRIAGE_CONFIG = {
    categories: [
        { id: "respiratory", name: "🫁 Respiratory & Breathing", desc: "Cough, congestion, sore throat, wheezing" },
        { id: "neurological", name: "🧠 Head & Neurological", desc: "Headache, migraine, dizziness, lightheadedness" },
        { id: "gastrointestinal", name: "🥣 Digestive & Stomach", desc: "Nausea, acidity, cramps, diarrhea, vomiting" },
        { id: "fever_infection", name: "🌡️ Fever & General Infection", desc: "Body aches, chills, fatigue, sweating" },
        { id: "dermatology", name: "🧴 Skin, Rash & Eyes", desc: "Itching, redness, rash, hives, eye irritation" },
        { id: "musculoskeletal", name: "🦴 Muscles & Joints", desc: "Back pain, joint stiffness, sprains, soreness" },
        { id: "general", name: "🌿 General Wellness & Other", desc: "Sleep issues, mild fatigue, general malaise" }
    ],
    durations: [
        { id: "under_24h", label: "Less than 24 hours", desc: "Brand new or sudden onset" },
        { id: "1_to_3_days", label: "1 to 3 days", desc: "Active short-term symptoms" },
        { id: "4_to_7_days", label: "4 to 7 days", desc: "Lingering almost a week" },
        { id: "over_1_week", label: "1 to 2 weeks", desc: "Persistent without clear recovery" },
        { id: "chronic", label: "More than 2 weeks / Recurring", desc: "Ongoing, chronic, or repeated flare-ups" }
    ],
    severities: [
        { id: "mild", label: "🟢 Mild (Manageable)", desc: "Noticeable but does not disrupt work, school, or sleep" },
        { id: "moderate", label: "🟡 Moderate (Disruptive)", desc: "Limits daily activities; resting or taking frequent breaks" },
        { id: "severe", label: "🔴 Severe (Debilitating)", desc: "Intense distress; unable to perform routine activities" }
    ],
    red_flags: [
        { id: "breathing_difficulty", label: "Severe shortness of breath or struggling to speak in full sentences" },
        { id: "chest_pain", label: "Pressure, squeezing, or crushing pain in the chest or radiating to jaw/arm" },
        { id: "confusion_stroke", label: "Sudden confusion, facial drooping, one-sided weakness, or slurred speech" },
        { id: "stiff_neck_fever", label: "High fever combined with severe neck stiffness and sensitivity to light" },
        { id: "dehydration_vomiting", label: "Inability to keep any fluids down for >24 hours with extreme dizziness" },
        { id: "severe_bleeding", label: "Uncontrolled bleeding or coughing/vomiting blood" }
    ],
    category_specific_questions: {
        respiratory: [
            "Barking or wheezing cough",
            "Discolored thick mucus or phlegm",
            "History of asthma or allergies",
            "Chest tightness with deep breaths"
        ],
        neurological: [
            "Throbbing pain on one side of head",
            "Nausea or sensitivity to light/sound",
            "Visual aura (flashing lights / blind spots)",
            "Tension or stiffness across forehead/scalp"
        ],
        gastrointestinal: [
            "Burning sensation behind breastbone (acid reflux)",
            "Frequent watery stools or cramping",
            "Stomach ache shortly after meals",
            "Bloating and excessive gas"
        ],
        fever_infection: [
            "Temperature exceeding 102°F (38.9°C)",
            "Intense body or muscle aches",
            "Swollen lymph nodes in neck or armpits",
            "Shivering or heavy night sweats"
        ],
        dermatology: [
            "Spreading red or itchy patches",
            "Raised hives or allergic welts",
            "Flaking, peeling, or cracked dry skin",
            "Eye redness, itching, or discharge"
        ],
        musculoskeletal: [
            "Joint swelling or warm to the touch",
            "Pain sharpens upon movement or weight-bearing",
            "Morning stiffness lasting over 30 minutes",
            "Recent physical strain, lift, or exercise"
        ],
        general: [
            "Trouble falling or staying asleep",
            "Unexplained daytime fatigue",
            "Brain fog or difficulty concentrating",
            "Mild dehydration or dry mouth"
        ]
    }
};

// Triage state
let currentTriageStep = 1;
let triageAnswers = {
    category: "respiratory",
    duration: "1_to_3_days",
    severity: "mild",
    red_flags: [],
    accompanying: []
};

// 1. Initialize Disclaimer Modal, Region, Sidebar, and Fetch Triage Options on Load
document.addEventListener('DOMContentLoaded', () => {
    const hasAccepted = localStorage.getItem('health_disclaimer_accepted_v1');
    if (!hasAccepted) {
        disclaimerModal.classList.remove('hidden');
    } else {
        disclaimerModal.classList.add('hidden');
    }

    const savedRegion = localStorage.getItem('health_assistant_region') || 'US';
    if (regionSelect) {
        regionSelect.value = savedRegion;
        updateFooterHotline(savedRegion);
    }

    // Restore desktop sidebar collapsed preference if saved
    const isSidebarCollapsed = localStorage.getItem('health_sidebar_collapsed') === 'true';
    const appLayout = document.getElementById('app-layout');
    if (appLayout && isSidebarCollapsed && window.innerWidth > 1023) {
        appLayout.classList.add('sidebar-collapsed');
    }

    // Prefetch triage steps
    fetch('/triage/options')
        .then(res => res.json())
        .then(data => {
            if (data && data.categories) {
                TRIAGE_CONFIG = data;
            }
        })
        .catch(err => console.log('Using built-in triage steps config:', err));
});

/**
 * Sidebar Collapse / Expand Controller (Desktop toggle & Mobile Drawer)
 */
function toggleSidebar(forceState) {
    const appLayout = document.getElementById('app-layout');
    if (!appLayout) return;

    const isMobile = window.innerWidth <= 1023;
    if (isMobile) {
        if (typeof forceState === 'boolean') {
            if (forceState) {
                appLayout.classList.add('sidebar-mobile-open');
            } else {
                appLayout.classList.remove('sidebar-mobile-open');
            }
        } else {
            appLayout.classList.toggle('sidebar-mobile-open');
        }
    } else {
        // Desktop collapse toggle
        if (typeof forceState === 'boolean') {
            if (forceState) {
                appLayout.classList.remove('sidebar-collapsed');
            } else {
                appLayout.classList.add('sidebar-collapsed');
            }
        } else {
            appLayout.classList.toggle('sidebar-collapsed');
        }
        localStorage.setItem('health_sidebar_collapsed', appLayout.classList.contains('sidebar-collapsed'));
    }
}

/**
 * Disclaimer Modal Functions
 */
function toggleAckButton() {
    modalAgreeBtn.disabled = !ackCheckbox.checked;
}

function acceptDisclaimer() {
    if (!ackCheckbox.checked) return;
    localStorage.setItem('health_disclaimer_accepted_v1', 'true');
    disclaimerModal.classList.add('hidden');
    userInput.focus();
}

/**
 * Region Selector
 */
function changeRegion(newRegion) {
    localStorage.setItem('health_assistant_region', newRegion);
    updateFooterHotline(newRegion);
}

function updateFooterHotline(region) {
    if (footerEmergencyNote && REGION_FOOTER_HOTLINES[region]) {
        footerEmergencyNote.textContent = REGION_FOOTER_HOTLINES[region];
    }
    const info = REGION_SIDEBAR_HOTLINES[region] || REGION_SIDEBAR_HOTLINES['GLOBAL'];
    const pNum = document.getElementById('sidebar-primary-num');
    const cNum = document.getElementById('sidebar-crisis-num');
    const rLabel = document.getElementById('sidebar-region-label');
    if (pNum) pNum.textContent = info.primary;
    if (cNum) cNum.textContent = info.crisis;
    if (rLabel) rLabel.textContent = info.label;
}

/**
 * Reset / Start New Conversation
 */
function resetChat() {
    conversationHistory = [];
    chatHistory.innerHTML = `
        <div class="chat-history-inner">
            <div class="message-wrapper bot-wrapper">
                <div class="avatar bot-avatar" aria-hidden="true">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 2v20M2 12h20"/>
                    </svg>
                </div>
                <div class="message-bubble bot-bubble">
                    <p>Hello! I am your <strong>AI Healthcare Information Assistant</strong>. Ask me about common health symptoms, medications, lab ranges, nutrition plans, or clinical risk calculations.</p>
                    
                    <div class="welcome-triage-card">
                        <div class="welcome-triage-icon">🏥</div>
                        <div class="welcome-triage-info">
                            <strong>Explore our 4 Unified Health Hubs:</strong>
                            <span>Symptom Triage, Meds & Diet, Clinical Risk Calculators, and Calm Wellbeing.</span>
                        </div>
                        <div class="welcome-actions-row">
                            <button type="button" class="welcome-bodymap-action" onclick="openSymptomTriageHub('bodymap')">
                                🩺 Symptom Hub
                            </button>
                            <button type="button" class="welcome-triage-action" onclick="openMedsLabsDietHub('polypharmacy')">
                                💊 Meds & Diet
                            </button>
                            <button type="button" class="welcome-bodymap-action" onclick="openClinicalRiskHub('all')">
                                🧮 Risk & Vitals
                            </button>
                            <button type="button" class="welcome-triage-action" onclick="openCalmMentalHealthHub('somatic_pacers')">
                                🧠 Calm Hub
                            </button>
                        </div>
                    </div>

                    <p class="bubble-subtext">Or explore common health topics:</p>
                    
                    <div class="quick-prompts" id="quick-prompts">
                        <div class="chips-scroll-container">
                            <button class="prompt-chip" type="button" onclick="sendSuggested('What are symptoms of Common Cold?')">Common Cold</button>
                            <button class="prompt-chip" type="button" onclick="sendSuggested('How to manage Migraine headaches?')">Migraine Tips</button>
                            <button class="prompt-chip" type="button" onclick="sendSuggested('What foods are high in iron?')">Iron-rich Foods</button>
                            <button class="prompt-chip" type="button" onclick="sendSuggested('What are precautions for Diabetes?')">Diabetes Care</button>
                            <button class="prompt-chip" type="button" onclick="sendSuggested('What is healthy sleep hygiene?')">Sleep Tips</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    userInput.value = '';
    userInput.focus();
}

/**
 * Send suggested topic or handle special trigger chips
 */
function sendSuggested(promptText) {
    if (promptText === '🩺 Launch Guided Triage' || promptText === 'Start Guided Triage') {
        openTriageModal();
        return;
    }
    if (promptText.startsWith('🚑 Open') || promptText.includes('Emergency Flashcard') || promptText.includes('Flashcard') || promptText.includes('First-Aid Protocol')) {
        openFirstAidModal();
        return;
    }
    if (promptText.includes('CPR 110 BPM Metronome') || promptText.includes('Metronome')) {
        openFirstAidModal('cpr_adult');
        return;
    }
    if (promptText === '📄 Attach First-Aid Steps to Doctor Intake Summary') {
        if (window.currentFirstAidCard) {
            attachFirstAidToDoctorSummary();
            openExportModal();
        } else {
            openFirstAidModal();
        }
        return;
    }
    if (userInput.disabled) return;
    userInput.value = promptText;
    chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
}

/**
 * Handle form submission
 */
async function handleSend(event) {
    if (event) event.preventDefault();

    const message = userInput.value.trim();
    if (!message) return;

    // Check if user requested triage via chat
    if (/^(start triage|guided triage|check my symptoms|symptom triage|triage)$/i.test(message)) {
        userInput.value = '';
        openTriageModal();
        return;
    }

    // Check if user requested First-Aid via chat
    if (/^(first aid|first-aid|emergency action|cpr|choking first aid|emergency flashcards|flashcards|first aid flashcards)$/i.test(message)) {
        userInput.value = '';
        openFirstAidModal();
        return;
    }

    // Check if user requested Visual Body Map via chat
    if (/^(body map|visual body map|symptom locator|body locator|where does it hurt|bodymap|anatomy map)$/i.test(message)) {
        userInput.value = '';
        openBodyMapModal();
        return;
    }

    // Check if user requested PDF export via chat
    if (/^(export report|export pdf|download pdf|download report|doctor report|export for doctor|pdf report|export)$/i.test(message)) {
        userInput.value = '';
        openExportModal();
        return;
    }

    const selectedRegion = regionSelect ? regionSelect.value : 'GLOBAL';

    // 1. Display user message & save to history
    appendUserMessage(message);
    conversationHistory.push({ role: 'user', text: message });
    userInput.value = '';

    // 2. Set loading state & show typing indicator
    setLoadingState(true);
    const typingId = showTypingIndicator();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                region: selectedRegion,
                history: conversationHistory.slice(-8)
            })
        });

        // Remove typing indicator
        removeTypingIndicator(typingId);

        const data = await response.json();

        if (response.status === 429) {
            appendBotMessage(
                data.reply || "⏳ Please wait a moment before sending another message.",
                false,
                'rate-limit-bubble'
            );
            return;
        }

        if (!response.ok) {
            throw new Error(`Server returned status: ${response.status}`);
        }

        const replyText = data.reply || "I'm sorry, I couldn't generate a response. Please try again.";
        const isEmergency = data.is_emergency || data.source === 'emergency_filter' || replyText.includes('EMERGENCY');
        const isMedicationGuard = data.is_medication_guard || data.source === 'medication_guard';

        // Save bot reply to history
        conversationHistory.push({ role: 'assistant', text: replyText });

        // 3. Display bot reply with interactive cards, citations, suggestions, polypharmacy warnings, and lab badges
        let customClass = '';
        if (isMedicationGuard) customClass = 'medication-bubble';

        appendBotMessage(
            replyText,
            isEmergency,
            customClass,
            data.citations || [],
            data.suggestions || [],
            isMedicationGuard,
            false,
            data.polypharmacy_alerts || [],
            data.lab_interpretations || [],
            data
        );

    } catch (error) {
        console.error('Chat connection error:', error);
        removeTypingIndicator(typingId);
        appendBotMessage(
            "⚠️ Unable to reach the server. Please check your network connection and try again.",
            false,
            'error-bubble'
        );
    } finally {
        setLoadingState(false);
    }
}

/**
 * ============================================================================
 * UNIFIED HEALTH HUB 1: SYMPTOM & TRIAGE HUB CONTROLLER (Body Map + 5-Step Triage)
 * ============================================================================
 */

function openSymptomTriageHub(tab = 'bodymap') {
    const hub = document.getElementById('symptom-triage-hub-modal') || document.getElementById('triage-modal') || document.getElementById('body-map-modal');
    if (hub) {
        hub.classList.remove('hidden');
        switchSymptomTriageTab(tab);
    }
}

function closeSymptomTriageHub() {
    const hub = document.getElementById('symptom-triage-hub-modal') || document.getElementById('triage-modal') || document.getElementById('body-map-modal');
    if (hub) hub.classList.add('hidden');
}

function switchSymptomTriageTab(tab) {
    const tabBodymap = document.getElementById('st-tab-bodymap');
    const tabTriage = document.getElementById('st-tab-triage');
    const viewBodymap = document.getElementById('st-view-bodymap');
    const viewTriage = document.getElementById('st-view-triage');

    if (tab === 'bodymap') {
        if (tabBodymap) tabBodymap.classList.add('active');
        if (tabTriage) tabTriage.classList.remove('active');
        if (viewBodymap) {
            viewBodymap.style.display = 'block';
            viewBodymap.classList.add('active');
        }
        if (viewTriage) {
            viewTriage.style.display = 'none';
            viewTriage.classList.remove('active');
        }
        selectBodyRegion(currentBodyRegion || 'head');
    } else {
        if (tabTriage) tabTriage.classList.add('active');
        if (tabBodymap) tabBodymap.classList.remove('active');
        if (viewTriage) {
            viewTriage.style.display = 'block';
            viewTriage.classList.add('active');
        }
        if (viewBodymap) {
            viewBodymap.style.display = 'none';
            viewBodymap.classList.remove('active');
        }
        renderTriageStep(currentTriageStep || 1);
    }
}

function openTriageModal() {
    openSymptomTriageHub('triage');
}

function closeTriageModal() {
    closeSymptomTriageHub();
}

function renderTriageStep(step) {
    currentTriageStep = step;
    triageStepIndicator.textContent = `Step ${step} of 5`;
    triageProgressFill.style.width = `${step * 20}%`;

    // Manage Buttons
    triagePrevBtn.style.display = (step > 1) ? 'block' : 'none';
    triageNextBtn.textContent = (step === 5) ? 'Complete Assessment ➔' : 'Continue ➔';

    if (step === 1) {
        // Step 1: Category
        let cardsHtml = TRIAGE_CONFIG.categories.map(c => `
            <div class="triage-option-card ${triageAnswers.category === c.id ? 'selected' : ''}" onclick="selectTriageSingle('category', '${c.id}', this)">
                <div class="triage-option-content">
                    <span class="triage-option-title">${c.name}</span>
                    <span class="triage-option-desc">${c.desc}</span>
                </div>
                <div class="triage-option-radio"></div>
            </div>
        `).join('');

        triageBody.innerHTML = `
            <h3 class="triage-step-heading">What is your primary area of concern?</h3>
            <p class="triage-step-subheading">Select the category that best matches where you feel symptoms:</p>
            <div class="triage-options-grid">${cardsHtml}</div>
        `;

    } else if (step === 2) {
        // Step 2: Duration
        let cardsHtml = TRIAGE_CONFIG.durations.map(d => `
            <div class="triage-option-card ${triageAnswers.duration === d.id ? 'selected' : ''}" onclick="selectTriageSingle('duration', '${d.id}', this)">
                <div class="triage-option-content">
                    <span class="triage-option-title">${d.label}</span>
                    <span class="triage-option-desc">${d.desc}</span>
                </div>
                <div class="triage-option-radio"></div>
            </div>
        `).join('');

        triageBody.innerHTML = `
            <h3 class="triage-step-heading">How long have you experienced these symptoms?</h3>
            <p class="triage-step-subheading">Understanding the timeline helps evaluate whether this is acute or persistent:</p>
            <div class="triage-options-grid">${cardsHtml}</div>
        `;

    } else if (step === 3) {
        // Step 3: Severity
        let cardsHtml = TRIAGE_CONFIG.severities.map(s => `
            <div class="triage-option-card ${triageAnswers.severity === s.id ? 'selected' : ''}" onclick="selectTriageSingle('severity', '${s.id}', this)">
                <div class="triage-option-content">
                    <span class="triage-option-title">${s.label}</span>
                    <span class="triage-option-desc">${s.desc}</span>
                </div>
                <div class="triage-option-radio"></div>
            </div>
        `).join('');

        triageBody.innerHTML = `
            <h3 class="triage-step-heading">How severe are your symptoms right now?</h3>
            <p class="triage-step-subheading">Assess how significantly this impacts your daily routine:</p>
            <div class="triage-options-grid">${cardsHtml}</div>
        `;

    } else if (step === 4) {
        // Step 4: Red Flags Screening
        let checkboxesHtml = TRIAGE_CONFIG.red_flags.map(rf => {
            const isChecked = triageAnswers.red_flags.includes(rf.label);
            return `
                <div class="triage-checkbox-card red-flag-card ${isChecked ? 'selected' : ''}" onclick="toggleTriageCheckbox('red_flags', '${escapeHtml(rf.label).replace(/'/g, "\\'")}', this)">
                    <div class="triage-check-box">${isChecked ? '✓' : ''}</div>
                    <span class="triage-checkbox-text">${rf.label}</span>
                </div>
            `;
        }).join('');

        const warningDisplay = (triageAnswers.red_flags.length > 0) ? 'block' : 'none';

        triageBody.innerHTML = `
            <h3 class="triage-step-heading">🚨 Emergency & Red-Flag Screening</h3>
            <p class="triage-step-subheading">Select any critical symptoms you are currently experiencing (or leave unselected if none):</p>
            <div class="triage-warning-box" id="triage-redflag-alert" style="display: ${warningDisplay}; margin-bottom: 8px;">
                ⚠️ <strong>Urgent Note:</strong> If experiencing severe chest pain, breathing struggles, or sudden weakness, call emergency services immediately.
            </div>
            <div class="triage-options-grid">${checkboxesHtml}</div>
        `;

    } else if (step === 5) {
        // Step 5: Accompanying Category Questions
        const specificList = TRIAGE_CONFIG.category_specific_questions[triageAnswers.category] || TRIAGE_CONFIG.category_specific_questions["general"];
        
        let checkboxesHtml = specificList.map(item => {
            const isChecked = triageAnswers.accompanying.includes(item);
            return `
                <div class="triage-checkbox-card ${isChecked ? 'selected' : ''}" onclick="toggleTriageCheckbox('accompanying', '${escapeHtml(item).replace(/'/g, "\\'")}', this)">
                    <div class="triage-check-box">${isChecked ? '✓' : ''}</div>
                    <span class="triage-checkbox-text">${item}</span>
                </div>
            `;
        }).join('');

        triageBody.innerHTML = `
            <h3 class="triage-step-heading">Specific Accompanying Symptoms</h3>
            <p class="triage-step-subheading">Select any specific signs related to your primary concern (optional):</p>
            <div class="triage-options-grid">${checkboxesHtml}</div>
        `;
    }
}

function selectTriageSingle(field, value, el) {
    triageAnswers[field] = value;
    const parent = el.parentElement;
    parent.querySelectorAll('.triage-option-card').forEach(card => card.classList.remove('selected'));
    el.classList.add('selected');
}

function toggleTriageCheckbox(field, item, el) {
    const arr = triageAnswers[field];
    const index = arr.indexOf(item);
    if (index > -1) {
        arr.splice(index, 1);
        el.classList.remove('selected');
        el.querySelector('.triage-check-box').textContent = '';
    } else {
        arr.push(item);
        el.classList.add('selected');
        el.querySelector('.triage-check-box').textContent = '✓';
    }

    if (field === 'red_flags') {
        const alertBox = document.getElementById('triage-redflag-alert');
        if (alertBox) {
            alertBox.style.display = (arr.length > 0) ? 'block' : 'none';
        }
    }
}

function nextTriageStep() {
    if (currentTriageStep < 5) {
        renderTriageStep(currentTriageStep + 1);
    } else {
        submitTriageAssessment();
    }
}

function prevTriageStep() {
    if (currentTriageStep > 1) {
        renderTriageStep(currentTriageStep - 1);
    }
}

async function submitTriageAssessment() {
    closeTriageModal();

    const selectedRegion = regionSelect ? regionSelect.value : 'GLOBAL';
    const catName = (TRIAGE_CONFIG.categories.find(c => c.id === triageAnswers.category) || {}).name || "General Symptoms";

    // 1. Post user triage action message to chat
    appendUserMessage(`Completed Guided Symptom Triage for: ${catName}`);
    conversationHistory.push({ role: 'user', text: `Guided Symptom Triage completed for ${catName}` });

    // 2. Show typing indicator
    setLoadingState(true);
    const typingId = showTypingIndicator();

    try {
        const response = await fetch('/triage/evaluate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                category: triageAnswers.category,
                duration: triageAnswers.duration,
                severity: triageAnswers.severity,
                red_flags: triageAnswers.red_flags,
                accompanying: triageAnswers.accompanying,
                region: selectedRegion
            })
        });

        removeTypingIndicator(typingId);

        const data = await response.json();

        if (response.status === 429) {
            appendBotMessage(data.reply || "⏳ Rate limit reached. Please wait a moment.", false, 'rate-limit-bubble');
            return;
        }

        const replyText = data.reply || "Unable to complete triage assessment.";
        const isEmergency = Boolean(data.is_emergency);
        const customClass = data.level_class || '';

        conversationHistory.push({ role: 'assistant', text: replyText });

        appendBotMessage(
            replyText,
            isEmergency,
            customClass,
            data.citations || [],
            data.suggestions || [],
            false,
            true, // isTriageReport
            [],
            [],
            data
        );

    } catch (err) {
        console.error('Triage assessment error:', err);
        removeTypingIndicator(typingId);
        appendBotMessage("⚠️ Error evaluating triage responses. Please try again.", false, 'error-bubble');
    } finally {
        setLoadingState(false);
    }
}

/**
 * Copy triage assessment text to clipboard
 */
function copyTriageToClipboard(btn) {
    const bubble = btn.closest('.message-bubble');
    if (!bubble) return;

    // Get plain text of the bubble (ignoring buttons)
    const clone = bubble.cloneNode(true);
    const actions = clone.querySelector('.triage-action-row');
    if (actions) actions.remove();
    const cards = clone.querySelector('.interactive-chat-card');
    if (cards) cards.remove();
    const suggestions = clone.querySelector('.smart-suggestions');
    if (suggestions) suggestions.remove();
    const citations = clone.querySelector('.citations-container');
    if (citations) citations.remove();

    const textToCopy = clone.innerText.trim();

    navigator.clipboard.writeText(textToCopy).then(() => {
        const origText = btn.innerHTML;
        btn.innerHTML = `<span>✓ Copied to Clipboard</span>`;
        setTimeout(() => {
            btn.innerHTML = origText;
        }, 2000);
    }).catch(() => {
        alert('Could not copy to clipboard.');
    });
}

/**
 * Append user message bubble to chat history
 */
function appendUserMessage(text) {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper user-wrapper';

    const avatar = document.createElement('div');
    avatar.className = 'avatar user-avatar';
    avatar.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
        </svg>
    `;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble user-bubble';
    bubble.textContent = text;

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    chatHistory.appendChild(wrapper);

    scrollToBottom();
}

/**
 * Build Interactive Compact Visual Chat Card for quick actions, calculations, and modalities
 */
function buildInteractiveChatCard(data) {
    if (!data || typeof data !== 'object') return '';

    // 1. Clinical Risk Calculator Card
    if (data.is_calculator_intent || data.calculator_id || data.calculator_info) {
        const cinfo = data.calculator_info || {};
        const cid = data.calculator_id || 'ascvd_10yr';
        const title = cinfo.title || 'Clinical Risk Calculator';
        const icon = cinfo.icon || '🧮';
        const badge = cinfo.badge || 'Evidence-Based Tool';
        const desc = cinfo.description || 'Calculate patient-specific clinical risk scores, guideline staging, and treatment pathways.';

        return `
            <div class="interactive-chat-card icc-calculator">
                <div class="icc-header">
                    <div class="icc-icon-wrapper icc-icon-calc">${icon}</div>
                    <div class="icc-header-text">
                        <div class="icc-badge-row">
                            <span class="icc-badge icc-badge-blue">${escapeHtml(badge)}</span>
                            <span class="icc-sub-badge">Clinical Suite</span>
                        </div>
                        <h4 class="icc-title">${escapeHtml(title)}</h4>
                    </div>
                </div>
                <div class="icc-body">
                    <p class="icc-desc">${escapeHtml(desc)}</p>
                    <div class="icc-metrics-grid">
                        <div class="icc-metric-item">
                            <span class="icc-metric-label">Clinical Target</span>
                            <span class="icc-metric-value">Validated Scoring & Staging</span>
                        </div>
                        <div class="icc-metric-item">
                            <span class="icc-metric-label">Outputs</span>
                            <span class="icc-metric-value">Risk % • Clinical Actions • PDF Summary</span>
                        </div>
                    </div>
                </div>
                <div class="icc-actions">
                    <button type="button" class="icc-action-btn icc-btn-primary" onclick="openClinicalRiskHub('${cid}')">
                        🧮 Launch ${escapeHtml(title)}
                    </button>
                    <button type="button" class="icc-action-btn icc-btn-secondary" onclick="openClinicalRiskHub('all')">
                        📊 All Risk Calculators
                    </button>
                    <button type="button" class="icc-action-btn icc-btn-secondary" onclick="openExportModal()">
                        📄 Add to Doctor PDF
                    </button>
                </div>
            </div>
        `;
    }

    // 2. Emergency First-Aid Action Flashcard
    if (data.is_first_aid_intent || data.first_aid_data || data.first_aid_card_id) {
        const card = data.first_aid_data || {};
        const cardId = data.first_aid_card_id || card.id || 'cpr_adult';
        const title = card.title || 'Emergency First-Aid Protocol';
        const icon = card.icon || '🚑';
        const category = card.category_label || 'Emergency Response';
        const summary = card.summary || 'Immediate sequential life-support and emergency first-aid actions.';
        const metronomeBtn = card.metronome_bpm ? `
            <button type="button" class="icc-action-btn icc-btn-emergency-pulse" onclick="openFirstAidModal('${cardId}')">
                ⏱️ Start CPR ${card.metronome_bpm} BPM Metronome
            </button>
        ` : '';

        const stepsPreview = (card.steps || []).slice(0, 2).map(s => `
            <div class="icc-step-pill">
                <span class="icc-step-num">Step ${s.step_num}</span>
                <span class="icc-step-text"><strong>${escapeHtml(s.title)}:</strong> ${escapeHtml(s.action)}</span>
            </div>
        `).join('');

        return `
            <div class="interactive-chat-card icc-emergency">
                <div class="icc-header">
                    <div class="icc-icon-wrapper icc-icon-emergency">${icon}</div>
                    <div class="icc-header-text">
                        <div class="icc-badge-row">
                            <span class="icc-badge icc-badge-red">🚨 ${escapeHtml(category)}</span>
                            <span class="icc-sub-badge">Action Flashcard</span>
                        </div>
                        <h4 class="icc-title">${escapeHtml(title)}</h4>
                    </div>
                </div>
                <div class="icc-body">
                    <p class="icc-desc">${escapeHtml(summary)}</p>
                    ${stepsPreview ? `<div class="icc-first-aid-steps-preview">${stepsPreview}</div>` : ''}
                </div>
                <div class="icc-actions">
                    <button type="button" class="icc-action-btn icc-btn-emergency" onclick="openFirstAidModal('${cardId}')">
                        🚑 Open Flashcard Guide
                    </button>
                    ${metronomeBtn}
                    <button type="button" class="icc-action-btn icc-btn-secondary" onclick="attachFirstAidToDoctorSummary(); openExportModal();">
                        📄 Attach to Doctor PDF
                    </button>
                </div>
            </div>
        `;
    }

    // 3. Calm & Mental Health Wellbeing Card
    if (data.is_mental_health_intent || data.mh_category || data.protocol_info) {
        const cat = data.mh_category || 'somatic_pacers';
        const pinfo = data.protocol_info || {};
        const title = pinfo.title || (data.scale_id ? 'Clinical Psychometric Assessment' : 'Calm & Mental Wellbeing Suite');
        const icon = pinfo.icon || (cat === 'crisis_safety' ? '🛡️' : '🧠');
        const badge = pinfo.badge || (cat === 'crisis_safety' ? 'Crisis Safety' : 'Somatic & Mental Health');
        const summary = pinfo.summary || 'Neurobiologically grounded breathing pacers, Jacobson PMR, and validated clinical scales.';

        return `
            <div class="interactive-chat-card icc-calm">
                <div class="icc-header">
                    <div class="icc-icon-wrapper icc-icon-calm">${icon}</div>
                    <div class="icc-header-text">
                        <div class="icc-badge-row">
                            <span class="icc-badge icc-badge-purple">🧠 ${escapeHtml(badge)}</span>
                            <span class="icc-sub-badge">Vagal Regulation</span>
                        </div>
                        <h4 class="icc-title">${escapeHtml(title)}</h4>
                    </div>
                </div>
                <div class="icc-body">
                    <p class="icc-desc">${escapeHtml(summary)}</p>
                    <div class="icc-metrics-grid">
                        <div class="icc-metric-item">
                            <span class="icc-metric-label">Active Modalities</span>
                            <span class="icc-metric-value">4-7-8 • Box Breathing • PMR • GAD-7 / PHQ-9</span>
                        </div>
                        <div class="icc-metric-item">
                            <span class="icc-metric-label">Neurobiology</span>
                            <span class="icc-metric-value">Parasympathetic Vagal Activation</span>
                        </div>
                    </div>
                </div>
                <div class="icc-actions">
                    <button type="button" class="icc-action-btn icc-btn-calm" onclick="openCalmMentalHealthHub('${cat}')">
                        🧠 Launch Calm Hub
                    </button>
                    <button type="button" class="icc-action-btn icc-btn-secondary" onclick="openCalmMentalHealthHub('somatic_pacers')">
                        🫁 4-7-8 Breathing Pacer
                    </button>
                    <button type="button" class="icc-action-btn icc-btn-secondary" onclick="openCalmMentalHealthHub('clinical_scales')">
                        📋 GAD-7 / PHQ-9 Screener
                    </button>
                </div>
            </div>
        `;
    }

    // 4. Medical Nutrition Therapy Card
    if (data.is_nutrition_intent || data.nutrition_data) {
        const mnt = data.nutrition_data || {};
        const protos = mnt.evaluated_protocols || [];
        const proto = protos[0] || {};
        const title = proto.name || (proto.condition ? `${proto.condition} Nutrition Protocol` : 'Medical Nutrition Therapy');
        const icon = proto.icon || '🥗';
        const prioritize = (mnt.prioritize_foods || proto.prioritize_foods || []).slice(0, 3).join(', ');
        const avoid = (mnt.avoid_foods || proto.avoid_foods || []).slice(0, 3).join(', ');

        return `
            <div class="interactive-chat-card icc-nutrition">
                <div class="icc-header">
                    <div class="icc-icon-wrapper icc-icon-nutrition">${icon}</div>
                    <div class="icc-header-text">
                        <div class="icc-badge-row">
                            <span class="icc-badge icc-badge-green">🥗 Dietary Protocol</span>
                            <span class="icc-sub-badge">Evidence-Based MNT</span>
                        </div>
                        <h4 class="icc-title">${escapeHtml(title)}</h4>
                    </div>
                </div>
                <div class="icc-body">
                    <div class="icc-food-grid">
                        <div class="icc-food-box icc-food-prioritize">
                            <span class="icc-food-label">🟢 Prioritize:</span>
                            <span class="icc-food-content">${escapeHtml(prioritize || 'High-fiber, unprocessed whole foods')}</span>
                        </div>
                        <div class="icc-food-box icc-food-avoid">
                            <span class="icc-food-label">🔴 Avoid / Limit:</span>
                            <span class="icc-food-content">${escapeHtml(avoid || 'Ultra-processed items, refined sugars & excess sodium')}</span>
                        </div>
                    </div>
                </div>
                <div class="icc-actions">
                    <button type="button" class="icc-action-btn icc-btn-primary" onclick="openMedsLabsDietHub('nutrition')">
                        🥗 Customize Nutrition Plan
                    </button>
                    <button type="button" class="icc-action-btn icc-btn-secondary" onclick="openMedsLabsDietHub('polypharmacy')">
                        💊 Food-Drug Interaction Cross Check
                    </button>
                    <button type="button" class="icc-action-btn icc-btn-secondary" onclick="openExportModal()">
                        📄 Add to Doctor PDF
                    </button>
                </div>
            </div>
        `;
    }

    // 5. Polypharmacy Safety Card
    if (data.is_medication_guard || data.polypharmacy_data) {
        const poly = data.polypharmacy_data || {};
        const interactions = poly.interactions || [];
        const top = interactions[0] || {};
        const severity = top.severity || 'MODERATE';
        const badgeColor = severity === 'MAJOR' ? 'icc-badge-red' : 'icc-badge-amber';

        return `
            <div class="interactive-chat-card icc-polypharmacy">
                <div class="icc-header">
                    <div class="icc-icon-wrapper icc-icon-poly">💊</div>
                    <div class="icc-header-text">
                        <div class="icc-badge-row">
                            <span class="icc-badge ${badgeColor}">${escapeHtml(severity)} PRECAUTION</span>
                            <span class="icc-sub-badge">Polypharmacy Matrix</span>
                        </div>
                        <h4 class="icc-title">Drug Interaction Alert: ${escapeHtml(top.item_1 || 'Drug A')} + ${escapeHtml(top.item_2 || 'Drug B')}</h4>
                    </div>
                </div>
                <div class="icc-body">
                    <p class="icc-desc"><strong>${escapeHtml(top.title || 'Potential interaction detected.')}</strong> ${escapeHtml(top.effects || '')}</p>
                </div>
                <div class="icc-actions">
                    <button type="button" class="icc-action-btn icc-btn-primary" onclick="openMedsLabsDietHub('polypharmacy')">
                        💊 Open Polypharmacy Checker
                    </button>
                    <button type="button" class="icc-action-btn icc-btn-secondary" onclick="openExportModal()">
                        📄 Attach to Doctor PDF
                    </button>
                </div>
            </div>
        `;
    }

    // 6. Laboratory Biomarker Card
    if (data.is_lab_interpretation || data.lab_data) {
        const lab = data.lab_data || {};
        return `
            <div class="interactive-chat-card icc-lab">
                <div class="icc-header">
                    <div class="icc-icon-wrapper icc-icon-lab">🔬</div>
                    <div class="icc-header-text">
                        <div class="icc-badge-row">
                            <span class="icc-badge icc-badge-cyan">${escapeHtml(lab.badge || 'Laboratory Biomarker')}</span>
                            <span class="icc-sub-badge">Evidence Reference</span>
                        </div>
                        <h4 class="icc-title">${escapeHtml(lab.test_name || 'Biomarker Interpretation')}</h4>
                    </div>
                </div>
                <div class="icc-body">
                    <div class="icc-metrics-grid">
                        <div class="icc-metric-item">
                            <span class="icc-metric-label">Your Value</span>
                            <span class="icc-metric-value">${escapeHtml(String(lab.value || ''))} ${escapeHtml(lab.unit || '')}</span>
                        </div>
                        <div class="icc-metric-item">
                            <span class="icc-metric-label">Target Reference</span>
                            <span class="icc-metric-value">${escapeHtml(lab.reference_range || lab.optimal_target || 'Normal Range')}</span>
                        </div>
                    </div>
                </div>
                <div class="icc-actions">
                    <button type="button" class="icc-action-btn icc-btn-primary" onclick="openMedsLabsDietHub('labs')">
                        🔬 Open Lab Interpreter
                    </button>
                    <button type="button" class="icc-action-btn icc-btn-secondary" onclick="openExportModal()">
                        📄 Attach to Doctor PDF
                    </button>
                </div>
            </div>
        `;
    }

    // 7. Condition Database Overview Card
    if (data.disease_data) {
        const d = data.disease_data;
        const name = d.disease_name || 'Condition';
        const cat = d.category || 'Clinical Topic';
        const symptoms = d.symptoms || '';
        const precautions = d.precautions || '';

        return `
            <div class="interactive-chat-card icc-condition">
                <div class="icc-header">
                    <div class="icc-icon-wrapper icc-icon-condition">🩺</div>
                    <div class="icc-header-text">
                        <div class="icc-badge-row">
                            <span class="icc-badge icc-badge-teal">${escapeHtml(cat)}</span>
                            <span class="icc-sub-badge">Verified Health Card</span>
                        </div>
                        <h4 class="icc-title">${escapeHtml(name)} Quick Overview</h4>
                    </div>
                </div>
                <div class="icc-body">
                    <div class="icc-food-grid">
                        <div class="icc-food-box icc-food-prioritize">
                            <span class="icc-food-label">🔍 Key Symptoms:</span>
                            <span class="icc-food-content">${escapeHtml(symptoms)}</span>
                        </div>
                        <div class="icc-food-box icc-food-avoid">
                            <span class="icc-food-label">🛡️ Recommended Care:</span>
                            <span class="icc-food-content">${escapeHtml(precautions)}</span>
                        </div>
                    </div>
                </div>
                <div class="icc-actions">
                    <button type="button" class="icc-action-btn icc-btn-primary" onclick="openSymptomTriageHub('triage')">
                        🩺 Start 5-Step Triage
                    </button>
                    <button type="button" class="icc-action-btn icc-btn-secondary" onclick="openMedsLabsDietHub('nutrition')">
                        🥗 Diet & Nutrition
                    </button>
                    <button type="button" class="icc-action-btn icc-btn-secondary" onclick="openExportModal()">
                        📄 Download Doctor PDF
                    </button>
                </div>
            </div>
        `;
    }

    // 8. Triage Trigger / Red-Flag Card
    if (data.is_triage_trigger || (data.has_red_flags && !data.is_emergency)) {
        return `
            <div class="interactive-chat-card icc-triage-trigger">
                <div class="icc-header">
                    <div class="icc-icon-wrapper icc-icon-triage">🩺</div>
                    <div class="icc-header-text">
                        <div class="icc-badge-row">
                            <span class="icc-badge icc-badge-amber">Symptom Triage</span>
                            <span class="icc-sub-badge">Clinical Red-Flag Screen</span>
                        </div>
                        <h4 class="icc-title">Guided Symptom Assessment</h4>
                    </div>
                </div>
                <div class="icc-body">
                    <p class="icc-desc">Assess severity, duration, and red-flag symptoms with our 5-step clinical triage engine.</p>
                </div>
                <div class="icc-actions">
                    <button type="button" class="icc-action-btn icc-btn-primary" onclick="openSymptomTriageHub('triage')">
                        🩺 Launch Guided Triage
                    </button>
                    <button type="button" class="icc-action-btn icc-btn-secondary" onclick="openSymptomTriageHub('bodymap')">
                        🗺️ Interactive Body Map
                    </button>
                </div>
            </div>
        `;
    }

    return '';
}

/**
 * Append bot response bubble with formatting, citations, smart quick-replies, triage actions, polypharmacy alerts, lab badges, and interactive visual cards
 */
function appendBotMessage(rawText, isEmergency = false, customClass = '', citations = [], suggestions = [], isMedicationGuard = false, isTriageReport = false, polypharmacyAlerts = [], labInterpretations = [], cardData = null) {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper bot-wrapper';

    const avatar = document.createElement('div');
    let avatarClass = 'avatar bot-avatar';
    if (isEmergency) avatarClass += ' emergency-avatar';
    if (isMedicationGuard) avatarClass += ' medication-avatar';
    if (isTriageReport) avatarClass += ' triage-avatar';
    avatar.className = avatarClass;

    if (isEmergency) {
        avatar.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="12 2 22 20 2 20 12 2"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
        `;
    } else if (isMedicationGuard) {
        avatar.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"/>
                <path d="m8.5 8.5 7 7"/>
            </svg>
        `;
    } else if (isTriageReport) {
        avatar.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
            </svg>
        `;
    } else {
        avatar.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2v20M2 12h20"/>
            </svg>
        `;
    }

    const bubble = document.createElement('div');
    let bubbleClasses = 'message-bubble bot-bubble';
    if (isEmergency) bubbleClasses += ' emergency-bubble';
    if (customClass) bubbleClasses += ` ${customClass}`;
    bubble.className = bubbleClasses;

    // 1. Main formatted text
    let htmlContent = formatMarkdown(rawText);

    // 1b. Interactive Compact Visual Chat Card (if intent/structured data returned)
    if (cardData) {
        const interactiveCardHtml = buildInteractiveChatCard(cardData);
        if (interactiveCardHtml) {
            htmlContent += interactiveCardHtml;
        }
    }

    // 2. Action row for Triage Report
    if (isTriageReport) {
        htmlContent += `
            <div class="triage-action-row">
                <button type="button" class="export-doctor-btn" onclick="openExportModal()">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                    </svg>
                    <span>📄 Download PDF Report</span>
                </button>
                <button type="button" class="copy-doctor-btn" onclick="copyTriageToClipboard(this)">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                    </svg>
                    <span>📋 Copy Summary</span>
                </button>
            </div>
        `;
    }

    // 3. Polypharmacy Alerts in Chat (if detected)
    if (polypharmacyAlerts && polypharmacyAlerts.length > 0) {
        polypharmacyAlerts.forEach(alert => {
            htmlContent += `
                <div class="chat-poly-alert">
                    <strong>🛡️ Drug Safety Notice (${escapeHtml(alert.drug_a)} + ${escapeHtml(alert.drug_b)}):</strong>
                    <span>${escapeHtml(alert.effect)}</span>
                    <div style="font-size: 0.74rem; margin-top: 4px; color: #881337;">
                        <em>${escapeHtml(alert.clinical_recommendation)}</em>
                    </div>
                </div>
            `;
        });
    }

    // 4. Lab Biomarker Badges in Chat (if detected)
    if (labInterpretations && labInterpretations.length > 0) {
        labInterpretations.forEach(lab => {
            const statusColor = lab.status_color || '#0891b2';
            htmlContent += `
                <div class="chat-lab-badge">
                    <div>
                        <strong>🔬 Biomarker: ${escapeHtml(lab.test_name)}</strong> = <strong>${lab.value} ${escapeHtml(lab.unit)}</strong>
                        <span style="display: block; font-size: 0.74rem; color: #475569;">Target: ${escapeHtml(lab.optimal_target)} &bull; Status: <strong style="color: ${statusColor};">${escapeHtml(lab.status_label)}</strong></span>
                    </div>
                    <button type="button" class="poly-chip" style="margin-left: 8px;" onclick="openLabModal()">Open Interpreter →</button>
                </div>
            `;
        });
    }

    // 5. Source Citations
    if (citations && citations.length > 0) {
        const citationLinks = citations.map(c => `
            <a href="${c.url}" target="_blank" rel="noopener noreferrer" class="citation-tag">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                    <polyline points="15 3 21 3 21 9"/>
                    <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
                ${escapeHtml(c.name)}
            </a>
        `).join('');

        htmlContent += `
            <div class="citations-container">
                <span class="citations-label">Verified Clinical Sources:</span>
                ${citationLinks}
            </div>
        `;
    }

    // 6. Smart Follow-Up Suggestions
    if (suggestions && suggestions.length > 0) {
        const chipsHtml = suggestions.map(s => `
            <button type="button" class="smart-chip" onclick="sendSuggested('${escapeHtml(s).replace(/'/g, "\\'")}')">
                💬 ${escapeHtml(s)}
            </button>
        `).join('');

        htmlContent += `
            <div class="smart-suggestions">
                <span class="smart-label">Suggested next questions:</span>
                <div class="smart-chips-row">${chipsHtml}</div>
            </div>
        `;
    }

    bubble.innerHTML = htmlContent;

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    chatHistory.appendChild(wrapper);

    scrollToBottom();
}

/**
 * Render typing indicator animation
 */
function showTypingIndicator() {
    const typingId = 'typing-' + Date.now();
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper bot-wrapper';
    wrapper.id = typingId;

    const avatar = document.createElement('div');
    avatar.className = 'avatar bot-avatar';
    avatar.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2v20M2 12h20"/>
        </svg>
    `;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble bot-bubble';
    bubble.innerHTML = `
        <div class="typing-indicator" aria-label="Thinking">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
    `;

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    chatHistory.appendChild(wrapper);
    scrollToBottom();

    return typingId;
}

/**
 * Remove typing indicator element
 */
function removeTypingIndicator(typingId) {
    const el = document.getElementById(typingId);
    if (el) {
        el.remove();
    }
}

/**
 * Toggle input loading state
 */
function setLoadingState(isLoading) {
    userInput.disabled = isLoading;
    sendButton.disabled = isLoading;
    if (!isLoading) {
        userInput.focus();
    }
}

/**
 * Scroll chat smoothly to the latest message
 */
function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

/**
 * Escape HTML characters
 */
function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

/**
 * Convert markdown to safe HTML with Red-Flag & Uncertainty highlight blocks and ELI5 details dropdowns
 */
function formatMarkdown(text) {
    if (!text) return '';

    let safe = escapeHtml(text);

    // Unescape safe clinical details and ELI5 components
    safe = safe.replace(/&lt;details class=&quot;clinical-details-dropdown&quot;&gt;/g, '<details class="clinical-details-dropdown">')
               .replace(/&lt;details class=&quot;clinical-details-dropdown&quot; open&gt;/g, '<details class="clinical-details-dropdown" open>')
               .replace(/&lt;details&gt;/g, '<details>')
               .replace(/&lt;\/details&gt;/g, '</details>')
               .replace(/&lt;summary&gt;(.*?)&lt;\/summary&gt;/g, '<summary>$1</summary>')
               .replace(/&lt;div class=&quot;(.*?)&quot;&gt;/g, '<div class="$1">')
               .replace(/&lt;div style=&quot;(.*?)&quot;&gt;/g, '<div style="$1">')
               .replace(/&lt;\/div&gt;/g, '</div>')
               .replace(/&lt;span class=&quot;(.*?)&quot;&gt;/g, '<span class="$1">')
               .replace(/&lt;span style=&quot;(.*?)&quot;&gt;/g, '<span style="$1">')
               .replace(/&lt;\/span&gt;/g, '</span>')
               .replace(/&lt;p style=&quot;(.*?)&quot;&gt;/g, '<p style="$1">')
               .replace(/&lt;p&gt;/g, '<p>')
               .replace(/&lt;\/p&gt;/g, '</p>')
               .replace(/&lt;ul style=&quot;(.*?)&quot;&gt;/g, '<ul style="$1">')
               .replace(/&lt;ul&gt;/g, '<ul>')
               .replace(/&lt;\/ul&gt;/g, '</ul>')
               .replace(/&lt;li&gt;/g, '<li>')
               .replace(/&lt;\/li&gt;/g, '</li>');

    // 1. Clinical Red-Flag block
    if (safe.includes('🚩 **CLINICAL RED-FLAG NOTICE**:')) {
        const parts = safe.split('🚩 **CLINICAL RED-FLAG NOTICE**:');
        const mainText = parts[0];
        const redFlagContent = '🚩 <strong>CLINICAL RED-FLAG NOTICE</strong>:' + parts[1];
        safe = `${mainText}<div class="redflag-highlight">${redFlagContent}</div>`;
    }

    // 2. Clinical Evidence & Uncertainty block
    if (safe.includes('🔬 **CLINICAL EVIDENCE &amp; UNCERTAINTY') || safe.includes('🔬 **CLINICAL EVIDENCE & UNCERTAINTY')) {
        const marker = safe.includes('🔬 **CLINICAL EVIDENCE &amp; UNCERTAINTY') ? '🔬 **CLINICAL EVIDENCE &amp; UNCERTAINTY' : '🔬 **CLINICAL EVIDENCE & UNCERTAINTY';
        const parts = safe.split(marker);
        const mainText = parts[0];
        const uncertaintyContent = '🔬 <strong>CLINICAL EVIDENCE &amp; UNCERTAINTY</strong>' + parts[1];
        safe = `${mainText}<div class="uncertainty-highlight">${uncertaintyContent}</div>`;
    }

    // 3. 3-Tier ELI5 Plain Language Chat Card Transformations
    if (safe.includes('💡 **Plain Language')) {
        safe = safe.replace(/💡 \*\*(?:Plain Language \(ELI5\)|Plain Language Summary|Plain Language)\*\*:?\s*(.*?)(?=(?:\n\n📋|\n\n🩺|\n\n🔬|\n\n🚩|\n\n\*Educational|$))/s, function(match, content) {
            return `<div class="eli5-headline-card tier-safe"><div class="eli5-status-icon">💡</div><div class="eli5-headline-body"><div class="eli5-title">Plain Language (ELI5) Summary</div><div class="eli5-desc">${content.trim()}</div></div></div>`;
        });
    }

    if (safe.includes('📋 **Evidence-Based Home Care') || safe.includes('📋 **Evidence-Based Key Tips') || safe.includes('💡 **3 Action Steps')) {
        safe = safe.replace(/(?:📋 \*\*(?:Evidence-Based Home Care &amp; Precautions|Evidence-Based Home Care & Precautions|Evidence-Based Home Care|Evidence-Based Key Tips)\*\*:?|💡 \*\*3 Action Steps You Can Take:\*\*)\s*(.*?)(?=(?:\n\n🩺|\n\n🔬|\n\n🚩|\n\n<details|\n\n\*Educational|$))/s, function(match, content) {
            const rawLines = content.trim().split(/\n+/);
            const itemsHtml = rawLines.map((line, idx) => {
                const clean = line.replace(/^[•\d\.\s\-\*]+/, '').trim();
                return clean ? `<div class="eli5-action-item"><span class="action-num-badge">${idx + 1}</span><span>${clean}</span></div>` : '';
            }).filter(Boolean).join('');
            return `<div class="eli5-actions-card"><div class="eli5-actions-title">📋 Evidence-Based Home Care &amp; Action Plan</div><div class="eli5-action-list">${itemsHtml}</div></div>`;
        });
    }

    if (safe.includes('🩺 **Questions for Your Doctor') || safe.includes('🩺 **Questions to Ask Your Doctor')) {
        safe = safe.replace(/🩺 \*\*(?:Questions for Your Doctor|Questions to Ask Your Doctor)\*\*:?\s*(.*?)(?=(?:\n\n🔬|\n\n🚩|\n\n\*Educational|$))/s, function(match, content) {
            const rawLines = content.trim().split(/\n+/);
            const questionsHtml = rawLines.map(line => {
                const clean = line.replace(/^[•\d\.\s\-\*]+/, '').trim();
                return clean ? `<li>${clean}</li>` : '';
            }).filter(Boolean).join('');
            return `<details class="clinical-details-dropdown" open><summary>🩺 Questions to Ask Your Doctor &amp; Clinical Talking Points</summary><div class="clinical-details-content"><ul style="margin: 4px 0 0 16px; padding: 0;">${questionsHtml}</ul></div></details>`;
        });
    }

    return formatParagraphs(safe);
}

function formatParagraphs(safeText) {
    // Bold: **text**
    let formatted = safeText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic: *text*
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Bullet points: • or *
    formatted = formatted.replace(/•\s+(.*?)(?=<br>|<\/p>|$)/g, '<li>$1</li>');

    // Convert double newlines to paragraph breaks, single newlines to <br> if not inside HTML tags
    const paragraphs = formatted.split(/\n\n+/);
    return paragraphs.map(p => {
        if (p.trim().startsWith('<details') || p.trim().startsWith('<div') || p.trim().startsWith('<ul')) {
            return p;
        }
        return `<p>${p.replace(/\n/g, '<br>')}</p>`;
    }).join('');
}

/**
 * ============================================================================
 * CLINICAL INTAKE SUMMARY (PDF & PRINT) CONTROLLER
 * ============================================================================
 */

function openExportModal() {
    compileClinicalIntake();
    const exportModal = document.getElementById('export-modal');
    if (exportModal) {
        exportModal.classList.remove('hidden');
    }
}

function closeExportModal() {
    const exportModal = document.getElementById('export-modal');
    if (exportModal) {
        exportModal.classList.add('hidden');
    }
}

/**
 * Compile structured clinical intake data from conversation history & triage state
 */
function compileClinicalIntake() {
    const metaContainer = document.getElementById('intake-doc-meta');
    const sectionsContainer = document.getElementById('intake-sections-content');
    if (!sectionsContainer) return;

    // 1. Format metadata
    const now = new Date();
    const dateFormatted = now.toLocaleDateString(undefined, { 
        weekday: 'short', 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
    const timeFormatted = now.toLocaleTimeString(undefined, { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    const selectedRegion = regionSelect ? regionSelect.value : 'GLOBAL';
    const emergencyNum = (REGION_FOOTER_HOTLINES[selectedRegion] || '').match(/\d{3,5}/) ? (REGION_FOOTER_HOTLINES[selectedRegion] || '').match(/\d{3,5}/)[0] : '911 / 112';
    const refCode = 'RPT-' + Math.random().toString(36).substring(2, 7).toUpperCase();

    if (metaContainer) {
        metaContainer.innerHTML = `
            <div><strong>Date:</strong> ${dateFormatted} at ${timeFormatted}</div>
            <div><strong>Region Context:</strong> ${selectedRegion} (Emergency: ${emergencyNum})</div>
            <div><strong>Document ID:</strong> ${refCode}</div>
        `;
    }

    // 2. Extract Category / Chief Concern
    let chiefConcern = "General Health Consultation & Symptom Screening";
    let categoryName = "General Health & Wellness";
    
    if (triageAnswers && triageAnswers.category) {
        const catObj = (TRIAGE_CONFIG.categories || []).find(c => c.id === triageAnswers.category);
        if (catObj) {
            categoryName = catObj.name;
            chiefConcern = catObj.name;
        }
    }

    // Check if user asked something prominent in conversation
    const userQueries = conversationHistory
        .filter(m => m.role === 'user' && !m.text.startsWith('Completed Guided Symptom Triage'))
        .map(m => m.text);

    if (userQueries.length > 0) {
        chiefConcern = `${chiefConcern} (${userQueries[0]})`;
    }

    // 3. Duration & Severity
    let durationLabel = "Not explicitly recorded";
    if (triageAnswers && triageAnswers.duration) {
        const durObj = (TRIAGE_CONFIG.durations || []).find(d => d.id === triageAnswers.duration);
        durationLabel = durObj ? durObj.label : triageAnswers.duration;
    }

    let severityLabel = "Mild (Manageable)";
    let severityClass = "intake-badge-green";
    if (triageAnswers && triageAnswers.severity) {
        if (triageAnswers.severity === 'severe') {
            severityLabel = "🔴 Severe (Debilitating - Seek Prompt Medical Review)";
            severityClass = "intake-badge-red";
        } else if (triageAnswers.severity === 'moderate') {
            severityLabel = "🟡 Moderate (Disruptive to Routine)";
            severityClass = "intake-badge-amber";
        } else {
            severityLabel = "🟢 Mild (Manageable)";
            severityClass = "intake-badge-green";
        }
    }

    // 4. Red-Flags Screening
    let redFlagsHtml = '';
    if (triageAnswers && triageAnswers.red_flags && triageAnswers.red_flags.length > 0) {
        const flagsList = triageAnswers.red_flags.map(f => `<li>⚠️ <strong>${escapeHtml(f)}</strong></li>`).join('');
        redFlagsHtml = `
            <div class="triage-warning-box" style="margin-top: 4px;">
                <strong>Critical Red-Flags Identified during Screening:</strong>
                <ul style="margin: 4px 0 0 18px; padding: 0;">${flagsList}</ul>
                <div style="margin-top: 4px; font-weight: 600;">Recommendation: Immediate clinical evaluation or emergency medical attention advised.</div>
            </div>
        `;
    } else {
        redFlagsHtml = `
            <div class="intake-data-block">
                <span class="intake-label">Emergency Red-Flag Screening</span>
                <span class="intake-badge intake-badge-green">✓ Screened Negative — No Acute Emergency Red-Flags Reported</span>
            </div>
        `;
    }

    // 5. Accompanying Symptoms & Specific Indicators
    let accompanyingList = (triageAnswers && triageAnswers.accompanying) ? [...triageAnswers.accompanying] : [];
    
    // Scan conversation for additional symptom keywords
    const commonSymptoms = ['cough', 'fever', 'headache', 'nausea', 'sore throat', 'fatigue', 'chest pain', 'congestion', 'dizziness', 'chills', 'shortness of breath', 'rash', 'joint pain'];
    const convText = conversationHistory.map(m => m.text).join(' ').toLowerCase();
    commonSymptoms.forEach(sym => {
        if (convText.includes(sym) && !accompanyingList.some(item => item.toLowerCase().includes(sym))) {
            accompanyingList.push(sym.charAt(0).toUpperCase() + sym.slice(1));
        }
    });

    let accompanyingHtml = '';
    if (accompanyingList.length > 0) {
        const items = accompanyingList.map(item => `
            <li class="intake-check-item">
                <span class="intake-checkbox-box" style="background: #0284c7; border-color: #0284c7; color: white; display: flex; align-items: center; justify-content: center; font-size: 10px;">✓</span>
                <span>${escapeHtml(item)}</span>
            </li>
        `).join('');
        accompanyingHtml = `<ul class="intake-checklist">${items}</ul>`;
    } else {
        accompanyingHtml = `<div style="font-size: 0.84rem; color: #64748b; font-style: italic;">No secondary accompanying symptoms recorded during session.</div>`;
    }

    // 6. Medication & Substances Discussed
    const commonMeds = ['ibuprofen', 'acetaminophen', 'paracetamol', 'aspirin', 'amoxicillin', 'azithromycin', 'omeprazole', 'metformin', 'lisinopril', 'albuterol', 'diphenhydramine', 'loratadine', 'cetirizine', 'naproxen', 'antacid'];
    const medsFound = [];
    commonMeds.forEach(med => {
        if (convText.includes(med)) {
            medsFound.push(med.charAt(0).toUpperCase() + med.slice(1));
        }
    });

    let medsHtml = '';
    if (medsFound.length > 0) {
        medsHtml = `
            <div class="intake-data-block">
                <span class="intake-label">Medications Queried / Discussed in Session</span>
                <span class="intake-val">${medsFound.map(m => escapeHtml(m)).join(', ')}</span>
                <span style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">⚠️ Educational discussion only. No prescriptions issued or dosage changes advised.</span>
            </div>
        `;
    } else {
        medsHtml = `
            <div class="intake-data-block">
                <span class="intake-label">Medications / Drug Interactions</span>
                <span class="intake-val" style="color: #64748b; font-weight: normal; font-size: 0.82rem;">None specifically queried during session. Patient should disclose active medications & allergies directly to doctor.</span>
            </div>
        `;
    }

    // 6. Polypharmacy & Drug Interactions Section
    let polypharmacyHtml = '';
    if (window.attachedPolypharmacyResults && window.attachedPolypharmacyResults.interactions && window.attachedPolypharmacyResults.interactions.length > 0) {
        const intItems = window.attachedPolypharmacyResults.interactions.map(item => `
            <div style="background: #fff1f2; border: 1px solid #fecdd3; border-left: 4px solid #e11d48; border-radius: 6px; padding: 8px 10px; margin-bottom: 6px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="color: #9f1239; font-size: 0.86rem;">${escapeHtml(item.drug_a)} + ${escapeHtml(item.drug_b)}</strong>
                    <span class="poly-severity-pill badge-${item.severity.toLowerCase()}">${escapeHtml(item.severity.toUpperCase())} RISK</span>
                </div>
                <div style="font-size: 0.78rem; color: #1e293b; margin-top: 3px;"><strong>Mechanism:</strong> ${escapeHtml(item.effect)}</div>
                <div style="font-size: 0.76rem; color: #475569; margin-top: 2px;"><strong>Clinical Precaution:</strong> ${escapeHtml(item.clinical_recommendation)}</div>
            </div>
        `).join('');
        polypharmacyHtml = `
            <div class="intake-section">
                <h3 class="intake-section-title">4. Multi-Drug Polypharmacy Safety Matrix</h3>
                <div style="font-size: 0.8rem; color: #475569; margin-bottom: 6px;">Checked medications / conditions: <strong>${(window.attachedPolypharmacyResults.drugs || []).join(', ')}</strong></div>
                ${intItems}
            </div>
        `;
    } else if (medsFound.length > 0) {
        polypharmacyHtml = `
            <div class="intake-section">
                <h3 class="intake-section-title">4. Medications & Substances Reviewed</h3>
                ${medsHtml}
            </div>
        `;
    } else {
        polypharmacyHtml = `
            <div class="intake-section">
                <h3 class="intake-section-title">4. Medications & Substances Reviewed</h3>
                ${medsHtml}
            </div>
        `;
    }

    // 7. Attached Lab Results & Biomarkers Section
    let labsHtml = '';
    if (window.attachedLabResults && window.attachedLabResults.length > 0) {
        const labRows = window.attachedLabResults.map(lab => `
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 12px; margin-bottom: 6px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="font-size: 0.86rem; color: #0f172a;">${escapeHtml(lab.test_name)}: ${lab.value} ${escapeHtml(lab.unit)}</strong>
                    <span class="intake-badge ${lab.status === 'optimal' ? 'intake-badge-green' : (lab.status === 'high' || lab.status === 'critical') ? 'intake-badge-red' : 'intake-badge-amber'}">${escapeHtml(lab.status_label)}</span>
                </div>
                <div style="font-size: 0.76rem; color: #64748b; margin-top: 2px;">Optimal Reference Target: <strong>${escapeHtml(lab.optimal_target)}</strong> &bull; Panel: ${escapeHtml(lab.panel)}</div>
                ${lab.physician_talking_points && lab.physician_talking_points.length > 0 ? `
                    <div style="font-size: 0.74rem; color: #1e3a8a; background: #eff6ff; padding: 4px 8px; border-radius: 4px; margin-top: 4px;">
                        <strong>Physician Talking Point:</strong> ${escapeHtml(lab.physician_talking_points[0])}
                    </div>
                ` : ''}
            </div>
        `).join('');
        labsHtml = `
            <div class="intake-section">
                <h3 class="intake-section-title">5. Patient Lab Biomarkers & Vitals Profile</h3>
                ${labRows}
            </div>
        `;
    }

    // 8. Attached Medical Nutrition Therapy (Diet-Disease Prescriptor) Section
    let nutritionHtml = '';
    if (window.attachedNutritionPlan && window.attachedNutritionPlan.evaluated_protocols && window.attachedNutritionPlan.evaluated_protocols.length > 0) {
        const plan = window.attachedNutritionPlan;
        const protocolNames = plan.evaluated_protocols.map(p => p.name).join(', ');
        const prioritizeFoods = (plan.prioritize_foods || []).slice(0, 6).map(f => `<li>🟢 <strong>${escapeHtml(f)}</strong></li>`).join('');
        const avoidFoods = (plan.avoid_foods || []).slice(0, 6).map(f => `<li>🔴 <strong>${escapeHtml(f)}</strong></li>`).join('');
        
        let conflictHtml = '';
        if (plan.has_conflicts && plan.conflict_resolutions) {
            const cList = plan.conflict_resolutions.map(c => `<li>⚖️ <strong>${escapeHtml(c.conflict)}:</strong> ${escapeHtml(c.resolution)}</li>`).join('');
            conflictHtml = `
                <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 6px; padding: 6px 10px; margin-top: 6px; font-size: 0.76rem; color: #92400e;">
                    <strong>Reconciled Multi-Condition Conflicts:</strong>
                    <ul style="margin: 2px 0 0 16px; padding: 0;">${cList}</ul>
                </div>
            `;
        }

        let drugFoodHtml = '';
        if (plan.has_drug_interactions && plan.food_drug_interactions) {
            const dList = plan.food_drug_interactions.map(d => `<li>⚠️ <strong>${escapeHtml(d.drug)} + ${escapeHtml(d.food_nutrient)}:</strong> ${escapeHtml(d.warning)}</li>`).join('');
            drugFoodHtml = `
                <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 6px 10px; margin-top: 6px; font-size: 0.76rem; color: #991b1b;">
                    <strong>Food-Drug Interaction Precautions:</strong>
                    <ul style="margin: 2px 0 0 16px; padding: 0;">${dList}</ul>
                </div>
            `;
        }

        nutritionHtml = `
            <div class="intake-section">
                <h3 class="intake-section-title">6. Medical Nutrition Therapy (Diet-Disease Prescriptor)</h3>
                <div style="font-size: 0.8rem; color: #166534; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 6px 10px; margin-bottom: 6px;">
                    <strong>Active Clinical Protocols:</strong> ${escapeHtml(protocolNames)}
                    <div style="font-size: 0.75rem; color: #15803d; margin-top: 2px;">${escapeHtml(plan.clinical_summary || '')}</div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 6px;">
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px;">
                        <strong style="font-size: 0.78rem; color: #166534;">🟢 Prioritize Foods:</strong>
                        <ul style="font-size: 0.74rem; margin: 4px 0 0 16px; padding: 0;">${prioritizeFoods}</ul>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px;">
                        <strong style="font-size: 0.78rem; color: #9f1239;">🔴 Avoid / Restrict:</strong>
                        <ul style="font-size: 0.74rem; margin: 4px 0 0 16px; padding: 0;">${avoidFoods}</ul>
                    </div>
                </div>
                ${conflictHtml}
                ${drugFoodHtml}
            </div>
        `;
    }

    // 8b. Attached First-Aid & Emergency Action Incident Section
    let firstAidHtml = '';
    if (window.attachedFirstAidIncident) {
        const fa = window.attachedFirstAidIncident;
        const stepsPreview = (fa.steps || []).slice(0, 3).map(s => `<li><strong>Step ${s.step_num}: ${escapeHtml(s.title)}</strong> - ${escapeHtml(s.action)}</li>`).join('');
        const donotsPreview = (fa.critical_donots || []).slice(0, 3).map(d => `<li>🚫 ${escapeHtml(d)}</li>`).join('');
        
        firstAidHtml = `
            <div class="intake-section">
                <h3 class="intake-section-title">Emergency & First-Aid Protocol Referenced</h3>
                <div style="font-size: 0.82rem; background: #fff1f2; border: 1.5px solid #fecdd3; border-radius: 8px; padding: 10px 12px; margin-bottom: 6px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <strong style="color: #9f1239; font-size: 0.9rem;">${escapeHtml(fa.icon || '🚑')} ${escapeHtml(fa.title)}</strong>
                        <span class="intake-badge intake-badge-red">${escapeHtml(fa.priority || 'URGENT')}</span>
                    </div>
                    <div style="font-size: 0.76rem; color: #881337; margin-bottom: 6px;">${escapeHtml(fa.summary || '')}</div>
                    
                    <div style="background: white; border: 1px solid #fed7aa; border-radius: 6px; padding: 6px 10px; margin-bottom: 6px;">
                        <strong style="font-size: 0.76rem; color: #9a3412;">⚡ Action Steps Taken / Initiated:</strong>
                        <ul style="font-size: 0.74rem; margin: 4px 0 0 16px; padding: 0; color: #334155;">${stepsPreview}</ul>
                    </div>
                    
                    <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 6px 10px;">
                        <strong style="font-size: 0.76rem; color: #991b1b;">🔴 Clinical DO NOT Warnings:</strong>
                        <ul style="font-size: 0.74rem; margin: 4px 0 0 16px; padding: 0; color: #7f1d1d;">${donotsPreview}</ul>
                    </div>
                </div>
            </div>
        `;
    }

    // 8c. Attached Clinical Risk Assessment & Calculator Report Section
    let calculatorHtml = '';
    if (window.attachedCalculatorReports && window.attachedCalculatorReports.length > 0) {
        const calcsList = window.attachedCalculatorReports.map(rep => {
            const paramsHtml = Object.entries(rep.parameters || {}).map(([k, v]) => `<li><strong>${escapeHtml(k)}:</strong> ${escapeHtml(v)}</li>`).join('');
            const rec = rep.statin_recommendation || rep.anticoagulation_recommendation || rep.clinical_advice || rep.recommendation || rep.triage_recommendation || rep.treatment_recommendation || rep.diagnostic_pathway || rep.prevention_guideline || '';
            return `
                <div style="font-size: 0.82rem; background: #f0fdf4; border: 1.5px solid #bbf7d0; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <strong style="color: #166534; font-size: 0.88rem;">🧮 ${escapeHtml(rep.calculator_title || 'Clinical Risk Tool')}</strong>
                        <span class="intake-badge intake-badge-green">${escapeHtml(rep.tier_label || rep.tier || 'Evaluated')}</span>
                    </div>
                    <div style="display: flex; align-items: baseline; gap: 6px; margin: 4px 0 6px;">
                        <span style="font-size: 1.25rem; font-weight: 800; color: #166534;">${rep.score !== undefined ? rep.score : (rep.bmi || '')}</span>
                        <span style="font-size: 0.8rem; color: #475569; font-weight: 600;">${escapeHtml(rep.score_unit || (rep.bmi ? 'kg/m²' : ''))}</span>
                    </div>
                    ${rec ? `
                        <div style="background: white; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 10px; margin-bottom: 6px; font-size: 0.76rem; color: #334155;">
                            <strong>Guideline Recommendation:</strong> ${escapeHtml(rec)}
                        </div>
                    ` : ''}
                    ${paramsHtml ? `
                        <ul style="font-size: 0.72rem; margin: 4px 0 0 16px; padding: 0; color: #64748b; display: grid; grid-template-columns: 1fr 1fr; gap: 2px 10px;">${paramsHtml}</ul>
                    ` : ''}
                </div>
            `;
        }).join('');

        calculatorHtml = `
            <div class="intake-section">
                <h3 class="intake-section-title">Clinical Risk Assessments & Calculators</h3>
                ${calcsList}
            </div>
        `;
    }

    // 8d. Attached Mental Health & Somatic Regulation Profile Section
    let mentalHealthHtml = '';
    if (window.attachedMentalHealthReports && window.attachedMentalHealthReports.length > 0) {
        const mhRows = window.attachedMentalHealthReports.map(rep => {
            if (rep.type === 'scale') {
                return `
                    <div style="font-size: 0.82rem; background: #faf5ff; border: 1.5px solid #e9d5ff; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <strong style="color: #6b21a8; font-size: 0.88rem;">🧠 ${escapeHtml(rep.scale_title || 'Psychometric Scale')}</strong>
                            <span class="intake-badge intake-badge-amber">${escapeHtml(rep.tier_label || rep.tier || 'Assessed')}</span>
                        </div>
                        <div style="display: flex; align-items: baseline; gap: 6px; margin: 4px 0 6px;">
                            <span style="font-size: 1.25rem; font-weight: 800; color: #6b21a8;">Score: ${rep.score}/${rep.max_score}</span>
                            <span style="font-size: 0.8rem; color: #64748b;">${escapeHtml(rep.score_unit || 'points')}</span>
                        </div>
                        <div style="background: white; border: 1px solid #ddd6fe; border-radius: 6px; padding: 6px 10px; font-size: 0.76rem; color: #334155; margin-bottom: 4px;">
                            <strong>Clinical Assessment:</strong> ${escapeHtml(rep.clinical_action || '')}
                        </div>
                        ${rep.has_suicide_flag ? `
                            <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 4px 8px; font-size: 0.74rem; color: #991b1b; font-weight: 700;">
                                🚨 Question 9 Alert: Positive endorsement for self-harm or death thoughts. National Suicide & Crisis Lifeline: 988.
                            </div>
                        ` : ''}
                    </div>
                `;
            } else if (rep.type === 'safety_plan') {
                const plan = rep.plan || {};
                return `
                    <div style="font-size: 0.82rem; background: #fdf4ff; border: 1.5px solid #f0abfc; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;">
                        <strong style="color: #86198f; font-size: 0.88rem;">🛡️ Stanley-Brown Crisis Safety Plan</strong>
                        <div style="font-size: 0.74rem; color: #701a75; margin: 4px 0 6px;">Evidence-based personalized crisis prevention protocol.</div>
                        <div style="font-size: 0.74rem; line-height: 1.45; color: #334155;">
                            <div><strong>1. Warning Signs:</strong> ${(plan.step1_warning_signs || []).join('; ')}</div>
                            <div><strong>2. Internal Coping:</strong> ${(plan.step2_internal_coping || []).join('; ')}</div>
                            <div><strong>3. Distracting People/Places:</strong> ${(plan.step3_social_distractions || []).join('; ')}</div>
                            <div><strong>4. Trusted Contacts:</strong> ${(plan.step4_trusted_contacts || []).join('; ')}</div>
                            <div><strong>5. Safe Environment:</strong> ${(plan.step6_environment_safety || []).join('; ')}</div>
                        </div>
                    </div>
                `;
            } else if (rep.type === 'somatic') {
                return `
                    <div style="font-size: 0.82rem; background: #f0fdf4; border: 1.5px solid #bbf7d0; border-radius: 8px; padding: 8px 12px; margin-bottom: 6px;">
                        <strong style="color: #166534; font-size: 0.86rem;">🫁 Vagal Somatic Regulation: ${escapeHtml(rep.title)}</strong>
                        <div style="font-size: 0.75rem; color: #15803d; margin-top: 2px;">Completed: ${rep.cycles_completed || 1} breathing cycles (${rep.duration_seconds || 60}s duration).</div>
                        <div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">Neurobiology: ${escapeHtml(rep.vagal_mechanism || '')}</div>
                    </div>
                `;
            }
            return '';
        }).join('');

        mentalHealthHtml = `
            <div class="intake-section">
                <h3 class="intake-section-title">Mental Health & Somatic Regulation Profile</h3>
                ${mhRows}
            </div>
        `;
    }

    // 8e. Attached Medical Vision & Radiology Scans Section
    let visionScansHtml = '';
    if (window.attachedVisionScans && window.attachedVisionScans.length > 0) {
        const scansList = window.attachedVisionScans.map(scan => {
            const findingsHtml = (scan.findings_breakdown && scan.findings_breakdown.length > 0)
                ? scan.findings_breakdown.map(f => `
                    <div style="margin-top: 4px; padding: 4px 6px; background: white; border-radius: 4px; border: 1px solid #e2e8f0; font-size: 0.74rem;">
                        <strong>${escapeHtml(f.organ_structure)}:</strong> <em>${escapeHtml(f.radiologist_finding)}</em>
                        <div style="color: #0284c7; margin-top: 1px;">➜ Plain English: ${escapeHtml(f.plain_english_meaning)}</div>
                    </div>
                `).join('')
                : '';

            return `
                <div style="font-size: 0.82rem; background: #f0f9ff; border: 1.5px solid #bae6fd; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <strong style="color: #0369a1; font-size: 0.88rem;">🩻 ${escapeHtml(scan.doc_type || 'Diagnostic Vision Scan')}</strong>
                        <span class="intake-badge intake-badge-green">OCR Grounded</span>
                    </div>
                    ${scan.radiologist_impression ? `
                        <div style="background: white; border: 1px solid #7dd3fc; border-radius: 6px; padding: 6px 10px; margin-bottom: 6px; font-size: 0.76rem; color: #0c4a6e;">
                            <strong>Impression:</strong> ${escapeHtml(scan.radiologist_impression)}
                        </div>
                    ` : ''}
                    <div style="font-size: 0.76rem; color: #334155; margin-bottom: 4px;">
                        <strong>Summary:</strong> ${escapeHtml(scan.summary || '')}
                    </div>
                    ${findingsHtml ? `
                        <div style="margin-top: 6px;">
                            <strong style="font-size: 0.75rem; color: #0369a1;">Detailed Organ & Structural Findings:</strong>
                            ${findingsHtml}
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');

        visionScansHtml = `
            <div class="intake-section">
                <h3 class="intake-section-title">Diagnostic Imaging & Vision OCR Records</h3>
                ${scansList}
            </div>
        `;
    }

    // 9. Assemble Structured Report Sections
    sectionsContainer.innerHTML = `
        <!-- Section 1: Chief Concern & Timeline -->
        <div class="intake-section">
            <h3 class="intake-section-title">1. Primary Concern & Timeline</h3>
            <div class="intake-grid">
                <div class="intake-data-block">
                    <span class="intake-label">Primary Area / Category</span>
                    <span class="intake-val">${escapeHtml(categoryName)}</span>
                </div>
                <div class="intake-data-block">
                    <span class="intake-label">Reported Duration</span>
                    <span class="intake-val">${escapeHtml(durationLabel)}</span>
                </div>
                <div class="intake-data-block">
                    <span class="intake-label">Reported Severity</span>
                    <span class="intake-badge ${severityClass}">${escapeHtml(severityLabel)}</span>
                </div>
            </div>
            ${userQueries.length > 0 ? `
                <div class="intake-data-block" style="margin-top: 6px;">
                    <span class="intake-label">Patient Initial Statement / Summary</span>
                    <span class="intake-val" style="font-weight: 500; font-size: 0.84rem; color: #334155;">"${escapeHtml(userQueries[0])}"</span>
                </div>
            ` : ''}
        </div>

        <!-- Section 2: Red Flag Screening -->
        <div class="intake-section">
            <h3 class="intake-section-title">2. Red-Flag & Emergency Screening</h3>
            ${redFlagsHtml}
        </div>

        <!-- Section 3: Accompanying Symptoms -->
        <div class="intake-section">
            <h3 class="intake-section-title">3. Accompanying Symptoms & Features</h3>
            ${accompanyingHtml}
        </div>

        <!-- Section 4: Polypharmacy / Medications -->
        ${polypharmacyHtml}

        <!-- Section 5: Lab Tests & Biomarkers -->
        ${labsHtml}

        <!-- Section 6: Medical Nutrition Therapy -->
        ${nutritionHtml}

        <!-- Section 7: First-Aid Incident (if recorded) -->
        ${firstAidHtml}

        <!-- Section 8: Clinical Risk Calculations (if recorded) -->
        ${calculatorHtml}

        <!-- Section 9: Mental Health & Somatic Regulation Profile (if recorded) -->
        ${mentalHealthHtml}

        <!-- Section 10: Diagnostic Imaging & Vision OCR Records (if attached) -->
        ${visionScansHtml}

        <!-- Section 11: Doctor Consultation Checklist -->
        <div class="intake-section">
            <h3 class="intake-section-title">Priority Questions for Doctor Consultation</h3>
            <ul class="intake-checklist">
                <li class="intake-check-item">
                    <span class="intake-checkbox-box"></span>
                    <span>What is the most probable clinical cause or diagnosis for these symptoms?</span>
                </li>
                <li class="intake-check-item">
                    <span class="intake-checkbox-box"></span>
                    <span>Are diagnostic tests, lab work, or imaging (e.g., blood panel, X-ray) recommended?</span>
                </li>
                <li class="intake-check-item">
                    <span class="intake-checkbox-box"></span>
                    <span>What warning signs or deterioration should prompt immediate emergency care?</span>
                </li>
                <li class="intake-check-item">
                    <span class="intake-checkbox-box"></span>
                    <span>Are my current prescription or over-the-counter medications safe to continue?</span>
                </li>
                <li class="intake-check-item">
                    <span class="intake-checkbox-box"></span>
                    <span>What is the expected recovery timeline, and when should I return for a follow-up?</span>
                </li>
            </ul>
        </div>
    `;
}

/**
 * Generate and download high-resolution PDF report using html2pdf.js
 */
async function downloadPdfReport() {
    const downloadBtn = document.getElementById('download-pdf-btn');
    const origBtnContent = downloadBtn ? downloadBtn.innerHTML : '';
    
    if (downloadBtn) {
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = `
            <svg class="spin-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="2" x2="12" y2="6"/>
                <line x1="12" y1="18" x2="12" y2="22"/>
                <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
                <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
                <line x1="2" y1="12" x2="6" y2="12"/>
                <line x1="18" y1="12" x2="22" y2="12"/>
                <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
                <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
            </svg>
            <span>Generating PDF...</span>
        `;
    }

    try {
        const docElement = document.getElementById('intake-document');
        if (!docElement) throw new Error('Intake document element not found');

        // Sync user notes textarea into a clean print container for high-fidelity canvas snapshot
        const notesTextarea = document.getElementById('intake-user-notes');
        let tempNotesDiv = document.getElementById('intake-notes-print-div');
        if (!tempNotesDiv && notesTextarea) {
            tempNotesDiv = document.createElement('div');
            tempNotesDiv.id = 'intake-notes-print-div';
            tempNotesDiv.className = 'intake-notes-print-display';
            notesTextarea.parentNode.insertBefore(tempNotesDiv, notesTextarea.nextSibling);
        }
        
        const userNotesVal = (notesTextarea && notesTextarea.value.trim()) 
            ? notesTextarea.value.trim() 
            : 'No additional notes entered by patient.';
            
        if (tempNotesDiv && notesTextarea) {
            tempNotesDiv.textContent = userNotesVal;
            notesTextarea.style.display = 'none';
            tempNotesDiv.style.display = 'block';
        }

        const dateStr = new Date().toISOString().slice(0, 10);
        const filename = `Clinical_Intake_Summary_${dateStr}.pdf`;

        const opt = {
            margin: [8, 8, 8, 8],
            filename: filename,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true, letterRendering: true, logging: false },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
            pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
        };

        if (window.html2pdf) {
            await html2pdf().set(opt).from(docElement).save();
        } else {
            window.print();
        }

        // Restore textarea display
        if (tempNotesDiv && notesTextarea) {
            notesTextarea.style.display = 'block';
            tempNotesDiv.style.display = 'none';
        }

        if (downloadBtn) {
            downloadBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span>✓ PDF Downloaded!</span>
            `;
            setTimeout(() => {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = origBtnContent;
            }, 2500);
        }
    } catch (err) {
        console.error('PDF generation error:', err);
        alert('Could not generate PDF directly. Opening print dialog as fallback.');
        window.print();
        if (downloadBtn) {
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = origBtnContent;
        }
    }
}

/**
 * Trigger print dialog
 */
function printIntakeSummary() {
    window.print();
}

/**
 * Copy plain text intake summary to clipboard
 */
function copyIntakeSummaryText(btn) {
    const docElement = document.getElementById('intake-document');
    if (!docElement) return;

    const userNotesVal = (document.getElementById('intake-user-notes') || {}).value || '';
    let textToCopy = `PATIENT PRE-CONSULTATION INTAKE SUMMARY\n`;
    textToCopy += `Generated: ${new Date().toLocaleString()}\n`;
    textToCopy += `----------------------------------------\n\n`;
    textToCopy += docElement.innerText.trim();

    if (userNotesVal.trim()) {
        textToCopy += `\n\nADDITIONAL PATIENT NOTES:\n${userNotesVal.trim()}`;
    }

    navigator.clipboard.writeText(textToCopy).then(() => {
        const origText = btn.innerHTML;
        btn.innerHTML = `<span>✓ Copied Text!</span>`;
        setTimeout(() => {
            btn.innerHTML = origText;
        }, 2000);
    }).catch(() => {
        alert('Could not copy to clipboard.');
    });
}

/**
 * ============================================================================
 * INTERACTIVE 2D VISUAL BODY MAP (SYMPTOM LOCATOR) CONTROLLER
 * ============================================================================
 */

const BODY_REGIONS_DATA = {
    head: {
        title: "Head, Brain & Neurological",
        icon: "🧠",
        category: "neurological",
        desc: "Forehead, temples, skull, cranial nerves, and neurological pathways:",
        symptoms: [
            { name: "Throbbing Migraine", query: "What causes throbbing migraine headaches and how to manage them?" },
            { name: "Tension Headache", query: "What are symptoms and relief techniques for tension headaches?" },
            { name: "Sinus Pressure & Pain", query: "How to relieve sinus pressure and forehead pain?" },
            { name: "Vertigo & Spinning", query: "What causes vertigo and dizziness when moving head?" },
            { name: "Brain Fog & Fatigue", query: "What are common causes of brain fog and mental fatigue?" }
        ]
    },
    throat: {
        title: "Neck, Sinuses & Throat",
        icon: "🧣",
        category: "respiratory",
        desc: "Throat, vocal cords, tonsils, and upper airway passages:",
        symptoms: [
            { name: "Sore Throat & Pain", query: "What are remedies for severe sore throat and pain swallowing?" },
            { name: "Post-Nasal Drip", query: "How to manage post-nasal drip and tickling throat cough?" },
            { name: "Swollen Tonsils / Exudate", query: "What are signs of tonsillitis and strep throat?" },
            { name: "Hoarse Voice / Laryngitis", query: "How to recover voice from laryngitis and vocal strain?" }
        ]
    },
    chest: {
        title: "Chest, Lungs & Heart",
        icon: "🫁",
        category: "respiratory",
        desc: "Lungs, bronchial tubes, heart rhythm, and ribcage:",
        symptoms: [
            { name: "Persistent Bronchial Cough", query: "What causes persistent chest cough with phlegm?" },
            { name: "Wheezing & Asthma Signs", query: "What are symptoms of asthma flare-up and prevention?" },
            { name: "Chest Tightness & Deep Breath Ache", query: "What causes chest tightness when breathing deeply?" },
            { name: "Heart Flutter / Palpitations", query: "What causes heart palpitations and fluttering in chest?" }
        ]
    },
    abdomen: {
        title: "Abdomen & Stomach (Digestive)",
        icon: "🥣",
        category: "gastrointestinal",
        desc: "Stomach, upper GI, intestines, liver, and gallbladder:",
        symptoms: [
            { name: "Heartburn & Acid Reflux (GERD)", query: "What lifestyle changes help manage GERD and acid reflux?" },
            { name: "Stomach Cramping & Gas", query: "How to relieve stomach cramps, bloating, and excessive gas?" },
            { name: "Nausea & Food Poisoning", query: "What to do for acute nausea and food poisoning recovery?" },
            { name: "IBS & Irregular Bowels", query: "What are symptoms and dietary management for IBS?" }
        ]
    },
    pelvis: {
        title: "Pelvic, Bladder & Reproductive",
        icon: "🚻",
        category: "urological",
        desc: "Urinary bladder, kidneys, reproductive tract, and pelvic floor:",
        symptoms: [
            { name: "Burning Urination (UTI)", query: "What are symptoms of a urinary tract infection (UTI)?" },
            { name: "Flank Pain (Kidney Stones)", query: "What are warning signs and prevention for kidney stones?" },
            { name: "Severe Menstrual Cramps", query: "What helps relieve severe menstrual cramps (dysmenorrhea)?" },
            { name: "Overactive Bladder / Urgency", query: "How to manage overactive bladder and frequent nighttime urination?" }
        ]
    },
    arms: {
        title: "Shoulders, Arms & Wrists",
        icon: "💪",
        category: "musculoskeletal",
        desc: "Shoulder rotator cuff, elbows, wrists, and hand nerves:",
        symptoms: [
            { name: "Carpal Tunnel Tingling (Hands)", query: "What are symptoms and stretches for carpal tunnel syndrome?" },
            { name: "Frozen Shoulder & Stiffness", query: "What causes frozen shoulder and how to improve mobility?" },
            { name: "Tennis Elbow / Tendonitis", query: "What are recovery steps for tendonitis and elbow strain?" },
            { name: "Hand & Finger Joint Soreness", query: "What are signs of arthritis in finger and hand joints?" }
        ]
    },
    spine: {
        title: "Spine & Lower Back (Lumbar)",
        icon: "🦴",
        category: "musculoskeletal",
        desc: "Cervical spine, thoracic spine, lumbar discs, and sciatic nerve:",
        symptoms: [
            { name: "Lower Back Strain (Lumbar)", query: "What are safe exercises and relief for acute lower back strain?" },
            { name: "Sciatica Shooting Leg Pain", query: "How to relieve sciatica nerve pain radiating down the leg?" },
            { name: "Neck Stiffness & Tech Neck", query: "How to fix cervical neck stiffness from desk and screen posture?" }
        ]
    },
    shoulders: {
        title: "Shoulders & Upper Back",
        icon: "🥋",
        category: "musculoskeletal",
        desc: "Trapezius, rhomboids, upper spine, and shoulder blades:",
        symptoms: [
            { name: "Trapezius Muscle Spasms & Knots", query: "How to release tight upper back and trapezius muscle spasms?" },
            { name: "Rotator Cuff Tendon Soreness", query: "What are symptoms of rotator cuff strain in the shoulder?" }
        ]
    },
    hips: {
        title: "Hips & Gluteal Area",
        icon: "🦵",
        category: "musculoskeletal",
        desc: "Hip joint, piriformis, bursae, and pelvic alignment:",
        symptoms: [
            { name: "Hip Bursitis & Walking Ache", query: "What causes hip bursitis pain when walking or lying on side?" },
            { name: "Piriformis & Deep Glute Ache", query: "How to stretch the piriformis muscle for deep hip soreness?" }
        ]
    },
    knees: {
        title: "Knees & Joint Mobility",
        icon: "🦵",
        category: "musculoskeletal",
        desc: "Knee joints, cartilage, meniscus, and surrounding ligaments:",
        symptoms: [
            { name: "Knee Osteoarthritis & Grating", query: "What low-impact exercises help with knee osteoarthritis?" },
            { name: "Knee Swelling & Ligament Sprain", query: "What are recovery protocols for a mild knee sprain?" }
        ]
    },
    feet: {
        title: "Feet, Ankles & Heels",
        icon: "🦶",
        category: "musculoskeletal",
        desc: "Plantar fascia, Achilles tendon, ankle joint, and toes:",
        symptoms: [
            { name: "Plantar Fasciitis (Morning Heel Pain)", query: "What are the best stretches and footwear for plantar fasciitis?" },
            { name: "Ankle Sprain & Twist", query: "How to apply RICE protocol for an acute ankle sprain?" },
            { name: "Gout (Big Toe Swelling & Heat)", query: "What triggers gout attacks and what foods should be avoided?" },
            { name: "Athlete's Foot Peeling & Itch", query: "How to treat athlete's foot fungal infection on feet?" }
        ]
    },
    skin: {
        title: "Skin & Dermatological Health",
        icon: "🧴",
        category: "dermatology",
        desc: "Whole-body skin barrier, rashes, hives, and allergic reactions:",
        symptoms: [
            { name: "Eczema Dry Itchy Patches", query: "What skincare routine helps manage eczema flare-ups?" },
            { name: "Hives & Allergic Welts", query: "What causes sudden hives and when are they an emergency?" },
            { name: "Acne Breakouts & Red Bumps", query: "What is an effective gentle routine for acne vulgaris?" },
            { name: "Ringworm / Fungal Circular Rash", query: "How to identify and treat ringworm fungal skin rash?" }
        ]
    },
    general: {
        title: "General Wellness, Fever & Fatigue",
        icon: "🌡️",
        category: "fever_infection",
        desc: "Systemic symptoms, temperature regulation, sleep, and energy levels:",
        symptoms: [
            { name: "High Fever & Chills", query: "What are safe home care steps for managing a viral fever?" },
            { name: "Chronic Fatigue & Low Energy", query: "What are common medical reasons for unexplained daily fatigue?" },
            { name: "Insomnia & Trouble Sleeping", query: "What is evidence-based sleep hygiene to overcome insomnia?" },
            { name: "Dehydration & Lightheadedness", query: "What are key signs of dehydration and how to rehydrate safely?" }
        ]
    }
};

let currentBodyRegion = "head";

function openBodyMapModal() {
    openSymptomTriageHub('bodymap');
}

function closeBodyMapModal() {
    closeSymptomTriageHub();
}

function toggleBodyView(view) {
    const frontBtn = document.getElementById('bodymap-front-btn');
    const backBtn = document.getElementById('bodymap-back-btn');
    const frontGroup = document.getElementById('zones-front');
    const backGroup = document.getElementById('zones-back');

    if (view === 'front') {
        frontBtn.classList.add('active');
        backBtn.classList.remove('active');
        if (frontGroup) frontGroup.style.display = 'block';
        if (backGroup) backGroup.style.display = 'none';
    } else {
        backBtn.classList.add('active');
        frontBtn.classList.remove('active');
        if (frontGroup) frontGroup.style.display = 'none';
        if (backGroup) backGroup.style.display = 'block';
    }
}

function selectBodyRegion(regionId) {
    const data = BODY_REGIONS_DATA[regionId];
    if (!data) return;

    currentBodyRegion = regionId;

    // Update active class on SVG elements
    document.querySelectorAll('.body-zone').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.bodymap-global-chip').forEach(el => el.classList.remove('active'));

    const activeEl = document.getElementById(`zone-${regionId}`) || document.getElementById(`zone-back-${regionId}`);
    if (activeEl) {
        activeEl.classList.add('active');
    }

    // Update Drawer
    const iconEl = document.getElementById('drawer-region-icon');
    const titleEl = document.getElementById('drawer-region-title');
    const descEl = document.getElementById('drawer-region-desc');
    const container = document.getElementById('drawer-symptoms-container');
    const triageBtn = document.getElementById('bodymap-triage-btn');

    if (iconEl) iconEl.textContent = data.icon;
    if (titleEl) titleEl.textContent = data.title;
    if (descEl) descEl.textContent = data.desc;

    if (container) {
        const cardsHtml = data.symptoms.map(s => `
            <div class="bodymap-symptom-card" onclick="querySymptomFromBodyMap('${escapeHtml(s.query).replace(/'/g, "\\'")}')">
                <div>
                    <div class="bodymap-symptom-name">${escapeHtml(s.name)}</div>
                    <div class="bodymap-symptom-desc">Click to ask AI assistant for grounded care guidance</div>
                </div>
                <div class="bodymap-symptom-action-tag">💬 Ask AI →</div>
            </div>
        `).join('');
        container.innerHTML = cardsHtml;
    }

    if (triageBtn) {
        triageBtn.textContent = `🩺 Start Guided Triage for ${data.title.split(' ')[0]}`;
    }
}

function querySymptomFromBodyMap(queryText) {
    closeSymptomTriageHub();
    if (userInput) {
        userInput.value = queryText;
        chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
}

function launchTriageFromSelectedRegion() {
    const data = BODY_REGIONS_DATA[currentBodyRegion];
    const category = data ? data.category : "general";
    
    // Pre-select category in triage wizard & switch seamlessly inside hub
    triageAnswers.category = category;
    switchSymptomTriageTab('triage');
    renderTriageStep(1);
}

/**
 * ============================================================================
 * UNIFIED HEALTH HUB 2: MEDICATIONS, LABS & DIET HUB CONTROLLER
 * ============================================================================
 */

function openMedsLabsDietHub(tab = 'polypharmacy') {
    const hub = document.getElementById('meds-labs-diet-hub-modal') || document.getElementById('polypharmacy-modal');
    if (hub) {
        hub.classList.remove('hidden');
        switchMedsLabsDietTab(tab);
    }
}

function closeMedsLabsDietHub() {
    const hub = document.getElementById('meds-labs-diet-hub-modal') || document.getElementById('polypharmacy-modal');
    if (hub) hub.classList.add('hidden');
    const labModal = document.getElementById('lab-modal');
    if (labModal) labModal.classList.add('hidden');
    const nutModal = document.getElementById('nutrition-modal');
    if (nutModal) nutModal.classList.add('hidden');
}

function switchMedsLabsDietTab(tab) {
    const tabPoly = document.getElementById('mld-tab-poly');
    const tabLabs = document.getElementById('mld-tab-labs');
    const tabNut = document.getElementById('mld-tab-nutrition');

    const viewPoly = document.getElementById('mld-view-poly');
    const viewLabs = document.getElementById('mld-view-labs');
    const viewNut = document.getElementById('mld-view-nutrition');

    // Toggle tab pills
    if (tabPoly) tabPoly.classList.toggle('active', tab === 'polypharmacy');
    if (tabLabs) tabLabs.classList.toggle('active', tab === 'labs');
    if (tabNut) tabNut.classList.toggle('active', tab === 'nutrition');

    // Toggle views
    if (viewPoly) {
        viewPoly.style.display = (tab === 'polypharmacy') ? 'block' : 'none';
        viewPoly.classList.toggle('active', tab === 'polypharmacy');
    }
    if (viewLabs) {
        viewLabs.style.display = (tab === 'labs') ? 'block' : 'none';
        viewLabs.classList.toggle('active', tab === 'labs');
    }
    if (viewNut) {
        viewNut.style.display = (tab === 'nutrition') ? 'block' : 'none';
        viewNut.classList.toggle('active', tab === 'nutrition');
    }

    if (tab === 'polypharmacy') {
        renderPolySelectedTags();
        const input = document.getElementById('poly-drug-input');
        if (input) setTimeout(() => input.focus(), 150);
    } else if (tab === 'labs') {
        openLabModalInternal();
    } else if (tab === 'nutrition') {
        initNutritionTabInternal();
    }
}

function openPolypharmacyModal() {
    openMedsLabsDietHub('polypharmacy');
}

function closePolypharmacyModal() {
    closeMedsLabsDietHub();
}

function openLabModal() {
    openMedsLabsDietHub('labs');
}

function closeLabModal() {
    closeMedsLabsDietHub();
}

function openNutritionModal() {
    openMedsLabsDietHub('nutrition');
}

function closeNutritionModal() {
    closeMedsLabsDietHub();
}

window.attachedPolypharmacyResults = null;
let selectedPolyDrugs = [];
let currentPolyEvaluation = null;

function handlePolyInputKeydown(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        addDrugFromInput();
    }
}

function addDrugFromInput() {
    const input = document.getElementById('poly-drug-input');
    if (!input) return;
    const val = input.value.trim();
    if (!val) return;
    
    // Split by comma if user typed multiple
    const parts = val.split(',').map(p => p.trim()).filter(Boolean);
    parts.forEach(p => addDrugTag(p));
    input.value = '';
}

function addDrugTag(drugName) {
    if (!drugName) return;
    const formatted = drugName.trim();
    if (!selectedPolyDrugs.some(d => d.toLowerCase() === formatted.toLowerCase())) {
        selectedPolyDrugs.push(formatted);
        renderPolySelectedTags();
        evaluatePolypharmacy();
    }
}

function removeDrugTag(drugName) {
    selectedPolyDrugs = selectedPolyDrugs.filter(d => d.toLowerCase() !== drugName.toLowerCase());
    renderPolySelectedTags();
    evaluatePolypharmacy();
}

function clearPolypharmacyBasket() {
    selectedPolyDrugs = [];
    currentPolyEvaluation = null;
    renderPolySelectedTags();
    const resultsSection = document.getElementById('poly-results-section');
    if (resultsSection) {
        resultsSection.innerHTML = `
            <div class="poly-placeholder-state">
                <div class="poly-ph-icon">🛡️</div>
                <h4>Add at least 2 medications or conditions to evaluate interactions</h4>
                <p>Our clinical safety matrix checks over 50 major drug-drug, drug-condition, and drug-food contraindications.</p>
            </div>
        `;
    }
    const attachBtn = document.getElementById('poly-attach-btn');
    if (attachBtn) attachBtn.style.display = 'none';
}

function renderPolySelectedTags() {
    const container = document.getElementById('poly-tags-container');
    const countEl = document.getElementById('poly-count');
    if (countEl) countEl.textContent = selectedPolyDrugs.length;

    if (!container) return;

    if (selectedPolyDrugs.length === 0) {
        container.innerHTML = `<span class="poly-empty-hint">No items selected yet. Click quick tags above or type a medication name.</span>`;
        return;
    }

    container.innerHTML = selectedPolyDrugs.map(drug => `
        <span class="poly-tag">
            <span>${escapeHtml(drug)}</span>
            <button type="button" class="poly-tag-remove" onclick="removeDrugTag('${escapeHtml(drug).replace(/'/g, "\\'")}')" aria-label="Remove ${escapeHtml(drug)}">×</button>
        </span>
    `).join('');
}

async function evaluatePolypharmacy() {
    const resultsSection = document.getElementById('poly-results-section');
    const attachBtn = document.getElementById('poly-attach-btn');
    if (!resultsSection) return;

    if (selectedPolyDrugs.length < 2) {
        resultsSection.innerHTML = `
            <div class="poly-placeholder-state">
                <div class="poly-ph-icon">🛡️</div>
                <h4>Add at least 2 medications or conditions to evaluate interactions</h4>
                <p>Currently selected: ${selectedPolyDrugs.length === 1 ? escapeHtml(selectedPolyDrugs[0]) : 'None'}. Add another to screen pairwise combinations.</p>
            </div>
        `;
        if (attachBtn) attachBtn.style.display = 'none';
        return;
    }

    resultsSection.innerHTML = `
        <div style="text-align: center; padding: 24px; color: #64748b;">
            <div class="typing-indicator" style="justify-content: center; margin-bottom: 8px;">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
            <span>Evaluating ${selectedPolyDrugs.length} substances across clinical interaction matrix...</span>
        </div>
    `;

    try {
        const response = await fetch('/api/check-interactions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drugs: selectedPolyDrugs })
        });
        const data = await response.json();
        currentPolyEvaluation = data;

        if (data.interaction_count === 0) {
            resultsSection.innerHTML = `
                <div class="eli5-result-container">
                    <!-- Tier 1: Plain English Headline -->
                    <div class="eli5-headline-card safe">
                        <div class="eli5-headline-badge">🟢 Safe Combination</div>
                        <p class="eli5-headline-text">No high-risk pairwise interactions were detected between <strong>${selectedPolyDrugs.map(d => escapeHtml(d)).join(', ')}</strong> in the clinical database.</p>
                    </div>

                    <!-- Tier 2: 3 Clear Action Steps -->
                    <div class="eli5-actions-card">
                        <div class="eli5-actions-title">💡 3 Simple Steps You Can Take:</div>
                        <div class="eli5-action-item">
                            <div class="eli5-action-number">1</div>
                            <div><strong>Consistent Schedule:</strong> Take each medication at your regular prescribed time, following food or water instructions.</div>
                        </div>
                        <div class="eli5-action-item">
                            <div class="eli5-action-number">2</div>
                            <div><strong>Track Any Changes:</strong> Keep a quick note of how you feel whenever starting a new prescription or supplement.</div>
                        </div>
                        <div class="eli5-action-item">
                            <div class="eli5-action-number">3</div>
                            <div><strong>Pharmacist Double-Check:</strong> Mention all over-the-counter vitamins or herbals to your pharmacist during refills.</div>
                        </div>
                    </div>

                    <!-- Tier 3: Collapsible Doctor/Pharmacist Details -->
                    <details class="clinical-details-dropdown">
                        <summary>🩺 View Pharmacist & Clinical Details (Clearance & Metabolism)</summary>
                        <div class="clinical-details-content">
                            <p style="margin: 0 0 6px 0;"><strong>Evaluated Substances:</strong> ${selectedPolyDrugs.map(d => escapeHtml(d)).join(', ')}</p>
                            <p style="margin: 0 0 6px 0;"><strong>Safety Status:</strong> 0 Major / Moderate CYP450 or pharmacodynamic interactions identified.</p>
                            <p style="margin: 0; font-size: 0.72rem; color: #64748b;">Notice: Renal clearance, liver enzymes, and individual genetics may influence drug absorption. Always verify with your prescriber.</p>
                        </div>
                    </details>
                </div>
            `;
            if (attachBtn) {
                attachBtn.style.display = 'inline-flex';
                attachBtn.textContent = '📄 Attach to Doctor PDF';
                attachBtn.disabled = false;
            }
            return;
        }

        const highestSev = (data.highest_severity || 'moderate').toLowerCase();
        const sevColorClass = highestSev === 'major' ? 'high' : 'moderate';
        const sevBadgeText = highestSev === 'major' ? '🔴 High-Risk Interaction Alert' : '🟡 Moderate Interaction Alert';

        const cardsHtml = data.interactions.map(item => {
            const sevClass = item.severity.toLowerCase();
            return `
                <div class="poly-interaction-card card-${sevClass}" style="margin-bottom: 8px;">
                    <div class="poly-int-header">
                        <span class="poly-int-pair">⚠️ ${escapeHtml(item.drug_a)} + ${escapeHtml(item.drug_b)}</span>
                        <span class="poly-severity-pill badge-${sevClass}">${escapeHtml(item.severity.toUpperCase())} RISK</span>
                    </div>
                    <div class="poly-int-effect">
                        <strong>Potential Mechanism:</strong> ${escapeHtml(item.effect)}
                    </div>
                    <div class="poly-int-recommendation">
                        <strong>Clinical Action:</strong> ${escapeHtml(item.clinical_recommendation)}
                    </div>
                    ${item.evidence ? `
                        <div class="poly-int-evidence">
                            Evidence Grounding: ${escapeHtml(item.evidence)}
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');

        resultsSection.innerHTML = `
            <div class="eli5-result-container">
                <!-- Tier 1: Plain English Headline -->
                <div class="eli5-headline-card ${sevColorClass}">
                    <div class="eli5-headline-badge">${sevBadgeText}</div>
                    <p class="eli5-headline-text">We found <strong>${data.interaction_count} potential interaction(s)</strong> among your selected medications. These may affect absorption or increase side effects.</p>
                </div>

                <!-- Tier 2: 3 Clear Action Steps -->
                <div class="eli5-actions-card">
                    <div class="eli5-actions-title">💡 3 Simple Steps You Can Take:</div>
                    <div class="eli5-action-item">
                        <div class="eli5-action-number">1</div>
                        <div><strong>Do Not Stop Abruptly:</strong> Continue your prescribed medicines unless your physician or pharmacist tells you to change them.</div>
                    </div>
                    <div class="eli5-action-item">
                        <div class="eli5-action-number">2</div>
                        <div><strong>Watch for Symptoms:</strong> Pay attention to dizziness, unusual fatigue, stomach irritation, or heart fluttering.</div>
                    </div>
                    <div class="eli5-action-item">
                        <div class="eli5-action-number">3</div>
                        <div><strong>Call Your Doctor or Pharmacist:</strong> Show them this interaction summary to ask about separating doses or adjusting timing.</div>
                    </div>
                </div>

                <!-- Tier 3: Collapsible Doctor/Pharmacist Details -->
                <details class="clinical-details-dropdown" open>
                    <summary>🩺 View Doctor & Pharmacist Details (Interaction Matrix & Citations)</summary>
                    <div class="clinical-details-content">
                        ${cardsHtml}
                    </div>
                </details>
            </div>
        `;

        if (attachBtn) {
            attachBtn.style.display = 'inline-flex';
            attachBtn.textContent = '📄 Attach to Doctor PDF';
            attachBtn.disabled = false;
        }

    } catch (err) {
        console.error('Polypharmacy check error:', err);
        resultsSection.innerHTML = `
            <div style="padding: 16px; color: #b91c1c; background: #fee2e2; border-radius: 10px;">
                ⚠️ Could not evaluate interactions at this time. Please ensure the backend server is running.
            </div>
        `;
    }
}

function attachPolypharmacyToDoctorSummary() {
    if (!currentPolyEvaluation) return;
    window.attachedPolypharmacyResults = currentPolyEvaluation;
    const attachBtn = document.getElementById('poly-attach-btn');
    if (attachBtn) {
        attachBtn.textContent = '✓ Attached to Doctor PDF!';
        attachBtn.disabled = true;
    }
}

function discussPolypharmacyInChat() {
    closePolypharmacyModal();
    if (selectedPolyDrugs.length === 0) return;
    const query = `Can you provide a clinical safety breakdown and precautions for taking these together: ${selectedPolyDrugs.join(', ')}?`;
    if (userInput) {
        userInput.value = query;
        chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
}

/**
 * ============================================================================
 * MEDICAL LAB TEST & BIOMARKER RANGE INTERPRETER CONTROLLER
 * ============================================================================
 */

window.attachedLabResults = [];
let cachedLabDefs = null;
let currentLabPanel = 'metabolic';
let currentLabKey = 'fasting_blood_glucose';
let currentLabInterpretation = null;
let labDebounceTimer = null;

async function openLabModalInternal() {
    if (!cachedLabDefs) {
        await fetchLabDefinitions();
    }
    populateLabSelect(currentLabPanel);
}

async function fetchLabDefinitions() {
    try {
        const response = await fetch('/api/lab-tests');
        const data = await response.json();
        cachedLabDefs = data.panels || {};
    } catch (err) {
        console.error('Failed to load lab definitions:', err);
    }
}

function switchLabPanel(panelKey, tabElement) {
    currentLabPanel = panelKey;
    document.querySelectorAll('.lab-tab-pill').forEach(el => el.classList.remove('active'));
    if (tabElement) tabElement.classList.add('active');
    populateLabSelect(panelKey);
}

function populateLabSelect(panelKey) {
    const select = document.getElementById('lab-test-select');
    if (!select || !cachedLabDefs || !cachedLabDefs[panelKey]) return;

    const tests = cachedLabDefs[panelKey].tests || {};
    const testKeys = Object.keys(tests);

    select.innerHTML = testKeys.map(key => `
        <option value="${key}">${escapeHtml(tests[key].name)} (${escapeHtml(tests[key].unit)})</option>
    `).join('');

    if (testKeys.length > 0) {
        currentLabKey = testKeys[0];
        select.value = currentLabKey;
        onLabTestSelected(currentLabKey);
    }
}

function onLabTestSelected(testKey) {
    currentLabKey = testKey;
    const testData = getTestData(testKey);
    if (!testData) return;

    const val1Input = document.getElementById('lab-val-input');
    const val2Group = document.getElementById('lab-val2-group');
    const unitTag = document.getElementById('lab-unit-tag');
    const valLabel = document.getElementById('lab-val-label');
    const targetLabel = document.getElementById('gauge-target-label');
    const minLabel = document.getElementById('gauge-min-label');
    const maxLabel = document.getElementById('gauge-max-label');

    if (testKey === 'blood_pressure') {
        if (valLabel) valLabel.textContent = 'Systolic (mmHg):';
        if (val2Group) val2Group.style.display = 'flex';
        const val2Input = document.getElementById('lab-val2-input');
        if (val1Input) val1Input.value = '120';
        if (val2Input) val2Input.value = '80';
        if (unitTag) unitTag.textContent = 'mmHg';
    } else {
        if (valLabel) valLabel.textContent = 'Your Lab Value:';
        if (val2Group) val2Group.style.display = 'none';
        if (val1Input) val1Input.value = testData.default_val;
        if (unitTag) unitTag.textContent = testData.unit;
    }

    if (targetLabel) targetLabel.textContent = `Target: ${testData.optimal_target || 'Normal Range'}`;
    if (minLabel) minLabel.textContent = `Min (${testData.min_gauge || '0'})`;
    if (maxLabel) maxLabel.textContent = `Max (${testData.max_gauge || '100'})`;

    evaluateCurrentLab();
}

function getTestData(testKey) {
    if (!cachedLabDefs) return null;
    for (const pKey in cachedLabDefs) {
        if (cachedLabDefs[pKey].tests && cachedLabDefs[pKey].tests[testKey]) {
            return cachedLabDefs[pKey].tests[testKey];
        }
    }
    return null;
}

function onLabValueChange() {
    clearTimeout(labDebounceTimer);
    labDebounceTimer = setTimeout(() => {
        evaluateCurrentLab();
    }, 200);
}

async function evaluateCurrentLab() {
    const val1Input = document.getElementById('lab-val-input');
    const val2Input = document.getElementById('lab-val2-input');
    const gaugePin = document.getElementById('gauge-pin');
    const reportCard = document.getElementById('lab-report-card');
    const attachBtn = document.getElementById('lab-attach-btn');

    if (!val1Input || !reportCard) return;

    const val1 = parseFloat(val1Input.value);
    const val2 = val2Input ? parseFloat(val2Input.value) : null;

    if (isNaN(val1)) return;

    try {
        const response = await fetch('/api/interpret-lab', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                test_key: currentLabKey,
                value: val1,
                value2: val2
            })
        });

        const data = await response.json();
        currentLabInterpretation = data;

        // Position dynamic visual gauge pin
        if (gaugePin && data.pin_percent !== undefined) {
            gaugePin.style.left = `${Math.max(4, Math.min(96, data.pin_percent))}%`;
        }

        // Map status tier styling
        const statusClass = (data.status || 'optimal').toLowerCase();
        let tierColor = 'safe';
        let statusIcon = '🟢';
        if (statusClass === 'borderline' || statusClass === 'moderate' || statusClass === 'low') {
            tierColor = 'moderate';
            statusIcon = '🟡';
        } else if (statusClass === 'elevated' || statusClass === 'high' || statusClass === 'critical') {
            tierColor = 'high';
            statusIcon = '🔴';
        }

        const causesList = (data.potential_causes || []).map(c => `<li>${escapeHtml(c)}</li>`).join('');
        const lifestyleList = (data.evidence_lifestyle || []).map(l => `<li>${escapeHtml(l)}</li>`).join('');
        const talkingList = (data.physician_talking_points || []).map(p => `<li><strong>•</strong> ${escapeHtml(p)}</li>`).join('');

        const action1 = (data.evidence_lifestyle && data.evidence_lifestyle[0]) ? escapeHtml(data.evidence_lifestyle[0]) : 'Maintain a balanced diet rich in whole foods and clean hydration.';
        const action2 = (data.evidence_lifestyle && data.evidence_lifestyle[1]) ? escapeHtml(data.evidence_lifestyle[1]) : 'Aim for 30 minutes of daily walking or physical activity aligned with your stamina.';
        const action3 = (data.physician_talking_points && data.physician_talking_points[0]) ? escapeHtml(data.physician_talking_points[0]) : 'Ask your doctor about the recommended retest interval for this biomarker.';

        reportCard.innerHTML = `
            <div class="eli5-result-container">
                <!-- Tier 1: Plain English Headline Card -->
                <div class="eli5-headline-card ${tierColor}">
                    <div class="eli5-headline-badge">${statusIcon} ${escapeHtml(data.status_label || data.status)}</div>
                    <p class="eli5-headline-text">
                        <strong>${escapeHtml(data.test_name)}</strong> is <strong>${data.value} ${escapeHtml(data.unit)}</strong> 
                        (Target Range: ${escapeHtml(data.optimal_target)}).
                    </p>
                </div>

                <!-- Tier 2: 3 Clear Action Steps -->
                <div class="eli5-actions-card">
                    <div class="eli5-actions-title">💡 3 Simple Steps You Can Take:</div>
                    <div class="eli5-action-item">
                        <div class="eli5-action-number">1</div>
                        <div><strong>Nutrition & Care:</strong> ${action1}</div>
                    </div>
                    <div class="eli5-action-item">
                        <div class="eli5-action-number">2</div>
                        <div><strong>Daily Habits:</strong> ${action2}</div>
                    </div>
                    <div class="eli5-action-item">
                        <div class="eli5-action-number">3</div>
                        <div><strong>Doctor Talking Point:</strong> ${action3}</div>
                    </div>
                </div>

                <!-- Tier 3: Collapsible Doctor Details -->
                <details class="clinical-details-dropdown">
                    <summary>🩺 View Doctor & Clinical Details (Standard Ranges, Causes & Talking Points)</summary>
                    <div class="clinical-details-content">
                        <div class="lab-detail-grid">
                            <div class="lab-detail-block">
                                <h5>Potential Clinical Causes</h5>
                                <ul>${causesList || '<li>Within standard reference limits.</li>'}</ul>
                            </div>
                            <div class="lab-detail-block">
                                <h5>Evidence-Based Nutrition & Care</h5>
                                <ul>${lifestyleList || '<li>Maintain balanced nutrition, adequate hydration, and active lifestyle.</li>'}</ul>
                            </div>
                        </div>
                        <div class="lab-talking-points" style="margin-top: 8px;">
                            <h5>Physician Talking Points</h5>
                            <ul style="list-style: none; padding: 0;">${talkingList}</ul>
                        </div>
                    </div>
                </details>
            </div>
        `;

        if (attachBtn) {
            attachBtn.textContent = '📄 Attach to Doctor PDF';
            attachBtn.disabled = false;
        }

    } catch (err) {
        console.error('Lab evaluation error:', err);
    }
}

function resetLabInputs() {
    onLabTestSelected(currentLabKey);
}

function attachLabToDoctorSummary() {
    if (!currentLabInterpretation) return;
    
    // Check if already in list, update if so, otherwise add
    const existingIndex = window.attachedLabResults.findIndex(l => l.test_key === currentLabInterpretation.test_key);
    if (existingIndex >= 0) {
        window.attachedLabResults[existingIndex] = currentLabInterpretation;
    } else {
        window.attachedLabResults.push(currentLabInterpretation);
    }

    const attachBtn = document.getElementById('lab-attach-btn');
    if (attachBtn) {
        attachBtn.textContent = `✓ Attached (${window.attachedLabResults.length} Lab${window.attachedLabResults.length > 1 ? 's' : ''} in PDF)`;
        attachBtn.disabled = true;
    }
}

function discussLabInChat() {
    closeLabModal();
    if (!currentLabInterpretation) return;
    const query = `Can you explain what a ${currentLabInterpretation.test_name} value of ${currentLabInterpretation.value} ${currentLabInterpretation.unit} indicates, and what questions I should prepare for my doctor?`;
    if (userInput) {
        userInput.value = query;
        chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
}

/**
 * ============================================================================
 * MEDICAL NUTRITION THERAPY & THERAPEUTIC DIET PRESCRIPTOR CONTROLLER
 * ============================================================================
 */

window.attachedNutritionPlan = null;
let selectedNutritionConditions = [];
let selectedDietaryPreferences = [];
let selectedNutritionMeds = [];
let currentNutritionEvaluation = null;

function initNutritionTabInternal() {
    renderNutritionConditionChips();
    renderDietaryPrefPills();
    renderNutritionMedTags();
}

function toggleNutritionCondition(conditionId) {
    if (!conditionId) return;
    const index = selectedNutritionConditions.indexOf(conditionId);
    if (index >= 0) {
        selectedNutritionConditions.splice(index, 1);
    } else {
        selectedNutritionConditions.push(conditionId);
    }
    renderNutritionConditionChips();
    evaluateNutritionPlan();
}

function renderNutritionConditionChips() {
    document.querySelectorAll('.nutrition-condition-chip').forEach(btn => {
        const id = btn.getAttribute('data-id');
        if (selectedNutritionConditions.includes(id)) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

function toggleDietaryPref(prefKey) {
    if (!prefKey) return;
    const index = selectedDietaryPreferences.indexOf(prefKey);
    if (index >= 0) {
        selectedDietaryPreferences.splice(index, 1);
    } else {
        selectedDietaryPreferences.push(prefKey);
    }
    renderDietaryPrefPills();
    if (selectedNutritionConditions.length > 0) {
        evaluateNutritionPlan();
    }
}

function renderDietaryPrefPills() {
    document.querySelectorAll('.nutrition-pref-pill').forEach(btn => {
        const pref = btn.getAttribute('data-pref');
        if (selectedDietaryPreferences.includes(pref)) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

function addNutritionMed() {
    const input = document.getElementById('nutrition-med-input');
    if (!input) return;
    const val = input.value.trim();
    if (!val) return;
    const parts = val.split(',').map(p => p.trim()).filter(Boolean);
    parts.forEach(p => {
        if (!selectedNutritionMeds.some(m => m.toLowerCase() === p.toLowerCase())) {
            selectedNutritionMeds.push(p);
        }
    });
    input.value = '';
    renderNutritionMedTags();
    if (selectedNutritionConditions.length > 0) {
        evaluateNutritionPlan();
    }
}

function quickAddNutritionMed(medName) {
    if (!medName) return;
    if (!selectedNutritionMeds.some(m => m.toLowerCase() === medName.toLowerCase())) {
        selectedNutritionMeds.push(medName);
        renderNutritionMedTags();
        if (selectedNutritionConditions.length > 0) {
            evaluateNutritionPlan();
        }
    }
}

function removeNutritionMed(medName) {
    selectedNutritionMeds = selectedNutritionMeds.filter(m => m.toLowerCase() !== medName.toLowerCase());
    renderNutritionMedTags();
    if (selectedNutritionConditions.length > 0) {
        evaluateNutritionPlan();
    }
}

function renderNutritionMedTags() {
    const basket = document.getElementById('nutrition-meds-basket');
    if (!basket) return;
    if (selectedNutritionMeds.length === 0) {
        basket.innerHTML = '<span class="empty-meds-text">No medications added</span>';
        return;
    }
    basket.innerHTML = selectedNutritionMeds.map(m => `
        <span class="nutrition-med-tag">
            <span>💊 ${escapeHtml(m)}</span>
            <span class="nutrition-med-tag-remove" onclick="removeNutritionMed('${escapeHtml(m).replace(/'/g, "\\'")}')" aria-label="Remove medication">×</span>
        </span>
    `).join('');
}

function resetNutritionForm() {
    selectedNutritionConditions = [];
    selectedDietaryPreferences = [];
    selectedNutritionMeds = [];
    currentNutritionEvaluation = null;
    renderNutritionConditionChips();
    renderDietaryPrefPills();
    renderNutritionMedTags();
    const container = document.getElementById('nutrition-results-container');
    if (container) {
        container.innerHTML = `
            <div class="nutrition-placeholder-state">
                <div class="nutrition-ph-icon">🥗</div>
                <h4>Select at least one condition above to generate your clinical nutrition plan</h4>
                <p>Our Medical Nutrition Therapy prescriptor balances multi-disease conflicts, calculates daily macro/micronutrient goals, and curates customized food lists.</p>
            </div>
        `;
    }
    const attachBtn = document.getElementById('nutrition-attach-btn');
    if (attachBtn) attachBtn.style.display = 'none';
}

async function evaluateNutritionPlan() {
    const container = document.getElementById('nutrition-results-container');
    const attachBtn = document.getElementById('nutrition-attach-btn');
    if (!container) return;

    if (selectedNutritionConditions.length === 0) {
        container.innerHTML = `
            <div class="nutrition-placeholder-state">
                <div class="nutrition-ph-icon">🥗</div>
                <h4>Select at least one condition above to generate your clinical nutrition plan</h4>
                <p>Our Medical Nutrition Therapy prescriptor balances multi-disease conflicts, calculates daily macro/micronutrient goals, and curates customized food lists.</p>
            </div>
        `;
        if (attachBtn) attachBtn.style.display = 'none';
        return;
    }

    container.innerHTML = `
        <div style="text-align: center; padding: 24px; color: #64748b;">
            <div class="typing-indicator" style="justify-content: center; margin-bottom: 8px;">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
            <span>Generating evidence-based Medical Nutrition Therapy protocol & resolving conflicts...</span>
        </div>
    `;

    try {
        const response = await fetch('/api/nutrition-recommendation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                conditions: selectedNutritionConditions,
                dietary_preferences: selectedDietaryPreferences,
                active_medications: selectedNutritionMeds
            })
        });

        const data = await response.json();
        currentNutritionEvaluation = data;
        renderNutritionResults(data);

        if (attachBtn) {
            attachBtn.style.display = 'inline-flex';
            attachBtn.textContent = '📄 Attach to Doctor PDF';
            attachBtn.disabled = false;
        }
    } catch (err) {
        console.error('Nutrition evaluation error:', err);
        container.innerHTML = `
            <div style="padding: 16px; color: #b91c1c; background: #fee2e2; border-radius: 10px;">
                ⚠️ Could not generate nutrition recommendation. Please ensure the backend server is running.
            </div>
        `;
    }
}

function renderNutritionResults(data) {
    const container = document.getElementById('nutrition-results-container');
    if (!container) return;

    // 1. Conflict Alerts
    let conflictHtml = '';
    if (data.has_conflicts && data.conflict_resolutions && data.conflict_resolutions.length > 0) {
        const cItems = data.conflict_resolutions.map(c => `
            <div style="margin-top: 4px;">
                <strong>⚖️ Conflict: ${escapeHtml(c.conflict)}</strong>
                <div>${escapeHtml(c.resolution)}</div>
            </div>
        `).join('');
        conflictHtml = `
            <div class="nutrition-conflict-alert" style="margin-bottom: 8px;">
                <div style="font-weight: 700; font-size: 0.82rem; margin-bottom: 2px;">Multi-Condition Dietary Conflict Reconciled</div>
                ${cItems}
            </div>
        `;
    }

    // 2. Food-Drug Warnings
    let drugWarningsHtml = '';
    if (data.has_drug_interactions && data.food_drug_interactions && data.food_drug_interactions.length > 0) {
        const dItems = data.food_drug_interactions.map(d => `
            <div style="margin-top: 4px;">
                <strong>⚠️ ${escapeHtml(d.drug)} + ${escapeHtml(d.food_nutrient)}</strong>: ${escapeHtml(d.warning)}
                <div style="font-size: 0.72rem; opacity: 0.85; margin-top: 2px;">Clinical Management: ${escapeHtml(d.action)}</div>
            </div>
        `).join('');
        drugWarningsHtml = `
            <div class="nutrition-drug-warning" style="margin-bottom: 8px;">
                <div style="font-weight: 700; font-size: 0.82rem; margin-bottom: 2px;">Food-Drug Interaction Precautions</div>
                ${dItems}
            </div>
        `;
    }

    // 3. Macronutrient & Mineral Target Cards
    let macroCardsHtml = '';
    if (data.macro_targets && Object.keys(data.macro_targets).length > 0) {
        const cards = Object.entries(data.macro_targets).map(([k, v]) => `
            <div class="nutrition-macro-card">
                <div class="macro-label">${escapeHtml(k.replace(/_/g, ' '))}</div>
                <div class="macro-val">${escapeHtml(v)}</div>
            </div>
        `).join('');
        macroCardsHtml = `<div class="nutrition-macro-grid" style="margin-bottom: 8px;">${cards}</div>`;
    }

    // 4. Two-Column Food Selection Matrix
    const prioritizeItems = (data.prioritize_foods || []).map(f => `
        <div class="food-list-item">
            <span style="color: #16a34a; flex-shrink: 0;">✓</span>
            <span>${escapeHtml(f)}</span>
        </div>
    `).join('');

    const avoidItems = (data.avoid_foods || []).map(f => `
        <div class="food-list-item">
            <span style="color: #dc2626; flex-shrink: 0;">✗</span>
            <span>${escapeHtml(f)}</span>
        </div>
    `).join('');

    const foodMatrixHtml = `
        <div class="nutrition-food-matrix" style="margin-bottom: 8px;">
            <div class="food-column-prioritize">
                <div class="food-column-title">
                    <span>🟢</span>
                    <span>Therapeutic Foods to Prioritize</span>
                </div>
                ${prioritizeItems || '<div class="empty-meds-text">No specific food priorities recorded.</div>'}
            </div>
            <div class="food-column-avoid">
                <div class="food-column-title">
                    <span>🔴</span>
                    <span>Foods to Strictly Avoid / Limit</span>
                </div>
                ${avoidItems || '<div class="empty-meds-text">No strict food exclusions recorded.</div>'}
            </div>
        </div>
    `;

    // 5. 1-Day Sample Meal Blueprint
    let mealBlueprintHtml = '';
    if (data.sample_meal_blueprint) {
        const b = data.sample_meal_blueprint;
        mealBlueprintHtml = `
            <div style="margin-top: 8px;">
                <div style="font-size: 0.82rem; font-weight: 700; color: var(--text-primary); margin-bottom: 6px;">🍽️ 1-Day Evidence-Based Sample Meal Blueprint</div>
                <div class="nutrition-blueprint-grid">
                    <div class="meal-plan-card">
                        <div class="meal-plan-header"><span>🌅</span><span>Breakfast</span></div>
                        <div class="meal-plan-desc">${escapeHtml(b.breakfast || 'Nutrient-dense breakfast aligned with targets.')}</div>
                    </div>
                    <div class="meal-plan-card">
                        <div class="meal-plan-header"><span>☀️</span><span>Lunch</span></div>
                        <div class="meal-plan-desc">${escapeHtml(b.lunch || 'Balanced high-fiber lunch.')}</div>
                    </div>
                    <div class="meal-plan-card">
                        <div class="meal-plan-header"><span>🌙</span><span>Dinner</span></div>
                        <div class="meal-plan-desc">${escapeHtml(b.dinner || 'Lean protein & vegetable-focused dinner.')}</div>
                    </div>
                    <div class="meal-plan-card">
                        <div class="meal-plan-header"><span>🍎</span><span>Snacks</span></div>
                        <div class="meal-plan-desc">${escapeHtml(b.snacks || 'Low glycemic, mineral-rich snack.')}</div>
                    </div>
                </div>
            </div>
        `;
    }

    // 6. Clinical Summary & Footnote
    const summaryHtml = `
        <div style="background: #f8fafc; border: 1px solid var(--border); border-radius: 10px; padding: 10px 14px; font-size: 0.78rem; color: var(--text-secondary); margin-top: 8px;">
            <strong style="color: var(--text-primary);">Clinical Strategy:</strong> ${escapeHtml(data.clinical_summary || '')}
        </div>
    `;

    const footnoteHtml = `
        <div class="nutrition-guideline-footer" style="margin-top: 8px;">
            Conforms to clinical consensus: ${escapeHtml(data.guidelines_reference || 'ADA, AHA, KDIGO, ACG, ESPEN guidelines')} &bull; Educational nutrition therapy only.
        </div>
    `;

    // Extract Top 3 Action steps from food lists
    const topFoods = (data.prioritize_foods || []).slice(0, 3).map(f => f.split('(')[0].trim()).join(', ');
    const topAvoid = (data.avoid_foods || []).slice(0, 3).map(f => f.split('(')[0].trim()).join(', ');
    const appliedLabel = (data.conditions_applied && data.conditions_applied.length > 0) ? data.conditions_applied.map(c => c.replace(/_/g, ' ')).join(', ') : 'Your Health Profile';

    container.innerHTML = `
        <div class="eli5-result-container">
            <!-- Tier 1: Plain English Headline Card -->
            <div class="eli5-headline-card safe">
                <div class="eli5-headline-badge">🥗 Personalized Nutrition Therapy Protocol Ready</div>
                <p class="eli5-headline-text">
                    Customized meal plan and nutrient targets calculated for: <strong>${escapeHtml(appliedLabel)}</strong>${data.has_conflicts ? ' (all dietary conflicts reconciled)' : ''}.
                </p>
            </div>

            <!-- Tier 2: 3 Clear Action Steps -->
            <div class="eli5-actions-card">
                <div class="eli5-actions-title">💡 3 Simple Steps You Can Take:</div>
                <div class="eli5-action-item">
                    <div class="eli5-action-number">1</div>
                    <div><strong>Add These to Your Plate:</strong> Focus daily meals on <strong>${escapeHtml(topFoods || 'whole vegetables, lean proteins, and fiber')}</strong>.</div>
                </div>
                <div class="eli5-action-item">
                    <div class="eli5-action-number">2</div>
                    <div><strong>Limit or Swap:</strong> Minimize intake of <strong>${escapeHtml(topAvoid || 'ultra-processed foods and excess sodium')}</strong>.</div>
                </div>
                <div class="eli5-action-item">
                    <div class="eli5-action-number">3</div>
                    <div><strong>Stay Hydrated & Consistent:</strong> Follow the balanced 1-day meal structure below and drink adequate clean water daily.</div>
                </div>
            </div>

            <!-- Tier 3: Collapsible Nutritionist Details -->
            <details class="clinical-details-dropdown" open>
                <summary>🩺 View Clinical Nutritionist Details (Macros, Blueprint & Warnings)</summary>
                <div class="clinical-details-content">
                    ${conflictHtml}
                    ${drugWarningsHtml}
                    ${macroCardsHtml}
                    ${foodMatrixHtml}
                    ${mealBlueprintHtml}
                    ${summaryHtml}
                    ${footnoteHtml}
                </div>
            </details>
        </div>
    `;
}

function attachNutritionToDoctorSummary() {
    if (!currentNutritionEvaluation) return;
    window.attachedNutritionPlan = currentNutritionEvaluation;
    const attachBtn = document.getElementById('nutrition-attach-btn');
    if (attachBtn) {
        attachBtn.textContent = '✓ Attached to Doctor PDF!';
        attachBtn.disabled = true;
    }
}

function discussNutritionInChat() {
    closeNutritionModal();
    if (selectedNutritionConditions.length === 0) return;
    const condNames = selectedNutritionConditions.map(c => c.toUpperCase()).join(', ');
    const query = `Can you provide clinical nutrition guidance and evidence-based dietary recommendations for: ${condNames}?`;
    if (userInput) {
        userInput.value = query;
        chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
}

/**
 * ============================================================================
 * INTERACTIVE FIRST-AID & EMERGENCY ACTION FLASHCARDS CONTROLLER
 * ============================================================================
 */

let firstAidCatalog = [];
let firstAidCategories = {};
let currentFirstAidCard = null;
let currentFirstAidStepIdx = 0;
let activeFirstAidCategory = 'all';
window.attachedFirstAidIncident = null;

// CPR Web Audio Metronome State
let cprAudioCtx = null;
let cprMetronomeInterval = null;
let cprCompressionCount = 0;
let isCprMetronomePlaying = false;

async function openFirstAidModal(cardId = null) {
    const modal = document.getElementById('firstaid-modal');
    if (modal) {
        modal.classList.remove('hidden');
    }

    if (!firstAidCatalog || firstAidCatalog.length === 0) {
        await fetchFirstAidCatalog();
    }

    if (cardId) {
        await selectFirstAidCard(cardId);
    } else {
        backToFirstAidGrid();
    }
}

function closeFirstAidModal() {
    const modal = document.getElementById('firstaid-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
    stopCprMetronome();
}

async function fetchFirstAidCatalog() {
    try {
        const response = await fetch('/api/first-aid-cards');
        if (!response.ok) throw new Error('Failed to fetch first-aid catalog');
        const data = await response.json();
        firstAidCatalog = data.cards || [];
        firstAidCategories = data.categories || {};
        renderFirstAidGrid(firstAidCatalog);
    } catch (err) {
        console.error('Error loading first-aid catalog:', err);
    }
}

function renderFirstAidGrid(cardsList) {
    const grid = document.getElementById('firstaid-cards-grid');
    if (!grid) return;

    if (!cardsList || cardsList.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 36px 16px; color: var(--text-muted);">
                <div style="font-size: 2rem; margin-bottom: 8px;">🔍</div>
                <h4 style="margin-bottom: 4px; color: var(--text-secondary);">No matching emergency protocols found</h4>
                <p style="font-size: 0.8rem;">Try searching for CPR, choking, bleeding, burns, stroke, seizure, or fractures.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = cardsList.map(card => {
        const priorityClass = card.priority === 'CRITICAL' 
            ? 'card-priority-critical' 
            : (card.priority === 'URGENT' ? 'card-priority-urgent' : 'card-priority-standard');
        
        const badgeClass = card.priority === 'CRITICAL'
            ? 'badge-critical'
            : (card.priority === 'URGENT' ? 'badge-urgent' : 'badge-standard');

        return `
            <button type="button" class="firstaid-card-item ${priorityClass}" onclick="selectFirstAidCard('${escapeHtml(card.id)}')">
                <div class="card-item-top">
                    <span class="card-item-icon">${escapeHtml(card.icon || '🚑')}</span>
                    <span class="card-item-badge ${badgeClass}">${escapeHtml(card.priority || 'URGENT')}</span>
                </div>
                <div>
                    <h4 class="card-item-title">${escapeHtml(card.title)}</h4>
                    <p class="card-item-summary">${escapeHtml(card.summary || '')}</p>
                </div>
                <div class="card-item-footer">
                    <span class="card-item-steps-tag">⚡ ${card.step_count || (card.steps ? card.steps.length : 4)} Action Steps</span>
                    ${card.has_metronome ? '<span class="card-item-metronome-tag">⏱️ 110 BPM Metronome</span>' : `<span>${escapeHtml(card.category_label || '')}</span>`}
                </div>
            </button>
        `;
    }).join('');
}

function filterFirstAidCategory(catKey, tabElem) {
    activeFirstAidCategory = catKey;
    
    // Update active tab button style
    const tabs = document.querySelectorAll('.firstaid-tab-pill');
    tabs.forEach(t => t.classList.remove('active'));
    if (tabElem) {
        tabElem.classList.add('active');
    } else {
        const matchingTab = document.querySelector(`.firstaid-tab-pill[data-cat="${catKey}"]`);
        if (matchingTab) matchingTab.classList.add('active');
    }

    // Reset search bar value if changing category
    const searchInput = document.getElementById('firstaid-search-input');
    if (searchInput && searchInput.value) {
        searchInput.value = '';
        const clearBtn = document.getElementById('firstaid-search-clear');
        if (clearBtn) clearBtn.style.display = 'none';
    }

    if (catKey === 'all') {
        renderFirstAidGrid(firstAidCatalog);
    } else {
        const filtered = firstAidCatalog.filter(c => c.category === catKey);
        renderFirstAidGrid(filtered);
    }
}

function onFirstAidSearch(query) {
    const cleanQ = (query || '').trim().toLowerCase();
    const clearBtn = document.getElementById('firstaid-search-clear');
    if (clearBtn) {
        clearBtn.style.display = cleanQ ? 'block' : 'none';
    }

    if (!cleanQ) {
        filterFirstAidCategory(activeFirstAidCategory);
        return;
    }

    const filtered = firstAidCatalog.filter(c => {
        return (c.title && c.title.toLowerCase().includes(cleanQ)) ||
               (c.summary && c.summary.toLowerCase().includes(cleanQ)) ||
               (c.category && c.category.toLowerCase().includes(cleanQ)) ||
               (c.id && c.id.toLowerCase().includes(cleanQ));
    });

    renderFirstAidGrid(filtered);
}

function clearFirstAidSearch() {
    const searchInput = document.getElementById('firstaid-search-input');
    if (searchInput) searchInput.value = '';
    const clearBtn = document.getElementById('firstaid-search-clear');
    if (clearBtn) clearBtn.style.display = 'none';
    filterFirstAidCategory(activeFirstAidCategory);
}

async function selectFirstAidCard(cardId) {
    stopCprMetronome();

    try {
        const response = await fetch(`/api/first-aid-cards/${encodeURIComponent(cardId)}`);
        if (!response.ok) throw new Error('Failed to fetch card details');
        const data = await response.json();
        const card = data.card;
        if (!card) return;

        currentFirstAidCard = card;
        currentFirstAidStepIdx = 0;

        // Switch container view
        const gridView = document.getElementById('firstaid-grid-container');
        const viewerView = document.getElementById('firstaid-viewer-container');
        const viewAllBtn = document.getElementById('firstaid-view-all-btn');
        const attachBtn = document.getElementById('firstaid-attach-btn');

        if (gridView) gridView.style.display = 'none';
        if (viewerView) viewerView.style.display = 'flex';
        if (viewAllBtn) viewAllBtn.style.display = 'inline-flex';
        if (attachBtn) {
            attachBtn.style.display = 'inline-flex';
            attachBtn.textContent = '📄 Attach Protocol to Doctor PDF';
            attachBtn.disabled = false;
        }

        // Render Hero Tags & Title
        const tagsContainer = document.getElementById('firstaid-viewer-tags');
        if (tagsContainer) {
            const badgeClass = card.priority === 'CRITICAL' ? 'badge-critical' : (card.priority === 'URGENT' ? 'badge-urgent' : 'badge-standard');
            tagsContainer.innerHTML = `
                <span class="card-item-badge ${badgeClass}">${escapeHtml(card.priority || 'URGENT')}</span>
                <span style="font-size: 0.76rem; color: var(--text-muted); font-weight: 600;">${escapeHtml(card.category_label || '')}</span>
            `;
        }

        const heroContainer = document.getElementById('firstaid-card-hero');
        if (heroContainer) {
            heroContainer.innerHTML = `
                <div class="hero-title-row">
                    <span class="hero-title-icon">${escapeHtml(card.icon || '🚑')}</span>
                    <h3 class="hero-title-text">${escapeHtml(card.title)}</h3>
                </div>
                <p class="hero-summary-text">${escapeHtml(card.summary || '')}</p>
                ${card.call_emergency_first ? `
                    <div style="margin-top: 8px; font-size: 0.78rem; font-weight: 700; color: #b91c1c; background: #fee2e2; border: 1px solid #fecaca; border-radius: 6px; padding: 4px 10px; display: inline-flex; align-items: center; gap: 6px;">
                        🚨 Immediate Action: Call emergency services (911 / 112 / 999) before or while starting first aid.
                    </div>
                ` : ''}
            `;
        }

        // Render CPR Metronome Widget if card has metronome_bpm
        const cprCard = document.getElementById('cpr-metronome-card');
        if (cprCard) {
            if (card.metronome_bpm) {
                cprCard.style.display = 'flex';
                const bpmTitle = cprCard.querySelector('.cpr-bpm-title');
                if (bpmTitle) bpmTitle.textContent = `CPR Compression Rate: ${card.metronome_bpm} BPM`;
                const counter = document.getElementById('cpr-compression-counter');
                if (counter) counter.textContent = 'Clicks: 0';
            } else {
                cprCard.style.display = 'none';
            }
        }

        // Render Step 1
        renderFirstAidStep(0);

        // Render Critical DO NOTs & Clinical Guidelines in Tier 3 Accordion
        const donotContainer = document.getElementById('firstaid-donot-card');
        if (donotContainer) {
            const donots = card.critical_donots || [];
            const donotsHtml = donots.length > 0 
                ? donots.map(d => `<li class="donot-item"><span>🚫</span><span>${escapeHtml(d)}</span></li>`).join('')
                : '<li style="font-size: 0.78rem; color: #64748b;">No specific absolute contraindications recorded.</li>';

            donotContainer.style.display = 'block';
            donotContainer.innerHTML = `
                <details class="clinical-details-dropdown" open style="margin-top: 8px;">
                    <summary>🩺 View Paramedic & Clinical Details (Critical DO NOTs & Citations)</summary>
                    <div class="clinical-details-content">
                        <div class="donot-header" style="margin-bottom: 6px;">
                            <span>🔴</span>
                            <span style="font-weight: 700; color: #991b1b;">CRITICAL CLINICAL DO NOTS:</span>
                        </div>
                        <ul class="donot-list" style="margin-bottom: 8px;">
                            ${donotsHtml}
                        </ul>
                        <div class="calc-citation-footer" style="margin-top: 6px;">
                            Conforms to clinical consensus: ${escapeHtml(card.guideline_source || 'American Heart Association (AHA) & Red Cross First Aid Guidelines')}
                        </div>
                    </div>
                </details>
            `;
        }

    } catch (err) {
        console.error('Error selecting first-aid card:', err);
    }
}

function renderFirstAidStep(stepIdx) {
    if (!currentFirstAidCard || !currentFirstAidCard.steps) return;
    const steps = currentFirstAidCard.steps;
    const total = steps.length;
    if (stepIdx < 0 || stepIdx >= total) return;

    currentFirstAidStepIdx = stepIdx;
    const step = steps[stepIdx];

    // Update progress bar & badge
    const bar = document.getElementById('firstaid-step-bar');
    const badge = document.getElementById('firstaid-step-badge');
    if (bar) bar.style.width = `${Math.round(((stepIdx + 1) / total) * 100)}%`;
    if (badge) badge.textContent = `Step ${stepIdx + 1} of ${total}`;

    // Update Step Card Content
    const cardContent = document.getElementById('firstaid-step-card');
    if (cardContent) {
        cardContent.innerHTML = `
            <div class="step-head-row">
                <span class="step-num-circle">${step.step_num || (stepIdx + 1)}</span>
                <h4 class="step-title-text">${escapeHtml(step.title || `Step ${stepIdx + 1}`)}</h4>
            </div>
            <div class="step-action-desc">${escapeHtml(step.action || '')}</div>
            ${step.detail ? `<div class="step-detail-desc">${escapeHtml(step.detail)}</div>` : ''}
            ${step.visual_hint ? `
                <div class="step-visual-hint">
                    <span>👁️</span>
                    <span><strong>Visual Flow:</strong> ${escapeHtml(step.visual_hint)}</span>
                </div>
            ` : ''}
        `;
    }

    // Update Step Dots
    const dotsContainer = document.getElementById('firstaid-step-dots');
    if (dotsContainer) {
        dotsContainer.innerHTML = steps.map((_, i) => `
            <span class="step-dot ${i === stepIdx ? 'active' : ''}" onclick="renderFirstAidStep(${i})" title="Go to Step ${i + 1}"></span>
        `).join('');
    }

    // Update Nav Buttons
    const prevBtn = document.getElementById('firstaid-step-prev');
    const nextBtn = document.getElementById('firstaid-step-next');
    if (prevBtn) prevBtn.disabled = (stepIdx === 0);
    if (nextBtn) {
        if (stepIdx === total - 1) {
            nextBtn.textContent = 'Protocol Complete ✓';
            nextBtn.disabled = true;
        } else {
            nextBtn.textContent = 'Next Step →';
            nextBtn.disabled = false;
        }
    }
}

function prevFirstAidStep() {
    if (currentFirstAidStepIdx > 0) {
        renderFirstAidStep(currentFirstAidStepIdx - 1);
    }
}

function nextFirstAidStep() {
    if (currentFirstAidCard && currentFirstAidCard.steps && currentFirstAidStepIdx < currentFirstAidCard.steps.length - 1) {
        renderFirstAidStep(currentFirstAidStepIdx + 1);
    }
}

function backToFirstAidGrid() {
    stopCprMetronome();
    const gridView = document.getElementById('firstaid-grid-container');
    const viewerView = document.getElementById('firstaid-viewer-container');
    const viewAllBtn = document.getElementById('firstaid-view-all-btn');
    const attachBtn = document.getElementById('firstaid-attach-btn');

    if (gridView) gridView.style.display = 'block';
    if (viewerView) viewerView.style.display = 'none';
    if (viewAllBtn) viewAllBtn.style.display = 'none';
    if (attachBtn) attachBtn.style.display = 'none';

    renderFirstAidGrid(firstAidCatalog);
}

// CPR Audio/Visual 110 BPM Metronome Engine
function initCprAudio() {
    if (!cprAudioCtx) {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (AudioContextClass) {
            cprAudioCtx = new AudioContextClass();
        }
    }
    if (cprAudioCtx && cprAudioCtx.state === 'suspended') {
        cprAudioCtx.resume();
    }
}

function playCprBeep() {
    try {
        initCprAudio();
        if (!cprAudioCtx) return;

        const osc = cprAudioCtx.createOscillator();
        const gain = cprAudioCtx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, cprAudioCtx.currentTime); // 880 Hz crisp beep

        gain.gain.setValueAtTime(0.25, cprAudioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, cprAudioCtx.currentTime + 0.04); // 40ms short pulse

        osc.connect(gain);
        gain.connect(cprAudioCtx.destination);

        osc.start(cprAudioCtx.currentTime);
        osc.stop(cprAudioCtx.currentTime + 0.04);
    } catch (e) {
        console.warn('AudioContext playback error:', e);
    }
}

function toggleCprMetronome() {
    if (isCprMetronomePlaying) {
        stopCprMetronome();
    } else {
        startCprMetronome();
    }
}

function startCprMetronome() {
    initCprAudio();
    isCprMetronomePlaying = true;
    cprCompressionCount = 0;

    const btn = document.getElementById('cpr-audio-btn');
    const btnIcon = document.getElementById('cpr-btn-icon');
    const btnText = document.getElementById('cpr-btn-text');
    const heart = document.getElementById('cpr-pulse-heart');

    if (btn) btn.classList.add('active');
    if (btnIcon) btnIcon.textContent = '⏸';
    if (btnText) btnText.textContent = 'Pause Metronome';
    if (heart) heart.classList.add('pulsing');

    playCprBeep();
    cprCompressionCount++;
    const counter = document.getElementById('cpr-compression-counter');
    if (counter) counter.textContent = `Compressions: ${cprCompressionCount}`;

    // 110 BPM = 60,000 ms / 110 = 545.45 ms
    const bpmInterval = (60 / 110) * 1000;
    cprMetronomeInterval = setInterval(() => {
        playCprBeep();
        cprCompressionCount++;
        const cntEl = document.getElementById('cpr-compression-counter');
        if (cntEl) cntEl.textContent = `Compressions: ${cprCompressionCount}`;
    }, bpmInterval);
}

function stopCprMetronome() {
    if (cprMetronomeInterval) {
        clearInterval(cprMetronomeInterval);
        cprMetronomeInterval = null;
    }
    isCprMetronomePlaying = false;

    const btn = document.getElementById('cpr-audio-btn');
    const btnIcon = document.getElementById('cpr-btn-icon');
    const btnText = document.getElementById('cpr-btn-text');
    const heart = document.getElementById('cpr-pulse-heart');

    if (btn) btn.classList.remove('active');
    if (btnIcon) btnIcon.textContent = '▶';
    if (btnText) btnText.textContent = 'Start 110 BPM Metronome';
    if (heart) heart.classList.remove('pulsing');
}

function attachFirstAidToDoctorSummary() {
    if (!currentFirstAidCard) return;
    window.attachedFirstAidIncident = currentFirstAidCard;
    const attachBtn = document.getElementById('firstaid-attach-btn');
    if (attachBtn) {
        attachBtn.textContent = '✓ Attached to Doctor PDF!';
        attachBtn.disabled = true;
    }
}

function discussFirstAidInChat() {
    closeFirstAidModal();
    if (!currentFirstAidCard) return;
    const query = `Can you provide emergency first-aid advice and precautions for: ${currentFirstAidCard.title}?`;
    if (userInput) {
        userInput.value = query;
        chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
}

/**
 * ============================================================================
 * EVIDENCE-BASED CLINICAL RISK CALCULATORS & VITAL TOOLS CONTROLLER
 * ============================================================================
 */

window.attachedCalculatorReports = [];
let calculatorCatalogData = null;
let activeCalculatorId = "ascvd";
let activeCalculatorCategory = "all";
let currentCalculatorResult = null;

// Initial Default Values
let calcState = {
    ascvd: { age: 55, sex: "male", race: "white_other", sbp: 130, tc: 200, hdl: 50, diabetic: false, smoker: false, bp_treatment: false },
    chads_vasc: { age: 68, sex: "female", chf: false, htn: true, dm: true, stroke: false, vascular: false },
    egfr: { scr: 1.1, age: 55, sex: "male" },
    fib4: { age: 50, ast: 35, alt: 40, platelets: 220 },
    curb65: { confusion: false, bun: 16, rr: 20, sbp: 120, dbp: 80, age: 65 },
    wells_dvt: { cancer: false, paralysis: false, bedridden: false, tenderness: true, swollen_leg: true, calf_swelling: true, pitting: true, veins: false, prev_dvt: false, alt_diag: false },
    qsofa: { rr: 20, altered_mental: false, sbp: 110 },
    findrisc: { age: 48, bmi: 27.5, waist: 92, sex: "male", activity: true, veg: true, bp_meds: false, glucose_hx: false, fam_hx: "none" },
    phq9: { answers: [1, 1, 0, 1, 0, 0, 0, 0, 0] },
    gad7: { answers: [1, 1, 1, 0, 0, 0, 0] },
    anthropometrics: { weight_kg: 72, height_cm: 175, age: 32, sex: "male", activity: "moderate" }
};

async function openCalculatorModal(targetCalcId) {
    const modal = document.getElementById('calculator-modal');
    if (modal) {
        modal.classList.remove('hidden');
        if (!calculatorCatalogData) {
            await fetchCalculatorCatalog();
        }
        if (targetCalcId) {
            selectCalculator(targetCalcId);
        } else {
            selectCalculator(activeCalculatorId || 'ascvd');
        }
    }
}

function closeCalculatorModal() {
    const modal = document.getElementById('calculator-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

async function fetchCalculatorCatalog() {
    try {
        const res = await fetch('/api/calculators');
        const data = await res.json();
        if (data.success) {
            calculatorCatalogData = data;
            renderCalculatorDropdown();
        }
    } catch (err) {
        console.error('Error fetching calculator catalog:', err);
    }
}

function filterCalculatorCategory(category, element) {
    activeCalculatorCategory = category;
    document.querySelectorAll('.calc-category-tabs .calc-tab-pill').forEach(btn => btn.classList.remove('active'));
    if (element) element.classList.add('active');

    renderCalculatorDropdown();

    // Select the first calculator in this category if active calculator not in it
    if (calculatorCatalogData && calculatorCatalogData.calculators) {
        const filtered = (category === 'all') 
            ? calculatorCatalogData.calculators 
            : calculatorCatalogData.calculators.filter(c => c.category === category);
        if (filtered.length > 0 && !filtered.some(c => c.id === activeCalculatorId)) {
            selectCalculator(filtered[0].id);
        }
    }
}

function renderCalculatorDropdown() {
    if (!calculatorCatalogData || !calculatorCatalogData.calculators) return;
    const select = document.getElementById('calc-tool-select');
    if (!select) return;

    const filtered = (activeCalculatorCategory === 'all')
        ? calculatorCatalogData.calculators
        : calculatorCatalogData.calculators.filter(c => c.category === activeCalculatorCategory);

    select.innerHTML = filtered.map(c => `
        <option value="${c.id}" ${c.id === activeCalculatorId ? 'selected' : ''}>${c.icon} ${escapeHtml(c.title)}</option>
    `).join('');
}

function onCalculatorSelected(calcId) {
    selectCalculator(calcId);
}

function selectCalculator(calcId) {
    activeCalculatorId = calcId;
    const select = document.getElementById('calc-tool-select');
    if (select) select.value = calcId;

    // Update Header Tag / Description
    if (calculatorCatalogData && calculatorCatalogData.calculators) {
        const cdata = calculatorCatalogData.calculators.find(c => c.id === calcId);
        if (cdata) {
            const badgeEl = document.getElementById('calc-badge-chip');
            const descEl = document.getElementById('calc-info-desc');
            if (badgeEl) badgeEl.textContent = cdata.badge || 'Evidence-Based';
            if (descEl) descEl.textContent = cdata.description || '';
        }
    }

    renderCalculatorForm(calcId);
    runCalculatorComputation();
}

function renderCalculatorForm(calcId) {
    const container = document.getElementById('calc-form-container');
    if (!container) return;

    if (calcId === 'ascvd') {
        const s = calcState.ascvd;
        container.innerHTML = `
            <div class="calc-form-grid">
                <div class="calc-field-row">
                    <label class="calc-field-label">Age (20–79 yrs):</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" id="ascvd-age" value="${s.age}" min="20" max="79" oninput="updateAscvdParam('age', this.value)">
                        <span class="calc-unit-tag">years</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Biological Sex:</label>
                    <div class="calc-radio-group">
                        <button type="button" class="calc-radio-pill ${s.sex === 'male' ? 'active' : ''}" onclick="setAscvdSex('male')">Male</button>
                        <button type="button" class="calc-radio-pill ${s.sex === 'female' ? 'active' : ''}" onclick="setAscvdSex('female')">Female</button>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Race Demographic:</label>
                    <div class="calc-radio-group">
                        <button type="button" class="calc-radio-pill ${s.race === 'white_other' ? 'active' : ''}" onclick="setAscvdRace('white_other')">White / Other</button>
                        <button type="button" class="calc-radio-pill ${s.race === 'african_american' ? 'active' : ''}" onclick="setAscvdRace('african_american')">African American</button>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Systolic Blood Pressure:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" id="ascvd-sbp" value="${s.sbp}" min="90" max="200" oninput="updateAscvdParam('sbp', this.value)">
                        <span class="calc-unit-tag">mmHg</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Total Cholesterol:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" id="ascvd-tc" value="${s.tc}" min="130" max="320" oninput="updateAscvdParam('tc', this.value)">
                        <span class="calc-unit-tag">mg/dL</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">HDL Cholesterol:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" id="ascvd-hdl" value="${s.hdl}" min="20" max="100" oninput="updateAscvdParam('hdl', this.value)">
                        <span class="calc-unit-tag">mg/dL</span>
                    </div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 8px; margin-top: 12px;">
                <label class="calc-checkbox-item">
                    <input type="checkbox" id="ascvd-smoker" ${s.smoker ? 'checked' : ''} onchange="updateAscvdParam('smoker', this.checked)">
                    <span>Currently Smokes Tobacco</span>
                </label>
                <label class="calc-checkbox-item">
                    <input type="checkbox" id="ascvd-diabetic" ${s.diabetic ? 'checked' : ''} onchange="updateAscvdParam('diabetic', this.checked)">
                    <span>Diagnosed with Diabetes</span>
                </label>
                <label class="calc-checkbox-item">
                    <input type="checkbox" id="ascvd-bp-meds" ${s.bp_treatment ? 'checked' : ''} onchange="updateAscvdParam('bp_treatment', this.checked)">
                    <span>Taking Blood Pressure Medication</span>
                </label>
            </div>
        `;
    } else if (calcId === 'chads_vasc') {
        const s = calcState.chads_vasc;
        container.innerHTML = `
            <div class="calc-form-grid">
                <div class="calc-field-row">
                    <label class="calc-field-label">Patient Age:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" id="chads-age" value="${s.age}" min="18" max="105" oninput="updateChadsParam('age', this.value)">
                        <span class="calc-unit-tag">years</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Biological Sex:</label>
                    <div class="calc-radio-group">
                        <button type="button" class="calc-radio-pill ${s.sex === 'male' ? 'active' : ''}" onclick="setChadsSex('male')">Male</button>
                        <button type="button" class="calc-radio-pill ${s.sex === 'female' ? 'active' : ''}" onclick="setChadsSex('female')">Female (+1)</button>
                    </div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 8px; margin-top: 12px;">
                <label class="calc-checkbox-item">
                    <input type="checkbox" ${s.chf ? 'checked' : ''} onchange="updateChadsParam('chf', this.checked)">
                    <span>Congestive Heart Failure / LVEF ≤40% (+1)</span>
                </label>
                <label class="calc-checkbox-item">
                    <input type="checkbox" ${s.htn ? 'checked' : ''} onchange="updateChadsParam('htn', this.checked)">
                    <span>Hypertension (+1)</span>
                </label>
                <label class="calc-checkbox-item">
                    <input type="checkbox" ${s.dm ? 'checked' : ''} onchange="updateChadsParam('dm', this.checked)">
                    <span>Diabetes Mellitus (+1)</span>
                </label>
                <label class="calc-checkbox-item">
                    <input type="checkbox" ${s.stroke ? 'checked' : ''} onchange="updateChadsParam('stroke', this.checked)">
                    <span>Prior Stroke, TIA, or Thromboembolism (+2)</span>
                </label>
                <label class="calc-checkbox-item">
                    <input type="checkbox" ${s.vascular ? 'checked' : ''} onchange="updateChadsParam('vascular', this.checked)">
                    <span>Vascular Disease (MI, PAD, Aortic Plaque) (+1)</span>
                </label>
            </div>
        `;
    } else if (calcId === 'egfr') {
        const s = calcState.egfr;
        container.innerHTML = `
            <div class="calc-form-grid">
                <div class="calc-field-row">
                    <label class="calc-field-label">Serum Creatinine:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" id="egfr-scr" value="${s.scr}" min="0.2" max="15.0" step="0.05" oninput="updateEgfrParam('scr', this.value)">
                        <span class="calc-unit-tag">mg/dL</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Patient Age:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" id="egfr-age" value="${s.age}" min="18" max="110" oninput="updateEgfrParam('age', this.value)">
                        <span class="calc-unit-tag">years</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Biological Sex:</label>
                    <div class="calc-radio-group">
                        <button type="button" class="calc-radio-pill ${s.sex === 'male' ? 'active' : ''}" onclick="setEgfrSex('male')">Male</button>
                        <button type="button" class="calc-radio-pill ${s.sex === 'female' ? 'active' : ''}" onclick="setEgfrSex('female')">Female</button>
                    </div>
                </div>
            </div>
        `;
    } else if (calcId === 'fib4') {
        const s = calcState.fib4;
        container.innerHTML = `
            <div class="calc-form-grid">
                <div class="calc-field-row">
                    <label class="calc-field-label">Patient Age:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.age}" min="18" max="100" oninput="updateFib4Param('age', this.value)">
                        <span class="calc-unit-tag">years</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">AST Level:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.ast}" min="5" max="800" oninput="updateFib4Param('ast', this.value)">
                        <span class="calc-unit-tag">U/L</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">ALT Level:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.alt}" min="5" max="800" oninput="updateFib4Param('alt', this.value)">
                        <span class="calc-unit-tag">U/L</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Platelet Count:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.platelets}" min="10" max="800" oninput="updateFib4Param('platelets', this.value)">
                        <span class="calc-unit-tag">10⁹/L</span>
                    </div>
                </div>
            </div>
        `;
    } else if (calcId === 'curb65') {
        const s = calcState.curb65;
        container.innerHTML = `
            <div class="calc-form-grid">
                <div class="calc-field-row">
                    <label class="calc-field-label">Blood Urea Nitrogen (BUN):</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.bun}" min="2" max="100" oninput="updateCurbParam('bun', this.value)">
                        <span class="calc-unit-tag">mg/dL</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Respiratory Rate:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.rr}" min="8" max="60" oninput="updateCurbParam('rr', this.value)">
                        <span class="calc-unit-tag">breaths/min</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Systolic BP:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.sbp}" min="50" max="240" oninput="updateCurbParam('sbp', this.value)">
                        <span class="calc-unit-tag">mmHg</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Diastolic BP:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.dbp}" min="30" max="140" oninput="updateCurbParam('dbp', this.value)">
                        <span class="calc-unit-tag">mmHg</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Patient Age:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.age}" min="18" max="105" oninput="updateCurbParam('age', this.value)">
                        <span class="calc-unit-tag">years</span>
                    </div>
                </div>
            </div>
            <div style="margin-top: 10px;">
                <label class="calc-checkbox-item">
                    <input type="checkbox" ${s.confusion ? 'checked' : ''} onchange="updateCurbParam('confusion', this.checked)">
                    <span><strong>New Confusion / Disorientation</strong> (Abbreviated Mental Test Score ≤8) (+1)</span>
                </label>
            </div>
        `;
    } else if (calcId === 'wells_dvt') {
        const s = calcState.wells_dvt;
        container.innerHTML = `
            <div style="font-size: 0.78rem; color: #475569; margin-bottom: 8px;">Select all clinical features present:</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 8px;">
                <label class="calc-checkbox-item"><input type="checkbox" ${s.cancer ? 'checked' : ''} onchange="updateWellsParam('cancer', this.checked)"><span>Active cancer (within 6 months) (+1)</span></label>
                <label class="calc-checkbox-item"><input type="checkbox" ${s.paralysis ? 'checked' : ''} onchange="updateWellsParam('paralysis', this.checked)"><span>Paralysis, paresis, or recent leg plaster (+1)</span></label>
                <label class="calc-checkbox-item"><input type="checkbox" ${s.bedridden ? 'checked' : ''} onchange="updateWellsParam('bedridden', this.checked)"><span>Bedridden ≥3 days or major surgery within 12 wks (+1)</span></label>
                <label class="calc-checkbox-item"><input type="checkbox" ${s.tenderness ? 'checked' : ''} onchange="updateWellsParam('tenderness', this.checked)"><span>Localized deep vein tenderness (+1)</span></label>
                <label class="calc-checkbox-item"><input type="checkbox" ${s.swollen_leg ? 'checked' : ''} onchange="updateWellsParam('swollen_leg', this.checked)"><span>Entire leg swollen (+1)</span></label>
                <label class="calc-checkbox-item"><input type="checkbox" ${s.calf_swelling ? 'checked' : ''} onchange="updateWellsParam('calf_swelling', this.checked)"><span>Calf swelling >3 cm vs unaffected leg (+1)</span></label>
                <label class="calc-checkbox-item"><input type="checkbox" ${s.pitting ? 'checked' : ''} onchange="updateWellsParam('pitting', this.checked)"><span>Pitting edema confined to symptomatic leg (+1)</span></label>
                <label class="calc-checkbox-item"><input type="checkbox" ${s.veins ? 'checked' : ''} onchange="updateWellsParam('veins', this.checked)"><span>Collateral superficial non-varicose veins (+1)</span></label>
                <label class="calc-checkbox-item"><input type="checkbox" ${s.prev_dvt ? 'checked' : ''} onchange="updateWellsParam('prev_dvt', this.checked)"><span>Previously documented DVT (+1)</span></label>
                <label class="calc-checkbox-item" style="background: #fff7ed; border-color: #fdba74;"><input type="checkbox" ${s.alt_diag ? 'checked' : ''} onchange="updateWellsParam('alt_diag', this.checked)"><span>Alternative diagnosis at least as likely as DVT (-2)</span></label>
            </div>
        `;
    } else if (calcId === 'qsofa') {
        const s = calcState.qsofa;
        container.innerHTML = `
            <div class="calc-form-grid">
                <div class="calc-field-row">
                    <label class="calc-field-label">Respiratory Rate:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.rr}" min="8" max="60" oninput="updateQsofaParam('rr', this.value)">
                        <span class="calc-unit-tag">breaths/min</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Systolic Blood Pressure:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.sbp}" min="50" max="220" oninput="updateQsofaParam('sbp', this.value)">
                        <span class="calc-unit-tag">mmHg</span>
                    </div>
                </div>
            </div>
            <div style="margin-top: 10px;">
                <label class="calc-checkbox-item">
                    <input type="checkbox" ${s.altered_mental ? 'checked' : ''} onchange="updateQsofaParam('altered_mental', this.checked)">
                    <span><strong>Altered Mentation:</strong> Glasgow Coma Scale (GCS) < 15 (+1)</span>
                </label>
            </div>
        `;
    } else if (calcId === 'findrisc') {
        const s = calcState.findrisc;
        container.innerHTML = `
            <div class="calc-form-grid">
                <div class="calc-field-row">
                    <label class="calc-field-label">Age (years):</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.age}" min="18" max="100" oninput="updateFindriscParam('age', this.value)">
                        <span class="calc-unit-tag">yrs</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Body Mass Index (BMI):</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.bmi}" min="15" max="60" step="0.1" oninput="updateFindriscParam('bmi', this.value)">
                        <span class="calc-unit-tag">kg/m²</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Waist Circumference:</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.waist}" min="50" max="160" oninput="updateFindriscParam('waist', this.value)">
                        <span class="calc-unit-tag">cm</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Sex:</label>
                    <div class="calc-radio-group">
                        <button type="button" class="calc-radio-pill ${s.sex === 'male' ? 'active' : ''}" onclick="setFindriscSex('male')">Male</button>
                        <button type="button" class="calc-radio-pill ${s.sex === 'female' ? 'active' : ''}" onclick="setFindriscSex('female')">Female</button>
                    </div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 8px; margin-top: 10px;">
                <label class="calc-checkbox-item"><input type="checkbox" ${s.activity ? 'checked' : ''} onchange="updateFindriscParam('activity', this.checked)"><span>Physical activity ≥30 min daily (0 pts if checked)</span></label>
                <label class="calc-checkbox-item"><input type="checkbox" ${s.veg ? 'checked' : ''} onchange="updateFindriscParam('veg', this.checked)"><span>Eats vegetables/fruit daily (0 pts if checked)</span></label>
                <label class="calc-checkbox-item"><input type="checkbox" ${s.bp_meds ? 'checked' : ''} onchange="updateFindriscParam('bp_meds', this.checked)"><span>Taking High Blood Pressure Medication (+2)</span></label>
                <label class="calc-checkbox-item"><input type="checkbox" ${s.glucose_hx ? 'checked' : ''} onchange="updateFindriscParam('glucose_hx', this.checked)"><span>History of High Blood Glucose / Gestational (+5)</span></label>
            </div>
            <div style="margin-top: 8px;">
                <label class="calc-field-label">Family History of Diabetes:</label>
                <select class="calc-select" style="margin-top: 4px;" onchange="updateFindriscParam('fam_hx', this.value)">
                    <option value="none" ${s.fam_hx === 'none' ? 'selected' : ''}>No family history (0 pts)</option>
                    <option value="second_degree" ${s.fam_hx === 'second_degree' ? 'selected' : ''}>Grandparent, aunt, uncle, or cousin (+3 pts)</option>
                    <option value="first_degree" ${s.fam_hx === 'first_degree' ? 'selected' : ''}>Parent, sibling, or child (+5 pts)</option>
                </select>
            </div>
        `;
    } else if (calcId === 'phq9') {
        const questions = [
            "1. Little interest or pleasure in doing things",
            "2. Feeling down, depressed, or hopeless",
            "3. Trouble falling or staying asleep, or sleeping too much",
            "4. Feeling tired or having little energy",
            "5. Poor appetite or overeating",
            "6. Feeling bad about yourself — or that you are a failure",
            "7. Trouble concentrating on things (reading, watching TV)",
            "8. Moving or speaking so slowly that others have noticed, or being fidgety/restless",
            "9. Thoughts that you would be better off dead, or of hurting yourself"
        ];
        const answers = calcState.phq9.answers;
        container.innerHTML = `
            <div style="font-size: 0.78rem; color: #475569; margin-bottom: 8px;">Over the last 2 weeks, how often have you been bothered by any of the following?</div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                ${questions.map((q, idx) => `
                    <div style="background: #f8fafc; border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px; display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap;">
                        <span style="font-size: 0.78rem; font-weight: 600; color: ${idx === 8 ? '#b91c1c' : 'var(--text-primary)'}; flex: 1; min-width: 240px;">${escapeHtml(q)}</span>
                        <select class="calc-select" style="max-width: 180px; padding: 4px 8px; font-size: 0.78rem;" onchange="updatePhq9Answer(${idx}, this.value)">
                            <option value="0" ${answers[idx] == 0 ? 'selected' : ''}>0 - Not at all</option>
                            <option value="1" ${answers[idx] == 1 ? 'selected' : ''}>1 - Several days</option>
                            <option value="2" ${answers[idx] == 2 ? 'selected' : ''}>2 - More than half</option>
                            <option value="3" ${answers[idx] == 3 ? 'selected' : ''}>3 - Nearly every day</option>
                        </select>
                    </div>
                `).join('')}
            </div>
        `;
    } else if (calcId === 'gad7') {
        const questions = [
            "1. Feeling nervous, anxious, or on edge",
            "2. Not being able to stop or control worrying",
            "3. Worrying too much about different things",
            "4. Trouble relaxing",
            "5. Being so restless that it is hard to sit still",
            "6. Becoming easily annoyed or irritable",
            "7. Feeling afraid as if something awful might happen"
        ];
        const answers = calcState.gad7.answers;
        container.innerHTML = `
            <div style="font-size: 0.78rem; color: #475569; margin-bottom: 8px;">Over the last 2 weeks, how often have you been bothered by the following problems?</div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                ${questions.map((q, idx) => `
                    <div style="background: #f8fafc; border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px; display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap;">
                        <span style="font-size: 0.78rem; font-weight: 600; color: var(--text-primary); flex: 1; min-width: 240px;">${escapeHtml(q)}</span>
                        <select class="calc-select" style="max-width: 180px; padding: 4px 8px; font-size: 0.78rem;" onchange="updateGad7Answer(${idx}, this.value)">
                            <option value="0" ${answers[idx] == 0 ? 'selected' : ''}>0 - Not at all</option>
                            <option value="1" ${answers[idx] == 1 ? 'selected' : ''}>1 - Several days</option>
                            <option value="2" ${answers[idx] == 2 ? 'selected' : ''}>2 - More than half</option>
                            <option value="3" ${answers[idx] == 3 ? 'selected' : ''}>3 - Nearly every day</option>
                        </select>
                    </div>
                `).join('')}
            </div>
        `;
    } else if (calcId === 'anthropometrics') {
        const s = calcState.anthropometrics;
        container.innerHTML = `
            <div class="calc-form-grid">
                <div class="calc-field-row">
                    <label class="calc-field-label">Weight (kg):</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.weight_kg}" min="20" max="300" step="0.5" oninput="updateAnthroParam('weight_kg', this.value)">
                        <span class="calc-unit-tag">kg</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Height (cm):</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.height_cm}" min="80" max="250" oninput="updateAnthroParam('height_cm', this.value)">
                        <span class="calc-unit-tag">cm</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Age (years):</label>
                    <div class="calc-input-wrap">
                        <input type="number" class="calc-num-input" value="${s.age}" min="10" max="110" oninput="updateAnthroParam('age', this.value)">
                        <span class="calc-unit-tag">yrs</span>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Biological Sex:</label>
                    <div class="calc-radio-group">
                        <button type="button" class="calc-radio-pill ${s.sex === 'male' ? 'active' : ''}" onclick="setAnthroSex('male')">Male</button>
                        <button type="button" class="calc-radio-pill ${s.sex === 'female' ? 'active' : ''}" onclick="setAnthroSex('female')">Female</button>
                    </div>
                </div>
                <div class="calc-field-row">
                    <label class="calc-field-label">Activity Level (for TDEE):</label>
                    <select class="calc-select" onchange="updateAnthroParam('activity', this.value)">
                        <option value="sedentary" ${s.activity === 'sedentary' ? 'selected' : ''}>Sedentary (Little or no exercise)</option>
                        <option value="light" ${s.activity === 'light' ? 'selected' : ''}>Light (Exercise 1–3 days/wk)</option>
                        <option value="moderate" ${s.activity === 'moderate' ? 'selected' : ''}>Moderate (Exercise 3–5 days/wk)</option>
                        <option value="active" ${s.activity === 'active' ? 'selected' : ''}>Active (Exercise 6–7 days/wk)</option>
                        <option value="very_active" ${s.activity === 'very_active' ? 'selected' : ''}>Very Active (Intense training / labor)</option>
                    </select>
                </div>
            </div>
        `;
    }
}

// Param Update Helpers
function updateAscvdParam(k, v) { calcState.ascvd[k] = (typeof calcState.ascvd[k] === 'number') ? parseFloat(v) || 0 : v; runCalculatorComputation(); }
function setAscvdSex(s) { calcState.ascvd.sex = s; renderCalculatorForm('ascvd'); runCalculatorComputation(); }
function setAscvdRace(r) { calcState.ascvd.race = r; renderCalculatorForm('ascvd'); runCalculatorComputation(); }

function updateChadsParam(k, v) { calcState.chads_vasc[k] = (k === 'age') ? parseInt(v) || 0 : v; runCalculatorComputation(); }
function setChadsSex(s) { calcState.chads_vasc.sex = s; renderCalculatorForm('chads_vasc'); runCalculatorComputation(); }

function updateEgfrParam(k, v) { calcState.egfr[k] = parseFloat(v) || 0; runCalculatorComputation(); }
function setEgfrSex(s) { calcState.egfr.sex = s; renderCalculatorForm('egfr'); runCalculatorComputation(); }

function updateFib4Param(k, v) { calcState.fib4[k] = parseFloat(v) || 0; runCalculatorComputation(); }

function updateCurbParam(k, v) { calcState.curb65[k] = (typeof calcState.curb65[k] === 'number') ? parseFloat(v) || 0 : v; runCalculatorComputation(); }

function updateWellsParam(k, v) { calcState.wells_dvt[k] = v; runCalculatorComputation(); }

function updateQsofaParam(k, v) { calcState.qsofa[k] = (typeof calcState.qsofa[k] === 'number') ? parseInt(v) || 0 : v; runCalculatorComputation(); }

function updateFindriscParam(k, v) { calcState.findrisc[k] = (typeof calcState.findrisc[k] === 'number') ? parseFloat(v) || 0 : v; runCalculatorComputation(); }
function setFindriscSex(s) { calcState.findrisc.sex = s; renderCalculatorForm('findrisc'); runCalculatorComputation(); }

function updatePhq9Answer(idx, val) { calcState.phq9.answers[idx] = parseInt(val) || 0; runCalculatorComputation(); }
function updateGad7Answer(idx, val) { calcState.gad7.answers[idx] = parseInt(val) || 0; runCalculatorComputation(); }

function updateAnthroParam(k, v) { calcState.anthropometrics[k] = (typeof calcState.anthropometrics[k] === 'number') ? parseFloat(v) || 0 : v; runCalculatorComputation(); }
function setAnthroSex(s) { calcState.anthropometrics.sex = s; renderCalculatorForm('anthropometrics'); runCalculatorComputation(); }

async function runCalculatorComputation() {
    const payload = {
        calculator_id: activeCalculatorId,
        inputs: collectCalculatorInputs(activeCalculatorId)
    };

    try {
        const res = await fetch('/api/calculators/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        if (result.success && result.data) {
            currentCalculatorResult = result.data;
            renderCalculatorResult(activeCalculatorId, result.data);
        }
    } catch (err) {
        console.error('Computation error:', err);
    }
}

function collectCalculatorInputs(calcId) {
    if (calcId === 'ascvd') {
        const s = calcState.ascvd;
        return {
            age: s.age,
            sex: s.sex,
            race: s.race,
            systolic_bp: s.sbp,
            total_cholesterol: s.tc,
            hdl_cholesterol: s.hdl,
            is_diabetic: s.diabetic,
            is_smoker: s.smoker,
            on_hypertension_treatment: s.bp_treatment
        };
    } else if (calcId === 'chads_vasc') {
        const s = calcState.chads_vasc;
        return {
            age: s.age,
            is_female: s.sex === 'female',
            congestive_heart_failure: s.chf,
            hypertension: s.htn,
            diabetes: s.dm,
            stroke_or_tia: s.stroke,
            vascular_disease: s.vascular
        };
    } else if (calcId === 'egfr') {
        const s = calcState.egfr;
        return {
            serum_creatinine: s.scr,
            age: s.age,
            is_female: s.sex === 'female'
        };
    } else if (calcId === 'fib4') {
        const s = calcState.fib4;
        return { age: s.age, ast: s.ast, alt: s.alt, platelets: s.platelets };
    } else if (calcId === 'curb65') {
        const s = calcState.curb65;
        return {
            confusion: s.confusion,
            bun_mg_dl: s.bun,
            respiratory_rate: s.rr,
            systolic_bp: s.sbp,
            diastolic_bp: s.dbp,
            age: s.age
        };
    } else if (calcId === 'wells_dvt') {
        const s = calcState.wells_dvt;
        return {
            active_cancer: s.cancer,
            paralysis_or_plaster: s.paralysis,
            bedridden_or_major_surgery: s.bedridden,
            localized_tenderness: s.tenderness,
            entire_leg_swollen: s.swollen_leg,
            calf_swelling_over_3cm: s.calf_swelling,
            pitting_edema: s.pitting,
            collateral_superficial_veins: s.veins,
            previous_dvt: s.prev_dvt,
            alternative_diagnosis_likely: s.alt_diag
        };
    } else if (calcId === 'qsofa') {
        const s = calcState.qsofa;
        return { respiratory_rate: s.rr, altered_mentation: s.altered_mental, systolic_bp: s.sbp };
    } else if (calcId === 'findrisc') {
        const s = calcState.findrisc;
        return {
            age: s.age,
            bmi: s.bmi,
            waist_cm: s.waist,
            is_female: s.sex === 'female',
            physical_activity_daily: s.activity,
            vegetables_daily: s.veg,
            on_bp_medication: s.bp_meds,
            history_high_blood_glucose: s.glucose_hx,
            family_history_diabetes: s.fam_hx
        };
    } else if (calcId === 'phq9') {
        return { answers: calcState.phq9.answers };
    } else if (calcId === 'gad7') {
        return { answers: calcState.gad7.answers };
    } else if (calcId === 'anthropometrics') {
        const s = calcState.anthropometrics;
        return {
            weight_kg: s.weight_kg,
            height_cm: s.height_cm,
            age: s.age,
            is_female: s.sex === 'female',
            activity_level: s.activity
        };
    }
    return {};
}

function openClinicalRiskHub(targetCalcId) {
    openCalculatorModal(targetCalcId);
}

function closeClinicalRiskHub() {
    closeCalculatorModal();
}

function openCalmMentalHealthHub(category = 'somatic_pacers') {
    openMentalHealthModal(category);
}

function closeCalmMentalHealthHub() {
    closeMentalHealthModal();
}

function generateCalculatorEli5(calcId, data) {
    const tier = (data.tier || data.stage || '').toLowerCase();
    let tierClass = 'safe';
    let badgeIcon = '🟢';
    let headlineText = '';
    let action1 = '';
    let action2 = '';
    let action3 = '';

    if (calcId === 'ascvd') {
        const score = data.score;
        if (score < 5) {
            tierClass = 'safe';
            badgeIcon = '🟢';
            headlineText = `Your 10-year heart attack and stroke risk is very low (${score}%).`;
        } else if (score < 7.5) {
            tierClass = 'moderate';
            badgeIcon = '🟡';
            headlineText = `Your 10-year cardiovascular risk is borderline (${score}%).`;
        } else if (score < 20) {
            tierClass = 'moderate';
            badgeIcon = '🟡';
            headlineText = `Your 10-year cardiovascular risk is intermediate (${score}%).`;
        } else {
            tierClass = 'high';
            badgeIcon = '🔴';
            headlineText = `Your 10-year cardiovascular risk is elevated (${score}%).`;
        }
        action1 = '<strong>Heart-Healthy Nutrition:</strong> Focus on whole vegetables, fiber-rich legumes, olive oil, and limit saturated fats.';
        action2 = '<strong>Daily Activity:</strong> Aim for at least 150 minutes of moderate aerobic exercise (such as brisk walking) per week.';
        action3 = '<strong>Doctor Check:</strong> Discuss your blood pressure and cholesterol levels with your physician to evaluate if preventive statins are beneficial.';
    } else if (calcId === 'egfr') {
        const score = data.score;
        if (score >= 90) {
            tierClass = 'safe';
            badgeIcon = '🟢';
            headlineText = `Your kidneys are filtering waste at an optimal, healthy rate (${score} mL/min/1.73m² - Stage 1).`;
        } else if (score >= 60) {
            tierClass = 'safe';
            badgeIcon = '🟢';
            headlineText = `Kidney filtration is mildly decreased (${score} mL/min/1.73m² - Stage 2), typical with healthy aging.`;
        } else if (score >= 45) {
            tierClass = 'moderate';
            badgeIcon = '🟡';
            headlineText = `Mild to moderate kidney reduction noted (${score} mL/min/1.73m² - Stage 3a).`;
        } else if (score >= 30) {
            tierClass = 'moderate';
            badgeIcon = '🟡';
            headlineText = `Moderate to severe kidney strain noted (${score} mL/min/1.73m² - Stage 3b).`;
        } else {
            tierClass = 'high';
            badgeIcon = '🔴';
            headlineText = `Significant kidney function reduction (${score} mL/min/1.73m² - Stage ${data.stage || '4/5'}).`;
        }
        action1 = '<strong>Hydration:</strong> Drink adequate clean water throughout the day unless your physician has placed you on fluid limits.';
        action2 = '<strong>Medication Safety:</strong> Avoid frequent use of NSAID pain relievers (like ibuprofen or naproxen) which stress kidney filters.';
        action3 = '<strong>Routine Labs:</strong> Recheck your serum creatinine, eGFR, and urine protein at your next medical visit.';
    } else if (calcId === 'cha2ds2_vasc') {
        const score = data.score;
        if (score <= 1) {
            tierClass = 'safe';
            badgeIcon = '🟢';
            headlineText = `Your annual stroke risk from atrial fibrillation is very low (Score: ${score}).`;
        } else if (score === 2) {
            tierClass = 'moderate';
            badgeIcon = '🟡';
            headlineText = `Moderate stroke risk profile (Score: ${score}). Clinical guidelines suggest discussing prevention.`;
        } else {
            tierClass = 'high';
            badgeIcon = '🔴';
            headlineText = `Elevated stroke risk profile (Score: ${score}). Anticoagulation therapy is clinically recommended.`;
        }
        action1 = '<strong>Rhythm Awareness:</strong> Note and log any heart palpitations, skipped beats, or sudden fatigue.';
        action2 = '<strong>Blood Pressure Management:</strong> Keep daily home blood pressure readings within your target (under 130/80 mmHg).';
        action3 = '<strong>Cardiologist Review:</strong> Review anticoagulation (blood thinner) options and bleeding risk factors with your cardiologist.';
    } else if (calcId === 'fib4') {
        const score = data.score;
        if (score < 1.30) {
            tierClass = 'safe';
            badgeIcon = '🟢';
            headlineText = `Low probability of advanced liver fibrosis or scarring (FIB-4: ${score}).`;
        } else if (score <= 2.67) {
            tierClass = 'moderate';
            badgeIcon = '🟡';
            headlineText = `Indeterminate / borderline liver fibrosis risk (FIB-4: ${score}). Periodic monitoring advised.`;
        } else {
            tierClass = 'high';
            badgeIcon = '🔴';
            headlineText = `Elevated liver fibrosis index (FIB-4: ${score}). Clinical hepatology evaluation recommended.`;
        }
        action1 = '<strong>Metabolic Health:</strong> Minimize added sugars, eliminate alcohol consumption, and maintain a healthy weight.';
        action2 = '<strong>Supplement Caution:</strong> Review all herbal supplements and over-the-counter medicines for liver safety.';
        action3 = '<strong>Specialist Follow-Up:</strong> Ask your doctor if non-invasive liver imaging (like FibroScan elastography) is indicated.';
    } else if (calcId === 'wells_dvt' || calcId === 'wells_pe') {
        const isLow = (data.tier || '').toLowerCase().includes('low');
        tierClass = isLow ? 'safe' : 'high';
        badgeIcon = isLow ? '🟢' : '🔴';
        headlineText = isLow 
            ? `Low pre-test probability of blood clot (Score: ${data.score}).`
            : `Moderate to High pre-test probability of blood clot (Score: ${data.score}). Prompt medical evaluation is required.`;
        action1 = '<strong>Emergency Red Flags:</strong> Seek emergency hospital care immediately if you experience sudden shortness of breath or sharp chest pain.';
        action2 = '<strong>Avoid Immobility:</strong> Gently stretch and move legs; avoid prolonged sitting or tight leg wear.';
        action3 = '<strong>Diagnostic Confirmation:</strong> Follow through with recommended diagnostic imaging (Doppler ultrasound or D-dimer blood test).';
    } else if (calcId === 'curb65') {
        const score = data.score;
        if (score <= 1) {
            tierClass = 'safe';
            badgeIcon = '🟢';
            headlineText = `Low pneumonia severity score (${score}/5). Safe for outpatient home recovery with prescribed care.`;
        } else if (score === 2) {
            tierClass = 'moderate';
            badgeIcon = '🟡';
            headlineText = `Moderate pneumonia severity (${score}/5). Requires close medical supervision or short observation.`;
        } else {
            tierClass = 'high';
            badgeIcon = '🔴';
            headlineText = `High pneumonia severity (${score}/5). Requires immediate inpatient hospital care.`;
        }
        action1 = '<strong>Medication Adherence:</strong> Complete all prescribed antibiotic or antiviral courses exactly as directed by your doctor.';
        action2 = '<strong>Vitals Monitoring:</strong> Monitor oxygen saturation (SpO2) and body temperature twice daily.';
        action3 = '<strong>Urgent Warning:</strong> Call emergency services if you experience severe shortness of breath or bluish lips/fingers.';
    } else if (calcId === 'qsofa') {
        const score = data.score;
        if (score <= 1) {
            tierClass = 'safe';
            badgeIcon = '🟢';
            headlineText = `Low acute sepsis probability (qSOFA Score: ${score}/3). Bedside criteria not met.`;
        } else {
            tierClass = 'high';
            badgeIcon = '🔴';
            headlineText = `High acute infection / sepsis warning (qSOFA Score: ${score}/3). Immediate hospital evaluation needed.`;
        }
        action1 = '<strong>Emergency Action:</strong> If experiencing confusion, extreme shivering, or fast breathing, go to the nearest emergency department.';
        action2 = '<strong>Infection Source:</strong> Identify and treat underlying infection (urinary, respiratory, skin) with physician-directed therapy.';
        action3 = '<strong>Hospital Assessment:</strong> Full clinical assessment including blood cultures and lactate tests is strongly indicated.';
    } else if (calcId === 'findrisc') {
        const score = data.score;
        if (score < 12) {
            tierClass = 'safe';
            badgeIcon = '🟢';
            headlineText = `Your 10-year risk of developing Type 2 diabetes is low (${score}/26).`;
        } else if (score <= 14) {
            tierClass = 'moderate';
            badgeIcon = '🟡';
            headlineText = `Your 10-year risk of developing Type 2 diabetes is moderate (${score}/26 - ~1 in 6 chance).`;
        } else {
            tierClass = 'high';
            badgeIcon = '🔴';
            headlineText = `Your 10-year risk of developing Type 2 diabetes is elevated (${score}/26 - ~1 in 3 chance).`;
        }
        action1 = '<strong>Dietary Fiber:</strong> Increase daily intake of whole vegetables, berries, and legumes while swapping refined grains for whole grains.';
        action2 = '<strong>Daily Activity:</strong> Engage in at least 30 minutes of physical activity (brisk walking, cycling) every day.';
        action3 = '<strong>Blood Sugar Screening:</strong> Request a fasting blood glucose or HbA1c test during your next physician visit.';
    } else if (calcId === 'anthropometrics') {
        const bmi = data.bmi;
        if (bmi < 18.5) {
            tierClass = 'moderate';
            badgeIcon = '🟡';
            headlineText = `Your BMI (${bmi} kg/m²) is below the standard healthy weight range.`;
        } else if (bmi < 25) {
            tierClass = 'safe';
            badgeIcon = '🟢';
            headlineText = `Your BMI (${bmi} kg/m²) is in the optimal healthy weight range.`;
        } else if (bmi < 30) {
            tierClass = 'moderate';
            badgeIcon = '🟡';
            headlineText = `Your BMI (${bmi} kg/m²) is slightly above the ideal range.`;
        } else {
            tierClass = 'high';
            badgeIcon = '🔴';
            headlineText = `Your BMI (${bmi} kg/m²) is in the elevated range. Structured lifestyle support is recommended.`;
        }
        action1 = `<strong>Daily Caloric Target:</strong> Your estimated daily energy expenditure (TDEE) is ~${data.tdee_kcal_day || 2000} kcal/day for your activity level.`;
        action2 = '<strong>Balanced Nutrition:</strong> Emphasize lean proteins, fibrous vegetables, and moderate healthy fats for sustained energy.';
        action3 = '<strong>Doctor/Dietitian Guidance:</strong> Discuss your individual body composition and metabolic health goals with a healthcare provider.';
    } else {
        const score = data.score !== undefined ? data.score : '';
        tierClass = tier.includes('high') || tier.includes('severe') ? 'high' : (tier.includes('mod') ? 'moderate' : 'safe');
        badgeIcon = tierClass === 'high' ? '🔴' : (tierClass === 'moderate' ? '🟡' : '🟢');
        headlineText = `Assessment result: ${data.tier_label || data.stage || 'Completed'} (Score: ${score}).`;
        action1 = '<strong>Daily Self-Care:</strong> Practice evidence-based relaxation and maintain regular daily sleep and activity rhythms.';
        action2 = '<strong>Track Symptoms:</strong> Note any changes or persistent patterns over the next 1-2 weeks.';
        action3 = '<strong>Professional Review:</strong> Share these assessment findings with your healthcare provider or counselor for personalized guidance.';
    }

    return { badgeIcon, tierClass, headlineText, action1, action2, action3 };
}

function renderCalculatorResult(calcId, data) {
    const card = document.getElementById('calc-result-card');
    if (!card) return;

    // Reset modifier classes
    card.className = 'calc-result-card';
    const tierKey = (data.tier || '').toLowerCase();
    if (tierKey) card.classList.add(`risk-${tierKey}`);

    const badgeClass = `badge-${tierKey || 'normal'}`;

    // Generate Plain-Language 3-Tier ELI5 Breakdown
    const eli5 = generateCalculatorEli5(calcId, data);

    let scoreHtml = '';
    if (calcId === 'anthropometrics') {
        scoreHtml = `
            <div class="calc-result-header">
                <div>
                    <div style="font-size: 0.74rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Body Mass Index (BMI)</div>
                    <div class="calc-score-main">
                        <span class="calc-score-number">${data.bmi}</span>
                        <span class="calc-score-unit">kg/m²</span>
                    </div>
                </div>
                <div class="calc-tier-badge ${badgeClass}">${escapeHtml(data.bmi_label)}</div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; margin: 6px 0;">
                <div style="background: white; border: 1px solid var(--border); border-radius: 8px; padding: 6px 10px;">
                    <div style="font-size: 0.7rem; color: #64748b;">Ideal Weight (IBW)</div>
                    <strong style="font-size: 0.92rem; color: #0369a1;">${data.ideal_body_weight_kg} kg</strong>
                </div>
                <div style="background: white; border: 1px solid var(--border); border-radius: 8px; padding: 6px 10px;">
                    <div style="font-size: 0.7rem; color: #64748b;">Body Surface Area</div>
                    <strong style="font-size: 0.92rem; color: #0369a1;">${data.body_surface_area_m2} m²</strong>
                </div>
                <div style="background: white; border: 1px solid var(--border); border-radius: 8px; padding: 6px 10px;">
                    <div style="font-size: 0.7rem; color: #64748b;">Basal Metabolic Rate</div>
                    <strong style="font-size: 0.92rem; color: #0369a1;">${data.bmr_kcal_day} kcal</strong>
                </div>
                <div style="background: white; border: 1px solid var(--border); border-radius: 8px; padding: 6px 10px;">
                    <div style="font-size: 0.7rem; color: #64748b;">Daily TDEE (${data.activity_level})</div>
                    <strong style="font-size: 0.92rem; color: #166534;">${data.tdee_kcal_day} kcal</strong>
                </div>
            </div>
        `;
    } else {
        scoreHtml = `
            <div class="calc-result-header">
                <div>
                    <div style="font-size: 0.74rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Computed Risk Score</div>
                    <div class="calc-score-main">
                        <span class="calc-score-number">${data.score}</span>
                        <span class="calc-score-unit">${escapeHtml(data.score_unit || '')}</span>
                    </div>
                </div>
                <div class="calc-tier-badge ${badgeClass}">${escapeHtml(data.tier_label || data.stage || '')}</div>
            </div>
        `;
    }

    const recText = data.statin_recommendation || data.anticoagulation_recommendation || data.clinical_advice || data.recommendation || data.triage_recommendation || data.diagnostic_pathway || data.clinical_action || data.prevention_guideline || data.treatment_recommendation;

    const alertBanner = data.safety_warning ? `
        <div class="calc-alert-banner">
            <span>🚨</span>
            <span>${escapeHtml(data.safety_warning)}</span>
        </div>
    ` : '';

    const breakdownItems = (data.breakdown || []).map(b => `<div class="calc-param-chip">• ${escapeHtml(b)}</div>`).join('');

    card.innerHTML = `
        <div class="eli5-result-container">
            <!-- Tier 1: Plain English Headline Card -->
            <div class="eli5-headline-card ${eli5.tierClass}">
                <div class="eli5-headline-badge">${eli5.badgeIcon} ${escapeHtml(data.tier_label || data.stage || data.bmi_label || 'Calculated Result')}</div>
                <p class="eli5-headline-text">${eli5.headlineText}</p>
            </div>

            <!-- Tier 2: 3 Clear Action Steps -->
            <div class="eli5-actions-card">
                <div class="eli5-actions-title">💡 3 Simple Steps You Can Take:</div>
                <div class="eli5-action-item">
                    <div class="eli5-action-number">1</div>
                    <div>${eli5.action1}</div>
                </div>
                <div class="eli5-action-item">
                    <div class="eli5-action-number">2</div>
                    <div>${eli5.action2}</div>
                </div>
                <div class="eli5-action-item">
                    <div class="eli5-action-number">3</div>
                    <div>${eli5.action3}</div>
                </div>
            </div>

            <!-- Tier 3: Collapsible Doctor & Clinical Details -->
            <details class="clinical-details-dropdown">
                <summary>🩺 View Doctor & Clinical Details (Formulas, Citations & Biomarkers)</summary>
                <div class="clinical-details-content">
                    ${scoreHtml}
                    ${alertBanner}
                    ${recText ? `
                        <div class="calc-guideline-box" style="margin: 8px 0;">
                            <strong>Guideline Clinical Action:</strong> ${escapeHtml(recText)}
                        </div>
                    ` : ''}
                    ${breakdownItems ? `
                        <div class="calc-details-grid" style="margin: 8px 0;">
                            ${breakdownItems}
                        </div>
                    ` : ''}
                    <div class="calc-citation-footer" style="margin-top: 8px;">
                        Citations: ${escapeHtml(data.citations || 'Evidence-Based Clinical Guidelines')}
                    </div>
                </div>
            </details>
        </div>
    `;

    // Reset attach button state
    const attachBtn = document.getElementById('calc-attach-btn');
    if (attachBtn) {
        attachBtn.textContent = '📄 Attach to Doctor PDF';
        attachBtn.disabled = false;
    }
}

function resetActiveCalculator() {
    // Reset to defaults
    renderCalculatorForm(activeCalculatorId);
    runCalculatorComputation();
}

function attachCalculatorToDoctorSummary() {
    if (!currentCalculatorResult) return;
    
    // Add to list or replace existing of same ID
    const cid = currentCalculatorResult.calculator_id || activeCalculatorId;
    window.attachedCalculatorReports = window.attachedCalculatorReports.filter(r => (r.calculator_id || r.id) !== cid);
    window.attachedCalculatorReports.push(currentCalculatorResult);

    const attachBtn = document.getElementById('calc-attach-btn');
    if (attachBtn) {
        attachBtn.textContent = '✓ Attached to Doctor PDF!';
        attachBtn.disabled = true;
    }
}

function discussCalculatorInChat() {
    closeCalculatorModal();
    if (!currentCalculatorResult) return;
    const title = currentCalculatorResult.calculator_title || activeCalculatorId;
    const score = currentCalculatorResult.score !== undefined ? `${currentCalculatorResult.score} ${currentCalculatorResult.score_unit || ''}` : (currentCalculatorResult.bmi ? `BMI ${currentCalculatorResult.bmi}` : '');
    const query = `Can you explain my clinical risk score for ${title} (${score}) and what next steps I should discuss with my doctor?`;
    if (userInput) {
        userInput.value = query;
        chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
}

/**
 * ============================================================================
 * CLINICALLY VALIDATED MENTAL HEALTH & SOMATIC TOOLKITS CONTROLLER
 * ============================================================================
 */

window.attachedMentalHealthReports = window.attachedMentalHealthReports || [];

let mhCatalog = null;
let activeMhCategory = 'somatic_pacers';
let activeSomaticPacerId = 'box_breathing';
let activeMentalHealthScaleId = 'phq9';
let activeGroundingToolId = 'grounding_54321';
let currentMhScaleResult = null;

// Pacer State
let isBreathingPacerRunning = false;
let pacerTimer = null;
let pacerElapsedTimer = null;
let pacerElapsedSeconds = 0;
let pacerCycleCount = 0;
let pacerCurrentPhaseIdx = 0;
let pacerPhaseRemaining = 0;
let pacerAudioEnabled = true;
let pacerAudioCtx = null;

// Scale Answers State
const scaleAnswersState = {
    phq9: [0, 0, 0, 0, 0, 0, 0, 0, 0],
    gad7: [0, 0, 0, 0, 0, 0, 0],
    pc_ptsd5: [false, false, false, false, false],
    isi: [0, 0, 0, 0, 0, 0, 0],
    pss4: [0, 0, 0, 0],
    cage_aid: [false, false, false, false]
};

// Somatic Pacer Configurations
const SOMATIC_PACER_CONFIGS = {
    box_breathing: {
        title: "Box Breathing (4-4-4-4 Square Pacer)",
        badge: "Navy SEALs / Autonomic Balance",
        neuro: "Rhythmic square pacing equalizes baroreceptor firing, increases high-frequency HRV, and balances sympathetic-parasympathetic tone.",
        phases: [
            { name: "Inhale", duration: 4, instruction: "Slow, deep diaphragmatic inhalation through the nose...", ringClass: "inhale-state", icon: "🌬️", freq: 440 },
            { name: "Hold", duration: 4, instruction: "Gently hold your breath with lungs full without straining...", ringClass: "hold-full-state", icon: "⏸️", freq: 523.25 },
            { name: "Exhale", duration: 4, instruction: "Smooth, complete exhalation through the mouth...", ringClass: "exhale-state", icon: "💨", freq: 392 },
            { name: "Hold", duration: 4, instruction: "Rest quietly with lungs empty before the next breath...", ringClass: "hold-empty-state", icon: "🧘", freq: 329.63 }
        ]
    },
    relaxing_478: {
        title: "4-7-8 Parasympathetic Relaxing Breath",
        badge: "Dr. Andrew Weil / Vagal Brake",
        neuro: "Prolonged exhalation relative to inhalation engages the vagus nerve brake on the sinoatrial node, triggering acetylcholine release and cardiac deceleration.",
        phases: [
            { name: "Inhale", duration: 4, instruction: "Quietly inhale through the nose for 4 seconds...", ringClass: "inhale-state", icon: "🌬️", freq: 440 },
            { name: "Hold", duration: 7, instruction: "Hold your breath comfortably with lungs full for 7 seconds...", ringClass: "hold-full-state", icon: "⏸️", freq: 523.25 },
            { name: "Exhale", duration: 8, instruction: "Make a soft whoosh sound as you exhale completely for 8 seconds...", ringClass: "exhale-state", icon: "💨", freq: 349.23 }
        ]
    },
    physiological_sigh: {
        title: "Physiological Sigh (Rapid Autonomic Reset)",
        badge: "Stanford Neurobiology / Dr. Huberman",
        neuro: "The second micro-inhale pops open collapsed pulmonary alveoli, optimizing carbon dioxide offloading and activating parasympathetic vagal afferents.",
        phases: [
            { name: "Deep Inhale", duration: 2, instruction: "Deep inhalation through the nose filling 80% of lungs...", ringClass: "inhale-state", icon: "🌬️", freq: 440 },
            { name: "Top-Off Inhale", duration: 1, instruction: "Sharp second inhale to completely fill lungs and pop alveoli...", ringClass: "hold-full-state", icon: "➕", freq: 587.33 },
            { name: "Long Sigh", duration: 6, instruction: "Slow, relaxed sigh all the way out through your open mouth...", ringClass: "exhale-state", icon: "😮‍💨", freq: 329.63 }
        ]
    }
};

async function openMentalHealthModal(category = 'somatic_pacers') {
    const modal = document.getElementById('mental-health-modal');
    if (modal) modal.classList.remove('hidden');

    if (!mhCatalog) {
        try {
            const res = await fetch('/api/mental-health/tools');
            mhCatalog = await res.json();
        } catch (e) {
            console.error('Failed to load mental health catalog:', e);
        }
    }

    switchMentalHealthCategory(category);
}

function closeMentalHealthModal() {
    const modal = document.getElementById('mental-health-modal');
    if (modal) modal.classList.add('hidden');
    stopBreathingPacer();
}

function switchMentalHealthCategory(category, btnElem) {
    activeMhCategory = category;

    // Update tab pills
    document.querySelectorAll('.mh-tab-pill').forEach(btn => {
        if (btn.getAttribute('data-cat') === category || (btnElem && btn === btnElem)) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Hide all view sections
    const views = ['somatic_pacers', 'clinical_scales', 'grounding_pmr', 'crisis_safety'];
    views.forEach(v => {
        const el = document.getElementById(`mh-view-${v}`);
        if (el) el.style.display = (v === category) ? 'block' : 'none';
    });

    // Initialize specific view content
    if (category === 'somatic_pacers') {
        onSomaticPacerSelect(activeSomaticPacerId);
    } else if (category === 'clinical_scales') {
        onMentalHealthScaleSelect(activeMentalHealthScaleId);
    } else if (category === 'grounding_pmr') {
        onGroundingToolSelect(activeGroundingToolId);
    }
}

// -----------------------------------------------------------------------------
// Somatic Breathing Pacer & Web Audio Engine
// -----------------------------------------------------------------------------

function onSomaticPacerSelect(pacerId) {
    stopBreathingPacer();
    activeSomaticPacerId = pacerId;
    const cfg = SOMATIC_PACER_CONFIGS[pacerId] || SOMATIC_PACER_CONFIGS.box_breathing;

    const badge = document.getElementById('mh-pacer-badge');
    const neuro = document.getElementById('mh-neuro-text');
    const select = document.getElementById('mh-pacer-select');
    const nameEl = document.getElementById('mh-phase-name');
    const timerEl = document.getElementById('mh-phase-timer');
    const iconEl = document.getElementById('mh-phase-icon');
    const instructionEl = document.getElementById('mh-phase-instruction');
    const ring = document.getElementById('mh-breathing-ring');

    if (badge) badge.textContent = cfg.badge;
    if (neuro) neuro.textContent = cfg.neuro;
    if (select) select.value = pacerId;
    if (nameEl) nameEl.textContent = 'Ready';
    if (timerEl) timerEl.textContent = '0s';
    if (iconEl) iconEl.textContent = '🫁';
    if (instructionEl) instructionEl.textContent = `Click 'Start Breathing Pacer' to begin paced ${cfg.title}.`;
    if (ring) ring.className = 'mh-breathing-ring';
}

function togglePacerAudio() {
    pacerAudioEnabled = !pacerAudioEnabled;
    const btn = document.getElementById('mh-sound-btn');
    const icon = document.getElementById('mh-sound-icon');
    const label = document.getElementById('mh-sound-label');
    if (btn && icon && label) {
        icon.textContent = pacerAudioEnabled ? '🔊' : '🔇';
        label.textContent = `Audio Chimes: ${pacerAudioEnabled ? 'ON' : 'OFF'}`;
    }
}

function playPacerChime(frequency = 440, duration = 0.5) {
    if (!pacerAudioEnabled) return;
    try {
        if (!pacerAudioCtx) {
            pacerAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (pacerAudioCtx.state === 'suspended') {
            pacerAudioCtx.resume();
        }
        const osc = pacerAudioCtx.createOscillator();
        const gain = pacerAudioCtx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(frequency, pacerAudioCtx.currentTime);

        // Soft gentle bell chime envelope
        gain.gain.setValueAtTime(0.001, pacerAudioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.12, pacerAudioCtx.currentTime + 0.04);
        gain.gain.exponentialRampToValueAtTime(0.001, pacerAudioCtx.currentTime + duration);

        osc.connect(gain);
        gain.connect(pacerAudioCtx.destination);

        osc.start();
        osc.stop(pacerAudioCtx.currentTime + duration);
    } catch (e) {
        // AudioContext may be restricted by browser policy before user interaction
    }
}

function toggleBreathingPacer() {
    if (isBreathingPacerRunning) {
        stopBreathingPacer();
    } else {
        startBreathingPacer();
    }
}

function startBreathingPacer() {
    isBreathingPacerRunning = true;
    pacerCurrentPhaseIdx = 0;

    const btn = document.getElementById('mh-pacer-toggle-btn');
    if (btn) {
        btn.textContent = '⏸ Pause Breathing Pacer';
        btn.style.background = 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
    }

    // Start elapsed timer
    pacerElapsedTimer = setInterval(() => {
        pacerElapsedSeconds++;
        const mins = String(Math.floor(pacerElapsedSeconds / 60)).padStart(2, '0');
        const secs = String(pacerElapsedSeconds % 60).padStart(2, '0');
        const elTime = document.getElementById('mh-elapsed-time');
        if (elTime) elTime.textContent = `Time: ${mins}:${secs}`;
    }, 1000);

    runPacerPhase();
}

function runPacerPhase() {
    if (!isBreathingPacerRunning) return;

    const cfg = SOMATIC_PACER_CONFIGS[activeSomaticPacerId] || SOMATIC_PACER_CONFIGS.box_breathing;
    const phase = cfg.phases[pacerCurrentPhaseIdx];
    pacerPhaseRemaining = phase.duration;

    const ring = document.getElementById('mh-breathing-ring');
    const nameEl = document.getElementById('mh-phase-name');
    const timerEl = document.getElementById('mh-phase-timer');
    const iconEl = document.getElementById('mh-phase-icon');
    const instructionEl = document.getElementById('mh-phase-instruction');

    if (ring) ring.className = `mh-breathing-ring ${phase.ringClass}`;
    if (nameEl) nameEl.textContent = phase.name;
    if (timerEl) timerEl.textContent = `${pacerPhaseRemaining}s`;
    if (iconEl) iconEl.textContent = phase.icon;
    if (instructionEl) instructionEl.textContent = phase.instruction;

    playPacerChime(phase.freq, 0.6);

    clearInterval(pacerTimer);
    pacerTimer = setInterval(() => {
        pacerPhaseRemaining--;
        if (timerEl) timerEl.textContent = `${pacerPhaseRemaining}s`;

        if (pacerPhaseRemaining <= 0) {
            clearInterval(pacerTimer);
            pacerCurrentPhaseIdx++;

            // If completed full cycle
            if (pacerCurrentPhaseIdx >= cfg.phases.length) {
                pacerCurrentPhaseIdx = 0;
                pacerCycleCount++;
                const countEl = document.getElementById('mh-cycle-count');
                if (countEl) countEl.textContent = `Cycles: ${pacerCycleCount}`;
            }

            if (isBreathingPacerRunning) {
                runPacerPhase();
            }
        }
    }, 1000);
}

function stopBreathingPacer() {
    isBreathingPacerRunning = false;
    clearInterval(pacerTimer);
    clearInterval(pacerElapsedTimer);

    const btn = document.getElementById('mh-pacer-toggle-btn');
    if (btn) {
        btn.textContent = '▶ Start Breathing Pacer';
        btn.style.background = 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)';
    }

    const ring = document.getElementById('mh-breathing-ring');
    if (ring) ring.className = 'mh-breathing-ring';
}

function resetBreathingPacer() {
    stopBreathingPacer();
    pacerElapsedSeconds = 0;
    pacerCycleCount = 0;
    const countEl = document.getElementById('mh-cycle-count');
    const elTime = document.getElementById('mh-elapsed-time');
    if (countEl) countEl.textContent = 'Cycles: 0';
    if (elTime) elTime.textContent = 'Time: 00:00';
    onSomaticPacerSelect(activeSomaticPacerId);
}

// -----------------------------------------------------------------------------
// Clinical Assessment Scales & Questionnaires Engine
// -----------------------------------------------------------------------------

function onMentalHealthScaleSelect(scaleId) {
    activeMentalHealthScaleId = scaleId;
    renderScaleQuestionnaire(scaleId);
}

function renderScaleQuestionnaire(scaleId) {
    const container = document.getElementById('mh-questionnaire-card');
    const resultCard = document.getElementById('mh-scale-result-card');
    if (!container) return;

    if (resultCard) resultCard.style.display = 'none';

    let questions = [];
    let options = [];

    if (scaleId === 'phq9') {
        questions = [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling or staying asleep, or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
            "Trouble concentrating on things, such as reading the newspaper or watching television",
            "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual",
            "Thoughts that you would be better off dead or of hurting yourself in some way"
        ];
        options = [
            { val: 0, label: "0 - Not at all" },
            { val: 1, label: "1 - Several days" },
            { val: 2, label: "2 - More than half the days" },
            { val: 3, label: "3 - Nearly every day" }
        ];
    } else if (scaleId === 'gad7') {
        questions = [
            "Feeling nervous, anxious, or on edge",
            "Not being able to stop or control worrying",
            "Worrying too much about different things",
            "Trouble relaxing",
            "Being so restless that it's hard to sit still",
            "Becoming easily annoyed or irritable",
            "Feeling afraid as if something awful might happen"
        ];
        options = [
            { val: 0, label: "0 - Not at all" },
            { val: 1, label: "1 - Several days" },
            { val: 2, label: "2 - More than half the days" },
            { val: 3, label: "3 - Nearly every day" }
        ];
    } else if (scaleId === 'pc_ptsd5') {
        questions = [
            "Had nightmares about the event(s) or thought about the event(s) when you did not want to?",
            "Tried hard not to think about the event(s) or went out of your way to avoid situations that reminded you of the event(s)?",
            "Been constantly on guard, watchful, or easily startled?",
            "Felt numb or detached from people, activities, or your surroundings?",
            "Felt guilty or unable to stop blaming yourself or others for the event(s) or problems the event(s) may have caused?"
        ];
        options = [
            { val: false, label: "No" },
            { val: true, label: "Yes" }
        ];
    } else if (scaleId === 'isi') {
        questions = [
            "Difficulty falling asleep",
            "Difficulty staying asleep",
            "Problems waking up too early",
            "How SATISFIED/DISSATISFIED are you with your current sleep pattern?",
            "How NOTICEABLE to others do you think your sleep problem is?",
            "How WORRIED/DISTRESSED are you about your current sleep problem?",
            "To what extent does your sleep problem INTERFERE with your daily functioning?"
        ];
        options = [
            { val: 0, label: "0 - None / Very Satisfied" },
            { val: 1, label: "1 - Mild" },
            { val: 2, label: "2 - Moderate" },
            { val: 3, label: "3 - Severe" },
            { val: 4, label: "4 - Very Severe" }
        ];
    } else if (scaleId === 'pss4') {
        questions = [
            "In the last month, how often have you felt that you were unable to control the important things in your life?",
            "In the last month, how often have you felt confident about your ability to handle personal problems? (Reverse Scored)",
            "In the last month, how often have you felt that things were going your way? (Reverse Scored)",
            "In the last month, how often have you felt difficulties were piling up so high you could not overcome them?"
        ];
        options = [
            { val: 0, label: "0 - Never" },
            { val: 1, label: "1 - Almost Never" },
            { val: 2, label: "2 - Sometimes" },
            { val: 3, label: "3 - Fairly Often" },
            { val: 4, label: "4 - Very Often" }
        ];
    } else if (scaleId === 'cage_aid') {
        questions = [
            "Have you ever felt you ought to CUT DOWN on your drinking or drug use?",
            "Have people ANNOYED you by criticizing your drinking or drug use?",
            "Have you ever felt bad or GUILTY about your drinking or drug use?",
            "Have you ever had a drink or used drugs first thing in the morning to steady nerves (EYE-OPENER)?"
        ];
        options = [
            { val: false, label: "No" },
            { val: true, label: "Yes" }
        ];
    }

    const currentAnswers = scaleAnswersState[scaleId] || [];

    const rowsHtml = questions.map((q, qIdx) => {
        const currentVal = currentAnswers[qIdx];
        const optsHtml = options.map(opt => {
            const isChecked = (currentVal === opt.val);
            const inputVal = (typeof opt.val === 'boolean') ? (opt.val ? '1' : '0') : opt.val;
            return `
                <label class="mh-opt-label">
                    <input type="radio" name="mh-q-${scaleId}-${qIdx}" value="${inputVal}" ${isChecked ? 'checked' : ''} onchange="onScaleAnswerChange('${scaleId}', ${qIdx}, this.value)">
                    <span>${escapeHtml(opt.label)}</span>
                </label>
            `;
        }).join('');

        return `
            <div class="mh-question-row">
                <div class="mh-question-text">${qIdx + 1}. ${escapeHtml(q)}</div>
                <div class="mh-options-row">
                    ${optsHtml}
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-size: 0.8rem; color: #64748b; font-weight: 700;">Over the last 2 weeks, how often have you been bothered by:</span>
            <button type="button" class="mh-btn-primary" onclick="submitScaleAssessment()">
                📊 Calculate Score
            </button>
        </div>
        ${rowsHtml}
        <div style="margin-top: 10px; display: flex; justify-content: flex-end;">
            <button type="button" class="mh-btn-primary" onclick="submitScaleAssessment()">
                📊 Calculate My Clinical Score
            </button>
        </div>
    `;
}

function onScaleAnswerChange(scaleId, qIdx, value) {
    if (scaleId === 'pc_ptsd5' || scaleId === 'cage_aid') {
        scaleAnswersState[scaleId][qIdx] = (value === '1' || value === 'true');
    } else {
        scaleAnswersState[scaleId][qIdx] = parseInt(value) || 0;
    }
    submitScaleAssessment();
}

async function submitScaleAssessment() {
    const scaleId = activeMentalHealthScaleId;
    const answers = scaleAnswersState[scaleId];

    try {
        const res = await fetch('/api/mental-health/assess', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scale_id: scaleId, answers: answers })
        });
        const data = await res.json();
        if (data.success) {
            currentMhScaleResult = { ...data, type: 'scale' };
            renderScaleAssessmentResult(data);
        }
    } catch (e) {
        console.error('Scale assessment error:', e);
    }
}

function renderScaleAssessmentResult(data) {
    const resultCard = document.getElementById('mh-scale-result-card');
    if (!resultCard) return;

    resultCard.style.display = 'flex';

    // Determine ELI5 Tier Status
    const tierStr = (data.tier_label || data.tier || '').toLowerCase();
    let tierColor = 'safe';
    let statusIcon = '🟢';
    let headlineText = `Your responses indicate ${escapeHtml(data.tier_label || data.tier)}.`;

    if (data.has_suicide_flag || tierStr.includes('severe') || tierStr.includes('high')) {
        tierColor = 'high';
        statusIcon = '🔴';
        headlineText = `Significant distress identified (${data.tier_label || data.tier}). Professional medical and clinical counseling support is strongly recommended.`;
    } else if (tierStr.includes('moderate')) {
        tierColor = 'moderate';
        statusIcon = '🟡';
        headlineText = `Noticeable symptoms identified (${data.tier_label || data.tier}). Evidence-based self-care and supportive counseling can provide meaningful relief.`;
    } else {
        tierColor = 'safe';
        statusIcon = '🟢';
        headlineText = `Minimal or mild symptoms detected (${data.tier_label || data.tier}). Your responses reflect healthy coping and emotional balance.`;
    }

    const alertHtml = data.has_suicide_flag ? `
        <div class="calc-alert-banner" style="background: #fef2f2; border: 1.5px solid #f87171; color: #991b1b; padding: 12px 14px; border-radius: 10px; margin-bottom: 8px;">
            <strong style="display: block; font-size: 0.9rem; margin-bottom: 4px;">🚨 CRITICAL SAFETY ALERT: Question 9 Positive Endorsement</strong>
            <p style="font-size: 0.8rem; margin: 0; line-height: 1.4;">${escapeHtml(data.safety_alert)}</p>
            <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                <a href="tel:988" class="hotline-pill hotline-pill-red" style="padding: 6px 12px; font-size: 0.8rem;">📞 Call / Text 988 (Free 24/7)</a>
                <a href="sms:741741?body=HOME" class="hotline-pill hotline-pill-amber" style="padding: 6px 12px; font-size: 0.8rem;">💬 Text 741741</a>
            </div>
        </div>
    ` : '';

    const recSomaticHtml = (data.recommended_somatic_protocols || []).map(p => `
        <button type="button" class="mh-btn-secondary" style="font-size: 0.76rem; padding: 5px 9px; margin-top: 4px;" onclick="launchRecommendedSomatic('${p.id}')">
            ${p.icon} Launch ${escapeHtml(p.title)}
        </button>
    `).join(' ');

    resultCard.innerHTML = `
        <div class="eli5-result-container" style="width: 100%;">
            ${alertHtml}

            <!-- Tier 1: Plain English Headline Card -->
            <div class="eli5-headline-card ${tierColor}">
                <div class="eli5-headline-badge">${statusIcon} ${escapeHtml(data.scale_title || 'Mental Wellbeing Assessment')}: ${escapeHtml(data.tier_label || data.tier)}</div>
                <p class="eli5-headline-text">${headlineText}</p>
            </div>

            <!-- Tier 2: 3 Clear Action Steps -->
            <div class="eli5-actions-card">
                <div class="eli5-actions-title">💡 3 Simple Steps You Can Take:</div>
                <div class="eli5-action-item">
                    <div class="eli5-action-number">1</div>
                    <div>
                        <strong>Somatic Regulation:</strong> Practice structured breathwork to calm nervous system arousal.
                        <div style="margin-top: 4px;">${recSomaticHtml || '<button type="button" class="mh-btn-secondary" style="font-size: 0.74rem; padding: 4px 8px;" onclick="switchMentalHealthCategory(\'somatic_pacers\')">🌬️ Box Breathing</button>'}</div>
                    </div>
                </div>
                <div class="eli5-action-item">
                    <div class="eli5-action-number">2</div>
                    <div><strong>Daily Rhythm:</strong> Maintain regular wake/sleep hours, get 15 minutes of morning sunlight, and stay connected with trusted friends or family.</div>
                </div>
                <div class="eli5-action-item">
                    <div class="eli5-action-number">3</div>
                    <div><strong>Clinical Support:</strong> Share this standardized screening score with your primary physician, counselor, or therapist for personalized guidance.</div>
                </div>
            </div>

            <!-- Tier 3: Collapsible Doctor & Psychometric Details -->
            <details class="clinical-details-dropdown">
                <summary>🩺 View Doctor & Psychometric Details (Cutoff Scores & Guidelines)</summary>
                <div class="clinical-details-content">
                    <div style="display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid #ede9fe; padding-bottom: 8px; margin-bottom: 8px;">
                        <div>
                            <span style="font-size: 0.72rem; text-transform: uppercase; color: #64748b; font-weight: 700;">Standardized Score</span>
                            <div style="font-size: 1.4rem; font-weight: 900; color: #6d28d9;">
                                ${data.score} <span style="font-size: 0.85rem; font-weight: 600; color: #64748b;">/ ${data.max_score} ${data.score_unit}</span>
                            </div>
                        </div>
                        <div class="calc-tier-badge" style="background: #ede9fe; color: #6d28d9; border: 1px solid #ddd6fe; font-size: 0.8rem; padding: 4px 10px;">
                            ${escapeHtml(data.tier_label || data.tier)}
                        </div>
                    </div>

                    <div style="margin-bottom: 8px;">
                        <strong style="color: #4c1d95; font-size: 0.8rem; display: block; margin-bottom: 2px;">Clinical Action & Practice Guidelines:</strong>
                        <p style="font-size: 0.78rem; color: #334155; margin: 0; line-height: 1.45;">${escapeHtml(data.clinical_action || '')}</p>
                    </div>

                    <div class="calc-citation-footer" style="margin-top: 6px;">
                        Citations: ${escapeHtml(data.citations || 'Clinically Validated Psychometric Toolkits')}
                    </div>
                </div>
            </details>
        </div>
    `;

    // Reset attach button
    const attachBtn = document.getElementById('mh-attach-btn');
    if (attachBtn) {
        attachBtn.textContent = '📄 Attach to Doctor PDF';
        attachBtn.disabled = false;
    }
}

function launchRecommendedSomatic(pacerOrToolId) {
    if (SOMATIC_PACER_CONFIGS[pacerOrToolId]) {
        switchMentalHealthCategory('somatic_pacers');
        onSomaticPacerSelect(pacerOrToolId);
    } else {
        switchMentalHealthCategory('grounding_pmr');
        onGroundingToolSelect(pacerOrToolId);
    }
}

// -----------------------------------------------------------------------------
// Grounding & PMR Toolkit
// -----------------------------------------------------------------------------

function onGroundingToolSelect(toolId) {
    activeGroundingToolId = toolId;
    renderGroundingView(toolId);
}

function renderGroundingView(toolId) {
    const container = document.getElementById('mh-grounding-container');
    if (!container) return;

    if (toolId === 'grounding_54321') {
        container.innerHTML = `
            <div style="background: white; border: 1px solid var(--border); border-radius: 12px; padding: 14px; margin-bottom: 10px;">
                <h4 style="font-size: 0.92rem; color: #1e293b; margin-bottom: 4px;">5-4-3-2-1 Somatosensory Grounding Protocol</h4>
                <p style="font-size: 0.78rem; color: #64748b; margin: 0;">Orient your sensory awareness outward into the physical room to interrupt acute panic, flashbacks, and dissociation. Check each box as you notice each item.</p>
            </div>
            <div class="mh-54321-step">
                <div class="mh-step-icon-badge">👁️</div>
                <div class="mh-step-info-col">
                    <div class="mh-step-title">5 Things You Can SEE</div>
                    <div class="mh-step-desc">Notice 5 distinct objects around you (e.g., shadows on the floor, colors on a book, wood grain, a light fixture).</div>
                </div>
            </div>
            <div class="mh-54321-step">
                <div class="mh-step-icon-badge">✋</div>
                <div class="mh-step-info-col">
                    <div class="mh-step-title">4 Things You Can physically FEEL</div>
                    <div class="mh-step-desc">Feel your feet firmly planted on the ground, the texture of your clothing, the cool temperature of the table, your watch on your wrist.</div>
                </div>
            </div>
            <div class="mh-54321-step">
                <div class="mh-step-icon-badge">👂</div>
                <div class="mh-step-info-col">
                    <div class="mh-step-title">3 Things You Can HEAR</div>
                    <div class="mh-step-desc">Listen for distant traffic, humming of air conditioning or computer fan, birds outside, or your own slow breath.</div>
                </div>
            </div>
            <div class="mh-54321-step">
                <div class="mh-step-icon-badge">👃</div>
                <div class="mh-step-info-col">
                    <div class="mh-step-title">2 Things You Can SMELL</div>
                    <div class="mh-step-desc">Notice fresh air, hand lotion, coffee, soap, or imagine a soothing scent of lavender or pine.</div>
                </div>
            </div>
            <div class="mh-54321-step">
                <div class="mh-step-icon-badge">👅</div>
                <div class="mh-step-info-col">
                    <div class="mh-step-title">1 Thing You Can TASTE</div>
                    <div class="mh-step-desc">Take a sip of cool water, a mint, or bring awareness to the inside of your mouth. Take one deep breath.</div>
                </div>
            </div>
        `;
    } else if (toolId === 'pmr_jacobson') {
        container.innerHTML = `
            <div style="background: white; border: 1px solid var(--border); border-radius: 12px; padding: 14px; margin-bottom: 10px;">
                <h4 style="font-size: 0.92rem; color: #1e293b; margin-bottom: 4px;">Progressive Muscle Relaxation (Jacobson PMR)</h4>
                <p style="font-size: 0.78rem; color: #64748b; margin: 0;">Isometrically tighten each muscle group hard for 5 seconds, then abruptly release and feel warm relaxation for 10 seconds.</p>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px;">
                <div style="background: white; border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px;">
                    <strong style="color: #6d28d9; font-size: 0.84rem;">1. Hands & Forearms</strong>
                    <div style="font-size: 0.76rem; color: #475569; margin-top: 3px;">Clench both fists tightly like squeezing a lemon (5s) → release abruptly limp (10s).</div>
                </div>
                <div style="background: white; border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px;">
                    <strong style="color: #6d28d9; font-size: 0.84rem;">2. Biceps & Upper Arms</strong>
                    <div style="font-size: 0.76rem; color: #475569; margin-top: 3px;">Bend elbows and flex biceps tight (5s) → let arms drop heavily to sides (10s).</div>
                </div>
                <div style="background: white; border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px;">
                    <strong style="color: #6d28d9; font-size: 0.84rem;">3. Forehead & Eyes</strong>
                    <div style="font-size: 0.76rem; color: #475569; margin-top: 3px;">Raise eyebrows high and squeeze eyes shut tight (5s) → smooth facial brow completely (10s).</div>
                </div>
                <div style="background: white; border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px;">
                    <strong style="color: #6d28d9; font-size: 0.84rem;">4. Jaw & Cheeks</strong>
                    <div style="font-size: 0.76rem; color: #475569; margin-top: 3px;">Clench teeth gently and pull mouth corners back (5s) → let jaw fall loosely open (10s).</div>
                </div>
                <div style="background: white; border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px;">
                    <strong style="color: #6d28d9; font-size: 0.84rem;">5. Shoulders & Neck</strong>
                    <div style="font-size: 0.76rem; color: #475569; margin-top: 3px;">Shrug shoulders up toward your ears (5s) → drop them heavily and feel relief (10s).</div>
                </div>
                <div style="background: white; border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px;">
                    <strong style="color: #6d28d9; font-size: 0.84rem;">6. Chest & Abdomen</strong>
                    <div style="font-size: 0.76rem; color: #475569; margin-top: 3px;">Tighten abdominal wall like preparing for a punch (5s) → exhale and soften stomach (10s).</div>
                </div>
                <div style="background: white; border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px;">
                    <strong style="color: #6d28d9; font-size: 0.84rem;">7. Thighs & Glutes</strong>
                    <div style="font-size: 0.76rem; color: #475569; margin-top: 3px;">Squeeze thigh muscles and press heels into floor (5s) → release all lower body tension (10s).</div>
                </div>
                <div style="background: white; border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px;">
                    <strong style="color: #6d28d9; font-size: 0.84rem;">8. Calves & Feet</strong>
                    <div style="font-size: 0.76rem; color: #475569; margin-top: 3px;">Point toes upward toward shins flexing calves (5s) → release and feel warm tingling (10s).</div>
                </div>
            </div>
        `;
    } else if (toolId === 'bilateral_tapping') {
        container.innerHTML = `
            <div style="background: white; border: 1px solid var(--border); border-radius: 12px; padding: 14px; margin-bottom: 10px;">
                <h4 style="font-size: 0.92rem; color: #1e293b; margin-bottom: 4px;">🦋 The Butterfly Hug & Bilateral Tapping (EMDR Somatic Protocol)</h4>
                <p style="font-size: 0.78rem; color: #64748b; margin: 0;">1. Cross arms across chest with fingertips resting on opposite collarbones.<br>2. Alternate tapping left hand, then right hand slowly at ~1.1 Hz rhythm.<br>3. Allow distressing thoughts to pass by without judgment while maintaining steady tactile rhythm.</p>
            </div>
            <div style="background: #faf5ff; border: 2px dashed #c084fc; border-radius: 12px; padding: 30px; text-align: center;">
                <span style="font-size: 3rem; display: block; margin-bottom: 6px;">🦋</span>
                <strong style="font-size: 1rem; color: #6b21a8;">Tap Left... Tap Right...</strong>
                <p style="font-size: 0.8rem; color: #7e22ce; margin-top: 4px;">Rhythmic alternating stimulation facilitates interhemispheric processing and calms the limbic system.</p>
            </div>
        `;
    } else if (toolId === 'autogenic_training') {
        container.innerHTML = `
            <div style="background: white; border: 1px solid var(--border); border-radius: 12px; padding: 14px; margin-bottom: 10px;">
                <h4 style="font-size: 0.92rem; color: #1e293b; margin-bottom: 4px;">☀️ Autogenic Somatic Training (Schultz Thermal Conditioning)</h4>
                <p style="font-size: 0.78rem; color: #64748b; margin: 0;">Sit comfortably, close your eyes, and repeat each somatic formula silently 3 times to induce peripheral vasodilation and vagal dominance.</p>
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <div style="background: white; border: 1px solid var(--border); border-left: 4px solid #f59e0b; border-radius: 8px; padding: 10px 14px; font-size: 0.82rem; color: #1e293b;">
                    "My right arm is heavy and warm... My left arm is heavy and warm..."
                </div>
                <div style="background: white; border: 1px solid var(--border); border-left: 4px solid #f59e0b; border-radius: 8px; padding: 10px 14px; font-size: 0.82rem; color: #1e293b;">
                    "My arms and legs are delightfully heavy and warm..."
                </div>
                <div style="background: white; border: 1px solid var(--border); border-left: 4px solid #06b6d4; border-radius: 8px; padding: 10px 14px; font-size: 0.82rem; color: #1e293b;">
                    "My heartbeat is calm and regular... My breathing is effortless..."
                </div>
                <div style="background: white; border: 1px solid var(--border); border-left: 4px solid #8b5cf6; border-radius: 8px; padding: 10px 14px; font-size: 0.82rem; color: #1e293b;">
                    "My solar plexus is pleasantly warm... My forehead is cool..."
                </div>
            </div>
        `;
    }
}

// -----------------------------------------------------------------------------
// Stanley-Brown Crisis Safety Plan Engine
// -----------------------------------------------------------------------------

async function saveSafetyPlan() {
    const payload = {
        warning_signs: (document.getElementById('sp-warning-signs')?.value || '').split(';').map(s => s.trim()).filter(Boolean),
        coping_strategies: (document.getElementById('sp-coping-strategies')?.value || '').split(';').map(s => s.trim()).filter(Boolean),
        social_distractions: (document.getElementById('sp-social-distractions')?.value || '').split(';').map(s => s.trim()).filter(Boolean),
        trusted_contacts: (document.getElementById('sp-trusted-contacts')?.value || '').split(';').map(s => s.trim()).filter(Boolean),
        professionals: (document.getElementById('sp-professionals')?.value || '').split(';').map(s => s.trim()).filter(Boolean),
        environment_safety: (document.getElementById('sp-environment-safety')?.value || '').split(';').map(s => s.trim()).filter(Boolean)
    };

    try {
        const res = await fetch('/api/mental-health/safety-plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            currentMhScaleResult = { ...data, type: 'safety_plan' };
            window.attachedMentalHealthReports = window.attachedMentalHealthReports.filter(r => r.type !== 'safety_plan');
            window.attachedMentalHealthReports.push(currentMhScaleResult);

            const attachBtn = document.getElementById('mh-attach-btn');
            if (attachBtn) {
                attachBtn.textContent = '✓ Safety Plan Saved & Attached to PDF!';
                attachBtn.disabled = true;
            }
        }
    } catch (e) {
        console.error('Save safety plan error:', e);
    }
}

function loadSampleSafetyPlan() {
    const s1 = document.getElementById('sp-warning-signs');
    const s2 = document.getElementById('sp-coping-strategies');
    const s3 = document.getElementById('sp-social-distractions');
    const s4 = document.getElementById('sp-trusted-contacts');
    const s5 = document.getElementById('sp-professionals');
    const s6 = document.getElementById('sp-environment-safety');

    if (s1) s1.value = "Insomnia for >2 nights; Feeling like a burden; Irritability; Withdrawal from friends";
    if (s2) s2.value = "5-minute Box Breathing (4-4-4-4); 5-4-3-2-1 Sensory Grounding; Cold water splash on face; Listening to acoustic playlist";
    if (s3) s3.value = "Visiting the local library/bookstore; Walking around public park; Coffee shop sitting";
    if (s4) s4.value = "Mom (Sarah) - 555-0192; Best Friend (Alex) - 555-0144; Sister (Emma) - 555-0177";
    if (s5) s5.value = "Dr. Miller (Psychologist) - 555-0122; City Community Mental Health Clinic: 555-0199";
    if (s6) s6.value = "Give lockbox key to trusted family member; Keep medications in monitored organizer; Stay in common living areas with family";
}

function resetActiveMentalHealthTool() {
    if (activeMhCategory === 'somatic_pacers') {
        resetBreathingPacer();
    } else if (activeMhCategory === 'clinical_scales') {
        scaleAnswersState[activeMentalHealthScaleId] = (activeMentalHealthScaleId === 'pc_ptsd5' || activeMentalHealthScaleId === 'cage_aid') ? [false, false, false, false, false] : [0, 0, 0, 0, 0, 0, 0, 0, 0];
        renderScaleQuestionnaire(activeMentalHealthScaleId);
    }
}

function attachMentalHealthToDoctorSummary() {
    if (activeMhCategory === 'somatic_pacers') {
        const cfg = SOMATIC_PACER_CONFIGS[activeSomaticPacerId] || SOMATIC_PACER_CONFIGS.box_breathing;
        const somaticRecord = {
            type: 'somatic',
            title: cfg.title,
            cycles_completed: Math.max(1, pacerCycleCount),
            duration_seconds: Math.max(30, pacerElapsedSeconds),
            vagal_mechanism: cfg.neuro
        };
        window.attachedMentalHealthReports = window.attachedMentalHealthReports.filter(r => r.title !== cfg.title);
        window.attachedMentalHealthReports.push(somaticRecord);
    } else if (activeMhCategory === 'clinical_scales') {
        if (!currentMhScaleResult) {
            submitScaleAssessment();
        }
        if (currentMhScaleResult) {
            const sid = currentMhScaleResult.scale_id;
            window.attachedMentalHealthReports = window.attachedMentalHealthReports.filter(r => r.scale_id !== sid);
            window.attachedMentalHealthReports.push(currentMhScaleResult);
        }
    } else if (activeMhCategory === 'crisis_safety') {
        saveSafetyPlan();
    }

    const attachBtn = document.getElementById('mh-attach-btn');
    if (attachBtn) {
        attachBtn.textContent = '✓ Attached to Doctor PDF!';
        attachBtn.disabled = true;
    }
}

function discussMentalHealthInChat() {
    closeMentalHealthModal();
    let query = "Can you provide clinical evidence and supportive somatic strategies for managing stress and anxiety?";
    if (currentMhScaleResult && currentMhScaleResult.scale_title) {
        query = `Can you explain my score for ${currentMhScaleResult.scale_title} (${currentMhScaleResult.score}/${currentMhScaleResult.max_score} - ${currentMhScaleResult.tier_label || currentMhScaleResult.tier}) and what questions I should ask my doctor or therapist?`;
    } else if (activeMhCategory === 'somatic_pacers') {
        const cfg = SOMATIC_PACER_CONFIGS[activeSomaticPacerId];
        query = `How does ${cfg.title} work neurobiologically to stimulate the vagus nerve and reduce anxiety?`;
    }
    if (userInput) {
        userInput.value = query;
        chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
}

/**
 * ============================================================================
 * MULTIMODAL MEDICAL DOCUMENT & VISION OCR CONTROLLER
 * ============================================================================
 */

let activeVisionMode = 'auto';
let currentVisionResult = null;
let currentVisionFile = null;
window.attachedVisionScans = window.attachedVisionScans || [];

function openVisionModal(mode = 'auto') {
    const modal = document.getElementById('vision-modal');
    if (!modal) return;
    modal.classList.remove('hidden');
    switchVisionMode(mode);
}

function closeVisionModal() {
    const modal = document.getElementById('vision-modal');
    if (modal) modal.classList.add('hidden');
}

function switchVisionMode(mode) {
    activeVisionMode = mode || 'auto';
    document.querySelectorAll('[id^="vision-tab-"]').forEach(tab => {
        tab.classList.remove('active');
    });
    const activeTab = document.getElementById(`vision-tab-${activeVisionMode}`);
    if (activeTab) activeTab.classList.add('active');
}

function triggerVisionFileInput() {
    const input = document.getElementById('vision-file-input');
    if (input) {
        input.removeAttribute('capture');
        input.value = '';
        input.click();
    }
}

function triggerVisionCamera() {
    const input = document.getElementById('vision-file-input');
    if (input) {
        input.setAttribute('capture', 'environment');
        input.value = '';
        input.click();
    }
}

function handleVisionFileSelect(event) {
    const file = event.target.files && event.target.files[0];
    if (file) {
        handleVisionFileUpload(file, activeVisionMode);
    }
}

function handleVisionDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    const dropzone = document.getElementById('vision-dropzone');
    if (dropzone) dropzone.classList.add('drag-over');
}

function handleVisionDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    const dropzone = document.getElementById('vision-dropzone');
    if (dropzone) dropzone.classList.remove('drag-over');
}

function handleVisionDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    const dropzone = document.getElementById('vision-dropzone');
    if (dropzone) dropzone.classList.remove('drag-over');

    const dt = event.dataTransfer;
    if (dt && dt.files && dt.files[0]) {
        handleVisionFileUpload(dt.files[0], activeVisionMode);
    }
}

function resetVisionUpload() {
    currentVisionResult = null;
    currentVisionFile = null;

    const uploadSec = document.getElementById('vision-upload-section');
    const processSec = document.getElementById('vision-processing-section');
    const resultsSec = document.getElementById('vision-results-section');
    const actionBtns = document.getElementById('vision-action-buttons');
    const fileInput = document.getElementById('vision-file-input');

    if (uploadSec) uploadSec.style.display = 'block';
    if (processSec) processSec.style.display = 'none';
    if (resultsSec) {
        resultsSec.style.display = 'none';
        resultsSec.innerHTML = '';
    }
    if (actionBtns) {
        actionBtns.style.display = 'none';
        actionBtns.innerHTML = '';
    }
    if (fileInput) fileInput.value = '';
}

async function handleVisionFileUpload(file, mode) {
    if (!file) return;

    // Validate size (5MB Max)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
        alert('Image file size exceeds the 5MB limit. Please upload a smaller image.');
        return;
    }

    currentVisionFile = file;
    const uploadSec = document.getElementById('vision-upload-section');
    const processSec = document.getElementById('vision-processing-section');
    const resultsSec = document.getElementById('vision-results-section');
    const fileNameEl = document.getElementById('vision-file-name');
    const fileSizeEl = document.getElementById('vision-file-size');
    const previewImg = document.getElementById('vision-preview-img');
    const statusMain = document.getElementById('vision-status-main');
    const statusSub = document.getElementById('vision-status-sub');
    const overlay = document.getElementById('vision-scan-overlay');

    if (uploadSec) uploadSec.style.display = 'none';
    if (processSec) processSec.style.display = 'block';
    if (resultsSec) resultsSec.style.display = 'none';
    if (overlay) overlay.style.display = 'block';

    if (fileNameEl) fileNameEl.textContent = file.name;
    if (fileSizeEl) fileSizeEl.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;

    // Preview image locally via FileReader
    const reader = new FileReader();
    reader.onload = (e) => {
        if (previewImg) previewImg.src = e.target.result;
    };
    reader.readAsDataURL(file);

    // Progressive status updates
    if (statusMain) statusMain.textContent = 'Analyzing Document with Gemini Multimodal Vision...';
    if (statusSub) statusSub.textContent = 'Reading clinical entities, biomarker values, and prescription labels...';

    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_hint', mode || 'auto');

    try {
        const response = await fetch('/api/vision/scan', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        currentVisionResult = data;

        if (overlay) overlay.style.display = 'none';

        if (!response.ok || !data.success) {
            const errMsg = data.error || 'Failed to analyze medical document.';
            if (statusMain) statusMain.textContent = 'OCR Scan Notice';
            if (statusSub) statusSub.textContent = errMsg;
            renderVisionError(errMsg);
            return;
        }

        if (statusMain) statusMain.textContent = '✓ Extraction & Verification Complete';
        if (statusSub) statusSub.textContent = `Identified: ${data.doc_type_label || data.doc_type}`;

        renderVisionResults(data);

    } catch (err) {
        console.error('Vision OCR upload error:', err);
        if (overlay) overlay.style.display = 'none';
        renderVisionError('Network or server error while processing image.');
    }
}

function renderVisionError(msg) {
    const resultsSec = document.getElementById('vision-results-section');
    if (!resultsSec) return;
    resultsSec.style.display = 'block';
    resultsSec.innerHTML = `
        <div class="eli5-result-container" style="margin-top: 14px;">
            <div class="eli5-headline-card high">
                <div class="eli5-headline-badge">⚠️ Document Scan Notice</div>
                <p class="eli5-headline-text">${escapeHtml(msg)}</p>
            </div>
            <div style="text-align: center; margin-top: 12px;">
                <button type="button" class="vision-btn-primary" onclick="resetVisionUpload()">
                    Try Another Photo
                </button>
            </div>
        </div>
    `;
}

function renderVisionResults(data) {
    const resultsSec = document.getElementById('vision-results-section');
    const actionBtns = document.getElementById('vision-action-buttons');
    if (!resultsSec) return;

    resultsSec.style.display = 'block';

    const docType = data.doc_type || 'general_medical_document';
    const docLabel = data.doc_type_label || 'Medical Document';
    const plainSummary = data.plain_language_summary || 'Document extracted successfully.';
    const keyTakeaways = data.key_takeaways || [];
    const extractedLabs = data.extracted_labs || [];
    const extractedMeds = data.extracted_medications || [];
    const polyCheck = data.polypharmacy_interaction_check;
    const docQuestions = data.doctor_questions || [];
    const findingsBreakdown = data.findings_breakdown || [];
    const jargonGlossary = data.jargon_glossary || [];
    const radImpression = data.radiologist_impression || '';
    const modality = data.modality || '';
    const bodyRegion = data.body_map_region || 'chest';

    // 1. Doc Type Badge & Confidence Header
    let docBadgeIcon = '📄';
    if (docType === 'prescription') docBadgeIcon = '💊';
    else if (docType === 'lab_report') docBadgeIcon = '🔬';
    else if (docType === 'vital_signs') docBadgeIcon = '💓';
    else if (docType === 'radiology_report' || modality) docBadgeIcon = '🩻';

    // 2. Radiology Impression Banner (Tier 1 Specialist Headline)
    let impressionHtml = '';
    if (radImpression) {
        impressionHtml = `
            <div class="vision-data-subcard vision-impression-subcard">
                <div class="vision-subcard-header">
                    <span class="subcard-icon">🩻</span>
                    <strong>Radiologist Impression (${escapeHtml(modality || 'Diagnostic Imaging')})</strong>
                </div>
                <div class="vision-impression-text">
                    ${escapeHtml(radImpression)}
                </div>
            </div>
        `;
    }

    // 3. Radiology Anatomical Findings Table (Tier 2)
    let findingsHtml = '';
    if (findingsBreakdown.length > 0) {
        const rows = findingsBreakdown.map(item => {
            const statusTier = (item.status_tier || 'NORMAL').toUpperCase();
            let statusClass = 'status-optimal';
            let statusIcon = '🟢';
            let statusLabel = 'Normal / Clear';

            if (statusTier.includes('ATTENTION') || statusTier.includes('ABNORMAL') || statusTier.includes('ACUTE') || statusTier.includes('CRITICAL')) {
                statusClass = 'status-high';
                statusIcon = '🔴';
                statusLabel = 'Needs Attention';
            } else if (statusTier.includes('INCIDENTAL') || statusTier.includes('MILD') || statusTier.includes('BORDERLINE')) {
                statusClass = 'status-borderline';
                statusIcon = '🟡';
                statusLabel = 'Mild / Incidental';
            }

            return `
                <tr>
                    <td class="vision-finding-structure"><strong>${escapeHtml(item.organ_structure || 'Structure')}</strong></td>
                    <td class="vision-finding-radiologist"><em>${escapeHtml(item.radiologist_finding || '')}</em></td>
                    <td class="vision-finding-translation">${escapeHtml(item.plain_english_meaning || '')}</td>
                    <td><span class="lab-status-badge ${statusClass}">${statusIcon} ${escapeHtml(statusLabel)}</span></td>
                </tr>
            `;
        }).join('');

        findingsHtml = `
            <div class="vision-data-subcard">
                <div class="vision-subcard-header">
                    <span class="subcard-icon">🩻</span>
                    <strong>Anatomical Findings & Plain English Translation (${findingsBreakdown.length} Structures)</strong>
                </div>
                <div class="vision-table-responsive">
                    <table class="vision-findings-table">
                        <thead>
                            <tr>
                                <th>Organ / Structure</th>
                                <th>Radiologist Finding</th>
                                <th>Plain English Meaning (ELI5)</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>${rows}</tbody>
                    </table>
                </div>
            </div>
        `;
    }

    // 4. Medical Jargon Glossary Grid (Tier 2)
    let glossaryHtml = '';
    if (jargonGlossary.length > 0) {
        const termCards = jargonGlossary.map(g => `
            <div class="glossary-term-card">
                <div class="glossary-term-name">💡 ${escapeHtml(g.term)}</div>
                <div class="glossary-term-def">${escapeHtml(g.definition)}</div>
            </div>
        `).join('');

        glossaryHtml = `
            <div class="vision-data-subcard">
                <div class="vision-subcard-header">
                    <span class="subcard-icon">📖</span>
                    <strong>Plain-Language Medical Jargon Glossary (${jargonGlossary.length} Terms)</strong>
                </div>
                <div class="vision-glossary-grid">${termCards}</div>
            </div>
        `;
    }

    // 5. Extracted Labs Table (Tier 2)
    let labsHtml = '';
    if (extractedLabs.length > 0) {
        const rows = extractedLabs.map(lab => {
            const statusLower = (lab.interpretation_status || 'normal').toLowerCase();
            let statusPillClass = 'status-optimal';
            let statusText = lab.interpretation_status || 'Normal';
            if (statusLower.includes('high') || statusLower.includes('elevated') || statusLower.includes('critical')) {
                statusPillClass = 'status-high';
            } else if (statusLower.includes('low') || statusLower.includes('borderline')) {
                statusPillClass = 'status-borderline';
            }

            return `
                <tr>
                    <td><strong>${escapeHtml(lab.biomarker_name || lab.test_key)}</strong></td>
                    <td><span class="vision-lab-val">${lab.value} ${escapeHtml(lab.unit || '')}</span></td>
                    <td><span class="vision-ref-range">${escapeHtml(lab.reference_range || 'Standard range')}</span></td>
                    <td><span class="lab-status-badge ${statusPillClass}">${escapeHtml(statusText)}</span></td>
                </tr>
            `;
        }).join('');

        labsHtml = `
            <div class="vision-data-subcard">
                <div class="vision-subcard-header">
                    <span class="subcard-icon">🔬</span>
                    <strong>Extracted Laboratory Biomarkers (${extractedLabs.length})</strong>
                </div>
                <div class="vision-table-responsive">
                    <table class="vision-labs-table">
                        <thead>
                            <tr>
                                <th>Biomarker</th>
                                <th>Value</th>
                                <th>Reference Target</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>${rows}</tbody>
                    </table>
                </div>
            </div>
        `;
    }

    // 6. Extracted Medications List (Tier 2)
    let medsHtml = '';
    if (extractedMeds.length > 0) {
        const medCards = extractedMeds.map(med => `
            <div class="vision-med-pill-card">
                <div class="vision-med-header">
                    <span class="vision-med-name">💊 ${escapeHtml(med.name || 'Medication')}</span>
                    ${med.dosage ? `<span class="vision-med-dose">${escapeHtml(med.dosage)}</span>` : ''}
                </div>
                <div class="vision-med-body">
                    ${med.frequency ? `<span class="vision-med-meta">⏱️ ${escapeHtml(med.frequency)}</span>` : ''}
                    ${med.instructions ? `<span class="vision-med-meta">📋 ${escapeHtml(med.instructions)}</span>` : ''}
                    ${med.warnings ? `<span class="vision-med-warning">⚠️ ${escapeHtml(med.warnings)}</span>` : ''}
                </div>
            </div>
        `).join('');

        medsHtml = `
            <div class="vision-data-subcard">
                <div class="vision-subcard-header">
                    <span class="subcard-icon">💊</span>
                    <strong>Extracted Prescriptions & Medications (${extractedMeds.length})</strong>
                </div>
                <div class="vision-meds-grid">${medCards}</div>
            </div>
        `;
    }

    // 7. Polypharmacy Interaction Alert Card (if detected)
    let polyHtml = '';
    if (polyCheck && polyCheck.has_interactions) {
        const intCards = (polyCheck.interactions || []).map(item => `
            <div class="poly-interaction-card card-${(item.severity || 'MODERATE').toLowerCase()}" style="margin-bottom: 6px;">
                <div class="poly-int-header">
                    <span class="poly-int-pair">⚠️ ${escapeHtml(item.item_1)} + ${escapeHtml(item.item_2)}</span>
                    <span class="poly-severity-pill badge-${(item.severity || 'MODERATE').toLowerCase()}">${escapeHtml(item.severity)}</span>
                </div>
                <div class="poly-int-effect"><strong>Mechanism:</strong> ${escapeHtml(item.effects || item.mechanism)}</div>
                <div class="poly-int-recommendation"><strong>Action:</strong> ${escapeHtml(item.action)}</div>
            </div>
        `).join('');

        polyHtml = `
            <div class="vision-data-subcard vision-poly-alert-box">
                <div class="vision-subcard-header">
                    <span class="subcard-icon">⚠️</span>
                    <strong style="color: #b91c1c;">Multi-Drug Interaction Alert (${polyCheck.total_interactions})</strong>
                </div>
                <div style="margin-top: 8px;">${intCards}</div>
            </div>
        `;
    }

    // 8. Physician Questions & Key Takeaways (Tier 3)
    let takeawaysHtml = '';
    if (keyTakeaways.length > 0) {
        takeawaysHtml = `
            <div class="eli5-action-item">
                <div class="eli5-action-number">✓</div>
                <div><strong>Key Takeaways:</strong>
                    <ul style="margin: 4px 0 0 0; padding-left: 18px;">
                        ${keyTakeaways.map(t => `<li>${escapeHtml(t)}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    let questionsHtml = '';
    if (docQuestions.length > 0) {
        questionsHtml = `
            <div class="eli5-action-item">
                <div class="eli5-action-number">❓</div>
                <div><strong>Questions to Ask Your Doctor or Specialist:</strong>
                    <ul style="margin: 4px 0 0 0; padding-left: 18px;">
                        ${docQuestions.map(q => `<li>${escapeHtml(q)}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    // Assemble Full 3-Tier ELI5 Document Card
    resultsSec.innerHTML = `
        <div class="eli5-result-container" style="margin-top: 14px;">
            <!-- Document Classification Header -->
            <div class="vision-classification-bar">
                <span class="vision-doc-badge">${docBadgeIcon} ${escapeHtml(docLabel)}</span>
                <span class="vision-verified-tag">✓ Gemini Vision OCR Grounded</span>
            </div>

            <!-- Tier 1: Plain English Headline Card -->
            <div class="eli5-headline-card safe">
                <div class="eli5-headline-badge">💡 Plain-Language Summary (ELI5)</div>
                <p class="eli5-headline-text">${escapeHtml(plainSummary)}</p>
            </div>

            <!-- Tier 1b: Radiologist Impression Banner (if available) -->
            ${impressionHtml}

            <!-- Tier 2: Extracted Clinical & Imaging Findings -->
            ${findingsHtml}
            ${glossaryHtml}
            ${labsHtml}
            ${medsHtml}
            ${polyHtml}

            <!-- Tier 3: Action Steps & Doctor Discussion Points -->
            <div class="eli5-actions-card">
                <div class="eli5-actions-title">📋 Next Steps & Clinical Recommendations:</div>
                ${takeawaysHtml}
                ${questionsHtml}
            </div>

            <!-- Collapsible Raw Transcription / Technical Breakdown -->
            ${data.raw_transcription ? `
                <details class="clinical-details-dropdown">
                    <summary>🔍 View Full OCR Transcription & Technical Findings</summary>
                    <div class="clinical-details-content">
                        <pre style="white-space: pre-wrap; font-size: 0.76rem; color: #475569; background: #f8fafc; padding: 10px; border-radius: 6px; margin: 0;">${escapeHtml(data.raw_transcription)}</pre>
                    </div>
                </details>
            ` : ''}
        </div>
    `;

    // 9. Build Action Buttons
    if (actionBtns) {
        actionBtns.style.display = 'flex';
        let buttonsHtml = '';

        if (docType === 'radiology_report' || modality || findingsBreakdown.length > 0) {
            buttonsHtml += `
                <button type="button" class="vision-action-trigger-btn vision-bodymap-btn" onclick="locateOnBodyMap('${escapeHtml(bodyRegion)}')">
                    🧍 Locate on 2D Body Map (${escapeHtml(bodyRegion.toUpperCase())})
                </button>
            `;
        }

        if (extractedLabs.length > 0) {
            buttonsHtml += `
                <button type="button" class="vision-action-trigger-btn" onclick="autoPopulateLabGauges()">
                    ⚡ Auto-Populate Lab Gauges (${extractedLabs.length})
                </button>
            `;
        }

        if (extractedMeds.length > 0) {
            buttonsHtml += `
                <button type="button" class="vision-action-trigger-btn" onclick="autoPopulatePolypharmacy()">
                    💊 Check Polypharmacy Matrix (${extractedMeds.length})
                </button>
            `;
        }

        buttonsHtml += `
            <button type="button" class="vision-action-trigger-btn vision-attach-btn" id="vision-attach-doc-btn" onclick="attachVisionToDoctorSummary()">
                📄 Attach to Doctor PDF
            </button>
            <button type="button" class="vision-action-trigger-btn" onclick="discussVisionInChat()">
                💬 Discuss in Chat
            </button>
        `;

        actionBtns.innerHTML = buttonsHtml;
    }
}

function locateOnBodyMap(regionKey) {
    closeVisionModal();
    const region = (regionKey || 'chest').toLowerCase();
    openSymptomTriageHub('bodymap');
    if (['spine', 'shoulders', 'hips'].includes(region)) {
        toggleBodyView('back');
    } else {
        toggleBodyView('front');
    }
    selectBodyRegion(region);
}

function autoPopulateLabGauges() {
    if (!currentVisionResult || !currentVisionResult.extracted_labs || currentVisionResult.extracted_labs.length === 0) {
        alert('No laboratory tests found in this document.');
        return;
    }

    const firstLab = currentVisionResult.extracted_labs[0];
    const testKey = firstLab.mapped_test_key || firstLab.test_key;

    closeVisionModal();
    openMedsLabsDietHub('labs');

    if (testKey) {
        onLabTestSelected(testKey);
        const val1Input = document.getElementById('lab-val-input');
        if (val1Input && firstLab.value !== undefined) {
            val1Input.value = firstLab.value;
            evaluateCurrentLab();
        }
    }
}

function autoPopulatePolypharmacy() {
    if (!currentVisionResult || !currentVisionResult.extracted_medications || currentVisionResult.extracted_medications.length === 0) {
        alert('No medications found in this document.');
        return;
    }

    const medNames = currentVisionResult.extracted_medications.map(m => m.name).filter(Boolean);
    closeVisionModal();
    openMedsLabsDietHub('polypharmacy');

    medNames.forEach(name => {
        addDrugTag(name);
    });

    evaluatePolypharmacy();
}

function attachVisionToDoctorSummary() {
    if (!currentVisionResult) return;

    window.attachedVisionScans = window.attachedVisionScans || [];
    window.attachedVisionScans.push({
        timestamp: new Date().toISOString(),
        doc_type: currentVisionResult.doc_type_label || currentVisionResult.doc_type,
        summary: currentVisionResult.plain_language_summary,
        modality: currentVisionResult.modality || '',
        anatomical_region: currentVisionResult.anatomical_region || '',
        body_map_region: currentVisionResult.body_map_region || '',
        radiologist_impression: currentVisionResult.radiologist_impression || '',
        findings_breakdown: currentVisionResult.findings_breakdown || [],
        jargon_glossary: currentVisionResult.jargon_glossary || [],
        extracted_labs: currentVisionResult.extracted_labs || [],
        extracted_medications: currentVisionResult.extracted_medications || [],
        takeaways: currentVisionResult.key_takeaways || []
    });

    // Also auto-attach extracted labs into window.attachedLabResults for PDF completeness
    if (currentVisionResult.extracted_labs && currentVisionResult.extracted_labs.length > 0) {
        currentVisionResult.extracted_labs.forEach(lab => {
            if (lab.mapped_test_key) {
                const existingIdx = window.attachedLabResults.findIndex(l => l.test_key === lab.mapped_test_key);
                const record = {
                    test_key: lab.mapped_test_key,
                    test_name: lab.biomarker_name,
                    value: lab.value,
                    unit: lab.unit,
                    optimal_target: lab.reference_range,
                    status: lab.interpretation_status,
                    status_label: lab.interpretation_status
                };
                if (existingIdx >= 0) {
                    window.attachedLabResults[existingIdx] = record;
                } else {
                    window.attachedLabResults.push(record);
                }
            }
        });
    }

    const attachBtn = document.getElementById('vision-attach-doc-btn');
    if (attachBtn) {
        attachBtn.textContent = '✓ Attached to Doctor PDF!';
        attachBtn.disabled = true;
    }
}

function discussVisionInChat() {
    closeVisionModal();
    if (!currentVisionResult) return;

    const summary = currentVisionResult.plain_language_summary || '';
    const impression = currentVisionResult.radiologist_impression ? ` Radiologist Impression: "${currentVisionResult.radiologist_impression}".` : '';
    const query = `I scanned a diagnostic imaging report (${currentVisionResult.doc_type_label || currentVisionResult.doc_type}).${impression} Summary: ${summary}. Can you help explain what this means for my health and what questions I should ask my doctor?`;

    if (userInput) {
        userInput.value = query;
        chatForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
}




