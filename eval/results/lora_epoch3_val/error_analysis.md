# Error analysis: lora_epoch3_val (val)

96 of 206 rows have a label or evidence error.

| Category | Count |
|---|---|
| unsupported_decision_gold_NEI | 34 |
| label_ok_evidence_missed | 29 |
| not_applicable_confusion | 9 |
| label_ok_evidence_mismatch | 9 |
| polarity_flip | 8 |
| missed_decision_pred_NEI | 7 |

## unsupported_decision_gold_NEI (34 rows)

**annotation 8** (patient sigir-20141, exclusion)

- Criterion: Unstable angina
- Gold: `not enough information`, evidence [0, 1, 2]
- Predicted: `not excluded`, evidence []
- Raw output: `{"label": "not excluded", "evidence": []}`
- Grounded explanation: Label 'not excluded': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 58-year-old African-American woman presents to the ER with episodic pressing/burning anterior chest pain that began two days earlier for the first time in her life.
  > [1] The pain started while she was walking, radiates to the back, and is accompanied by nausea, diaphoresis and mild dyspnea, but is not increased on inspiration.
  > [2] The latest episode of pain ended half an hour prior to her arrival.
  > [3] She is known to have hypertension and obesity.
  > [4] She denies smoking, diabetes, hypercholesterolemia, or a family history of heart disease.
  > [5] She currently takes no medications.
  > [6] Physical examination is normal.
  > [7] The EKG shows nonspecific changes.
  > [8] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 15** (patient sigir-20141, exclusion)

- Criterion: Pregnant and nursing women
- Gold: `not enough information`, evidence []
- Predicted: `not excluded`, evidence []
- Raw output: `{"label": "not excluded", "evidence": []}`
- Grounded explanation: Label 'not excluded': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 58-year-old African-American woman presents to the ER with episodic pressing/burning anterior chest pain that began two days earlier for the first time in her life.
  > [1] The pain started while she was walking, radiates to the back, and is accompanied by nausea, diaphoresis and mild dyspnea, but is not increased on inspiration.
  > [2] The latest episode of pain ended half an hour prior to her arrival.
  > [3] She is known to have hypertension and obesity.
  > [4] She denies smoking, diabetes, hypercholesterolemia, or a family history of heart disease.
  > [5] She currently takes no medications.
  > [6] Physical examination is normal.
  > [7] The EKG shows nonspecific changes.
  > [8] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 18** (patient sigir-20141, exclusion)

- Criterion: Patients not eligible for Tc 99m SPECT
- Gold: `not enough information`, evidence []
- Predicted: `not excluded`, evidence []
- Raw output: `{"label": "not excluded", "evidence": []}`
- Grounded explanation: Label 'not excluded': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 58-year-old African-American woman presents to the ER with episodic pressing/burning anterior chest pain that began two days earlier for the first time in her life.
  > [1] The pain started while she was walking, radiates to the back, and is accompanied by nausea, diaphoresis and mild dyspnea, but is not increased on inspiration.
  > [2] The latest episode of pain ended half an hour prior to her arrival.
  > [3] She is known to have hypertension and obesity.
  > [4] She denies smoking, diabetes, hypercholesterolemia, or a family history of heart disease.
  > [5] She currently takes no medications.
  > [6] Physical examination is normal.
  > [7] The EKG shows nonspecific changes.
  > [8] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.


## label_ok_evidence_missed (29 rows)

**annotation 0** (patient sigir-20141, inclusion)

