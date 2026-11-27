"""
Motor de regras de negócio para o fluxo de importação — DEMONSTRAÇÃO.

Ideia: um domínio regulado (aduaneiro) é um conjunto de REGRAS versionadas, cada uma
ligada a uma NORMA com data de vigência. O motor não "sabe aduaneiro": ele sabe
avaliar regras contra uma operação, e cada decisão sai com a norma que a sustenta.

É esta a competência que a vaga-alvo pede ("documentar os processos impactados sempre
que houver mudança", com a regra escrita ao lado do relatório que a consome) e é esta
que um dev sênior demonstra: entrar num domínio que não
conhece, modelar as regras, versioná-las, cobriu os casos de fronteira com testes
antes de as pôr a produzir.

Execução: python3 demo.py   |   Testes: python3 -m unittest -v test_regras.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Callable, Optional

# --------------------------------------------------------------------------- #
# NORMA: fonte legal com estado de vigência. A regra aponta para a norma.      #
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Norma:
    id: str
    titulo: str
    publicada_em: date
    vigente_de: date
    revogada_em: Optional[date] = None
    revogada_por: Optional[str] = None
    url: str = ""

    def vigente_em(self, dia: date) -> bool:
        if dia < self.vigente_de:
            return False
        if self.revogada_em is not None and dia >= self.revogada_em:
            return False
        return True

    def rotulo_vigencia(self) -> str:
        if self.revogada_em:
            return f"revogada em {self.revogada_em.isoformat()} por {self.revogada_por}"
        return f"vigente desde {self.vigente_de.isoformat()}"


@dataclass(frozen=True)
class Decisao:
    regra: str
    resultado: str          # BLOQUEIA | PERMITE | REVISAR
    motivo: str
    norma_id: str
    vigencia: str

    def __str__(self) -> str:
        return f"[{self.resultado:8s}] {self.regra} — {self.motivo}  ({self.norma_id}, {self.vigencia})"


@dataclass
class Operacao:
    """Uma operação de importação, vista só pelo que as regras precisam."""
    data_registro: date
    documento: str                       # "DI" | "DUIMP"
    tipo: str                            # "importacao" | "remessa"
    ncm: str
    chegada_carga: Optional[date] = None
    recepcao_carga: Optional[date] = None
    data_saida: Optional[date] = None
    importador_regular: bool = True
    carga_vinculada: bool = True
    sem_irregularidade_impeditiva: bool = True
    tributos_pagos: bool = True
    divergencia_valor_aduaneiro: bool = False
    layout_fiscal_novo: bool = True      # sabe emitir NF-e de IBS/CBS no layout novo?

    @property
    def antecipada(self) -> bool:
        return self.chegada_carga is not None and self.data_registro < self.chegada_carga


# --------------------------------------------------------------------------- #
# NORMAS (todas verificadas nas fontes oficiais — ver catalogo_regras.md)      #
# --------------------------------------------------------------------------- #

NORMAS: dict[str, Norma] = {
    "PC-77-2018": Norma(
        id="PC-77-2018",
        titulo="Portaria Coana nº 77/2018 — DUIMP (projeto-piloto do NPI)",
        publicada_em=date(2018, 9, 26), vigente_de=date(2018, 10, 1),
        revogada_em=date(2024, 9, 19), revogada_por="Portaria Coana nº 165/2024",
        url="http://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=95195",
    ),
    "PC-165-2024": Norma(
        id="PC-165-2024",
        titulo="Portaria Coana nº 165/2024 — registo da Duimp e cronograma de obrigatoriedade",
        publicada_em=date(2024, 9, 19), vigente_de=date(2024, 9, 19),
        url="https://www.gov.br/siscomex/pt-br/legislacao/receita-federal",
    ),
    "PC-70-2022": Norma(
        id="PC-70-2022",
        titulo="Portaria Coana nº 70/2022 — despacho antecipado e retificação após a chegada",
        publicada_em=date(2022, 3, 31), vigente_de=date(2022, 3, 31),
        url="https://www.gov.br/receitafederal/pt-br/assuntos/aduana-e-comercio-exterior/manuais/despacho-de-importacao/topicos-1/conceitos-e-definicoes/despacho-de-importacao/Introducao",
    ),
    "IN-680-2006": Norma(
        id="IN-680-2006",
        titulo="Instrução Normativa SRF nº 680/2006 — despacho aduaneiro de importação",
        publicada_em=date(2006, 10, 2), vigente_de=date(2006, 10, 2),
        url="https://www.gov.br/receitafederal/pt-br/assuntos/aduana/todos-os-servicos-aduaneiros",
    ),
    "SIS-020-2026": Norma(
        id="SIS-020-2026",
        titulo="Comunicado Siscomex Importação nº 020/2026 — cronograma de desligamento da DI",
        publicada_em=date(2026, 1, 1), vigente_de=date(2026, 1, 1),
        url="https://www.gov.br/siscomex/pt-br/noticias/noticias-siscomex-importacao/Comunicados/importacao-no-2026-020/",
    ),
    "CRONO-DI-2026": Norma(
        id="CRONO-DI-2026",
        titulo="Cronograma de desligamento de DI e DSI-e (v30, 13/11/2026) — desligamento final em 10/12/2026",
        publicada_em=date(2026, 11, 13), vigente_de=date(2026, 11, 13),
        url="https://www.gov.br/siscomex/pt-br/programa-portal-unico/cronograma-de-desligamento-di",
    ),
    "AC-4-2026": Norma(
        id="AC-4-2026",
        titulo="Ato Conjunto RFB/CGIBS nº 4/2026 — documentos fiscais de IBS e CBS na importação",
        publicada_em=date(2026, 7, 30), vigente_de=date(2026, 7, 30),
        url="https://cgibs.gov.br/atos-tecnicos-conjuntos",
    ),
    "ATC-11-2026": Norma(
        id="ATC-11-2026",
        titulo="Ato Técnico Conjunto RFB/SUANA/CGIBS nº 11/2026 — documentação técnica da Duimp",
        publicada_em=date(2026, 11, 10), vigente_de=date(2026, 11, 12),
        url="https://cgibs.gov.br/atos-tecnicos-conjuntos",
    ),
    "GECEX-272-2021": Norma(
        id="GECEX-272-2021",
        titulo="Resolução Gecex nº 272/2021 — Nomenclatura Comum do Mercosul (NCM) e TEC",
        publicada_em=date(2021, 11, 19), vigente_de=date(2021, 11, 19),
        url="https://www.gov.br/mdic/pt-br/assuntos/camex/resolucoes/gecex/resolucoes",
    ),
}

# --------------------------------------------------------------------------- #
# DADOS: o que a regra consulta. Em produção isto seria API da RFB / tabelas.    #
# --------------------------------------------------------------------------- #

# NCM com vigência terminada (Nota Técnica 2016.003 da NF-e / Resoluções Gecex)
NCM_EXTINTAS: dict[str, date] = {
    "85045000": date(2024, 6, 30),
    "02071400": date(2024, 7, 31),
    "27109100": date(2024, 3, 31),
    "28201000": date(2024, 3, 31),
    "90029000": date(2024, 3, 31),
}
# NCM criadas depois (exemplo real, Res. Gecex 563/2024)
NCM_CRIADAS: dict[str, date] = {
    "48119020": date(2024, 7, 1),
    "85045010": date(2024, 7, 1),
    "85045090": date(2024, 7, 1),
}

DATA_DESLIGAMENTO_DI = date(2026, 12, 10)
DATA_NF_E_IBS_CBS_DUIMP = date(2027, 1, 1)
PRAZO_SAIDA_APOS_REGISTO = 30


# --------------------------------------------------------------------------- #
# REGRAS. Cada uma devolve uma ou mais Decisao.                                #
# --------------------------------------------------------------------------- #

def r01_documento_obrigatorio(op: Operacao) -> list[Decisao]:
    """R01 — Qual documento de registo é válido nesta data."""
    if op.data_registro >= DATA_DESLIGAMENTO_DI:
        if op.documento != "DUIMP":
            return [Decisao("R01 documento de registo", "BLOQUEIA",
                f"a partir de {DATA_DESLIGAMENTO_DI.isoformat()} o registo faz-se por DUIMP; "
                f"a {op.documento} está desligada", "CRONO-DI-2026", "desde 13/11/2026")]
        return [Decisao("R01 documento de registo", "PERMITE",
            "DUIMP — único documento válido nesta data", "CRONO-DI-2026", "desde 13/11/2026")]
    if op.documento != "DI":
        return [Decisao("R01 documento de registo", "REVISAR",
            "DUIMP em data anterior ao desligamento: depende do cronograma de obrigatoriedade "
            "da operação (ver Portaria Coana 165/2024)", "PC-165-2024", "desde 19/09/2024")]
    return [Decisao("R01 documento de registo", "PERMITE",
        "DI válida nesta data", "PC-165-2024", "desde 19/09/2024")]


def r02_antecipacao(op: Operacao) -> list[Decisao]:
    """R02 — É registar a declaração antes da chegada da carga?"""
    if op.chegada_carga is None:
        return [Decisao("R02 registo antecipado", "PERMITE",
            "sem chegada declarada: registo antecipado é a regra", "PC-165-2024", "desde 19/09/2024")]
    if op.data_registro < op.chegada_carga:
        return [Decisao("R02 registo antecipado", "PERMITE",
            "registo antecipado: a Duimp pode ser registada antes da chegada, em qualquer situação",
            "PC-165-2024", "desde 19/09/2024")]
    if op.recepcao_carga is None or op.data_registro < op.recepcao_carga:
        return [Decisao("R02 registo antecipado", "BLOQUEIA",
            "carga já chegou: o registo só pode ocorrer depois da recepção no controlo de carga",
            "PC-165-2024", "desde 19/09/2024")]
    return [Decisao("R02 registo antecipado", "PERMITE",
        "registo posterior à recepção da carga", "PC-165-2024", "desde 19/09/2024")]


def r03_prazo_saida(op: Operacao) -> list[Decisao]:
    """R03 — Prazo de saída da mercadoria registada antecipadamente."""
    if not op.antecipada:
        return []
    if op.data_saida is None:
        limite = op.data_registro + timedelta(days=PRAZO_SAIDA_APOS_REGISTO)
        return [Decisao("R03 prazo de saída", "REVISAR",
            f"sem data de saída registada; limite geral de {PRAZO_SAIDA_APOS_REGISTO} dias = "
            f"{limite.isoformat()} — mas há hipóteses excepcionais por verificar no caso concreto",
            "PC-165-2024", "desde 19/09/2024")]
    limite = op.data_registro + timedelta(days=PRAZO_SAIDA_APOS_REGISTO)
    if op.data_saida > limite:
        return [Decisao("R03 prazo de saída", "BLOQUEIA",
            f"saída em {op.data_saida.isoformat()} excede o limite de {PRAZO_SAIDA_APOS_REGISTO} dias "
            f"({limite.isoformat()})", "PC-165-2024", "desde 19/09/2024")]
    return [Decisao("R03 prazo de saída", "PERMITE",
        f"saída dentro do limite ({limite.isoformat()})", "PC-165-2024", "desde 19/09/2024")]


def r04_retificacao(op: Operacao) -> list[Decisao]:
    """R04 — Retificação: sempre possível; o que muda é o efeito sobre o desembaraço."""
    if not op.divergencia_valor_aduaneiro:
        return [Decisao("R04 retificação", "PERMITE",
            "retificações são admitidas a qualquer momento após o registo (antecipado ou posterior "
            "à chegada) e também após o desembaraço", "IN-680-2006", "desde 02/10/2006")]
    return [Decisao("R04 retificação", "REVISAR",
        "retificação com divergência de valor aduaneiro: o desembaraço fica subordinado ao "
        "recolhimento complementar antes de liberar a mercadoria", "IN-680-2006", "desde 02/10/2006")]


def r05_effectividade_do_registro(op: Operacao) -> list[Decisao]:
    """R05 — Os quatro requisitos de'effectividade do registo."""
    falhas = []
    if not op.importador_regular:
        falhas.append("regularidade cadastral do importador")
    if not op.carga_vinculada:
        falhas.append("carga vinculada à declaração")
    if not op.sem_irregularidade_impeditiva:
        falhas.append("ausência de irregularidade impeditiva (omissão de dado obrigatório, erro, "
                      "impossibilidade legal absoluta)")
    if not op.tributos_pagos:
        falhas.append("confirmação do pagamento dos tributos, contribuições e direitos, incluindo a "
                      "Taxa de Utilização do Siscomex")
    if falhas:
        return [Decisao("R05'effectividade do registo", "BLOQUEIA",
            "o registo não se effective enquanto: " + "; ".join(falhas),
            "PC-77-2018", "vigente 01/10/2018 a 19/09/2024")]
    return [Decisao("R05 efectividade do registo", "PERMITE",
        "os quatro requisitos de efectividade estão satisfeitos — regra transcrita do regime "
        "histórico; ver R08 quanto à norma em vigor", "PC-77-2018",
        "vigente 01/10/2018 a 19/09/2024")]


