# Dockerfile
FROM python:3.11-slim

# Installer bash, git, nano, bash-completion og curl
RUN apt-get update && apt-get install -y \
    bash \
    git \
    nano \
    bash-completion \
    curl \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Last ned git-prompt som gir __git_ps1
RUN curl -Lo /etc/bash_completion.d/git-prompt \
  https://raw.githubusercontent.com/git/git/master/contrib/completion/git-prompt.sh


# Konfigurer Bash-prompt for å vise Git-branch
RUN echo "\
source /etc/bash_completion.d/git-prompt.sh\n\
PS1='\\u@\\h:\\w\$(__git_ps1 \" (%s)\")\\$ '\n" \
>> /root/.bashrc

RUN useradd -m -s /bin/bash vscode



# Sett arbeidsmappe i containeren
WORKDIR /app

# Kopier kravfil og installer Python-avhengigheter
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopier resten av prosjektet inn i containeren
COPY . .

# Gi alt eierskap til `vscode` før bytte av bruker
RUN chown -R vscode:vscode /app


USER vscode
RUN echo "\
source /etc/bash_completion.d/git-prompt.sh\n\
PS1='\\u@\\h:\\w\$(__git_ps1 \" (%s)\")\\$ '\n" \
>> /home/vscode/.bashrc


# Start applikasjonen
CMD ["sleep", "infinity"]
