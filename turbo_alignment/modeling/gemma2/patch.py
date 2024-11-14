from transformers.models.gemma2.modeling_gemma2 import GEMMA2_ATTENTION_CLASSES

from .ulysses_attn import Gemma2FlashAttention2Ulysses


def patch_gemma_attn_dict():
    GEMMA2_ATTENTION_CLASSES['flash_attention_2_ulysses'] = Gemma2FlashAttention2Ulysses