def r06_classificacao_fiscal(op: Operacao) -> list[Decisao]:
    """R06 — A NCM escolhida existe na data do registo?"""
    fim = NCM_EXTINTAS.get(op.ncm)
    if fim and op.data_registro >= fim:
        return [Decisao("R06 classificação fiscal (NCM)", "BLOQUEIA",
            f"NCM {op.ncm} sem vigência a partir de {fim.isoformat()}: reclassificar antes do registo",
            "GECEX-272-2021", "desde 19/11/2021")]
    inicio = NCM_CRIADAS.get(op.ncm)
    if inicio and op.data_registro < inicio:
        return [Decisao("R06 classificação fiscal (NCM)", "BLOQUEIA",
            f"NCM {op.ncm} só vigorou a partir de {inicio.isoformat()}; registo anterior é inválido",
            "GECEX-272-2021", "desde 19/11/2021")]
    return [Decisao("R06 classificação fiscal (NCM)", "PERMITE",
        f"NCM {op.ncm} vigente na data do registo", "GECEX-272-2021", "desde 19/11/2021")]


def r07_layout_fiscal_cbs_ibs(op: Operacao) -> list[Decisao]:
    """R07 — O layout do documento fiscal de IBS/CBS muda em 01/01/2027 para operações por Duimp."""
    if op.documento != "DUIMP" or op.data_registro < DATA_NF_E_IBS_CBS_DUIMP:
        return []
    if not op.layout_fiscal_novo:
        return [Decisao("R07 layout fiscal IBS/CBS", "REVISAR",
            f"registo por DUIMP a partir de {DATA_NF_E_IBS_CBS_DUIMP.isoformat()} exige NF-e de IBS/CBS "
            "no layout aprovado; o sistema actual não emite nesse layout",
            "AC-4-2026", "desde 30/07/2026")]
    return [Decisao("R07 layout fiscal IBS/CBS", "PERMITE",
        "sistema emite o documento fiscal no layout aprovado em vigor", "AC-4-2026", "desde 30/07/2026")]


