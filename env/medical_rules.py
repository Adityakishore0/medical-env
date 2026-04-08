"""
medical_rules.py
Ground truth for graders — based on WHO, NHS, Mayo Clinic guidelines.
Covers ALL common real-world conditions a patient might present with.
"""

MEDICAL_RULES = {

    # ── GASTROINTESTINAL ──────────────────────────────────────────────────────

    "stomach_pain": {
        "keywords": ["stomach pain", "pet dard", "abdominal pain", "tummy ache", "pet mein dard"],
        "must_ask": ["location", "duration", "vomiting", "fever", "food relation", "medications", "stool changes"],
        "red_flags": ["blood in vomit", "blood in stool", "severe unbearable pain", "rigid abdomen", "fainting"],
        "likely_conditions": ["gastritis", "acidity", "food poisoning", "IBS", "appendicitis", "peptic ulcer"],
        "safe_medicines": ["pantoprazole", "omeprazole", "antacid", "gelusil", "digene", "ors", "domperidone"],
        "dangerous_medicines": ["ibuprofen", "diclofenac", "aspirin", "naproxen", "nimesulide"],
        "safe_foods": ["rice", "banana", "curd", "plain roti", "coconut water", "boiled vegetables"],
        "avoid_foods": ["spicy food", "oily food", "tea", "coffee", "alcohol", "raw salad"],
        "hospital_if": ["blood in vomit or stool", "pain unbearable for more than 6 hours", "high fever with pain", "rigid hard abdomen", "no urine for 8 hours"],
    },

    "acidity_gerd": {
        "keywords": ["acidity", "heartburn", "chest burning", "seeney mein jalan", "acid reflux", "khatta aana"],
        "must_ask": ["timing after meals", "lying down worsens", "spicy food history", "smoking", "medications"],
        "red_flags": ["difficulty swallowing", "weight loss", "blood in vomit", "chest pain radiating to arm"],
        "likely_conditions": ["GERD", "peptic ulcer", "gastritis", "hiatal hernia"],
        "safe_medicines": ["pantoprazole 40mg", "omeprazole 20mg", "antacid syrup", "gelusil", "ranitidine"],
        "dangerous_medicines": ["ibuprofen", "aspirin", "diclofenac", "steroids"],
        "safe_foods": ["cold milk", "banana", "coconut water", "plain rice", "boiled dal"],
        "avoid_foods": ["spicy food", "tea", "coffee", "chocolate", "citrus fruits", "alcohol", "late night eating"],
        "hospital_if": ["difficulty swallowing solid food", "vomiting blood", "black tarry stool", "unexplained weight loss"],
    },

    "diarrhea": {
        "keywords": ["diarrhea", "loose motion", "loose stool", "dast", "watery stool", "paikhana"],
        "must_ask": ["frequency", "blood in stool", "fever", "vomiting", "recent food", "travel history", "duration"],
        "red_flags": ["blood in stool", "high fever", "signs of dehydration", "no urine", "sunken eyes"],
        "likely_conditions": ["viral gastroenteritis", "food poisoning", "bacterial infection", "IBS", "cholera"],
        "safe_medicines": ["ors", "oral rehydration salts", "zinc tablets", "loperamide for adults only", "probiotics"],
        "dangerous_medicines": ["antibiotics without prescription", "loperamide for children under 12"],
        "safe_foods": ["ors", "coconut water", "banana", "plain rice", "plain curd", "boiled potato"],
        "avoid_foods": ["dairy", "spicy food", "raw vegetables", "oily food", "fruit juice"],
        "hospital_if": ["blood in stool", "fever above 39C", "no urine for 8 hours", "unable to keep fluids down", "child becomes very weak"],
    },

    "vomiting_nausea": {
        "keywords": ["vomiting", "nausea", "ulti", "ji machalna", "throwing up", "feel like vomiting"],
        "must_ask": ["frequency", "blood in vomit", "fever", "headache", "last meal", "medications", "pregnancy possibility"],
        "red_flags": ["blood in vomit", "projectile vomiting", "severe headache", "stiff neck", "head injury"],
        "likely_conditions": ["gastroenteritis", "food poisoning", "pregnancy", "migraine", "medication side effect"],
        "safe_medicines": ["ondansetron 4mg", "domperidone", "metoclopramide", "ors"],
        "dangerous_medicines": ["aspirin for children", "ibuprofen on empty stomach"],
        "safe_foods": ["sips of water", "ors", "plain rice water", "coconut water", "dry biscuits"],
        "avoid_foods": ["solid food until vomiting stops", "dairy", "spicy food", "oily food"],
        "hospital_if": ["blood in vomit", "vomiting for more than 24 hours", "signs of dehydration", "severe headache", "child with high fever"],
    },

    "constipation": {
        "keywords": ["constipation", "kabz", "no stool", "hard stool", "difficulty passing stool", "qabz"],
        "must_ask": ["duration", "diet", "water intake", "exercise", "medications", "blood in stool", "pain"],
        "red_flags": ["blood in stool", "severe abdominal pain", "weight loss", "pencil thin stool"],
        "likely_conditions": ["functional constipation", "IBS", "hypothyroidism", "medication side effect", "colorectal issue"],
        "safe_medicines": ["isabgol husk", "lactulose syrup", "dulcolax if severe", "glycerin suppository"],
        "dangerous_medicines": ["regular laxative overuse", "enemas without guidance"],
        "safe_foods": ["papaya", "prunes", "fiber rich food", "plenty of water", "leafy vegetables", "whole grains"],
        "avoid_foods": ["refined flour", "junk food", "dairy in excess", "bananas in excess"],
        "hospital_if": ["blood in stool", "severe pain", "no stool for more than 7 days", "vomiting with constipation"],
    },

    # ── RESPIRATORY ───────────────────────────────────────────────────────────

    "fever": {
        "keywords": ["fever", "bukhar", "temperature", "body hot", "tapman", "high temperature"],
        "must_ask": ["temperature reading", "duration", "chills", "body ache", "rash", "travel history", "urine color", "cough"],
        "red_flags": ["fever above 104F", "stiff neck", "rash", "difficulty breathing", "confusion", "seizure", "infant under 3 months"],
        "likely_conditions": ["viral fever", "malaria", "dengue", "typhoid", "UTI", "covid", "bacterial infection"],
        "safe_medicines": ["paracetamol 500mg every 6 hours", "crocin", "dolo 650", "plenty of fluids"],
        "dangerous_medicines": ["aspirin for children", "ibuprofen without food", "antibiotics without prescription"],
        "safe_foods": ["plenty of water", "coconut water", "dal ka pani", "khichdi", "fruit juice"],
        "avoid_foods": ["heavy oily food", "outside food", "cold drinks"],
        "hospital_if": ["fever above 104F for more than 2 days", "severe body ache with fever", "rash appears", "difficulty breathing", "infant with any fever", "confusion or fits"],
    },

    "cold_cough": {
        "keywords": ["cold", "cough", "sardi", "khansi", "runny nose", "naak behna", "sore throat", "gale mein dard", "sneezing", "chheenk"],
        "must_ask": ["duration", "fever", "color of mucus", "difficulty breathing", "chest pain", "smoker", "blood in cough"],
        "red_flags": ["blood in cough", "difficulty breathing", "high fever", "chest pain", "cough more than 3 weeks"],
        "likely_conditions": ["common cold", "viral URI", "allergic rhinitis", "sinusitis", "bronchitis", "TB if chronic"],
        "safe_medicines": ["paracetamol", "cetirizine", "cough syrup benadryl", "steam inhalation", "honey ginger"],
        "dangerous_medicines": ["antibiotics without prescription", "aspirin for children"],
        "safe_foods": ["warm water", "ginger tea", "turmeric milk", "honey", "warm soup", "steam"],
        "avoid_foods": ["cold drinks", "ice cream", "cold water", "fried food"],
        "hospital_if": ["difficulty breathing", "blood in cough", "fever more than 3 days", "chest pain", "cough more than 3 weeks"],
    },

    "breathing_difficulty": {
        "keywords": ["difficulty breathing", "breathlessness", "sans lena mushkil", "chest tight", "wheezing", "saans phoolna"],
        "must_ask": ["sudden or gradual", "chest pain", "fever", "asthma history", "allergy", "position makes worse", "heart history"],
        "red_flags": ["sudden severe breathlessness", "chest pain", "blue lips or fingertips", "cannot speak full sentences"],
        "likely_conditions": ["asthma", "COPD", "pneumonia", "heart failure", "anxiety", "anemia", "pulmonary embolism"],
        "safe_medicines": ["salbutamol inhaler if asthma known", "position upright", "fresh air"],
        "dangerous_medicines": ["beta blockers in asthma", "NSAIDs in asthma"],
        "safe_foods": ["warm fluids", "steam"],
        "avoid_foods": ["known allergens", "cold food"],
        "hospital_if": ["ANY difficulty breathing is potentially serious — go to hospital if it is new or worsening", "blue lips", "chest pain with breathlessness", "cannot complete sentences"],
    },

    "sore_throat": {
        "keywords": ["sore throat", "gala dard", "throat pain", "gale mein kharash", "difficulty swallowing", "tonsils"],
        "must_ask": ["fever", "duration", "white patches on throat", "ear pain", "rash", "difficulty swallowing"],
        "red_flags": ["difficulty breathing", "cannot swallow saliva", "severe swelling", "muffled voice"],
        "likely_conditions": ["viral pharyngitis", "strep throat", "tonsillitis", "mononucleosis"],
        "safe_medicines": ["paracetamol", "benzydamine gargle", "warm salt water gargle", "strepsils lozenges"],
        "dangerous_medicines": ["antibiotics without prescription", "aspirin for children"],
        "safe_foods": ["warm water", "honey", "cold ice cream to soothe", "soft foods", "soup"],
        "avoid_foods": ["spicy food", "hard food", "cold drinks"],
        "hospital_if": ["cannot swallow", "difficulty breathing", "high fever with white patches", "drooling", "muffled voice"],
    },

    # ── PAIN ──────────────────────────────────────────────────────────────────

    "headache": {
        "keywords": ["headache", "sir dard", "head pain", "migraine", "sar mein dard", "throbbing head"],
        "must_ask": ["location", "duration", "severity", "nausea", "light sensitivity", "fever", "neck stiffness", "vision changes", "triggered by"],
        "red_flags": ["sudden worst headache of life", "stiff neck with fever", "vision loss", "weakness on one side", "confusion", "after head injury"],
        "likely_conditions": ["tension headache", "migraine", "sinusitis", "dehydration", "hypertension", "meningitis if red flags"],
        "safe_medicines": ["paracetamol 500mg", "ibuprofen with food", "sumatriptan for migraine if prescribed", "rest in dark room"],
        "dangerous_medicines": ["codeine overuse", "regular painkiller overuse causes rebound headache"],
        "safe_foods": ["plenty of water", "electrolytes", "ginger tea", "regular meals"],
        "avoid_foods": ["alcohol", "caffeine excess", "skipping meals", "processed cheese", "chocolates for migraine"],
        "hospital_if": ["sudden severe worst headache", "headache with stiff neck and fever", "headache after head injury", "headache with vision changes or weakness", "headache in children with vomiting"],
    },

    "back_pain": {
        "keywords": ["back pain", "kamar dard", "spine pain", "lower back", "peth ke peeche dard", "backache"],
        "must_ask": ["location", "duration", "radiation to leg", "numbness", "weakness", "bowel bladder changes", "injury history", "age"],
        "red_flags": ["numbness in groin or inner thigh", "loss of bladder or bowel control", "weakness in legs", "fever with back pain", "cancer history"],
        "likely_conditions": ["muscle strain", "lumbar disc prolapse", "sciatica", "kidney stone", "ankylosing spondylitis"],
        "safe_medicines": ["paracetamol", "diclofenac gel topical", "muscle relaxant if prescribed", "hot water bag"],
        "dangerous_medicines": ["long term oral NSAIDs without monitoring", "steroids without prescription"],
        "safe_foods": ["anti inflammatory diet", "turmeric milk", "plenty of water"],
        "avoid_foods": ["alcohol", "processed food"],
        "hospital_if": ["loss of bladder or bowel control", "weakness in both legs", "numbness in groin", "fever with severe back pain", "back pain after accident"],
    },

    "joint_pain": {
        "keywords": ["joint pain", "jodo mein dard", "knee pain", "ghutne mein dard", "arthritis", "swollen joint", "body pain"],
        "must_ask": ["which joint", "duration", "swelling", "redness", "morning stiffness", "fever", "injury", "age", "multiple joints"],
        "red_flags": ["hot red swollen single joint with fever", "recent tick bite", "joint pain after sore throat"],
        "likely_conditions": ["osteoarthritis", "rheumatoid arthritis", "gout", "reactive arthritis", "fibromyalgia"],
        "safe_medicines": ["paracetamol", "diclofenac gel topical", "warm compress", "cold pack for acute injury"],
        "dangerous_medicines": ["long term oral steroids without prescription", "overuse of NSAIDs"],
        "safe_foods": ["turmeric", "ginger", "omega 3 rich fish", "anti inflammatory diet", "calcium and vitamin D"],
        "avoid_foods": ["red meat in excess", "alcohol", "refined sugar", "processed food"],
        "hospital_if": ["hot red swollen joint with fever", "cannot move joint at all", "after injury with swelling", "joint pain in child with fever"],
    },

    "chest_pain": {
        "keywords": ["chest pain", "seene mein dard", "heart pain", "chest tightness", "left chest", "dil mein dard"],
        "must_ask": ["location", "radiation to arm or jaw", "sweating", "breathlessness", "duration", "exertion or rest", "nausea", "age and history"],
        "red_flags": ["crushing chest pain", "radiation to left arm or jaw", "sweating with chest pain", "breathlessness", "sudden onset"],
        "likely_conditions": ["acidity GERD", "muscle strain", "anxiety", "angina", "heart attack", "pulmonary embolism"],
        "safe_medicines": ["antacid if acidity suspected", "paracetamol for muscle pain"],
        "dangerous_medicines": ["do not self medicate chest pain — must see doctor"],
        "safe_foods": ["rest", "avoid heavy meals"],
        "avoid_foods": ["spicy food if acidity", "heavy meals", "exertion"],
        "hospital_if": ["ANY chest pain that is new severe or with sweating or breathlessness — GO TO HOSPITAL IMMEDIATELY", "crushing or squeezing chest pain", "pain radiating to arm jaw or back", "chest pain with fainting"],
    },

    # ── URINARY ───────────────────────────────────────────────────────────────

    "urinary_problems": {
        "keywords": ["burning urine", "peshab mein jalan", "frequent urination", "baar baar peshab", "UTI", "blood in urine", "urine infection"],
        "must_ask": ["burning or pain", "frequency", "blood in urine", "fever", "back pain", "discharge", "pregnancy possibility", "diabetes"],
        "red_flags": ["blood in urine", "fever with urinary symptoms", "back or flank pain", "no urine output"],
        "likely_conditions": ["UTI", "urinary tract infection", "kidney infection", "kidney stone", "STI"],
        "safe_medicines": ["plenty of water", "cranberry juice", "if confirmed UTI nitrofurantoin or trimethoprim by doctor"],
        "dangerous_medicines": ["antibiotics without urine test", "self treating with random antibiotics"],
        "safe_foods": ["plenty of water minimum 3 litres", "coconut water", "barley water", "cranberry juice"],
        "avoid_foods": ["spicy food", "alcohol", "caffeine", "holding urine"],
        "hospital_if": ["fever with urinary symptoms", "blood in urine", "back or flank pain", "no urine output", "symptoms in pregnancy", "child with urinary symptoms"],
    },

    # ── SKIN ──────────────────────────────────────────────────────────────────

    "skin_problems": {
        "keywords": ["rash", "itching", "khujli", "skin irritation", "red skin", "urticaria", "hives", "eczema", "pimples", "acne"],
        "must_ask": ["location", "duration", "spreading", "fever", "new food or soap or medicine", "allergy history", "itching", "discharge"],
        "red_flags": ["widespread rash with fever", "difficulty breathing with rash", "rash after new medicine", "painful blistering rash"],
        "likely_conditions": ["allergic reaction", "eczema", "fungal infection", "viral rash", "contact dermatitis", "urticaria"],
        "safe_medicines": ["cetirizine for itching", "calamine lotion", "hydrocortisone 1% cream", "antifungal cream if fungal"],
        "dangerous_medicines": ["oral steroids without prescription", "strong steroid cream on face"],
        "safe_foods": ["avoid identified trigger foods", "plenty of water"],
        "avoid_foods": ["identified allergens", "spicy food if it worsens"],
        "hospital_if": ["rash with difficulty breathing", "widespread painful blistering", "rash after new medicine", "high fever with rash", "rash in child that does not fade with glass pressure"],
    },

    # ── MENTAL HEALTH ─────────────────────────────────────────────────────────

    "anxiety_stress": {
        "keywords": ["anxiety", "stress", "tension", "chinta", "panic", "heart racing", "worry", "nervous", "depression", "sad"],
        "must_ask": ["duration", "trigger", "sleep", "appetite", "work or family stress", "chest pain", "breathlessness", "suicidal thoughts"],
        "red_flags": ["suicidal thoughts", "self harm", "inability to function", "psychosis symptoms"],
        "likely_conditions": ["generalised anxiety disorder", "panic disorder", "depression", "adjustment disorder"],
        "safe_medicines": ["no OTC medicines — must see doctor for mental health", "melatonin for sleep if mild"],
        "dangerous_medicines": ["alcohol for stress", "self medicating with sleeping pills", "benzodiazepines without prescription"],
        "safe_foods": ["balanced diet", "reduce caffeine", "omega 3", "regular exercise", "meditation"],
        "avoid_foods": ["alcohol", "excess caffeine", "sugar"],
        "hospital_if": ["thoughts of suicide or self harm", "cannot function at all", "hearing or seeing things", "family concerned about safety"],
    },

    # ── WOMEN'S HEALTH ────────────────────────────────────────────────────────

    "menstrual_problems": {
        "keywords": ["period pain", "period late", "irregular period", "heavy bleeding", "PCOD", "PCOS", "mahavari", "masik dharm"],
        "must_ask": ["last period date", "cycle length", "pain severity", "flow heavy or light", "clots", "pregnancy possibility", "other symptoms"],
        "red_flags": ["pregnancy with bleeding", "severe pain", "fainting", "very heavy bleeding soaking pad every hour"],
        "likely_conditions": ["dysmenorrhea", "PCOS", "endometriosis", "anovulation", "thyroid issue"],
        "safe_medicines": ["mefenamic acid or ibuprofen for period pain with food", "heat pad", "paracetamol"],
        "dangerous_medicines": ["hormonal pills without prescription", "emergency contraception overuse"],
        "safe_foods": ["iron rich food", "dates", "leafy vegetables", "warm ginger tea", "magnesium rich food"],
        "avoid_foods": ["caffeine", "salty food", "processed food during period"],
        "hospital_if": ["pregnancy with any bleeding", "very heavy bleeding", "severe pain not relieved by medicines", "period absent for 3 months"],
    },

    # ── EYE AND EAR ───────────────────────────────────────────────────────────

    "eye_problems": {
        "keywords": ["eye pain", "red eye", "aankh mein dard", "blurry vision", "itchy eye", "discharge from eye", "conjunctivitis"],
        "must_ask": ["redness", "discharge", "vision change", "pain", "injury", "contact lenses", "chemical exposure"],
        "red_flags": ["sudden vision loss", "severe eye pain", "chemical in eye", "eye injury", "halos around lights"],
        "likely_conditions": ["conjunctivitis", "allergic eye", "dry eye", "stye", "glaucoma if acute pain"],
        "safe_medicines": ["antiallergic eye drops", "warm compress for stye", "artificial tears for dry eye"],
        "dangerous_medicines": ["steroid eye drops without prescription", "contact lens in red eye"],
        "safe_foods": ["vitamin A rich food", "carrot", "leafy greens"],
        "avoid_foods": [],
        "hospital_if": ["sudden vision loss", "severe eye pain", "chemical splash in eye", "eye injury", "vision changes with headache"],
    },

    "ear_problems": {
        "keywords": ["ear pain", "kaan dard", "ear discharge", "hearing loss", "tinnitus", "ringing in ear", "ear block"],
        "must_ask": ["pain or discharge", "hearing loss", "fever", "recent cold", "swimming", "child or adult", "duration"],
        "red_flags": ["severe pain with fever", "discharge with blood", "sudden complete hearing loss", "dizziness with hearing loss"],
        "likely_conditions": ["otitis media", "ear wax", "outer ear infection", "eustachian tube dysfunction"],
        "safe_medicines": ["paracetamol for pain", "warm compress", "ear wax softener drops"],
        "dangerous_medicines": ["ear drops if eardrum perforated", "cotton buds — never insert"],
        "safe_foods": ["plenty of fluids if infection"],
        "avoid_foods": [],
        "hospital_if": ["severe ear pain with fever", "discharge from ear", "sudden hearing loss", "dizziness with ear symptoms", "child with ear pain and high fever"],
    },

    # ── DIABETES RELATED ──────────────────────────────────────────────────────

    "diabetes_symptoms": {
        "keywords": ["sugar high", "blood sugar", "diabetes", "madhumeh", "excessive thirst", "frequent urination", "weight loss sudden"],
        "must_ask": ["known diabetic", "current medicines", "blood sugar reading", "diet", "foot wounds", "vision changes", "chest pain"],
        "red_flags": ["blood sugar above 400", "unconscious or confused diabetic", "diabetic foot with pus", "chest pain in diabetic"],
        "likely_conditions": ["uncontrolled diabetes", "diabetic ketoacidosis", "hypoglycemia", "new onset diabetes"],
        "safe_medicines": ["continue prescribed medicines", "check blood sugar regularly", "metformin if prescribed"],
        "dangerous_medicines": ["skipping insulin", "random herbal medicines stopping prescribed medicines"],
        "safe_foods": ["low glycemic food", "vegetables", "whole grains", "dal", "avoid sugar completely"],
        "avoid_foods": ["sugar", "sweets", "white rice in excess", "fruit juice", "maida"],
        "hospital_if": ["blood sugar above 300 with symptoms", "confusion or unconsciousness", "diabetic foot wound", "vomiting and cannot take medicines", "chest pain"],
    },

    # ── HYPERTENSION ──────────────────────────────────────────────────────────

    "high_blood_pressure": {
        "keywords": ["high BP", "blood pressure high", "hypertension", "BP badh gaya", "high blood pressure"],
        "must_ask": ["BP reading", "current medicines", "headache", "vision changes", "chest pain", "shortness of breath", "family history"],
        "red_flags": ["BP above 180 systolic", "severe headache with high BP", "chest pain", "vision changes", "pregnancy"],
        "likely_conditions": ["essential hypertension", "secondary hypertension", "hypertensive crisis"],
        "safe_medicines": ["continue prescribed antihypertensives", "amlodipine losartan if prescribed"],
        "dangerous_medicines": ["stopping BP medicines suddenly", "NSAIDs raise BP", "decongestants raise BP"],
        "safe_foods": ["low salt diet", "DASH diet", "fruits", "vegetables", "reduce oil"],
        "avoid_foods": ["excess salt", "processed food", "alcohol", "smoking", "pickles", "papad"],
        "hospital_if": ["BP above 180 at home", "severe headache with high BP", "chest pain", "vision changes", "confusion", "pregnancy with high BP"],
    },
}


def find_matching_rule(complaint: str) -> dict:
    """Find the best matching medical rule for a given complaint."""
    complaint_lower = complaint.lower()
    best_match = None
    best_score = 0

    for condition, rule in MEDICAL_RULES.items():
        score = 0
        for keyword in rule["keywords"]:
            if keyword.lower() in complaint_lower:
                score += 1
        if score > best_score:
            best_score = score
            best_match = rule

    return best_match or MEDICAL_RULES["fever"]  # default fallback


def get_all_conditions() -> list:
    return list(MEDICAL_RULES.keys())
