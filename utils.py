import re

def extract_code_snippet(text, context_lines=5):
    """
    Extract code snippet with enhanced context awareness.
    
    Args:
        text (str): The source code text to analyze
        context_lines (int): Number of context lines to include before and after
        
    Returns:
        str: Extracted code snippet with context
    """
    lines = text.split('\n')
    total_lines = len(lines)
    
    # Enhanced pattern matching for code structures
    code_patterns = {
        'function': r'^\s*(def|function)\s+\w+\s*\(',
        'class': r'^\s*class\s+\w+',
        'method': r'^\s*\w+\s*:\s*function',
        'variable': r'^\s*(var|let|const)\s+\w+\s*=',
        'decorator': r'^\s*@\w+',
        'import': r'^\s*(import|from)\s+\w+',
    }
    
    # Find the most relevant line with enhanced detection
    relevant_line_idx = 0
    for idx, line in enumerate(lines):
        if any(re.match(pattern, line) for pattern in code_patterns.values()):
            relevant_line_idx = idx
            # If this is a decorator, include the following function/class
            if re.match(code_patterns['decorator'], line) and idx + 1 < total_lines:
                for next_idx in range(idx + 1, min(idx + 4, total_lines)):
                    if any(re.match(pattern, lines[next_idx]) for pattern in 
                          [code_patterns['function'], code_patterns['class']]):
                        relevant_line_idx = next_idx
def analyze_code_structure(code, language='python'):
    """
    Analyze code structure and identify documentation needs.
    
    Args:
        code (str): The source code to analyze
        language (str): Programming language of the code
        
    Returns:
        dict: Analysis results including documentation suggestions
    """
    analysis = {
        'functions': [],
        'classes': [],
        'needs_documentation': [],
        'has_documentation': []
    }
    
    lines = code.split('\n')
    current_item = None
    
    for idx, line in enumerate(lines):
        # Check for function definitions
        if re.match(r'^\s*(def|function)\s+\w+\s*\(', line):
            name = re.search(r'(def|function)\s+(\w+)', line).group(2)
            has_docstring = False
            
            # Check for docstring in next lines
            if idx + 1 < len(lines):
                next_lines = '\n'.join(lines[idx+1:idx+4])
                has_docstring = '"""' in next_lines or "'''" in next_lines
            
            item = {'name': name, 'line': idx + 1, 'has_documentation': has_docstring}
            analysis['functions'].append(item)
            
            if not has_docstring:
                analysis['needs_documentation'].append(f"Function: {name}")
            else:
                analysis['has_documentation'].append(f"Function: {name}")
                
        # Check for class definitions
        elif re.match(r'^\s*class\s+\w+', line):
            name = re.search(r'class\s+(\w+)', line).group(1)
            has_docstring = False
            
            # Check for docstring in next lines
            if idx + 1 < len(lines):
                next_lines = '\n'.join(lines[idx+1:idx+4])
                has_docstring = '"""' in next_lines or "'''" in next_lines
            
            item = {'name': name, 'line': idx + 1, 'has_documentation': has_docstring}
            analysis['classes'].append(item)
            
            if not has_docstring:
                analysis['needs_documentation'].append(f"Class: {name}")
            else:
                analysis['has_documentation'].append(f"Class: {name}")
    
    return analysis
                        break
            break
    
    # Calculate enhanced context range
    start_idx = max(0, relevant_line_idx - context_lines)
    end_idx = min(total_lines, relevant_line_idx + context_lines + 1)
    
    # Adjust range to include complete code blocks
    while start_idx > 0 and re.match(r'^\s+', lines[start_idx]):
        start_idx -= 1
    while end_idx < total_lines and re.match(r'^\s+', lines[end_idx - 1]):
        end_idx += 1
        
    return '\n'.join(lines[start_idx:end_idx])

def get_file_language(file_extension):
    """Return the programming language based on file extension."""
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.h': 'cpp',
        '.cs': 'csharp',
        '.rb': 'ruby',
        '.go': 'go'
    }
    return extension_map.get(file_extension.lower(), 'text')

def format_code_for_display(code, language):
    """Format code for display with syntax highlighting."""
    return f"