- Criterion: Patients of chronic stable angina with abnormal Exercise Myocardial Perfusion Spect Scan with reversible and partially reversible ischemic changes.
- Gold: `not enough information`, evidence [0, 1, 2]
- Predicted: `not enough information`, evidence []
- Raw output: `{"label": "not enough information", "evidence": []}`
- Grounded explanation: Label 'not enough information': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 58-year-old African-American woman presents to the ER with episodic pressing/burning anterior chest pain that began two days earlier for the first time in her life.
  > [1] The pain started while she was walking, radiates to the back, and is accompanied by nausea, diaphoresis and mild dyspnea, but is not increased on inspiration.
  > [2] The latest episode of pain ended half an hour prior to her arrival.
  > [3] She is known to have hypertension and obesity.
  > [4] She denies smoking, diabetes, hypercholesterolemia, or a family history of heart disease.
  > [5] She currently takes no medications.
  > [6] Physical examination is normal.
  > [7] The EKG shows nonspecific changes.
  > [8] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 13** (patient sigir-20141, exclusion)

- Criterion: IDDM (Type-1 diabetes mellitus)
- Gold: `not excluded`, evidence [4]
- Predicted: `not excluded`, evidence []
- Raw output: `{"label": "not excluded", "evidence": []}`
- Grounded explanation: Label 'not excluded': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 58-year-old African-American woman presents to the ER with episodic pressing/burning anterior chest pain that began two days earlier for the first time in her life.
  > [1] The pain started while she was walking, radiates to the back, and is accompanied by nausea, diaphoresis and mild dyspnea, but is not increased on inspiration.
  > [2] The latest episode of pain ended half an hour prior to her arrival.
  > [3] She is known to have hypertension and obesity.
  > [4] She denies smoking, diabetes, hypercholesterolemia, or a family history of heart disease.
  > [5] She currently takes no medications.
  > [6] Physical examination is normal.
  > [7] The EKG shows nonspecific changes.
  > [8] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 14** (patient sigir-20141, exclusion)

- Criterion: Systolic blood pressure < 100 mm Hg
- Gold: `not excluded`, evidence [3]
- Predicted: `not excluded`, evidence []
- Raw output: `{"label": "not excluded", "evidence": []}`
- Grounded explanation: Label 'not excluded': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 58-year-old African-American woman presents to the ER with episodic pressing/burning anterior chest pain that began two days earlier for the first time in her life.
  > [1] The pain started while she was walking, radiates to the back, and is accompanied by nausea, diaphoresis and mild dyspnea, but is not increased on inspiration.
  > [2] The latest episode of pain ended half an hour prior to her arrival.
  > [3] She is known to have hypertension and obesity.
  > [4] She denies smoking, diabetes, hypercholesterolemia, or a family history of heart disease.
  > [5] She currently takes no medications.
  > [6] Physical examination is normal.
  > [7] The EKG shows nonspecific changes.
  > [8] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.


## not_applicable_confusion (9 rows)

**annotation 24** (patient sigir-20141, exclusion)

- Criterion: Patients with IHD within 6 months after percutaneous coronary intervention(PCI), and who are stable but are going to implement PCI or coronary artery bypass grafting(CABG)
- Gold: `not applicable`, evidence []
- Predicted: `not excluded`, evidence []
- Raw output: `{"label": "not excluded", "evidence": []}`
- Grounded explanation: Label 'not excluded': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 58-year-old African-American woman presents to the ER with episodic pressing/burning anterior chest pain that began two days earlier for the first time in her life.
  > [1] The pain started while she was walking, radiates to the back, and is accompanied by nausea, diaphoresis and mild dyspnea, but is not increased on inspiration.
  > [2] The latest episode of pain ended half an hour prior to her arrival.
  > [3] She is known to have hypertension and obesity.
  > [4] She denies smoking, diabetes, hypercholesterolemia, or a family history of heart disease.
  > [5] She currently takes no medications.
  > [6] Physical examination is normal.
  > [7] The EKG shows nonspecific changes.
  > [8] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 33** (patient sigir-20142, inclusion)

