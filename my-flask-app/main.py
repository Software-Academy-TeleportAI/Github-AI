from flask import Flask, jsonify, request
import time
import threading
import requests

app = Flask(__name__)

def generate_docs_process(job_id, repo_url, token, callback_url):
    """
    This function runs in the background. It simulates cloning, 
    analyzing, and generating docs.
    """
    print(f"[{job_id}] 🚀 Starting generation for: {repo_url}")
    
    try:
        
        mermaid_code = """
        classDiagram
            class AuthController {
                +register(Request request)
                +login(Request request)
            }
            class User {
                +string email
                +string password
            }
            AuthController --> User : creates
        """

    
        final_result = {
            "job_id": job_id,
            "status": "completed",
            "summary": "Application handling user authentication...",
            
          
            "architecture_diagram": mermaid_code,
            
            "files": [
            
            ],
            "readme_suggestion": "# Project Title..."
        }
        
   
        response = requests.post(callback_url, json=final_result)
        
        if response.status_code == 200:
            print(f"[{job_id}]  Laravel acknowledged receipt.")
        else:
            print(f"[{job_id}]  Laravel returned error: {response.status_code}")

    except Exception as e:
     
        requests.post(callback_url, json={
            "job_id": job_id, 
            "status": "failed", 
            "error": str(e)
        })


@app.route('/api/start-generation', methods=['POST'])
def start_generation():
    data = request.json
    

    job_id = data.get('job_id')
    repo_url = data.get('repo_url')
    github_token = data.get('github_token')
    callback_url = data.get('callback_url')

    if not all([job_id, repo_url, callback_url]):
        return jsonify({"error": "Missing required fields"}), 400

    thread = threading.Thread(
        target=generate_docs_process, 
        args=(job_id, repo_url, github_token, callback_url)
    )
    thread.start()

    return jsonify({
        "message": "Generation started successfully",
        "job_id": job_id,
        "status": "processing"
    }), 202

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