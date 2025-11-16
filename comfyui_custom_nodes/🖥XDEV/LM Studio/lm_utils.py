"""LM Studio Shared Utilities

Centralized utilities for all LM Studio nodes to eliminate code duplication.
"""

import json
import re
import subprocess
import urllib.error
import urllib.request
from collections.abc import Callable
from functools import wraps
from typing import Any

# Compile regex patterns once at module level for performance
JSON_PATTERN = re.compile(r'\{.*?\}', re.DOTALL)
JSON_NESTED_PATTERN = re.compile(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', re.DOTALL)


class LMStudioError(Exception):
    """Base exception for LM Studio errors."""
    pass


class LMStudioConnectionError(LMStudioError):
    """Connection-related errors."""
    pass


class LMStudioAPIError(LMStudioError):
    """API response errors."""
    pass


class LMStudioModelError(LMStudioError):
    """Model loading/availability errors."""
    pass


class LMStudioAPIClient:
    """Centralized API communication for LM Studio."""
    
    DEFAULT_TIMEOUT = 60
    VISION_TIMEOUT = 120
    LONG_TIMEOUT = 90
    
    @staticmethod
    def make_request(
        server_url: str,
        endpoint: str,
        payload: dict[str, Any],
        timeout: int = DEFAULT_TIMEOUT
    ) -> dict[str, Any]:
        """Make API request to LM Studio server.
        
        Args:
            server_url: Base server URL (e.g., "http://localhost:1234")
            endpoint: API endpoint (e.g., "/v1/chat/completions")
            payload: Request payload dictionary
            timeout: Request timeout in seconds
            
        Returns:
            API response as dictionary
            
        Raises:
            LMStudioConnectionError: Connection failed
            LMStudioAPIError: Invalid response or API error
        """
        try:
            url = f"{server_url}{endpoint}"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            raise LMStudioAPIError(f"HTTP {e.code}: {error_body}") from e

        except (urllib.error.URLError, ConnectionRefusedError, OSError) as e:
            raise LMStudioConnectionError(f"Cannot connect to {server_url}") from e
            
        except json.JSONDecodeError as e:
            raise LMStudioAPIError("Invalid JSON response from server") from e
    
    @staticmethod
    def get_loaded_models(server_url: str) -> list[dict[str, Any]]:
        """Get list of loaded models from LM Studio.
        
        Args:
            server_url: Base server URL
            
        Returns:
            List of model dictionaries
            
        Raises:
            LMStudioConnectionError: Connection failed
        """
        try:
            url = f"{server_url}/v1/models"
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("data", [])
                
        except Exception as e:
            raise LMStudioConnectionError(f"Cannot fetch models: {str(e)}") from e


class InfoFormatter:
    """Format info outputs consistently across all nodes."""
    
    @staticmethod
    def create_header(title: str, emoji: str = "📝") -> list[str]:
        """Create info output header.
        
        Args:
            title: Node title
            emoji: Emoji prefix
            
        Returns:
            List of header lines
        """
        lines = []
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"{emoji} {title}")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return lines
    
    @staticmethod
    def add_model_info(lines: list[str], loaded_model: str | None, warning: str | None) -> None:
        """Add model loading info.
        
        Args:
            lines: Info lines list to append to
            loaded_model: Name of loaded model or None
            warning: Warning message or None
        """
        if loaded_model:
            lines.append(f"🔵 Model: {loaded_model}")
            if warning:
                print(warning)  # Print warning to console
        else:
            lines.append("⚪ No model loaded")
    
    @staticmethod
    def add_parameters(lines: list[str], params: dict[str, Any]) -> None:
        """Add parameter information.
        
        Args:
            lines: Info lines list to append to
            params: Dictionary of parameter name -> value
        """
        param_emojis = {
            "temperature": "🌡️",
            "max_tokens": "📏",
            "seed": "🎲",
            "format": "📋",
            "response_format": "📋",
            "detail_level": "🔍",
            "blend_ratio": "⚖️",
            "blend_mode": "🎨",
            "control_strength": "💪",
            "region_count": "🔢",
        }
        
        for key, value in params.items():
            emoji = param_emojis.get(key, "⚙️")
            label = key.replace("_", " ").title()
            
            # Format value
            if isinstance(value, float):
                formatted = f"{value:.2f}"
            elif isinstance(value, str):
                formatted = value.upper() if len(value) < 20 else value
            else:
                formatted = str(value)
            
            lines.append(f"{emoji} {label}: {formatted}")
    
    @staticmethod
    def add_completion(lines: list[str], output_text: str, success: bool = True) -> None:
        """Add completion status and statistics.
        
        Args:
            lines: Info lines list to append to
            output_text: Generated output text
            success: Whether generation succeeded
        """
        if success:
            word_count = len(output_text.split())
            char_count = len(output_text)
            lines.append("✅ Generation complete!")
            lines.append(f"📊 Output: ~{word_count} words, {char_count} characters")
        else:
            lines.append("❌ Generation failed")
        
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    @staticmethod
    def format(parts: list[str]) -> str:
        """Join info parts into final string.
        
        Args:
            parts: List of info lines
            
        Returns:
            Joined info string
        """
        return "\n".join(parts)


