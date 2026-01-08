from flask import Flask, jsonify, request
import time
import threading
import requests
from github_service import SetUpGithub
import os
from dotenv import load_dotenv
from ai import LLM

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = Flask(__name__)

def get_all_files(contents, repo):
    files = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            files.append(file_content)
    return files


def get_key_technical_files(all_files, framework: str):
    """
    Filters the repository to find the files that define the 'Business Logic'
    based on the framework.
    """
    key_files_content = ""
    priority_files = []
    patterns = {
        "Laravel": ["app/Models", "database/migrations", "app/Http/Controllers"],
        "Django": ["models.py", "views.py", "serializers.py"],
        "React": ["types.ts", "interfaces.ts", "store", "context"],
        "Next.js": ["prisma/schema.prisma", "types.ts"],
        "Flask": ["models.py", "app.py"]
    }

    search_paths = patterns.get(framework, ["src", "app", "models"])

    count = 0
    max_files = 10 

    for file in all_files:
        
        if any(p in file.path for p in search_paths) and file.path.endswith(('.php', '.py', '.ts', '.js', '.prisma')):
            if count < max_files:
                try:
                    
                    content = file.decoded_content.decode('utf-8')
                    
                    if len(content) > 2000: 
                        content = content[:2000] + "...(truncated)"
                    
                    key_files_content += f"\n\n--- FILE: {file.path} ---\n{content}"
                    count += 1
                except:
                    continue
    
    return key_files_content

def generate_technical_docs_process(job_id, repo_url, token, callback_url):
    print(f"[{job_id}] ⚙️ Starting TECHNICAL generation for: {repo_url}")
    
    try:
        repoClass = SetUpGithub(github_token=token, repo_url=repo_url)
        repo = repoClass.authenticate()
        
        languages = list(repo.get_languages().keys())
        llm = LLM(repo_languages=languages, model="gemini-2.5-flash", api_key=GOOGLE_API_KEY, user_choice="google")

        contents = repo.get_contents("")
        all_files = get_all_files(contents, repo)
        file_paths = [f.path for f in all_files]
        framework = llm.detect_framework(file_paths)
        print(f"[{job_id}] Framework: {framework}")

        print("Extracting key file contents for deep analysis...")
        key_code = get_key_technical_files(all_files, framework)

        print("Generating technical architecture diagram...")
        tech_result = llm.generate_technical_architecture(framework, file_paths, key_code)

        print("Generating technical specs...")
        docs = llm.generate_documentation(tech_result)

        
        final_result = {
            "job_id": job_id,
            "status": "completed",
            "type": "technical",
            "summary": f"Technical Deep Dive into {framework} Data & Logic Layer.",
            "architecture_diagram": tech_result.mermaid_code,
            "readme_suggestion": docs
        }
        
        requests.post(callback_url, json=final_result)
        print(f"[{job_id}] ✅ Technical Docs Sent.")

    except Exception as e:
        print(f"[{job_id}] ❌ Error: {e}")
        requests.post(callback_url, json={"job_id": job_id, "status": "failed", "error": str(e)})


def generate_docs_process(job_id, repo_url, token, callback_url):
    repoClass = SetUpGithub(github_token=token, repo_url=repo_url)
    repo = repoClass.authenticate()

    languages = repo.get_languages()
    repo_languages = list(languages.keys())

    llm = LLM(repo_languages=repo_languages, model="gemini-2.5-flash", api_key=GOOGLE_API_KEY, user_choice="google")

    print(f"Fetching files from repository: {repo_url}")
    contents = repo.get_contents("")
    all_files = get_all_files(contents, repo)

    print("Generating repository structure diagram...")
    file_paths = [f.path for f in all_files]
    framework_type = llm.detect_framework(file_paths)
    structure_summary = llm._summarize_structure(file_paths)
    print("Generating high-level architecture diagram...")
    arch_result = llm.generate_high_level_architecture(framework_type, structure_summary)

    print("Generating documentation text...")
    docs = llm.generate_documentation(arch_result)


    """
    This function runs in the background. It simulates cloning, 
    analyzing, and generating docs.
    """
    print(f"[{job_id}] 🚀 Starting generation for: {repo_url}")
    
    try:
    
        final_result = {
            "job_id": job_id,
            "status": "completed",
            "summary": "Application handling user authentication...",
            
          
            "architecture_diagram": arch_result.mermaid_code,
            
            "files": [
            
            ],
            "readme_suggestion": docs
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
    tehnical = data.get('tehnical')
    callback_url = data.get('callback_url')

    if not all([job_id, repo_url, callback_url]):
        return jsonify({"error": "Missing required fields"}), 400
    
    if tehnical:
        print(f"Starting TECHNICAL doc generation for job: {job_id}")
        thread = threading.Thread(
            target=generate_technical_docs_process, 
            args=(job_id, repo_url, github_token, callback_url)
        )
    else:
        print(f"Starting STANDARD doc generation for job: {job_id}")
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