# app/auth_utils.py
from passlib.context import CryptContext
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_pw(p:str)->str: return pwd.hash(p)
def verify_pw(p:str,h:str)->bool: return pwd.verify(p,h)
