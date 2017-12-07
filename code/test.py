""" ===========================================================================
File   : test.py
CSC410 : Project 6: Program Normalizer and Control Flow Graph Visualizer
Author : Harman Sran

Tests functionality of:
- Component -1   :  Constructing AST objects
- Component  1   :  Converting AST objects to equivalent CFG objects
- Component  3+4 :  Converting CFG objects to equivalent AST objects
- Component  5   :  Normalizing AST objects
- Component  6   :  Visualizing CFG (and AST) objects with GV
=========================================================================== """
from lib import *
from ast import *
from cfg import *
from conv import *
from norm import *

# ADD SAMPLE ASTs TO THIS LIST FOR AUTO-TESTING IN 'test.py'
# IMPORTANT: File path must be relative to this dir (code/)
sample_asts = ["../samples/if.txt", \
               "../samples/while.txt", \
               "../samples/if_NOT.txt", \
               "../samples/seqwhile.txt", \
               "../samples/nestedwhile.txt", \
               "../samples/ambwhile.txt"]
               

''' ---------------------------------------------------------------------------
Validates AST generation by visualizing using GV
--------------------------------------------------------------------------- '''
def test_AST_generation(ast_files):
    print("\nBeginning AST generation test [Component -1].")
    for ast_path in ast_files:
        visualize_ast(get_AST(ast_path), \
                      name=ast_path.split("/")[-1].split(".")[0])

''' ---------------------------------------------------------------------------
Validates AST to CFG conversion by converting all ASTs defined in files to CFGs
and saves resulting CFGs using GraphViz for visualization
--------------------------------------------------------------------------- '''
def test_AST_to_CFG_conversion(ast_files, show_epsilons, show_node_labels):
    print("\nBeginning AST to CFG conversion test [Component 1].")
    for ast_path in ast_files:
        ast = get_AST(ast_path)
        visualize_cfg(get_CFG(ast), \
                      name=ast_path.split("/")[-1].split(".")[0], \
                      show_epsilons=show_epsilons, \
                      show_node_labels=show_node_labels)

''' ---------------------------------------------------------------------------
Validates CFG to AST conversion by converting all ASTs defined in files to CFGs
and then converts the CFGs to ASTs (from scratch), and saves resulting ASTs 
using GraphViz for visualization
--------------------------------------------------------------------------- '''
def test_CFG_to_AST_conversion(ast_files):
    print("\nBeginning CFG to AST conversion test [Components 3 and 4]")
    for ast_path in ast_files:
        ast = get_AST(ast_path)
        cfg = get_CFG(ast)
        visualize_ast(to_ast(cfg), \
                      name=ast_path.split("/")[-1].split(".")[0], \
                      folder="conv_asts/")

''' ---------------------------------------------------------------------------
Validates AST normalization by normalizing (removing all but one back edge)
of all ASTs passed in
--------------------------------------------------------------------------- '''
def test_AST_normalization(ast_files):
    print("\nBeginning AST normalization test [Component 5]")
    for ast_path in ast_files:
        ast = get_AST(ast_path)
        n_ast, n_cfg = normalize_ast(ast, ret_norm_cfg=True)
        visualize_cfg(n_cfg, \
               name=ast_path.split("/")[-1].split(".")[0], \
               folder="norm_cfgs/", \
               show_epsilons=show_epsilons, \
               show_node_labels=show_node_labels)
        visualize_ast(n_ast, \
                      name=ast_path.split("/")[-1].split(".")[0], \
                      folder="norm_asts/")
        print("")

# Run tests to validate component functionality
if __name__=='__main__':

    ''' SET UP '''
    if len(sys.argv) > 2:
        print("Usage: > python3 test.py [en]\n" + \
              "         -e : CFG: Label empty transitions\n" + \
              "         -n : CFG: Label nodes")
        exit()
    show_epsilons   = False
    show_node_labels = False
    if len(sys.argv) == 2:
        show_epsilons   = "e" in sys.argv[1]
        show_node_labels = "n" in sys.argv[1]

    print("\n========== Beginning Program Normalizer and AST/ CFG Visualizer Tests ==========")
    print("\nBuilt with Python 3.63 and Windows GV installation; Python 2.* not supported.")
    print("\nNote that all AST file paths (in test.py) should be relative to test.py!")
    print("\nShowing epsilons    (enable by passing <e>): " + str(show_epsilons))
    print("\nShowing node labels (enable by passing <n>): " + str(show_node_labels))
    print("\n================================================================================")

    ''' Successive tests will re-test the functionality of previous tests -
        so if intermediate results are not desired, comment all but the last '''
    # Component -1
    test_AST_generation(sample_asts)
    print("\n================================================================================")

    # Component 1
    test_AST_to_CFG_conversion(sample_asts, show_epsilons, show_node_labels)
    print("\n================================================================================")

    # Component 3 and 4
    test_CFG_to_AST_conversion(sample_asts)
    print("\n================================================================================")

    # Component 5
    test_AST_normalization(sample_asts)
    print("\n================================================================================")
    
    # Component 6 tested in all the above