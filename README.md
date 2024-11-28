# FormSensei

FormSensei is a social media platform where you can get expert and community feedback regarding your workout form. 
This project is built using Python and follows a microservices architecture.

## **1. Prerequisites**

Before running the application, ensure you have the following installed on your system:

- **Python 3.9+**
- **Docker** (if using the Dockerized setup)
- **Git** (optional, for cloning the repository)

---
##
**Install Docker**
 
 Download and install Docker from the [official website](https://www.docker.com/get-started). Follow the instructions for your operating system.

**Run Docker**

Launch the Docker Desktop Application


**Shortcut using the docker compose file**

```sh
docker-compose up
```
and CTR + C to terminate or
```sh
docker-compose down
```
 **Build Docker Image**

```sh
 docker build -t form-sensei .
```

**Run Docker Container**

docker run -d -p 8000:8000 form-sensei

**Access the Application**
http://localhost:8000
or
http://127.0.0.1:8000/

or the API
http://127.0.0.1:8000/docs

**Stop the Container**
either in the Desktop APP or with the CMD
```sh
 docker stop <container-id>
```


## Features

- User authentication and management
- Post creation, editing, and deletion
- Database integration
- API endpoints for user and post services

## Setup

1. **Create Python Virtual Environment**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2. **Install Dependencies**

    ```sh
    pip install -r requirements.txt
    ```

3. **Commit Convention**

    Follow the commit convention as described [here](https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13).

## Usage

1. **Run the Application**

    ```sh
    python app/main.py
    ```

2. **Run Tests**

    ```sh
    python -m unittest discover -s app/tests
    ```

## Project Structure

    app/
    ├── main.py             # API entry point
    ├── db.py               # Database connection and models
    ├── services/
    │   ├── post_service.py # Services for the post endpoint
    │   └── user_service.py # Services for the user endpoint
    ├── schemas/
    │   ├── post_schema.py  # Schema for the return of post endpoint
    │   └── user_schema.py  # Schema for the return of user endpoint
    ├── test_app.py         # Test Case file
    ├── README.md           # Documentation
    ├── backend.py          # Deprecated, should be deleted after tests are adapted
    └── deleteDB.py         # Should be put into db.py

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Open a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


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


    

    