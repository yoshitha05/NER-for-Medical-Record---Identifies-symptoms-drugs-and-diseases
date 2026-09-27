"""Medical dictionary for the spaCy EntityRuler. Matching is case-insensitive.
Add new terms to the right list; multi-word terms are fine ("chest pain")."""

DISEASES = [
    # infections
    "dengue", "malaria", "typhoid", "chikungunya", "tuberculosis", "tb", "covid-19", "covid",
    "influenza", "flu", "common cold", "pneumonia", "bronchitis", "sinusitis", "tonsillitis",
    "pharyngitis", "conjunctivitis", "otitis media", "urinary tract infection", "uti",
    "gastroenteritis", "hepatitis", "hepatitis a", "hepatitis b", "hepatitis c", "jaundice",
    "cholera", "measles", "chickenpox", "mumps", "herpes zoster", "cellulitis", "sepsis", "hiv",
    "leptospirosis", "scrub typhus", "fungal infection", "scabies",
    # heart and blood
    "hypertension", "high blood pressure", "hypotension", "coronary artery disease",
    "heart attack", "myocardial infarction", "heart failure", "angina", "arrhythmia",
    "atrial fibrillation", "stroke", "deep vein thrombosis", "anemia", "anaemia",
    "hyperlipidemia", "high cholesterol", "thalassemia",
    # hormones and metabolism
    "diabetes", "diabetes mellitus", "type 1 diabetes", "type 2 diabetes", "prediabetes",
    "hypothyroidism", "hyperthyroidism", "pcos", "polycystic ovary syndrome", "obesity",
    "gout", "vitamin d deficiency", "vitamin b12 deficiency",
    # lungs
    "asthma", "copd", "chronic obstructive pulmonary disease", "allergic rhinitis",
    # stomach, liver, kidney
    "gastritis", "gerd", "acid reflux", "peptic ulcer", "irritable bowel syndrome", "ibs",
    "appendicitis", "fatty liver", "cirrhosis", "pancreatitis", "gallstones", "kidney stones",
    "chronic kidney disease", "ckd", "hemorrhoids", "piles",
    # brain and mind
    "migraine", "epilepsy", "parkinson's disease", "alzheimer's disease", "dementia",
    "depression", "anxiety disorder", "bipolar disorder", "vertigo",
    # bones, skin, others
    "arthritis", "rheumatoid arthritis", "osteoarthritis", "osteoporosis", "spondylosis",
    "psoriasis", "eczema", "dermatitis", "acne", "cataract", "glaucoma",
    "cancer", "breast cancer", "lung cancer", "leukemia", "lymphoma",
]

DRUGS = [
    # pain and fever
    "paracetamol", "acetaminophen", "dolo 650", "dolo", "crocin", "calpol", "ibuprofen",
    "brufen", "combiflam", "aspirin", "ecosprin", "diclofenac", "voveran", "aceclofenac",
    "zerodol", "naproxen", "tramadol", "mefenamic acid", "meftal",
    # antibiotics and anti-infectives
    "amoxicillin", "augmentin", "amoxicillin-clavulanate", "azithromycin", "azithral",
    "ciprofloxacin", "ciplox", "levofloxacin", "ofloxacin", "doxycycline", "cefixime",
    "taxim-o", "cefuroxime", "ceftriaxone", "metronidazole", "flagyl", "nitrofurantoin",
    "clindamycin", "linezolid", "vancomycin", "fluconazole", "itraconazole", "clotrimazole",
    "acyclovir", "oseltamivir", "albendazole", "ivermectin", "hydroxychloroquine",
    "chloroquine", "artemether", "isoniazid", "rifampicin",
    # diabetes
    "metformin", "glycomet", "glimepiride", "amaryl", "gliclazide", "sitagliptin", "januvia",
    "vildagliptin", "galvus", "teneligliptin", "empagliflozin", "jardiance", "dapagliflozin",
    "insulin", "insulin glargine", "lantus", "voglibose",
    # blood pressure and heart
    "amlodipine", "telmisartan", "telma", "losartan", "olmesartan", "ramipril", "enalapril",
    "atenolol", "metoprolol", "bisoprolol", "carvedilol", "hydrochlorothiazide",
    "chlorthalidone", "furosemide", "lasix", "spironolactone", "atorvastatin",
    "rosuvastatin", "clopidogrel", "warfarin", "heparin", "apixaban", "nitroglycerin",
    # stomach
    "pantoprazole", "pan 40", "pan-d", "pantocid", "omeprazole", "omez", "rabeprazole",
    "esomeprazole", "ranitidine", "famotidine", "domperidone", "ondansetron", "emeset",
    "loperamide", "ors", "digene", "gelusil", "lactulose", "sucralfate",
    # allergy, cough, lungs
    "cetirizine", "levocetirizine", "loratadine", "fexofenadine", "allegra", "montelukast",
    "montair lc", "montair", "salbutamol", "asthalin", "albuterol", "budesonide",
    "formoterol", "ambroxol", "dextromethorphan", "benadryl", "chlorpheniramine",
    # steroids, thyroid, vitamins
    "prednisolone", "prednisone", "dexamethasone", "hydrocortisone", "methylprednisolone",
    "levothyroxine", "thyronorm", "eltroxin", "carbimazole", "vitamin d3", "vitamin b12",
    "folic acid", "iron supplements", "calcium carbonate", "shelcal", "becosules",
    # brain and mind
    "sertraline", "fluoxetine", "escitalopram", "amitriptyline", "alprazolam", "clonazepam",
    "levetiracetam", "phenytoin", "sodium valproate", "sumatriptan", "betahistine",
    "pregabalin", "gabapentin",
]

SYMPTOMS = [
    # general
    "fever", "high fever", "mild fever", "low-grade fever", "chills", "fatigue", "tiredness",
    "weakness", "malaise", "body ache", "body aches", "body pain", "night sweats", "sweating",
    "weight loss", "weight gain", "loss of appetite", "dehydration",
    # head and nerves
    "headache", "severe headache", "dizziness", "giddiness", "fainting", "confusion",
    "seizures", "numbness", "tingling", "blurred vision", "insomnia",
    # breathing and chest
    "cough", "dry cough", "wet cough", "productive cough", "persistent cough",
    "sore throat", "runny nose", "nasal congestion", "blocked nose", "sneezing",
    "shortness of breath", "breathlessness", "difficulty breathing", "wheezing",
    "chest pain", "chest tightness", "palpitations",
    # stomach
    "nausea", "vomiting", "diarrhea", "diarrhoea", "loose motions", "constipation",
    "abdominal pain", "stomach pain", "stomach ache", "bloating", "acidity", "heartburn",
    "indigestion", "blood in stool",
    # urine
    "frequent urination", "burning urination", "burning micturition", "blood in urine",
    "excessive thirst",
    # pain and skin
    "joint pain", "back pain", "lower back pain", "neck pain", "muscle pain", "knee pain",
    "ear pain", "toothache", "rash", "skin rash", "itching", "swelling", "loss of taste",
    "loss of smell", "yellowing of skin",
]