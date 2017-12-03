""" ===========================================================================
File   : ast.py
CSC410 : Project 6: Program Normalizer and Control Flow Graph Visualizer
Author : Harman Sran

Defines AST class that is While Program

Provides functionality for converting from an CFG (as defined in cfg.py)
to an AST
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
    ast = AST(val)

    # LOOP(STMT)
    if (val == LOOP):
        ast.setLeft(_generate_AST(body(wp)))
    
    # AMB(LSTMT, RSTMT) / SEQ(LSTMT, RSTMT)
    elif (val in [AMB, SEQ]):
        ast.setLeft(_generate_AST(lbody(wp)))
        ast.setRight(_generate_AST(rbody(wp)))

    # ASSUME(EXPR)
    elif (val == ASSUME):
        ast.setLeft(_EXPR_to_AST(body(wp)))

    # ASSIGN(VAR, EXPR)
    elif (val == ASSIGN):
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
Given assignment string "VAR = EXPR"; return ASSIGN AST
--------------------------------------------------------------------------- '''
def get_assignment_ast(stmt):
    ast  = AST(ASSIGN)
    toks = stmt.split(" = ")
    
    var  = toks[0]
    ast.setLeft(_EXPR_to_AST(var))

    expr = toks[1]
    ast.setRight(_EXPR_to_AST(expr))

    return ast

''' ---------------------------------------------------------------------------
Given ASSUME AST; return assumption string "EXPR" 
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
Given assumption string "EXPR"; return ASSUME AST
--------------------------------------------------------------------------- '''
def get_assumption_ast(stmt):
    ast = AST(ASSUME)
    ast.setLeft(_EXPR_to_AST(stmt))
    return ast

''' ---------------------------------------------------------------------------
Return AST of while program defined in file at path f
--------------------------------------------------------------------------- '''
def get_AST(path):
    resetNodeID() # Ensure unique node ID for each node
    return _generate_AST(_flatten(path))