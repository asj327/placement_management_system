from flask import Flask
from db import init_db
from student_routes import student_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# Register student blueprint
app.register_blueprint(student_bp, url_prefix='/student')

if __name__ == '__main__':
    app.run(debug=True)
