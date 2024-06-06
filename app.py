from flask import Flask, render_template, request
from flask_mail import Mail, Message
from pymongo import MongoClient

app = Flask(__name__)

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ''  # Change to your email
app.config['MAIL_PASSWORD'] = ' '    # Change to your email password

# MongoDB configuration
client = MongoClient('mongodb://localhost:27017/')
db = client['bloodDonationDB']
donors_collection = db['donors']
requests_collection = db['requests']

mail = Mail(app)

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/donate', methods=['GET'])
def donate_form():
    return render_template('donate.html')
@app.route('/donate', methods=['POST'])
def donate():
    if request.method == 'POST':
        data = request.form
        donors_collection.insert_one({
            'name': data['name'],
            'email': data['email'],
            'bloodGroup': data['bloodGroup'],
            'phno': data['phno']
        })
        message = 'Thank you for your donation!'
        message_type = 'success' 
    else:
        message = 'Method Not Allowed'
        message_type = 'error'
    return render_template('donate.html', message=message, message_type=message_type)
    
@app.route('/request', methods=['GET'])
def request_blood_form():
    return render_template('request_blood.html')

@app.route('/request', methods=['POST'])
def request_blood():
    if request.method == 'POST':
        data = request.form
        requests_collection.insert_one({
            'name': data['name'],
            'email': data['email'],
            'phno': data['phno'],
            'bloodGroup': data['bloodGroup']

        })
        
        matching_donors = list(donors_collection.find({'bloodGroup': data['bloodGroup']}))

        with app.app_context():
            for donor in matching_donors:
                msg = Message(subject='Blood Request', sender='mail id', recipients=[donor['email']])
                msg.body = f"Hello {donor['name']},\n\nThere is a blood request for {data['bloodGroup']} blood group.\n\nDetails of the requester:\nName: {data['name']}\nEmail: {data['email']}\nPhone Number: {data['phno']}\n\nThank you."
                mail.send(msg)

        return render_template('matching_donors.html', matching_donors=matching_donors)
    else:
        return 'Method Not Allowed', 405

if __name__ == '__main__':
    app.run(debug=True)