def r08_norma_de_referencia_desatualizada(op: Operacao) -> list[Decisao]:
    """R08 — A base de regras ainda cita uma norma revogada para esta data?"""
    norma = NORMAS["PC-77-2018"]
    if norma.vigente_em(op.data_registro):
        return [Decisao("R08 vigência da norma de referência", "PERMITE",
            f"{norma.id} vigente na data do registo", norma.id, norma.rotulo_vigencia())]
    return [Decisao("R08 vigência da norma de referência", "REVISAR",
        f"a regra apoia-se em {norma.id}, revogada em {norma.revogada_em.isoformat()} por "
        f"{norma.revogada_por}; a base de regras tem de migrar para a norma que a revogou",
        "PC-165-2024", "desde 19/09/2024")]


REGRAS: list[tuple[str, str, str, Callable[[Operacao], list[Decisao]]]] = [
    ("R01", "Qual documento de registo é válido nesta data",
     "PC-165-2024; CRONO-DI-2026", r01_documento_obrigatorio),
    ("R02", "É permitido registar a declaração antes da chegada da carga",
     "PC-165-2024", r02_antecipacao),
    ("R03", "Prazo de saída da mercadoria registada antecipadamente",
     "PC-165-2024", r03_prazo_saida),
    ("R04", "Retificação da declaração e o seu efeito sobre o desembaraço",
     "IN-680-2006", r04_retificacao),
    ("R05", "Requisitos de efectividade do registo", "PC-77-2018", r05_effectividade_do_registro),
    ("R06", "A NCM escolhida vigia na data do registo", "GECEX-272-2021", r06_classificacao_fiscal),
    ("R07", "Layout do documento fiscal de IBS/CBS na importação",
     "AC-4-2026", r07_layout_fiscal_cbs_ibs),
    ("R08", "A norma de referência da regra ainda está vigente",
     "PC-77-2018 / PC-165-2024", r08_norma_de_referencia_desatualizada),
]


