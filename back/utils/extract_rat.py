from utils.extract_sign import validar_assinatura

def extract_rat_data(text: str) -> dict:

    assinatura_valida = validar_assinatura(text)

    return {
        "TERMO": "RAT",
        "ASSINADO": assinatura_valida,
        "STATUS TERMO": "OK" if assinatura_valida  else "ERRO",
        "TIPO": "----------",
        "MODELO": "----------",
        "MARCA": "----------",
        "SERIAL": "----------",
        "MONITOR": "----------",
        "MODELO MONITOR": "----------",
        "SERIAL MONITOR": "----------",
        "PATRIMÔNIO": "----------",
        "NF": "----------",
        "CHAMADO": "----------",
        "HOSTNAME": "----------",
        "RAM": "----------",
        "MEMÓRIA": "----------",
        "MOUSE": "----------",
        "TECLADO": "----------",
        "HEADSET": "----------",
        "KIT BOAS-VINDAS": "----------",
        "WEBCAM": "----------",
        "HUB USB": "----------",
        "SUPORTE ERGONÔMICO": "----------",
        "CABO DE SEGURANÇA": "----------",
        "MOCHILA": "----------",
        "DOCK STATION": "----------",
        "LACRE DE SEGURANÇA": "----------",
        "CABO RCA": "----------",
        "BATERIA EXTRA": "----------",
        "CARREGADOR EXTRA": "----------",
        "CABO DE FORÇA DO MONITOR": "----------",
        "FONTE": "----------",
        "ADAPTADOR HDMI": "----------"
    }
