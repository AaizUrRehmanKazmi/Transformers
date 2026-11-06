# Error analysis: final_test (test)

90 of 206 rows have a label or evidence error.

| Category | Count |
|---|---|
| unsupported_decision_gold_NEI | 37 |
| missed_decision_pred_NEI | 18 |
| label_ok_evidence_missed | 14 |
| label_ok_evidence_mismatch | 8 |
| not_applicable_confusion | 6 |
| polarity_flip | 5 |
| label_ok_unsupported_evidence | 1 |
| format_failure | 1 |

## unsupported_decision_gold_NEI (37 rows)

**annotation 174** (patient sigir-201410, exclusion)

- Criterion: Patients with previous axillary surgery
- Gold: `not enough information`, evidence []
- Predicted: `not excluded`, evidence []
- Raw output: `{"label": "not excluded", "evidence": []}`
- Grounded explanation: Label 'not excluded': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning.
  > [1] She is now complaining of a cool right foot.
  > [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
  > [3] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 175** (patient sigir-201410, inclusion)

- Criterion: Chronic renal failure requiring hemodialysis.
- Gold: `not enough information`, evidence []
- Predicted: `not included`, evidence []
- Raw output: `{"label": "not included", "evidence": []}`
- Grounded explanation: Label 'not included': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning.
  > [1] She is now complaining of a cool right foot.
  > [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
  > [3] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 193** (patient sigir-201411, exclusion)

- Criterion: Patients were moribund.
- Gold: `not enough information`, evidence [0, 1, 2, 3, 4]
- Predicted: `not excluded`, evidence []
- Raw output: `{"label": "not excluded", "evidence": []}`
- Grounded explanation: Label 'not excluded': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 40-year-old woman with no past medical history presents to the ER with excruciating pain in her right arm that had started 1 hour prior to her admission.
  > [1] She denies trauma.
  > [2] On examination she is pale and in moderate discomfort, as well as tachypneic and tachycardic.
  > [3] Her body temperature is normal and her blood pressure is 80/60.
  > [4] Her right arm has no discoloration or movement limitation.
  > [5] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.


## missed_decision_pred_NEI (18 rows)

**annotation 177** (patient sigir-201410, inclusion)

- Criterion: Maintenance hemodialysis after central vena catheterization.
- Gold: `not included`, evidence []
- Predicted: `not enough information`, evidence []
- Raw output: `{"label": "not enough information", "evidence": []}`
- Grounded explanation: Label 'not enough information': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning.
  > [1] She is now complaining of a cool right foot.
  > [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
  > [3] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 185** (patient sigir-201411, inclusion)

- Criterion: Patients were included if they were diagnosed with Shock, Acute respiratory distress syndrome (ARDS), or both.
- Gold: `included`, evidence [2, 3]
- Predicted: `not enough information`, evidence []
- Raw output: `{"label": "not enough information", "evidence": []}`
- Grounded explanation: Label 'not enough information': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 40-year-old woman with no past medical history presents to the ER with excruciating pain in her right arm that had started 1 hour prior to her admission.
  > [1] She denies trauma.
  > [2] On examination she is pale and in moderate discomfort, as well as tachypneic and tachycardic.
  > [3] Her body temperature is normal and her blood pressure is 80/60.
  > [4] Her right arm has no discoloration or movement limitation.
  > [5] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 186** (patient sigir-201411, inclusion)

- Criterion: Heart rate of at least 90/min;
- Gold: `included`, evidence [2]
- Predicted: `not enough information`, evidence [3]
- Raw output: `{"label": "not enough information", "evidence": [3]}`
- Grounded explanation: Label 'not enough information', based on patient sentences: [3] Her body temperature is normal and her blood pressure is 80/60.
- Patient note:

  > [0] A 40-year-old woman with no past medical history presents to the ER with excruciating pain in her right arm that had started 1 hour prior to her admission.
  > [1] She denies trauma.
  > [2] On examination she is pale and in moderate discomfort, as well as tachypneic and tachycardic.
  > [3] Her body temperature is normal and her blood pressure is 80/60.
  > [4] Her right arm has no discoloration or movement limitation.
  > [5] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.


## label_ok_evidence_missed (14 rows)

**annotation 176** (patient sigir-201410, inclusion)

- Criterion: No medical history of central vena catheterization.
- Gold: `included`, evidence [0]
- Predicted: `included`, evidence []
- Raw output: `{"label": "included", "evidence": []}`
- Grounded explanation: Label 'included': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning.
  > [1] She is now complaining of a cool right foot.
  > [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
  > [3] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 179** (patient sigir-201410, exclusion)

- Criterion: Had been performed central venous puncture or catheterization before.
- Gold: `not excluded`, evidence [0]
- Predicted: `not excluded`, evidence []
- Raw output: `{"label": "not excluded", "evidence": []}`
- Grounded explanation: Label 'not excluded': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning.
  > [1] She is now complaining of a cool right foot.
  > [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
  > [3] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 197** (patient sigir-201411, exclusion)

- Criterion: Decreased level of consciousness
- Gold: `not excluded`, evidence [0, 5]
- Predicted: `not excluded`, evidence []
- Raw output: `{"label": "not excluded", "evidence": []}`
- Grounded explanation: Label 'not excluded': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 40-year-old woman with no past medical history presents to the ER with excruciating pain in her right arm that had started 1 hour prior to her admission.
  > [1] She denies trauma.
  > [2] On examination she is pale and in moderate discomfort, as well as tachypneic and tachycardic.
  > [3] Her body temperature is normal and her blood pressure is 80/60.
  > [4] Her right arm has no discoloration or movement limitation.
  > [5] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.


## label_ok_evidence_mismatch (8 rows)

**annotation 306** (patient sigir-201417, inclusion)

- Criterion: Patients with liver space occupying lesion (LOE) that require extended hepatic resection.
- Gold: `not enough information`, evidence [3]
- Predicted: `not enough information`, evidence [2, 3]
- Raw output: `{"label": "not enough information", "evidence": [2, 3]}`
- Grounded explanation: Label 'not enough information', based on patient sentences: [2] Abdominal ultrasound shows hepatomegaly and abundant free intraperitoneal fluid. [3] Exploratory laparotomy reveals a ruptured liver abscess, which is then surgically drained.
- Patient note:

  > [0] A 48-year-old white male with history of common variable immunodeficiency (CVID) with acute abdominal pain, fever, dehydration, HR of 132 bpm, BP 80/40.
  > [1] The physical examination is remarkable for tenderness and positive Murphy sign.
  > [2] Abdominal ultrasound shows hepatomegaly and abundant free intraperitoneal fluid.
  > [3] Exploratory laparotomy reveals a ruptured liver abscess, which is then surgically drained.
  > [4] After surgery, the patient is taken to the ICU.
  > [5] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 381** (patient sigir-201421, inclusion)

- Criterion: Age > 18 years at the time of signing the informed consent form
- Gold: `included`, evidence [0]
- Predicted: `included`, evidence [4]
- Raw output: `{"label": "included", "evidence": [4]}`
- Grounded explanation: Label 'included', based on patient sentences: [4] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.
- Patient note:

  > [0] A 21-year-old female is evaluated for progressive arthralgias and malaise.
  > [1] On examination she is found to have alopecia, a rash mainly distributed on the bridge of her nose and her cheeks, a delicate non-palpable purpura on her calves, and swelling and tenderness of her wrists and ankles.
  > [2] Her lab shows normocytic anemia, thrombocytopenia, a 4/4 positive ANA and anti-dsDNA.
  > [3] Her urine is positive for protein and RBC casts.
  > [4] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 382** (patient sigir-201421, inclusion)

- Criterion: Fulfil at least 4 criteria for SLE as defined by the American College of Rheumatology (ACR)
- Gold: `included`, evidence [0, 1, 2]
- Predicted: `included`, evidence [0, 1, 2, 3]
- Raw output: `{"label": "included", "evidence": [0, 1, 2, 3]}`
- Grounded explanation: Label 'included', based on patient sentences: [0] A 21-year-old female is evaluated for progressive arthralgias and malaise. [1] On examination she is found to have alopecia, a rash mainly distributed on the bridge of her nose and her cheeks, a delicate non-palpable purpura on her calves, and swelling and tenderness of her wrists and ankles. [2] Her lab shows normocytic anemia, thrombocytopenia, a 4/4 positive ANA and anti-dsDNA. [3] Her urine is positive for protein and RBC casts.
- Patient note:

  > [0] A 21-year-old female is evaluated for progressive arthralgias and malaise.
  > [1] On examination she is found to have alopecia, a rash mainly distributed on the bridge of her nose and her cheeks, a delicate non-palpable purpura on her calves, and swelling and tenderness of her wrists and ankles.
  > [2] Her lab shows normocytic anemia, thrombocytopenia, a 4/4 positive ANA and anti-dsDNA.
  > [3] Her urine is positive for protein and RBC casts.
  > [4] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.


## not_applicable_confusion (6 rows)

**annotation 322** (patient sigir-201417, exclusion)

- Criterion: Pregnant women or women of childbearing age who do not have adequate contraception.
- Gold: `not excluded`, evidence [0]
- Predicted: `not applicable`, evidence []
- Raw output: `{"label": "not applicable", "evidence": []}`
- Grounded explanation: Label 'not applicable': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 48-year-old white male with history of common variable immunodeficiency (CVID) with acute abdominal pain, fever, dehydration, HR of 132 bpm, BP 80/40.
  > [1] The physical examination is remarkable for tenderness and positive Murphy sign.
  > [2] Abdominal ultrasound shows hepatomegaly and abundant free intraperitoneal fluid.
  > [3] Exploratory laparotomy reveals a ruptured liver abscess, which is then surgically drained.
  > [4] After surgery, the patient is taken to the ICU.
  > [5] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 683** (patient sigir-20158, exclusion)

- Criterion: Previous tonsillectomy, including partial tonsillectomy
- Gold: `not applicable`, evidence []
- Predicted: `not excluded`, evidence []
- Raw output: `{"label": "not excluded", "evidence": []}`
- Grounded explanation: Label 'not excluded': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 10 yo boy with nighttime snoring, pauses in breathing, and restlessness with nighttime awakenings.
  > [1] No history of headache or night terrors.
  > [2] The boy's teacher recently contacted his parents because she was concerned about his declining grades, lack of attention, and excessive sleepiness during class.
  > [3] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 693** (patient sigir-20158, exclusion)

- Criterion: Suspected diagnosis of a sleep disorder other than OSA (i.e., periodic leg movements, narcolepsy, insomnia, central sleep apnea, sleep hypoventilation syndrome)
- Gold: `not applicable`, evidence []
- Predicted: `not excluded`, evidence []
- Raw output: `{"label": "not excluded", "evidence": []}`
- Grounded explanation: Label 'not excluded': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 10 yo boy with nighttime snoring, pauses in breathing, and restlessness with nighttime awakenings.
  > [1] No history of headache or night terrors.
  > [2] The boy's teacher recently contacted his parents because she was concerned about his declining grades, lack of attention, and excessive sleepiness during class.
  > [3] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.


## polarity_flip (5 rows)

**annotation 162** (patient sigir-201410, inclusion)

- Criterion: Patients undergoing open abdominal aortic aneurysm repair
- Gold: `not included`, evidence []
- Predicted: `included`, evidence [0, 1, 2]
- Raw output: `{"label": "included", "evidence": [0, 1, 2]}`
- Grounded explanation: Label 'included', based on patient sentences: [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning. [1] She is now complaining of a cool right foot. [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
- Patient note:

  > [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning.
  > [1] She is now complaining of a cool right foot.
  > [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
  > [3] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 163** (patient sigir-201410, inclusion)

- Criterion: Patients undergoing endovascular abdominal aneurysm repair
- Gold: `not included`, evidence []
- Predicted: `included`, evidence [0, 1, 2]
- Raw output: `{"label": "included", "evidence": [0, 1, 2]}`
- Grounded explanation: Label 'included', based on patient sentences: [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning. [1] She is now complaining of a cool right foot. [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
- Patient note:

  > [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning.
  > [1] She is now complaining of a cool right foot.
  > [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
  > [3] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 164** (patient sigir-201410, inclusion)

- Criterion: Patients undergoing surgical lower limb revascularisation (suprainguinal or infrainguinal)
- Gold: `not included`, evidence []
- Predicted: `included`, evidence [0]
- Raw output: `{"label": "included", "evidence": [0]}`
- Grounded explanation: Label 'included', based on patient sentences: [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning.
- Patient note:

  > [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning.
  > [1] She is now complaining of a cool right foot.
  > [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
  > [3] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.


## label_ok_unsupported_evidence (1 rows)

**annotation 384** (patient sigir-201421, inclusion)

- Criterion: Laboratory values as follows Hemoglobin ≥ 100 g/L Absolute neutrophil count ≥ 1.0 x 109/L Total bilirubin ≤ 1.5 x upper limit of normal (ULN) AST (SGOT) / ALT (SGPT) ≤ 2.5 x ULN
- Gold: `not enough information`, evidence []
- Predicted: `not enough information`, evidence [2]
- Raw output: `{"label": "not enough information", "evidence": [2]}`
- Grounded explanation: Label 'not enough information', based on patient sentences: [2] Her lab shows normocytic anemia, thrombocytopenia, a 4/4 positive ANA and anti-dsDNA.
- Patient note:

  > [0] A 21-year-old female is evaluated for progressive arthralgias and malaise.
  > [1] On examination she is found to have alopecia, a rash mainly distributed on the bridge of her nose and her cheeks, a delicate non-palpable purpura on her calves, and swelling and tenderness of her wrists and ankles.
  > [2] Her lab shows normocytic anemia, thrombocytopenia, a 4/4 positive ANA and anti-dsDNA.
  > [3] Her urine is positive for protein and RBC casts.
  > [4] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.


## format_failure (1 rows)

**annotation 697** (patient sigir-20158, exclusion)

- Criterion: Pregnant
- Gold: `not applicable`, evidence []
- Predicted: `invalid`, evidence []  (parse error: label_not_valid_for_type)
- Raw output: `{"label": "not pregnant", "evidence": []}`
- Grounded explanation: Label 'invalid': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 10 yo boy with nighttime snoring, pauses in breathing, and restlessness with nighttime awakenings.
  > [1] No history of headache or night terrors.
  > [2] The boy's teacher recently contacted his parents because she was concerned about his declining grades, lack of attention, and excessive sleepiness during class.
  > [3] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.
