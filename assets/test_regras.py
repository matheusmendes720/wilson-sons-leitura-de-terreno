"""Testes do motor de regras. Cada teste é um PASS falsificável: se a regra mudar, o teste expira."""
import unittest
from datetime import date

from regras import (
    DATA_DESLIGAMENTO_DI, DATA_NF_E_IBS_CBS_DUIMP, Operacao,
    avaliar, catalogo_markdown, resumo,
)


def op(**kw) -> Operacao:
    base = dict(
        data_registro=date(2026, 11, 16), documento="DUIMP", tipo="importacao",
        ncm="84713012", chegada_carga=date(2026, 11, 20), recepcao_carga=date(2026, 11, 21),
        data_saida=date(2026, 12, 20),
    )
    base.update(kw)
    return Operacao(**base)


class TesteRegra01Documento(unittest.TestCase):
    def test_di_apos_desligamento_e_bloqueada(self):
        d = avaliar(op(data_registro=date(2026, 12, 11), documento="DI"))
        self.assertEqual(resumo(d), "BLOQUEIA")
        self.assertTrue(any("DI" in x.motivo for x in d))

    def test_duimp_apos_desligamento_e_permitida(self):
        """A operação passa a regra de substantia (R01) mas o agregado é REVISAR,
        porque a regra R08 aponta para uma norma revogada — que é o ponto do motor."""
        d = avaliar(op(data_registro=date(2026, 12, 11)))
        r01 = [x for x in d if x.regra.startswith("R01")][0]
        self.assertEqual(r01.resultado, "PERMITE")
        self.assertEqual(resumo(d), "REVISAR")
        r08 = [x for x in d if x.regra.startswith("R08")][0]
        self.assertEqual(r08.resultado, "REVISAR")

    def test_duimp_antes_do_desligamento_marca_revisao(self):
        d = avaliar(op(data_registro=date(2026, 11, 16)))
        r01 = [x for x in d if x.regra.startswith("R01")][0]
        self.assertEqual(r01.resultado, "REVISAR")

    def test_fronteira_um_dia_antes_do_desligamento_ainda_e_di(self):
        d = avaliar(op(data_registro=date(2026, 12, 9), documento="DI"))
        r01 = [x for x in d if x.regra.startswith("R01")][0]
        self.assertEqual(r01.resultado, "PERMITE")


class TesteRegra02Antecipacao(unittest.TestCase):
    def test_registo_antes_da_chegada_e_permitido(self):
        d = avaliar(op(data_registro=date(2026, 11, 16), chegada_carga=date(2026, 11, 20)))
        r = [x for x in d if x.regra.startswith("R02")][0]
        self.assertEqual(r.resultado, "PERMITE")

    def test_registo_apos_chegada_e_antes_da_recepcao_e_bloqueado(self):
        d = avaliar(op(data_registro=date(2026, 11, 20), chegada_carga=date(2026, 11, 20),
                       recepcao_carga=date(2026, 11, 21)))
        r = [x for x in d if x.regra.startswith("R02")][0]
        self.assertEqual(r.resultado, "BLOQUEIA")

    def test_registo_apos_recepcao_e_permitido(self):
        d = avaliar(op(data_registro=date(2026, 11, 22), chegada_carga=date(2026, 11, 20),
                       recepcao_carga=date(2026, 11, 21)))
        r = [x for x in d if x.regra.startswith("R02")][0]
        self.assertEqual(r.resultado, "PERMITE")


class TesteRegra03Prazo(unittest.TestCase):
    def test_saida_dentro_do_limite(self):
        d = avaliar(op(data_registro=date(2026, 12, 1), chegada_carga=date(2026, 12, 5),
                       data_saida=date(2026, 12, 30)))
        r = [x for x in d if x.regra.startswith("R03")][0]
        self.assertEqual(r.resultado, "PERMITE")

    def test_saida_fora_do_limite_bloqueia(self):
        d = avaliar(op(data_registro=date(2026, 12, 1), chegada_carga=date(2026, 12, 5),
                       data_saida=date(2027, 1, 15)))
        r = [x for x in d if x.regra.startswith("R03")][0]
        self.assertEqual(r.resultado, "BLOQUEIA")

    def test_sem_data_de_saida_marca_revisao_nao_permite(self):
        d = avaliar(op(data_registro=date(2026, 12, 1), chegada_carga=date(2026, 12, 5),
                       data_saida=None))
        r = [x for x in d if x.regra.startswith("R03")][0]
        self.assertEqual(r.resultado, "REVISAR")


