import docx
import sys

def read_docx(file_path):
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        return f"Error reading file: {e}"

if __name__ == "__main__":
    content = read_docx("documents/Protocolo de seguridad.docx")
    print(content)
