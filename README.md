# Cigar 
<p align=center>
<image src="https://github.com/Malwarize/cigaro/assets/130087473/8c69f0d7-c4b2-4937-bf38-7593a7ecb8fa" />
</p>
<h2 align=center>wrapper framework for any command line tool</h2> 


# Installation
```bash
pip install cigaro
```

# How to use
### 1. Create Tool module for your command line tool
the tool module should have a class that inherits from `cigar.ToolAbstract`
```python
# modules.py
# create a class that inherits from ToolAbstract
from cigaro.AbstractTool import ToolAbstract
class Hydra(ToolAbstract):
    def __init__(self, target: str, user: str, wordlist: str, protocol: str):
        path = "/usr/bin/hydra"
        super().__init__(path, "hydra", "-l", user, "-P", wordlist, target, protocol, "-t", "4")
    
    # define rules for parsing the output
    @staticmethod
    def password_rule(output):
        lines = output.splitlines()
        i = 0
        for line in lines:
            if "login:" in line:
                line_to_select: str = lines[i + 1]
                return line_to_select.split(" ")[1]
            i += 1
    
    @staticmethod
    def username_rule(output):
        lines = output.splitlines()
        i = 0
        for line in lines:
            if "login:" in line:
                line_to_select: str = lines[i + 1]
                return line_to_select.split(" ")[0]
            i += 1

    @property
    def username(self):
        return self.username_result

    @property
    def password(self):
        return self.password_result

    def on_end(self):
        return super().on_end()
```

### 2. what is rule?
rule is a function that takes the output of the command line tool and returns the result you want to get from the output
#### how to define a rule?
* implicitly
the implicit definition of a rule function must end with `_rule` and must be static
```python
@staticmethod
def password_rule(output):
    lines = output.splitlines()
    i = 0
    for line in lines:
        if "login:" in line:
            line_to_select: str = lines[i + 1]
            return line_to_select.split(" ")[1]
        i += 1
```
* explicitly
the explicit definition of a rule must override the `on_end` using self.rule_register(rule_name, rule_function)
```python
from cigaro.AbstractTool import ToolAbstract


class NmapLite(ToolAbstract):
    def __init__(self, tport: str, target: str):
        super().__init__("nmap", "-p", tport, target)
        self.rule_register("state", self.state_rule_explicit)

    @staticmethod  # added in explicit rule definition
    def state_rule_explicit(out):
        lines = out.splitlines()
        i = 0
        for line in lines:
            if "PORT" in line:
                line_to_select: str = lines[i + 1]
                return line_to_select.split(" ")[1]
            i += 1

    # implicit rule definition
    @staticmethod
    def service_rule(out):
        lines = out.splitlines()
        i = 0
        for line in lines:
            if "PORT" in line:
                line_to_select: str = lines[i + 1]
                return line_to_select.split(" ")[2]
            i += 1

    @staticmethod
    def port_rule(out):
        lines = out.splitlines()
        i = 0
        for line in lines:
            if "PORT" in line:
                line_to_select: str = lines[i + 1]
                return line_to_select.split(" ")[0]
            i += 1
    @staticmethod
    def portr(out):
        pass
    @property
    def port_r(self):
        return self.port_result

    @property
    def state_r(self):
        return self.state_result

    @property
    def service_r(self):
        return self.service_result

    def on_end(self):
        self.rule_register("state", self.state_rule_explicit)
        return super().on_end()
```

### how to get the result?
you should to define a property, this property should return the result of the rule
the return variable should be named `rule_name` + `_result`
```python
@property
def username(self):
    return self.username_result
```

### 3. how to use the tool module?

```python
from yourmodule import Hydra

hydra = Hydra(
    "localhost",
    "admin",
    "wordlist.txt",
    "ssh"
)
hydra.start()
hydra.wait()

print(hydra.username)
print(hydra.password)
```


### Async Support
example on webpalm tool
[webpalm](github.com/Malwarize/webpalm)
```python
import json
import shutil

from cigaro.AbstractTool import ToolAbstractAsync


class WebPalmAsync(ToolAbstractAsync):
    def __init__(self, target: str, level: int):
        name = "webpalm"
        path = shutil.which("webpalm", path="/home/xorbit/go/bin")
        super().__init__(name, path, "-u", target, "-l", str(level), "-o", "/tmp/web_palm_output.json")

    @staticmethod
    def urls_rule(_):
        with open("/tmp/web_palm_output.json", "r") as f:
            urls = json.load(f)
        return urls

    @property
    def urls(self):
        return self.urls_result
```

### 4. how to use the tool module async?
```python
from yourmodule import WebPalmAsync
webpalm = WebPalmAsync("https://google.com", 1)
await webpalm.start()
await webpalm.wait()
print(webpalm.urls)
```
