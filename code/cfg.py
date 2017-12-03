""" ===========================================================================
File   : cfg.py
CSC410 : Project 6: Program Normalizer and Control Flow Graph Visualizer
Author : Michael/ Harman

Defines the CFG class and its components

Provides functionality for converting from an AST (as defined in ast.py)
to a CFG
=========================================================================== """
from lib import *
from ast import *


""" ======================================================================= """
""" ==================      CLASSES               ========================= """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Define an CFG (Control Flow Graph) for While Programs:
    - A wrapper around a singleton Entry and singleton Exit node
    - Forwards and Backwards traversable (entry->exit and also exit->entry)
    - Holds edge set for easy visualization
--------------------------------------------------------------------------- '''
class CFG():
    def __init__(self):
        self._entryNode = None
        self._exitNode  = None
        self._edgeSet   = set() # Complete set of edges in CFG

    def getEntryNode(self):
        return self._entryNode

    def getExitNode(self):
        return self._exitNode

    def getEdgeSet(self):
        return self._edgeSet

    def setEntryNode(self, node):
        self._entryNode = node

    def setExitNode(self, node):
        self._exitNode = node

    def unionEdges(self, edges):
        self._edgeSet = self._edgeSet | edges

''' ---------------------------------------------------------------------------
Define a node in the CFG:
    - A wrapper around sets of Incoming and Outgoing edges
--------------------------------------------------------------------------- '''
class Node():
    def __init__(self, atomic_type=None, exit_node=None):
        self._id = str(nextNodeID()); # unique; set once
        
        # Optionally store atom this node is head for (SEQ, LOOP, AMB, ASSUME, ASSIGN)
        assert atomic_type is None or atomic_type in ATOMS
        self._type = atomic_type

        # Special case for AMB (entry) nodes; store the exit node
        if exit_node is not None:
            assert self._type == AMB
            self._amb_exit = exit_node
        else:
            self._amb_exit = None

        self._incoming = set()
        self._outgoing = set()

    def getID(self):
        return self._id

    def getAMBExit(self):
        assert self.getType() == AMB
        return self._amb_exit

    def getIncomingEdges(self):
        return self._incoming

    def getOutgoingEdges(self):
        return self._outgoing

    def getType(self):
        return self._type

    def addIncomingEdge(self, edge):
        if not isinstance(edge, Edge):
            print("Warning; adding non-edge to incoming set: " + edge.__str__())
        self._incoming.add(edge)

    def addOutgoingEdge(self, edge):
        if not isinstance(edge, Edge):
            print("Warning; adding non-edge to outgoing set: " + edge.__str__())
        self._outgoing.add(edge)

    def delIncomingEdge(self, edge):
        if not isinstance(edge, Edge):
            print("Warning; removing non-edge from incoming set: " + edge.__str__())
        self._incoming.remove(edge)

    def delOutgoingEdge(self, edge):
        if not isinstance(edge, Edge):
            print("Warning; removing non-edge from outgoing set: " + edge.__str__())
        self._outgoing.remove(edge)

    def setType(atomic_type):
        assert atomic_type is None or atomic_type in ATOMS
        self._type = atomic_type 


''' ---------------------------------------------------------------------------
Define a node in the CFG:
    - Contains edge value (e.g. a=b) and references to source/ target nodes
--------------------------------------------------------------------------- '''
class Edge():
    def __init__(self, data, source, endpoint, edge_type=None):
        self._data = data

        # Optionally store special edge type (LOOP_BACK, LOOP_ENTRY, AMB_SPLIT, AMB_JOIN, SEQ_TRANS)
        assert edge_type is None or edge_type in EDGE_TYPES
        self._type = edge_type

        self._source   = source
        self._endpoint = endpoint

    def getType(self):
        return self._type

    def getSource(self):
        return self._source

    def getEndpoint(self):
        return self._endpoint 

    def getData(self):
        return self._data

    def setType(edge_type):
        assert edge_type is None or edge_type in EDGE_TYPES
        self._type = edge_type

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
    epsilonEdge = Edge(EPS, pre.getExitNode(), post.getEntryNode(), SEQ_TRANS)
    pre.getExitNode().addOutgoingEdge(epsilonEdge)
    post.getEntryNode().addIncomingEdge(epsilonEdge)

    # WE DON'T DO THIS BECAUSE pre MIGHT BE A LOOP - e.g. it's exit is a LOOP node
    # Set EXIT of pre as a SEQ type node
    # < pre.getExitNode().setType(SEQ) >

    # Encapsulate sub-CFGs into parent;
    # ... parent's ENTRY is pre's; parent's EXIT is post's 
    cfg.setEntryNode(pre.getEntryNode())
    cfg.setExitNode(post.getExitNode())

    # Set of edges in CFG
    cfg.unionEdges(pre.getEdgeSet() | post.getEdgeSet() | set([epsilonEdge]))

    return cfg

''' ---------------------------------------------------------------------------
Return CFG object corresponding to well-formed ASSIGN AST object

