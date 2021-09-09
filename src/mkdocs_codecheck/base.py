from __future__ import annotations
from pathlib import Path
import typing as T
import logging
import re
import os
from operator import itemgetter
import py_compile
import subprocess

from . import handlers
from . import dotignore

class bcolors:
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC      = '\033[0m'

# http://www.useragentstring.com
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0"
SUMMARY = {
    'total': 0,
    'passed': 0,
    'checked': 0,
    'checked_syntax': 0,
    'checked_runtime': 0,
    'errors': 0,
    'errors_syntax': 0,
    'errors_runtime': 0,
    'skipped': 0,
    'problems': {},
    'failure': False
    }

STATUS_LABELS = {
    'passed':     '✓',
    'permission': '✖',
    'syntax':     '✖',
    'skipped':    '/',
    'error':      '⚠'
}

def print_summary( root_path ):
    print(f'SUMMARY')
    print(f'       Total files: {SUMMARY["total"]}')
    print(f'     Syntax checks: {SUMMARY["checked_syntax"]}')
    print(f'  Files NOT tested: {SUMMARY["skipped"]}')
    print(f'      Files passed: {SUMMARY["passed"]}')
    print(f'ERRORS')
    print(f'     Syntax errors: {SUMMARY["errors_syntax"]}')
    print(f'   Run-time errors: {SUMMARY["errors_runtime"]}')

    for file_path in SUMMARY['problems']:
        problem = SUMMARY['problems'][file_path]
        rel_file_path = relative_path( root_path, file_path )
        p_msg = problem['msg']
        p_type = problem['type']
        print(f'\n{bcolors.OKBLUE}{rel_file_path}{bcolors.ENDC}')
        print(f'[{STATUS_LABELS[p_type]}] {p_msg}')

def relative_path( root_path, file_path ) -> str:
    cur_dir_name = str( root_path ).rpartition('/')[2]
    rfp = './' + cur_dir_name + str(file_path).replace( str(root_path), '' )
    return rfp
        
#def ignore_file( fn ) -> bool:
#    # TODO - switch to an .ignore-file file mechanism
#    e = r'^(__init__.py|.*\~|\..*)$'
#    regex = re.compile(e)
#    if regex.search( fn.name ):
#        logging.debug(f'Ignore {fn.name}? Yes.')
#        return True
#    logging.debug(f'Ignore {fn.name}? No.')
#    return False

def append_problem(fn, msg, t):
    #logging.info( fn )
    SUMMARY['problems'][fn["fn"]] = { 'msg': msg, 'type': t }    

def process_code(
        path: Path,
        recurse: bool = False,
        exclude: [str] = None,
        syntax_only: bool = False,
        languages: [str] = None
) -> bool:
    bad = False
    code_files = find_code_samples( path, recurse=recurse, exclude=exclude )
    root_path = None

    logging.debug(f'Processing languages: {languages}')
    for f in code_files:
        full_path = f["fn"].name
        root_path = f["path"]
        SUMMARY['total'] += 1
        logging.debug(f'{SUMMARY["total"]}. Processing {full_path}')
        # This should not be necessary as the dotignore file should be used instead
        #ignore = ignore_file( f["fn"] )
        #logging.debug(f'  {SUMMARY["total"]}. Exclude? {ignore}')
        #if ignore:
        #    continue

        try:
            handler = handlers.find_handler( f )
            logging.debug(f'  {SUMMARY["total"]}. {full_path} is type {handler.language}')
            skip = (languages != None and str(handler.language) not in languages)
            logging.debug(f'  {SUMMARY["total"]}. Skip this file? {skip} (is {handler.language} in {languages})')
            if skip:
                logging.debug(f'  {SUMMARY["total"]}. Skipping language for {handler.language}')
                continue
            else:
                logging.debug(f'  {SUMMARY["total"]}. Checking syntax for {full_path}')  
                SUMMARY['checked_syntax'] += 1
                handler.check_syntax()
                if not syntax_only: 
                    logging.debug(f'  {SUMMARY["total"]}. Executing {full_path}')
                    SUMMARY['checked_runtime'] += 1
                    result = handler.check_runtime()
                    if result.returncode > 0:
                        #logging.info( f'handler.check_runtime() FAILED for {full_path}' )
                        #logging.info( f'   stderr: {result.stderr}' )
                        #logging.info( f'   stdout: {result.stdout}' )
                        #if re.search( r'429 Client Error', result.stderr ):
                        #    logging.info( f'Rate limit error possibly detected.' )
                        append_problem( f, result.stderr, "error" )
                        SUMMARY['errors'] += 1
                        SUMMARY['errors_runtime'] += 1
                    else:
                        #logging.info( f'handler.check_runtime() succeeded. stdout: {result.stdout}' )
                        SUMMARY['passed'] += 1
        except handlers.NoCodeHandler as e:
            logging.debug(f'  {SUMMARY["total"]}. No handler found for: {f["fn"].name}')
            SUMMARY['skipped'] += 1
        except handlers.SyntaxError as e:
            logging.debug(f'  {SUMMARY["total"]}. There is a syntax problem with the file.')
            append_problem( f, f'Syntax error: {e}', 'syntax' )
            SUMMARY['errors_syntax'] += 1
        except handlers.PermissionsError as e:
            logging.debug(f'  {SUMMARY["total"]}. The file is not executable.')
            append_problem( f, "Not executable.", "permission" )
            SUMMARY['errors'] += 1
            SUMMARY['errors_runtime'] += 1
        except handlers.TimedOutError as e:
            logging.debug(f'  {SUMMARY["total"]}. Process took too long to run.')
            append_problem( f, 'Timed out.', 'error' )
            SUMMARY['errors'] += 1
            SUMMARY['errors_runtime'] += 1
        except handlers.RuntimeError as e:
            logging.debug(f'  {SUMMARY["total"]}. The script ({full_path}) exited with an error status code')
            append_problem( f, f'Error executing script: {e}', 'error' )
            SUMMARY['errors'] += 1
            SUMMARY['errors_runtime'] += 1
            
    if SUMMARY['errors'] > 0: bad = True
    print_summary( root_path )
    return bad

def exclude_file( link, exclude ) -> bool:
    for e in exclude:
        regex = re.compile(e)
        if regex.search( link ):
            return True
    return False

def find_code_samples( path: Path, recurse: bool, exclude: [] = None
                  ) -> tuple[ T.Iterable, T.Iterable ]:
    path = Path(path).resolve().expanduser()  # must have .resolve()
    # these look for local and relative links only
    # markdown regex to extract links from [Link label](link url)
    code_samples = []
    di = dotignore.dotignore('.codecheck-ignore')
    for fn in di.get_files(path, recurse):
        #full_path = os.path.join( path, fn.name )
        if os.path.isfile( fn ):
            #logging.debug(f'{fn} is a file')
            code_samples.append( {
                'fn': fn,
                'path': path } )
    return code_samples
                
