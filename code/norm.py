""" ===========================================================================
File   : norm.py
CSC410 : Project 6: Program Normalizer and Control Flow Graph Visualizer
Author : Harman Sran

Normalizes given AST objects; removes all back edges except 1 by applying 
3 different algorithms for 3 different cases:

Handles Sequential (SEQ), Ambiguous (AMB), and Nested (LOOP) combinations
=========================================================================== """
from lib import *
from ast import *
from cfg import *


""" ======================================================================= """
""" ==================     PRIVATE FUNCTIONS      ========================= """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Scan for sequential back edges in all sub-structures (e.g. in AMBs and LOOPs)
... and reduce to a single back edge per sub-structure
- CFG modified in place
--------------------------------------------------------------------------- '''
def _normalize_seq_cfg(cfg):
    # Traverse until LOOP; save LOOP node and skip to next seq (if available)
    
    # Recursively call _normalize_seq_cfg on encountered AMB/ LOOP bodies (snip to treat
    # as independent sub_structures)

    # On next LOOP node, apply SEQ algorithm

    # Call _normalize_seq_cfg on <post2>
    pass

''' ---------------------------------------------------------------------------
Scan for branching back edges in all sub-structures (e.g. in AMBs and LOOPs)
... and reduce to a single back edge per sub-structure
- CFG modified in place
--------------------------------------------------------------------------- '''
def _normalize_amb_cfg(cfg):
    # Traverse until AMB;

    # Try to get first LOOP on path1 and first LOOP on path2

    # If both paths have LOOPs, apply AMB algorithm

    # If only one path has LOOP; apply seq to that path until only one back edge
    # ... then pull that LOOP out using AMB algorithm

    # Call _normalize_amb_cfg on AMB exit
    pass

''' ---------------------------------------------------------------------------
Scan for nested back edges in all sub-structures (e.g. in AMBs and LOOPs)
... and reduce to a single back edge per sub-structure
- CFG modified in place
--------------------------------------------------------------------------- '''
def _normalize_loop_cfg(cfg):
    # Traverse until LOOP;

    # Traverse inside LOOP until LOOP

    # Apply algorithm

    # Rec call _normalize_loop_cfg on LOOP exit
    pass

''' ---------------------------------------------------------------------------
Return equivalent CFG to given cfg that has at most one back edge
--------------------------------------------------------------------------- '''
def _normalize_cfg(cfg):
    # While there are atleast two backedges do:
    _normalize_seq_cfg(cfg)
    _normalize_amb_cfg(cfg)
    _normalize_loop_cfg(cfg)

""" ======================================================================= """
""" ================== PUBLIC INTERFACE =================================== """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Return normalized AST representation, AST*, of given AST; AST* is equivalent
to given AST except that it has at most one LOOP construct.

Optionally returns normalized CFG
--------------------------------------------------------------------------- '''
def normalize_ast(ast, ret_norm_cfg=False):
    cfg = get_cfg(ast)
    _normalize_cfg(cfg)
    if ret_norm_cfg:
        return to_ast(cfg), cfg
    else:
        return to_ast(cfg)