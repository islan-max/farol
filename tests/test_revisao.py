from farol.achados import Achado
from farol.comentarios import corpo, resumo_excedente
from farol.revisao import TETO_INLINE, montar


def achado(path="a.py", line=1, codigo="E722", ferramenta="ruff"):
    return Achado(path, line, ferramenta, codigo, "mensagem da ferramenta", "https://exemplo.dev/r")


def test_mesma_regra_repetida_vira_um_comentario_so():
    rev = montar([achado(line=3), achado(line=10), achado("b.py", 7)])
    assert len(rev.inline) == 1 and rev.total == 3
    c = rev.inline[0]
    assert (c.achado.path, c.achado.line) == ("a.py", 3)
    assert [(x.path, x.line) for x in c.tambem] == [("a.py", 10), ("b.py", 7)]
    assert "Também aparece em: `a.py:10`, `b.py:7`." in corpo(c)


def test_arquivo_novo_com_200_problemas_gera_no_maximo_o_teto_sem_duplicados():
    # 15 regras diferentes, cada uma repetida muitas vezes: o ruído tem que caber no teto.
    achados = [achado(line=n, codigo=f"X{n % 15:03d}") for n in range(200)]
    rev = montar(achados)
    assert len(rev.inline) == TETO_INLINE
    chaves = [c.achado.codigo for c in rev.inline + rev.excedente]
    assert len(chaves) == len(set(chaves)) == 15  # nenhuma regra duas vezes
    assert len(rev.excedente) == 5
    assert rev.total == 200


def test_excedente_vai_agrupado_por_regra_com_os_locais():
    rev = montar([achado(line=n, codigo=f"X{n:03d}") for n in range(3)], teto=1)
    assert len(rev.excedente) == 2
    assert "`a.py:1`" in resumo_excedente(rev)


def test_seguranca_passa_na_frente_quando_o_teto_aperta():
    rev = montar([achado(line=1, codigo="E722"), achado(line=50, codigo="S608")], teto=1)
    assert rev.inline[0].achado.codigo == "S608"
    assert rev.excedente[0].achado.codigo == "E722"


def test_no_eval_do_eslint_tambem_conta_como_seguranca():
    achados = [
        achado(line=1, codigo="no-var", ferramenta="eslint"),
        achado(line=9, codigo="no-eval", ferramenta="eslint"),
    ]
    rev = montar(achados, teto=1)
    assert rev.inline[0].achado.codigo == "no-eval"


def test_erro_de_sintaxe_e_um_por_arquivo_e_nao_se_junta_entre_arquivos():
    rev = montar([achado("a.py", 1, None), achado("b.py", 1, None)])
    assert len(rev.inline) == 2


def test_sem_licao_cai_para_a_mensagem_da_ferramenta_sem_inventar():
    texto = corpo(montar([achado(codigo="Z999")]).inline[0])
    assert "mensagem da ferramenta" in texto and "https://exemplo.dev/r" in texto
    assert "Por que importa" not in texto


def test_com_licao_o_comentario_ensina():
    texto = corpo(montar([achado(codigo="E722")]).inline[0])
    for trecho in ("Por que importa.", "Como corrigir.", "# antes", "# depois", "nível iniciante"):
        assert trecho in texto
