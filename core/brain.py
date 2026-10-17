"""
JARVIS AI Brain
Gemini-powered AI engine with function calling for system control.
"""
import asyncio
import json
import logging
import threading
from typing import Callable, Optional

logger = logging.getLogger("jarvis.brain")


class Brain:
    """Gemini AI engine with function calling."""

    def __init__(self, config, on_response: Callable = None, on_action: Callable = None):
        self.config = config
        self.on_response = on_response    # callback(text: str)
        self.on_action = on_action        # callback(action: str)

        self._client = None
        self._chat = None
        self._tools = []
        self._tool_map = {}
        self._initialized = False

    def initialize(self):
        """Initialize Gemini client and tools."""
        try:
            from google import genai
            from google.genai import types
            from tools.definitions import get_tool_functions

            # Initialize Gemini client
            self._client = genai.Client(api_key=self.config.GEMINI_API_KEY)

            # Get tool functions
            self._tools = get_tool_functions()
            self._tool_map = {fn.__name__: fn for fn in self._tools}

            # Create chat with system prompt and tools
            self._chat = self._client.chats.create(
                model=self.config.GEMINI_MODEL,
                config=types.GenerateContentConfig(
                    system_instruction=self.config.JARVIS_SYSTEM_PROMPT,
                    tools=self._tools,
                    temperature=0.7,
                    max_output_tokens=2048,
                ),
            )

            self._initialized = True
            logger.info("Brain initialized with Gemini and tools.")
            return True

        except Exception as e:
            logger.error(f"Brain initialization failed: {e}")
            return False

    def process_command(self, text: str) -> str:
        """Process a user command through Gemini with function calling.

        Returns the final text response after any tool calls are executed.
        """
        if not self._initialized:
            if not self.initialize():
                return "I'm sorry sir, my AI systems are offline. Please check the API key configuration."

        try:
            response = self._chat.send_message(text)
            return self._handle_response(response)

        except Exception as e:
            logger.error(f"Brain processing error: {e}")
            return f"I encountered an error processing that request: {e}"

    def _handle_response(self, response) -> str:
        """Handle Gemini response, executing any function calls."""
        from google.genai import types

        # Collect all parts
        final_text = ""
        max_iterations = 10  # Prevent infinite loops

        for iteration in range(max_iterations):
            # Check if there are function calls in the response
            has_function_calls = False

            if response.candidates and response.candidates[0].content:
                parts = response.candidates[0].content.parts

                function_responses = []

                for part in parts:
                    if part.function_call:
                        has_function_calls = True
                        fn_call = part.function_call
                        fn_name = fn_call.name
                        fn_args = dict(fn_call.args) if fn_call.args else {}

                        logger.info(f"Executing tool: {fn_name}({fn_args})")

                        if self.on_action:
                            self.on_action(f"Executing: {fn_name}")

                        # Execute the function
                        result = self._execute_tool(fn_name, fn_args)
                        logger.info(f"Tool result: {result[:200]}")

                        function_responses.append(
                            types.Part.from_function_response(
                                name=fn_name,
                                response={"result": result}
                            )
                        )

                    elif part.text:
                        final_text += part.text

                # If we had function calls, send results back to Gemini
                if has_function_calls and function_responses:
                    response = self._chat.send_message(function_responses)
                    continue

            # No more function calls — we're done
            break

        # Extract final text from last response if we looped
        if response.candidates and response.candidates[0].content:
            parts = response.candidates[0].content.parts
            for part in parts:
                if part.text and part.text not in final_text:
                    final_text += part.text

        return final_text.strip() if final_text.strip() else "Done."

    def _execute_tool(self, name: str, args: dict) -> str:
        """Execute a tool function by name."""
        try:
            fn = self._tool_map.get(name)
            if fn is None:
                return f"Unknown tool: {name}"

            result = fn(**args)
            return str(result)
        except Exception as e:
            logger.error(f"Tool execution error ({name}): {e}")
            return f"Error executing {name}: {e}"

    def process_command_async(self, text: str, callback: Callable = None):
        """Process command in background thread."""
        def _run():
            result = self.process_command(text)
            if callback:
                callback(result)
            elif self.on_response:
                self.on_response(result)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
