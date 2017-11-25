""" ===========================================================================
File   : ast.py
CSC410 : Project 6: Program Normalizer and Control Flow Graph Visualizer
Author : Harman Sran

Defines AST class that is While Program
=========================================================================== """
import sys
from lib import *


""" ======================================================================= """
""" ================== PRIVATE CLASSES/ FUNCTIONS ========================= """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Define an AST
--------------------------------------------------------------------------- '''
class AST():
    def __init__(self, value):
        self._left     = None
        self._right    = None
        self._value    = value
        self._isExpr   = value in EXPRS

    def getLeft(self):
        return self._left

    def getRight(self):
        return self._right

    def getValue(self):
        return self._value

    def isExpr(self):
        return self._isExpr

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

    print("AST for: " + val)

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
        #ast.setLeft(lbody(wp))
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
Return flattened string of while program defined in file at path f
--------------------------------------------------------------------------- '''
def get_AST(path):
    return _generate_AST(_flatten(path))


""" ======================================================================= """
""" ================== TESTING ============================================ """
""" ======================================================================= """
# if __name__=='__main__':
#     print("")
#     print(_flatten("../samples/if.txt"))
#     print("")
#     print("")
#     ast = get_AST("../samples/if.txt")
#     print(ast.__str__())
#     print("")
#     print("")
#     print("")
#     print("")
#     print(_flatten("../samples/while.txt"))
#     print("")
#     print("")
#     ast = get_AST("../samples/while.txt")
#     print(ast.__str__())
#     print("")
