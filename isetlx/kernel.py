from ipykernel.kernelbase import Kernel
import re
import queue
import subprocess
import threading


def enqueue_stream(stream, queue, err):
    while True:
        c = stream.read(1)
        queue.put((err, c))
    stream.close()


class ProcessHandler:    
    def __init__(self):
        self.p = subprocess.Popen(['setlX', '-h'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        self.q = queue.Queue()
        self.to = threading.Thread(target=enqueue_stream,
                                   args=(self.p.stdout, self.q, False))
        self.te = threading.Thread(target=enqueue_stream,
                                   args=(self.p.stderr, self.q, True))
        self.te.start()
        self.to.start()
        # skip initial greeting
        self.forward_response(None, True)
    
    def forward_response(self, kernel, silent=False):
        err_out = b''
        out = b''
        d_out = {'name': 'stdout', 'text': ''}
        d_err_out = {'name': 'stderr', 'text': ''}
        while True:
            try:
                err, c = self.q.get(timeout=0.2)
                if err:
                    err_out += c
                else:
                    out += c
            except:
                pass

            if out == b'=>':
                break
            
            if b'\n' in out:
                if not silent:
                    d_out['text'] = out.decode('utf-8')
                    if d_out['text'].strip() != '':
                        kernel.send_response(kernel.iopub_socket, 'stream', d_out)
                out = b''

            if b'\n' in err_out:
                if not silent:
                    d_err_out['text'] = err_out.decode('utf-8')
                    kernel.send_response(kernel.iopub_socket, 'stream', d_err_out)
                err_out = b''


def cell_to_cmd(string):
    # remove all multi-line comments (/*COMMENT */) from string
    string = re.sub(re.compile('/\*.*?\*/',re.DOTALL ), '', string)
    # remove all single-line comments (//COMMENT\n ) from string
    string = re.sub(re.compile('//.*?\n' ), '', string)
    return (string.strip().replace('\n', ' ') + '\n').encode("utf-8")


class SetlXKernel(Kernel):
    implementation = 'iSetlX'
    implementation_version = '1.0'
    language = 'SetlX'
    language_version = '2.7.2'
    # alternative syntax highlighting: https://codemirror.net/mode/index.html
    language_info = {
        'name': 'SetlX',
        'mimetype': 'text/setlx',
        'codemirror_mode': 'text/x-java',
        'file_extension': '.stlx',
    }
    banner = "iSetlX Kernel"
    
    p_handler = None
    
    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        if SetlXKernel.p_handler is None:
            SetlXKernel.p_handler = ProcessHandler()
        SetlXKernel.p_handler.p.stdin.write(cell_to_cmd(code))
        SetlXKernel.p_handler.p.stdin.flush()
        if not silent:
            SetlXKernel.p_handler.forward_response(self)

        return {'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }
    
    def do_shutdown(self, restart):
        SetlXKernel.p_handler.p.kill()
        if restart:
            SetlXKernel.p_handler = ProcessHandler()

