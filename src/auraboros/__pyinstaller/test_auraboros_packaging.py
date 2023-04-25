"""WIP"""
# from pathlib import Path
# import subprocess

# from PyInstaller import __main__ as pyi_main


# def test_pyi(tmp_path, caplog):
#     SOURCE_DIR = str(
#         Path(__file__).absolute().parent.parent.parent)
#     # SOURCE_DIR is same as (project root dir path)/src/
#     app_name = "test_auraboros"
#     workpath = tmp_path / "build"
#     distpath = tmp_path / "dist"
#     app = tmp_path / (app_name + ".py")
#     app.write_text("\n".join([
#         "from pathlib import Path",
#         "import sys",
#         f"sys.path.append(r'{SOURCE_DIR}')",
#         "from auraboros import engine",
#         "from auraboros.gamescene import SceneManager, Scene",
#         "engine.init()",
#         "scenemanager = SceneManager()",
#         "scenemanager.push(Scene(scenemanager))",
#         "engine.run(scenemanager)"]))
#     args = [
#         '--workpath', str(workpath),
#         '--distpath', str(distpath),
#         '--specpath', str(tmp_path),
#         str(app),
#     ]
#     pyi_main.run(args)
#     exit_status, out = subprocess.getstatusoutput(
#         [str(distpath / app_name / app_name)])
#     print("output: ", out)
#     assert exit_status == 0
