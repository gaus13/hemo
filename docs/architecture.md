@ During Registration what is the authentication flow @
Register Request
        │
        ▼
Hash Password
        │
        ▼
Save User
        │
        ▼
Create JWT
        │
        ▼
Return JWT

@ During Login @
Login Request
        │
        ▼
Find User
        │
        ▼
verify_password()
        │
        ▼
Password Correct?
        │
        ▼
create_access_token()

########### This is the complete authentication lifecycle ###################
REGISTER
    │
    ▼
hash_password()
    │
    ▼
Database
    │
    ▼
create_access_token()
    │
    ▼
JWT Returned

Later...

Protected Request
    │
    ▼
decode_token()
    │
    ▼
user_id
    │
    ▼
Database
    │
    ▼
Current User