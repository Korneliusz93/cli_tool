# Copilot Instructions for Linux CLI Utilities

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a Python-based command line utilities project designed for openSUSE Linux. The project focuses on creating helpful CLI tools that integrate with typical Linux commands.

## Guidelines
- Use Python 3.8+ features and best practices
- Follow PEP 8 style guidelines
- Integrate with Linux system commands using subprocess
- Use argparse for command line argument parsing
- Include proper error handling and logging
- Write utilities that are useful for system administration and daily Linux tasks
- Use pathlib for file system operations
- Include unit tests for all utilities
- Follow Unix philosophy: do one thing well

## Code Style
- Use type hints for function parameters and return values
- Use dataclasses for configuration objects
- Prefer subprocess.run() over os.system() for executing Linux commands
- Use logging instead of print statements for debugging
- Handle permissions and file system errors gracefully
