import re


def strip_markdown(text: str) -> str:
    """
    Fjerner vanlig markdown-formattering fra tekst.
    """
    text = re.sub(r'(`{1,3})(.*?)\1', r'\2', text)  # kode
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)  # kursiv
    text = re.sub(r'__([^_]+)__', r'\1', text)  # understrek
    text = re.sub(r'#+\s', '', text)  # overskrifter
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # lenker
    return text.strip()
