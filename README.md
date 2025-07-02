# DC2025
Prototype for en AI-assistent som hjelper kundeservice med å svare på henvendelser basert på dokumentasjon fra Digdir og interne rutiner.

## 🚀 Project Setup – Dev Container Enabled

Welcome to the project! This repository is set up for **fast onboarding** using **Visual Studio Code Remote - Containers (Dev Containers)**. Follow the steps below to get started.

---

## 📦 Requirements

Make sure you have the following installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (and it's running)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

---

## ⚙️ Getting Started

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-org/your-project.git
   cd your-project


## 🧑‍💻 Open in Dev Container

4. **Open the folder in VS Code**  
   - Launch **Visual Studio Code**
   - Open the project folder (`File` → `Open Folder...`)

5. **Reopen in Container**

   VS Code should prompt you:

   > _"This folder contains a Dev Container configuration. Reopen in container?"_

   👉 Click **“Reopen in Container”**

   **If you don’t get the prompt:**
   - Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
   - Search: **`Dev Containers: Reopen in Container`** and run it

6. **Done! 🎉**  
   The container will automatically:
   - ✅ Copy `.env.template` → `.env` (if not already present)
   - ✅ Install dependencies from `requirements.txt`
   - ✅ Set up a fully configured Python environment ready to use


### 🌐 Open the API Docs

Once the dev container is running and the app has started (automatically or manually), you can open your browser and go to:

http://localhost:8000/docs


This opens the **interactive API documentation** powered by **FastAPI (Swagger UI)**, where you can explore and test all available endpoints. 

---
# Developer info
All services has (in progress) a Minimal Usage documentation within the class documentation.
Please read this and use as intended.

## 🧹 Ruff
Ruff is a fast, all-in-one Python linter, formatter, and import sorter.
### Basic Commands

```bash
ruff check . # Lint the codebase
ruff check . --fix # Auto-fix lint issues
ruff format . # Format the code
ruff format --check . # Check formatting
```

