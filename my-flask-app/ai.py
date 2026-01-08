from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from google.oauth2 import service_account
import json
import os
from typing import List, Dict, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path
from ai_models_connection.llm_provider import LLMProviderFactory
from ai_models_connection.main import InitModelAI

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

private_key = os.getenv("PRIVATE_KEY").replace("\\n", "\n") 

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
type = os.getenv('GOOGLE_TYPE')
project_id = os.getenv('GOOGLE_PROJECT_ID')
private_key_id = os.getenv('PRIVATE_KEY_ID')
private_key = private_key
client_email = os.getenv('CLIENT_EMAIL')
client_id = os.getenv('CLIENT_ID')
auth_uri = os.getenv('AUTH_URI')
token_uri = os.getenv('TOKEN_URI')
auth_provider = os.getenv('AUTH_PROVIDER')
client_cert_url = os.getenv('CLIENT_CERT_URL')
universe_domain = os.getenv('UNIVERS_DOMAIN')

print("Loaded GOOGLE_API_KEY:", GOOGLE_API_KEY is not None)

json_string = """
{{
  "type": "{type}",
  "project_id": "{project_id}",
  "private_key_id": "{private_key_id}",
  "private_key": "{private_key}",
  "client_email": "{client_email}",
  "client_id": "{client_id}",
  "auth_uri": "{auth_uri}",
  "token_uri": "{token_uri}",
  "auth_provider_x509_cert_url": "{auth_provider}",
  "client_x509_cert_url": "{client_cert_url}",
  "universe_domain": "{universe_domain}"
}}
""".format(
    type=type,
    project_id=project_id,
    private_key_id=private_key_id,
    private_key=private_key,
    client_email=client_email,
    client_id=client_id,
    auth_uri=auth_uri,
    token_uri=token_uri,
    auth_provider=auth_provider,
    client_cert_url=client_cert_url,
    universe_domain=universe_domain
)

@dataclass
class DiagramResult:
    """Store diagram generation results"""
    mermaid_code: str
    description: str
    file_path: str
    success: bool = True
    error: str = None


