import pandas as pd


class DataValidator:
    ## @brief Construtor padrão
    def __init__(self):
        pass

    ## @brief Função para validas dados de um coluna
    #  @param data_frama Data Frame do arquivo para ser validado
    #  @param collum_name Nome da coluna do arquivo
    def valid_collum_not_null(
        self, data_frame: pd.DataFrame, collum_name: str
    ) -> pd.DataFrame:
        if collum_name not in data_frame.columns:
            print(f"Coluna {collum_name} não encontrada.")
            return data_frame

        nulos = data_frame[collum_name].isna().sum()

        if nulos > 0:
            data_frame[collum_name] = data_frame[collum_name].fillna("PENDENTE")
        return data_frame

    ## @brief Verifica se o CNPJ é válido
    #  @param cnpj str Suporte ao novo CNPJ 2026
    def verify_cnpj(self, cnpj: str) -> bool:
        if len(cnpj) != 14:
            return False

        for char in cnpj:
            ascii_code = ord(char)
            if not ((48 <= ascii_code <= 57) or (65 <= ascii_code <= 90)):
                print(f"Char inválido: {char} (ASCII {ascii_code})")
                return False

        if cnpj == cnpj[0] * 14:
            print(f"Sequência de dígitos inválidos")
            return False

        # Primeiro dígito verificador
        soma = 0
        peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        for i in range(12):
            soma += (ord(cnpj[i]) - 48) * peso[i]

        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto

        if (ord(cnpj[12]) - 48) != digito1:
            print(f"Primeiro dígito verificador inválido")
            return False

        # Segundo dígito verificador
        soma = 0
        peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        for i in range(13):
            soma += (ord(cnpj[i]) - 48) * peso[i]

        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto

        if (ord(cnpj[13]) - 48) != digito2:
            print(f"Segundo dígito verificador inválido")
            return False

        return True

    ## @brief Valida CNPJs e separa inválidos
    #  @param data_frame DataFrame a validar
    #  @param collum_name Nome da coluna com CNPJ
    #  @return Tupla (df_validos, df_invalidos)
    def validade_cnpjs(self, data_frame: pd.DataFrame, collum_name: str = "CNPJ"):
        if collum_name not in data_frame.columns:
            print(f"Coluna '{collum_name}' não encontrada")
            return data_frame, pd.DataFrame()

        data_frame["CNPJ_Valido"] = data_frame[collum_name].apply(
            lambda x: self.verify_cnpj(str(x))
            if pd.notna(x) and str(x) != "PENDENTE"
            else False
        )

        df_validos = data_frame.loc[data_frame["CNPJ_Valido"] == True].copy()
        df_invalidos = data_frame.loc[data_frame["CNPJ_Valido"] == False].copy()

        if "CNPJ_Valido" in df_validos.columns:
            df_validos = df_validos.drop("CNPJ_Valido", axis=1)

        if "CNPJ_Valido" in df_invalidos.columns:
            df_invalidos = df_invalidos.drop("CNPJ_Valido", axis=1)

        total = len(data_frame)
        validos = len(df_validos)
        invalidos = len(df_invalidos)

        print(f"Total: {total}")
        print(f"Válidos: {validos} ({validos / total * 100:.1f}%)")
        print(f"Inválidos: {invalidos} ({invalidos / total * 100:.1f}%)")

        return df_validos, df_invalidos

    ## @brief Valida Coluna e separa pendentes
    #  @param data_frame DataFrame a validar
    #  @param collum_name Nome da Coluna
    #  @return Tupla (df_validos, df_invalidos)
    def validate_collum_str(
        self, data_frame: pd.DataFrame, collum_name: str = "Razao_Social"
    ):
        if collum_name not in data_frame.columns:
            print(f"Coluna: '{collum_name}' não encontrada")
            return data_frame, pd.DataFrame()

        data_frame["Temp_Valido"] = data_frame[collum_name].apply(
            lambda x: False
            if pd.isna(x) or str(x).strip().upper() == "PENDENTE"
            else True
        )

        df_validos = data_frame.loc[data_frame["Temp_Valido"] == True].copy()
        df_invalidos = data_frame.loc[data_frame["Temp_Valido"] == False].copy()

        if "Temp_Valido" in df_validos.columns:
            df_validos = df_validos.drop("Temp_Valido", axis=1)

        if "Temp_Valido" in df_invalidos.columns:
            df_invalidos = df_invalidos.drop("Temp_Valido", axis=1)

        return df_validos, df_invalidos

    def validade_number(
        self, data_frame: pd.DataFrame, collum_name: str = "ValorDespesas"
    ):
        if collum_name not in data_frame.columns:
            print(f"Coluna: '{collum_name}' não encontrada")
            return data_frame, pd.DataFrame()

        data_frame["Numeros_Negativos"] = data_frame[collum_name].apply(
            lambda x: False if x >= 0 else True
        )

        df_validos = data_frame.loc[data_frame["Numeros_Negativos"] == False].copy()
        df_invalidos = data_frame.loc[data_frame["Numeros_Negativos"] == True].copy()

        if "Numeros_Negativos" in df_validos.columns:
            df_validos = df_validos.drop("Numeros_Negativos", axis=1)

        if "Numeros_Negativos" in df_invalidos.columns:
            df_invalidos = df_invalidos.drop("Numeros_Negativos", axis=1)

        print(f"Numeros de linhas com numeros negativos{len(df_invalidos)}")

        return df_validos, df_invalidos


# VALOR NUMERICO POSITIVO igual ^
