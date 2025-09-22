from main_home.models import ComponentInformation, TestOffered

component_data = [
    (1, 'Red Blood Cell Count (RBC)', 'M/μL', 4.5, 5.5, 4, 5),
    (2, 'White Blood Cell Count (WBC)', 'cells/μL', 4.3, 10.8, 4.3, 10.8),
    (3, 'Platelet Count (PLT)', 'mm3', 150, 450, 150, 450),
    (4, 'Hemoglobin (Hb)', 'g/dL', 13.5, 17.5, 12, 15.5),
    (5, 'Hematocrit (Hct)', '%', 38.8, 50, 34.9, 44.5),
    (6, 'Mean Corpuscular Volume (MCV)', 'fL', 80, 96, 80, 96),
    (7, 'Mean Corpuscular Hemoglobin (MCH)', 'pg', 27, 31, 27, 31),
    (8, 'Mean Corpuscular Hemoglobin Concentration (MCHC)', 'g/dL', 32, 36, 32, 36),
    (9, 'Glucose (GLU)', 'mg/dL', 70, 99, 70, 99),
    (10, 'Sodium (Na)', 'mEq/L', 135, 145, 135, 145),
    (11, 'Potassium (K)', 'mEq/L', 3.5, 5, 3.5, 5),
    (12, 'Calcium (Ca)', 'mg/dL', 8.5, 10.5, 8.5, 10.5),
    (13, 'Chloride (Cl)', 'mEq/L', 96, 106, 96, 106),
    (14, 'Carbon Dioxide (CO2)', 'mEq/L', 23, 29, 23, 29),
    (15, 'Blood Urea Nitrogen (BUN)', 'mg/dL', 7, 20, 7, 20),
    (16, 'Creatinine (Cr)', 'mg/dL', 0.6, 1.3, 0.5, 1.1),
    (17, 'Total Cholesterol (TC)', 'mg/dL', 200, 240, 200, 240),
    (18, 'High-Density Lipoprotein (HDL)', 'mg/dL', 40, 60, 50, 60),
    (19, 'Low-Density Lipoprotein (LDL)', 'mg/dL', 100, 190, 100, 190),
    (20, 'Triglyceride (TG)', 'mg/dL', 100, 200, 100, 200),
    (21, 'HbA1c', '%', 4, 6.5, 4, 6.5),
    (22, 'Vitamin D', 'ng/mL', 12, 50, 12, 50),
    (23, 'Albumin (Alb)', 'g/dL', 3.5, 5.5, 3.5, 5.5),
    (24, 'Bilirubin (Bili)', 'mg/dL', 0.1, 1.2, 0.1, 1.2),
    (25, 'Total Protein Level (TP)', 'g/dL', 6.0, 8.5, 6.0, 8.5),
    (26, 'Alkaline Phosphatase (ALP)', 'IU/L', 30, 120, 30, 120),
    (27, 'Alanine Aminotransferase (ALT)', 'IU/L', 10, 40, 10, 40),
    (28, 'Aspartate Aminotransferase (AST)', 'IU/L', 10, 35, 10, 35),
    (29, 'Thyroid-Stimulating Hormone (TSH)', 'μIU/mL', 0.4, 4, 0.4, 4),
    (30, 'Triiodothyronine (T3)', 'ng/dL', 80, 200, 80, 200),
    (31, 'Thyroxine (T4)', 'μg/dL', 4.5, 12, 4.5, 12),
    (32, 'Prothrombin Time (PT)', 'seconds', 10, 14, 10, 14),
    (33, 'Partial Thromboplastin Time (PTT)', 'seconds', 25, 35, 25, 35),
    (34, 'International Normalized Ratio (INR)', 'ratio', 0.8, 1.2, 0.8, 1.2),
    (35, 'Red Cell Distribution Width (RDW)', '%', 11.5, 14.5, 11.5, 14.5),
]

test_data = [
    (1, 'Complete Blood Count (CBC)',29),
    (2, 'Basic Metabolic Panel (BMP)',26),
    (3, 'Lipid Panel',19),
    (4, 'Hemoglobin A1C (HbA1c)',31),
    (5, 'Vitamin D Levels',18),
    (6, 'Coagulation Panel',86),
    (7, 'Thyroid Function Tests', 100),
    (8, 'Comprehensive Metabolic Panel (CMP)',48)
]



print("Inserting component Data...")

for data in component_data:
    component = ComponentInformation()
    component.id = data[0]
    component.name = data[1]
    component.unit = data[2]
    component.low_male_range = data[3]
    component.high_male_range = data[4]
    component.low_female_range = data[5]
    component.high_female_range = data[6]
    component.save()
    
print("Components Saved!")
    
print("Inserting Test names Data...")
    
for data in test_data:
    test_offered = TestOffered()
    test_offered.id = data[0]
    test_offered.name = data[1]
    test_offered.price = data[2]
    if data[1] in ['Complete Blood Count (CBC)', 'Hemoglobin A1C (HbA1c)', 'Coagulation Panel', 'Thyroid Function Tests']:
        test_offered.urgent = True
        
    test_offered.save()
    

print("Test names Saved!")
