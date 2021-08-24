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
% pip install -e codechecker-mkdocs
```

## Usage

### How to structure your documentation

A core design requirement for this system to work is that the code samples you wish to embed in your documentation have been fully aabstracted out of the documentation itself. That means that each individual code sample be placed in a dedicated file, and then included or inserted into your documentation when your docs are built. 

In mkdocs, for example, the [mdx_include](https://github.com/neurobin/mdx_include) plugin can be used to insert a code sample located in a separate file. Let's take a look:

```markdown
This is my documentation for my developer platform. Here is a simple "Hello World"
script you can use to get started:

    ```python
	{!> code-samples/hello-world.py ln:10- !}
	```
```

### How to structure a code sample



### Ignoring files

Using the same syntax as a `.gitignore` file, you can create a `.codetest-ignore` file to exclude certain files from being tested. This is helpful if you need to exclude node modules, python modules and other libraries from being tested. 

### Python code

```python
import mkdocs-codecheck as cc
cc.process_code("~/docs", recurse=True)
```

### Command-line

This program may be invoked by either:

```sh
mkdocs-codecheck
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
* `--exclude str` - a pattern for a file or path to exclude from being checked; use this argument multiple times to exclude multiple files. Regular expressions are ok. 
* `--dotenv str` - a fully qualified path to a .env file containing environment variables to source prior to executing code samples
* `-r`, `--recurse` - recurse through all directories under path
* `-v` or `--verbose` -prints the URLs as they are checked

Example

> mkdocs-codecheck ~/github/
