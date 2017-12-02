""" ===========================================================================
File   : ast.py
CSC410 : Project 6: Program Normalizer and Control Flow Graph Visualizer
Author : Harman Sran

Defines AST class that is While Program
=========================================================================== """
from lib import *


""" ======================================================================= """
""" ================== CLASSES/ PRIVATE FUNCTIONS ========================= """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Define an AST (Abstract Syntax Tree) for While Programs
--------------------------------------------------------------------------- '''
class AST():
    def __init__(self, value):
        self._id = str(nextNodeID()); # unique; set once
        self._left     = None
        self._right    = None
        self._value    = value

    def getID(self):
        return self._id

    def getLeft(self):
        return self._left

    def getRight(self):
        return self._right

    def getValue(self):
        return self._value

    def setLeft(self, ast):
        self._left = ast

    def setRight(self, ast):
        self._right = ast

    def __str__(self, depth=0):
        ret = ""

        # Print right AST
        if self._right != None:
            ret += self._right.__str__(depth + 1)

        # Print own value
        ret += "\n" + ("         "*depth) + str(self._value)

        # Print left AST
        if self._left != None:
            ret += self._left.__str__(depth + 1)

        return ret

''' ---------------------------------------------------------------------------
Return flattened string of while program defined in file at path f
--------------------------------------------------------------------------- '''
def _flatten(path):
    return ''.join(open(path, 'r').read().split())

''' ---------------------------------------------------------------------------
Return AST object defined by well-formed while program in while_str
--------------------------------------------------------------------------- '''
def _generate_AST(wp):
    val = header(wp)

    # LOOP(STMT)
    if (val == LOOP):
        ast = AST(val)
        ast.setLeft(_generate_AST(body(wp)))
    
    # AMB(LSTMT, RSTMT) / SEQ(LSTMT, RSTMT)
    elif (val in [AMB, SEQ]):
        ast = AST(val)
        ast.setLeft(_generate_AST(lbody(wp)))
        ast.setRight(_generate_AST(rbody(wp)))

    # ASSUME(EXPR)
    elif (val == ASSUME):
        ast = AST(val)
        ast.setLeft(_EXPR_to_AST(body(wp)))

    # ASSIGN(VAR, EXPR)
    elif (val == ASSIGN):
        ast = AST(val)
        ast.setLeft(_EXPR_to_AST(lbody(wp)))
        ast.setRight(_EXPR_to_AST(rbody(wp)))

    else:
        raise ValueError("Encountered unsupported atom: " + val)

    return ast


''' ---------------------------------------------------------------------------
Return AST object defined by well-formed expression (e.g. a==b)
--------------------------------------------------------------------------- '''
def _EXPR_to_AST(expr):

    # Check if it's just NOT
    if (header(expr) == NOT):
        ast = AST(header(expr))
        ast.setLeft(_EXPR_to_AST(body(expr)))
        return ast

    # Try splitting by all BI_EXPRS; MUST BE A SIMPLE EXPRESSION (e.g. a==b)
    for bexp in BI_EXPRS:
        sides = expr.split(bexp)
        if (len(sides) == 2):
            ast = AST(bexp)
            ast.setLeft(_EXPR_to_AST(sides[0]))
            ast.setRight(_EXPR_to_AST(sides[1]))
            return ast
    
    return AST(expr) # Constant or TRUE/ FALSE


""" ======================================================================= """
""" ================== PUBLIC INTERFACE =================================== """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Given ASSIGN AST; return assignment string "VAR = EXPR" 
--------------------------------------------------------------------------- '''
def get_assignment_stmt(ast):
    assert ast.getValue() == ASSIGN

    var      = ast.getLeft()
    expr_ast = ast.getRight()
    expr     = expr_ast.getValue()

    # ASSIGN(a, ...)
    ret      = var.getValue() + " = "

    if expr == NOT:
        # ASSIGN(a, NOT(b))
        return ret + expr + "(" + expr_ast.getLeft().getValue() + ")"

    elif expr in BI_EXPRS:
        # ASSIGN(a, b == c)
        return ret + "(" + expr_ast.getLeft().getValue() + " " + expr + " " + expr_ast.getRight().getValue() + ")"

    # ASSIGN(a, b | TRUE | FALSE)
    return ret + expr

''' ---------------------------------------------------------------------------
Given ASSUME AST; return assignment string "VAR = EXPR" 
--------------------------------------------------------------------------- '''
def get_assumption_stmt(ast):
    assert ast.getValue() in [ASSUME, NOT]

    expr_ast = ast.getLeft()
    expr     = expr_ast.getValue() 

    if expr == NOT:
        # ASSUME(NOT(...)) <=> NOT(ASSUME(...))
        return expr + "(" + get_assumption_stmt(expr_ast) + ")"

    elif expr in BI_EXPRS:
        # Sub expressions a,b (e.g. a == b) must be atomic
        # ... (e.g. { NOT(a) == b } should be rewritten to { a != b })
        return expr_ast.getLeft().getValue() + " " + expr + " " + expr_ast.getRight().getValue() 

    return expr # TRUE | FALSE | Boolean var

''' ---------------------------------------------------------------------------
Return AST of while program defined in file at path f
--------------------------------------------------------------------------- '''
def get_AST(path):
    resetNodeID() # Ensure unique node ID for each node
    return _generate_AST(_flatten(path))

''' ---------------------------------------------------------------------------
Validates AST generation by printing AST string and tree (rotated 90 ccw).
--------------------------------------------------------------------------- '''
def test_AST_generation(ast_files):
    print("\nBeginning AST test; all AST file paths must be relative to ast.py")
    for ast_path in ast_files:
        visualize_ast(get_AST(ast_path), \
                      name=ast_path.split("/")[-1].split(".")[0])

        # print("\nTesting AST at path " + ast_path + ":")
        # print(_flatten(ast_path))
        # print("\nGenerated AST (rotated 90 degrees CCW):")
        # print(get_AST(ast_path).__str__())
        # print("\n")

""" ======================================================================= """
""" ================== TESTING ============================================ """
""" ======================================================================= """
if __name__=='__main__':
    test_AST_generation(sample_asts)