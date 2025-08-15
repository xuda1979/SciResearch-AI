import asyncio
import docker
import io
import tarfile
from typing import Any

class PythonExecTool:
    """A tool for executing Python code in a sandboxed environment."""

    def __init__(self, timeout: int = 60):
        self.timeout = timeout
        self._docker_client = None

    @property
    def name(self) -> str:
        return "python_exec"

    @property
    def description(self) -> str:
        return "Executes Python code in a sandboxed Docker container."

    async def __call__(self, code: str) -> str:
        """Execute the given Python code and return the output."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._run_code_in_docker, code)

    def _get_docker_client(self):
        if self._docker_client is None:
            self._docker_client = docker.from_env()
            try:
                self._docker_client.images.get("python:3.11")
            except docker.errors.ImageNotFound:
                print("Pulling python:3.11 image...")
                self._docker_client.images.pull("python:3.11")
        return self._docker_client

    def _run_code_in_docker(self, code: str) -> str:
        """Runs the given code in a docker container and returns the output."""
        client = self._get_docker_client()

        script_name = "script.py"
        tarstream = io.BytesIO()
        with tarfile.open(fileobj=tarstream, mode="w") as tar:
            script_bytes = code.encode("utf-8")
            tarinfo = tarfile.TarInfo(name=script_name)
            tarinfo.size = len(script_bytes)
            tar.addfile(tarinfo, io.BytesIO(script_bytes))
        tarstream.seek(0)

        container = client.containers.create(
            "python:3.11",
            command="sleep infinity",
            detach=True,
        )
        try:
            container.start()
            container.put_archive(path="/tmp", data=tarstream.read())
            exec_result = container.exec_run(
                f"python /tmp/{script_name}",
                timeout=self.timeout
            )
            output = exec_result.output.decode("utf-8")
        except Exception as e:
            output = f"An error occurred: {e}"
        finally:
            container.remove(force=True)

        return output
