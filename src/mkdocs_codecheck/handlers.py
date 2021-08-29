import logging
import py_compile
import subprocess
import os

def find_handler( f ):# -> CodeHandler:
    logging.debug(f'Finding handler for {f}')
    if PythonCodeHandler.can_handle( f ):
        #logging.info('Python file found')
        return PythonCodeHandler( f )
    elif PHPCodeHandler.can_handle( f ):
        #logging.info('PHP file found')
        return PHPCodeHandler( f )
    else:
        #logging.info(f"Could not find handler for {f['fn']}")
        raise NoCodeHandler(f'Could not find handler for {f}')

class CodeHandlerException(Exception):
    """Base class for other exceptions"""
    pass
class NoCodeHandler(CodeHandlerException):
    pass
class SyntaxError(CodeHandlerException):
    pass
class RuntimeError(CodeHandlerException):
    pass
class PermissionsError(CodeHandlerException):
    pass
class TimedOutError(CodeHandlerException):
    pass

class CodeHandler:
    language = None
    code_file = None
    def __init__(self, l, f):
        self.data = []
        self.language = l
        self.code_file = f
    def can_handle( f ) -> bool:
        #logging.info(f'Don\'t know how to detect files for {self.language}')
        pass
    def check_syntax( self ):
        #logging.info(f'Don\'t know how to check syntax for {self.language}')
        pass
    def check_runtime( self ):
        #logging.info(f'Don\'t know how to check run time for {self.language}')
        pass

class PythonCodeHandler( CodeHandler ):
    def __init__(self, f):
        super().__init__( 'python', f )
        self.data = []
    def can_handle( f ):
        if f["fn"].name.endswith('.py'):
            return True
        return False
    def check_syntax(self):
        # TODO - capture STDOUT and save full stacktrace to SUMMARY
        super().check_syntax()
        full_path = self.code_file['fn']
        #logging.info(f'Checking python syntax: {full_path}')
        try:
            result = py_compile.compile( full_path, doraise=True )
        except (py_compile.PyCompileError) as e:
            raise SyntaxError(e)
        else:
            return result
    def check_runtime(self):
        # TODO - capture STDOUT and do not output to terminal
        super().check_runtime()
        full_path = self.code_file['fn']
        #logging.info(f'Processing Python file: {full_path}')
        try:
            result = subprocess.run(full_path,timeout=10,check=True)
        except (py_compile.PyCompileError) as e:
            raise SyntaxError(e)
        except subprocess.PermissionError as e:
            raise PermissionsError(e)
        except subprocess.TimeoutExpired as e:
            raise TimedOutError(e)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(e)
        else:
            return result

class PHPCodeHandler( CodeHandler ):
    def __init__(self, f):
        super().__init__( 'php', f )
        self.data = []
    def can_handle( f ):
        if f["fn"].name.endswith('.php'):
            return True
        return False
    def check_syntax(self):
        # TODO - capture STDOUT and save full stacktrace to SUMMARY
        super().check_syntax()
        full_path = self.code_file['fn']
        #logging.info(f'Checking PHP syntax: {full_path}')
        result = subprocess.call(['php','-l',full_path])
        if result != 0:
            raise SyntaxError(f'Syntax error in: {full_path}')
        return result
    def check_runtime(self):
        # TODO - capture STDOUT and do not output to terminal
        super().check_runtime()
        full_path = self.code_file['fn']
        #logging.info(f'Processing PHP file: {full_path}')
        result = subprocess.call(['php',full_path])
        if result != 0:
            raise RuntimeError(r'Error running command: php {full_path}')
        return result


