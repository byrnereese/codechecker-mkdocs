import logging
import py_compile
import subprocess
import os

def find_handler( f ):# -> CodeHandler:
    logging.debug(f'Finding handler for {f}')
    if PythonCodeHandler.can_handle( f ):
        logging.debug('Python file found')
        return PythonCodeHandler( f )
    raise NoCodeHandler(f'Could not find handler for {f}')

class CodeHandlerError(Exception):
    """Base class for other exceptions"""
    pass

class NoCodeHandler(CodeHandlerError):
    pass

class CodeHandler:
    type = None
    code_file = None
    def __init__(self, t, f):
        self.data = []
        self.type = t
        self.code_file = f
    def can_handle( f ) -> bool:
        #logging.info(f'Don\'t know how to detect files for {self.type}')
        pass
    def check_syntax( self ):
        #logging.info(f'Don\'t know how to check syntax for {self.type}')
        pass
    def check_runtime( self ):
        #logging.info(f'Don\'t know how to check run time for {self.type}')
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
        logging.debug(f'Checking python syntax: {full_path}')
        return py_compile.compile( full_path, doraise=True )
    def check_runtime(self):
        # TODO - capture STDOUT and do not output to terminal
        super().check_runtime()
        full_path = self.code_file['fn']
        logging.debug(f'Processing Python file: {full_path}')
        #client_id = os.environ.get('RC_CLIENT_ID')
        #logging.info(f'Environment var RC_CLIENT_ID={client_id}')
        return subprocess.run(full_path,timeout=10,check=True)
    

