from typing import Sequence

from kgquery.queryApi import Query, KGClient


class Embargo_statu:
    name: any


def _embargostatu_from_payload(payload: dict) -> Embargo_statu:
    embargostatu = Embargo_statu()
    embargostatu.name = payload["https://schema.hbp.eu/myQuery/name"] if "https://schema.hbp.eu/myQuery/name" in payload else None
    return embargostatu


class Modality:
    name: any


def _modality_from_payload(payload: dict) -> Modality:
    modality = Modality()
    modality.name = payload["https://schema.hbp.eu/myQuery/name"] if "https://schema.hbp.eu/myQuery/name" in payload else None
    return modality


class Owner:
    name: any


def _owner_from_payload(payload: dict) -> Owner:
    owner = Owner()
    owner.name = payload["https://schema.hbp.eu/myQuery/name"] if "https://schema.hbp.eu/myQuery/name" in payload else None
    return owner


class Publication:
    name: any


def _publication_from_payload(payload: dict) -> Publication:
    publication = Publication()
    publication.name = payload["https://schema.hbp.eu/myQuery/name"] if "https://schema.hbp.eu/myQuery/name" in payload else None
    return publication


class File:
    url: any
    file_size: any
    name: any


def _file_from_payload(payload: dict) -> File:
    file = File()
    file.url = payload["https://schema.hbp.eu/myQuery/url"] if "https://schema.hbp.eu/myQuery/url" in payload else None
    file.file_size = payload["https://schema.hbp.eu/myQuery/fileSize"] if "https://schema.hbp.eu/myQuery/fileSize" in payload else None
    file.name = payload["https://schema.hbp.eu/myQuery/name"] if "https://schema.hbp.eu/myQuery/name" in payload else None
    return file


class Dataset:
    name: any
    createdat: any
    data_descriptor: any
    embargostatus: Sequence[Embargo_statu]
    modality: Sequence[Modality]
    owners: Sequence[Owner]
    publications: Sequence[Publication]
    files: Sequence[File]
    description: any
    id: any


def _dataset_from_payload(payload: dict) -> Dataset:
    dataset = Dataset()
    dataset.name = payload["https://schema.hbp.eu/myQuery/name"] if "https://schema.hbp.eu/myQuery/name" in payload else None
    dataset.createdat = payload["https://schema.hbp.eu/myQuery/created_at"] if "https://schema.hbp.eu/myQuery/created_at" in payload else None
    dataset.data_descriptor = payload["https://schema.hbp.eu/myQuery/dataDescriptor"] if "https://schema.hbp.eu/myQuery/dataDescriptor" in payload else None
    dataset.embargostatus = []
    if "https://schema.hbp.eu/myQuery/embargo_status" in payload and isinstance(payload["https://schema.hbp.eu/myQuery/embargo_status"], list):
        for c in payload["https://schema.hbp.eu/myQuery/embargo_status"]:
            dataset.embargostatus.append(_embargostatu_from_payload(c))
    dataset.modality = []
    if "https://schema.hbp.eu/myQuery/modality" in payload and isinstance(payload["https://schema.hbp.eu/myQuery/modality"], list):
        for c in payload["https://schema.hbp.eu/myQuery/modality"]:
            dataset.modality.append(_modality_from_payload(c))
    dataset.owners = []
    if "https://schema.hbp.eu/myQuery/owners" in payload and isinstance(payload["https://schema.hbp.eu/myQuery/owners"], list):
        for c in payload["https://schema.hbp.eu/myQuery/owners"]:
            dataset.owners.append(_owner_from_payload(c))
    dataset.publications = []
    if "https://schema.hbp.eu/myQuery/publications" in payload and isinstance(payload["https://schema.hbp.eu/myQuery/publications"], list):
        for c in payload["https://schema.hbp.eu/myQuery/publications"]:
            dataset.publications.append(_publication_from_payload(c))
    dataset.files = []
    if "https://schema.hbp.eu/myQuery/files" in payload and isinstance(payload["https://schema.hbp.eu/myQuery/files"], list):
        for c in payload["https://schema.hbp.eu/myQuery/files"]:
            dataset.files.append(_file_from_payload(c))
    dataset.description = payload["https://schema.hbp.eu/myQuery/description"] if "https://schema.hbp.eu/myQuery/description" in payload else None
    dataset.id = payload["https://schema.hbp.eu/myQuery/id"] if "https://schema.hbp.eu/myQuery/id" in payload else None
    return dataset


class Hbp_datasetDataset(Query[Dataset]):

    def __init__(self, client: KGClient):
        super().__init__(client, "minds/core/dataset/v1.0.0", "hbp_dataset")

    def create_result(self, payload: dict) -> Dataset:
        return _dataset_from_payload(payload)

    def create_filter_params(self) -> str:
        filter = ""
        return filter

