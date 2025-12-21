## Remaining Code Quality Issues
### Ruff Linting
820	W293  	[ ] blank-line-with-whitespace
226	N806  	[ ] non-lowercase-variable-in-function
197	UP045 	[ ] non-pep604-annotation-optional
187	UP006 	[ ] non-pep585-annotation
185	      	[ ] invalid-syntax
 83	F821  	[ ] undefined-name
 54	F841  	[ ] unused-variable
 50	E402  	[ ] module-import-not-at-top-of-file
 42	N803  	[ ] invalid-argument-name
 26	B007  	[ ] unused-loop-control-variable
 23	B028  	[ ] no-explicit-stacklevel
 21	F401  	[ ] unused-import
 21	SIM102	[ ] collapsible-if
 18	B904  	[ ] raise-without-from-inside-except
 14	F811  	[ ] redefined-while-unused
 13	N802  	[ ] invalid-function-name
 12	W291  	[ ] trailing-whitespace
 10	I001  	[*] unsorted-imports
  9	C401  	[ ] unnecessary-generator-set
  8	SIM108	[ ] if-else-block-instead-of-if-exp
  6	N999  	[ ] invalid-module-name
  4	SIM103	[ ] needless-bool
  3	SIM105	[ ] suppressible-exception
  2	B011  	[ ] assert-false
  2	B017  	[ ] assert-raises-exception
  2	E722  	[ ] bare-except
  2	E731  	[ ] lambda-assignment
  2	N812  	[ ] lowercase-imported-as-non-lowercase
  2	N818  	[ ] error-suffix-on-exception-name
  2	SIM110	[ ] reimplemented-builtin
  2	SIM118	[ ] in-dict-keys
  1	C408  	[ ] unnecessary-collection-call
  1	C416  	[ ] unnecessary-comprehension
  1	E741  	[ ] ambiguous-variable-name
  1	F404  	[ ] late-future-import
  1	N816  	[ ] mixed-case-variable-in-global-scope
  1	SIM115	[ ] open-file-with-context-handler
  1	SIM201	[ ] negate-equal-op
  1	SIM401	[ ] if-else-block-instead-of-dict-get
  1	UP007 	[ ] non-pep604-annotation-union
Found 2057 errors.
[*] 10 fixable with the `--fix` option (1348 hidden fixes can be enabled with the `--unsafe-fixes` option).
### Type Checking (mypy)
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/opt/hostedtoolcache/Python/3.12.12/x64/lib/python3.12/site-packages/mypy/__main__.py", line 9, in <module>
    from mypy.main import main, process_options
  File "mypy/main.py", line 43, in <module>
AttributeError: module 'platform' has no attribute 'python_implementation'
Type checking completed
