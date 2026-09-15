import os
import json
import requests
from pathlib import Path

class ChameleonAgent:
    def __init__(self, target_dir=".", model_name="phi3"):
        self.target_dir = Path(target_dir).resolve()
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434/api/generate"
        
    def harvest_ambient_context(self):
        """Scans the working directory to understand the tech stack and naming conventions."""
        context = {
            "detected_files": [],
            "extensions": set(),
            "inferred_environment": "Generic Workstation"
        }
        
        # Scan the directory to look for existing project files
        for root, dirs, files in os.walk(self.target_dir):
            # Limit scan depth to 2 levels to ensure blazing-fast performance
            depth = len(Path(root).relative_to(self.target_dir).parts)
            if depth > 2:
                continue
            for file in files:
                if not file.startswith('.'):  # Ignore hidden files like .git
                    context["detected_files"].append(file)
                    ext = Path(file).suffix
                    if ext:
                        context["extensions"].add(ext)
                        
        # Basic heuristic inference engine to figure out what type of project this is
        ext_list = list(context["extensions"])
        if '.js' in ext_list or '.json' in ext_list:
            context["inferred_environment"] = "Node.js / JavaScript Backend Environment"
        elif '.py' in ext_list:
            context["inferred_environment"] = "Python / Data Science Workstation"
        elif '.go' in ext_list:
            context["inferred_environment"] = "Go Microservices Node"
            
        context["extensions"] = list(context["extensions"])
        return context

    def synthesize_honeytoken(self, system_context):
        """Uses a local LLM to generate a high-fidelity, context-aware decoy file configuration."""
        prompt = f"""
        You are an advanced automation engine deployed inside a target system.
        System Context:
        - Inferred Environment: {system_context['inferred_environment']}
        - Existing Files in Directory: {system_context['detected_files'][:10]}
        
        Task: 
        Generate the content for a highly realistic decoy file that a hacker would want to steal (e.g., config file, credentials file, .env file). It must look exactly like it belongs in this specific directory structure.
        Include a fake API key or credential string formatted as 'HONEY_KEY_XYZ123'.
        
        Respond strictly in valid JSON format with two keys:
        "filename": (a highly realistic filename matching the environment)
        "content": (the exact text content of the file, properly formatted)
        Do not include markdown blocks or conversational text outside the JSON output.
        """
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            response_data = response.json()
            # Parse the JSON response received from the LLM
            generation = json.loads(response_data['response'])
            return generation
        except Exception as e:
            print(f"[-] LLM Synthesis failed: {e}")
            return None

    def deploy_trap(self):
        print("[*] Harvesting ambient system fingerprint...")
        context = self.harvest_ambient_context()
        print(f"[+] Fingerprint compiled. Inferred Tech Stack: {context['inferred_environment']}")
        
        print(f"[*] Dispatching synthesis request to local LLM ({self.model_name})...")
        decoy = self.synthesize_honeytoken(context)
        
        if decoy:
            trap_path = self.target_dir / decoy['filename']
            with open(trap_path, 'w') as f:
                f.write(decoy['content'])
            print(f"[++] Successfully deployed high-fidelity trap file at: {trap_path}")
            return decoy['filename']
        else:
            print("[-] Decoy synthesis aborted.")
            return None

if __name__ == "__main__":
    # Initialize the agent in the current directory
    agent = ChameleonAgent(model_name="phi3")
    deployed_file = agent.deploy_trap()
