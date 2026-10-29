"""Ponto de entrada da linha de comando."""

from farol import __version__


def main(argv: list[str] | None = None) -> int:
    print(f"Farol {__version__}")
    return 0
