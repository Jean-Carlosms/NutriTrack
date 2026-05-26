CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    sex TEXT NOT NULL,
    height_cm REAL NOT NULL,
    current_weight_kg REAL NOT NULL,
    target_weight_kg REAL NOT NULL,
    activity_level TEXT NOT NULL,
    goal TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    portion_grams REAL NOT NULL,
    calories REAL NOT NULL,
    protein_g REAL NOT NULL,
    carbs_g REAL NOT NULL,
    fat_g REAL NOT NULL,
    fiber_g REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_date TEXT NOT NULL,
    meal_type TEXT NOT NULL,
    UNIQUE (meal_date, meal_type)
);

CREATE TABLE IF NOT EXISTS meal_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    quantity_grams REAL NOT NULL,
    FOREIGN KEY (meal_id) REFERENCES meals (id),
    FOREIGN KEY (food_id) REFERENCES foods (id)
);

CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_date TEXT NOT NULL,
    weight_kg REAL NOT NULL,
    waist_navel_cm REAL,
    waist_min_cm REAL,
    abdomen_cm REAL,
    chest_cm REAL,
    hip_cm REAL,
    right_arm_cm REAL,
    left_arm_cm REAL,
    right_thigh_cm REAL,
    left_thigh_cm REAL,
    neck_cm REAL,
    calf_cm REAL
);
