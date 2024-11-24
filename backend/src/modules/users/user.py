from flask import request, jsonify
import bcrypt
import os
from __main__ import app, db
from sqlalchemy.exc import IntegrityError

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
        data = request.get_json()

        # Validate input
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Username, email, and password are required'}), 400

        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=hashed_password,
            profilePicture=data.get('profilePicture'),
            school=data.get('school'),
            major=data.get('major')
        )

        db.session.add(new_user)
        db.session.commit()


        # create a directory for the user
        # can be used to store the profile picture and conversation history
        os.makedirs(f"files/{new_user.id}/.lessnotes")

        return jsonify({
            'message': 'User created successfully',
            'user': new_user.to_dict()
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Username or email already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500
    
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

@app.route('/files/<int:user_id>', methods=['GET'])
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