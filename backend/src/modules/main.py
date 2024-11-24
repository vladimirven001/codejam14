from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lessnotes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

global db
db = SQLAlchemy(app)

import users.user 
import rag.rag
import conversations.conversation
import conversations.message
import llm.llm

# Initialize the database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=8000, debug=True)