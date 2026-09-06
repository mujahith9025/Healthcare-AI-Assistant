"""
Medical Nutrition Therapy (MNT) & Therapeutic Diet-Disease Prescriptor Module.
Provides clinically grounded, evidence-based dietary protocols, multi-condition conflict resolution,
macronutrient/micronutrient targets, and food-drug interaction cross-checks.
Conforms to ADA, AHA, KDIGO, ACG, and ESPEN clinical nutrition consensus guidelines.
"""

from typing import Dict, Any, List, Optional, Set
import re

# Comprehensive Clinical Nutrition Protocols Database
NUTRITION_PROTOCOLS: Dict[str, Dict[str, Any]] = {
    # 1. Hypertension & Cardiovascular
    "hypertension": {
        "id": "hypertension",
        "name": "DASH Protocol (Dietary Approaches to Stop Hypertension)",
        "condition": "Hypertension & Cardiovascular Health",
        "icon": "❤️",
        "category": "cardiovascular",
        "principles": "Reduces systolic/diastolic arterial pressure through sodium restriction, high potassium, magnesium, and calcium intake.",
        "macro_targets": {
            "sodium": "< 1,500 – 2,300 mg/day",
            "potassium": "3,500 – 4,700 mg/day (if renal function normal)",
            "magnesium": "400 – 500 mg/day",
            "fiber": "≥ 30 g/day",
            "saturated_fat": "< 6% of total daily calories"
        },
        "prioritize_foods": [
            "Leafy green vegetables (spinach, kale, Swiss chard)",
            "Berries (blueberries, strawberries, blackberries)",
            "Beets and beetroot juice (high natural dietary nitrates)",
            "Unsalted raw nuts and seeds (flaxseeds, chia, walnuts, pumpkin seeds)",
            "Whole grains (steel-cut oats, quinoa, brown rice, whole wheat)",
            "Fat-free / low-fat plain Greek yogurt and milk",
            "Fatty cold-water fish (wild salmon, sardines, mackerel)",
            "Garlic, olive oil, and potassium-rich bananas and avocados"
        ],
        "avoid_foods": [
            "Cured, processed, and deli meats (bacon, sausage, hot dogs, salami)",
            "Canned soups, broths, and salted bouillon cubes",
            "Commercial frozen pre-packaged dinners and fast foods",
            "Salted snacks (potato chips, pretzels, salted roasted nuts)",
            "High-sodium condiments (soy sauce, teriyaki, fish sauce, ketchup)",
            "Excessive alcohol (>1 standard drink/day for women, >2 for men)",
            "Licorice root supplements (contains glycyrrhizin which raises BP)"
        ],
        "sample_meal_plan": {
            "breakfast": "Steel-cut oatmeal topped with fresh blueberries, ground flaxseed, and a dash of Ceylon cinnamon + unsweetened almond milk.",
            "lunch": "Mediterranean spinach salad with grilled wild salmon, sliced avocado, cucumbers, cherry tomatoes, and extra virgin olive oil/lemon dressing.",
            "dinner": "Herb-roasted skinless chicken breast with roasted beets, steamed broccoli, and 1/2 cup cooked quinoa.",
            "snacks": "A small handful of unsalted walnuts + 1 medium banana or low-fat plain Greek yogurt."
        },
        "guideline_sources": "American Heart Association (AHA) & ACC Guidelines"
    },

    # 2. Type 2 Diabetes & Insulin Resistance
    "diabetes": {
        "id": "diabetes",
        "name": "Low-Glycemic Mediterranean Metabolic Protocol",
        "condition": "Type 2 Diabetes, Prediabetes & Insulin Resistance",
        "icon": "🩸",
        "category": "metabolic",
        "principles": "Stabilizes postprandial blood glucose, enhances insulin sensitivity, and lowers HbA1c through low glycemic load and high soluble fiber.",
        "macro_targets": {
            "carbohydrate": "35 – 45% (complex, low-GI sources only)",
            "fiber": "35 – 50 g/day (minimum 15g soluble fiber)",
            "protein": "20 – 25% (lean, plant & seafood sources)",
            "healthy_fats": "30 – 35% (monounsaturated & omega-3)",
            "added_sugars": "0 g/day"
        },
        "prioritize_foods": [
            "Non-starchy cruciferous vegetables (broccoli, cauliflower, Brussels sprouts)",
            "Legumes and pulses (lentils, chickpeas, black beans)",
            "Berries and green apples (low-glycemic index fruits)",
            "Avocados, extra virgin olive oil, and raw almonds",
            "Chia seeds, hemp seeds, and psyllium husk",
            "Wild-caught fish, organic tofu, and skinless poultry",
            "Cinnamon, apple cider vinegar, and unsweetened green tea"
        ],
        "avoid_foods": [
            "Sugar-sweetened beverages (soda, fruit juices, sweet tea, energy drinks)",
            "Refined grains (white bread, white rice, standard pasta, pastries)",
            "High-fructose corn syrup, candy, pastries, and table sugar",
            "Deep-fried foods and trans-fats (fried chicken, French fries)",
            "Sweetened flavored yogurts and instant flavored oatmeals",
            "Dried fruits with added sugars (candied cranberries, glazed dates)"
        ],
        "sample_meal_plan": {
            "breakfast": "Scrambled eggs or tofu with sautéed baby spinach, mushrooms, and half an avocado, served with 1 slice 100% sprouted grain toast.",
            "lunch": "Warm lentil and vegetable bowl with kale, roasted bell peppers, roasted pumpkin seeds, and tahini-lemon dressing.",
            "dinner": "Pan-seared Atlantic cod or chicken breast with sautéed asparagus and cauliflower rice with garlic and olive oil.",
            "snacks": "Sliced cucumber rounds with 2 tbsp hummus or a handful of raw almonds."
        },
        "guideline_sources": "American Diabetes Association (ADA) Standards of Care"
    },

    # 3. Chronic Kidney Disease (CKD Stages 3-5)
    "ckd": {
        "id": "ckd",
        "name": "Renal Protective Protocol (Controlled Electrolytes & Protein)",
        "condition": "Chronic Kidney Disease (Stages 3 to 5 non-dialysis)",
        "icon": "🫘",
        "category": "renal",
        "principles": "Slows renal decline and prevents uremic toxicity by strictly regulating protein burden, serum phosphorus, potassium, and sodium.",
        "macro_targets": {
            "protein": "0.6 – 0.8 g/kg body weight/day (non-dialysis)",
            "sodium": "< 1,500 – 2,000 mg/day",
            "phosphorus": "< 800 – 1,000 mg/day (avoid inorganic additives)",
            "potassium": "< 2,000 – 2,500 mg/day (individualized by lab values)",
            "fluids": "As individualized by nephrologist"
        },
        "prioritize_foods": [
            "Low-potassium fruits (apples, berries, grapes, pineapples, pears)",
            "Low-potassium vegetables (cabbage, cauliflower, green beans, cucumbers)",
            "White rice, white sourdough bread (lower phosphorus than whole wheat in advanced CKD)",
            "Egg whites (high biological value, low phosphorus protein)",
            "Olive oil and canola oil (healthy non-protein calorie sources)",
            "Fresh unenhanced lean meats (in strictly measured portions)"
        ],
        "avoid_foods": [
            "Phosphorus additives (look for 'PHOS' on ingredient labels: sodas, processed meats)",
            "High-potassium fruits (bananas, oranges, cantaloupe, kiwis, dried fruits)",
            "High-potassium vegetables (potatoes, sweet potatoes, tomatoes, spinach, avocados)",
            "Nuts, seeds, peanut butter, and dried beans (high phosphorus & potassium)",
            "Salt substitutes containing potassium chloride (e.g. Nu-Salt, NoSalt)",
            "Dairy products in large quantities (milk, hard cheeses, ice cream)"
        ],
        "sample_meal_plan": {
            "breakfast": "Egg white omelet with diced bell peppers and onions, served with 1 slice white sourdough bread and fresh sliced apple.",
            "lunch": "Grilled chicken breast (2 oz) over shredded green cabbage and cucumber salad with olive oil and white vinegar.",
            "dinner": "Baked white fish (3 oz) served with steamed cauliflower florets and 1/2 cup jasmine white rice.",
            "snacks": "Fresh blueberries or red grapes."
        },
        "guideline_sources": "KDIGO Clinical Practice Guideline for Diabetes and CKD"
    },

    # 4. Gout & Hyperuricemia
    "gout": {
        "id": "gout",
        "name": "Low-Purine & Uric Acid Clearance Protocol",
        "condition": "Hyperuricemia, Gout & Uric Acid Nephrolithiasis",
        "icon": "🦶",
        "category": "rheumatology",
        "principles": "Lowers serum uric acid synthesis and accelerates urinary clearance to prevent acute inflammatory joint flares.",
        "macro_targets": {
            "hydration": "≥ 3.0 Liters water/day (promotes renal uric acid excretion)",
            "purine_intake": "< 100 – 150 mg/day",
            "vitamin_c": "500 – 1,000 mg/day (uricosuric action)",
            "fructose": "Strictly minimized"
        },
        "prioritize_foods": [
            "Tart cherries and tart cherry juice (anthocyanins significantly lower uric acid)",
            "Low-fat and fat-free dairy (milk, yogurt, cottage cheese promote excretion)",
            "Vitamin C-rich fruits and vegetables (bell peppers, strawberries, lemons)",
            "Complex low-purine carbohydrates (oats, brown rice, whole wheat)",
            "Hydrating liquids (pure water, unsweetened black coffee, lemon water)",
            "Plant-based proteins (tofu, peas - plant purines do not trigger gout)"
        ],
        "avoid_foods": [
            "Organ meats (liver, kidneys, sweetbreads, brain)",
            "High-purine seafood (anchovies, sardines, mackerel, scallops, mussels, tuna)",
            "Game meats and excessive red meat (beef, lamb, pork)",
            "Beer, ale, and grain spirits (high yeast purines and impairs clearance)",
            "High-fructose corn syrup (HFCS) and fruit juice concentrates",
            "Yeast extracts (Marmite, Brewer's yeast supplements)"
        ],
        "sample_meal_plan": {
            "breakfast": "Low-fat Greek yogurt parfait with 1/2 cup fresh tart cherries and rolled oats.",
            "lunch": "Tofu and roasted vegetable wrap in a whole wheat tortilla with mixed field greens and olive oil vinaigrette.",
            "dinner": "Baked lemon-herb chicken breast (3 oz) served with steamed green beans and a baked sweet potato.",
            "snacks": "A glass of water with fresh lemon squeeze + 1 fresh pear."
        },
        "guideline_sources": "American College of Rheumatology (ACR) Gout Guidelines"
    },

    # 5. GERD & Acid Reflux
    "gerd": {
        "id": "gerd",
        "name": "Anti-Reflux & Lower Esophageal Sphincter (LES) Protective Protocol",
        "condition": "Gastroesophageal Reflux Disease (GERD) & Esophagitis",
        "icon": "🥣",
        "category": "gastrointestinal",
        "principles": "Prevents gastric hyperacidity and relaxes LES tone through alkaline food choices and meal timing rules.",
        "macro_targets": {
            "meal_timing": "Stop all food intake at least 3 hours before sleep",
            "meal_size": "Small, frequent meals (4–5 per day) instead of large meals",
            "dietary_fat": "Moderate to low (excess fat delays gastric emptying)"
        },
        "prioritize_foods": [
            "Oatmeal, rolled oats, and whole grain bread",
            "Non-citrus fruits (bananas, melons, apples, pears)",
            "Lean poultry, turkey, and white fish (poached, baked, or grilled)",
            "Green vegetables (asparagus, broccoli, green beans, cucumbers, celery)",
            "Ginger and chamomile herbal tea (natural GI soothing agents)",
            "Almond milk and low-fat plant milks"
        ],
        "avoid_foods": [
            "Citrus fruits and juices (oranges, grapefruits, lemons, limes)",
            "Tomato products (marinara sauce, ketchup, tomato soup)",
            "Chocolate, peppermint, and spearmint (chemically relaxes the LES)",
            "Caffeinated coffee, espresso, and energy drinks",
            "Carbonated beverages and sodas (increases intragastric pressure)",
            "Deep-fried, high-fat foods and spicy hot peppers",
            "Raw garlic and raw onions"
        ],
        "sample_meal_plan": {
            "breakfast": "Warm oatmeal made with almond milk, topped with sliced banana and a drizzle of honey.",
            "lunch": "Turkey breast sandwich on whole wheat bread with cucumber slices and romaine lettuce (no mustard/mayo).",
            "dinner": "Baked chicken breast with steamed zucchini and roasted butternut squash.",
            "snacks": "Fresh cantaloupe slices or a cup of warm chamomile tea."
        },
        "guideline_sources": "American College of Gastroenterology (ACG) GERD Guidelines"
    },

    # 6. Irritable Bowel Syndrome (IBS)
    "ibs": {
        "id": "ibs",
        "name": "3-Phase Low-FODMAP Protocol",
        "condition": "Irritable Bowel Syndrome (IBS-D, IBS-C, IBS-M)",
        "icon": "🌱",
        "category": "gastrointestinal",
        "principles": "Reduces osmotic water shifts and bacterial fermentation in the colon by restricting fermentable oligosaccharides, disaccharides, monosaccharides, and polyols.",
        "macro_targets": {
            "phases": "Phase 1: Elimination (2–6 wks) -> Phase 2: Reintroduction -> Phase 3: Personalization",
            "soluble_fiber": "Increase gradually (e.g. psyllium husk)"
        },
        "prioritize_foods": [
            "Proteins: Eggs, firm tofu, chicken, turkey, beef, fish",
            "Grains: Rice, quinoa, oats, gluten-free bread/pasta",
            "Vegetables: Spinach, carrots, cucumbers, bell peppers, zucchini, potatoes",
            "Fruits: Blueberries, strawberries, oranges, kiwis, unripe bananas",
            "Fats & Dairy: Garlic-infused olive oil, lactose-free milk/yogurt, hard cheeses (Cheddar, Parmesan)"
        ],
        "avoid_foods": [
            "High Fructose: Honey, agave, high-fructose corn syrup, apples, mangoes",
            "Lactose: Cow's milk, soft cheeses (ricotta, cottage cheese), regular ice cream",
            "Fructans: Garlic, onions, wheat, rye, inulin / chicory root fiber",
            "Galactooligosaccharides (GOS): Beans, lentils, chickpeas, soy milk made from whole beans",
            "Polyols: Sorbitol, mannitol, xylitol (sugar-free gums), mushrooms, cauliflowers, plums, peaches"
        ],
        "sample_meal_plan": {
            "breakfast": "Gluten-free oats cooked in lactose-free milk with fresh strawberries and a pinch of chia seeds.",
            "lunch": "Grilled chicken breast over quinoa, chopped carrots, cucumbers, and spinach with garlic-infused olive oil.",
            "dinner": "Pan-seared salmon with roasted zucchini and a baked potato with a sprinkle of aged cheddar.",
            "snacks": "1 ripe mandarin orange or a handful of roasted peanuts."
        },
        "guideline_sources": "Monash University FODMAP Research Center"
    },

    # 7. Non-Alcoholic Fatty Liver Disease (NAFLD)
    "nafld": {
        "id": "nafld",
        "name": "Anti-Steatotic Mediterranean Liver Protocol",
        "condition": "NAFLD / Metabolic Dysfunction-Associated Steatotic Liver Disease (MASLD)",
        "icon": "🧪",
        "category": "hepatic",
        "principles": "Reverses hepatic steatosis, reduces liver enzyme elevations (ALT/AST), and improves systemic insulin sensitivity.",
        "macro_targets": {
            "added_sugars": "0 g/day (specifically eliminate industrial fructose)",
            "omega_3": "≥ 2,000 mg/day EPA/DHA",
            "weight_target": "5 – 10% gradual body weight reduction if indicated"
        },
        "prioritize_foods": [
            "Coffee (2–3 cups daily of black/filtered coffee has strong anti-fibrotic evidence)",
            "Extra virgin olive oil (high polyphenol content reduces hepatic lipid accumulation)",
            "Fatty fish (salmon, trout, sardines rich in omega-3 fatty acids)",
            "Cruciferous vegetables and artichokes",
            "Nuts (walnuts, almonds rich in vitamin E and antioxidants)",
            "Green tea and rosemary/turmeric spices"
        ],
        "avoid_foods": [
            "Fructose-sweetened beverages, fruit juices, and table sugar",
            "Alcohol in any quantity (strictly abstain during active liver inflammation)",
            "Ultra-processed convenience foods and industrial seed oils high in trans fats",
            "Refined carbohydrates and white flour products",
            "Saturated animal fats and processed meats"
        ],
        "sample_meal_plan": {
            "breakfast": "Black coffee + 2 poached eggs with sautéed kale and sliced avocado on whole grain toast.",
            "lunch": "Mediterranean tuna salad with mixed greens, cherry tomatoes, walnuts, and extra virgin olive oil.",
            "dinner": "Baked salmon with roasted Brussels sprouts and half a sweet potato.",
            "snacks": "A handful of raw walnuts + 1 cup of unsweetened green tea."
        },
        "guideline_sources": "EASL-EASD-EASO Clinical Practice Guidelines for NAFLD"
    },

    # 8. Hyperlipidemia & High Cholesterol
    "hyperlipidemia": {
        "id": "hyperlipidemia",
        "name": "Therapeutic Lifestyle Changes (TLC) Lipid-Lowering Protocol",
        "condition": "Hypercholesterolemia, Elevated LDL-C & Dyslipidemia",
        "icon": "🫀",
        "category": "cardiovascular",
        "principles": "Lowers atherogenic apolipoprotein B and LDL cholesterol through saturated fat reduction, plant stanols/sterols, and viscous soluble fiber.",
        "macro_targets": {
            "saturated_fat": "< 5 – 6% of total daily calories",
            "dietary_cholesterol": "< 200 mg/day",
            "soluble_fiber": "10 – 25 g/day (binds intestinal bile acids)",
            "plant_sterols": "2 g/day (blocks cholesterol absorption)"
        },
        "prioritize_foods": [
            "Oat bran, barley, and steel-cut oats (rich in beta-glucan)",
            "Beans, chickpeas, and kidney beans (viscous fiber powerhouse)",
            "Plant sterol/stanol-enriched foods",
            "Apples, citrus fruits, and pears (rich in pectin)",
            "Tree nuts (almonds, walnuts, pistachios)",
            "Soy protein (edamame, unsweetened soy milk, tofu)",
            "Cold-pressed extra virgin olive oil and avocado oil"
        ],
        "avoid_foods": [
            "Fatty cuts of red meat, poultry skin, and lard",
            "Full-fat dairy (butter, heavy cream, full-fat cheeses)",
            "Tropical oils (palm oil, palm kernel oil, coconut oil in excess)",
            "Commercial baked goods, pastries, and hydrogenated shortenings",
            "Deep-fried fast foods"
        ],
        "sample_meal_plan": {
            "breakfast": "Warm oat bran porridge with 1 tbsp chia seeds, chopped almonds, and diced apple.",
            "lunch": "Black bean and avocado bowl with quinoa, cilantro, roasted bell peppers, and lime-olive oil dressing.",
            "dinner": "Grilled Atlantic salmon with steamed asparagus and a side of barley pilaf.",
            "snacks": "1 fresh orange + a small handful of raw pistachios."
        },
        "guideline_sources": "National Cholesterol Education Program (NCEP) TLC Guidelines"
    },

    # 9. Celiac Disease
    "celiac": {
        "id": "celiac",
        "name": "Strict Gluten-Free Mucosal Healing Protocol",
        "condition": "Celiac Disease & Dermatitis Herpetiformis",
        "icon": "🌾",
        "category": "gastrointestinal",
        "principles": "Achieves complete intestinal villous healing and prevents autoimmune malabsorption by eliminating all gluten proteins.",
        "macro_targets": {
            "gluten_threshold": "< 20 ppm (strict 100% elimination)",
            "micronutrient_monitoring": "Iron, Folate, Vitamin B12, Vitamin D, Zinc"
        },
        "prioritize_foods": [
            "Naturally gluten-free grains: Quinoa, certified GF oats, brown rice, millet, buckwheat",
            "All fresh whole fruits and fresh raw vegetables",
            "Unprocessed lean meats, poultry, seafood, and eggs",
            "Nuts, seeds, and unflavored plain legumes",
            "Plain dairy, olive oil, and certified gluten-free labeled products"
        ],
        "avoid_foods": [
            "Wheat, barley, rye, triticale, spelt, kamut, farro, semolina, durum",
            "Regular bread, pasta, pizza crusts, flour tortillas, cookies, and beer",
            "Soy sauce (unless explicitly labeled certified Tamari / Gluten-Free)",
            "Malt vinegar, malt flavoring, and beer/ale",
            "Cross-contaminated shared fryers (restaurant French fries cooked in same oil as breaded items)"
        ],
        "sample_meal_plan": {
            "breakfast": "Certified gluten-free rolled oats with almond milk, chia seeds, and fresh berries.",
            "lunch": "Quinoa salad with grilled chicken, cherry tomatoes, cucumbers, Kalamata olives, and olive oil.",
            "dinner": "Baked salmon with roasted sweet potatoes and steamed green beans.",
            "snacks": "Fresh apple slices with natural peanut butter."
        },
        "guideline_sources": "American College of Gastroenterology (ACG) Celiac Guidelines"
    },

    # 10. Iron-Deficiency Anemia
    "anemia": {
        "id": "anemia",
        "name": "Hemoglobin Synthesis & Iron Bioavailability Protocol",
        "condition": "Iron-Deficiency Anemia & Low Serum Ferritin",
        "icon": "🩸",
        "category": "hematology",
        "principles": "Maximizes non-heme and heme iron absorption while eliminating intestinal chelators at meal times.",
        "macro_targets": {
            "elemental_iron": "18 mg/day (women) / 8 mg/day (men); higher in diagnosed deficiency",
            "vitamin_c_pairing": "≥ 50 – 100 mg Vitamin C paired with every iron-rich meal"
        },
        "prioritize_foods": [
            "Heme Iron (highly bioavailable): Lean red beef, turkey dark meat, liver, sardines, clams",
            "Non-Heme Iron: Lentils, black beans, spinach, fortified cereals, pumpkin seeds, tofu",
            "Vitamin C enhancers (pair simultaneously): Bell peppers, broccoli, citrus, strawberries, tomatoes",
            "Cast iron skillet cooking (naturally infuses dietary iron into prepared meals)"
        ],
        "avoid_foods": [
            "Tea and coffee consumed WITH meals (tannins and polyphenols inhibit iron absorption by up to 70%)",
            "High-dose calcium supplements or dairy consumed at the exact same time as iron meals",
            "Whole bran cereals high in phytates when consumed without Vitamin C"
        ],
        "sample_meal_plan": {
            "breakfast": "Fortified whole grain cereal with sliced strawberries and kiwi + a glass of 100% orange juice (wait 1 hour before morning coffee).",
            "lunch": "Iron-rich lentil soup served with a raw bell pepper and baby spinach salad dressed with fresh lemon juice.",
            "dinner": "Lean beef stir-fry cooked in a cast iron skillet with broccoli florets, snap peas, and brown rice.",
            "snacks": "Pumpkin seeds (pepitas) and dried unsulfured apricots."
        },
        "guideline_sources": "WHO Guidelines on Iron Bioavailability & Supplementation"
    },

    # 11. Osteopenia & Osteoporosis
    "osteoporosis": {
        "id": "osteoporosis",
        "name": "Bone Density & Skeletal Matrix Protocol",
        "condition": "Osteopenia, Osteoporosis & Fracture Prevention",
        "icon": "🦴",
        "category": "endocrinology",
        "principles": "Enhances bone mineral density and mineralization through balanced calcium, Vitamin D3, Vitamin K2, and adequate protein.",
        "macro_targets": {
            "calcium": "1,000 – 1,200 mg/day (dietary preferred over high-dose supplements)",
            "vitamin_d": "800 – 2,000 IU/day",
            "protein": "1.0 – 1.2 g/kg body weight/day (supports collagen bone scaffolding)"
        },
        "prioritize_foods": [
            "Dairy products: Low-fat Greek yogurt, kefir, milk, hard cheeses",
            "Calcium-set organic tofu and fortified plant milks",
            "Canned sardines and wild salmon with soft edible bones",
            "Dark leafy greens (bok choy, kale, collard greens - low oxalate sources)",
            "Prunes / dried plums (evidence shows 5–6 daily helps prevent bone loss)",
            "Fermented foods (natto, fermented cheeses rich in natural Vitamin K2)"
        ],
        "avoid_foods": [
            "Excess sodium (>2,300 mg/day increases urinary calcium excretion)",
            "Cola beverages (contains phosphoric acid which impairs bone mineral balance)",
            "Excessive alcohol intake (>2 drinks/day suppresses osteoblast bone formation)",
            "Chronic extreme protein deficiency"
        ],
        "sample_meal_plan": {
            "breakfast": "Plain Greek yogurt topped with 4 chopped prunes, sliced almonds, and a drizzle of honey.",
            "lunch": "Canned wild salmon salad (with soft edible bones) over baby kale and shredded bok choy with sesame dressing.",
            "dinner": "Calcium-set tofu and vegetable stir-fry with broccoli, snap peas, and brown rice.",
            "snacks": "1 glass of calcium & vitamin D fortified almond milk + 1 string cheese."
        },
        "guideline_sources": "National Osteoporosis Foundation (NOF) Clinical Guidelines"
    },

    # 12. Migraine & Chronic Headaches
    "migraine": {
        "id": "migraine",
        "name": "Neuro-Vascular Trigger Elimination Protocol",
        "condition": "Migraine, Chronic Daily Headache & Vestibular Migraine",
        "icon": "🧠",
        "category": "neurology",
        "principles": "Stabilizes neurovascular tone by eliminating tyramine, nitrates, histamine, and artificial additives while ensuring stable blood glucose.",
        "macro_targets": {
            "hydration": "≥ 2.5 Liters water/day (dehydration is #1 acute trigger)",
            "magnesium": "400 – 600 mg/day (dietary + supplemental under guidance)",
            "riboflavin_b2": "400 mg/day"
        },
        "prioritize_foods": [
            "Fresh unaged meats, poultry, and fresh wild fish",
            "Magnesium-rich foods (pumpkin seeds, spinach, quinoa, black beans)",
            "Omega-3 fatty acids (salmon, chia seeds)",
            "Ginger (proven natural anti-nausea and anti-neuroinflammatory properties)",
            "Regular, scheduled meals (prevents hypoglycemia-induced migraine attacks)"
        ],
        "avoid_foods": [
            "Aged cheeses (parmesan, blue cheese, cheddar - high in tyramine)",
            "Cured meats containing nitrates/nitrites (hot dogs, salami, bacon)",
            "Monosodium glutamate (MSG) and hydrolyzed vegetable proteins",
            "Artificial sweeteners (specifically aspartame and sucralose)",
            "Red wine and dark spirits (tannins, histamines, congeners)",
            "Skipping meals or fasting for prolonged irregular intervals"
        ],
        "sample_meal_plan": {
            "breakfast": "Oatmeal with chia seeds, blueberries, and pumpkin seeds + large glass of water.",
            "lunch": "Fresh roasted chicken breast with quinoa and steamed spinach with olive oil.",
            "dinner": "Fresh baked cod with baked sweet potato and steamed green beans.",
            "snacks": "Fresh apple with sunflower seed butter + ginger herbal tea."
        },
        "guideline_sources": "American Headache Society (AHS) Nutrition Guidance"
    }
}