ASSIGN(VAR, EXPR) ==> {  ( ) --- VAR=EXPR --> ( )  }
--------------------------------------------------------------------------- '''
def _generate_ASSIGN_CFG(ast):
    cfg = CFG()
    entryNode = Node(ASSIGN)
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

    # Set of edges in CFG
    cfg.unionEdges(set([edge]))

    return cfg

''' ---------------------------------------------------------------------------
Return CFG object corresponding to well-formed ASSUME AST object

ASSUME(EXPR) ==> {  ( ) --- EXPR --> ( )  }
--------------------------------------------------------------------------- '''
def _generate_ASSUME_CFG(ast):
    cfg = CFG()
    entryNode = Node(ASSUME)
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

    # Set of edges in CFG
    cfg.unionEdges(set([edge]))
    
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
    exitNode  = Node() 
    entryNode = Node(AMB, exitNode)
    
    # Recursively generate the two sub-CFGs for LSTMT and RSTMT
    lcfg = _generate_CFG(ast.getLeft())
    rcfg = _generate_CFG(ast.getRight())

    # Epsilon transitions out from entryNode (x2)
    entryLeftOutEdge  = Edge(EPS, entryNode, lcfg.getEntryNode(), AMB_SPLIT)
    entryRightOutEdge = Edge(EPS, entryNode, rcfg.getEntryNode(), AMB_SPLIT)
    entryNode.addOutgoingEdge(entryLeftOutEdge)
    entryNode.addOutgoingEdge(entryRightOutEdge)
    lcfg.getEntryNode().addIncomingEdge(entryLeftOutEdge)
    rcfg.getEntryNode().addIncomingEdge(entryRightOutEdge)

    # Epsilon transitions in to exitNode (x2)
    exitLeftInEdge  = Edge(EPS, lcfg.getExitNode(), exitNode, AMB_JOIN)
    exitRightInEdge = Edge(EPS, rcfg.getExitNode(), exitNode, AMB_JOIN)
    lcfg.getExitNode().addOutgoingEdge(exitLeftInEdge)
    rcfg.getExitNode().addOutgoingEdge(exitRightInEdge)
    exitNode.addIncomingEdge(exitLeftInEdge)
    exitNode.addIncomingEdge(exitRightInEdge)

    # Encapsulate entry/ exit nodes in CFG, and return
    cfg.setEntryNode(entryNode)
    cfg.setExitNode(exitNode)

    # Set of edges in CFG
    cfg.unionEdges(lcfg.getEdgeSet() | rcfg.getEdgeSet() | set([entryLeftOutEdge,  \
                                                                entryRightOutEdge, \
                                                                exitLeftInEdge,    \
                                                                exitRightInEdge]))

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
    whileNode = Node(LOOP) # Both entry and exit

    # Get CFG that is the body of the LOOP
    body_cfg = _generate_CFG(ast.getLeft())
    
    # Epsilon transition to enter the main LOOP body (from whileNode)
    loopEntryEdge = Edge(EPS, whileNode, body_cfg.getEntryNode(), LOOP_ENTRY)
    whileNode.addOutgoingEdge(loopEntryEdge)
    body_cfg.getEntryNode().addIncomingEdge(loopEntryEdge)

    # Epsilon transition to exit the main LOOP body (back to whileNode)
    loopBackEdge = Edge(EPS, body_cfg.getExitNode(), whileNode, LOOP_BACK)
    body_cfg.getExitNode().addOutgoingEdge(loopBackEdge)
    whileNode.addIncomingEdge(loopBackEdge)

    # Encapsulate entry/ exit nodes in CFG (same), and return
    cfg.setEntryNode(whileNode)
    cfg.setExitNode(whileNode)

    # Set of edges in CFG
    cfg.unionEdges(body_cfg.getEdgeSet() | set([loopEntryEdge, loopBackEdge]))

    return cfg

""" ======================================================================= """
""" ================== PUBLIC INTERFACE =================================== """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Return CFG of while program defined in AST
--------------------------------------------------------------------------- '''
def get_CFG(ast):
    resetNodeID() # Ensure unique node ID for each node
    return _generate_CFG(ast)