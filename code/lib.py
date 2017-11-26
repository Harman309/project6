""" ===========================================================================
File   : lib.py
CSC410 : Project 6: Program Normalizer and Control Flow Graph Visualizer
Author : Harman Sran

Helper functions for visualizing CFG and define constant keywords
=========================================================================== """
import StringIO

# Atomic grammar nodes
SEQ    = "SEQ"
LOOP   = "LOOP"
AMB    = "AMB"
ASSUME = "ASSUME"
ASSIGN = "ASSIGN"

# List the atomic nodes
ATOMS  = [SEQ, LOOP, AMB, ASSUME, ASSIGN]

# Expressions
TRUE   = "TRUE"
FALSE  = "FALSE"
NOT    = "NOT"
EQ     = "=="
NEQ    = "!="
GT     = ">"
LT     = "<"
GEQ    = ">="
LEQ    = "<="

# Epsilon transition
EPS    = "epsilon_transition"

# List of expr nodes
EXPRS    = [TRUE, FALSE, NOT, EQ, NEQ, GT, LT, GEQ, LEQ]
BI_EXPRS = [EQ, NEQ, GT, LT, GEQ, LEQ]

AST_NODES = ATOMS + EXPRS


# STRING HELPERS

# SEQ(...) -> Return "SEQ"
def header(wp):
    return wp.split("(")[0]

# SEQ(...) -> Return "..."
def body(wp):
    return wp[wp.find("(")+1 : wp.rfind(")")]

# Helper for splitting "LSTMT, RSTMT" - *STMT are arbitrarily complex
# From: https://stackoverflow.com/questions/26808913/split-string-at-commas-except-when-in-bracket-environment
def stmt_split(body):
    parts = []
    bracket_level = 0
    current = []
    # trick to remove special-case of trailing chars
    for c in (body + ","):
        if c == "," and bracket_level == 0:
            parts.append("".join(current))
            current = []
        else:
            if c == "(":
                bracket_level += 1
            elif c == ")":
                bracket_level -= 1
            current.append(c)
    return parts

# SEQ(LSTMT, RSTMT) -> Return LSTMT
def lbody(wp):
    return stmt_split(body(wp))[0]

# SEQ(LSTMT, RSTMT) -> Return RSTMT
def rbody(wp):
    return stmt_split(body(wp))[1]