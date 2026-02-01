import csv
import os

CSV_FILE = os.path.join(os.path.dirname(__file__), "crop_disease_db.csv")

# -------- FALLBACK (USED ONLY IF CSV FAILS) --------
FALLBACK_DATA = {
    "corn common rust": {
        "overview": "Corn Common Rust is a fungal disease affecting maize leaves.",
        "cause": "Caused by fungus Puccinia sorghi.",
        "treatment": {
            "chemical": "Spray Mancozeb or Propiconazole.",
            "organic": "Neem oil spray every 7 days."
        },
        "prevention": [
            "Use resistant varieties",
            "Ensure proper spacing"
        ]
    }
}

# -------- CSV LOADER --------
def load_csv_data():
    data = {}
    if not os.path.exists(CSV_FILE):
        return data

    try:
        with open(CSV_FILE, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                disease = row["disease"].strip().lower()
                data[disease] = {
                    "overview": row.get("overview", ""),
                    "cause": row.get("cause", ""),
                    "treatment": {
                        "chemical": row.get("chemical", ""),
                        "organic": row.get("organic", "")
                    },
                    "prevention": [p.strip() for p in row.get("prevention", "").split(",") if p.strip()]
                }
    except Exception as e:
        print(f"Error loading CSV: {e}")
    return data

CSV_DATA = load_csv_data()

# -------- MAIN FUNCTION USED BY app.py --------
def get_disease_info(disease_name):
    if not disease_name:
        return None

    key = disease_name.strip().lower()

    # ✨ NEW: Check if the plant is healthy before searching
    if "healthy" in key:
        return {
            "overview": "The plant appears healthy.",
            "cause": "None",
            "treatment": {"chemical": "None", "organic": "None"},
            "prevention": ["Continue regular monitoring", "Maintain proper watering"]
        }

    # 1️⃣ Try CSV
    for csv_key in CSV_DATA:
        if csv_key in key or key in csv_key:
            return CSV_DATA[csv_key]

    # 2️⃣ Fallback (safe)
    if key in FALLBACK_DATA:
        return FALLBACK_DATA[key]

    # 3️⃣ Return a default dictionary instead of None to prevent crashes
    return {
        "overview": "No specific data found for this condition.",
        "cause": "Unknown",
        "treatment": {"chemical": "N/A", "organic": "N/A"},
        "prevention": []
    }