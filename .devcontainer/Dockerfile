# Dockerfile
FROM python:3.11-slim

# Installer bash, git, nano, bash-completion og curl
RUN apt-get update && apt-get install -y --no-install-recommends \
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    git \
    nano \
    bash-completion \
    curl \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Last ned git-prompt som gir __git_ps1
RUN curl -Lo /etc/bash_completion.d/git-prompt \
  https://raw.githubusercontent.com/git/git/master/contrib/completion/git-prompt.sh

# Create dev user
RUN useradd -m -s /bin/bash vscode
# Create dev user
RUN useradd -m -s /bin/bash vscode

# Konfigurer Bash-prompt for å vise Git-branch
RUN echo "\
source /etc/bash_completion.d/git-prompt.sh\n\
PS1='\\u@\\h:\\w\$(__git_ps1 \" (%s)\")\\$ '\n" \ 
| tee -a /root/.bashrc /home/vscode/.bashrc
PS1='\\u@\\h:\\w\$(__git_ps1 \" (%s)\")\\$ '\n" \ 
| tee -a /root/.bashrc /home/vscode/.bashrc

# Sett arbeidsmappe i containeren
WORKDIR /app

# Kopier kravfil og installer Python-avhengigheter
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Kopier resten av prosjektet inn i containeren
COPY . .

# Gi alt eierskap til `vscode` før bytte av bruker
RUN chown -R vscode:vscode /app
USER vscode

# Start applikasjonen
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
