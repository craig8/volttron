import docker

client = docker.from_env()

container = client.containers.run('mysql', detach=True, auto_remove=True,
                                  ports={3306:3306}, environment={'MYSQL_ROOT_PASSWORD': 'test'})

print(container.id)