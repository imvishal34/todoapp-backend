DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'password'
DB_NAME = 'todo-app'
import secrets

JWT_SECRET_KEY = secrets.token_urlsafe(32)
