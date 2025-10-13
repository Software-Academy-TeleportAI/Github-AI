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


class LLMDiagramGenerator:
    """Generate code diagrams using Google Gemini LLM"""
    
    def __init__(self, credentials_json: str = None, user_choice: str = "google"):
        """Initialize LLM with credentials"""
        if credentials_json and user_choice:
            provider = LLMProviderFactory.create_provider(user_choice, credentials_json)
            model_ai = InitModelAI(provider)
            self.llm = model_ai.llm

        else:
            credentials_info = json.loads(json_string)
            credentials = service_account.Credentials.from_service_account_info(credentials_info)
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", credentials=credentials)

   
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Setup prompts for diagram generation"""
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """"You are an expert software architect and code analyzer. Your task is to analyze code files and create clear, accurate Mermaid diagrams.

                    Guidelines:
                    1. Identify all classes, interfaces, structs, functions, and their relationships
                    2. Show inheritance, composition, and important dependencies
                    3. Keep diagrams clean - show only the most important methods (max 5 per class)
                    4. Use **valid Mermaid classDiagram syntax** only
                    5. **Do NOT add notes for individual methods or attributes.**
                    6. Only use `note for ClassName "..."` or detached notes like `note "..." as Note1`
                    7. Ensure diagrams pass Mermaid parser validation
                    8. Add a short plain-text description after the ```mermaid``` block."
                """
            ),

            MessagesPlaceholder(variable_name="messages")
        ])
        
        self.structure_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert in repository structure analysis. Create a Mermaid graph showing the file/module organization.

                Guidelines:
                1. Create a tree/graph structure showing directories and key files
                2. Group related files together
                3. Show important dependencies between modules
                4. Keep it clean and readable
                5. Use appropriate Mermaid graph syntax

                Return ONLY the Mermaid diagram code wrapped in ```mermaid``` blocks."""
            ),
            MessagesPlaceholder(variable_name="messages")
        ])
        
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