- Criterion: full of physical examination and laboratory examination have been carried out after one week，but still cannot make a definite diagnosis
- Gold: `not applicable`, evidence []
- Predicted: `included`, evidence []
- Raw output: `{"label": "included", "evidence": []}`
- Grounded explanation: Label 'included': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] An 8-year-old male presents in March to the ER with fever up to 39 C, dyspnea and cough for 2 days.
  > [1] He has just returned from a 5 day vacation in Colorado.
  > [2] Parents report that prior to the onset of fever and cough, he had loose stools.
  > [3] He denies upper respiratory tract symptoms.
  > [4] On examination he is in respiratory distress and has bronchial respiratory sounds on the left.
  > [5] A chest x-ray shows bilateral lung infiltrates.
  > [6] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 558** (patient sigir-201430, exclusion)

- Criterion: Inability to provide informed consent.
- Gold: `not applicable`, evidence [8]
- Predicted: `not excluded`, evidence [8]
- Raw output: `{"label": "not excluded", "evidence": [8]}`
- Grounded explanation: Label 'not excluded', based on patient sentences: [8] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.
- Patient note:

  > [0] A 72-year-old man complains of increasing calf pain when walking uphill.
  > [1] The symptoms have gradually increased over the past 3 months.
  > [2] The patient had an uncomplicated myocardial infarction 2 years earlier and a transient ischemic attack 6 months ago.
  > [3] Over the past month, his blood pressure has worsened despite previous control with diltiazem, hydrochlorothiazide, and propranolol.
  > [4] His is currently taking isosorbide dinitrate, hydrochlorothiazide, and aspirin.
  > [5] On physical examination, his blood pressure is 151/91 mm Hg, and his pulse is 67/min.
  > [6] There is a right carotid bruit.
  > [7] His lower extremities are slightly cool to the touch and have diminished pulses at the dorsalis pedis.
  > [8] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.


## label_ok_evidence_mismatch (9 rows)

**annotation 38** (patient sigir-20142, inclusion)

- Criterion: Patients with cough or shortness of breath
- Gold: `included`, evidence [0]
- Predicted: `included`, evidence [0, 4]
- Raw output: `{"label": "included", "evidence": [0, 4]}`
- Grounded explanation: Label 'included', based on patient sentences: [0] An 8-year-old male presents in March to the ER with fever up to 39 C, dyspnea and cough for 2 days. [4] On examination he is in respiratory distress and has bronchial respiratory sounds on the left.
- Patient note:

  > [0] An 8-year-old male presents in March to the ER with fever up to 39 C, dyspnea and cough for 2 days.
  > [1] He has just returned from a 5 day vacation in Colorado.
  > [2] Parents report that prior to the onset of fever and cough, he had loose stools.
  > [3] He denies upper respiratory tract symptoms.
  > [4] On examination he is in respiratory distress and has bronchial respiratory sounds on the left.
  > [5] A chest x-ray shows bilateral lung infiltrates.
  > [6] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 263** (patient sigir-201415, exclusion)

- Criterion: 13. Evidence of uterine pathology other than leiomyoma
- Gold: `excluded`, evidence [5]
- Predicted: `excluded`, evidence [4]
- Raw output: `{"label": "excluded", "evidence": [4]}`
- Grounded explanation: Label 'excluded', based on patient sentences: [4] The ultrasound reports enlarged uterus (12 cm x 9 cm x 7 cms) with multiple cystic areas in the interior.
- Patient note:

  > [0] A 36-year-old woman presents to the emergency department with 12 weeks of amenorrhea, vaginal spotting that has increased since yesterday, lower abdominal tenderness, nausea and vomiting.
  > [1] The physical exam reveals overall tender abdomen, 18-week sized uterus, and cervical dilation of 2 cm.
  > [2] The complete blood count and biochemical profile are normal.
  > [3] Point of care pregnancy test with cut-off sensitivity of 25 mIU/ml Beta-HCG is negative.
  > [4] The ultrasound reports enlarged uterus (12 cm x 9 cm x 7 cms) with multiple cystic areas in the interior.
  > [5] The differential diagnosis includes vesicular mole vs fibroid degeneration.
  > [6] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 499** (patient sigir-201427, inclusion)

