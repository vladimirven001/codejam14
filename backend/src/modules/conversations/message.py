from flask import jsonify, request
from __main__ import app, db
from conversations.conversation import get_conversation_by_id

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(10000), nullable=False)
    conversationId = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    isHuman = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'conversationId': self.conversationId,
            'isHuman': self.isHuman
        }
    
def get_messages_by_conversation_id(conversation_id):
    try:
        messages = Message.query.filter_by(conversationId=conversation_id).all()
        return sorted(messages, key=lambda message: message.id)
    except Exception as e:
        return None
    
@app.route('/conversation/<int:conversation_id>/messages', methods=['GET'])
def get_messages_by_conversation_id_frontend(conversation_id):
    try:
        messages = get_messages_by_conversation_id(conversation_id)
        return jsonify({
            'messages': [message.to_dict() for message in messages]
            }), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred while getting messages', 'details': str(e)}), 500
    
@app.route('/conversation/<int:conversation_id>/messages', methods=['POST'])
def create_message(conversation_id):
    try:
        text = request.json.get('text')
        is_human = request.json.get('isHuman')
        # Validate input
        if not text or not conversation_id or is_human is None:
            return jsonify({'error': 'Text, conversationId, and isHuman are required'}), 400

        conversation = get_conversation_by_id(conversation_id)
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404

        new_message = Message(
            text=text,
            conversationId=conversation_id,
            isHuman=is_human
        )
        db.session.add(new_message)
        db.session.commit()
        return jsonify({
            'message': 'Message created successfully',
            'createdMessage': new_message.to_dict()
            }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while creating a message', 'details': str(e)}), 500