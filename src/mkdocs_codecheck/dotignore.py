from pathlib import Path
import typing as T
import logging
import re

logging.basicConfig(level=logging.INFO)

class dotignore:
    
    def __init__(self, filename):
        self.rules = []
        self.dotignore_filename = filename

    def read_dotignore( self ):
        """
        This will be throwing something most likely in an error. How do we handle that?
        """
        logging.debug(f'Opening {self.dotignore_filename}')
        with open(self.dotignore_filename) as file:
            lines = file.readlines()
            for line in lines:
                line = line.rstrip()
                logging.debug(f'line: {line}')
                self.rules.append( line )
        return self.rules

    def ignore_file( self, filename ):
        m = re.match( r'^(.+)\/([^\/]+)$', str(filename) )
        path = m.group(1)
        fn = m.group(2)
        logging.debug(f'path={path}, file={fn}')
        for rule in self.rules:
            rule = str(rule)
            logging.debug(f'Checking {fn} against {rule}')
            if re.search( rf"{rule}", str(filename), re.IGNORECASE ):
                logging.debug(f'Ignoring {fn}')
                return True
        return False
        
    def get_files(self, path: Path, recurse: bool = False) -> T.Iterable[Path]:
        """
        yield files in path with suffix ext. Optionally, recurse directories.
        """
        self.read_dotignore()
        path = Path(path).expanduser().resolve()
        if path.is_dir():
            for p in path.iterdir():
                if p.is_file():
                    if self.ignore_file( p ):
                        continue
                    else:
                        yield p
                elif p.is_dir():
                    if recurse:
                        yield from self.get_files(p, recurse)
        elif path.is_file():
            logging.debug(f'Adding file to be checked: {path}')
            yield path
        else:
            raise FileNotFoundError(path)

