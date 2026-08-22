"Why do we separate security.py and auth.py?"

A strong answer would be:
"security.py is responsible for password hashing and verification, while auth.py is responsible for creating and validating JWT tokens. They solve different problems and following the Single Responsibility Principle makes the code easier to maintain, test, and extend."

Why did we check for the email before calling: in request endpoint
bcs of
 Request comes
      │
      ▼
Hash password (CPU work)
      │
      ▼
Query database
      │
      ▼
Oops! Email already exists.(we wasted cpu time)
      │
      ▼
Return 409