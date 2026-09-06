import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'health_info.db')

# Expanded dataset of 123 vetted, curated clinical health conditions across major specialties
HEALTH_DATA = [
    # =========================================================================
    # 1. INFECTIOUS & GENERAL ILLNESSES (20 Conditions)
    # =========================================================================
    (
        "Common Cold",
        "Infectious",
        "Runny or stuffy nose, sore throat, mild dry cough, sneezing, and slight fatigue.",
        "Get adequate rest, stay well-hydrated with warm fluids, and wash hands frequently."
    ),
    (
        "Flu",
        "Infectious",
        "Sudden moderate fever, body aches, exhaustion, chills, headache, and dry cough.",
        "Rest at home, drink plenty of fluids, and isolate to avoid spreading the virus."
    ),
    (
        "COVID-19",
        "Infectious",
        "Fever, dry cough, tiredness, loss of taste or smell, and nasal congestion.",
        "Isolate from others, monitor oxygen saturation, stay hydrated, and follow local public health guidelines."
    ),
    (
        "Dengue",
        "Infectious",
        "High fever, severe headache, retro-orbital pain (behind eyes), joint/muscle aches, and mild rash.",
        "Stay well-hydrated with oral rehydration salts, rest, avoid NSAIDs/aspirin, and use mosquito netting."
    ),
    (
        "Malaria",
        "Infectious",
        "Recurring fever cycles with chills, profuse sweating, headache, and body aches.",
        "Seek prompt medical blood testing, take prescribed antimalarials, and avoid mosquito exposure."
    ),
    (
        "Typhoid",
        "Infectious",
        "Gradually rising prolonged fever, abdominal discomfort, headache, loss of appetite, and constipation or diarrhea.",
        "Drink only boiled or purified water, eat thoroughly cooked meals, and seek laboratory blood confirmation."
    ),
    (
        "Strep Throat",
        "Infectious",
        "Sudden severe throat pain, difficulty swallowing, red swollen tonsils with white exudate, and fever.",
        "Gargle with warm salt water, drink soothing broths, and see a doctor for a rapid throat swab test."
    ),
    (
        "Sinusitis",
        "Infectious",
        "Facial pressure around forehead and cheeks, thick discolored nasal discharge, congestion, and reduced smell.",
        "Use warm facial compresses, inhale steam, and try saline nasal irrigation rinses."
    ),
    (
        "Mononucleosis",
        "Infectious",
        "Extreme fatigue, swollen lymph nodes in neck and armpits, sore throat, and low-grade fever.",
        "Get abundant bed rest, stay hydrated, and avoid heavy lifting or contact sports to protect the spleen."
    ),
    (
        "Chickenpox",
        "Infectious",
        "Itchy fluid-filled blisters across the body, mild fever, tiredness, and loss of appetite.",
        "Apply calamine lotion, take lukewarm colloidal oatmeal baths, and avoid scratching blisters."
    ),
    (
        "Shingles",
        "Infectious",
        "Painful localized rash with blisters typically appearing on one side of torso, accompanied by tingling or burning.",
        "Keep the rash clean and dry, wear loose cotton clothes, and consult a doctor promptly for antiviral therapy."
    ),
    (
        "Pneumonia",
        "Infectious",
        "Productive cough with greenish or rusty phlegm, fever, sweating, chills, and sharp chest discomfort when breathing deeply.",
        "Seek urgent medical evaluation for chest imaging and antibiotics, rest, and drink plenty of fluids."
    ),
    (
        "Acute Bronchitis",
        "Infectious",
        "Persistent chest cough with clear or discolored mucus, mild chest soreness, fatigue, and slight shortness of breath.",
        "Use a cool-mist humidifier, drink warm herbal teas, rest, and avoid exposure to smoke or fumes."
    ),
    (
        "Tonsillitis",
        "Infectious",
        "Red swollen tonsils, painful swallowing, tender neck glands, bad breath, and fever.",
        "Rest the voice, gargle with warm salt water, eat soft foods, and consult a physician if fever persists."
    ),
    (
        "Laryngitis",
        "Infectious",
        "Hoarseness, loss of voice, tickling sensation in throat, and mild dry cough.",
        "Rest vocal cords completely, avoid whispering, inhale soothing steam, and avoid caffeine and smoke."
    ),
    (
        "Whooping Cough",
        "Infectious",
        "Severe coughing fits followed by a high-pitched 'whoop' sound, vomiting after coughing, and exhaustion.",
        "Seek prompt medical care for antibiotic evaluation, stay hydrated, and ensure up-to-date pertussis vaccination."
    ),
    (
        "Lyme Disease",
        "Infectious",
        "Expanding bullseye skin rash (erythema migrans), fever, chills, fatigue, body aches, and swollen lymph nodes.",
        "Consult a physician immediately for early antibiotic treatment, check skin for ticks after outdoor activities."
    ),
    (
        "Scabies",
        "Infectious",
        "Intense itching especially at night, small pimple-like rash, and thin burrow tracks between fingers and wrists.",
        "Seek medical evaluation for topical permethrin, wash all bedding and clothing in hot water, and treat household contacts."
    ),
    (
        "Norovirus",
        "Infectious",
        "Sudden watery diarrhea, violent vomiting, stomach cramps, low-grade fever, and dehydration.",
        "Drink small frequent sips of oral rehydration fluids, wash hands thoroughly with soap, and disinfect surfaces."
    ),
    (
        "Rotavirus",
        "Infectious",
        "Severe watery diarrhea, vomiting, fever, and rapid dehydration primarily in infants and young children.",
        "Administer oral rehydration salts promptly, monitor wet diapers, and seek immediate pediatric care if lethargic."
    ),

    # =========================================================================
    # 2. RESPIRATORY & PULMONARY (10 Conditions)
    # =========================================================================
    (
        "Asthma",
        "Respiratory",
        "Wheezing, shortness of breath, chest tightness, and nighttime coughing triggered by cold air or allergens.",
        "Avoid known environmental triggers, keep prescribed rescue inhalers accessible, and maintain an asthma action plan."
    ),
    (
        "COPD",
        "Respiratory",
        "Chronic progressive shortness of breath, chronic cough with mucus, wheezing, and frequent chest infections.",
        "Avoid all tobacco smoke and air pollutants, practice pursed-lip breathing, and follow pulmonary rehabilitation."
    ),
    (
        "Allergic Rhinitis",
        "Respiratory",
        "Sneezing, itchy watery eyes, runny nose with clear discharge, and post-nasal drip triggered by pollen or dust.",
        "Use HEPA air filters, rinse sinuses with saline, keep windows closed during high pollen counts, and avoid allergens."
    ),
    (
        "Chronic Bronchitis",
        "Respiratory",
        "Daily cough producing sputum for at least three consecutive months over two successive years.",
        "Quit smoking, avoid airborne irritants, stay physically active within tolerance, and stay vaccinated against flu/pneumonia."
    ),
    (
        "Emphysema",
        "Respiratory",
        "Progressive shortness of breath during physical exertion, barrel-shaped chest, fatigue, and chronic wheezing.",
        "Strictly avoid smoking and secondhand smoke, practice diaphragmatic breathing, and consult a pulmonologist."
    ),
    (
        "Sleep Apnea",
        "Respiratory",
        "Loud chronic snoring, gasping episodes during sleep, morning headaches, daytime sleepiness, and brain fog.",
        "Maintain a healthy weight, avoid sleeping flat on the back, limit alcohol before bed, and consult a sleep specialist."
    ),
    (
        "Pleurisy",
        "Respiratory",
        "Sharp stabbing chest pain that worsens significantly with deep breaths, coughing, or sneezing.",
        "Rest in a comfortable position, avoid strenuous breathing exercises, and seek urgent medical evaluation to rule out complications."
    ),
    (
        "Post-Nasal Drip",
        "Respiratory",
        "Constant throat clearing, tickling cough, feeling of mucus dripping in back of throat, and morning hoarseness.",
        "Stay hydrated, sleep with head slightly elevated, use saline nasal sprays, and avoid dry indoor air."
    ),
    (
        "Hyperventilation",
        "Respiratory",
        "Rapid shallow breathing, lightheadedness, tingling in fingers and lips, and chest tightness often tied to anxiety.",
        "Practice slow rhythmic belly breathing (inhale 4 seconds, hold 4 seconds, exhale 6 seconds), and rest in a calm space."
    ),
    (
        "Pulmonary Fibrosis Awareness",
        "Respiratory",
        "Gradual dry hacking cough, shortness of breath on exertion, unexplained weight loss, and widening of fingertips (clubbing).",
        "Avoid dust and chemical fumes, follow structured exercise plans, and seek specialized pulmonary evaluation."
    ),

    # =========================================================================
    # 3. CARDIOVASCULAR & CIRCULATORY (10 Conditions)
    # =========================================================================
    (
        "Hypertension",
        "Cardiovascular",
        "Often symptomless initially, but may cause morning headaches, lightheadedness, or slight dizziness.",
        "Limit dietary sodium to under 2,000mg/day, practice routine aerobic exercise, manage stress, and track blood pressure."
    ),
    (
        "Hypotension",
        "Cardiovascular",
        "Lightheadedness when standing up quickly, dizziness, fainting, blurred vision, and general fatigue.",
        "Stand up gradually, drink plenty of water throughout the day, avoid prolonged hot baths, and consider compression socks."
    ),
    (
        "High Cholesterol",
        "Cardiovascular",
        "Typically silent without physical symptoms, but increases risk for arterial plaque buildup.",
        "Consume soluble fiber (oats, legumes), reduce saturated and trans fats, engage in brisk walking, and check lipid panels."
    ),
    (
        "Atherosclerosis",
        "Cardiovascular",
        "Narrowing of arteries causing reduced blood flow, leg cramping while walking, or mild exertion fatigue.",
        "Follow a heart-healthy Mediterranean diet, maintain regular physical exercise, and avoid all forms of tobacco."
    ),
    (
        "Peripheral Artery Disease",
        "Cardiovascular",
        "Painful cramping in calves, thighs, or hips during walking that subsides with rest (claudication), cold feet.",
        "Do supervised walking exercises, inspect feet daily for cuts or sores, keep legs warm, and consult a vascular doctor."
    ),
    (
        "Heart Palpitations",
        "Cardiovascular",
        "Sensations of a fluttering, pounding, racing, or skipped heartbeat during rest or mild exertion.",
        "Reduce caffeine and alcohol intake, practice deep relaxation techniques, stay hydrated, and consult a doctor if accompanied by chest pain."
    ),
    (
        "Deep Vein Thrombosis Awareness",
        "Cardiovascular",
        "Swelling, warmth, redness, and tenderness in one leg (typically the calf) after prolonged immobility.",
        "Avoid sitting motionless for long periods, walk during long flights/trips, and seek emergency evaluation if sudden calf swelling occurs."
    ),
    (
        "Atrial Fibrillation Awareness",
        "Cardiovascular",
        "Irregular rapid pulse, fluttering in chest, fatigue, dizziness, and mild shortness of breath.",
        "Track heart rate regularity, limit stimulants and alcohol, manage blood pressure, and consult a cardiologist."
    ),
    (
        "Raynaud's Phenomenon",
        "Cardiovascular",
        "Fingers or toes turning white then blue and cold in response to cold temperatures or stress, followed by throbbing.",
        "Wear warm gloves and thermal socks, avoid sudden temperature drops, avoid smoking, and manage emotional stress."
    ),
    (
        "Varicose Veins",
        "Cardiovascular",
        "Enlarged swollen bluish veins in legs, heaviness, aching, and mild swelling around ankles after standing.",
        "Elevate legs above heart level when resting, wear graduated compression stockings, and avoid prolonged stationary standing."
    ),

    # =========================================================================
    # 4. METABOLIC & ENDOCRINE (12 Conditions)
    # =========================================================================
    (
        "Diabetes",
        "Metabolic",
        "Increased thirst, frequent urination, unexplained fatigue, slow-healing cuts, and blurred vision.",
        "Monitor blood glucose regularly, maintain a balanced low-glycemic diet, and exercise daily."
    ),
    (
        "Type 1 Diabetes",
        "Metabolic",
        "Rapid unexplained weight loss, extreme thirst, excessive urination, and constant hunger.",
        "Adhere strictly to physician-prescribed insulin routines, monitor blood ketones, and maintain balanced nutrition."
    ),
    (
        "Pre-Diabetes",
        "Metabolic",
        "Mildly elevated blood sugar with subtle signs like darkened skin patches on neck/armpits (acanthosis nigricans).",
        "Engage in 150 minutes of weekly moderate exercise, reduce refined sugars, and aim for 5-7% healthy weight loss."
    ),
    (
        "Gestational Diabetes",
        "Metabolic",
        "High blood glucose developing during pregnancy, often symptomless or causing mild fatigue and thirst.",
        "Follow prescribed prenatal meal plans, monitor blood sugar before and after meals, and attend all obstetric checkups."
    ),
    (
        "Hypothyroidism",
        "Metabolic",
        "Fatigue, unexpected weight gain, sensitivity to cold, constipation, dry skin, and thinning hair.",
        "Get periodic thyroid panel blood tests (TSH/Free T4), maintain balanced iodine intake, and take prescribed thyroid hormone as directed."
    ),
    (
        "Hyperthyroidism",
        "Metabolic",
        "Rapid weight loss despite increased appetite, rapid heartbeat (tachycardia), nervousness, sweating, and tremors.",
        "Avoid excess dietary iodine, manage stress, stay in cool environments, and consult an endocrinologist."
    ),
    (
        "Hashimoto's Thyroiditis",
        "Metabolic",
        "Slow-onset fatigue, enlargement of thyroid gland (goiter) in neck, sluggish metabolism, and muscle weakness.",
        "Follow a nutrient-dense anti-inflammatory diet, track thyroid antibodies with a physician, and manage sleep quality."
    ),
    (
        "Gout",
        "Metabolic",
        "Sudden severe pain, intense swelling, redness, and heat in a single joint, most commonly the big toe.",
        "Limit high-purine foods (red meat, shellfish, alcohol/beer), drink 2-3 liters of water daily, and elevate the joint."
    ),
    (
        "Metabolic Syndrome",
        "Metabolic",
        "Combination of abdominal obesity, elevated triglycerides, low HDL, high blood pressure, and borderline glucose.",
        "Adopt a whole-foods plant-rich Mediterranean diet, perform daily physical activity, and track metabolic risk markers."
    ),
    (
        "PCOS",
        "Metabolic",
        "Irregular menstrual cycles, excess facial/body hair (hirsutism), severe acne, and weight gain around abdomen.",
        "Eat a low-glycemic balanced diet, engage in strength training, prioritize stress reduction, and consult a gynecologist."
    ),
    (
        "Osteoporosis",
        "Metabolic",
        "Gradual loss of bone density, stooped posture, loss of height, and bones fracturing easily from minor falls.",
        "Perform weight-bearing exercises, ensure adequate dietary calcium and vitamin D, and practice home fall-prevention measures."
    ),
    (
        "Obesity Management",
        "Metabolic",
        "Excess body fat accumulation impacting joint comfort, energy levels, sleep quality, and cardiovascular health.",
        "Focus on sustainable caloric balance, high-fiber nutrient-rich whole foods, daily step goals, and supportive medical guidance."
    ),

    # =========================================================================
    # 5. GASTROINTESTINAL & DIGESTIVE (15 Conditions)
    # =========================================================================
    (
        "GERD",
        "Gastrointestinal",
        "Burning sensation in chest after eating (heartburn), acid regurgitation, sour taste in mouth, and chronic throat clearing.",
        "Eat smaller frequent meals, avoid lying down for 3 hours after eating, elevate head of bed, and avoid trigger foods."
    ),
    (
        "Gastritis",
        "Gastrointestinal",
        "Gnawing or burning ache in upper abdomen, nausea, bloating after meals, and loss of appetite.",
        "Avoid spicy and acidic foods, limit alcohol and NSAID pain relievers, eat smaller portions, and stay hydrated."
    ),
    (
        "Peptic Ulcer",
        "Gastrointestinal",
        "Burning stomach pain improved or worsened by eating, feeling full quickly, bloating, and nausea.",
        "Avoid coffee, alcohol, and NSAIDs; eat non-irritating bland foods, and consult a doctor for H. pylori testing."
    ),
    (
        "IBS",
        "Gastrointestinal",
        "Recurrent abdominal cramping, bloating, gas, and alternating bouts of constipation and diarrhea.",
        "Identify dietary triggers with a low-FODMAP approach, practice stress reduction, and increase soluble fiber gradually."
    ),
    (
        "IBD Awareness",
        "Gastrointestinal",
        "Persistent diarrhea often with blood or mucus, abdominal cramping, fatigue, and unintended weight loss.",
        "Keep a detailed food symptom journal, stay hydrated with electrolyte fluids, and consult a gastroenterologist."
    ),
    (
        "Celiac Disease",
        "Gastrointestinal",
        "Bloating, chronic diarrhea, smelly fatty stools, weight loss, and fatigue after consuming gluten (wheat/barley/rye).",
        "Strictly adhere to a 100% gluten-free diet, read food labels carefully, and consult a registered dietitian."
    ),
    (
        "Lactose Intolerance",
        "Gastrointestinal",
        "Bloating, stomach rumbling, gas, and diarrhea occurring 30 minutes to 2 hours after consuming dairy products.",
        "Use lactose-free dairy alternatives, try plant-based milks (almond, oat), and take lactase enzyme tablets if consuming dairy."
    ),
    (
        "Constipation",
        "Gastrointestinal",
        "Hard dry stools, infrequent bowel movements (fewer than 3 per week), and straining during elimination.",
        "Increase daily dietary fiber (beans, prunes, oats), drink at least 8 glasses of water daily, and stay physically active."
    ),
    (
        "Acute Diarrhea",
        "Gastrointestinal",
        "Frequent loose watery stools, mild abdominal cramping, and dehydration.",
        "Replenish fluids with oral rehydration salts, eat bland BRAT diet foods (bananas, rice, applesauce, toast), and rest."
    ),
    (
        "Hemorrhoids",
        "Gastrointestinal",
        "Painless bright red bleeding during bowel movements, itching or discomfort around anal area, and swelling.",
        "Eat high-fiber foods, avoid straining or sitting on toilet for prolonged periods, and take warm sitz baths."
    ),
    (
        "Gallstones",
        "Gastrointestinal",
        "Sudden intense pain in upper right abdomen radiating to right shoulder or back, especially after fatty meals.",
        "Limit high-fat fried meals, maintain a healthy body weight, and seek medical evaluation if severe pain persists."
    ),
    (
        "Fatty Liver Disease",
        "Gastrointestinal",
        "Usually silent, but may cause mild right upper quadrant discomfort, fatigue, and sluggishness.",
        "Eliminate added sugars and refined carbohydrates, practice daily aerobic exercise, avoid alcohol, and maintain weight."
    ),
    (
        "Diverticulitis",
        "Gastrointestinal",
        "Constant severe pain in lower left abdomen, fever, nausea, and marked change in bowel habits.",
        "Seek medical evaluation for imaging, rest the bowel with clear liquid diet during acute flare-ups as advised by doctor."
    ),
    (
        "Food Poisoning",
        "Gastrointestinal",
        "Sudden nausea, severe vomiting, watery diarrhea, low-grade fever, and stomach cramps within hours of contaminated food.",
        "Drink small sips of oral rehydration solutions, rest, avoid solid foods until vomiting stops, and wash hands."
    ),
    (
        "Pancreatitis Awareness",
        "Gastrointestinal",
        "Severe upper abdominal pain radiating straight to the back, tenderness to touch, rapid pulse, and nausea.",
        "Seek immediate emergency medical care, withhold solid foods, avoid alcohol entirely, and stay under hospital observation."
    ),

    # =========================================================================
    # 6. NEUROLOGICAL & MENTAL HEALTH (13 Conditions)
    # =========================================================================
    (
        "Migraine",
        "Neurological",
        "Throbbing pain usually on one side of head, nausea, and intense sensitivity to light and sound.",
        "Rest in a dark quiet room, apply a cold compress to the forehead, stay well-hydrated, and track triggers."
    ),
    (
        "Tension Headache",
        "Neurological",
        "Dull aching band-like tightness around forehead, temples, or back of head and neck, worsened by stress.",
        "Practice gentle neck stretches, take screen breaks using the 20-20-20 rule, stay hydrated, and massage temples."
    ),
    (
        "Cluster Headache",
        "Neurological",
        "Severe piercing or burning pain strictly around one eye, accompanied by eye redness, tearing, and nasal congestion.",
        "Avoid alcohol and tobacco triggers, maintain consistent sleep schedules, and consult a neurologist for specific therapies."
    ),
    (
        "Sinus Headache",
        "Neurological",
        "Deep constant throbbing pressure in cheekbones, bridge of nose, and forehead, worsening when bending forward.",
        "Inhale warm steam, use saline nasal rinses, apply warm compresses, and treat underlying sinus congestion."
    ),
    (
        "Vertigo",
        "Neurological",
        "Spinning sensation when moving head, dizziness, loss of balance, and mild nausea (often BPPV).",
        "Move head slowly, sit on edge of bed before standing, avoid sudden position changes, and perform guided canalith maneuvers."
    ),
    (
        "Insomnia",
        "Neurological",
        "Difficulty falling asleep, waking up frequently during the night, and daytime fatigue or irritability.",
        "Maintain a strict sleep schedule, avoid screens 1 hour before bed, keep bedroom dark and cool, and avoid evening caffeine."
    ),
    (
        "Generalized Anxiety",
        "Neurological",
        "Excessive uncontrollable worry, muscle tension, restlessness, rapid heartbeat, and difficulty concentrating.",
        "Practice box breathing (4-4-4-4), limit caffeine and energy drinks, engage in daily walking, and seek counseling."
    ),
    (
        "Depression",
        "Neurological",
        "Persistent feelings of sadness, loss of interest in hobbies, changes in appetite or sleep, and profound fatigue.",
        "Maintain a daily routine, spend time in natural sunlight, stay connected with trusted friends, and speak with a therapist."
    ),
    (
        "Burnout and Chronic Stress",
        "Neurological",
        "Physical and emotional exhaustion, cynicism towards work, chronic headaches, digestive issues, and feeling overwhelmed.",
        "Set clear work-life boundaries, prioritize restorative sleep, take regular short breaks, and engage in relaxing hobbies."
    ),
    (
        "Panic Attack Awareness",
        "Neurological",
        "Sudden surge of intense fear, racing heart, trembling, hyperventilation, sweating, and feeling of losing control.",
        "Use 5-4-3-2-1 sensory grounding techniques, practice slow diaphragmatic breathing, and remember the episode will pass."
    ),
    (
        "Restless Legs Syndrome",
        "Neurological",
        "Uncomfortable creeping or crawling sensation in legs causing an irresistible urge to move them, worse at rest and night.",
        "Take a warm bath before bed, gently massage leg muscles, avoid evening caffeine, and check iron/ferritin levels."
    ),
    (
        "Peripheral Neuropathy",
        "Neurological",
        "Gradual numbness, tingling, burning pain, or sensitivity starting in the toes or feet, spreading upward.",
        "Inspect feet daily for injuries, wear comfortable padded footwear, manage underlying blood sugar, and consult a doctor."
    ),
    (
        "Motion Sickness",
        "Neurological",
        "Dizziness, pale skin, cold sweats, and nausea triggered by movement in cars, boats, or airplanes.",
        "Look at the distant horizon, sit in front seat or over airplane wing, open fresh air vents, and sip ginger tea."
    ),

    # =========================================================================
    # 7. MUSCULOSKELETAL, JOINT & BONE (12 Conditions)
    # =========================================================================
    (
        "Osteoarthritis",
        "Musculoskeletal",
        "Joint pain and stiffness worsening after activity, grating sensation (crepitus), and morning stiffness under 30 minutes.",
        "Engage in low-impact exercises (swimming, cycling), maintain a healthy weight, and use warm compresses for stiffness."
    ),
    (
        "Rheumatoid Arthritis",
        "Musculoskeletal",
        "Symmetrical joint swelling in hands and wrists, morning stiffness lasting over an hour, fatigue, and warm tender joints.",
        "Follow an anti-inflammatory diet rich in omega-3s, balance rest with gentle motion, and consult a rheumatologist."
    ),
    (
        "Cervical Spondylosis",
        "Musculoskeletal",
        "Neck pain, stiffness, muscle spasms across shoulders, and occasional tingling radiating into arms from desk work.",
        "Set computer monitor at eye level, do gentle chin tucks and neck rotations, use an ergonomic pillow, and avoid looking down at phones."
    ),
    (
        "Lumbar Strain",
        "Musculoskeletal",
        "Aching lower back pain, muscle tightness, stiffness, and difficulty standing upright after lifting or sitting long periods.",
        "Avoid prolonged bed rest, apply ice for first 48 hours then mild warmth, practice gentle walking, and maintain core strength."
    ),
    (
        "Sciatica",
        "Musculoskeletal",
        "Sharp shooting pain, burning, or numbness traveling from lower back through buttocks and down the back of one leg.",
        "Avoid sitting on soft low couches, do gentle hamstring and piriformis stretches, use lumbar support, and walk regularly."
    ),
    (
        "Plantar Fasciitis",
        "Musculoskeletal",
        "Sharp stabbing heel pain during the first steps in the morning or after resting, easing after walking.",
        "Perform calf and plantar fascia stretches before stepping out of bed, wear supportive arch footwear, and roll foot on a tennis ball."
    ),
    (
        "Carpal Tunnel Syndrome",
        "Musculoskeletal",
        "Numbness, tingling, and weakness in thumb, index, and middle fingers, often waking patient up at night.",
        "Wear a neutral wrist splint at night, take regular typing breaks, adjust keyboard height, and do gentle tendon glides."
    ),
    (
        "Tendonitis",
        "Musculoskeletal",
        "Dull ache and tenderness concentrated around a tendon joint (shoulder, elbow, Achilles), worse with movement.",
        "Follow R.I.C.E. principles (Rest, Ice, Compression, Elevation), avoid repetitive aggravating movements, and rest the limb."
    ),
    (
        "Frozen Shoulder",
        "Musculoskeletal",
        "Progressive shoulder stiffness, dull aching pain, and inability to raise arm or reach behind back.",
        "Perform gentle pendulum exercises within pain tolerance, apply moist heat before stretching, and consult physical therapy."
    ),
    (
        "Fibromyalgia",
        "Musculoskeletal",
        "Widespread musculoskeletal pain across both sides of body, chronic fatigue, non-restorative sleep, and brain fog.",
        "Engage in consistent gentle aerobic activity (walking/swimming), establish regular sleep routines, and practice stress management."
    ),
    (
        "Sprains and Strains",
        "Musculoskeletal",
        "Sudden pain, swelling, bruising, and limited mobility following a twist or pull of an ankle, knee, or wrist.",
        "Protect and rest the injured area, apply ice for 15-20 minutes several times daily, compress with an elastic bandage, and elevate."
    ),
    (
        "Bursitis",
        "Musculoskeletal",
        "Localized joint swelling, tenderness, warmth, and aching pain in hip, knee, or shoulder bursa sac.",
        "Rest the affected joint, cushion joint with padding, apply cold packs, and avoid direct pressure or kneeling."
    ),

    # =========================================================================
    # 8. DERMATOLOGICAL & SKIN HEALTH (11 Conditions)
    # =========================================================================
    (
        "Eczema",
        "Dermatology",
        "Dry itchy patches of skin, redness, cracking, and scaling on hands, inner elbows, or behind knees.",
        "Apply thick fragrance-free moisturizing creams immediately after lukewarm baths, and wear soft breathable cotton fabrics."
    ),
    (
        "Psoriasis",
        "Dermatology",
        "Raised red skin plaques covered with thick silvery scales, most commonly on elbows, knees, and scalp.",
        "Keep skin well-moisturized, get brief safe sunlight exposure, avoid skin injuries and smoking, and consult a dermatologist."
    ),
    (
        "Contact Dermatitis",
        "Dermatology",
        "Red itchy rash, burning, or small blisters appearing where skin touched an irritant (poison ivy, nickel, soap, perfume).",
        "Wash the area with mild soap and water, apply cool compresses and soothing calamine lotion, and identify/avoid the allergen."
    ),
    (
        "Acne Vulgaris",
        "Dermatology",
        "Blackheads, whiteheads, pimples, and tender red bumps on face, chest, and upper back.",
        "Wash face gently twice daily with mild non-comedogenic cleanser, avoid popping pimples, and use oil-free skincare."
    ),
    (
        "Rosacea",
        "Dermatology",
        "Persistent facial redness across cheeks and nose, visible blood vessels (telangiectasia), and occasional acne-like bumps.",
        "Apply daily mineral sunscreen (SPF 30+), avoid known triggers (spicy foods, hot drinks, alcohol), and use gentle cleansers."
    ),
    (
        "Hives",
        "Dermatology",
        "Raised itchy red or skin-colored welts (wheals) that appear and change location rapidly across body.",
        "Take cool baths, wear loose non-binding clothing, apply cold damp cloths, and seek emergency care if lips/throat swell."
    ),
    (
        "Ringworm",
        "Dermatology",
        "Circular ring-shaped itchy rash with raised red borders and clearer skin in the center (fungal infection).",
        "Keep skin clean and dry, apply OTC antifungal cream as directed, avoid sharing personal items, and wash towels in hot water."
    ),
    (
        "Athlete's Foot",
        "Dermatology",
        "Itching, peeling, burning, and cracked skin between toes and on soles of feet.",
        "Dry between toes thoroughly after washing, change socks daily, wear breathable footwear, and use antifungal foot powder."
    ),
    (
        "Dandruff",
        "Dermatology",
        "White oily flakes on scalp and shoulders, accompanied by mild scalp itching and redness (seborrheic dermatitis).",
        "Use medicated anti-dandruff shampoo (containing zinc pyrithione, ketoconazole, or selenium sulfide) twice weekly."
    ),
    (
        "Sunburn",
        "Dermatology",
        "Hot red tender skin that burns to touch, mild swelling, and peeling several days after UV sun exposure.",
        "Apply cool pure aloe vera gel, drink extra water, take cool showers, and stay completely out of the sun while healing."
    ),
    (
        "Cold Sores",
        "Dermatology",
        "Small fluid-filled blisters on or around the lips, preceded by a tingling or burning sensation (HSV-1).",
        "Avoid picking or touching sores, apply soothing petroleum jelly or OTC docosanol cream early, and avoid kissing or sharing utensils."
    ),

    # =========================================================================
    # 9. UROLOGICAL, RENAL & REPRODUCTIVE HEALTH (10 Conditions)
    # =========================================================================
    (
        "UTI",
        "Urological",
        "Burning sensation when urinating, frequent strong urge to pee with little output, cloudy urine, and pelvic discomfort.",
        "Drink plenty of water to flush bacteria, avoid caffeine and alcohol, and see a doctor for a urine culture and antibiotics."
    ),
    (
        "Kidney Stones",
        "Urological",
        "Severe sharp cramping pain in lower back and side (flank) radiating to groin, blood in urine (hematuria), and nausea.",
        "Drink 2-3 liters of water daily, limit dietary sodium and excess animal protein, and seek urgent medical evaluation for stone sizing."
    ),
    (
        "Overactive Bladder",
        "Urological",
        "Sudden uncontrollable urge to urinate, frequent nighttime urination (nocturia), and occasional urge incontinence.",
        "Practice pelvic floor (Kegel) exercises, schedule bladder training intervals, limit evening fluid intake, and reduce caffeine."
    ),
    (
        "BPH Awareness",
        "Urological",
        "Weak urine stream, difficulty starting urination, dribbling at end, and frequent nighttime waking in men over 50.",
        "Avoid drinking fluids 2 hours before bed, double-void to empty bladder fully, and consult a urologist for prostate health check."
    ),
    (
        "PMS",
        "Reproductive",
        "Mood swings, irritability, bloating, breast tenderness, food cravings, and fatigue occurring 1-2 weeks before menstruation.",
        "Engage in regular light exercise, reduce caffeine and salty foods, prioritize 8 hours of sleep, and practice relaxation."
    ),
    (
        "Dysmenorrhea",
        "Reproductive",
        "Throbbing or cramping pain in lower abdomen and lower back starting right before or during menstrual period.",
        "Apply a heating pad to lower abdomen, stay physically active with light walking or yoga, and stay well-hydrated."
    ),
    (
        "Menopause Support",
        "Reproductive",
        "Hot flashes, night sweats, sleep disturbances, mood changes, and vaginal dryness during midlife transition.",
        "Dress in removable layers, keep bedroom cool, practice paced breathing during hot flashes, and maintain bone-density nutrition."
    ),
    (
        "Endometriosis Awareness",
        "Reproductive",
        "Severe chronic pelvic pain during periods, painful intercourse, heavy bleeding, and gastrointestinal symptoms during cycles.",
        "Track pain symptoms with a cycle calendar, apply heat therapy, and consult a specialized gynecologist for evaluation."
    ),
    (
        "Yeast Infection",
        "Reproductive",
        "Intense vaginal itching, burning sensation during urination, and thick white clumpy discharge (cottage-cheese texture).",
        "Wear loose breathable cotton underwear, avoid scented feminine washes and douching, and consult a doctor for antifungal therapy."
    ),
    (
        "Bacterial Vaginosis",
        "Reproductive",
        "Thin watery grayish vaginal discharge, noticeable fishy odor (especially after intercourse), and mild irritation.",
        "Avoid douching and scented bubble baths, wear breathable cotton underwear, and consult a healthcare provider for antibiotic treatment."
    ),

    # =========================================================================
    # 10. SENSORY, ORAL & NUTRITIONAL HEALTH (10 Conditions)
    # =========================================================================
    (
        "Conjunctivitis",
        "Sensory",
        "Redness in whites of eyes, gritty feeling, watery or crusty discharge, and swollen eyelids (pink eye).",
        "Apply clean cool compresses, avoid rubbing eyes, wash hands frequently, and avoid wearing contact lenses until clear."
    ),
    (
        "Dry Eye Syndrome",
        "Sensory",
        "Stinging, burning, or scratchy sensation in eyes, sensitivity to light, eye fatigue, and stringy mucus.",
        "Use preservative-free lubricating artificial tears, take screen breaks using the 20-20-20 rule, and use a room humidifier."
    ),
    (
        "Stye",
        "Sensory",
        "Painful red lump along the edge of the eyelid near eyelashes, tenderness, swelling, and tearing.",
        "Apply a clean warm compress for 10-15 minutes 3-4 times daily, do not squeeze or pop the stye, and avoid eye makeup."
    ),
    (
        "Ear Infection",
        "Sensory",
        "Sharp or dull ear pain, feeling of fullness or muffled hearing, mild fever, and fluid drainage from ear.",
        "Apply a warm washcloth against ear for comfort, keep ear dry, rest upright, and consult a doctor if pain lasts over 48 hours."
    ),
    (
        "Swimmer's Ear",
        "Sensory",
        "Itching in ear canal, redness, pain when tugging outer earlobe, and yellowish discharge after swimming.",
        "Keep ear canal completely dry, tilt head to drain trapped water after showers, and see a doctor for antibiotic ear drops."
    ),
    (
        "Tinnitus Awareness",
        "Sensory",
        "Ringing, buzzing, hissing, or humming sound in one or both ears with no external sound source.",
        "Protect ears from loud noises with earplugs, use white-noise background sounds when sleeping, and reduce caffeine/stress."
    ),
    (
        "Canker Sores",
        "Sensory",
        "Small painful round ulcers with white or yellowish center and red border inside mouth, cheeks, or tongue.",
        "Rinse mouth with mild salt water, avoid acidic and spicy foods, use soft-bristled toothbrush, and apply oral soothing gels."
    ),
    (
        "Anemia",
        "Nutrition",
        "Persistent fatigue, pale skin or nail beds, weakness, dizziness, cold hands and feet, and brittle nails.",
        "Eat iron-rich foods (beans, spinach, lentils, lean poultry) paired with vitamin C, and check blood ferritin with a doctor."
    ),
    (
        "Vitamin D Deficiency",
        "Nutrition",
        "Bone pain, muscle aches, generalized fatigue, frequent sickness, and low mood.",
        "Get safe morning sunlight exposure, consume fortified foods or fatty fish, and check serum 25-hydroxyvitamin D levels."
    ),
    (
        "Dehydration",
        "Nutrition",
        "Dry mouth, dark yellow concentrated urine, extreme thirst, lightheadedness, and mild headache.",
        "Drink water or electrolyte solutions promptly, rest in a cool shaded area, and avoid intense heat exposure."
    )
]