DIETARY_PREFERENCES_CATALOG = {
    "vegetarian": {
        "name": "Vegetarian",
        "icon": "🥬",
        "rules": "Excludes all animal meats and poultry; includes plant proteins, dairy, and eggs."
    },
    "vegan": {
        "name": "Vegan",
        "icon": "🌱",
        "rules": "Strict 100% plant-based; excludes meat, poultry, seafood, dairy, eggs, and honey."
    },
    "gluten_free": {
        "name": "Gluten-Free",
        "icon": "🌾",
        "rules": "Excludes all wheat, barley, rye, triticale, and cross-contaminated oats."
    },
    "dairy_free": {
        "name": "Dairy-Free / Lactose-Free",
        "icon": "🥛",
        "rules": "Excludes bovine milk, cream, cheese, butter, and whey."
    },
    "low_sodium": {
        "name": "Strict Low-Sodium (<1.5g)",
        "icon": "🧂",
        "rules": "Caps total daily dietary sodium below 1,500 mg for severe fluid retention or resistant hypertension."
    },
    "low_carb": {
        "name": "Low-Carb / Ketogenic",
        "icon": "🥑",
        "rules": "Restricts net carbohydrates to <50g/day, focusing on healthy fats and adequate protein."
    },
    "nut_free": {
        "name": "Nut-Free (Allergy Safe)",
        "icon": "🥜",
        "rules": "Excludes all tree nuts and peanuts."
    }
}


