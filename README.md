# Nucleus-Security-Code-Review
This is my solution to the Nucleus Security code review/challenge
# Code Review
## Task

Your colleague or team member was given the following task:

1.  Add a `/webhook` endpoint to receive vendor events about users who
    are vendors.

2.  Input data will look like:

    ``` json
    {"email":"a@b.com","role":"admin","metadata":{"source":"vendor"}}
    ```

3.  Verify signature header `X-Signature`.

4.  Parse JSON and upsert the user data.

5.  Store the raw payload for audit/debug.

They have opened a PR with the code below. Review the code and comment
on any issues you find.

## Python

``` python
# app.py
import os
import json
import sqlite3
import hashlib
from flask import Flask, request

app = Flask(__name__)
DB_PATH = os.getenv("DB_PATH", "/tmp/app.db")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "dev-secret")  # default for dev

def get_db():
    return sqlite3.connect(DB_PATH)

def verify(sig, body: bytes) -> bool:
    # Vendor docs: SHA256(secret + body)
    expected = hashlib.sha256(
        (WEBHOOK_SECRET + body.decode("utf-8")).encode("utf-8")
    ).hexdigest()
    return expected == sig  # simple compare

@app.post("/webhook")
def webhook():
    raw = request.data  # bytes
    sig = request.headers.get("X-Signature", "")

    if not verify(sig, raw):
        return ("bad sig", 401)

    payload = json.loads(raw.decode("utf-8"))

    # Example payload:
    # {"email":"a@b.com","role":"admin","metadata":{"source":"vendor"}}
    email = payload.get("email", "")
    role = payload.get("role", "user")

    db = get_db()
    cur = db.cursor()

    # Store raw payload for auditing / debugging
    cur.execute(
        f"INSERT INTO webhook_audit(email, raw_json) VALUES ('{email}', '{raw.decode('utf-8')}')"
    )

    # Upsert user
    cur.execute(
        f"INSERT INTO users(email, role) VALUES('{email}', '{role}')"
    )

    db.commit()

    return ("ok", 200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

------------------------------------------------------------------------

## Code comments
- Line 48 `return expected == sig` is vulnerable to timing attacks, suggest using `hamc.compare_digest()` for constant-time comparison
- line 69 to 76 `cur.execute(...` risks an SQL injection, use parameterized queries instead
- line 74 Missing upsert logic, use `INSERT INTO ... ON CONFLICT(email) DO UPDATE`
- line 62 `email = payload.get("email", "")`, add validation for the required fields to prevent bad data
- line 63 `payload.get("role", "user")` wrap in `trl/except` to prevent invalid JSON
- There is a resource leak as `db` is never closed
- line 45 `WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "dev-secret")` is an unsafe fallback, fail fast if missing in production
- should ensure request is actually from vendor

# Code Challenge Follow Up Questions
1. I was able to create a basic four function calculator.
2. One challenge that was encountered during this was the frontend/backend communication. During the process, I had some issues with updating the UI correctly and handling the errors properly. Another challenge during the process was trying to figure out a way to evaluate user input without introduicing security risks. I solved this with an implimented parser using AST to control the operations instead of just using Python's eval. Remembering to handle edge cases, like zero division, slipped my mind when building the calculator, which led to an error when testing.
3. If given unlimeted time, I would expand the calculator from a basic four function calculator into a scientific one. I would also try to impliment keyboard input instead of having the calculator just be mouse/on click.
4. During coding process, I did have AI look overmy code to help with some of the challenges I ran into. It did well to remind me of edge cases to look out for. However, for thingsl ike frontend & backend communication challenges, it was a bit less helpful as the code spanned multiple files. To help improve the accurarcy in pinpointing what was wrong, I slowly went down the list of suggestion for what was wrong and updated the prompt each time its suggested fixes did not work. This allowed me to eventually pinpoint the file and section of code that was causing the communication error.