- Criterion: Patients who are 18 years or older with a clinical or genetic diagnosis of FAP or attenuated FAP.
- Gold: `included`, evidence [0, 3]
- Predicted: `included`, evidence [0, 1, 2]
- Raw output: `{"label": "included", "evidence": [0, 1, 2]}`
- Grounded explanation: Label 'included', based on patient sentences: [0] A 21-year-old college student undergoes colonoscopy due to family history of multiple polyps in his older siblings. [1] His brother underwent total proctocolectomy at age 22, and his sister underwent a total proctocolectomy at age 28, after both were found to have hundreds of colonic adenomas on colonoscopy. [2] Both siblings are currently well without any findings of neoplasms.
- Patient note:

  > [0] A 21-year-old college student undergoes colonoscopy due to family history of multiple polyps in his older siblings.
  > [1] His brother underwent total proctocolectomy at age 22, and his sister underwent a total proctocolectomy at age 28, after both were found to have hundreds of colonic adenomas on colonoscopy.
  > [2] Both siblings are currently well without any findings of neoplasms.
  > [3] The patient undergoes sigmoidoscopy and is found to have dozens of small colonic polyps within rectosigmoid.
  > [4] Several of these are biopsied and are all benign adenomas.
  > [5] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.


## polarity_flip (8 rows)

**annotation 31** (patient sigir-20142, inclusion)

- Criterion: patients have fever more than one week
- Gold: `not included`, evidence [0]
- Predicted: `included`, evidence [0]
- Raw output: `{"label": "included", "evidence": [0]}`
- Grounded explanation: Label 'included', based on patient sentences: [0] An 8-year-old male presents in March to the ER with fever up to 39 C, dyspnea and cough for 2 days.
- Patient note:

  > [0] An 8-year-old male presents in March to the ER with fever up to 39 C, dyspnea and cough for 2 days.
  > [1] He has just returned from a 5 day vacation in Colorado.
  > [2] Parents report that prior to the onset of fever and cough, he had loose stools.
  > [3] He denies upper respiratory tract symptoms.
  > [4] On examination he is in respiratory distress and has bronchial respiratory sounds on the left.
  > [5] A chest x-ray shows bilateral lung infiltrates.
  > [6] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 241** (patient sigir-201415, exclusion)

- Criterion: Uterus size exceeding the umbilical level
- Gold: `not excluded`, evidence [1]
- Predicted: `excluded`, evidence [0, 4]
- Raw output: `{"label": "excluded", "evidence": [0, 4]}`
- Grounded explanation: Label 'excluded', based on patient sentences: [0] A 36-year-old woman presents to the emergency department with 12 weeks of amenorrhea, vaginal spotting that has increased since yesterday, lower abdominal tenderness, nausea and vomiting. [4] The ultrasound reports enlarged uterus (12 cm x 9 cm x 7 cms) with multiple cystic areas in the interior.
- Patient note:

  > [0] A 36-year-old woman presents to the emergency department with 12 weeks of amenorrhea, vaginal spotting that has increased since yesterday, lower abdominal tenderness, nausea and vomiting.
  > [1] The physical exam reveals overall tender abdomen, 18-week sized uterus, and cervical dilation of 2 cm.
  > [2] The complete blood count and biochemical profile are normal.
  > [3] Point of care pregnancy test with cut-off sensitivity of 25 mIU/ml Beta-HCG is negative.
  > [4] The ultrasound reports enlarged uterus (12 cm x 9 cm x 7 cms) with multiple cystic areas in the interior.
  > [5] The differential diagnosis includes vesicular mole vs fibroid degeneration.
  > [6] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 252** (patient sigir-201415, exclusion)

