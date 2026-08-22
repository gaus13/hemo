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

@@@@@  My vision for Hemo (the version I want us to build) @@@@

                    HEMO
                       │
        ┌──────────────┴──────────────┐
        │                             │
 Authentication                Authorization
        │                             │
        └──────────────┬──────────────┘
                       │
                 User Profiles
                       │
         ┌─────────────┴─────────────┐
         │                           │
     Donor Profile            Requester Profile
         │                           │
         └─────────────┬─────────────┘
                       │
                Blood Requests
                       │
              Matching Algorithm
                       │
         Distance + Blood Match +
         Eligibility + Reliability
                       │
               Volunteer Workflow
                       │
              Donation Verification
                       │
               Donation History
                       │
               Reliability Score
                       │
              Notifications (Email/SMS)
                       │
          Analytics + Admin Dashboard



                 HEMO

        ┌──────────────────┐
        │      User        │
        └──────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
 Donor Profile      Requester Profile
        │                   │
        │             Creates Blood Request
        │                   │
        ▼                   ▼
 Volunteers          Blood Request Marketplace
        │                   ▲
        └──────────┬────────┘
                   │
            Donation Happens
                   │
                   ▼
      Donor uploads hospital proof
                   │
                   ▼
     Requester confirms donation
                   │
                   ▼
      Donation Verified by System
                   │
                   ▼
        Donation History Created
                   │
                   ▼
      Reliability Score Updated          





                          ┌───────────────┐
                    │     ACTIVE    │
                    └───────┬───────┘
                            │
                     Donor accepts
                            │
                            ▼
                    ┌───────────────┐
                    │ DONOR_MATCHED │
                    └───────┬───────┘
                            │
                    Donor cancels
                            │
                            ▼
                    ┌───────────────┐
                    │     ACTIVE    │◄──── Donor B
                    └───────┬───────┘       accepts
                            │
                            ▼
                    DONOR_MATCHED
                            │
                            ▼
                  DONATION_IN_PROGRESS
                            │
                            ▼
                   DONATION_VERIFIED
                            │
                            ▼
                        COMPLETED