from flytekit import task, workflow, Resources, ImageSpec
from flytekit.extras.accelerators import T4

# this exemple covers the following features:
# + build and push image using flyte CLI
# + run a task on a speicific GPU node
# - use sercrets from k8s
# - mount some PVC into a Pod with task
# - run freestyle container

pytorch_image = ImageSpec(
    name="flyte-pytorch",
      python_version="3.10",
      packages=["torch"],
      platform="linux/amd64",
      registry="ghcr.io/nuclear0wl",
  )

if pytorch_image.is_container(): 
  import torch

# gpu access
# https://docs.flyte.org/en/latest/user_guide/productionizing/configuring_access_to_gpus.html
@task(container_image=pytorch_image,
    requests=Resources( gpu="1"), accelerator=T4,
    limits=Resources(mem="2Gi"))
def gpu_available() -> bool:
    return torch.cuda.is_available()

@task()
def print_message(msg: bool) -> str:
    return f"Task was run on GPU: %s" % (msg)

@workflow
def k8s_settings_wf() -> str:
    result = print_message(gpu_available())
    return result

# Run the workflow locally by calling it like a Python function
if __name__ == "__main__":
    print(f"Result of k8s_settings_wf() is {k8s_settings_wf()}")