def avaliar(op: Operacao) -> list[Decisao]:
    """Avalia a operação contra todas as regras. Devolve todas as decisões."""
    decisoes: list[Decisao] = []
    for _id, _enunciado, _fonte, fn in REGRAS:
        decisoes.extend(fn(op))
    return decisoes


def resumo(decisoes: list[Decisao]) -> str:
    """Regra agregadora: o resultado final é o mais restritivo encontrado."""
    for nivel in ("BLOQUEIA", "REVISAR"):
        if any(d.resultado == nivel for d in decisoes):
            return nivel
    return "PERMITE"


def catalogo_markdown() -> str:
    """Gera o catálogo a partir do próprio código — o catálogo não pode divergir das regras."""
    linhas = [
        "# Catálogo de regras — fluxo de importação (demonstração)", "",
        "> **Gerado automaticamente a partir de `regras.py`.** O catálogo é a mesma coisa que o motor "
        "executa — não há manutenção paralela, logo não há divergência possível entre o que se "
        "documenta e o que se aplica.", "",
        "Cada regra tem: um identificador, um enunciado, a norma que a sustenta, a vigência dessa "
        "norma, e o que a regra **decide**. O motor devolve, por operação, a decisão e a norma que a "
        "sustenta.", "",
        "| Regra | Pergunta que responde | Norma | Estado da norma | O que decide |",
        "|---|---|---|---|---|",
    ]
    for rid, enunciado, fonte, fn in REGRAS:
        norma_ids = [n for n in NORMAS if n in fonte]
        estados = []
        for n in norma_ids:
            no = NORMAS[n]
            if no.revogada_em:
                estados.append(f"`{n}` **revogada** em {no.revogada_em.isoformat()} por {no.revogada_por}")
            else:
                estados.append(f"`{n}` vigente desde {no.vigente_de.isoformat()}")
        linhas.append(f"| **{rid}** | {enunciado} | {fonte} | {' · '.join(estados)} | "
                      f"ver `{fn.__name__}` |")
    linhas += [
        "", "## As decisões que o motor sabe tomar", "",
        "| Resultado | Significado |", "|---|---|",
        "| `BLOQUEIA` | a operação não pode prosseguir nestas condições |",
        "| `REVISAR` | há excepção ou hipótese que o motor não decide sozinho — e isso é declarado, "
        "não escondido |",
        "| `PERMITE` | a regra está satisfeita |", "",
        "## Normas catalogadas (todas verificadas na fonte)", "",
        "| Norma | Publicada | Vigência | Fonte |", "|---|---|---|---|",
    ]
    for n in NORMAS.values():
        linhas.append(f"| `{n.id}` — {n.titulo} | {n.publicada_em.isoformat()} | {n.rotulo_vigencia()} | "
                      f"[{n.url}]({n.url}) |")
    citadas = set()
    for _rid, _enunciado, _fonte, _fn in REGRAS:
        citadas.update(n for n in NORMAS if n in _fonte)
    contexto = [n.id for n in NORMAS.values() if n.id not in citadas]
    linhas += [
        "", f"**{len(citadas)}** destas normas são citadas por uma regra. As outras "
        f"**{len(contexto)}** ({', '.join(contexto)}) estão catalogadas como contexto "
        "normativo — são consultadas por regra, mas não sustentam uma regra isolada. "
        "A distinção é gerada a partir do código, como o resto deste catálogo.",
    ]
    linhas += [
        "", "## Por que isto é a demonstração", "",
        "A vaga-alvo pede *«documentar os processos impactados sempre que houver mudança»*. Isto é "
        "o mesmo trabalho, noutro domínio: regras versionadas, ligadas a normas com data, testadas nos "
        "casos de fronteira, e executadas por código — não por memória. O domínio (aduaneiro) não é o "
        "da companhia: é uma demonstração de método, não de assunto.", "",
        "E tem uma data no fim: **a DI desliga a 10/12/2026**. O documento de registo que toda a "
        "cadeia usava muda de nome em 13 dias, e a documentação técnica da Duimp foi aprovada por um "
        "Ato Técnico Conjunto de **10/11/2026** — há dezassete dias. Qualquer operação, base de dados e "
        "regra que não acompanha essa mudança quebra em dezembro.", "",
        "É esse o trabalho que a expansão do Tecon Salvador vai pedir: não 'usar o sistema', mas "
        "**fazer a regra virar sistema**, e mudar a regra quando ela muda.", "",
    ]
    return "\n".join(linhas)
