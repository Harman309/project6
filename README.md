# CSC410: Project 6:
## Program Normalizer and Control Flow Graph Visualizer

## Usage
- Python 3 required (tested with Python 3.6.3); Python 2.* not supported
- Add AST files to test in sample/
- Add sample files to sample_asts list in lib.py
- Test all components together, by running (optional flag 'e' for epsilon labels; and flag 'n' for node labels):
> python3 test.py en
- Follow output to retrieve results
- Successive tests in test.py repeat prior tests for completeness; comment out prior tests to not generate intermediate files (e.g. remove all but normalization test to just compute and visualize the normalized WHILE programs)

## Implementation
- All required components are implemented
- Component 5 has some limitations on a few edge cases:
    - A single LOOP on one AMB branch, but none on the other may cause unexpected behaviour
    - A nesting deeper than two LOOPs at a time may cause unexpected behaviour; to work-around this, re-run twice
- Core functionality of Component 5 (for each case) is demonstrated in samples/


## Team
- Michael Li
- Harman Sran
- Ryan Downes
- Joey Ding

### Component -1
- ast.txt -> AST object
- Handled by ast.py

### Component 1
- AST object -> CFG object
- Handled by cfg.py

### Component 3 and 4
- CFG object -> AST object
- Handled by conv.py

### Component 5
- AST object -> AST* object
- Handled by norm.py

### Component 6
- Visualize CFG (and AST) object
- Handled by lib.py

### Validate
- Test all components
- Handled by test.py