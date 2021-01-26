from .neuro_morpho import NeuroMorphoProvider
from .model_db import ModelDbProvider
from .knowledge import KnowledgeProvider

enabled_dataset_providers = [NeuroMorphoProvider()]
enabled_model_providers = [ModelDbProvider()]