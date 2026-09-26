#!/usr/bin/env python3
"""
CodeAlpha Task 3: Secure Code Review (Remediated Version)
Author: Hailemariam Zeleke
Description: Secure version of app.py. Each fix is numbered to match the
vulnerability it remediates in the original application.
"""

import base64
import binascii
import json
import os
import sqlite3

from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

# ==================== FIX 1: SECRETS FROM ENVIRONMENT VARIABLES ====================
# ✅ Credentials are read from the environment at runtime, never stored in code.
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


# ==================== FIX 2: PARAMETERIZED QUERIES (SQL INJECTION) ====================
def get_user(username):
    """Look up a user with a parameterized query."""
    conn = sqlite3.connect("users.db")
    try:
        cursor = conn.cursor()
        # ✅ The driver passes username as data; it can never change the SQL statement.
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()
    finally:
        conn.close()


# ==================== FIX 3: OUTPUT ESCAPING (XSS) ====================
@app.route("/greet")
def greet():
    """Greet the user, escaping their input before it reaches the HTML."""
    name = request.args.get("name", "Guest")
    # ✅ escape() converts <, >, &, " and ' into HTML entities.
    return f"<h1>Hello, {escape(name)}</h1>"


# ==================== FIX 4: SAFE DESERIALIZATION ====================
@app.route("/load")
def load_data():
    """Load user-supplied data using JSON instead of pickle."""
    data = request.args.get("data")
    if not data:
        return "No data"
    try:
        # ✅ JSON can only describe data (strings, numbers, lists, objects), never code.
        obj = json.loads(base64.b64decode(data, validate=True))
    except (binascii.Error, ValueError):
        return "Error loading data", 400
    # ✅ The decoded value is escaped too, so it can't inject HTML.
    return f"Loaded: {escape(str(obj))}"


# ==================== FIX 5: DEBUG DISABLED, LOCAL BINDING ====================
if __name__ == "__main__":
    # ✅ Debug mode is off, and the server listens on localhost only.
    app.run(debug=False, host="127.0.0.1", port=5000)
