from langchain_community.document_loaders import TextLoader as LangchainTextLoader


class TextLoader:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self):
        loader = LangchainTextLoader(
            self.file_path
        )

        return loader.load()
