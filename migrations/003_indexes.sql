CREATE UNIQUE INDEX IF NOT EXISTS idx_weekly_reports_week_start
ON weekly_reports (week_start);

CREATE INDEX IF NOT EXISTS idx_meals_meal_date
ON meals (meal_date);

CREATE INDEX IF NOT EXISTS idx_measurements_measurement_date
ON measurements (measurement_date);

CREATE INDEX IF NOT EXISTS idx_meal_items_meal_id
ON meal_items (meal_id);

CREATE INDEX IF NOT EXISTS idx_meal_items_food_id
ON meal_items (food_id);