def get_all_nutrition_protocols() -> Dict[str, Any]:
    """Returns catalog of all standard Medical Nutrition Therapy condition protocols and preferences."""
    conditions_list = []
    for cid, cdata in NUTRITION_PROTOCOLS.items():
        conditions_list.append({
            "id": cid,
            "name": cdata.get("name", cid),
            "condition": cdata.get("condition", ""),
            "icon": cdata.get("icon", "🥗"),
            "category": cdata.get("category", "general")
        })

    return {
        "success": True,
        "protocols": NUTRITION_PROTOCOLS,
        "conditions": conditions_list,
        "dietary_preferences": DIETARY_PREFERENCES_CATALOG
    }


def check_food_drug_interactions(medications: List[str]) -> List[Dict[str, Any]]:
    """
    Screens active patient medications for critical clinical food/nutrient interactions.
    """
    warnings = []
    if not medications:
        return warnings

    meds_norm = [m.lower().strip() for m in medications if m and str(m).strip()]

    for med in meds_norm:
        # 1. Warfarin / Coumadin + Vitamin K
        if "warfarin" in med or "coumadin" in med or "jantoven" in med:
            warnings.append({
                "drug": "Warfarin (Coumadin)",
                "food_nutrient": "Vitamin K (Leafy Greens, Broccoli)",
                "severity": "HIGH",
                "warning": "Vitamin K opposes Warfarin's anticoagulant mechanism, decreasing INR and increasing thromboembolism risk.",
                "action": "Maintain a steady, consistent daily intake of green leafy vegetables. Do not make drastic changes to Vitamin K intake without consulting your anticoagulation clinic."
            })

        # 2. Statins & Calcium Channel Blockers + Grapefruit
        if any(s in med for s in ["atorvastatin", "lipitor", "simvastatin", "zocor", "lovastatin", "amlodipine", "norvasc", "felodipine", "nifedipine"]):
            matched_name = "Atorvastatin / Simvastatin / CCB"
            warnings.append({
                "drug": matched_name,
                "food_nutrient": "Grapefruit & Seville Oranges",
                "severity": "HIGH",
                "warning": "Furanocoumarins in grapefruit irreversibly inhibit intestinal CYP3A4 enzymes, causing toxic drug accumulation and elevating rhabdomyolysis or severe hypotension risk.",
                "action": "Avoid grapefruit, grapefruit juice, and Seville oranges entirely during therapy."
            })

        # 3. Levothyroxine + Calcium / Iron / Soy / Coffee
        if "levothyroxine" in med or "synthroid" in med or "tirosint" in med or "euthyrox" in med:
            warnings.append({
                "drug": "Levothyroxine (Synthroid)",
                "food_nutrient": "Calcium, Iron Supplements, Soy & Espresso",
                "severity": "MODERATE",
                "warning": "Dietary calcium, iron salts, and soy protein bind to levothyroxine in the GI tract, drastically impairing systemic absorption.",
                "action": "Take levothyroxine with plain water on an empty stomach 30–60 minutes before breakfast. Separate calcium/iron supplements by at least 4 hours."
            })

        # 4. Antibiotics (Fluoroquinolones & Tetracyclines) + Dairy / Minerals
        if any(abx in med for abx in ["ciprofloxacin", "cipro", "levofloxacin", "levaquin", "doxycycline", "tetracycline", "minocycline"]):
            warnings.append({
                "drug": "Fluoroquinolone / Tetracycline Antibiotic",
                "food_nutrient": "Dairy Products, Calcium-Fortified Juices & Antacids",
                "severity": "HIGH",
                "warning": "Divalent and trivalent cations (Ca2+, Mg2+, Fe2+, Al3+) form insoluble chelates with the antibiotic, reducing bioavailability by up to 90%.",
                "action": "Avoid milk, yogurt, and mineral supplements 2 hours before and 4 hours after taking your antibiotic dose."
            })

        # 5. MAO Inhibitors + Tyramine
        if any(maoi in med for maoi in ["phenelzine", "nardil", "tranylcypromine", "parnate", "isocarboxazid", "marplan", "selegiline"]):
            warnings.append({
                "drug": "MAO Inhibitor (Phenelzine / Tranylcypromine)",
                "food_nutrient": "Tyramine-Rich Foods (Aged Cheese, Cured Meats, Draft Beer)",
                "severity": "CRITICAL",
                "warning": "MAO inhibition blocks intestinal tyramine breakdown; uninhibited tyramine causes massive peripheral norepinephrine release leading to life-threatening Hypertensive Crisis.",
                "action": "Strictly eliminate aged cheeses, cured meats, fermented soy (soy sauce, tofu, miso), sauerkraut, and draft beers."
            })

        # 6. Lithium + Sodium & Hydration
        if "lithium" in med or "eskalith" in med or "lithobid" in med:
            warnings.append({
                "drug": "Lithium Carbonate",
                "food_nutrient": "Dietary Sodium & Fluid Balance",
                "severity": "HIGH",
                "warning": "Low dietary sodium or dehydration causes compensatory proximal renal reabsorption of lithium, precipitating neurotoxicity.",
                "action": "Maintain consistent baseline dietary sodium and drink 2–3 liters of water daily. Avoid crash low-sodium diets."
            })

        # 7. ACE Inhibitors / ARBs + Potassium Salt Substitutes
        if any(ace in med for ace in ["lisinopril", "enalapril", "ramipril", "losartan", "valsartan", "spironolactone"]):
            warnings.append({
                "drug": "ACE Inhibitor / ARB / Spironolactone",
                "food_nutrient": "Potassium Chloride Salt Substitutes",
                "severity": "HIGH",
                "warning": "RAAS blockade reduces renal potassium excretion; concurrent high potassium intake or KCl salt substitutes can induce fatal hyperkalemia.",
                "action": "Avoid 'No-Salt' or 'Lite-Salt' potassium chloride substitutes; use culinary herbs and citrus instead."
            })

    return warnings


