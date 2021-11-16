import logging
import py_compile
import subprocess
import os

def rchop(s, suffix):
    if suffix and s.endswith(suffix):
        return s[:-len(suffix)]
    return s

def is_handler_enabled( language ) -> bool:
    if language == 'python' or language == "py":
        return PythonCodeHandler.is_enabled()
    elif language == 'java':
        return JavaCodeHandler.is_enabled()
    elif language == 'php':
        return PHPCodeHandler.is_enabled()
    elif language == 'ruby' or language == "rb":
        return RubyCodeHandler.is_enabled()
    elif language == 'javascript' or language == 'js':
        return JavaScriptCodeHandler.is_enabled()
    elif language == 'c#' or language == 'csharp':
        return CSharpCodeHandler.is_enabled()
    else:
        raise UnknownLanguage(f'Unknown language {language}: cannot process.')

def find_handler( f ):# -> CodeHandler:
    logging.debug(f'Finding handler for {f}')
    if PythonCodeHandler.can_handle( f ):
        #logging.info('Python file found')
        return PythonCodeHandler( f )
    elif PHPCodeHandler.can_handle( f ):
        #logging.info('PHP file found')
        return PHPCodeHandler( f )
    elif JavaCodeHandler.can_handle( f ):
        #logging.info('Java file found')
        return JavaCodeHandler( f )
    elif JavaScriptCodeHandler.can_handle( f ):
        #logging.info('JavaScript file found')
        return JavaScriptCodeHandler( f )
    elif RubyCodeHandler.can_handle( f ):
        #logging.info('Ruby file found')
        return RubyCodeHandler( f )
    elif CSharpCodeHandler.can_handle( f ):
        #logging.info('Ruby file found')
        return CSharpCodeHandler( f )
    else:
        #logging.info(f"Could not find handler for {f['fn']}")
        raise NoCodeHandler(f'Could not find handler for {f}')

class CodeHandlerException(Exception):
    """Base class for other exceptions"""
    pass
class NoCodeHandler(CodeHandlerException):
    pass
class UnknownLanguage(CodeHandlerException):
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
    def is_enabled() -> bool:
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
    def is_enabled():
        return True
    def check_syntax(self):
        # TODO - capture STDOUT and save full stacktrace to SUMMARY
        super().check_syntax()
        full_path = self.code_file['fn']
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
            result = subprocess.run(full_path,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                    universal_newlines=True,timeout=10,
                                    check=False)
        except (py_compile.PyCompileError) as e:
            raise SyntaxError(e)
        except OSError as e:
            raise RuntimeError(e)
        except PermissionError as e:
            raise PermissionsError(e)
        except subprocess.TimeoutExpired as e:
            raise TimedOutError(e, result)
        except subprocess.CalledProcessError as e:
            # This is a controlled failure, meaning the script exited with a status > 0
            raise RuntimeError(e)
        else:
            #logging.info( f'Exiting check_runtime() successfully for {full_path}')
            return result

class PHPCodeHandler( CodeHandler ):
    def __init__(self, f):
        super().__init__( 'php', f )
        self.data = []
    def can_handle( f ):
        if f["fn"].name.endswith('.php'):
            return True
        return False
    def is_enabled():
        try:
            result = subprocess.run(['php','-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    def check_syntax(self):
        # TODO - capture STDOUT and save full stacktrace to SUMMARY
        super().check_syntax()
        full_path = self.code_file['fn']
        result = subprocess.call(['php','-l',full_path])
        if result != 0:
            raise SyntaxError(f'Syntax error in: {full_path}', result)
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

class JavaScriptCodeHandler( CodeHandler ):
    def __init__(self, f):
        super().__init__( 'js', f )
        self.data = []
    def can_handle( f ):
        if f["fn"].name.endswith('.js') or f["fn"].name.endswith('.json'):
            return True
        return False
    def is_enabled():
        try:
            result = subprocess.run(['node','-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    def check_syntax(self):
        # TODO - capture STDOUT and save full stacktrace to SUMMARY
        super().check_syntax()
        full_path = self.code_file['fn']
        result = subprocess.call(['node','--check',full_path])
        if result != 0:
            raise SyntaxError(f'Syntax error in: {full_path}', result)
        return result
    def check_runtime(self):
        # TODO - capture STDOUT and do not output to terminal
        super().check_runtime()
        full_path = self.code_file['fn']
        #logging.info(f'Processing JavaScript file: {full_path}')
        result = subprocess.call(['node',full_path])
        if result != 0:
            raise RuntimeError(r'Error running command: node {full_path}')
        return result

class RubyCodeHandler( CodeHandler ):
    def __init__(self, f):
        super().__init__( 'ruby', f )
        self.data = []
    def can_handle( f ):
        if f["fn"].name.endswith('.rb'):
            return True
        return False
    def is_enabled():
        try:
            result = subprocess.run(['ruby','-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    def check_syntax(self):
        # TODO - capture STDOUT and save full stacktrace to SUMMARY
        super().check_syntax()
        full_path = self.code_file['fn']
        result = subprocess.call(['ruby','-c',full_path])
        if result != 0:
            raise SyntaxError(f'Syntax error in: {full_path}', result)
        return result
    def check_runtime(self):
        # TODO - capture STDOUT and do not output to terminal
        super().check_runtime()
        full_path = self.code_file['fn']
        #logging.info(f'Processing JavaScript file: {full_path}')
        result = subprocess.call(['ruby',full_path])
        if result != 0:
            raise RuntimeError(r'Error running command: ruby {full_path}')
        return result

class JavaCodeHandler( CodeHandler ):
    def __init__(self, f):
        super().__init__( 'java', f )
        self.data = []
    def can_handle( f ):
        if f["fn"].name.endswith('.java'):
            return True
        return False
    def is_enabled():
        try:
            result1 = subprocess.run(['java','--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result2 = subprocess.run(['javac','--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    def check_syntax(self):
        # TODO - capture STDOUT and save full stacktrace to SUMMARY
        super().check_syntax()
        full_path = self.code_file['fn']
        result = subprocess.call(['javac',full_path])
        if result != 0:
            raise SyntaxError(f'Syntax error in: {full_path}', result)
        return result
    def check_runtime(self):
        # TODO - capture STDOUT and do not output to terminal
        super().check_runtime()
        full_path = self.code_file['fn']
        #logging.info(f'Processing Java file: {full_path}')
        #return result

class CSharpCodeHandler( CodeHandler ):
    def __init__(self, f):
        super().__init__( 'csharp', f )
        self.data = []
    def can_handle( f ):
        if f["fn"].name == 'Program.cs':
            return True
        return False
    def is_enabled():
        try:
            result1 = subprocess.run(['dotnet','--info'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    def check_syntax(self):
        # TODO - capture STDOUT and save full stacktrace to SUMMARY
        super().check_syntax()
        full_path = self.code_file['fn']
        prj_dir = rchop(str(full_path), 'Program.cs')
        result = subprocess.call(['dotnet','build',prj_dir])
        if result != 0:
            raise SyntaxError(f'Syntax error in: {full_path}', result)
        return result
    def check_runtime(self):
        # TODO - capture STDOUT and do not output to terminal
        super().check_runtime()
        full_path = self.code_file['fn']
        prj_dir = rchop(str(full_path), 'Program.cs')
        result = subprocess.call(['dotnet','run',prj_dir])
        if result != 0:
            raise RuntimeError(f'Error running project: {prj_dir}', result)
        return result