- Criterion: 2. Uterine size >20 weeks as evaluated by US or MR.
- Gold: `not excluded`, evidence [1]
- Predicted: `excluded`, evidence [4]
- Raw output: `{"label": "excluded", "evidence": [4]}`
- Grounded explanation: Label 'excluded', based on patient sentences: [4] The ultrasound reports enlarged uterus (12 cm x 9 cm x 7 cms) with multiple cystic areas in the interior.
- Patient note:

  > [0] A 36-year-old woman presents to the emergency department with 12 weeks of amenorrhea, vaginal spotting that has increased since yesterday, lower abdominal tenderness, nausea and vomiting.
  > [1] The physical exam reveals overall tender abdomen, 18-week sized uterus, and cervical dilation of 2 cm.
  > [2] The complete blood count and biochemical profile are normal.
  > [3] Point of care pregnancy test with cut-off sensitivity of 25 mIU/ml Beta-HCG is negative.
  > [4] The ultrasound reports enlarged uterus (12 cm x 9 cm x 7 cms) with multiple cystic areas in the interior.
  > [5] The differential diagnosis includes vesicular mole vs fibroid degeneration.
  > [6] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.


## missed_decision_pred_NEI (7 rows)

**annotation 367** (patient sigir-201420, inclusion)

- Criterion: Has experienced acute surgical abdomen requiring open abdominal laparotomy with primary closure
- Gold: `included`, evidence [0, 4]
- Predicted: `not enough information`, evidence []
- Raw output: `{"label": "not enough information", "evidence": []}`
- Grounded explanation: Label 'not enough information': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 32-year-old woman is admitted to the ER following a car accident.
  > [1] She has sustained multiple injuries including upper and lower extremity fractures.
  > [2] She is fully awake and alert, and she reports that she was not wearing a seat belt.
  > [3] Her blood pressure is 134/74 mm Hg, and her pulse is 87/min.
  > [4] Physical examination reveals a tender abdomen with guarding and rebound in all four quadrants.
  > [5] She has no bowel sounds.
  > [6] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 369** (patient sigir-201420, exclusion)

- Criterion: Estimated Abbreviated Injury Scale (AIS) score of six (6) at the time of surgery, for all trauma patients
- Gold: `not excluded`, evidence [2]
- Predicted: `not enough information`, evidence []
- Raw output: `{"label": "not enough information", "evidence": []}`
- Grounded explanation: Label 'not enough information': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 32-year-old woman is admitted to the ER following a car accident.
  > [1] She has sustained multiple injuries including upper and lower extremity fractures.
  > [2] She is fully awake and alert, and she reports that she was not wearing a seat belt.
  > [3] Her blood pressure is 134/74 mm Hg, and her pulse is 87/min.
  > [4] Physical examination reveals a tender abdomen with guarding and rebound in all four quadrants.
  > [5] She has no bowel sounds.
  > [6] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.

**annotation 370** (patient sigir-201420, exclusion)

- Criterion: American Society of Anesthesiologists Physical Status Classification (ASA) score of five (5) or greater (As ASA scoring is a subjective measure, if the PI finds the patient stable enough for study participation despite a score of 5, enrollment may continue.)
- Gold: `not excluded`, evidence [2]
- Predicted: `not enough information`, evidence []
- Raw output: `{"label": "not enough information", "evidence": []}`
- Grounded explanation: Label 'not enough information': the model cited no supporting sentence. Absence of evidence is not treated as proof of eligibility or ineligibility.
- Patient note:

  > [0] A 32-year-old woman is admitted to the ER following a car accident.
  > [1] She has sustained multiple injuries including upper and lower extremity fractures.
  > [2] She is fully awake and alert, and she reports that she was not wearing a seat belt.
  > [3] Her blood pressure is 134/74 mm Hg, and her pulse is 87/min.
  > [4] Physical examination reveals a tender abdomen with guarding and rebound in all four quadrants.
  > [5] She has no bowel sounds.
  > [6] The patient will provide informed consent, and will comply with the trial protocol without any practical issues.
