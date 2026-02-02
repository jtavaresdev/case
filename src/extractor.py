import zipfile
from pathlib import Path

import requests


class DataExtractor:
    ## @brief Contrutor da classe DataExtractor
    #  @param base_url URL base de onde baixar arquivos
    def __init__(
        self,
        base_url,
        raw_dir="dados/raw",
        output_dir="dados/output",
        extract_dir="dados/extracted",
    ):
        self.base_url = base_url
        self.raw_dir = Path(raw_dir)
        self.output_dir = Path(output_dir)
        self.extract_dir = Path(extract_dir)

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.extract_dir.mkdir(parents=True, exist_ok=True)

    ## @brief Função para baixar arquivos
    #  @param url URL para baixar arquivo
    #  @param nome_arquivo Nome para ser alvo após download
    def baixar_arquivo(self, url, nome_arquivo):
        """Baixa um arquivo específico"""
        destino = self.raw_dir / nome_arquivo

        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            with open(destino, "wb") as f:
                f.write(response.content)

            return destino

        except requests.exceptions.RequestException as e:
            print(f"Erro: {e}\n")
            return None

    ## @brief Função para baixar trimestre de um ano
    #  @param ano Ano para ser baixado os arquivos
    def baixar_trimestre(self, ano):
        """Baixa todos os arquivos de um ano"""
        base_url = f"{self.base_url}/{ano}/"

        arquivos = [f"1T{ano}.zip", f"2T{ano}.zip", f"3T{ano}.zip"]

        todos_extraidos = []
        for arquivo in arquivos:
            url = base_url + arquivo
            zip_baixado = self.baixar_arquivo(url, arquivo)
            if zip_baixado:
                extraido = self.extrair_zip(zip_baixado)
                if extraido:
                    todos_extraidos.append(extraido)

        print(f"Baixado = {len(todos_extraidos)}")
        return todos_extraidos

    ## @brief Função para desempacotar arquivos zipados
    #  @param zip_path Path do arquivo
    def extrair_zip(self, zip_path):
        pasta_destino = self.extract_dir / zip_path.stem
        # TODO exist_ok=False ?
        pasta_destino.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                arquivos_dentro = zip_ref.namelist()

                zip_ref.extractall(pasta_destino)

                arquivos_extraidos = [pasta_destino / nome for nome in arquivos_dentro]
                return arquivos_extraidos

        except zipfile.BadZipFile as b:
            print(f"Erro ZIP corrompido: {b}\n")
            return None
        except Exception as e:
            print(f"Erro ao extrair: {e}\n")
            return None


if __name__ == "__main__":
    extractor = DataExtractor(
        base_url="https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis"
    )

    arquivos = extractor.baixar_trimestre(ano=2025)
    operadoras = extractor.baixar_arquivo(
        "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv",
        "Relatorio_cadop",
    )

    for arq in arquivos:
        print(f"   {arq}")
