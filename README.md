# Link Checker for Mkdocs-based static generated sites

Project status: in active development. Not recommended for production use. 

This project was originally conceived at RingCentral to help automate the validation and testing of the code samples contained within its [mkdocs-powered Developer Guide](https://github.com/ringcentral/ringcentral-api-docs/).

## Install

For latest release:

```sh
% python -m pip install mkdocs-codecheck
```

Or, for latest development version.

```sh
% git clone https://github.com/byrnereese/codechecker-mkdocs
% cd codechecker-mkdocs
% python setup.py install 
```

## Usage

### Setting up your environment

Each programming language you will be running tests for will likely have their own unique requirements for executing these tests. For example, to test Java, the `javac` and/or `java` programs will need to be in your path. The following are instructions on how you setup your testing environment for each supported language:

**Python**

Setup a virtual environment for your python code samples. Navigate to your mkdocs-powered repository, and run the following command:

```bash
% pip install venv
% python -m venv .
```

Then activate your virtual environment:

```bash
% source ./bin/activate
```

Finally, consult the documentation associated with the code samples you will be testing, and install any prerequisites or python libraries into this virtual environment that your code samples rely on. 

**PHP**

**Java**

**Ruby**

Not yet supported.

**Javascript**

Not yet supported. 

### How to structure your documentation

A core design requirement for this system to work is that the code samples you wish to embed in your documentation have been fully aabstracted out of the documentation itself. That means that each individual code sample be placed in a dedicated file, and then included or inserted into your documentation when your docs are built. 

In mkdocs, for example, the [mdx_include](https://github.com/neurobin/mdx_include) plugin can be used to insert a code sample located in a separate file. Let's take a look:

    This is my documentation for my developer platform. Here is a simple 
	"Hello World" script you can use to get started:

    ```python
    {!> code-samples/hello-world.py ln:10- !}
    ```

The above code inserts the contents of the `hello-world.py` file into the current markdown file. It inserts the contents of the file starting on line #10. This is done because the first 10 lines contain boilerplate content we don't typically display in our documentation. 

### How to structure a code sample

Each individual code sample must:

* Be contained in its own dedicated file
* Be a fully self-contained, and executable file
* Not require input from the user
* Catch all errors, and return a system exit code greater than 0 to signal to the framework that an error occurred
* Return a system exit code of 0 upon successful completion of the code sample

It is recommended:

* Environment variables be used for passing input into a code sample
* Boilerpate content be added to the top of your code samples to guide others in how to use them

Examples:
* [quick-start.py at RingCentral](https://github.com/ringcentral/ringcentral-api-docs/blob/autotest-code-samples/code-samples/messaging/quick-start.py)

### Ignoring files

Using the same syntax as a `.gitignore` file, you can create a `.codetest-ignore` file to exclude certain files from being tested. This is helpful if you need to exclude node modules, python modules and other libraries from being tested. 

### Running mkdocs-codecheck from within a python script

```python
import mkdocs-codecheck as cc
cc.process_code("~/docs", recurse=True)
```

### Running mkdocs-codecheck from the command-line

This program may be invoked by either:

```sh
mkdocs-codecheck --recurse ~/docs
```

or

```sh
python -m mkdocs-codecheck
```

#### Command link arguments

Usage

> mkdocs-codecheck [-h] [-v] [--dotenv PATH_TO_DOTENV] [--exclude EXCLUDE] [--recurse] path

Positional arguments:

* `path` - root path to code samples

Optional arguments:

* `-h`, `--help` - show a help message and exit
* `--exclude <str>` - a pattern for a file or path to exclude from being checked; use this argument multiple times to exclude multiple files. Regular expressions are ok. 
* `--dotenv <str>` - a fully qualified path to a .env file containing environment variables to source prior to executing code samples
* `--languages <str>` - a comma-delimitted list of languages you will test, e.g. `java`, `php`, `python`, et al.
* `--syntax-only` - do not attempt to run code samples, simply check them for syntax errors only
* `-r`, `--recurse` - recurse through all directories under path
* `-v` or `--verbose` -prints the URLs as they are checked

Example

> mkdocs-codecheck --languages python,php --dotenv ~/.env ~/github/
