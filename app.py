#!/usr/bin/env python3
"""
CodeAlpha Task 3: Secure Code Review
Author: Hailemariam Zeleke
Description: A deliberately vulnerable Flask application for security review.
"""

from flask import Flask, request
import sqlite3
import pickle
import base64
import os

app = Flask(__name__)

# ==================== VULNERABILITY 1: HARDCODED CREDENTIALS ====================
ADMIN_PASSWORD = "admin123"  # <-- NEVER hardcode passwords!

# ==================== VULNERABILITY 2: SQL INJECTION ====================
def get_user(username):
    """Vulnerable to SQL Injection - DO NOT USE IN PRODUCTION"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # ❌ This is vulnerable: user input is concatenated directly into the query
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return user

# ==================== VULNERABILITY 3: CROSS-SITE SCRIPTING (XSS) ====================
@app.route('/greet')
def greet():
    """Vulnerable to XSS - user input is echoed without sanitization"""
    name = request.args.get('name', 'Guest')
    # ❌ This is vulnerable: name is directly inserted into HTML
    return f"<h1>Hello, {name}</h1>"

# ==================== VULNERABILITY 4: INSECURE DESERIALIZATION ====================
@app.route('/load')
def load_data():
    """Vulnerable to Insecure Deserialization using pickle"""
    data = request.args.get('data')
    if data:
        try:
            decoded = base64.b64decode(data)
            # ❌ This is vulnerable: pickle.loads can execute arbitrary code
            obj = pickle.loads(decoded)
            return f"Loaded: {obj}"
        except:
            return "Error loading data"
    return "No data"

# ==================== VULNERABILITY 5: DEBUG MODE ENABLED ====================
if __name__ == "__main__":
    # ❌ Debug mode exposes sensitive errors to users
    app.run(debug=True, host='0.0.0.0', port=5000)