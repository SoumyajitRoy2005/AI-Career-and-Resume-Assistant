
import sqlite3, hashlib, json, os
DB="nexora.db"
def conn():
    c=sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        email TEXT PRIMARY KEY, password TEXT NOT NULL, profile TEXT NOT NULL DEFAULT '{}')""")
    c.commit(); return c
def hp(s): return hashlib.sha256(s.encode()).hexdigest()
def create_user(email,password):
    c=conn()
    try:
        c.execute("INSERT INTO users(email,password,profile) VALUES(?,?,?)",(email.lower().strip(),hp(password),"{}")); c.commit(); return True,""
    except sqlite3.IntegrityError: return False,"An account with this email already exists."
    finally: c.close()
def login(email,password):
    c=conn(); row=c.execute("SELECT password,profile FROM users WHERE email=?",(email.lower().strip(),)).fetchone(); c.close()
    if row and row[0]==hp(password): return True,json.loads(row[1])
    return False,None
def save_profile(email,profile):
    c=conn(); c.execute("UPDATE users SET profile=? WHERE email=?",(json.dumps(profile),email.lower().strip())); c.commit(); c.close()
