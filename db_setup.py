import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "medicine_system.db")

def ensure_schema(conn):
    cursor = conn.cursor()
    
    # Helper to check columns
    def get_columns(table_name):
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        return [row[1] for row in cursor.fetchall()]
        
    def count_rows(table_name):
        try:
            cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
            return cursor.fetchone()[0]
        except:
            return 0

    # 1. users table
    cols = get_columns('users')
    if not cols:
        cursor.execute("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                email TEXT UNIQUE,
                password TEXT,
                age INTEGER,
                gender TEXT,
                region TEXT
            )
        """)
    elif 'email' not in cols or 'user_id' not in cols:
        if count_rows('users') == 0:
            cursor.execute("DROP TABLE users")
            cursor.execute("""
                CREATE TABLE users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT,
                    email TEXT UNIQUE,
                    password TEXT,
                    age INTEGER,
                    gender TEXT,
                    region TEXT
                )
            """)

    # 2. Legacy USER table migration (if separate from users)
    if 'USER' in [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
        user_cols = get_columns('USER')
        if 'username' in user_cols:
            try:
                cursor.execute("SELECT username, password, name, age, gender, allergy FROM USER")
                for u_name, pwd, name, age, gender, allergy in cursor.fetchall():
                    cursor.execute("""
                        INSERT OR IGNORE INTO users (full_name, email, password, age, gender, region)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (name or u_name, u_name, pwd, age, gender, allergy))
            except Exception as e:
                print(f"Legacy USER migration note: {e}")

    # 3. problem table
    prob_cols = get_columns('problem')
    if not prob_cols or 'problem_description' not in prob_cols:
        if count_rows('problem') == 0:
            cursor.execute("DROP TABLE IF EXISTS problem")
            cursor.execute("""
                CREATE TABLE problem (
                    problem_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    problem_name TEXT UNIQUE,
                    problem_description TEXT
                )
            """)
        else:
            if 'problem_description' not in prob_cols:
                cursor.execute("ALTER TABLE problem ADD COLUMN problem_description TEXT")

    # 4. remedy table
    rem_cols = get_columns('remedy')
    if not rem_cols or 'remedy_name' not in rem_cols:
        if count_rows('remedy') == 0:
            cursor.execute("DROP TABLE IF EXISTS remedy")
            cursor.execute("""
                CREATE TABLE remedy (
                    remedy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    problem_id INTEGER,
                    remedy_name TEXT,
                    remedy_type TEXT,
                    remedy_form TEXT,
                    description TEXT,
                    dosage TEXT,
                    consumption_steps TEXT,
                    precautions TEXT,
                    yoga_exercise TEXT,
                    FOREIGN KEY (problem_id) REFERENCES problem (problem_id) ON DELETE CASCADE
                )
            """)

    # 5. ingredient table
    ing_cols = get_columns('ingredient')
    if not ing_cols or 'advantages' not in ing_cols:
        if count_rows('ingredient') == 0:
            cursor.execute("DROP TABLE IF EXISTS ingredient")
            cursor.execute("""
                CREATE TABLE ingredient (
                    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ingredient_name TEXT UNIQUE,
                    advantages TEXT
                )
            """)

    # 6. remedy_ingredient table
    ri_cols = get_columns('remedy_ingredient')
    if not ri_cols or 'quantity_needed' not in ri_cols:
        if count_rows('remedy_ingredient') == 0:
            cursor.execute("DROP TABLE IF EXISTS remedy_ingredient")
            cursor.execute("""
                CREATE TABLE remedy_ingredient (
                    remedy_id INTEGER,
                    ingredient_id INTEGER,
                    quantity_needed TEXT,
                    PRIMARY KEY (remedy_id, ingredient_id),
                    FOREIGN KEY (remedy_id) REFERENCES remedy (remedy_id) ON DELETE CASCADE,
                    FOREIGN KEY (ingredient_id) REFERENCES ingredient (ingredient_id) ON DELETE CASCADE
                )
            """)

    # 7. tracker table
    tr_cols = get_columns('tracker')
    if not tr_cols or 'remedy_name' not in tr_cols or 'user_id' not in tr_cols:
        if count_rows('tracker') == 0:
            cursor.execute("DROP TABLE IF EXISTS tracker")
            cursor.execute("""
                CREATE TABLE tracker (
                    tracker_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    status TEXT,
                    notes TEXT,
                    remedy_name TEXT,
                    next_dose_time DATETIME,
                    start_date DATE,
                    day_number INTEGER DEFAULT 1,
                    total_days INTEGER DEFAULT 7,
                    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
                )
            """)

    # 8. clinics table
    clin_cols = get_columns('clinics')
    if not clin_cols or 'clinic_name' not in clin_cols:
        if count_rows('clinics') == 0:
            cursor.execute("DROP TABLE IF EXISTS clinics")
            cursor.execute("""
                CREATE TABLE clinics (
                    clinic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    clinic_name TEXT,
                    address TEXT,
                    phone TEXT,
                    type TEXT
                )
            """)

    conn.commit()

