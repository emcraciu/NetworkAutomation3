# Module8: Using the subprocess Module

## 1. Introduction

The subprocess module in Python allows you to create and manage
additional processes directly from Python code. It is a powerful tool
for interacting with the operating system, running shell commands, and
handling input/output streams.

Common use cases include:
- Running shell commands
- Automating system administration tasks
- Capturing output from external programs
- Building scripts that integrate with command-line tools

## 2. Requirements
- All code in this module will be executed on remote ubuntu container
- Pycharm integration with container and virtual python environment

## 3. The Basics: subprocess.run()
The simplest way to run a command is by using subprocess.run(). It runs
the command described by args and waits for it to complete.

Example:
```python
import subprocess

result = subprocess.run(['echo', 'Hello World'],
capture_output=True, text=True)
print(result.stdout)
```


Explanation: This will run the \'echo\' command and capture its output.
The \'capture_output=True\' argument tells Python to save the output.
The \'text=True\' argument decodes the result to a string instead of
bytes.

## 4. Capturing Errors

You can also capture standard error output. 
This is useful when commands fail, and you need diagnostic information.

```python
import subprocess

result = subprocess.run(['l', 'non_existent_file'], capture_output=True, text=True)
print('STDOUT:', result.stdout)
print('STDERR', result.stderr)
```

## 5. Using check=True

If you want Python to raise an exception when a command fails, use check=True.

```python
import subprocess

try:
    subprocess.run(['ls', 'non_existent_file'], check=True)
except subprocess.CalledProcessError as e:
    print('Error:', e)
```

## 6. Advanced Usage: subprocess.Popen

The subprocess.Popen class provides more control over input, output, and
errors. It allows you to interact with processes while they are running.

```python
import subprocess

process = subprocess.Popen(['grep', 'hello'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
output, _ = process.communicate('hello world\nPython subprocess module')
print(output)
```

Explanation: Here we create a process running \'grep hello\'. We send
text to its input and capture the matching output.

## 7. Security Considerations

- Avoid using shell=True with untrusted input; it can lead to security vulnerabilities.
- Always prefer passing commands as lists of arguments.
- Validate and sanitize any input passed to subprocess.

## 8. Conclusion

The subprocess module is a versatile tool for managing system processes.
By using subprocess.run() for simple cases and subprocess.Popen for
advanced interaction, you can integrate powerful command-line utilities
into your Python programs safely and effectively.

## 9. References
- Python official documentation: [subprocess](https://docs.python.org/3/library/subprocess.html)
- Real Python: [The subprocess Module](https://realpython.com/python-subprocess/)