class LLM:
    """Generate code diagrams using Google Gemini LLM"""
    
    def __init__(self, credentials_json: str = None, user_choice: str = "google", model: str = "gemini-2.0-flash", repo_languages: List[str] = None, api_key: str = None):
        """Initialize LLM with credentials"""
        if api_key and user_choice:
            print(f"Using {user_choice} model: {model}, cred: {api_key}")
            provider = LLMProviderFactory.create_provider(provider_name=user_choice, api_key=api_key, model=model)
            model_ai = InitModelAI(provider)
            self.llm = model_ai.llm

        else:
            credentials_info = json.loads(json_string)
            credentials = service_account.Credentials.from_service_account_info(credentials_info)
            print(f"Using Google Gemini model: {model}, cred: Service Account")
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)

        self.languages = repo_languages or []
        self._setup_prompts()

    def detect_framework(self, file_paths: List[str]) -> str:
        """
        Analyzes file list to determine the primary framework.
        """
        files_set = set(f.lower() for f in file_paths)
        
        # PHP / Laravel
        if 'artisan' in files_set and 'composer.json' in files_set:
            return "Laravel"
        
        # JS / Frontend frameworks
        if 'package.json' in files_set:
            # In a real scenario, we'd read package.json, but simplified check:
            if 'next.config.js' in files_set or 'next.config.ts' in files_set:
                return "Next.js"
            if 'angular.json' in files_set:
                return "Angular"
            if any(f.endswith('.jsx') or f.endswith('.tsx') for f in files_set):
                return "React"
            if 'vue.config.js' in files_set:
                return "Vue.js"
                
        # Python
        if 'manage.py' in files_set:
            return "Django"
        if 'app.py' in files_set or 'wsgi.py' in files_set:
            return "Flask/FastAPI"
            
        return "Generic " + (self.languages[0] if self.languages else "Code")
    
    def _setup_prompts(self):
        """Setup prompts for diagram generation"""
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                f""""You are an expert software architect and code analyzer. Your task is to analyze code files and create clear, accurate Mermaid diagrams.
                    The code what you are analyzing is written in the following programming languages: {self.languages}.

                    CRITICAL RULES FOR MERMAID SYNTAX:
                    1. Use ONLY standard Mermaid classDiagram syntax
                    2. **NEVER use note statements** - they cause parsing errors
                    3. Show classes, methods, and relationships ONLY

                    Guidelines:
                    1. Identify all classes, interfaces, structs, functions, and their relationships
                    2. Show inheritance, composition, and important dependencies
                    4. Use **valid Mermaid classDiagram syntax** only
                    5. **Do NOT add notes for individual methods or attributes.**
                    6. Only use `note for ClassName "..."` or detached notes like `note "..." as Note1`
                    7. Ensure diagrams pass Mermaid parser validation
                    8. Add a short plain-text description after the ```mermaid``` block."
                    9. NEVER use curly braces like abstract or static
                    10. Use <<abstract>> to denote abstract classes above the class name, not inside curly braces
                    11. Use <<static>> to denote static methods, not inside curly braces

                    Return ONLY valid Mermaid classDiagram code in ```mermaid``` blocks, followed by a plain text description.
                    """
            ),

            MessagesPlaceholder(variable_name="messages")
        ])
        
        self.structure_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                f"""You are an expert in repository structure analysis. Create a Mermaid graph showing the file/module organization.
                 The code what you are analyzing is written in the following programming languages: {self.languages}.

                Guidelines:
                1. Create a tree/graph structure showing directories and key files
                2. Group related files together
                3. Show important dependencies between modules
                4. Keep it clean and readable
                5. Use appropriate Mermaid graph syntax

                    CRITICAL RULES FOR MERMAID SYNTAX:
                    1. Use ONLY standard Mermaid classDiagram syntax
                    2. **NEVER use note statements** - they cause parsing errors
                    3. Show classes, methods, and relationships ONLY

                    Guidelines:
                    1. Identify all classes, interfaces, structs, functions, and their relationships
                    2. Show inheritance, composition, and important dependencies
                    4. Use **valid Mermaid classDiagram syntax** only
                    5. **Do NOT add notes for individual methods or attributes.**
                    6. Only use `note for ClassName "..."` or detached notes like `note "..." as Note1`
                    7. Ensure diagrams pass Mermaid parser validation
                    8. Add a short plain-text description after the ```mermaid``` block."
                    9. NEVER use curly braces like abstract or static
                    10. Use <<abstract>> to denote abstract classes above the class name, not inside curly braces
                    11. Use <<static>> to denote static methods, not inside curly braces

                Return ONLY the Mermaid diagram code wrapped in ```mermaid``` blocks."""
            ),
            MessagesPlaceholder(variable_name="messages")
        ])
        
        self.documentation_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert Technical Writer and Software Architect.
                Your task is to analyze a raw Mermaid diagram definition and generate comprehensive, human-readable documentation.

                Goal: Convert the technical diagram structure into a clear architectural explanation.

                Guidelines for Analysis:
                1. **Executive Summary**: Start with a high-level overview of what the system represents based on the diagram.
                2. **Component Breakdown**: Explain the purpose of key classes, modules, or nodes found in the diagram.
                3. **Relationships & Logic**: 
                   - If it is a Class Diagram: Explain the inheritance hierarchy, dependencies, and composition. Explain *why* these relationships exist.
                   - If it is a Graph/Tree: Explain the folder structure or data flow.
                4. **Design Patterns**: Identify and mention any visible design patterns (e.g., Factory, Singleton, Observer, MVC).

                Formatting Rules:
                1. Output **strictly in Markdown**.
                2. Use clear headings (##, ###).
                3. Use bullet points for readability.
                4. **Bold** key class names or component names.
                5. Do NOT output the Mermaid code again; only output the text description.
                6. Put space between paragraphs for better readability.
                7. Be sure that the important text has a bigger font size.

                Return the Markdown documentation explaining the provided diagram."""
            ),
            MessagesPlaceholder(variable_name="messages")
        ])

        self.high_level_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a CTO explaining a software architecture to a non-technical CEO.
                Your goal is to create a high-level System Architecture Diagram using Mermaid.

                Context: The application is built using **{framework}**.

                Guidelines for the Diagram:
                1. **Abstraction Level**: High. Do NOT show specific class names or file names.
                2. **Nodes**: Represent logical modules (e.g., "User", "Web Interface", "Authentication Service", "Payment Database").
                3. **Flow**: Show how data flows from the User -> Frontend -> Backend -> Database.
                4. **Labels**: Use plain English for arrows (e.g., "Submits Form", "Fetches Data", "Validates").

                CRITICAL MERMAID RULES:
                1. Use `graph TD` (Top-Down) or `graph LR` (Left-Right).
                2. Use Subgraphs to group areas (e.g., `subgraph "Frontend"`, `subgraph "Server"`).
                3. Do NOT use classDiagram syntax.
                4. Styling: Use simple shapes. `([User])` for people, `[(Database)]` for storage.

                Return ONLY the Mermaid code wrapped in ```mermaid``` blocks."""
            ),
            MessagesPlaceholder(variable_name="messages")
        ])

        self.technical_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a Lead Software Architect conducting a code review.
                Your goal is to create a detailed **Technical Architecture Diagram** using Mermaid.

                Context: The application is built using **{framework}**.

                Guidelines:
                1. **Focus**: strict implementation details (Classes, Interfaces, Database Tables).
                2. **Syntax**: Use `classDiagram` or `erDiagram`.
                3. **Detail Level**: Show key methods, attributes, and relationships (inheritance <|--, composition *--, aggregation o--).
                
                FRAMEWORK SPECIFIC RULES:
                - **Laravel/Django/Spring**: Focus on **Models** (Entities) and **Controllers**. Show the data model relationships.
                - **React/Vue/Angular**: Focus on the **Component Tree**. Show which components manage state or call APIs.
                - **Microservices**: Show the API contracts and data schemas.

                CRITICAL MERMAID RULES:
                1. Use standard `classDiagram` syntax.
                2. Do NOT use notes.
                3. If using `classDiagram`, use `class Name {{ type attribute \n method() }}` format.
                4. Group related classes using `namespace` if possible.

                Return ONLY the Mermaid code wrapped in ```mermaid``` blocks."""
            ),
            MessagesPlaceholder(variable_name="messages")
        ])
        
        self.technical_chain = self.technical_prompt | self.llm
        self.high_level_chain = self.high_level_prompt | self.llm
        self.documentation_chain = self.documentation_prompt | self.llm
        self.analysis_chain = self.analysis_prompt | self.llm
        self.structure_chain = self.structure_prompt | self.llm
    
    def generate_class_diagram(self, file_path: str, code_content: str) -> DiagramResult:
        """Generate class diagram for a single file"""
        try:

            max_chars = 15000
            if len(code_content) > max_chars:
                code_content = code_content[:max_chars] + "\n\n... (truncated)"
            
            messages = [
                {
                    "role": "user",
                    "content": f"""Analyze this code file and create a Mermaid class diagram.

                    File: {file_path}

                    Code:
                    ```
                    {code_content}
                    ```
                    IMPORTANT: 
                    - Use ONLY valid Mermaid classDiagram syntax
                    - Do NOT include any note statements
                    - Show classes, attributes, methods, and relationships
                    - Keep it clean and parseable
                    Generate a comprehensive class diagram showing all classes, their relationships, and key methods."""
                }
            ]
            
            response = self.analysis_chain.invoke({"messages": messages})
            
            mermaid_code = self._extract_mermaid_code(response.content)
            description = self._extract_description(response.content)
            
            return DiagramResult(
                mermaid_code=mermaid_code,
                description=description,
                file_path=file_path,
                success=True
            )
            
        except Exception as e:
            return DiagramResult(
                mermaid_code="",
                description="",
                file_path=file_path,
                success=False,
                error=str(e)
            )
    
    def generate_high_level_architecture(self, framework: str, file_summary: str) -> DiagramResult:
        """Generates a simplified architecture diagram for non-tech users"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": f"""Create a high-level architecture diagram for this {framework} project.
                    
                    Based on this file structure, infer the major modules:
                    {file_summary}
                    
                    Show the "Big Picture" view."""
                }
            ]
            
            response = self.high_level_chain.invoke({
                "messages": messages, 
                "framework": framework
            })
            
            mermaid_code = self._extract_mermaid_code(response.content)
            
            return DiagramResult(
                mermaid_code=mermaid_code,
                description=f"High-level architecture of the {framework} application",
                file_path="architecture_overview",
                success=True
            )
        except Exception as e:
            return DiagramResult("", "", "", False, str(e))
        
    def generate_technical_architecture(self, framework: str, file_list: List[str], key_file_contents: str) -> DiagramResult:
        """Generates a detailed class/ERD diagram for developers"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": f"""Create a technical class diagram for this {framework} project.

                    Key Files & Classes found:
                    {key_file_contents}

                    Repository Structure:
                    {self._summarize_structure(file_list)}

                    Generate a detailed diagram showing the core logic and data relationships."""
                }
            ]
            
            response = self.technical_chain.invoke({
                "messages": messages, 
                "framework": framework
            })
            
            mermaid_code = self._extract_mermaid_code(response.content)
            
            return DiagramResult(
                mermaid_code=mermaid_code,
                description=f"Detailed technical architecture of {framework} Core Components",
                file_path="technical_architecture",
                success=True
            )
        except Exception as e:
            return DiagramResult("", "", "", False, str(e))

    def generate_repository_structure(self, file_list: List[str]) -> DiagramResult:
        """Generate overall repository structure diagram"""
        try:
        
            structure_summary = self._summarize_structure(file_list)
            
            messages = [
                {
                    "role": "user",
                    "content": f"""Create a Mermaid graph diagram showing the structure of this repository.

                    Repository structure:
                    {structure_summary}

                    Create a clear, hierarchical diagram showing directories and their key files."""
                }
            ]
            
            response = self.structure_chain.invoke({"messages": messages})
            mermaid_code = self._extract_mermaid_code(response.content)
            
            return DiagramResult(
                mermaid_code=mermaid_code,
                description="Repository structure diagram",
                file_path="repository_structure",
                success=True
            )
            
        except Exception as e:
            return DiagramResult(
                mermaid_code="",
                description="",
                file_path="repository_structure",
                success=False,
                error=str(e)
            )
    
    def generate_multi_file_diagram(self, files: List[Tuple[str, str]]) -> DiagramResult:
        """Generate diagram showing relationships across multiple files"""
        try:
            
            file_summaries = []
            for file_path, content in files[:10]: 
                summary = content[:1000]
                file_summaries.append(f"File: {file_path}\n{summary}\n---")
            
            combined = "\n\n".join(file_summaries)
            
            messages = [
                {
                    "role": "user",
                    "content": f"""Analyze these multiple code files and create a unified Mermaid class diagram showing how they relate to each other.

                    Focus on:
                    - Cross-file relationships
                    - Imports and dependencies
                    - Inheritance across files
                    - Key interactions

                    Files:
                    {combined}

                Create a comprehensive diagram showing the architecture."""
                }
            ]
            
            response = self.analysis_chain.invoke({"messages": messages})
            mermaid_code = self._extract_mermaid_code(response.content)
            description = self._extract_description(response.content)
            
            return DiagramResult(
                mermaid_code=mermaid_code,
                description=description,
                file_path="multi_file_architecture",
                success=True
            )
            
        except Exception as e:
            return DiagramResult(
                mermaid_code="",
                description="",
                file_path="multi_file_architecture",
                success=False,
                error=str(e)
            )
        
    def generate_documentation(self, diagram_result: DiagramResult) -> str:
        """Generate documentation from a diagram"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": f"""Here is a Mermaid diagram definition:

                    ```mermaid
                    {diagram_result.mermaid_code}
                    ```

                    Generate comprehensive documentation explaining the architecture shown in this diagram."""
                }
            ]
            
            response = self.documentation_chain.invoke({"messages": messages})
            return response.content
            
        except Exception as e:
            return f"Error generating documentation: {str(e)}"
    
    def _extract_mermaid_code(self, content: str) -> str:
        """Extract mermaid code from LLM response"""
        import re
        
        pattern = r'```mermaid\s*(.*?)\s*```'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return content.strip()
    
    def _extract_description(self, content: str) -> str:
        """Extract description from LLM response"""
      
        parts = content.split('```')
        if len(parts) > 2:
            return parts[-1].strip()
        return "No description provided"
    
    def _summarize_structure(self, file_list: List[str]) -> str:
        """Summarize repository structure"""
        from collections import defaultdict
        
        structure = defaultdict(list)
        for file_path in file_list:
            parts = file_path.split('/')
            if len(parts) > 1:
                directory = '/'.join(parts[:-1])
                filename = parts[-1]
                structure[directory].append(filename)
            else:
                structure['root'].append(file_path)
        
        summary = []
        for directory, files in sorted(structure.items()):
            summary.append(f"\n{directory}/")
            for file in sorted(files)[:10]: 
                summary.append(f"  - {file}")
            if len(files) > 10:
                summary.append(f"  ... ({len(files) - 10} more files)")
        
        return "\n".join(summary)


class DiagramExporter:
    """Export diagrams to files"""
    
    @staticmethod
    def save_diagram(result: DiagramResult, output_dir: str = "docs/diagrams"):
        """Save diagram to markdown file"""
        os.makedirs(output_dir, exist_ok=True)
        
        safe_name = result.file_path.replace('/', '_').replace('.', '_')
        output_path = os.path.join(output_dir, f"{safe_name}.md")
        
        content = f"# Diagram: {result.file_path}\n\n"
        
        if result.success:
            content += f"## Description\n\n{result.description}\n\n"
            content += f"## Diagram\n\n```mermaid\n{result.mermaid_code}\n```\n"
        else:
            content += f"## Error\n\n{result.error}\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Saved: {output_path}")
        return output_path
