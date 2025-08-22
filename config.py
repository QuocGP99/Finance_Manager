from dotenv import load_dotenv
import os

load_dotenv()  # Tải các biến môi trường từ file .env

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///finance.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev")
SQLALCHEMY_TRACK_MODIFICATIONS = False
