import functools
import os

import torch
import torch.distributed as dist

from transformers.modeling_outputs import CausalLMOutput, CausalLMOutputWithPast, CausalLMOutputWithCrossAttentions


@functools.lru_cache()
def print_once(msg):
    print(msg)


def write_shape(ar, filename):
    with open(filename, 'w', encoding='utf-8') as output:
        output.write(' '.join(map(str, ar.shape)))
        output.write('\n')
        output.write(str(ar.dtype))


def create_hook(name: str, output_dir: str = '/mnt/p.geyn/gradients', seq_p_inited: bool = False):
    def hook(grad):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        middle_name = f'_rank_{dist.get_rank()}' if seq_p_inited else ''
        shape_filename = os.path.join(output_dir, name + middle_name + '.shape')
        filename = os.path.join(output_dir, name + middle_name + '.npy')

        write_shape(grad, shape_filename)
        print(f'{dist.get_rank()=} {name=} {grad.min().item()=} {grad.max().item()=}')

        np_grad = grad.float().cpu().numpy()
        print(f'{dist.get_rank()=} {name=} {np_grad.min().item()=} {np_grad.max().item()=}')
        np_grad.tofile(filename)

    return hook


def process_forward_output(output_dir, name, middle_name, output) -> bool:
    shape_filename = os.path.join(output_dir, name + middle_name + '.shape')
    filename = os.path.join(output_dir, name + middle_name + '.npy')
    if os.path.exists(filename):
        return False

    if isinstance(output, (CausalLMOutput, CausalLMOutputWithCrossAttentions, CausalLMOutputWithPast)):
        output = output.logits

    if not isinstance(output, torch.Tensor):
        print_once(f'have output: {type(output)}')
        return False

    write_shape(output, shape_filename)

    print(f'{dist.get_rank()=} {name=} {output.min().item()=} {output.max().item()=} {output.dtype=}')

    np_output = output.float().cpu().detach().numpy()
    print(f'{dist.get_rank()=} {name=} {np_output.min().item()=} {np_output.max().item()=}')
    np_output.tofile(filename)
    return True


class ForwardHook:
    def __init__(self, name: str, output_dir: str, seq_p_inited: bool = False):
        self.name = name
        self.output_dir = output_dir
        suff = f'_{dist.get_rank()}' if seq_p_inited else ''
        self.forward_file = os.path.join(output_dir, f'forward_order{suff}.txt')
        self.written = False
        self.middle_name = f'_rank_{dist.get_rank()}' if seq_p_inited else ''

        os.makedirs(self.output_dir, exist_ok=True)

    def __call__(self, module, args, output):
        set_flag = False
        if isinstance(output, tuple):
            for ind, local_output in enumerate(output):
                if process_forward_output(self.output_dir, f'{self.name}_{ind}', self.middle_name, local_output):
                    if not self.written:
                        with open(self.forward_file, 'a') as o:
                            o.write(f'{self.name}_{ind}\n')

                        set_flag = True
        else:
            if process_forward_output(self.output_dir, self.name, self.middle_name, output):
                if not self.written:
                    with open(self.forward_file, 'a') as o:
                        o.write(f'{self.name}\n')

                    set_flag = True

        if set_flag:
            self.written = True


def create_forward_hook(name: str, output_dir: str = '/mnt/p.geyn/forward', seq_p_inited: bool = False):
    return ForwardHook(name, output_dir, seq_p_inited)
