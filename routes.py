from flask import request, redirect, render_template, jsonify
from app import app
import os
import io
from io import StringIO
from models import *
import face_recognition
import numpy as np
from PIL import Image
import pickle
import json
from mask_detection import give_predictions
from werkzeug.utils import secure_filename
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# def allowed_file(register_image):
# 	return '.' in register_image and register_image.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET','VIEW'])
def home():
    if request.method=='VIEW':
        return render_template('index.html')
    else:
        return jsonify({'message to the new User': 'Welcome to M-GAP, Go on to the registration page to begin your journey with us.'})


@app.route('/register', methods=['GET'])
def register():
    return jsonify({"API for Registration Page": "Fill in the details"})
    try:
        return render_template('register.html')
    except:
        return None


@app.route('/verify')
def verify():
    return render_template('verify.html')


@app.route('/result')
def result():
    return render_template('final.html')


@app.route('/send_details', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        # posted_data = request.get_json()

        register_image = str(Image.open(request.files['register_image'], "r"))
        data = json.load(request.files['data'])
        name = data['name']
        email = data['email']
        gender = data['gender']
        age = data['age']
        contact = data['contact']
        face_encoding = data['face_encoding']
        # # name = request.form['demo-name']
        # # email = request.form['demo-email']
        # # gender = request.form['demo-gender']
        # # age = int(request.form['demo-age'])
        # # contact = request.form['demo-contact']
        # # face_encoding = np.array(json.loads(request.form['encoding']))  #TODO
        # image = request.files['image']
        # register_image = secure_filename(image.register_image)

        # register_image = request.form['register_image']
        new_User = User(name=name, email=email, gender=gender, age=age, contact=contact,
                        register_image=register_image, face_encoding=face_encoding)  # , face_encoding=pickle.dumps(face_encoding))register_image=register_image
        try:
            db.session.add(new_User)
            db.session.commit()
            # return redirect('/register')
            # return jsonify(username=g.user.name,
            #        email=g.user.email,
            #        id=g.user.id)
            return jsonify({'message': 'User has registered with all the details'})
        except Exception as e:
            print(e)
            return 'There was an issue adding the details of the User to your database'
    else:
        # users = User.query.order_by(User.id).all()
        # return render_template('register.html', users=users)
        return jsonify({'name': 'Enter name',
                        'age': 'Enter Age',
                        'contact': 'Enter contact',
                        'email': 'Enter email',
                        'register_image': 'Upload a high resolution picture of your face so that M-GAP can carry out Facial Recognition on it'})


@app.route('/send_email', methods=['POST'])
def sendmail():
    if request.method == 'POST':
        posted_data = request.get_json()
        user_name = posted_data['user_name']
        user_email = posted_data['user_email']
        message = Mail(
            from_email='maintaingap.safetytracker@gmail.com',
            to_emails=user_email,
            subject='You have been registered with M-GAP',
            html_content=f'Hi {user_name} !<br>Thank you for registering with us '

        )
        return jsonify({'response': 'The mail has been sent',
                        'message': 'Hi ' + user_name + '! Thank you for registering with us'})

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        return jsonify({'message': 'The mail has been sent to the user'})

        # print(response.body)
        # print(response.headers)
    except Exception as e:
        print(e)


@app.route('/verification_details', methods=['POST', 'PUT', 'PATCH', 'GET'])
def details():
    # temperature = float(request.form['demo-temp'])
    # try:
    #     user_id = int(request.form['user-id'])
    # except:
    #     user_id = None
    if request.method == 'POST':
        temperature = request.args.get('temperature')
        user_id = request.args.get('user_id')
        mask_detected = request.args.get('mask_detected', int)

    # mask_detected = bool(int(request.form['mask-detected']))
        if user_id:
            new_Scan = Scan(mask_detected, temperature, user_id)
            try:
                db.session.add(new_Scan)
                db.session.commit()

                if(new_Scan.temperature < 99.0 and new_Scan.mask_detected == 1):
                    return render_template('verified.html', person=new_Scan.person)
                elif(new_Scan.temperature < 99.0 and new_Scan.mask_detected == 0):
                    return render_template('notmask.html', person=new_Scan.person)
                elif(new_Scan.temperature > 99.0 and new_Scan.mask_detected == 1):
                    return render_template('nottemp.html', person=new_Scan.person)
                else:
                    return render_template('failed.html', person=new_Scan.person)
            except Exception as e:
                print(e)
                return 'There was an issue adding the details of the User to your database'

        else:
            if(temperature < 99.0 and mask_detected == 1):
                return render_template('noface.html')
            elif (temperature > 99.0 and mask_detected == 1):
                return render_template('notemp.html')
            elif (temperature < 99.0 and mask_detected == 0):
                return render_template('nomask.html')
            else:
                return render_template('notverified.html')

    if request.method == 'PATCH':
        temperature = request.args.get('temperature')
        user_id = request.args.get('user_id')
        mask_detected = request.args.get('mask_detected', int)
        if user_id:
            new_Scan = Scan(mask_detected, temperature, user_id)
            try:
                db.session.add(new_Scan)
                db.session.commit()

                if(new_Scan.temperature < 99.0 and new_Scan.mask_detected == 1):
                    return render_template('verified.html', person=new_Scan.person)
                elif(new_Scan.temperature < 99.0 and new_Scan.mask_detected == 0):
                    return render_template('notmask.html', person=new_Scan.person)
                elif(new_Scan.temperature > 99.0 and new_Scan.mask_detected == 1):
                    return render_template('nottemp.html', person=new_Scan.person)
                else:
                    return render_template('failed.html', person=new_Scan.person)
            except Exception as e:
                print(e)
                return 'There was an issue adding the details of the User to your database'


@app.route('/register-image', methods=['POST', 'GET'])
def register_face():
    if request.method == 'POST':
        image = request.files['webcam']
        image = np.array(Image.open(image))
        try:
            face_locations = face_recognition.face_locations(image)
            top, right, bottom, left = face_locations[0]
            face_image = image[top:bottom, left:right]
            face_encoding = face_recognition.face_encodings(face_image)
            dump = pickle.dumps(face_encoding[0])
            return jsonify(face_encoding[0].tolist())
        except:
            return jsonify([])
    if request.method == 'GET':
        image = request.files['webcam']
        image = np.array(Image.open(image))
        try:
            face_locations = face_recognition.face_locations(image)
            top, right, bottom, left = face_locations[0]
            face_image = image[top:bottom, left:right]
            face_encoding = face_recognition.face_encodings(face_image)
            dump = pickle.dumps(face_encoding[0])

            return jsonify({"Image encoding": face_encoding[0].tolist()})
        except:
            return jsonify({"Image encoding": "CREATED"})


@app.route('/verify-face', methods=['POST'])
def verify_face():
    image = request.files['webcam']
    image = np.array(Image.open(image))
    try:
        face_locations = face_recognition.face_locations(image)
        top, right, bottom, left = face_locations[0]
        face_image = image[top:bottom, left:right]
        face_encoding = face_recognition.face_encodings(face_image)
        all_users = User.query.all()
        face_encodings = [pickle.loads(user.face_encoding)
                          for user in all_users]
        user_ids = [user.id for user in all_users]
        results = face_recognition.face_distance(
            face_encodings, face_encoding[0])
        best_match_index = np.argmin(results)
        if results[best_match_index] <= 0.35:
            verified_user_id = user_ids[best_match_index]
            print('Person Verified!', 'User ID:', verified_user_id)
        else:
            print(results[best_match_index])
            raise Exception
        return jsonify({'user_id': verified_user_id})
    except:
        print('No face detected!', flush=True)
        # return jsonify({'user_id': None})
        return jsonify({'Face Detected': 'Yes'})


@app.route('/verify-mask', methods=['POST'])
def verify_mask():
    image = request.files['webcam']
    mask_on = give_predictions(image)
    return jsonify({'Mask Detection': int(mask_on)})
