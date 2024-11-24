
from __main__ import app, db
from utils.hash import compute_hash
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String(120), nullable=False)
    path = db.Column(db.String(120), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    processed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'hash': self.hash,
            'path': self.path,
            'userId': self.userId,
            'processed': self.processed
        }
    
    def __str__(self):
        return f"File(id={self.id}, hash={self.hash}, path={self.path}, userId={self.userId}, processed={self.processed})"

    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        if other == None:
            return False
        if not isinstance(other, File):
            return False
        return self.hash == other.hash
    
def create_file(file_path, user_id):
    try:
        # Validate input
        if not file_path or not user_id:
            raise RuntimeError('Path, and userId are required')

        file_hash = compute_hash(file_path)

        # Check if a file with the same hash and userId exists
        existing_file = File.query.filter_by(hash=file_hash, userId=user_id).first()

        if existing_file:
            # Update the existing file's attributes
            existing_file.processed = False  # Reset 'processed' status if needed
            db.session.commit()
            return existing_file  # Return the updated file object
        else:
            # Create and add a new file
            new_file = File(
                hash=file_hash,
                path=file_path,
                userId=user_id
            )
            db.session.add(new_file)
            db.session.commit()
            return new_file  # Return the newly created file object
    
    except IntegrityError as e:
        db.session.rollback()
        raise RuntimeError(f"Integrity error occurred: {e}")
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"An unexpected error occurred: {e}")

# Get files by userid
def get_files_by_user_id(userId):
    try:
        files = File.query.filter_by(userId=userId).all()
        return [file.to_dict() for file in files]
    except IntegrityError as e:
        db.session.rollback()
        raise RuntimeError(f"Integrity error occurred: {e}")
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"An unexpected error occurred: {e}")
    