def reconcile_dietary_conflicts(conditions: List[str]) -> List[Dict[str, Any]]:
    """
    Identifies conflicting dietary instructions across multiple comorbidities.
    Reconciles conflicts based on organ preservation precedence (KDIGO, AHA, ADA).
    """
    conflicts = []
    norm_conditions = [c.lower().strip() for c in conditions if c and str(c).strip()]

    # Conflict 1: DASH (High Potassium) vs CKD (Low Potassium)
    if "hypertension" in norm_conditions and "ckd" in norm_conditions:
        conflicts.append({
            "conflict": "DASH Potassium Target vs. CKD Renal Potassium Restriction",
            "severity": "CRITICAL",
            "primary_priority": "Renal Organ Protection (CKD)",
            "conditions_involved": ["Hypertension (DASH)", "Chronic Kidney Disease (CKD)"],
            "conflict_explanation": "Standard DASH diet for hypertension encourages high potassium (3,500–4,700 mg/day), but advanced CKD requires strict potassium restriction (<2,000 mg/day) to prevent life-threatening hyperkalemia.",
            "resolution": "Renal potassium restriction (<2,000 mg/day) takes absolute precedence over DASH targets to prevent cardiac arrhythmias. Control blood pressure through strict sodium restriction (<1,500 mg/day) and medications under nephrologist supervision."
        })

    # Conflict 2: Gout (High Protein Purines) vs Diabetes (Low Carb / High Protein)
    if "gout" in norm_conditions and "diabetes" in norm_conditions:
        conflicts.append({
            "conflict": "Diabetes Low-Carb Protein vs. Gout Purine Minimization",
            "severity": "MODERATE",
            "primary_priority": "Dual Metabolic Balance",
            "conditions_involved": ["Gout", "Type 2 Diabetes"],
            "conflict_explanation": "Low-carb diabetes diets frequently rely on red meats and seafood, which are high in purines and can provoke severe gout attacks.",
            "resolution": "Emphasize low-purine plant proteins (tofu, low-fat Greek yogurt, eggs) and high-fiber, low-glycemic vegetables rather than animal purines or refined carbohydrates."
        })

    # Conflict 3: GERD (Low Fat / Frequent Meals) vs NAFLD (High Healthy Fats)
    if "gerd" in norm_conditions and "nafld" in norm_conditions:
        conflicts.append({
            "conflict": "GERD Low-Fat LES Tone vs. NAFLD Monounsaturated Fat Density",
            "severity": "MODERATE",
            "primary_priority": "Symptom & Hepatic Protection",
            "conditions_involved": ["GERD", "Fatty Liver (NAFLD)"],
            "conflict_explanation": "NAFLD guidelines encourage generous extra virgin olive oil and nuts, but concentrated fats can relax the lower esophageal sphincter and trigger acid reflux in GERD.",
            "resolution": "Distribute portion-controlled healthy unsaturated fats in small amounts across meals rather than concentrated large servings, and avoid eating any fats within 3 hours of sleep."
        })

    # Conflict 4: Celiac (GF Alternatives) vs Diabetes (Glycemic Spike)
    if "celiac" in norm_conditions and "diabetes" in norm_conditions:
        conflicts.append({
            "conflict": "Processed Gluten-Free High-GI Starch vs. Diabetes Glycemic Control",
            "severity": "MODERATE",
            "primary_priority": "Strict Gluten-Free Low-GI",
            "conditions_involved": ["Celiac Disease", "Type 2 Diabetes"],
            "conflict_explanation": "Commercial gluten-free baked products often use refined rice flour and tapioca starch, which possess a very high glycemic index and spike blood sugar rapidly.",
            "resolution": "Choose naturally gluten-free whole grains (quinoa, certified GF steel-cut oats, buckwheat, brown rice) with high fiber rather than refined commercial gluten-free breads and pastries."
        })

    return conflicts


