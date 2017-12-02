""" ===========================================================================
File   : cfg.py
CSC410 : Project 6: Program Normalizer and Control Flow Graph Visualizer
Author : Michael/ Harman

Defines the CFG class and its components

Provides functionality for converying from an AST (as defined in ast.py)
to a CFG
=========================================================================== """
from lib import *
from ast import *

from sets import Set

#import graphviz as gv #TODO: Need to install


""" ======================================================================= """
""" ==================      CLASSES               ========================= """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Define an CFG (Control Flow Graph) for While Programs:
    - A wrapper around a singleton Entry and singleton Exit node
    - Forwards and Backwards traversable (entry->exit and also exit->entry)
--------------------------------------------------------------------------- '''
class CFG():
    def __init__(self):
        self._entryNode = None
        self._exitNode  = None

    def getEntryNode(self):
        return self._entryNode

    def getExitNode(self):
        return self._exitNode

    def setEntryNode(self, node):
        self._entryNode = node

    def setExitNode(self, node):
        self._exitNode = node

''' ---------------------------------------------------------------------------
Define a node in the CFG:
    - A wrapper around a set of Incoming and a set of Outgoing edges
--------------------------------------------------------------------------- '''
class Node():
    def __init__(self):
        self._incoming  = Set()
        self._outgoing = Set()

    def getIncomingEdges(self):
        return self._incoming # Return private Set, not copy

    def getOutgoingEdges(self):
        return self._outgoing # Return private Set, not copy

    def addIncomingEdge(self, edge):
        if not isinstance(edge, Edge):
            print("Warning; adding non-edge to incoming set: " + edge.__str__())
        self._incoming.add(edge)

    def addOutgoingEdge(self, edge):
        if not isinstance(edge, Edge):
            print("Warning; adding non-edge to outgoing set: " + edge.__str__())
        self._outgoing.add(edge)

''' ---------------------------------------------------------------------------
Define a node in the CFG:
    - Contains edge value (e.g. a=b) and references to source/ target nodes
--------------------------------------------------------------------------- '''
class Edge():
    def __init__(self, data, source, endpoint):
        self._data = data
        self._source = source
        self._endpoint = endpoint

    def getSource(self):
        return self._source

    def getEndpoint(self):
        return self._endpoint 

    def getData(self):
        return self._data

""" ======================================================================= """
""" ==================     PRIVATE FUNCTIONS      ========================= """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Return CFG object corresponding to well-formed AST object
--------------------------------------------------------------------------- '''
def _generate_CFG(ast):
    ast_type = ast.getValue()

    # Only ATOMS supported
    if not (ast_type in ATOMS):
        raise ValueError("Attempt to build CFG for non-atom AST type: " + ast_type)

    # SEQ(LSTMT, RSTMT)
    if ast_type == SEQ:
        cfg = _generate_SEQ_CFG(ast)

    # ASSIGN(VAR, EXPR)
    elif ast_type == ASSIGN:
        cfg = _generate_ASSIGN_CFG(ast)

    # ASSUME(EXPR)
    elif ast_type == ASSUME:
        cfg = _generate_ASSUME_CFG(ast)

    # AMB(LSTMT, RSTMT)
    elif ast_type == AMB:
        cfg = _generate_AMB_CFG(ast)

    # LOOP(STMT)
    elif ast_type == LOOP:
        cfg = _generate_LOOP_CFG(ast)

    else:
        raise ValueError("Attempt to build CFG for unsupported AST atom: " + ast_type)

    return cfg

''' ---------------------------------------------------------------------------
Return CFG object corresponding to well-formed SEQ AST object

- Entry node is entry of CFG(L_AST)
- Exit node is exit of CFG(R_AST)

SEQ(L_AST, R_AST) ==> {  CFG(L_AST) ---Epsilon--> CFG(R_AST)  }
                  ==> {  pre        ---Epsilon-->       post  }
--------------------------------------------------------------------------- '''
def _generate_SEQ_CFG(ast):
    cfg = CFG()

    # Recursively generate the two sub-CFGs
    pre  = _generate_CFG(ast.getLeft())
    post = _generate_CFG(ast.getRight())

    # Add null edge from EXIT of pre, to ENTRY of post
    epsilonEdge = Edge(EPS, pre.getExitNode(), post.getEntryNode())
    pre.getExitNode().addOutgoingEdge(epsilonEdge)
    post.getEntryNode().addIncomingEdge(epsilonEdge)

    # Encapsulate sub-CFGs into parent;
    # ... parent's ENTRY is pre's; parent's EXIT is post's 
    cfg.setEntryNode(pre.getEntryNode())
    cfg.setExitNode(post.getExitNode())

    return cfg

''' ---------------------------------------------------------------------------
Return CFG object corresponding to well-formed ASSIGN AST object

ASSIGN(VAR, EXPR) ==> {  ( ) --- VAR=EXPR --> ( )  }
--------------------------------------------------------------------------- '''
def _generate_ASSIGN_CFG(ast):
    cfg = CFG()
    entryNode = Node()
    exitNode  = Node()

    # Get ASSIGN statement; e.g. VAR = EXPR
    assign_stmt = get_assignment_stmt(ast)
    
    # Generate and set ASSIGN edge
    edge = Edge(assign_stmt, entryNode, exitNode)
    entryNode.addOutgoingEdge(edge)
    exitNode.addIncomingEdge(edge)

    # Encapsulate entry/ exit nodes in CFG, and return
    cfg.setEntryNode(entryNode)
    cfg.setExitNode(exitNode)

    return cfg

