import docker
import tempfile
import os
import subprocess
from typing import Optional
import logging
import sys
import asyncio

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

async def call_tool(user_code: str, 
              dependencies: str, 
              language: str = "python",
              docker_image: str = "python:3.11-slim",
              work_dir: Optional[str] = None) -> dict:
    """
    Writes user code to disk and runs it in a Docker container.
    
    Args:
        user_code: The user's program as a string
        language: Programming language (used for file extension)
        docker_image: Docker image to use for execution
        timeout: Maximum execution time in seconds
        work_dir: Optional working directory for the container
    
    Returns:
        dict with 'stdout', 'stderr', 'return_code'
    """
    # Create a temporary file for the code
    file_extension = ".py" if language.lower() == "python" else f".{language}"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix=file_extension, delete=False) as temp_file:
        temp_file.write(user_code)
        temp_file_path = temp_file.name
        temp_dir = os.path.dirname(temp_file_path)
        temp_filename = os.path.basename(temp_file_path)

    logger.info(f"wrote user code to: {temp_file_path}")
    dep_list = dependencies.replace(",", " ")

    try:
        # Initialize Docker client
        client = docker.from_env()

        cmd_str = f"python /app/{temp_filename}"
        if dep_list:
            cmd_str = f"pip install {dep_list} && " + cmd_str
        
        # Create container
        container = client.containers.run(
            docker_image,
            command=f'/bin/bash -c "{cmd_str}"',
            volumes={temp_dir: {'bind': '/app', 'mode': 'ro'}},
            working_dir='/app',
            network_mode = "host",
            remove=True,
            detach=False,
            stdout=True,
            stderr=True,
            mem_limit='4g',      # Security: limit memory
            cpu_quota=20000,       # Security: limit CPU usage
        )

        # Parse output
        output = container.decode('utf-8')
        lines = output.strip()
        logger.info(f"raw output from container: {lines}")

        return [("stdout:", lines)]

    except docker.errors.ContainerError as e:
        return [("stderr:", e.stderr.decode('utf-8'))]

    except docker.errors.NotFound:
        return {
            'stdout': '',
            'stderr': f'Docker image {docker_image} not found',
            'return_code': 1
        }
    except docker.errors.APIError as e:
        return {
            'stdout': '',
            'stderr': f'Docker API error: {str(e)}',
            'return_code': 1
        }
    except subprocess.TimeoutExpired:
        return {
            'stdout': '',
            'stderr': f'Execution timeout after {timeout} seconds',
            'return_code': 124
        }
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass

# Example usage
if __name__ == "__main__":
    sample_code = """
print("Hello from Docker!")
x = 5 + 3
print(f"Calculation: {x}")
"""
    
    result = asyncio.run(call_tool(sample_code))
    print(f"STDOUT: {result}")
