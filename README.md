# CAAT for Python
Commands as Arrow Types for Python

CAAT provides a way for programs to call each other regardless of the language used as if they were functions.
This is the library for the Python language, it provides the required classes, functions, and variables for calling 
foreign code or for making your scripts callable from foreign code.


## How it works
When you call a foreign command, an environment variable called `CAAT_ARGS` is set with a JSON string that represents the arguments passed into the function. They are also passed in via the command line arguments but this is for legacy reasons. The JSON string gets parsed into a format that the language can understand.
At the same time, the caller opens up a socket at `/tmp/caat_pid` where pid is the pid of the caller process. This is set as the `CAAT_SOCKET` variable which is also passed into the callee. When the callee is done with what it is doing, it should call the function or macro that will write the return value back to the caller. This will also end the program.


## Examples
#### Script 1
```python
import caat

ff = caat.ForiegnFunction('python')

return_value = ff('other.py', 1, [1, 2, 3])

print(return_value)
```

#### Script 2
```python
import caat

caat.return_caat(caat.argv[2])
```

#### Output
```
python script.py
[1, 2, 3]
```