''' ---------------------------------------------------------------------------
Return CFG object corresponding to well-formed ASSUME AST object

ASSUME(EXPR) ==> {  ( ) --- EXPR --> ( )  }
--------------------------------------------------------------------------- '''
def _generate_ASSUME_CFG(ast):
    cfg = CFG()
    entryNode = Node()
    exitNode  = Node()

    # Get ASSUME statement; e.g. EXPR
    assume_stmt = get_assumption_stmt(ast)
    
    # Generate and set ASSIGN edge
    edge = Edge(assume_stmt, entryNode, exitNode)
    entryNode.addOutgoingEdge(edge)
    exitNode.addIncomingEdge(edge)

    # Encapsulate entry/ exit nodes in CFG, and return
    cfg.setEntryNode(entryNode)
    cfg.setExitNode(exitNode)
    
    return cfg

''' ---------------------------------------------------------------------------
Return CFG object corresponding to well-formed AMB AST object

AMB(LSTMT, RSTMT) ==> 
                                 -> CFG(LSTMT)
                                /            \
                               E              E
                              /                \
                        {  ( )                 -> ( )  }
                              \               /
                               E             E
                                \           /
                                -> CFG(RSTMT)
--------------------------------------------------------------------------- '''
def _generate_AMB_CFG(ast):
    cfg = CFG()
    entryNode = Node()
    exitNode  = Node() 

    # Recursively generate the two sub-CFGs for LSTMT and RSTMT
    lcfg = _generate_CFG(ast.getLeft())
    rcfg = _generate_CFG(ast.getRight())

    # Epsilon transitions out from entryNode (x2)
    entryLeftOutEdge  = Edge(EPS, entryNode, lcfg.getEntryNode())
    entryRightOutEdge = Edge(EPS, entryNode, rcfg.getEntryNode())
    entryNode.addOutgoingEdge(entryLeftOutEdge)
    entryNode.addOutgoingEdge(entryRightOutEdge)
    lcfg.getEntryNode().addIncomingEdge(entryLeftOutEdge)
    rcfg.getEntryNode().addIncomingEdge(entryRightOutEdge)

    # Epsilon transitions in to exitNode (x2)
    exitLeftInEdge  = Edge(EPS, lcfg.getExitNode(), exitNode)
    exitRightInEdge = Edge(EPS, rcfg.getExitNode(), exitNode)
    lcfg.getExitNode().addOutgoingEdge(exitLeftInEdge)
    rcfg.getExitNode().addOutgoingEdge(exitRightInEdge)
    exitNode.addIncomingEdge(exitLeftInEdge)
    exitNode.addIncomingEdge(exitRightInEdge)

    # Encapsulate entry/ exit nodes in CFG, and return
    cfg.setEntryNode(entryNode)
    cfg.setExitNode(exitNode)

    return cfg

''' ---------------------------------------------------------------------------
Return CFG object corresponding to well-formed LOOP AST object

- ( ) is both entry and exit node

LOOP(STMT) ==> 
                         -> CFG(STMT)
                        /           |
                       E            E  
                      /             |
                {  ( ) <-------------   }
--------------------------------------------------------------------------- '''
def _generate_LOOP_CFG(ast):
    cfg = CFG()
    whileNode = Node() # Both entry and exit

    # Get CFG that is the body of the LOOP
    body_cfg = _generate_CFG(ast.getLeft())
    
    # Epsilon transition to enter the main LOOP body (from whileNode)
    loopEntryEdge = Edge(EPS, whileNode, body_cfg.getEntryNode())
    whileNode.addOutgoingEdge(loopEntryEdge)
    body_cfg.getEntryNode().addIncomingEdge(loopEntryEdge)

    # Epsilon transition to exit the main LOOP body (to whileNode)
    loopExitEdge = Edge(EPS, body_cfg.getExitNode(), whileNode)
    body_cfg.getExitNode().addOutgoingEdge(loopExitEdge)
    whileNode.addIncomingEdge(loopExitEdge)

    # Encapsulate entry/ exit nodes in CFG (same), and return
    cfg.setEntryNode(whileNode)
    cfg.setExitNode(whileNode)

    return cfg

""" ======================================================================= """
""" ================== PUBLIC INTERFACE =================================== """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Return CFG of while program defined in AST
--------------------------------------------------------------------------- '''
def get_CFG(ast):
    return _generate_CFG(ast)

''' ---------------------------------------------------------------------------
Validates AST to CFG conversion by converting all ASTs defined in files to CFGs
and saves resulting CFGs using GraphViz
--------------------------------------------------------------------------- '''
def test_AST_to_CFG_conversion(ast_files):
    print("\nBeginning CFG test; all AST file paths must be relative to ast.py")
    for ast_path in ast_files:
        print("\nTesting AST to CFG conversion for AST at path " + ast_path + ":")
        ast = get_AST(ast_path)
        cfg = get_CFG(ast)
        assert cfg is not None
        print("\nSuccess! TODO: Print out CFG in GraphViz\n")

""" ======================================================================= """
""" ================== TESTING ============================================ """
""" ======================================================================= """
if __name__=='__main__':
    test_AST_to_CFG_conversion(sample_asts)