class OutputFormatter:
    """Format main output text consistently."""
    
    @staticmethod
    def wrap_output(text: str, title: str = "GENERATED TEXT", emoji: str = "🎯") -> str:
        """Wrap output text with header and footer.
        
        Args:
            text: Output text to wrap
            title: Header title
            emoji: Emoji prefix
            
        Returns:
            Formatted output string
        """
        output = f"{'='*50}\n"
        output += f"{emoji} {title}\n"
        output += f"{'='*50}\n\n"
        output += text.strip()
        output += f"\n\n{'='*50}"
        return output


class JSONParser:
    """Parse JSON responses with robust fallback handling."""
    
    @staticmethod
    def parse_response(
        response: str,
        expected_keys: list[str] | None = None,
        nested: bool = False
    ) -> dict[str, Any]:
        """Parse JSON from response with regex fallback.
        
        Args:
            response: Response text potentially containing JSON
            expected_keys: List of keys that should be in the JSON
            nested: Whether to use nested JSON pattern for complex objects
            
        Returns:
            Parsed JSON dictionary or empty dict if parsing fails
        """
        # Try direct JSON parsing first
        try:
            parsed = json.loads(response)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
        
        # Try regex extraction
        pattern = JSON_NESTED_PATTERN if nested else JSON_PATTERN
        match = pattern.search(response)
        if match:
            try:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
        
        # If expected keys provided, try to extract from text
        if expected_keys:
            result = {}
            for key in expected_keys:
                # Look for "key": "value" or key: value patterns
                key_pattern = rf'["\']?{key}["\']?\s*:\s*["\']([^"\']+)["\']'
                key_match = re.search(key_pattern, response, re.IGNORECASE)
                if key_match:
                    result[key] = key_match.group(1)
            
            if result:
                return result
        
        # Return empty dict if all parsing fails
        return {}
    
    @staticmethod
    def extract_field(parsed: dict[str, Any], field: str, default: str = "") -> str:
        """Extract field from parsed JSON with fallback.
        
        Args:
            parsed: Parsed JSON dictionary
            field: Field name to extract
            default: Default value if field not found
            
        Returns:
            Field value or default
        """
        return parsed.get(field, default)


class ErrorFormatter:
    """Format error messages consistently."""
    
    @staticmethod
    def format_connection_error(server_url: str, details: str = "") -> str:
        """Format connection error message.
        
        Args:
            server_url: Server URL that failed
            details: Additional error details
            
        Returns:
            Formatted error message
        """
        msg = "❌ Connection Error\n\n"
        msg += f"Cannot connect to LM Studio at:\n{server_url}\n\n"
        msg += "🔧 Troubleshooting:\n"
        msg += "1. Make sure LM Studio is running\n"
        msg += "2. Check that Local Server is started in LM Studio\n"
        msg += "3. Verify the server URL is correct\n"
        msg += f"4. Try opening in browser: {server_url}/v1/models\n"
        
        if details:
            msg += f"\n\nTechnical details: {details}"
        
        return msg
    
    @staticmethod
    def format_api_error(error_msg: str, http_code: int | None = None) -> str:
        """Format API error message.
        
        Args:
            error_msg: Error message from API
            http_code: HTTP status code if applicable
            
        Returns:
            Formatted error message
        """
        if http_code:
            msg = f"❌ API Error {http_code}\n\n"
        else:
            msg = "❌ API Error\n\n"
        
        msg += f"Server response: {error_msg}\n\n"
        msg += "🔧 Common causes:\n"
        msg += "• No model loaded (load a model in LM Studio)\n"
        msg += "• Model doesn't support the requested operation\n"
        msg += "• Invalid parameters in request\n"
        msg += "• Model still loading (wait and retry)\n"
        
        return msg
    
    @staticmethod
    def format_model_error(details: str = "") -> str:
        """Format model loading error message.
        
        Args:
            details: Additional error details
            
        Returns:
            Formatted error message
        """
        msg = "❌ Model Error\n\n"
        msg += "No model loaded or model not responding.\n\n"
        msg += "🔧 Steps to fix:\n"
        msg += "1. Open LM Studio\n"
        msg += "2. Load a model from the model library\n"
        msg += "3. Start the Local Server (icon in top-right)\n"
        msg += "4. Wait for model to fully load\n"
        msg += "5. Try again\n"
        
        if details:
            msg += f"\n\nDetails: {details}"
        
        return msg


