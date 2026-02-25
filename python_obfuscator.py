import ast
import random
import string
import base64
#made by modelguyzz
def obfuscate_script(source_code: str) -> str:
    """
    Obfuscates Python source code with:
    Variable and function renaming
    String encryption (Base64)
    Dead code injection
    Polymorphic output (randomized each call)
    """
    # Helper: Generate random variable/function names
    def random_name(length=6):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    # made by modelguyzz
    # Step 1: Parse source code to AST
    tree = ast.parse(source_code)
    
    # Step 2: Collect variable and function names
    class NameCollector(ast.NodeVisitor):
        def __init__(self):
            self.names = set()
        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Store) or isinstance(node.ctx, ast.Load):
                self.names.add(node.id)
        def visit_FunctionDef(self, node):
            self.names.add(node.name)
            self.generic_visit(node)
    
    collector = NameCollector()
    collector.visit(tree)
    
    # Step 3: Build name mapping
    name_map = {name: random_name(random.randint(3, 10)) for name in collector.names}
    
    # Step 4: AST Transformer for renaming and string encryption
    class Obfuscator(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id in name_map:
                node.id = name_map[node.id]
            return node
        
        def visit_FunctionDef(self, node):
            if node.name in name_map:
                node.name = name_map[node.name]
            self.generic_visit(node)
            return node
        
        def visit_Str(self, node):
            # Encrypt string using base64
            encoded = base64.b64encode(node.s.encode("utf-8")).decode("utf-8")
            return ast.Call(
                func=ast.Name(id='_decode_string', ctx=ast.Load()),
                args=[ast.Constant(value=encoded)],
                keywords=[]
            )
    # made by modelguyzz
    obfuscator = Obfuscator()
    tree = obfuscator.visit(tree)
    ast.fix_missing_locations(tree)
    
    # Step 5: Dead code injection
    dead_code_snippets = [
        "if False:\n    x = 12345\n",
        "y = 0\nfor _ in range(0): y += 1\n",
        "z = 'dummy' + 'code'\n",
        "import math\nmath.sqrt(0)\n"
    ]
    dead_code = random.choice(dead_code_snippets)
    
    # Step 6: Build final source code with string decoder and dead code
    final_code = f"""
import base64
{dead_code}
def _decode_string(s):
    return base64.b64decode(s).decode('utf-8')

"""
    final_code += ast.unparse(tree)
    return final_code
