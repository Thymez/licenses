from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import random
import string
from datetime import datetime, timedelta

# Initialize Firebase
cred = credentials.Certificate('thymez-tick-firebase-adminsdk-wppmw-ea800a99ce.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key

# Function to generate License ID
def generate_license_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

# Route for the homepage with form to create a new license
@app.route('/')
def index():
    return render_template('index.html')

# Route to create a new license
@app.route('/create_license', methods=['POST'])
def create_license():
    user_name = request.form.get('user_name')
    days_valid = int(request.form.get('days_valid'))
    
    if user_name and days_valid:
        new_license_id = generate_license_id()
        expiration_date = datetime.now() + timedelta(days=days_valid)
        
        # License data
        new_license_data = {
            'user': user_name,
            'lastLogin': datetime.now().isoformat(),
            'loginCount': 1,
            'expirationDate': expiration_date.strftime("%Y-%m-%d")
        }
        
        db.collection('licenses').document(new_license_id).set(new_license_data)
        flash(f'License created for user "{user_name}" with License ID: {new_license_id}. Expires on: {expiration_date.strftime("%Y-%m-%d")}', 'success')
    
    return redirect(url_for('index'))

# Route to display all licenses
@app.route('/licenses')
def display_licenses():
    licenses_ref = db.collection('licenses')
    licenses = [doc.to_dict() | {"id": doc.id} for doc in licenses_ref.stream()]
    return render_template('licenses.html', licenses=licenses)

# Route to delete a license
@app.route('/delete_license/<license_id>', methods=['POST'])
def delete_license(license_id):
    db.collection('licenses').document(license_id).delete()
    flash(f'License {license_id} deleted successfully!', 'success')
    return redirect(url_for('display_licenses'))

# Route to edit a license
@app.route('/edit_license/<license_id>', methods=['POST'])
def edit_license(license_id):
    new_user_name = request.form.get('new_user_name')
    if new_user_name:
        license_ref = db.collection('licenses').document(license_id)
        license_ref.update({
            'user': new_user_name,
            'lastLogin': datetime.now().isoformat()
        })
        flash("License updated successfully!", 'success')
    return redirect(url_for('display_licenses'))

if __name__ == '__main__':
    app.run(debug=True)
