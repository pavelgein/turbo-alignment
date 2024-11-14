from peft import (
    LoraConfig,
    PeftType,
    PrefixTuningConfig,
    PromptEncoderConfig,
    PromptTuningConfig,
)
from transformers import (
    AutoModel,
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
)

from turbo_alignment.common.registry import Registrable
from turbo_alignment.settings.model import ModelType
# from turbo_alignment.modeling.gemma2.little_gemma import Gemma2ForCausalLMUlysses
from turbo_alignment.modeling.mp_pretrained import Gemma2ForCausalLMWithMPU

class TransformersAutoModelRegistry(Registrable):
    ...


class PeftConfigRegistry(Registrable):
    ...


TransformersAutoModelRegistry.register(ModelType.CAUSAL)(AutoModelForCausalLM)
TransformersAutoModelRegistry.register(ModelType.SEQ_CLS)(AutoModelForSequenceClassification)
TransformersAutoModelRegistry.register(ModelType.ENC)(AutoModel)
TransformersAutoModelRegistry.register(ModelType.GEMMA_WITH_ULYSSES)(Gemma2ForCausalLMWithMPU)

PeftConfigRegistry.register(PeftType.LORA)(LoraConfig)
PeftConfigRegistry.register(PeftType.PREFIX_TUNING)(PrefixTuningConfig)
PeftConfigRegistry.register(PeftType.PROMPT_TUNING)(PromptTuningConfig)
PeftConfigRegistry.register(PeftType.P_TUNING)(PromptEncoderConfig)
