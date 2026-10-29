from farol.cli import main


def test_main_imprime_a_versao(capsys):
    assert main([]) == 0
    assert capsys.readouterr().out.startswith("Farol ")
