from ipykernel.kernelapp import IPKernelApp
from . import SetlXKernel

if __name__ == '__main__':
    IPKernelApp.launch_instance(kernel_class=SetlXKernel)