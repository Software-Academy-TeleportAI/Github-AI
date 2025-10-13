from github import Github
import base64
from llm import LLMDiagramGenerator, DiagramExporter
from integration import InitModelAI, SetUpGithub
from dotenv import load_dotenv
import os

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")

repoClass = SetUpGithub(github_token=GITHUB_TOKEN, repo_name=REPO_NAME)
repo = repoClass.authenticate()

print("Initializing LLM Diagram Generator...")
generator = LLMDiagramGenerator()
exporter = DiagramExporter()


def get_all_files(contents):
    files = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            files.append(file_content)
    return files


print(f"Fetching files from repository: {REPO_NAME}")
contents = repo.get_contents("")
all_files = get_all_files(contents)

print(f"Found {len(all_files)} total files")

code_extensions = ('.py')
code_files = [f for f in all_files if f.path.endswith(code_extensions)]

print(f"Found {len(code_files)} code files to analyze\n")

all_code_contents = []

for idx, file in enumerate(code_files, 1):
    print(f"[{idx}/{len(code_files)}] Processing: {file.path}")
    
    try:
        content = file.decoded_content.decode("utf-8", errors="ignore")
        
        all_code_contents.append((file.path, content))
        
        print(f"  → Generating diagram with LLM...")
        result = generator.generate_class_diagram(file.path, content)
        
        if result.success:
            output_path = exporter.save_diagram(result)
            print(f"  ✓ Diagram saved: {output_path}")
            
     
            if result.description:
                print(f"  📝 {result.description[:100]}...")
        else:
            print(f"  ✗ Failed: {result.error}")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print()

print("=" * 60)
print("Generating repository structure diagram...")
file_paths = [f.path for f in all_files]
structure_result = generator.generate_repository_structure(file_paths)

if structure_result.success:
    exporter.save_diagram(structure_result)
    print("✓ Repository structure diagram created")

if len(all_code_contents) > 1:
    print("\nGenerating multi-file architecture diagram...")
    multi_result = generator.generate_multi_file_diagram(all_code_contents)
    
    if multi_result.success:
        exporter.save_diagram(multi_result)
        print("✓ Multi-file architecture diagram created")

print("\n" + "=" * 60)
print("✓ All diagrams generated successfully!")
print(f"📁 Check the 'docs/diagrams' folder for all diagrams")
print("=" * 60)
