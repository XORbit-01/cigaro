import subprocess


class ToolAbstract:
    def __init__(self, name: str, path: str, *args):
        self._rules = {}
        self.args = args
        self.path = path
        self.name = name
        self._process: subprocess.Popen = None
        self._exit_code = None
        self._results = None
        self._stdout = None
        self._stderr = None

    def start(self):
        if self._process is None:
            self._process = subprocess.Popen(
                [self.path, *self.args],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        else:
            raise RuntimeError("Process already started")

    @property
    def stdout(self):
        if self._stdout is None:
            raise RuntimeError("Process not finished or started")
        return self._stdout

    @property
    def stderr(self):
        if self._stderr is None:
            raise RuntimeError("Process not finished or started")
        return self._stderr

    @property
    def exit_code(self):
        if self._exit_code is None:
            raise RuntimeError("Process not finished")
        return self._exit_code

    def _parse_implicit_rules(self):
        self._results = {}
        for method in dir(self.__class__):
            if method.endswith("_rule"):
                self.rule_register(method[:-5], getattr(self, method))

    def rule_register(self, name: str, rule):
        self._rules[name] = rule

    def generate_results(self):
        for rule in self._rules:
            self._results[rule] = self._rules[rule](self._stdout)

    def compile_results(self):
        for rule in self._results:
            setattr(self, rule + "_result", self._results[rule])

    def _on_exit(self):
        self._stdout, self._stderr = self._process.communicate()
        self._stdout = self._stdout.decode()
        self._stderr = self._stderr.decode()
        self._parse_implicit_rules()
        self.generate_results()
        self.compile_results()

    def wait(self):
        if self._process is not None:
            self._exit_code = self._process.wait()
            self._on_exit()
        else:
            raise RuntimeError("Process not started")

    def terminate(self):
        if self._process is not None:
            self._process.terminate()
            self._on_exit()
        else:
            raise RuntimeError("Process not started")

    def kill(self):
        if self._process is not None:
            self._process.kill()
            self._on_exit()
        else:
            raise RuntimeError("Process not started")

    def on_end(self):
        self._on_exit()


import subprocess
import asyncio


class ToolAbstractAsync:
    def __init__(self, name: str, path: str, *args):
        self._rules = {}
        self.args = args
        self.path = path
        self.name = name
        self._process: subprocess.Popen = None
        self._exit_code = None
        self._results = None
        self._stdout = None
        self._stderr = None

    async def start(self):
        if self._process is None:
            self._process = await asyncio.create_subprocess_exec(
                self.path, *self.args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        else:
            raise RuntimeError("Process already started")

    @property
    def stdout(self):
        if self._stdout is None:
            raise RuntimeError("Process not finished or started")
        return self._stdout

    @property
    def stderr(self):
        if self._stderr is None:
            raise RuntimeError("Process not finished or started")
        return self._stderr

    @property
    def exit_code(self):
        if self._exit_code is None:
            raise RuntimeError("Process not finished")
        return self._exit_code

    def _parse_implicit_rules(self):
        self._results = {}
        for method in dir(self.__class__):
            if method.endswith("_rule"):
                self.rule_register(method[:-5], getattr(self, method))

    def rule_register(self, name: str, rule):
        self._rules[name] = rule

    def generate_results(self):
        for rule in self._rules:
            self._results[rule] = self._rules[rule](self._stdout)

    def compile_results(self):
        for rule in self._results:
            setattr(self, rule + "_result", self._results[rule])

    async def _on_exit(self):
        self._stdout, self._stderr = await self._process.communicate()
        self._stdout = self._stdout.decode()
        self._stderr = self._stderr.decode()
        self._parse_implicit_rules()
        self.generate_results()
        self.compile_results()

    async def wait(self):
        if self._process is not None:
            self._exit_code = await self._process.wait()
            await self._on_exit()
        else:
            raise RuntimeError("Process not started")

    async def terminate(self):
        if self._process is not None:
            self._process.terminate()
            await self._on_exit()
        else:
            raise RuntimeError("Process not started")

    async def kill(self):
        if self._process is not None:
            self._process.kill()
            await self._on_exit()
        else:
            raise RuntimeError("Process not started")

    async def on_end(self):
        await self._on_exit()
