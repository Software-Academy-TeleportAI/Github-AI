from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Server is running! Go to /api/users to see the JSON mock."


@app.route("/api/generate/docs")
def generate_docs():
    return jsonify({"message": "Documentation generated successfully."})

@app.route("/api/users")
def get_mock_users():
    
    mock_data = {
        "status": "success",
        "count": 3,
        "data": [
            {
                "id": 1,
                "username": "jdoe_99",
                "role": "admin",
                "active": True
            },
            {
                "id": 2,
                "username": "alice_w",
                "role": "editor",
                "active": False
            },
            {
                "id": 3,
                "username": "bob_builder",
                "role": "viewer",
                "active": True
            }
        ]
    }
    
    return jsonify(mock_data)

if __name__ == "__main__":
    app.run(debug=True, port=8001)