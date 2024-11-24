from utils.create_directory_structure import create_directory_structure
from flask import json, request, jsonify, send_from_directory
import bcrypt
import os
from __main__ import app, db
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'files')

class User(db.Model):  # Make User inherit from db.Model for SQLAlchemy compatibility
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    profilePicture = db.Column(db.String(200), nullable=True)
    school = db.Column(db.String(120), nullable=True)
    major = db.Column(db.String(120), nullable=True)

    def to_dict(self):
        return {
            'password': self.password,
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'profilePicture': self.profilePicture,
            'school': self.school,
            'major': self.major
        }
    
    def __str__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email}, profilePicture={self.profilePicture}, school={self.school}, major={self.major})"

    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        if other == None:
            return False
        if not isinstance(other, User):
            return False
        return self.id == other.id
    

def get_user_by_id_controller(user_id):
    """
    Get user details by ID.
    """
    try:
        user = User.query.get(user_id)
        if user:
            return user
        else:
            return None
    except Exception as e:
        return None

@app.route('/signup', methods=['POST'])
def create_user():
    try:
        data = request.form
        profile_picture = request.files.get('profilePicture')
        
        # Validate input
        if not data['username'] or not data['email'] or not data['password']:
            print("Error")
            return jsonify({'error': 'Username, email, and password are required'}), 400

        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')        
        # Create new user first to get the ID
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=hashed_password,
            profilePicture=None,  # We'll update this after saving the file
            school=data['school'],
            major=data['major']
        )
        db.session.add(new_user)
        db.session.commit()

        # Handle profile picture upload
        if profile_picture:
            # Create user's profile picture directory
            user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(new_user.id), 'profile_picture')
            os.makedirs(user_dir, exist_ok=True)
            
            # Secure the filename
            filename = secure_filename(profile_picture.filename)
            
            # Save the file
            profile_picture_path = os.path.join(str(new_user.id), 'profile_picture', filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_picture_path)
            profile_picture.save(full_path)
            
            # Update the user's profile picture path in the database
            new_user.profilePicture = profile_picture_path
            db.session.commit()

        # Create .lessnotes directory
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], str(new_user.id), '.lessnotes'), exist_ok=True)

        return jsonify({
            'message': 'User created successfully',
            'user': new_user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@app.route('/images/<path:filename>', methods=['GET'])
def get_image(filename):
    try:
        # Log the requested filename for debugging
        print(f"Requested filename: {filename}")
        
        # The filename already contains the full path like "2/profile_picture/image.jpg"
        # Split it to get the directory and actual filename
        file_path = os.path.normpath(filename)
        
        # Prevent directory traversal
        if file_path.startswith('..') or file_path.startswith('/'):
            return "Invalid path", 400
            
        # Get the full directory path
        directory = os.path.join(app.config['UPLOAD_FOLDER'], os.path.dirname(file_path))
        filename = os.path.basename(file_path)
        
        # Log the full path for debugging
        print(f"Looking for file in: {directory}")
        print(f"Filename: {filename}")
        
        # Check if file exists
        full_path = os.path.join(directory, filename)
        if not os.path.exists(full_path):
            print(f"File not found at: {full_path}")
            return f"File not found: {filename}", 404
            
        return send_from_directory(directory, filename)
    except Exception as e:
        print(f"Error serving image: {str(e)}")
        return f"Error: {str(e)}", 500
   
    
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('emailOrUsername')).first()
    if not user or user == None:
        user = User.query.filter_by(username=data.get('emailOrUsername')).first()

    if user and bcrypt.checkpw(data.get('password').encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """
    Get user details by ID.
    """
    try:
        user = User.query.get(user_id)
        if user:
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({'error': f'User with ID {user_id} not found'}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500
    
@app.route('/users/email/<string:email>', methods=['GET'])
def get_user_by_email(email):
    """
    Get user details by email.
    """
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({'error': f'User with email {email} not found'}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500
    
@app.route('/users/username/<string:username>', methods=['GET'])
def get_user_by_username(username):
    """
    Get user details by username.
    """
    try:
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({'error': f'User with username {username} not found'}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500
    
@app.route('/users', methods=['GET'])
def get_users():
    """
    Get all users in the database.
    """
    try:
        users = User.query.all()
        if users:
            return jsonify([user.to_dict() for user in users]), 200
        else:
            return jsonify({'message': 'No users found'}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500
    
# Update user details by email and use a request body to reseive the new details
@app.route('/users/<string:email>', methods=['PUT'])
def update_user_by_email(email):
    try:
        data = request.get_json()
        user = User.query.filter_by(email=email).first()
        if user:
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.password = data.get('password', user.password)
            user.profilePicture = data.get('profilePicture', user.profilePicture)
            user.school = data.get('school', user.school)
            user.major = data.get('major', user.major)
            db.session.commit()
            return jsonify({'message': 'User updated successfully', 'user': user.to_dict()}), 200
        else:
            return jsonify({'error': f'User with email {email} not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500

@app.route('/users/<int:user_id>/files', methods=['GET'])
def get_user_files(user_id):
    """
    Returns the folder containing files for the given user ID in a recursive structure.
    """
    try:
        # Check if the user exists (assume User is a valid model with query)
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': f'User with ID {user_id} not found'}), 404

        # Define the folder path
        folder_path = f"files/{user_id}/data"
        
        # Check if the directory exists
        if not os.path.exists(folder_path):
            return jsonify({'error': f'No folder found for user with ID {user_id}'}), 404

        # Recursive function to build the directory structure
        def build_directory_structure(path):
            if os.path.basename(path)[0] == '.':
                return None
            structure = {
                "name": os.path.basename(path),
                "files": [{"name": f} for f in os.listdir(path) if (os.path.isfile(os.path.join(path, f)) and f[0] != '.')],
                "subdirectories": []
            }
            for subdir in os.listdir(path):
                full_subdir_path = os.path.join(path, subdir)
                if os.path.isdir(full_subdir_path):
                    structure["subdirectories"].append(build_directory_structure(full_subdir_path))
            return structure

        # Build the directory structure starting from the root folder
        directory_structure = build_directory_structure(folder_path)

        return jsonify(directory_structure), 200

    except Exception as e:
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500
    
# @app.route('/users/<int:user_id>/uploadFiles', methods=['POST'])
def uploadFiles(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': f'User not found'}), 404

        data = request.get_json()
        
        # base_path = os.path.normpath(os.path.join('./files', str(user_id)))

        # if os.path.exists(os.path.join(base_path, 'data')):
        #     shutil.rmtree(os.path.join(base_path, 'data'))  # Recursively delete the folder and its contents

        # create_directory_structure(base_path, data)

        return jsonify({'message': 'files uploaded'}), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500

@app.route('/users/<user_id>/uploadFiles', methods=['POST'])
def upload_files(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': f'User not found'}), 404
        
        # directory_metadata = request.form.get('directoryMetadata')
        files = request.files.getlist('files')
        base_path = os.path.normpath(os.path.join('./files', str(user_id), 'data'))
        
        create_directory_structure(base_path, files)

        return jsonify({"message": "Files uploaded successfully"}), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500