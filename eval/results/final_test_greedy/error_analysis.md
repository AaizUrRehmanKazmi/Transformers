# Error analysis: final_test_greedy (test)

92 of 206 rows have a label or evidence error.

| Category | Count |
|---|---|
| unsupported_decision_gold_NEI | 32 |
| missed_decision_pred_NEI | 19 |
| label_ok_evidence_mismatch | 12 |
| label_ok_unsupported_evidence | 11 |
| label_ok_evidence_missed | 8 |
| not_applicable_confusion | 6 |
| polarity_flip | 4 |

## unsupported_decision_gold_NEI (32 rows)

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


## missed_decision_pred_NEI (19 rows)

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


## label_ok_evidence_mismatch (12 rows)

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

**annotation 307** (patient sigir-201417, inclusion)

- Criterion: Patient selection should be cautious, covering basically 5 types of liver damage which must be submitted prior to liver volumetry: Metastatic Disease subsidiary right hepatectomy extended to segment IV Metastatic Disease subsidiary right hepatectomy with suspected diseased liver (neoadjuvant chemotherapy) (in cases of doubt may be used liver function test indocyanine green) Bilobar liver metastases with multiple nodules in the right lobe and more than 3 nodules greater than 30 mm in the left hepatic lobe (LHI) will perform lumpectomies the LHI + right portal branch ligation (or postoperative percutaneous embolization) in order to make right hepatectomy 4-6 weeks (two stage surgery) Subsidiary Hepatocarcinoma extended right hepatectomy Liver Injury benign / malignant (Hemangiomas, hydatid cysts or liver tumors / primary bile hepatoblastoma), which by extension threatens the viability of the remaining liver tissue.
- Gold: `not enough information`, evidence [3]
- Predicted: `not enough information`, evidence [0, 1, 2, 3, 4]
- Raw output: `{"label": "not enough information", "evidence": [0, 1, 2, 3, 4]}`
- Grounded explanation: Label 'not enough information', based on patient sentences: [0] A 48-year-old white male with history of common variable immunodeficiency (CVID) with acute abdominal pain, fever, dehydration, HR of 132 bpm, BP 80/40. [1] The physical examination is remarkable for tenderness and positive Murphy sign. [2] Abdominal ultrasound shows hepatomegaly and abundant free intraperitoneal fluid. [3] Exploratory laparotomy reveals a ruptured liver abscess, which is then surgically drained. [4] After surgery, the patient is taken to the ICU.
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


## label_ok_unsupported_evidence (11 rows)

**annotation 161** (patient sigir-201410, inclusion)

- Criterion: Patients undergoing elective carotid endarterectomy
- Gold: `not included`, evidence []
- Predicted: `not included`, evidence [0]
- Raw output: `{"label": "not included", "evidence": [0]}`
- Grounded explanation: Label 'not included', based on patient sentences: [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning.
- Patient note:

  > [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning.
  > [1] She is now complaining of a cool right foot.
  > [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
  > [3] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 162** (patient sigir-201410, inclusion)

- Criterion: Patients undergoing open abdominal aortic aneurysm repair
- Gold: `not included`, evidence []
- Predicted: `not included`, evidence [0, 1, 2]
- Raw output: `{"label": "not included", "evidence": [0, 1, 2]}`
- Grounded explanation: Label 'not included', based on patient sentences: [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning. [1] She is now complaining of a cool right foot. [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
- Patient note:

  > [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning.
  > [1] She is now complaining of a cool right foot.
  > [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
  > [3] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 189** (patient sigir-201411, inclusion)

- Criterion: at least 1 of 3 signs of hypoperfusion (urine output < 0.5mL/kg of body weight per hour for 1 hour or more; neurologic dysfunction defined by confusion, psychosis, or a Glasgow coma scale score of ≤ 6; plasma lactate higher than the upper limit of the normal value).
- Gold: `not enough information`, evidence []
- Predicted: `not enough information`, evidence [2, 3]
- Raw output: `{"label": "not enough information", "evidence": [2, 3]}`
- Grounded explanation: Label 'not enough information', based on patient sentences: [2] On examination she is pale and in moderate discomfort, as well as tachypneic and tachycardic. [3] Her body temperature is normal and her blood pressure is 80/60.
- Patient note:

  > [0] A 40-year-old woman with no past medical history presents to the ER with excruciating pain in her right arm that had started 1 hour prior to her admission.
  > [1] She denies trauma.
  > [2] On examination she is pale and in moderate discomfort, as well as tachypneic and tachycardic.
  > [3] Her body temperature is normal and her blood pressure is 80/60.
  > [4] Her right arm has no discoloration or movement limitation.
  > [5] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.


## label_ok_evidence_missed (8 rows)

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

**annotation 198** (patient sigir-201411, exclusion)

- Criterion: Inability to answer questions
- Gold: `not excluded`, evidence [5]
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


## polarity_flip (4 rows)

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

**annotation 166** (patient sigir-201410, exclusion)

- Criterion: Significant upper limb peripheral arterial disease
- Gold: `not excluded`, evidence []
- Predicted: `excluded`, evidence [1, 2]
- Raw output: `{"label": "excluded", "evidence": [1, 2]}`
- Grounded explanation: Label 'excluded', based on patient sentences: [1] She is now complaining of a cool right foot. [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
- Patient note:

  > [0] A physician is called to see a 67-year-old woman who underwent cardiac catheterization via the right femoral artery earlier in the morning.
  > [1] She is now complaining of a cool right foot.
  > [2] Upon examination she has a pulsatile mass in her right groin with loss of distal pulses, and auscultation reveals a bruit over the point at which the right femoral artery was entered.
  > [3] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.