def evaluate_nutrition_therapy(
    conditions: List[str],
    dietary_preferences: Optional[List[str]] = None,
    active_medications: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generates a personalized Medical Nutrition Therapy prescription.
    Integrates multiple disease protocols, reconciles nutrient conflicts, applies dietary preferences,
    and cross-checks drug-food timings.
    """
    if not conditions:
        conditions = ["hypertension"]

    dietary_preferences = [p.lower().strip() for p in (dietary_preferences or []) if p and str(p).strip()]
    active_medications = [m.strip() for m in (active_medications or []) if m and str(m).strip()]

    selected_protocols = []
    combined_prioritize: List[str] = []
    combined_avoid: List[str] = []
    macro_summary: Dict[str, str] = {}
    clinical_principles = []

    for c in conditions:
        c_key = c.lower().strip()
        if c_key in NUTRITION_PROTOCOLS:
            proto = NUTRITION_PROTOCOLS[c_key]
            selected_protocols.append(proto)
            combined_prioritize.extend(proto["prioritize_foods"][:6])
            combined_avoid.extend(proto["avoid_foods"][:6])
            macro_summary.update(proto["macro_targets"])
            clinical_principles.append(f"{proto['name']}: {proto['principles']}")

    # Apply Multi-Condition Conflict Resolution
    conflicts = reconcile_dietary_conflicts(conditions)
    if conflicts:
        for conf in conflicts:
            if "potassium" in conf["conflict"].lower() and "hypertension" in conditions and "ckd" in conditions:
                macro_summary["potassium"] = "< 2,000 mg/day (CKD Renal Precedence Over DASH)"

    # Filter by Dietary Preferences
    if "vegetarian" in dietary_preferences or "vegan" in dietary_preferences:
        meat_terms = ["salmon", "chicken", "meat", "beef", "sardine", "cod", "mackerel", "tuna", "pork", "poultry", "seafood", "fish"]
        combined_prioritize = [f for f in combined_prioritize if not any(term in f.lower() for term in meat_terms)]
        if "vegan" in dietary_preferences:
            combined_prioritize = [f for f in combined_prioritize if not any(dairy in f.lower() for dairy in ["yogurt", "milk", "cheese", "egg"])]

    if "gluten_free" in dietary_preferences:
        gluten_terms = ["whole wheat", "barley", "rye", "couscous", "spelt"]
        combined_prioritize = [f for f in combined_prioritize if not any(g in f.lower() for g in gluten_terms)]

    if "low_sodium" in dietary_preferences:
        macro_summary["sodium"] = "< 1,500 mg/day"

    # Deduplicate food lists
    def dedupe(seq):
        seen = set()
        out = []
        for x in seq:
            norm = x.lower().strip()
            if norm not in seen:
                seen.add(norm)
                out.append(x)
        return out

    combined_prioritize = dedupe(combined_prioritize)
    combined_avoid = dedupe(combined_avoid)

    # Food-Drug Interactions
    drug_warnings = check_food_drug_interactions(active_medications)

    # Primary sample meal blueprint
    primary_protocol = selected_protocols[0] if selected_protocols else NUTRITION_PROTOCOLS["hypertension"]
    sample_blueprint = primary_protocol.get("sample_meal_plan", {})

    guideline_citations = " & ".join(dedupe([p.get("guideline_sources", "") for p in selected_protocols if p.get("guideline_sources")]))

    return {
        "success": True,
        "evaluated_protocols": selected_protocols,
        "conditions_evaluated": conditions,
        "macro_targets": macro_summary,
        "prioritize_foods": combined_prioritize[:8],
        "avoid_foods": combined_avoid[:8],
        "sample_meal_blueprint": sample_blueprint,
        "has_conflicts": len(conflicts) > 0,
        "conflict_resolutions": conflicts,
        "has_drug_interactions": len(drug_warnings) > 0,
        "food_drug_interactions": drug_warnings,
        "clinical_summary": " | ".join(clinical_principles[:2]) if clinical_principles else "Evidence-based therapeutic dietary intervention.",
        "guidelines_reference": guideline_citations or "ADA, AHA, KDIGO, ACG, ESPEN Guidelines",
        "clinical_disclaimer": "Medical Nutrition Therapy provides evidence-based dietary education and does not replace individualized clinical management by a Registered Dietitian (RD) or Physician."
    }

