from pathlib import Path

from flask import Flask, redirect

from multiprocessing import Pool, cpu_count

from subprocess import Popen, PIPE, check_output

from os import PathLike


def transcode(file: str | PathLike):
    target = Path(file).with_suffix(".opus")
    cmd = Popen(
        (
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "quiet",
            "-i",
            file,
            "-f",
            "flac",
            "--",
            "-",
        ),
        stdout=PIPE,
    )
    check_output(
        ("opusenc", "--quiet", "--bitrate", "96.000", "--", "-", target),
        stdin=cmd.stdout,
    )
    cmd.wait()
    # Path(file).unlink(missing_ok=True)

def f(file: str | PathLike):
    file = Path(file)
    if file.is_file() and file.suffix == ".flac":
        transcode(file)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    
    @app.route("/")
    def index():
        return "<form action='/convert' method='POST'><input type='submit'></form>"
    
    @app.route("/convert", methods=["POST"])
    def convert():
        file = Path("/home/dominik/Music")
        
        workers = cpu_count()
        with Pool(workers) as pool:
            pool.map(f, [ff for ff in file.rglob("*")])
            
        return redirect("/")

    return app
