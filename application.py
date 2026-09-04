from flask import Flask, request, render_template, session, redirect, url_for, jsonify
import numpy as np
import pickle
import sqlite3

# -------------------------------
# Flask App
# -------------------------------
application = Flask(__name__)
app = application

# Flask session secret key
app.secret_key = "remedycare_project_2026"

import os
from db_setup import setup_db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "medicine_system.db")

# Automatically ensure SQLite schema and seed data exist on startup
setup_db(DB_PATH)

# -------------------------------
# SQLite Database Connection
# -------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------------
# Load ML Model
# -------------------------------
MODEL_PATH = os.path.join(BASE_DIR, "models", "svc.pkl")
svc = pickle.load(open(MODEL_PATH, "rb"))

# -------------------------------
# Symptoms & Diseases Mappings
# -------------------------------
symptoms_dict = {'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3, 'shivering': 4, 'chills': 5, 'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8, 'ulcers_on_tongue': 9, 'muscle_wasting': 10, 'vomiting': 11, 'burning_micturition': 12, 'spotting_ urination': 13, 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16, 'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight_loss': 19, 'restlessness': 20, 'lethargy': 21, 'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24, 'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27, 'sweating': 28, 'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32, 'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36, 'back_pain': 37, 'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40, 'mild_fever': 41, 'yellow_urine': 42, 'yellowing_of_eyes': 43, 'acute_liver_failure': 44, 'fluid_overload': 45, 'swelling_of_stomach': 46, 'swelled_lymph_nodes': 47, 'malaise': 48, 'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51, 'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55, 'chest_pain': 56, 'weakness_in_limbs': 57, 'fast_heart_rate': 58, 'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61, 'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65, 'bruising': 66, 'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69, 'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71, 'brittle_nails': 72, 'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75, 'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78, 'hip_joint_pain': 79, 'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82, 'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85, 'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88, 'bladder_discomfort': 89, 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91, 'passage_of_gases': 92, 'internal_itching': 93, 'toxic_look_(typhos)': 94, 'depression': 95, 'irritability': 96, 'muscle_pain': 97, 'altered_sensorium': 98, 'red_spots_over_body': 99, 'belly_pain': 100, 'abnormal_menstruation': 101, 'dischromic _patches': 102, 'watering_from_eyes': 103, 'increased_appetite': 104, 'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107, 'rusty_sputum': 108, 'lack_of_concentration': 109, 'visual_disturbances': 110, 'receiving_blood_transfusion': 111, 'receiving_unsterile_injections': 112, 'coma': 113, 'stomach_bleeding': 114, 'distention_of_abdomen': 115, 'history_of_alcohol_consumption': 116, 'fluid_overload.1': 117, 'blood_in_sputum': 118, 'prominent_veins_on_calf': 119, 'palpitations': 120, 'painful_walking': 121, 'pus_filled_pimples': 122, 'blackheads': 123, 'scurring': 124, 'skin_peeling': 125, 'silver_like_dusting': 126, 'small_dents_in_nails': 127, 'inflammatory_nails': 128, 'blister': 129, 'red_sore_around_nose': 130, 'yellow_crust_ooze': 131}

diseases_list = {0: '(vertigo) Paroymsal Positional Vertigo', 1: 'AIDS', 2: 'Acne', 3: 'Alcoholic hepatitis', 4: 'Allergy', 5: 'Arthritis', 6: 'Bronchial Asthma', 7: 'Cervical spondylosis', 8: 'Chicken pox', 9: 'Chronic cholestasis', 10: 'Common Cold', 11: 'Dengue', 12: 'Diabetes', 13: 'Dimorphic hemmorhoids(piles)', 14: 'Drug Reaction', 15: 'Fungal infection', 16: 'GERD', 17: 'Gastroenteritis', 18: 'Heart attack', 19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E', 23: 'Hypertension', 24: 'Hyperthyroidism', 25: 'Hypoglycemia', 26: 'Hypothyroidism', 27: 'Impetigo', 28: 'Jaundice', 29: 'Malaria', 30: 'Migraine', 31: 'Osteoarthristis', 32: 'Paralysis (brain hemorrhage)', 33: 'Peptic ulcer diseae', 34: 'Pneumonia', 35: 'Psoriasis', 36: 'Tuberculosis', 37: 'Typhoid', 38: 'Urinary tract infection', 39: 'Varicose veins', 40: 'hepatitis A'}

# -------------------------------
# ML Prediction Function
# -------------------------------
def get_predicted_disease(patient_symptoms):
    input_vector = np.zeros(len(symptoms_dict))

    for item in patient_symptoms:
        clean_item = item.lower().strip().replace(" ", "_")
        if clean_item in symptoms_dict:
            input_vector[symptoms_dict[clean_item]] = 1

    prediction = svc.predict([input_vector])[0]
    disease = diseases_list.get(prediction, "Unknown Disease")
    
    symptoms_str = "_".join(patient_symptoms).lower()
    
    if any(x in symptoms_str for x in ['joint', 'knee', 'stiffness', 'walking', 'muscle']):
        if disease not in ['Arthritis', 'Osteoarthristis', 'Cervical spondylosis']:
            disease = 'Arthritis'
            
    if any(x in symptoms_str for x in ['chest', 'cough', 'breathless', 'throat']):
        if disease not in ['Heart attack', 'Bronchial Asthma', 'Pneumonia', 'Tuberculosis', 'Common Cold']:
            disease = 'Bronchial Asthma'
            
    if any(x in symptoms_str for x in ['headache', 'dizziness', 'vision', 'spinning']):
        if disease not in ['Migraine', '(vertigo) Paroymsal Positional Vertigo', 'Paralysis (brain hemorrhage)']:
            disease = 'Migraine'

    if any(x in symptoms_str for x in ['sinus', 'congestion', 'sneezing', 'runny_nose']):
        if disease not in ['Allergy', 'Bronchial Asthma', 'Common Cold']:
            disease = 'Allergy'

    return disease

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE email = ? AND password = ?"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session["user_id"] = user["user_id"]
            session["full_name"] = user["full_name"]
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", message="Invalid Email or Password")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        age = request.form.get("age")
        gender = request.form.get("gender")
        region = request.form.get("allergy")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return render_template("register.html", message="Email already registered.")

            query = "INSERT INTO users (full_name, email, password, age, gender, region) VALUES (?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (full_name, email, password, age, gender, region))
            conn.commit()
            
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            session["user_id"] = user["user_id"]
            session["full_name"] = user["full_name"]
            
            cursor.close()
            conn.close()
            return redirect(url_for("dashboard"))
            
        except Exception as e:
            if conn: conn.close()
            return render_template("register.html", message="System Error: " + str(e))
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (session["user_id"],))
    user_data = cursor.fetchone()

    if not user_data:
        cursor.close()
        conn.close()
        session.clear()
        return redirect(url_for("login"))

    cursor.execute("""
        SELECT *, (day_number * 100 / total_days) as progress_percent 
        FROM tracker 
        WHERE user_id = ? AND status = 'In Progress' 
        ORDER BY tracker_id DESC
    """, (session["user_id"],))
    active_trackers = cursor.fetchall()

    cursor.execute("SELECT * FROM tracker WHERE user_id = ? AND status != 'In Progress' ORDER BY tracker_id DESC", (session["user_id"],))
    history_data = cursor.fetchall()

    cursor.execute("SELECT * FROM clinics")
    clinics = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template("dashboard.html", 
                           active=active_trackers, 
                           history=history_data, 
                           user=user_data,
                           clinics=clinics)

@app.route("/start_treatment/<disease>")
def start_treatment(disease):
    if "user_id" not in session: 
        return redirect(url_for("login"))
    
    remedy_name = request.args.get("remedy", "Standard Protocol")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    notes = f"Clinical Protocol for {disease}"
    
    cursor.execute("""
        INSERT INTO tracker (user_id, status, notes, remedy_name, next_dose_time, start_date, day_number, total_days)
        VALUES (?, ?, ?, ?, datetime('now'), date('now'), 1, 14)
    """, (session["user_id"], "In Progress", notes, remedy_name))
    
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/mark_dose_done/<int:tracker_id>")
def mark_dose_done(tracker_id):
    if "user_id" not in session: 
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tracker WHERE tracker_id = ? AND user_id = ?", (tracker_id, session["user_id"]))
    track = cursor.fetchone()
    
    if track:
        cursor.execute("""
            UPDATE tracker 
            SET next_dose_time = datetime('now', '+6 hours'),
                day_number = day_number + 1
            WHERE tracker_id = ?
        """, (tracker_id,))
        
        if track['day_number'] >= track['total_days']:
            cursor.execute("UPDATE tracker SET status = 'Completed' WHERE tracker_id = ?", (tracker_id,))
            
        conn.commit()
    
    cursor.close()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

def helper(dis, user_age=25, user_gender='Male'):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM problem WHERE TRIM(problem_name) = TRIM(?)", (dis,))
    problem = cursor.fetchone()
    
    data = {
        "description": "",
        "medications": [],
        "precautions": [],
        "diets": [],
        "workouts": [],
        "remedies": []
    }
    
    if problem:
        data["description"] = problem['problem_description']
        problem_id = problem['problem_id']
        
        cursor.execute("SELECT * FROM remedy WHERE problem_id = ?", (problem_id,))
        remedies = cursor.fetchall()
        
        for r in remedies:
            cursor.execute("""
                SELECT i.*, ri.quantity_needed 
                FROM ingredient i
                JOIN remedy_ingredient ri ON i.ingredient_id = ri.ingredient_id
                WHERE ri.remedy_id = ?
            """, (r['remedy_id'],))
            r = dict(r)
            r['ingredients'] = cursor.fetchall()
            data["remedies"].append(r)
               
    cursor.close()
    conn.close()
    
    data['dosage_context'] = f"Adjusted for {user_gender}, Age {user_age}"
    return data

@app.route("/predict", methods=["POST"])
def predict():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if request.is_json:
        data = request.get_json()
        symptoms = data.get("symptoms", [])
        weather = data.get("weather", "Normal")
        temp = data.get("temp", "25")
        body_part = data.get("body_part", "General")
        severity = data.get("severity", "5")
    else:
        symptoms = request.form.getlist("symptoms")
        weather = "Normal"
        temp = "25"
        body_part = "General"
        severity = "5"

    if not symptoms:
        return jsonify({"error": "No symptoms selected"}), 400

    predicted_disease = get_predicted_disease(symptoms)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        notes = f"Disease: {predicted_disease} | Severity: {severity}/10 | Weather: {weather} ({temp}°C) | Part: {body_part}"
        insert_query = "INSERT INTO tracker (user_id, status, notes, start_date) VALUES (?, ?, ?, date('now'))"
        cursor.execute(insert_query, (session["user_id"], "Diagnosed", notes))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e: 
        print(f"DB Error: {e}")

    if request.is_json:
        return jsonify({"disease": predicted_disease, "severity": severity})
    
    return redirect(url_for("result_page", disease=predicted_disease, severity=severity))

@app.route("/result")
def result_page():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    disease = request.args.get("disease")
    severity = request.args.get("severity", "5")

    if not disease:
        return redirect(url_for("dashboard"))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT age, gender FROM users WHERE user_id = ?", (session["user_id"],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        session.clear()
        return redirect(url_for("login"))

    data = helper(disease, user['age'], user['gender'])
    
    clinic = None
    if int(severity) >= 8:
        e_conn = get_db_connection()
        e_cursor = e_conn.cursor()
        e_cursor.execute("SELECT * FROM clinics ORDER BY RANDOM() LIMIT 1")
        clinic = e_cursor.fetchone()
        e_cursor.close()
        e_conn.close()

    return render_template(
        "result.html",
        disease=disease,
        severity=int(severity),
        description=data['description'],
        precautions=data['precautions'],
        remedies=data['remedies'],
        dosage_context=data.get('dosage_context', ""),
        clinic=clinic
    )

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/developer")
def developer():
    return render_template("devloper.html")

@app.route("/search")
def search():
    query = request.args.get("query", "")
    if not query:
        return jsonify([])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT problem_name as name, 'Condition' as type FROM problem WHERE problem_name LIKE ? LIMIT 5", (f"%{query}%",))
    results = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT remedy_name as name, 'Remedy' as type FROM remedy WHERE remedy_name LIKE ? LIMIT 5", (f"%{query}%",))
    remedies = [dict(row) for row in cursor.fetchall()]
    results.extend(remedies)
    
    cursor.close()
    conn.close()
    return jsonify(results)

@app.route("/diagnostic")
def diagnostic():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("diagnostic.html")

@app.route("/weather")
def weather():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("weather_assessment.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        if "user_id" not in session: 
            return jsonify({"error": "Unauthorized"}), 401
        
        user_msg = request.json.get("message", "").lower()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        found_disease = None
        if "throat" in user_msg or ("pain" in user_msg and "stomach" not in user_msg): 
            found_disease = "GERD"
        elif "cold" in user_msg or "cough" in user_msg: 
            found_disease = "Common Cold"
        elif "stomach" in user_msg: 
            found_disease = "Peptic ulcer diseae"
        elif "fever" in user_msg: 
            found_disease = "Malaria"
        elif "head" in user_msg: 
            found_disease = "Migraine"
        
        if found_disease:
            cursor.execute("SELECT * FROM problem WHERE problem_name = ?", (found_disease,))
            prob = cursor.fetchone()
            
            if prob:
                cursor.execute("""
                    SELECT r.* FROM remedy r 
                    WHERE r.problem_id = ? LIMIT 1
                """, (prob['problem_id'],))
                rem = cursor.fetchone()
                
                response = {
                    "reply": f"Based on your symptoms, it seems like <strong>{found_disease}</strong>.",
                    "reason": prob['problem_description'] if prob['problem_description'] else "Clinical assessment required.",
                    "remedy": f"Try <strong>{rem['remedy_name']}</strong>: {rem['description']}" if rem else "Follow a light diet and drink warm water.",
                    "precautions": "Maintain hydration and avoid irritants.",
                    "status": "success"
                }
            else:
                response = {"reply": "I've detected the symptoms, but I need more details. Are you feeling nauseous?", "status": "fallback"}
        else:
            response = {"reply": "I am analyzing your symptoms. Could you please specify if you have any fever, skin rash, or digestive issues?", "status": "fallback"}
            
        cursor.close()
        conn.close()
        return jsonify(response)
    except Exception as e:
        print(f"Chatbot Error: {e}")
        return jsonify({"reply": "My clinical database is currently synchronizing. Please try again in a moment.", "status": "error"})

if __name__ == '__main__':
    app.run(debug=True)
