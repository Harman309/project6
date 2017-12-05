""" ===========================================================================
File   : lib.py
CSC410 : Project 6: Program Normalizer and Control Flow Graph Visualizer
Author : Harman Sran

Helper functions for visualizing AST/ CFG and define constant keywords
=========================================================================== """
from io import StringIO
from graphviz import Digraph
import os
import sys


""" ======================================================================= """
""" ==================     MACROS       =================================== """
""" ======================================================================= """

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
EPS    = "E"

# List of expr nodes
EXPRS    = [TRUE, FALSE, NOT, EQ, NEQ, GT, LT, GEQ, LEQ]
BI_EXPRS = [EQ, NEQ, GT, LT, GEQ, LEQ]

AST_NODES = ATOMS + EXPRS

# Special edge types; used for CFG to AST conversion
LOOP_BACK  = "LOOP_BACK_EDGE"
LOOP_ENTRY = "LOOP_ENTRY_EDGE"
AMB_SPLIT  = "AMB_SPLIT_EDGE"
AMB_JOIN   = "AMB_JOIN_EDGE"
SEQ_TRANS  = "SEQ_EDGE"

EDGE_TYPES = [LOOP_BACK, LOOP_ENTRY, AMB_SPLIT, AMB_JOIN, SEQ_TRANS]

""" ======================================================================= """
""" ================== NODE ID HELPER   =================================== """
""" ======================================================================= """

# Global Node ID; used to uniquely identify graph nodes
_g_NID = 0

# Increment global node ID
def increment_global_nodeID():
    global _g_NID
    _g_NID = _g_NID + 1

# Get next global node ID; increment to keep unique
def nextNodeID():
    next_id = _g_NID
    increment_global_nodeID()
    return next_id

# Reset global node ID
def resetNodeID():
    global _g_NID
    _g_NID = 0

""" ======================================================================= """
""" ================== STRING HELPERS   =================================== """
""" ======================================================================= """

# SEQ(...) -> Return "SEQ"
def header(wp):
    return wp.split("(")[0]

# SEQ(...) -> Return "..."
def body(wp):
    return wp[wp.find("(")+1 : wp.rfind(")")]

# Helper for splitting "LSTMT, RSTMT" - *STMT are arbitrarily complex
# From: https://stackoverflow.com/questions/26808913/split-string-at- \
#           commas-except-when-in-bracket-environment
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

""" ======================================================================= """
""" ================== AST VISUALIZATION=================================== """
""" ======================================================================= """
def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

''' ---------------------------------------------------------------------------
Fill dot object with AST node data
--------------------------------------------------------------------------- '''
def ast_to_dot(dot, ast):
    # Add root
    dot.node(ast.getID(), ast.getValue())

    # Add left child to root
    lchild = ast.getLeft()
    if lchild:        
        ast_to_dot(dot, lchild)
        dot.edge(ast.getID(), lchild.getID())

    # Add right child to root
    rchild = ast.getRight()
    if rchild:
        ast_to_dot(dot, rchild)
        dot.edge(ast.getID(), rchild.getID())

''' ---------------------------------------------------------------------------
Use graphViz to render AST and save in folder as name
--------------------------------------------------------------------------- '''
def visualize_ast(ast, name="ast", folder="asts/"):
    # Create folder, and sub-folder for this ast - unless exists
    afolder = folder + name + "/"
    mkdir(folder)
    mkdir(afolder)

    # Generate DOT format graph, given AST
    dot = Digraph(comment=name)
    ast_to_dot(dot, ast)

    # Render graph and save as { folder/name/name.gv; folder/name/name.pdf }
    graph = afolder + name + ".gv"
    dot.render(graph)
    print("\nAST \'" + name + "\' saved to " + graph)

""" ======================================================================= """
""" ================== CFG VISUALIZATION=================================== """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Fill dot object with edge data
--------------------------------------------------------------------------- '''
def populate_dot(dot, edges, show_eps):
    for e in edges:
        dot.edge(e.getSource().getID(), e.getEndpoint().getID(), \
                 # Hide epsilons
                 label= "" if (e.getData() == EPS) and not show_eps else \
                        " " + e.getData() + " ")

''' ---------------------------------------------------------------------------
Use graphViz to render graph cfg and save in folder as name
--------------------------------------------------------------------------- '''
def visualize_cfg(cfg, name="graph", folder="graphs/", \
                  show_epsilons=True, show_node_labels=True):
    # Create folder, and sub-folder for this graph - unless exists
    gfolder = folder + name + "/"
    mkdir(folder)
    mkdir(gfolder)

    # Generate DOT format graph, given cfg's Edge set
    dot = Digraph(comment=name)
    populate_dot(dot, cfg.getEdgeSet(), show_epsilons)

    # Hide node labels
    if not show_node_labels:
        dot.node_attr["label"] = ""

    # Render graph and save as { folder/name/name.gv; folder/name/name.pdf }
    graph = gfolder + name + ".gv"
    dot.render(graph)
    print("\nCFG \'" + name + "\' saved to " + graph)