class TesteRegra04Retificacao(unittest.TestCase):
    def test_sem_divergencia_permite(self):
        d = avaliar(op())
        r = [x for x in d if x.regra.startswith("R04")][0]
        self.assertEqual(r.resultado, "PERMITE")

    def test_com_divergencia_marca_revisao(self):
        d = avaliar(op(divergencia_valor_aduaneiro=True))
        r = [x for x in d if x.regra.startswith("R04")][0]
        self.assertEqual(r.resultado, "REVISAR")


class TesteRegra05Effectividade(unittest.TestCase):
    def test_requisitos_satisfeitos_permite(self):
        d = avaliar(op())
        r = [x for x in d if x.regra.startswith("R05")][0]
        self.assertEqual(r.resultado, "PERMITE")

    def test_carga_nao_vinculada_bloqueia(self):
        d = avaliar(op(carga_vinculada=False))
        r = [x for x in d if x.regra.startswith("R05")][0]
        self.assertEqual(r.resultado, "BLOQUEIA")
        self.assertIn("carga vinculada", r.motivo)

    def test_tributos_nao_pagos_bloqueia(self):
        d = avaliar(op(tributos_pagos=False))
        r = [x for x in d if x.regra.startswith("R05")][0]
        self.assertEqual(r.resultado, "BLOQUEIA")


class TesteRegra06Ncm(unittest.TestCase):
    def test_ncm_extinta_bloqueia(self):
        d = avaliar(op(ncm="85045000", data_registro=date(2024, 7, 15)))
        r = [x for x in d if x.regra.startswith("R06")][0]
        self.assertEqual(r.resultado, "BLOQUEIA")

    def test_ncm_valida_permite(self):
        d = avaliar(op(ncm="84713012"))
        r = [x for x in d if x.regra.startswith("R06")][0]
        self.assertEqual(r.resultado, "PERMITE")

    def test_ncm_criada_depois_bloqueia_uso_cedo(self):
        d = avaliar(op(ncm="85045010", data_registro=date(2024, 5, 1)))
        r = [x for x in d if x.regra.startswith("R06")][0]
        self.assertEqual(r.resultado, "BLOQUEIA")


class TesteRegra07CbsIbs(unittest.TestCase):
    def test_registo_em_2027_sem_layout_novo_marca_revisao(self):
        d = avaliar(op(data_registro=date(2027, 2, 1), layout_fiscal_novo=False))
        r = [x for x in d if x.regra.startswith("R07")][0]
        self.assertEqual(r.resultado, "REVISAR")

    def test_registo_em_2027_com_layout_novo_permite(self):
        d = avaliar(op(data_registro=date(2027, 2, 1), layout_fiscal_novo=True))
        r = [x for x in d if x.regra.startswith("R07")][0]
        self.assertEqual(r.resultado, "PERMITE")

    def test_antes_de_2027_a_regra_nao_fala(self):
        d = avaliar(op(data_registro=date(2026, 11, 16), layout_fiscal_novo=False))
        self.assertEqual([x for x in d if x.regra.startswith("R07")], [])


class TesteRegra08VigenciaDaNorma(unittest.TestCase):
    def test_norma_revogada_marca_revisao_apos_2024(self):
        d = avaliar(op(data_registro=date(2026, 11, 16)))
        r = [x for x in d if x.regra.startswith("R08")][0]
        self.assertEqual(r.resultado, "REVISAR")
        self.assertIn("165/2024", r.motivo)

    def test_antes_da_revogacao_permite(self):
        d = avaliar(op(data_registro=date(2024, 1, 10)))
        r = [x for x in d if x.regra.startswith("R08")][0]
        self.assertEqual(r.resultado, "PERMITE")


class TesteCatalogo(unittest.TestCase):
    def test_catalogo_e_gerado_do_codigo_e_contem_todas_as_regras(self):
        md = catalogo_markdown()
        for rid, _e, _f, _fn in __import__("regras").REGRAS:
            self.assertIn(f"**{rid}**", md)

    def test_catalogo_declara_a_data_do_desligamento(self):
        self.assertIn("10/12/2026", catalogo_markdown())


if __name__ == "__main__":
    unittest.main(verbosity=2)
