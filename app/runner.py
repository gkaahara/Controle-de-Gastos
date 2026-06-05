import sys
import os
import webbrowser
import logging
from threading import Timer


def get_data_dir():
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "data")
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _open_browser():
    webbrowser.open("http://127.0.0.1:5000")


def main():
    data_dir = get_data_dir()
    os.makedirs(data_dir, exist_ok=True)

    log_file = os.path.join(data_dir, "app.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        force=True,
    )
    logging.info("Iniciando projeto-gastos...")
    logging.info("Diretorio de dados: %s", data_dir)

    try:
        from app import create_app

        app = create_app(data_dir=data_dir)
        app.config["DEBUG"] = False

        Timer(1.5, _open_browser).start()
        logging.info("Servidor em http://127.0.0.1:5000")
        app.run(host="127.0.0.1", port=5000, debug=False)
    except Exception as e:
        logging.error("Erro ao iniciar: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    main()
