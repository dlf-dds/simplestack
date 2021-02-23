clean-python:				##@b--utils clean up proj tree (python)
	@find . -name /*.pyc -delete
	@find . -name __pycache__ | xargs rm -rf
	@find . -name '*egg-info' | xargs rm -rf
	@find . -name '.cache' | xargs rm -rf
	@find . -name '.build' | xargs rm -rf
	@find . -name '*.log' | xargs rm -rf
	@find . -name '*.log*' | xargs rm -rf
	@find . -name '*.coverage' | xargs rm -rf
	@find . -name 'coverage.xml' | xargs rm -rf	
	@find . -name '*pytest_cache' | xargs rm -rf			
	@rm -rf ./htmlcov/
	@rm -rf ./prof/
	@rm -rf ./pytest_cache/
	@rm -rf */.pytest_cache/
	@rm -rf ./build/
	@rm -rf ./dist/
	@rm -rf ./.mypy_cache/	
