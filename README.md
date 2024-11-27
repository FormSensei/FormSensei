# FormSensei

## Setup 

    create python venv

    commit convention
    https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13

## Files

    app/
    ├── main.py             # API entry point
    ├── db.py               # Database connection and models
    ├── services/
    │   ├── post_service.py # Services for the post endpoint
    │   └── user_service.py # Services for the user endpoint
    ├── schemas/
    │   ├── post_schema.py  # Schema for the return of post endpoint
    │   └── user_schema.py  # Schema for the retunr of user endpoint
    ├── test_app.py         # Test Case file
    ├── README.md           # Documentation
    ├── backend.py          # Deprecated, should be deleted after tests are adapted
    └── deleteDB.py         # Should be put into db.py


    

    