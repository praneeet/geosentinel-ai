"""
GeoSentinel AI - Codebase Exporter & LLM Context Digest Generator
Packages the clean source code into:
1. GEOSENTINEL_CODEBASE_DIGEST.md (Single comprehensive Markdown file for LLMs)
2. geosentinel_ai_source_archive.zip (Clean zip under 1MB for drag-and-drop into Claude/ChatGPT)
"""
import os
import sys
import zipfile

def export_codebase():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    digest_path = os.path.join(root_dir, "GEOSENTINEL_CODEBASE_DIGEST.md")
    zip_path = os.path.join(root_dir, "geosentinel_ai_clean_source.zip")

    ignore_dirs = {
        ".git", ".venv", "node_modules", ".pytest_cache", "dist",
        "__pycache__", "build", "coverage", "htmlcov", "postgres_data", "redis_data"
    }

    ignore_extensions = {
        ".db", ".sqlite", ".sqlite3", ".joblib", ".pyc", ".pyo",
        ".png", ".jpg", ".jpeg", ".ico", ".svg", ".zip", ".tar", ".gz"
    }

    included_extensions = {
        ".py", ".jsx", ".js", ".json", ".html", ".css", ".md",
        ".yml", ".yaml", ".ini", ".conf", ".ps1", ".bat", ".txt", ".mako"
    }

    print(f"Scanning project root: {root_dir}")
    source_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Prune ignored directories in-place
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in ignore_extensions:
                continue
            if fname in {".env", "geosentinel.db", "geosentinel_ai_clean_source.zip", "GEOSENTINEL_CODEBASE_DIGEST.md"}:
                continue
            
            # Include code, config, docs
            if ext in included_extensions or fname in {"Dockerfile", "Dockerfile.prod", "LICENSE", ".env.example", ".gitignore"}:
                full_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(full_path, root_dir).replace("\\", "/")
                source_files.append((rel_path, full_path))

    source_files.sort(key=lambda x: x[0])
    print(f"Found {len(source_files)} relevant source code and configuration files.")

    # 1. Create Clean ZIP Archive
    print(f"Generating clean zip archive: {zip_path}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel_path, full_path in source_files:
            zf.write(full_path, arcname=f"geosentinel-ai/{rel_path}")
    zip_size_kb = os.path.getsize(zip_path) / 1024
    print(f"Archive created successfully: {zip_size_kb:.1f} KB")

    # 2. Create Single-File Markdown Digest
    print(f"Generating single-file LLM context digest: {digest_path}")
    with open(digest_path, "w", encoding="utf-8") as out:
        out.write("# GeoSentinel AI — Complete Monorepo Source Code Digest\n\n")
        out.write("> Automated export for deep architectural, mathematical, and security analysis by AI models.\n")
        out.write(f"> Total Files Included: {len(source_files)}\n\n")
        out.write("## File Index\n\n")
        for rel_path, _ in source_files:
            out.write(f"- `{rel_path}`\n")
        out.write("\n---\n\n")

        for rel_path, full_path in source_files:
            out.write(f"## File: `{rel_path}`\n\n")
            lang = ""
            ext = os.path.splitext(rel_path)[1].lower()
            if ext in {".py"}:
                lang = "python"
            elif ext in {".js", ".jsx"}:
                lang = "javascript"
            elif ext in {".json"}:
                lang = "json"
            elif ext in {".css"}:
                lang = "css"
            elif ext in {".html"}:
                lang = "html"
            elif ext in {".md"}:
                lang = "markdown"
            elif ext in {".yml", ".yaml"}:
                lang = "yaml"
            elif ext in {".ini", ".conf"}:
                lang = "ini"
            elif ext in {".ps1"}:
                lang = "powershell"
            elif ext in {".bat"}:
                lang = "bat"

            out.write(f"```{lang}\n")
            try:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"# [Error reading file: {e}]\n")
            out.write("\n```\n\n---\n\n")

    digest_size_kb = os.path.getsize(digest_path) / 1024
    print(f"Digest generated successfully: {digest_size_kb:.1f} KB")
    print("Done!")

if __name__ == "__main__":
    export_codebase()

