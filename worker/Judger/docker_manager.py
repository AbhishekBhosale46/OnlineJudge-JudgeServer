import docker


class DockerManager:

    """
    DockerManager handles Docker operations such as building images and creating containers.
    """

    def __init__(self, time_limit, memory_limit, judger_vol_path):
        """
        Initializes DockerManager with the Docker client.
        """

        self.client = docker.from_env()
        self.image_name = "judger-runtime-img"
        self.container_name = "judger-runtime-cnt"
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.judger_vol_path = judger_vol_path

    def get_container(self):
        """
        Create a new container or return a running container

        Returns:
        - container
        """

        try:
            container = self.client.containers.get(self.container_name)
        except docker.errors.NotFound:
            try:
                image = self.client.images.get(self.image_name)
                container = self.client.containers.run(
                    image=image.id,
                    name=self.container_name,
                    detach=True,
                    tty=True,
                    volumes={self.judger_vol_path: {'bind': '/workspace', 'mode': 'rw'}},
                    mem_limit=f'{self.memory_limit}m',
                    network_disabled=True,
                    read_only=True,
                    stderr=True,
                    stdout=True,
                    user='nobody',
                )
            except docker.errors.ImageNotFound:
                image, logs = self.client.images.build(
                    path="./judger_dockerfile/", tag=self.image_name, forcerm=True)
                container = self.client.containers.run(
                    image=image.id,
                    name=self.container_name,
                    detach=True,
                    tty=True,
                    volumes={self.judger_vol_path: {'bind': '/workspace', 'mode': 'rw'}},
                    mem_limit=f'{self.memory_limit}m',
                    network_disabled=True,
                    read_only=True,
                    stderr=True,
                    stdout=True,
                    stdin_open=True,
                    user='nobody'
                )

        container.start()
        return container