def init_db():
    """Create the health_info table and the health_info_fts virtual table for full-text search."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop and recreate schema cleanly to support upgraded columns and FTS
    cursor.execute('DROP TABLE IF EXISTS health_info_fts')
    cursor.execute('DROP TABLE IF EXISTS health_info')

    # 1. Main relational table
    cursor.execute('''
        CREATE TABLE health_info (
            disease_id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            symptoms TEXT NOT NULL,
            precautions TEXT NOT NULL
        )
    ''')

    cursor.executemany('''
        INSERT INTO health_info (disease_name, category, symptoms, precautions)
        VALUES (?, ?, ?, ?)
    ''', HEALTH_DATA)

    # 2. SQLite FTS5 Virtual Table for high-speed Full-Text Search
    cursor.execute('''
        CREATE VIRTUAL TABLE health_info_fts USING fts5(
            disease_id UNINDEXED,
            disease_name,
            category,
            symptoms,
            precautions,
            tokenize='porter unicode61'
        )
    ''')

    # Populate FTS table
    cursor.execute('''
        INSERT INTO health_info_fts (disease_id, disease_name, category, symptoms, precautions)
        SELECT disease_id, disease_name, category, symptoms, precautions FROM health_info
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {DB_PATH} with {len(HEALTH_DATA)} conditions and FTS5 indexing.")

if __name__ == '__main__':
    init_db()
