from flask import jsonify
from __main__ import app, db
from users.user import get_user_by_id
from datetime import datetime

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.userId,
            'time': self.time.isoformat()
        }
    
def get_conversation_by_id(conversation_id):
    try:
        conversation = Conversation.query.get(conversation_id)
        return conversation
    except Exception as e:
        return None
    
@app.route('/users/<int:user_id>/conversations', methods=['POST'])
def create_conversation(user_id):
    try:
        # Validate input
        if not user_id:
            return jsonify({'error': 'UserId is required'})
        
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        new_conversation = Conversation(
            userId=user_id,
            time=datetime.now()
        )
        db.session.add(new_conversation)
        db.session.commit()
        return jsonify({
            'message': 'Conversation created successfully',
            'conversation': new_conversation.to_dict()
            }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while creating a conversation', 'details': str(e)}), 500
    
@app.route('/users/<int:user_id>/conversations', methods=['GET'])
def get_conversations_by_user_id(user_id):
    try:
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User does with id '+ user_id +' not exist'}), 404
        conversations = Conversation.query.filter_by(userId=user_id).all()
        if not conversations:
            return jsonify({'error': 'No conversations found'}), 404
        return jsonify({
            'conversations': [conversation.to_dict() for conversation in conversations]
        }), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred while retrieving conversations', 'details': str(e)}), 500