def handle_lmstudio_errors(func: Callable) -> Callable:
    """Decorator to handle LM Studio errors consistently.
    
    Catches common exceptions and formats error messages.
    Returns tuple with error message and info output.
    
    Usage:
        @handle_lmstudio_errors
        def my_node_method(self, ...):
            # method implementation
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract self and server_url from args/kwargs
        server_url = kwargs.get('server_url', 'http://localhost:1234')
        
        try:
            return func(*args, **kwargs)
            
        except LMStudioConnectionError as e:
            error_msg = ErrorFormatter.format_connection_error(server_url, str(e))
            info = "❌ Connection failed - see main output"
            
            # Return appropriate number of empty strings based on function signature
            # Most nodes return (str, str) or (str, str, str)
            return (error_msg, info) if func.__name__ in ['check_model'] else (error_msg, "", info)
            
        except LMStudioAPIError as e:
            error_msg = ErrorFormatter.format_api_error(str(e))
            info = "❌ API error - see main output"
            return (error_msg, "", info)
            
        except LMStudioModelError as e:
            error_msg = ErrorFormatter.format_model_error(str(e))
            info = "❌ Model error - see main output"
            return (error_msg, "", info)
            
        except Exception as e:
            error_msg = f"❌ Unexpected Error\n\n{str(e)}"
            info = f"❌ Error: {str(e)}"
            return (error_msg, "", info)
    
    return wrapper


def build_messages(
    prompt: str,
    system_prompt: str | None = None,
    response_format: str = "text",
    user_input: str | None = None
) -> list[dict[str, str]]:
    """Build messages array for API request.
    
    Args:
        prompt: Main prompt text
        system_prompt: Optional system prompt
        response_format: "text" or "json"
        user_input: Optional additional user input to append
        
    Returns:
        List of message dictionaries
    """
    messages = []
    
    # Add system prompt
    if system_prompt:
        sys_prompt = system_prompt
        if response_format == "json":
            sys_prompt += " Always respond with valid JSON format."
        messages.append({"role": "system", "content": sys_prompt})
    
    # Build user prompt
    user_prompt = prompt
    if user_input:
        user_prompt = f"{prompt}\n\n{user_input}"
    
    messages.append({"role": "user", "content": user_prompt})
    
    return messages


def build_payload(
    messages: list[dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 200,
    response_format: str = "text",
    model: str | None = None,
    seed: int = -1,
    stream: bool = False
) -> dict[str, Any]:
    """Build API request payload.
    
    Args:
        messages: Messages array
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        response_format: "text" or "json"
        model: Model name (optional)
        seed: Random seed (-1 for random)
        stream: Whether to stream responses
        
    Returns:
        Request payload dictionary
    """
    payload = {
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }
    
    # Add JSON format if requested
    if response_format == "json":
        payload["response_format"] = {"type": "json_object"}
    
    # Add optional parameters
    if model:
        payload["model"] = model
    
    if seed >= 0:
        payload["seed"] = seed
    
    return payload


def extract_response_text(result: dict[str, Any]) -> str:
    """Extract generated text from API response.
    
    Args:
        result: API response dictionary
        
    Returns:
        Generated text
        
    Raises:
        LMStudioAPIError: If response format is invalid
    """
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    if not content:
        raise LMStudioAPIError("No response content in API result")
    
    return content.strip()


def run_lms_cli(arguments: list[str], timeout: int = 10) -> tuple[bool, str]:
    """Run the LM Studio CLI and return success flag + output.

    Args:
        arguments: Command arguments to pass after ``lms``.
        timeout: Seconds to wait before aborting the process.

    Returns:
        Tuple of (success, combined_output).

    Raises:
        LMStudioModelError: If the CLI is missing or times out.
    """
    command = ["lms", *arguments]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as err:
        raise LMStudioModelError(
            "lms CLI not found in PATH. Run 'lms bootstrap' from %USERPROFILE%/.lmstudio/bin to install."
        ) from err
    except subprocess.TimeoutExpired as err:
        raise LMStudioModelError("lms CLI command timed out") from err

    output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    return result.returncode == 0, output.strip()


# Lazy import helpers for heavy dependencies
_PIL_Image = None
_numpy = None

def get_pil_image() -> Any:
    """Lazy import PIL.Image."""
    global _PIL_Image
    if _PIL_Image is None:
        from PIL import Image
        _PIL_Image = Image
    return _PIL_Image


def get_numpy() -> Any:
    """Lazy import numpy."""
    global _numpy
    if _numpy is None:
        import numpy as np
        _numpy = np
    return _numpy


__all__ = [
    # Exceptions
    "LMStudioError",
    "LMStudioConnectionError",
    "LMStudioAPIError",
    "LMStudioModelError",
    
    # API Client
    "LMStudioAPIClient",
    
    # Formatters
    "InfoFormatter",
    "OutputFormatter",
    "JSONParser",
    "ErrorFormatter",
    
    # Decorators
    "handle_lmstudio_errors",
    
    # Helpers
    "build_messages",
    "build_payload",
    "extract_response_text",
    "run_lms_cli",
    "get_pil_image",
    "get_numpy",
]
