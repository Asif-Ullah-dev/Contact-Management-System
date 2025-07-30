from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv
import io

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(50), nullable=True)        #  NEW
    priority = db.Column(db.String(20), nullable=True)     #  NEW 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  

@app.route('/')
def index():
    contacts = Contact.query.all()
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['POST'])
def add_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    title = request.form.get('title')
    priority = request.form.get('priority')

    new_contact = Contact(name=name, email=email, phone=phone, title=title, priority=priority)
    db.session.add(new_contact)
    db.session.commit()
    flash("✅ Contact added successfully!", "success")
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_contact(id):
    contact = Contact.query.get(id)
    db.session.delete(contact)
    db.session.commit()
    flash("🗑️ Contact deleted.", "success")
    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_contact(id):
    contact = Contact.query.get(id)
    if request.method == 'POST':
        contact.name = request.form.get('name')
        contact.email = request.form.get('email')
        contact.phone = request.form.get('phone')
        contact.title = request.form.get('title')
        contact.priority = request.form.get('priority')
        db.session.commit()
        flash("✏️ Contact updated!", "success")
        return redirect(url_for('index'))
    return render_template('update.html', contact=contact)

@app.route('/export_csv')
def export_csv():
    contacts = Contact.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Title', 'Priority'])
    for contact in contacts:
        writer.writerow([contact.id, contact.name, contact.email, contact.phone, contact.title, contact.priority])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name="contacts.csv")

@app.route('/deals')
def deals():
    return render_template('deals.html')

@app.route('/leads')
def leads():
    return render_template('leads.html')

@app.route('/accounts')
def accounts():
    return render_template('accounts.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/import_csv', methods=['POST'])
def import_csv():
    if 'csv_file' not in request.files:
        flash('❌ No file uploaded!', 'error')
        return redirect(url_for('index'))

    file = request.files['csv_file']
    if file.filename == '':
        flash('❌ No selected file!', 'error')
        return redirect(url_for('index'))

    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    reader = csv.DictReader(stream)

    imported = 0
    for row in reader:
        if 'name' in row and 'email' in row and 'phone' in row:
            contact = Contact(
                name=row['name'],
                email=row['email'],
                phone=row['phone'],
                title=row.get('title', ''),
                priority=row.get('priority', '')
            )
            db.session.add(contact)
            imported += 1

    db.session.commit()
    flash(f"✅ Imported {imported} contacts from CSV!", "success")
    return redirect(url_for('index'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ensures table and DB are created
    app.run(debug=True)
