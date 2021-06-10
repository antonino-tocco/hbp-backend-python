from .epfl_morphology import EpflMorphologyProvider
from .neuro_morpho import NeuroMorphoProvider
from .model_db import ModelDbProvider
from .knowledge import KnowledgeProvider
from .hippocampome import HippocampomeProvider
from .internal_morphology import InternalMorphologyProvider
from .internal_electrophysiology import InternalElectrophysiologyProvider

enabled_dataset_providers = [NeuroMorphoProvider(), EpflMorphologyProvider(), EpflElectrophysiologyProvider(), HippocampomeProvider()]
enabled_model_providers = [ModelDbProvider()]