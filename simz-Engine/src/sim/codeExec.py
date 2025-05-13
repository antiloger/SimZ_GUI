from src.sim.sim_types import RunnerFile
from typing import Any, Callable, Dict, Optional
import ast
import inspect
import os


class CodeExec:
    def __init__(self, code: RunnerFile, im_Comp, im_Gen):
        self.run = ""
        self.model = ""
        self.generator = ""
        self.event = ""
        self._run_namespace = {}
        self.run_funcs = []
        self._generator_namespace = {}
        self.generator_funcs = []
        self._model_namespace = {}
        self._model_funcs = []
        self._event_namespace = {}
        self.event_funcs = []
        # Import dependencies once
        self._default_imports = {
            "Component": im_Comp,
            "GenContainer": im_Gen,
            "os": os,
            # Add any other required imports here
        }
        self.load(code)

    def load(self, code: RunnerFile):
        """Load and execute the code components into namespaces"""
        self.run = code.run
        self.model = code.model
        self.generator = code.generator
        self.event = code.event

        # Process each component
        if self.run:
            self._run_namespace = self._prepare_code(self.run)
            self.run_funcs = extract_function_names(self.run)

        if self.generator:
            self._generator_namespace = self._prepare_code(self.generator)
            self.generator_funcs = extract_function_names(self.generator)
        #
        # if self.model:
        #     self._model_namespace = self._prepare_code(self.model)
        #     self._model_funcs = extract_function_names(self.model)
        #
        if self.event:
            self._event_namespace = self._prepare_code(self.event)
            self.event_funcs = extract_function_names(self.event)

    def _prepare_code(self, code_str: str):
        """Validate syntax and execute code in a new namespace"""
        try:
            # First validate syntax
            ast.parse(code_str)

            # Create namespace with common imports
            namespace = self._default_imports.copy()

            # Execute code directly in the namespace
            exec(code_str, namespace)
            return namespace
        except SyntaxError as e:
            print(f"Syntax error in code: {e}")
            return {}
        except Exception as e:
            print(f"Error executing code: {e}")
            return {}

    # def execute_run(self, component, input_data):
    #     """Execute the run function with the specified signature"""
    #     return self._execute_simulation_function(
    #         "run", self._run_namespace, component, input_data
    #     )
    #
    # def execute_generator(self, component):
    #     """Execute the generator function with the specified signature"""
    #     return self._execute_simulation_function(
    #         "generate_data", self._generator_namespace, component
    #     )
    #
    # def execute_model(self, component, input_data):
    #     """Execute the model function with the specified signature"""
    #     return self._execute_simulation_function(
    #         "process_model", self._model_namespace, component, input_data
    #     )
    #
    # def execute_event(self, component, input_data):
    #     """Execute the event function with the specified signature"""
    #     return self._execute_simulation_function(
    #         "handle_event", self._event_namespace, component, input_data
    #     )

    def execute_test(self, data):
        try:
            # First validate syntax
            ast.parse(self.run)

            # Create namespace with common imports
            namespace = {
                "os": os,
            }

            # Execute code directly in the namespace
            exec(self.run, namespace)

            func = namespace.get("run")
            if not callable(func):
                print("Error:  is not callable")
                return None
            func(data)

        except SyntaxError as e:
            print(f"Syntax error in code: {e}")
            return {}
        except Exception as e:
            print(f"Error executing code: {e}")
            return {}

    def execute_function(
        self,
        func_name: str,
        namespace: Dict[str, Any],
    ):
        """Execute a simulation function with the standard signature"""
        if func_name not in namespace:
            print(f"Error: '{func_name}' function not found in the code")
            return None

        func = namespace[func_name]

        if not callable(func):
            print(f"Error: '{func_name}' is not callable")
            return None

        return func
        # try:
        #     result = func(component, input_data)
        #
        #     # Handle generator functions (those that use 'yield')
        #     if inspect.isgeneratorfunction(func):
        #         return result  # Return the generator object for the caller to iterate
        #     else:
        #         return result  # Return the normal function result
        # except Exception as e:
        #     print(f"Error calling {func_name} function: {e}")
        #     return None

    def execute_run_function(
        self,
        func_name: str,
    ) -> Optional[Callable]:
        """Execute a simulation function with the standard signature"""
        # Use consistent _generator_namespace with underscore
        if func_name not in self._run_namespace:
            print(f"Error: '{func_name}' function not found in the generator code")
            return None

        func = self._run_namespace[func_name]

        if not callable(func):
            print(f"Error: '{func_name}' is not callable")
            return None

        # Check if it's a generator function
        if not inspect.isgeneratorfunction(func):
            print(
                f"Warning: '{func_name}' is not a generator function but is expected to be one"
            )
            # Not returning None here as it might still work in some cases

        return func

    def execute_genCustom_function(
        self,
        func_name: str,
    ) -> Optional[Callable]:
        """Execute a simulation function with the standard signature"""

        # Use consistent _generator_namespace with underscore
        if func_name not in self._generator_namespace:
            print(f"Error: '{func_name}' function not found in the generator code")
            return None

        func = self._generator_namespace[func_name]

        if not callable(func):
            print(f"Error: '{func_name}' is not callable")
            return None

        # Check if it's a generator function
        if not inspect.isgeneratorfunction(func):
            print(
                f"Warning: '{func_name}' is not a generator function but is expected to be one"
            )
            # Not returning None here as it might still work in some cases

        return func

    def execute_gen_function(
        self,
    ) -> Optional[Callable]:
        """Execute a simulation function with the standard signature"""
        func_name = "generate"

        # Use consistent _generator_namespace with underscore
        if func_name not in self._generator_namespace:
            print(f"[NAMESPACE] ?? {self._generator_namespace}")
            print(f"Error: '{func_name}' function not found in the generator code")
            return None

        func = self._generator_namespace[func_name]

        if not callable(func):
            print(f"Error: '{func_name}' is not callable")
            return None

        # Check if it's a generator function
        if not inspect.isgeneratorfunction(func):
            print(
                f"Warning: '{func_name}' is not a generator function but is expected to be one"
            )
            # Not returning None here as it might still work in some cases

        return func

    def execute_event_function(
        self,
        func_name: str,
    ) -> Optional[Callable]:
        """Execute a function from the event namespace"""
        if not self.event or func_name not in self._event_namespace:
            return None

        func = self._event_namespace[func_name]

        if not callable(func):
            print(f"Error: '{func_name}' is not callable")
            return None

        return func


def extract_function_names(code_str):
    """Extract function names from a string of Python code"""
    if not code_str:
        return []

    try:
        # Parse the code string
        tree = ast.parse(code_str)

        # Find all function definitions
        function_names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_names.append(node.name)

        return function_names
    except SyntaxError:
        print("Syntax error in code")
        return []
    except Exception as e:
        print(f"Error parsing code: {e}")
        return []
