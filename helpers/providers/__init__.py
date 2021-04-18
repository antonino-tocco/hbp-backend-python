from .neuro_morpho import NeuroMorphoProvider
from .model_db import ModelDbProvider
from .knowledge import KnowledgeProvider
from .hippocampome import HippocampomeProvider
from .internal import InternalProvider

enabled_dataset_providers = [NeuroMorphoProvider(), InternalProvider(), HippocampomeProvider()]
enabled_model_providers = [ModelDbProvider()]