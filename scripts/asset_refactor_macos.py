import os
import shutil
import ast
import re

def clean_python_code(source):
    """
    Remove comments and docstrings from Python source code using AST.
    """
    try:
        parsed = ast.parse(source)
    except SyntaxError:
        return source

    # Remove docstrings
    for node in ast.walk(parsed):
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef, ast.Module)):
            continue
        if not len(node.body):
            continue
        if isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            node.body.pop(0)

    # Unparse (removes comments automatically as AST doesn't store them)
    if hasattr(ast, 'unparse'):
        return ast.unparse(parsed)
    return source

def main():
    root_dir = os.getcwd()
    review_kit_dir = os.path.join(root_dir, 'review-kit', 'review-kit-A-pFDO')
    research_omap_dir = os.path.join(root_dir, 'research-omap')

    # 1. Clean and Create Directories
    if os.path.exists(review_kit_dir):
        shutil.rmtree(review_kit_dir)
    os.makedirs(review_kit_dir, exist_ok=True)
    
    if not os.path.exists(research_omap_dir):
        os.makedirs(research_omap_dir)

    # 2. Copy Assets
    print(f"Copying assets to {review_kit_dir}...")
    for item in ['src', 'docs', '.cursorrules']:
        s = os.path.join(root_dir, item)
        d = os.path.join(review_kit_dir, item)
        if os.path.exists(s):
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            elif os.path.isfile(s):
                shutil.copy2(s, d)

    # 3. Sanitize (Desensitize)
    print("Sanitizing assets (removing comments, docstrings, empty lines)...")
    for root, dirs, files in os.walk(review_kit_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.py'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    cleaned_content = clean_python_code(content)
                    
                    # Remove empty lines
                    lines = [line for line in cleaned_content.split('\n') if line.strip()]
                    final_content = '\n'.join(lines)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(final_content)
                except Exception as e:
                    print(f"Error cleaning {file_path}: {e}")

    print("Asset Refactoring Complete.")

if __name__ == "__main__":
    main()
