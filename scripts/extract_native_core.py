"""Mechanical extraction, with upstream attribution; remove language-only imports.

Arithmetic, verification and response routing are retained verbatim. This avoids
requiring Transformers just to deploy the deterministic service.
"""
import ast
import hashlib
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1])/'compiled_credit_llm/checkpoint'
original=(source/'modeling_compiled_credit_llm.py').read_text()
tree=ast.parse(original)
nodes=[]
for node in tree.body:
    if isinstance(node,ast.ImportFrom) and (node.module=='transformers' or node.level):
        continue
    if isinstance(node,ast.ClassDef) and node.name=='CompiledCreditLLMForConditionalGeneration':
        methods=[m for m in node.body if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)) and m.name!='__init__']
        node=ast.ClassDef(name='CreditEngineMethods',bases=[ast.Attribute(value=ast.Name(id='nn',ctx=ast.Load()),attr='Module',ctx=ast.Load())],keywords=[],body=methods,decorator_list=[])
    nodes.append(node)
result=ast.unparse(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])))
header='# Derived from Javier Mancilla, Qwenderwriter, CC BY-NC 4.0.\n# Source commit 8d6015075d421eb1102db6dcc48a1caa62f84828.\n# Mechanical AST extraction; language superclass and constructor removed.\n'
(ROOT/'creditlab/native_core.py').write_text(header+result+'\n')
(ROOT/'creditlab/routing.py').write_text('# Javier Mancilla, Qwenderwriter, CC BY-NC 4.0; copied for response parity.\n'+(source/'routing.py').read_text())
print('Extracted deterministic core without Transformers imports')