def setup_db(db_path=None):
    if db_path is None:
        db_path = DEFAULT_DB_PATH
        
    conn = sqlite3.connect(db_path)
    ensure_schema(conn)
    cursor = conn.cursor()

    # Seed Clinics Data if empty
    cursor.execute("SELECT COUNT(*) FROM clinics")
    if cursor.fetchone()[0] == 0:
        clinics_list = [
            ('RemediCare Central Hospital', 'Sector 12, Medical Plaza, Bangalore', '+91 98765 43210', 'Emergency Care'),
            ('Sanjeevani Ayurvedic Center', 'MG Road, Near RemediCare Pharmacy, Bangalore', '+91 88888 77777', 'Holistic Hospital'),
            ('City Clinical Trauma Hub', 'Whitefield Industrial Area, Bangalore', '+91 77777 66666', 'Critical Care'),
            ('Dhanvantari Health Point', 'Indiranagar Main Road, Bangalore', '+91 99999 00000', 'Specialty Clinic'),
            ('Vedic Emergency Unit', 'Koramangala 4th Block, Bangalore', '+91 66666 55555', 'Trauma Center')
        ]
        cursor.executemany("INSERT INTO clinics (clinic_name, address, phone, type) VALUES (?, ?, ?, ?)", clinics_list)

    # Authentic Home Remedy Data Injection if empty
    cursor.execute("SELECT COUNT(*) FROM problem")
    if cursor.fetchone()[0] == 0:
        remedy_data = [
            ('(vertigo) Paroymsal Positional Vertigo', 'Ginger & Coriander Infusion', 'Crush 1 inch ginger and 1 tsp coriander seeds. Boil in 1.5 cups water until reduced to 1 cup. Strain.', '150ml', 'Sip slowly while sitting upright.', 'Avoid sudden head movements and bright flickering lights.', 'Clinical Infusion', 'Shanmukhi Mudra', [('Ginger', 'Relieves nausea'), ('Coriander', 'Cooling')]),
            ('AIDS', 'Ashwagandha & Giloy Immunity Tea', 'Boil 5 inches of Giloy stem and 1 tsp Ashwagandha powder in water until reduced.', '1 Cup', 'Drink warm every morning.', 'Maintain high hygiene and avoid raw unwashed fruits.', 'Immunity Brew', 'Kapalbhati Pranayama', [('Giloy', 'Immunity'), ('Ashwagandha', 'Vitality')]),
            ('Acne', 'Turmeric & Neem Facial Mask', 'Mix 1 tsp Turmeric with 1 tsp Neem powder and water to make a thick paste.', 'Apply on spots', 'Keep for 20 mins then wash.', 'Avoid oily, spicy foods and direct sun exposure after application.', 'Healing Paste', 'Sheetali Pranayama', [('Turmeric', 'Anti-bacterial'), ('Neem', 'Purifier')]),
            ('Alcoholic hepatitis', 'Kutki & Punarnava Liver Tonic', 'Mix 3g Kutki and 3g Punarnava powder in lukewarm water.', '200ml', 'Take before meals.', 'Absolute cessation of alcohol. Avoid heavy, fried meals.', 'Liver Tonic', 'Katichakrasana', [('Kutki', 'Liver protect'), ('Punarnava', 'Detox')]),
            ('Allergy', 'Tulsi & Black Pepper Decoction', 'Boil 10 Tulsi leaves and 4 crushed peppercorns. Add honey after cooling.', '100ml', 'Drink twice daily.', 'Avoid dairy and cold drinks during allergy peaks.', 'Nervine Decoction', 'Bhastrika Pranayama', [('Tulsi', 'Anti-allergic'), ('Pepper', 'Clears congestion')]),
            ('Arthritis', 'Ginger-Garlic Warm Milk', 'Boil 2 cloves of garlic in a cup of milk. Use ginger oil for massage.', '1 Cup', 'Drink at night.', 'Avoid fermented foods (curd, idli) and cold winds.', 'Oral & External', 'Gomukhasana', [('Garlic', 'Lubricant'), ('Ginger', 'Anti-inflammatory')]),
            ('Bronchial Asthma', 'Honey & Cinnamon Syrup', 'Mix 1 tsp honey with half tsp cinnamon and ginger juice.', '1 tbsp', 'Lick slowly after meals.', 'Avoid cold showers and exposure to dust/pollen.', 'Linctus Syrup', 'Bhujangasana', [('Honey', 'Soothes'), ('Cinnamon', 'Clears mucus')]),
            ('Cervical spondylosis', 'Sesame-Garlic Warm Compress', 'Warm sesame oil with garlic cloves for gentle neck massage.', 'External', 'Apply twice daily.', 'Use a thin pillow. Avoid long hours of continuous mobile use.', 'Medicated Oil', 'Greeva Sanchalana', [('Sesame', 'Nourishing'), ('Garlic', 'Relieves pain')]),
            ('Chicken pox', 'Neem & Sandalwood Soothing Wash', 'Add neem leaves to lukewarm bath water. Apply sandalwood paste.', 'Daily Bath', 'Bathe twice daily.', 'Maintain isolation. Avoid spicy and salty foods.', 'External Wash', 'Shavasana', [('Neem', 'Anti-viral'), ('Sandalwood', 'Cooling')]),
            ('Chronic cholestasis', 'Bhumyamalaki Liver Flush', 'Mix 5g Bhumyamalaki powder with half cup buttermilk.', '100ml', 'Take before breakfast.', 'Limit fat intake. Avoid processed sugars.', 'Digestive Flush', 'Dhanurasana', [('Bhumyamalaki', 'Bile flow'), ('Buttermilk', 'Digestive')]),
            ('Common Cold', 'Ginger, Tulsi & Honey Tea', 'Boil ginger and tulsi leaves. Add honey after straining.', '1 Cup', 'Drink 3 times daily.', 'Keep ears and chest covered. Avoid citrus fruits.', 'Herbal Brew', 'Surya Bhedana', [('Ginger', 'Expels cold'), ('Tulsi', 'Immunity')]),
            ('Dengue', 'Papaya Leaf & Goat Milk', 'Extract papaya leaf juice. Take with goat milk.', '20ml', 'Take twice daily.', 'Strict bed rest. Monitor platelet counts every 12 hours.', 'Platelet Booster', 'Anulom Vilom', [('Papaya', 'Platelets'), ('Goat Milk', 'Nutritious')]),
            ('Diabetes', 'Fenugreek & Jamun Seed Powder', 'Mix equal parts of Fenugreek and Jamun seed powder.', '1 tsp', 'Take with water before breakfast.', 'Limit carbohydrate intake. Avoid sedentary lifestyle.', 'Clinical Powder', 'Mandukasana', [('Fenugreek', 'Fiber'), ('Jamun', 'Sugar control')]),
            ('Dimorphic hemmorhoids(piles)', 'Buttermilk & Cumin Drink', 'Mix buttermilk with roasted cumin and rock salt.', '1 Glass', 'Take with lunch.', 'Avoid sitting on hard surfaces. Increase fiber intake.', 'Digestive Lassi', 'Ashwini Mudra', [('Buttermilk', 'Probiotic'), ('Cumin', 'Digestion')]),
            ('Drug Reaction', 'Aloe Vera & Cilantro Juice', 'Blend Aloe Vera gel with fresh cilantro and water.', '100ml', 'Drink twice daily.', 'Immediately stop the suspected drug. Avoid sun.', 'Cooling Juice', 'Tadasana', [('Aloe', 'Soothing'), ('Cilantro', 'Detox')]),
            ('Fungal infection', 'Coconut Oil & Camphor Rub', 'Mix crushed camphor in pure coconut oil. Apply on skin.', 'External', 'Apply after bath.', 'Keep skin dry. Wear loose cotton clothes.', 'Topical Balm', 'Pawanmuktasana', [('Coconut', 'Anti-fungal'), ('Camphor', 'Anti-itch')]),
            ('GERD', 'Fennel & Cardamom Infusion', 'Soak fennel and cardamom in hot water for 10 mins.', '1 Cup', 'Drink after meals.', 'Do not lie down immediately after eating.', 'Antacid Infusion', 'Vajrasana', [('Fennel', 'Alkaline'), ('Cardamom', 'Neutralizer')]),
            ('Gastroenteritis', 'Pomegranate Peel Tea', 'Boil dried pomegranate peel in water.', '50ml', 'Take every 4 hours.', 'Avoid solid food for 24 hours. Drink ORS.', 'Astringent Tea', 'Matsyasana', [('Pomegranate', 'Stops loose motion'), ('Water', 'Hydration')]),
            ('Heart attack', 'Arjuna Bark & Cardamom Milk', 'Boil Arjuna bark in milk and water until reduced.', '1 Cup', 'Drink daily at night.', 'Strictly avoid high-cholesterol foods and smoking.', 'Cardiac Tonic', 'Hridayakasana', [('Arjuna', 'Heart strength'), ('Cardamom', 'Flavor')]),
            ('Hepatitis B', 'Bhumyamalaki & Kalmegh', 'Mix Bhumyamalaki and Kalmegh powder. Take with water.', '1 tsp', 'Twice daily.', 'Avoid all oily and sugary foods. Rest is crucial.', 'Liver Guard', 'Ardha Matsyendrasana', [('Bhumyamalaki', 'Anti-viral'), ('Kalmegh', 'Detox')]),
            ('Hepatitis C', 'Turmeric & Honey Paste', 'Mix Turmeric with raw honey.', '1 tsp', 'Take twice daily.', 'Avoid unsterile needles and alcohol.', 'Healing Electuary', 'Bhujangasana', [('Turmeric', 'Repair'), ('Honey', 'Enzymes')]),
            ('Hepatitis D', 'Punarnava Water', 'Boil Punarnava root in water until reduced.', '1 Cup', 'Drink daily.', 'Maintain low salt intake to reduce liver swelling.', 'Diuretic Decoction', 'Paschimottanasana', [('Punarnava', 'Swelling reduction'), ('Water', 'Flush')]),
            ('Hepatitis E', 'Radish Leaf Juice', 'Grind radish leaves and extract juice.', '50ml', 'Take for 10 days.', 'Drink boiled water only. Avoid street food.', 'Enzyme Booster', 'Halasana', [('Radish', 'Cleanses bile'), ('Water', 'Purity')]),
            ('Hypertension', 'Sarpagandha & Watermelon', 'Take Sarpagandha powder at night. Eat watermelon in morning.', '1g', 'At bedtime.', 'Reduce salt intake. Avoid stressful environments.', 'BP Balancer', 'Shavasana', [('Sarpagandha', 'Calming'), ('Watermelon', 'Diuretic')]),
            ('Hyperthyroidism', 'Coriander Seed Overnight Water', 'Soak coriander seeds in water overnight. Drink in morning.', '1 Cup', 'Empty stomach.', 'Avoid iodized salt and excessive caffeine.', 'Metabolic Cooler', 'Sarvangasana', [('Coriander', 'Thyroid balance'), ('Water', 'Hydration')]),
            ('Hypoglycemia', 'Dates & Raisins Mix', 'Eat soaked dates and raisins when feeling weak.', '5 units', 'Immediate.', 'Always carry a small sugary snack.', 'Energy Mix', 'Trikonasana', [('Dates', 'Natural sugar'), ('Raisins', 'Iron')]),
            ('Hypothyroidism', 'Walnuts & Brazil Nuts', 'Consume walnuts and brazil nuts daily.', '3 Nuts', 'Daily.', 'Avoid cruciferous vegetables (cabbage, broccoli) raw.', 'Glandular Support', 'Matsyasana', [('Walnuts', 'Omega-3'), ('Brazil Nut', 'Selenium')]),
            ('Impetigo', 'Neem & Turmeric Oil', 'Infuse neem in mustard oil with turmeric. Apply on sores.', 'External', 'Apply twice daily.', 'Avoid sharing towels or clothes with others.', 'Antiseptic Oil', 'Janu Sirsasana', [('Neem', 'Antibiotic'), ('Turmeric', 'Healing')]),
            ('Jaundice', 'Sugarcane Juice & Lemon', 'Drink sugarcane juice with lemon and ginger.', '1 Glass', 'Twice daily.', 'Avoid all heavy fats and alcohol for 1 month.', 'Liver Energizer', 'Gomukhasana', [('Sugarcane', 'Glucose'), ('Lemon', 'Vitamin C')]),
            ('Malaria', 'Sudarshan Churna & Warm Water', 'Mix Sudarshan powder in warm water.', '200ml', '3 times daily.', 'Use mosquito nets. Stay in well-ventilated rooms.', 'Fever Relief', 'Viparita Karani', [('Sudarshan', 'Anti-fever'), ('Water', 'Hydration')]),
            ('Migraine', 'Cow Ghee Nasal Drops', 'Put warm cow ghee in each nostril.', '2 Drops', 'Morning & Night.', 'Avoid loud noises and skipping meals.', 'Nasal Therapy', 'Padahastasana', [('Ghee', 'Nervous cooling'), ('Brahmi', 'Calm')]),
            ('Osteoarthristis', 'Sesame Seed & Milk', 'Soak sesame seeds overnight. Consume in morning.', '1 tsp', 'Daily.', 'Avoid cold floor sitting. Use warm water for bathing.', 'Bone Supplement', 'Setu Bandhasana', [('Sesame', 'Calcium'), ('Milk', 'Strength')]),
            ('Paralysis (brain hemorrhage)', 'Ashwagandha & Almond Milk', 'Mix Ashwagandha in warm almond milk.', '1 Cup', 'Drink at night.', 'Maintain consistent physiotherapy. Monitor BP.', 'Nerve Regenerator', 'Anulom Vilom', [('Ashwagandha', 'Neuro-repair'), ('Almond', 'Brain food')]),
            ('Peptic ulcer diseae', 'Cold Milk & Licorice', 'Mix Licorice powder in cold milk.', '1 Cup', 'Empty stomach.', 'Avoid spicy food, tea, and coffee.', 'Mucosal Shield', 'Vajrasana', [('Licorice', 'Healing'), ('Cold Milk', 'Buffer')]),
            ('Pneumonia', 'Trikatu & Honey', 'Mix Trikatu powder with honey.', '1 tsp', '3 times daily.', 'Avoid cold air. Keep the chest warm.', 'Expectorant', 'Gomukhasana', [('Trikatu', 'Heating'), ('Honey', 'Clears phlegm')]),
            ('Psoriasis', 'Coconut Oil & Neem Rub', 'Mix coconut oil with neem juice. Apply on patches.', 'External', 'Apply after bath.', 'Avoid high stress and citrus fruits.', 'Soothing Topical', 'Sarvangasana', [('Coconut', 'Moisturizing'), ('Neem', 'Anti-inflammatory')]),
            ('Tuberculosis', 'Chyawanprash & Goat Milk', 'Take Chyawanprash with goat milk.', '1 tbsp', 'Twice daily.', 'Maintain complete course of DOTS. Ensure sunlight.', 'Lung Tonic', 'Ujjayi Pranayama', [('Chyawanprash', 'Immunity'), ('Goat Milk', 'Nourishing')]),
            ('Typhoid', 'Raisins & Khubani Soak', 'Eat soaked raisins and apricots.', '12 units', 'Morning.', 'Drink only filtered/boiled water.', 'Recovery Mix', 'Balasana', [('Raisins', 'Easy energy'), ('Apricot', 'Digestive')]),
            ('Urinary tract infection', 'Barley Water & Cranberry', 'Boil barley in water. Drink throughout day.', '1 Liter', 'Continuous.', 'Maintain genital hygiene. Drink plenty of water.', 'Renal Flush', 'Mula Bandha', [('Barley', 'Diuretic'), ('Cranberry', 'Antibacterial')]),
            ('Varicose veins', 'Apple Cider Vinegar Rub', 'Gently massage ACV upwards on veins.', 'External', 'Twice daily.', 'Avoid standing for long hours. Wear support hose.', 'Vascular Rub', 'Viparita Karani', [('ACV', 'Flow improvement'), ('Massage', 'Circulation')]),
            ('hepatitis A', 'Papaya & Lemon Juice', 'Eat papaya with lemon and black salt.', '1 Bowl', 'Twice daily.', 'Avoid outside food and raw salads.', 'Digestive Enzyme', 'Ardha Matsyendrasana', [('Papaya', 'Enzymes'), ('Lemon', 'Vitamin C')])
        ]

        for p_name, r_name, prep, dose, cons, prec, form, yoga, ingredients in remedy_data:
            cursor.execute("INSERT OR IGNORE INTO problem (problem_name, problem_description) VALUES (?, ?)", (p_name, "Clinical Ayurvedic Protocol"))
            cursor.execute("SELECT problem_id FROM problem WHERE problem_name = ?", (p_name,))
            p_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO remedy (problem_id, remedy_name, description, dosage, consumption_steps, precautions, remedy_form, yoga_exercise, remedy_type) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Home Remedy')
            """, (p_id, r_name, prep, dose, cons, prec, form, yoga))
            r_id = cursor.lastrowid
            
            for ing_name, adv in ingredients:
                cursor.execute("INSERT OR IGNORE INTO ingredient (ingredient_name, advantages) VALUES (?, ?)", (ing_name, adv))
                cursor.execute("SELECT ingredient_id FROM ingredient WHERE ingredient_name = ?", (ing_name,))
                i_id = cursor.fetchone()[0]
                cursor.execute("INSERT OR IGNORE INTO remedy_ingredient (remedy_id, ingredient_id, quantity_needed) VALUES (?, ?, ?)", (r_id, i_id, "As needed"))

    conn.commit()
    conn.close()
    print("RemediCare SQLite Database Initialized Successfully.")

if __name__ == "__main__":
    setup_db()
