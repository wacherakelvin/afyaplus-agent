# evaluation/evaluation_data.py
"""15-question clinical verification set, 5 per channel.
References follow standard guidance (WHO IMCI, Kenya MoH, product labels) and should be
reviewed by a clinician before any production use."""

EVALUATION_DATA = [
    # ---------------- USSD -> triage_advisor ----------------
    {"id": "q01", "channel": "USSD", "feature": "triage_advisor",
     "question": "My 2-month-old baby feels hot and has a temperature of 38.5°C. What should I do?",
     "clinical_reference": "Any baby younger than 3 months with a temperature of 38°C or higher needs to be seen at a health facility immediately, even if the baby otherwise seems well. Keep breastfeeding on the way and do not give adult medicines. Go even faster if the baby is not feeding, very sleepy, having fits, or breathing fast."},
    {"id": "q02", "channel": "USSD", "feature": "triage_advisor",
     "question": "My father has had crushing chest pain for 20 minutes and is sweating. What should we do?",
     "clinical_reference": "Chest pain lasting more than a few minutes with sweating, breathlessness, or pain spreading to the arm, jaw or back may be a heart attack and is an emergency. Call 999 or 112, or get him to the nearest hospital immediately, and do not let him drive himself. Keep him resting while you wait, and if he is not allergic and the emergency operator or a health worker advises it, he can chew one adult aspirin."},
    {"id": "q03", "channel": "USSD", "feature": "triage_advisor",
     "question": "My mother's face suddenly drooped on one side and her speech is slurred. Can she rest and see a doctor tomorrow?",
     "clinical_reference": "No. Sudden face drooping, weakness of an arm or leg on one side, or slurred speech are warning signs of a stroke and she needs emergency care now. Call 999 or 112 or go to the nearest hospital immediately and note the time the symptoms started, because some stroke treatments only work within a few hours. Do not give her food, drink or medicines by mouth until she has been assessed."},
    {"id": "q04", "channel": "USSD", "feature": "triage_advisor",
     "question": "I am 7 months pregnant and have a severe headache and blurred vision. Is this normal?",
     "clinical_reference": "No. A severe headache with blurred vision in late pregnancy can be a sign of pre-eclampsia, which is dangerous for both mother and baby. Go to a health facility with maternity services immediately to have your blood pressure and urine checked. Also go immediately for vaginal bleeding, fits, severe abdominal pain, fever, leaking fluid, or if the baby is moving less than usual."},
    {"id": "q05", "channel": "USSD", "feature": "triage_advisor",
     "question": "My 3-year-old has had watery diarrhoea since yesterday. How do I care for him at home?",
     "clinical_reference": "Give oral rehydration solution (ORS) after every loose stool and keep giving food and fluids, including breast milk. Give zinc once daily for 10 to 14 days as directed by a health worker or the packet. Take him to a health facility immediately if he cannot drink, vomits everything, is very sleepy, has sunken eyes, has blood in the stool, or the diarrhoea lasts 14 days or more."},

    # ---------------- Mobile App -> medication_assistant ----------------
    {"id": "q06", "channel": "Mobile App", "feature": "medication_assistant",
     "question": "I was prescribed amoxicillin for 7 days but I feel better after 3 days. Can I stop?",
     "clinical_reference": "No. Finish the whole course exactly as prescribed even if you feel better, because stopping early can let the infection return and encourages antibiotic resistance. Do not save leftover tablets or share them with others. Stop taking it and seek urgent care if you develop a rash, swelling of the face or lips, or difficulty breathing, as these can be signs of an allergic reaction."},
    {"id": "q07", "channel": "Mobile App", "feature": "medication_assistant",
     "question": "What is the maximum amount of paracetamol an adult can take in a day?",
     "clinical_reference": "For a healthy adult the usual dose is 500 mg to 1 g every 4 to 6 hours, with no more than 4 g (eight 500 mg tablets) in 24 hours. Check the labels of cold and flu remedies, because many also contain paracetamol and the doses add up. People with liver disease, low body weight or heavy alcohol use should ask a pharmacist or doctor for a lower limit, and anyone who has taken more than the maximum should seek medical help immediately even if they feel well."},
    {"id": "q08", "channel": "Mobile App", "feature": "medication_assistant",
     "question": "I forgot my evening dose of Coartem for malaria. What should I do?",
     "clinical_reference": "Take the missed dose as soon as you remember and then continue the remaining doses at the usual times, but never take two doses at once to make up. Take each dose with food or milk containing fat, which helps the medicine absorb, and complete all six doses over three days. If you vomit within one hour of a dose, repeat that dose, and return to the clinic if the fever continues or you feel worse."},
    {"id": "q09", "channel": "Mobile App", "feature": "medication_assistant",
     "question": "Since starting metformin I have stomach upset and diarrhoea. Should I stop taking it?",
     "clinical_reference": "Do not stop metformin without speaking to your clinician. Stomach upset and diarrhoea are common when starting and usually improve over a few weeks; taking it with or just after meals helps, and your clinician may lower the dose or switch to an extended-release tablet. Seek urgent care for severe vomiting, severe abdominal pain, fast or difficult breathing or unusual drowsiness, which can be signs of a rare but serious side effect called lactic acidosis."},
    {"id": "q10", "channel": "Mobile App", "feature": "medication_assistant",
     "question": "I use insulin and I am shaking, sweating and confused. What should I do right now?",
     "clinical_reference": "These are signs of low blood sugar (hypoglycaemia). Immediately take 15 to 20 grams of fast-acting sugar, such as half a glass of fruit juice or regular soda or 3 to 4 glucose tablets, then recheck your blood sugar after 15 minutes and repeat if it is still below 4 mmol/L. Once it recovers, eat a snack or meal containing starch; if the person becomes unconscious or cannot swallow, give nothing by mouth and call 999 or 112."},

    # ---------------- Web Portal -> clinical_faq ----------------
    {"id": "q11", "channel": "Web Portal", "feature": "clinical_faq",
     "question": "How should I prepare for a fasting blood sugar test?",
     "clinical_reference": "Do not eat or drink anything except plain water for at least 8 hours before the test, so a morning appointment is usually easiest. Keep taking your usual medicines unless your clinician says otherwise, but ask in advance about diabetes medicines or insulin, which may need adjusting to avoid low blood sugar. Avoid heavy exercise, smoking and alcohol before the test, and bring a list of your current medicines."},
    {"id": "q12", "channel": "Web Portal", "feature": "clinical_faq",
     "question": "What blood pressure reading means I have high blood pressure, and what can I do about it?",
     "clinical_reference": "High blood pressure (hypertension) is usually diagnosed when clinic readings are 140/90 mmHg or higher on at least two separate occasions; one high reading alone is not enough. Eating less salt (under 5 g, about one teaspoon a day), at least 150 minutes of physical activity a week, limiting alcohol, stopping smoking and keeping a healthy weight all help, and many people also need daily medicine. A reading of 180/120 mmHg or higher with chest pain, severe headache, confusion or weakness is an emergency."},
    {"id": "q13", "channel": "Web Portal", "feature": "clinical_faq",
     "question": "Which vaccines should my baby get in the first year in Kenya?",
     "clinical_reference": "Under Kenya's routine schedule, babies receive BCG and oral polio at birth; pentavalent, pneumococcal and oral polio vaccines at 6, 10 and 14 weeks; rotavirus vaccine at 6 and 10 weeks; and injectable polio at 14 weeks. Measles-rubella vaccine is given at 9 months and again at 18 months, with yellow fever at 9 months in at-risk counties. Bring the Mother and Child Health booklet to every visit, and if a dose is missed the clinic will help the baby catch up rather than restarting."},
    {"id": "q14", "channel": "Web Portal", "feature": "clinical_faq",
     "question": "I have been coughing for three weeks and sweating at night. Could it be TB, and is testing expensive?",
     "clinical_reference": "A cough lasting two weeks or more, especially with fever, night sweats or weight loss, can be a sign of tuberculosis (TB) and should be tested. Visit any public health facility, where TB testing (usually a sputum test such as GeneXpert) and treatment are free in Kenya. TB is curable with about six months of daily medicine that must be completed in full, and the people you live with should also be screened."},
    {"id": "q15", "channel": "Web Portal", "feature": "clinical_faq",
     "question": "A neighbour's dog bit my son and broke the skin. What should we do?",
     "clinical_reference": "Wash the wound immediately with soap and running water for about 15 minutes, then go to a health facility the same day, even if the wound looks small. A health worker will assess the need for rabies vaccination (post-exposure prophylaxis), which must start as soon as possible because rabies is almost always fatal once symptoms appear, and may also give a tetanus vaccine or antibiotics. If possible, find out whether the dog is vaccinated and report it so it can be observed for 10 days."},
]