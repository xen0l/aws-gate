import hashlib
import os
import platform

from invoke import task


@task
def build_binary(ctx):
    ctx.run("pyinstaller ./aws-gate.spec")


@task
def test_binary(ctx):
    ctx.run("./dist/aws-gate --version")
    ctx.run("./dist/aws-gate --help")


@task
def prepare_binary(ctx):  # pylint: disable=unused-argument
    binary_name = "aws-gate"
    binary_path = f"./dist/{binary_name}"
    platform_suffix = f"{platform.system()}_{platform.machine()}"
    platform_binary_name = f"{binary_name}-{platform_suffix}"
    platform_binary_path = f"{binary_path}-{platform_suffix}"

    os.rename(binary_path, platform_binary_path)

    with open(f"{platform_binary_path}-sha256sum.txt", "w") as h:
        with open(f"{platform_binary_path}", "rb") as f:
            hash = hashlib.sha256(f.read()).hexdigest()
            h.write(f"{hash}  {platform_binary_name}\n")


@task
def clean_binary(ctx):
    ctx.run("rm -vrf ./dist")
