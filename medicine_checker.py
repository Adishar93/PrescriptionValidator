import pandas as pd
from flask import Flask, request, jsonify

def initialize(symptoms, doctor_prescription):
    # Load the dataset
    csv_path = './medicine_dataset.csv'
    df = pd.read_csv(csv_path)

    # Convert all use and substitute columns to lowercase for case-insensitive comparison
    use_columns = ['use0', 'use1', 'use2', 'use3']
    substitute_columns = ['substitute0', 'substitute1', 'substitute2', 'substitute3']
    for col in use_columns + substitute_columns:
        df[col] = df[col].str.lower()

    # Create a set for all unique words in symptoms for efficient searching
    symptom_words = set(word for phrase in symptoms for word in phrase.split())

    # Find unique medications and substitutes that match the symptoms
    matches = set()
    for _, row in df.iterrows():
        # Check each use column for matches with any of the symptoms
        if any(symptom_word in row[use].split() for use in use_columns for symptom_word in symptom_words if pd.notnull(row[use])):
            # Add the medication name and substitutes to the set of matches
            matches.add(row['name'])
            matches.update(row[sub] for sub in substitute_columns if pd.notnull(row[sub]))

    # Create ai_prescription from the unique matches found
    ai_prescription = ', '.join(matches)

    # Convert doctor_prescription to a set for case-insensitive comparison
    doctor_prescription_set = set(med.lower() for med in doctor_prescription)

    # Compare doctor_prescription with ai_prescription
    if doctor_prescription_set & set(ai_prescription.split(', ')):
        return True
    else:
        return False






app = Flask(__name__)

@app.route('/verify-prescription', methods=['POST'])
def verify_prescription_route():
    data = request.get_json()

    if 'transcript' in data and 'prescription' in data:
        transcript = data['transcript']
        prescription = data['prescription']
        
         # Define the symptoms to compare
        symptoms = [transcript]
        # Define the doctor's prescription
        doctor_prescription = prescription.split(", ")
        approved = initialize(symptoms, doctor_prescription)

        return jsonify({'approved': approved})
    else:
        return jsonify({'error': 'Missing transcript or prescription in the request'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)